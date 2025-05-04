import datetime
import json
import io
import os
import sys
import yaml
import base64
import uuid
import tensorflow as tf
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.schema import OutputFormat, SchemaVersion
from cyclonedx.factory.license import LicenseFactory
from cyclonedx.model import HashType, XsUri, HashAlgorithm
from cyclonedx.model.contact import OrganizationalEntity, OrganizationalContact
from cyclonedx.model import Property
from cyclonedx.builder.this import this_component as cdx_lib_component
from cyclonedx.model import ExternalReference, ExternalReferenceType
from cyclonedx.output.json import JsonV1Dot5, JsonV1Dot6
from cyclonedx.validation.json import JsonStrictValidator
from cyclonedx.exception import MissingOptionalDependencyException
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key


lc_factory = LicenseFactory()


def transform_to_cyclonedx(bom_data):
    """
    Transform the given BOM data into a CycloneDX format.
    Args:
        bom_data (dict): The BOM data to transform.
    Returns:
        Bom: A CycloneDX formatted BOM instance.
    """

    # Create a new BOM instance
    bom = Bom()
    bom.version = 1

    # BOM: metadata =========================================================================================================
    bom.metadata.timestamp = datetime.datetime.now()
    
    # Add the cycloneDX library component to the BOM metadata
    bom.metadata.tools.components.add(cdx_lib_component())

    # Add the BOM generator and platform tool (aibomgen) to the BOM metadata
    bom.metadata.tools.components.add(
        Component(
            name="AIBoMGen",
            version="0.1.0",
            type=ComponentType.PLATFORM,
            description="A platform for AI training and generating trusted AIBOMs",
            supplier=OrganizationalEntity(
                name="IDLab from Imec, Ghent University",
                urls=[
                    XsUri('https://www.idlab.ugent.be')
                ],
                contacts=[
                    OrganizationalContact(
                        name="Wiebe Vandendriessche",
                        email="wiebe.vandendriessche@ugent.be",
                        phone="+32 9 264 92 00",
                    )
                ]
            ),
            group="IDLab from Imec and Ghent University",
            licenses=[lc_factory.make_from_string('MIT')],
        )
    )

    # Set authors
    bom.metadata.authors = [
        OrganizationalContact(
            name="AIBoMGen by Wiebe Vandendriessche",
            email="wiebe.vandendriessche@ugent.be",
        )
    ]

    # Set supplier and manufacturer
    bom.metadata.supplier = OrganizationalEntity(
        name="IDLab from Imec, Ghent University",
        urls=[
            XsUri('https://www.idlab.ugent.be')
        ],
    )
    bom.metadata.manufacturer = OrganizationalEntity(
        name="IDLab from Imec, Ghent University",
        urls=[
            XsUri('https://www.idlab.ugent.be')
        ],
    )

    # BOM: components =========================================================================================================

    # Add environment details as a component
    environment = bom_data.get("environment", {})
    gpu_info = environment.get("gpu_info", [])
    celery_task_info = environment.get("celery_task_info", {})
    docker_info = environment.get("docker_info", {})
    vulnerability_scan = environment.get("vulnerability_scan", {})
    
    environment_properties = [
        Property(name="OS", value=environment.get("os", "Unknown")),
        Property(name="Python Version", value=environment.get("python_version", "Unknown")),
        Property(name="TensorFlow Version", value=environment.get("tensorflow_version", "Unknown")),
        Property(name="CPU Count", value=str(environment.get("cpu_count", "Unknown"))),
        Property(name="Memory Total (MB)", value=str(environment.get("memory_total", "Unknown"))),
        Property(name="Disk Usage (MB)", value=str(environment.get("disk_usage", "Unknown"))),
        Property(name="Request Time", value=environment.get("request_time", "Unknown")),
        Property(name="Start Training Time", value=environment.get("start_training_time", "Unknown")),
        Property(name="Start AIBoM Time", value=environment.get("start_aibom_time", "Unknown")),
        Property(name="Training Time (seconds)", value=str(environment.get("training_time", "Unknown"))),
        Property(name="Job ID", value=environment.get("job_id", "Unknown")),
        Property(name="Unique Directory", value=environment.get("unique_dir", "Unknown")),
    ]

    # Add GPU Info as individual properties
    for gpu in gpu_info:
        environment_properties.extend([
            Property(name="GPU Name", value=gpu.get("name", "Unknown")),
            Property(name="GPU Memory Total (MB)", value=str(gpu.get("memory_total", "Unknown"))),
            Property(name="GPU Memory Used (MB)", value=str(gpu.get("memory_used", "Unknown"))),
        ])

    # Add Celery Task Info as individual properties
    environment_properties.extend([
        Property(name="Celery Task ID", value=celery_task_info.get("task_id", "Unknown")),
        Property(name="Celery Task Name", value=celery_task_info.get("task_name", "Unknown")),
        Property(name="Celery Queue", value=celery_task_info.get("queue", "Unknown")),
    ])

    # Add Docker Info as individual properties
    environment_properties.extend([
        Property(name="Docker Container ID", value=docker_info.get("container_id", "Unknown")),
        Property(name="Docker Image Name", value=docker_info.get("image_name", "Unknown")),
        Property(name="Docker Image ID", value=docker_info.get("image_id", "Unknown")),
    ])

    # Add Vulnerability Scan Info as individual properties
    if "error" in vulnerability_scan:
        environment_properties.append(
            Property(name="Vulnerability Scan Error", value=vulnerability_scan["error"])
        )
    else:
        for severity, count in vulnerability_scan.items():
            environment_properties.append(
                Property(name=f"Vulnerability Scan {severity}", value=str(count))
            )
    
    environment_component = Component(
        type=ComponentType.CONTAINER,
        name="Training Environment",
        description="Details of the environment used for training",
        properties=environment_properties
    )
    bom.components.add(environment_component)
    
    # Materials and Products use in DATA and MACHINE LEARNING component =========================================================================================================
    
    # Add materials as components
    material_components = []
    dataset_hash = None
    dataset_definition_hash = None
    architecture_summary = "Unknown"
    dataset_properties = []
    
    for material_path, material_info in bom_data.get("materials", {}).items():
        minio_path = material_path  # Use MinIO path instead of local path
        if material_path.endswith("model.keras"):
            # Use TensorFlow to load the model and extract the architecture summary
            local_path = material_info.get("local_path", "")
            if os.path.exists(local_path):
                try:
                    model = tf.keras.models.load_model(local_path)
                    # Create a formatted string to summarize the model layers
                    architecture_summary_lines = ["Name\tType\tShape"]
                    for layer in model.layers:
                        # Use layer.output.shape to get the output tensor's shape
                        output_shape = getattr(layer.output, 'shape', 'Unknown')
                        architecture_summary_lines.append(
                            f"{layer.name}\t{layer.__class__.__name__}\t{output_shape}"
                        )
                    # Join the lines into a single string
                    architecture_summary = "\n".join(architecture_summary_lines)
                except Exception as e:
                    print(f"Failed to load model and extract architecture summary from {local_path}: {e}")
            continue
        elif material_path.endswith(".zip") or material_path.endswith(".csv"):
            # Handle dataset properties
            dataset_hash = material_info.get("sha256", "")
            dataset_properties.append(Property(name="Dataset MinIO Path", value=minio_path))
        elif material_path.endswith(".yaml"):
            # Handle dataset definition properties
            dataset_definition_hash = material_info.get("sha256", "")
            local_path = material_info.get("local_path", "")
            if os.path.exists(local_path):
                try:
                    with open(local_path, "r") as file:
                        dataset_definition = yaml.safe_load(file)
                        preprocessing = dataset_definition.get("preprocessing", {})
                        dataset_properties.extend([
                            Property(name="Input Shape", value=str(dataset_definition.get("input_shape", "Unknown"))),
                            Property(name="Output Shape", value=str(dataset_definition.get("output_shape", "Unknown"))),
                            Property(name="Preprocessing", value=json.dumps(preprocessing, indent=4)),  # Properly formatted JSON
                        ])
                except Exception as e:
                    print(f"Failed to read dataset definition from {local_path}: {e}")

    # Make DATA component use dataset and dataset definition
    if dataset_hash and dataset_definition_hash:
        data_component = Component(
            type=ComponentType.DATA,
            name="Training Dataset",
            description="Dataset and dataset definition used for training",
            hashes=[
                HashType(alg=HashAlgorithm.SHA_256, content=dataset_hash),
                HashType(alg=HashAlgorithm.SHA_256, content=dataset_definition_hash),
            ],
            properties=dataset_properties + [
                Property(name="Dataset Hash", value=dataset_hash),
                Property(name="Dataset Definition Hash", value=dataset_definition_hash),
            ]
        )
        bom.components.add(data_component)
        material_components.append(data_component)

    # Add products as components
    trained_model_hash = None
    metrics_hash = None
    metrics_properties = []

    for product_path, product_info in bom_data.get("products", {}).items():
        minio_path = product_path  # Use MinIO path instead of local path
        if product_path.endswith("trained_model.keras"):
            trained_model_hash = product_info.get("sha256", "")
        elif product_path.endswith("metrics.json"):
            metrics_hash = product_info.get("sha256", "")
            local_path = product_info.get("local_path", "")
            if os.path.exists(local_path):
                try:
                    with open(local_path, "r") as file:
                        metrics_data = json.load(file)
                        metrics_properties.extend([
                            Property(name=f"Metric: {key}", value=str(value)) for key, value in metrics_data.items()
                        ])
                except Exception as e:
                    print(f"Failed to read metrics from {local_path}: {e}")


    # Combine fit_params, optional_params, and trained model into a MACHINE_LEARNING_MODEL component
    fit_params = bom_data.get("fit_params", {})
    optional_params = bom_data.get("optional_params", {})

    model_component = Component(
        type=ComponentType.MACHINE_LEARNING_MODEL,
        name=optional_params.get("model_name", "Trained Model"),
        version=optional_params.get("model_version", "1.0"),
        description=optional_params.get(
            "model_description", "A trained machine learning model"),
        hashes=[
            HashType(alg=HashAlgorithm.SHA_256, content=trained_model_hash),
            HashType(alg=HashAlgorithm.SHA_256, content=metrics_hash),
        ],
        properties=[
            Property(name="Framework", value=optional_params.get("framework", "Unknown")),
            Property(name="License", value=optional_params.get("license_name", "Unknown")),
            Property(name="Architecture Summary", value=architecture_summary),
            Property(name="Trained Model Hash", value=trained_model_hash),
            Property(name="Metrics Hash", value=metrics_hash),
        ] + metrics_properties + [
            Property(name=f"Fit Param: {key}", value=str(value)) for key, value in fit_params.items()
        ] + [
            Property(name=f"Optional Param: {key}", value=str(value)) for key, value in optional_params.items()
        ]
    )
    bom.components.add(model_component)

    # External references ===================================================================================

    # Add the .link file as an external reference
    attestations = bom_data.get("attestations", {})
    if attestations:
        external_reference = ExternalReference(
            type=ExternalReferenceType.ATTESTATION,
            url=XsUri(attestations.get("minio_path", "Unknown")),
            comment=attestations.get(
                "description", "Attestation file for artifact integrity verification"
            ),
        )
        bom.external_references = [external_reference]
        
    # Relationships (dependencies) =========================================================================================================
    
    # Register dependencies between components
    if model_component and data_component and environment_component:
        bom.register_dependency(model_component, [data_component, environment_component])

    return bom


