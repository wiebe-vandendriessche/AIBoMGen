import sys
from datetime import datetime
from typing import TYPE_CHECKING
import json
from cyclonedx.model import HashType, XsUri, HashAlgorithm
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.contact import OrganizationalEntity
from cyclonedx.model.tool import Tool
from cyclonedx.output.json import JsonV1Dot5
from cyclonedx.output import make_outputter, OutputFormat
from cyclonedx.validation.json import JsonStrictValidator
from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.model import Property
from cyclonedx.factory.license import LicenseFactory
from cyclonedx.schema import SchemaVersion
from cyclonedx.output import BaseOutput, OutputFormat
import os

if TYPE_CHECKING:
    from cyclonedx.output.json import Json as JsonOutputter
    from cyclonedx.validation.json import JsonValidator


def generate_cyclonedx_format(aibom, output_folder):
    bom = Bom()
    lc_factory = LicenseFactory()

    bom.metadata.tools.components.add(
        Component(
            name="AIBoMGen",
            version="0.1.0",
            type=ComponentType.PLATFORM,
            supplier=OrganizationalEntity(
                name="Ghent University",
                urls=[XsUri('https://www.ugent.be/')]
            ),
            group="Ghent University",
            licenses=[lc_factory.make_from_string('MIT')],
        )
    )


    # Model component (main model)
    # needs to be widely extended with mlflow data
    model_component = Component(
        type=ComponentType.MACHINE_LEARNING_MODEL,
        name=aibom.get("model_name", "Unknown Model"),
        description=aibom.get("description", "No description available"),
        bom_ref="ai-model",
        properties=[
            Property(name="category", value="custom-training"),
            Property(name="mlflow_experiment_id", value=aibom["mlflow_info"].get("experiment_id", "N/A")),
            Property(name="mlflow_experiment_name", value=aibom["mlflow_info"].get("experiment_name", "N/A")),
            Property(name="mlflow_run_id", value=aibom["mlflow_info"].get("run_id", "N/A")),
            Property(name="mlflow_run_start_time", value=str(aibom["mlflow_info"].get("run_start_time", "N/A"))),
            Property(name="mlflow_run_end_time", value=str(aibom["mlflow_info"].get("run_end_time", "N/A"))),
            Property(name="mlflow_status", value=aibom["mlflow_info"].get("status", "N/A")),
        ],
    )

    # Add MLflow parameters
    for param, value in aibom["mlflow_info"].get("parameters", {}).items():
        model_component.properties.add(Property(name=f"mlflow_param_{param}", value=str(value)))

    # Add MLflow metrics
    for metric, value in aibom["mlflow_info"].get("metrics", {}).items():
        model_component.properties.add(Property(name=f"mlflow_metric_{metric}", value=str(value)))

    # Add MLflow tags
    for tag, value in aibom["mlflow_info"].get("tags", {}).items():
        model_component.properties.add(Property(name=f"mlflow_tag_{tag}", value=str(value)))

    # Include MLflow artifacts
    for artifact in aibom["mlflow_info"].get("artifacts", []):
        model_component.properties.add(Property(name="mlflow_artifact", value=artifact))

    model_summary = aibom["mlflow_info"].get("model_summary", "N/A")
    model_component.properties.add(Property(name="model_summary", value=model_summary))

    bom.components.add(model_component)

    installed_components = []  # Store installed components for dependencies
    # Installed Packages (Dependencies)
    for package in aibom.get("installed_packages", []):
        library_component = Component(
            type=ComponentType.LIBRARY,
            name=package,
            version="not yet done",
            bom_ref="package",
        )
        bom.components.add(library_component)
        installed_components.append(library_component)  # Add to the list of dependencies

    # Docker Image Details
    if "docker_image" in aibom:
        docker_component = Component(
            type=ComponentType.CONTAINER,
            name=aibom["docker_image"].get("image_name", "Unknown Image"),
            version=aibom["docker_image"].get("image_tag", "Unknown Version"),
            bom_ref="docker-image",
        )
        bom.components.add(docker_component)

    # Mounted Data Access (Datasets)
    dataset_components = []  # Store dataset components for dependencies
    # Add mounted data access as dataset components
    for file_entry in aibom.get("mounted_data_access", []):
        dataset_component = Component(
            type=ComponentType.DATA,
            name=file_entry.get("file", "Unknown File"),
            description="Dataset used for training",
            bom_ref=f"dataset-{file_entry.get('hash', 'unknown')}",
        )
        dataset_hash = HashType(alg=HashAlgorithm("SHA-256"), content=file_entry.get("hash", "unknown"))
        dataset_component.hashes.add(dataset_hash)
        dataset_component.properties.add(Property(name="dataset-hash", value=file_entry.get("hash", "unknown")))
        dataset_component.properties.add(Property(name="file-path", value=file_entry.get("file", "Unknown File")))

        bom.components.add(dataset_component)
        dataset_components.append(dataset_component)  # Add to the list of dependencies


# GPU Information
    if "gpu_info" in aibom:
        gpu_component = Component(
            type=ComponentType.DEVICE,
            name="Hardware",
            description=f"Training executed on {aibom['gpu_info']}",
            bom_ref="gpu-info",
        )
        bom.components.add(gpu_component)

    # Register dependencies for model_component
    bom.register_dependency(model_component, installed_components + dataset_components)

    # Generate JSON output
    my_json_outputter: 'JsonOutputter' = JsonV1Dot5(bom)
    serialized_json = my_json_outputter.output_as_string(indent=4)

    # Manually format the output using json.dumps() to pretty print it
    pretty_json = json.dumps(json.loads(serialized_json), indent=4)

    # Validation
    my_json_validator = JsonStrictValidator(SchemaVersion.V1_6)
    try:
        validation_errors = my_json_validator.validate_str(pretty_json)
        if validation_errors:
            print('JSON invalid', 'ValidationError:', repr(validation_errors), sep='\n', file=sys.stderr)
            sys.exit(2)
        print('JSON valid')
    except MissingOptionalDependencyException as error:
        print('JSON-validation was skipped due to', error)

    # Define the output file path
    aibom_file_path = os.path.join(output_folder, "aibom.json")

    # Try to write the JSON output to the file
    try:
        with open(aibom_file_path, "w") as file:
            file.write(pretty_json)
    except FileExistsError:
        print(f"File {aibom_file_path} already exists, overwriting...")
        os.remove(aibom_file_path)  # Remove existing file before writing new one
        with open(aibom_file_path, "w") as file:
            file.write(pretty_json)
    finally:
        print(f"Final AIBoM generated at {aibom_file_path}")