def serialize_bom(bom, output_path, schema_version=SchemaVersion.V1_6):
    """
    Serialize the BOM to a file in JSON format and validate it.
    Args:
        bom (Bom): The CycloneDX BOM instance.
        output_path (str): The file path to save the serialized BOM.
        schema_version (SchemaVersion): The CycloneDX schema version to use.
    """
    # Generate JSON output
    try:
        json_outputter = JsonV1Dot6(bom)
        serialized_json = json_outputter.output_as_string(indent=4)

        # Manually format the output using json.dumps() to pretty print it
        pretty_json = json.dumps(json.loads(serialized_json), indent=4)

        # Validation
        
        json_validator = JsonStrictValidator(schema_version)
        try:
            validation_errors = json_validator.validate_str(pretty_json)
            if validation_errors:
                print("JSON invalid", "ValidationError:", repr(
                    validation_errors), sep="\n", file=sys.stderr)
                sys.exit(2)
            print("JSON valid")
        except MissingOptionalDependencyException as error:
            print("JSON validation was skipped due to", error)

        # Write the JSON output to the file
        try:
            with open(output_path, "w") as file:
                file.write(pretty_json)
        except FileExistsError:
            print(f"File {output_path} already exists, overwriting...")
            # Remove existing file before writing new one
            os.remove(output_path)
            with open(output_path, "w") as file:
                file.write(pretty_json)
        finally:
            print(f"Final AIBoM generated at {output_path}")

    except MissingOptionalDependencyException as error:
        print(
            f"Serialization failed due to missing optional dependency: {error}")

# deprecated
def sign_bom(bom_path, private_key_path, signature_path):
    """
    Sign the BOM using the platform's private key.

    Args:
        bom_path (str): Path to the BOM file to be signed.
        private_key_path (str): Path to the private key file in PEM format.
        signature_path (str): Path to save the generated signature.
    """
    try:
        # Load the private key from PEM format
        with open(private_key_path, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)
            if not isinstance(private_key, Ed25519PrivateKey):
                raise ValueError("The provided private key is not an Ed25519 key.")

        # Load the BOM content
        with open(bom_path, "r") as bom_file:
            bom_content = bom_file.read()

        # Sign the BOM
        signature = private_key.sign(bom_content.encode())

        # Save the signature to a file
        with open(signature_path, "wb") as sig_file:
            sig_file.write(base64.b64encode(signature))

        print(f"BOM signed and saved to {signature_path}")
    except Exception as e:
        print(f"Failed to sign BOM: {e}")


def sign_and_include_bom_as_property(bom, private_key_path):
    """
    Sign the BOM and include the signature as a property in the BOM metadata.

    Args:
        bom (Bom): The CycloneDX BOM instance.
        private_key_path (str): Path to the private key file in PEM format.
    """
    try:
        # Serialize the BOM to JSON
        json_outputter = JsonV1Dot6(bom)
        serialized_json = json_outputter.output_as_string(indent=4)

        # Load the private key from PEM format
        with open(private_key_path, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)
            if not isinstance(private_key, Ed25519PrivateKey):
                raise ValueError("The provided private key is not an Ed25519 key.")

        # Sign the serialized BOM content
        signature = private_key.sign(serialized_json.encode())
        encoded_signature = base64.b64encode(signature).decode()

        # Add the signature as a property in the BOM metadata
        bom.metadata.properties = bom.metadata.properties.union([
            Property(
                name="BOM Signature",
                value=encoded_signature
            )
        ])

        print("Signature successfully added to the BOM as a property.")
    except Exception as e:
        print(f"Failed to sign and include the BOM: {e}")