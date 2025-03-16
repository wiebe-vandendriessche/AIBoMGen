from _typeshed import SupportsWrite

from celery_config import celery_app
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset
import hashlib
from datetime import datetime
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes as crypt_hashes
from cryptography.hazmat.backends import default_backend

@celery_app.task(name="tasks.run_training", time_limit=3600)
def run_training(job_params, expected_hash):
    """Training task"""

    job_uuid = run_training.request.id

    model_name = job_params["model_name"]
    dataset_name = job_params["dataset_name"]
    num_train_epochs = job_params["num_train_epochs"]
    per_device_train_batch_size = job_params["per_device_train_batch_size"]
    per_device_eval_batch_size = job_params["per_device_eval_batch_size"]
    learning_rate = job_params["learning_rate"]
    logging_steps = job_params["logging_steps"]
    save_steps = job_params["save_steps"]
    eval_steps = job_params["eval_steps"]
    warmup_steps = job_params["warmup_steps"]
    weight_decay = job_params["weight_decay"]
    max_grad_norm = job_params["max_grad_norm"]
    eval_strategy = job_params["evaluation_strategy"]
    logging_strategy = job_params["logging_strategy"]

    try:
        dataset = load_dataset(dataset_name)


        # reduced for testing purposes
        reduced_train = dataset["train"].select(range(256))
        reduced_test = dataset["test"].select(range(32))

        dataset_hash = compute_dataset_hash(dataset)
        if dataset_hash != expected_hash:
            return {"error": "Dataset hash mismatch! Possible tampering detected."}

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        def tokenize_function(example):
            return tokenizer(example["text"], padding="max_length", truncation=True)

        tokenized_train = reduced_train.map(tokenize_function, batched=True)
        tokenized_test = reduced_test.map(tokenize_function, batched=True)

        training_args = TrainingArguments(
            output_dir=f"/app/results/{job_uuid}",
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=per_device_train_batch_size,
            per_device_eval_batch_size=per_device_eval_batch_size,
            learning_rate=learning_rate,
            logging_steps=logging_steps,
            save_steps=save_steps,
            eval_steps=eval_steps,
            warmup_steps=warmup_steps,
            weight_decay=weight_decay,
            max_grad_norm=max_grad_norm,
            eval_strategy=eval_strategy,
            logging_dir=f"/app/logs/{job_uuid}",
            save_strategy="steps",
            logging_strategy=logging_strategy,
            log_level="info"
        )

        # training_args = TrainingArguments(
        #     output_dir="./results",
        #     num_train_epochs=1,
        #     per_device_train_batch_size=4,
        #     per_device_eval_batch_size=4,
        #     logging_dir="./logs",
        #     save_strategy="no",  # Disable saving every epoch
        # )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_test
        )

        training_time = datetime.now().isoformat()

        trainer.train()

        trainer.save_model(f"/app/results/{job_uuid}")

        # Create the AIBoM
        aibom = generate_aibom(
            model_name=model_name,
            dataset_name=dataset_name,
            dataset_hash=dataset_hash,
            training_params=job_params,
            model_used=model_name,
            training_time=training_time
        )

        signature = sign_aibom(aibom)

        # Add the signature to the AIBoM
        aibom["signature"] = signature.hex()

        # Save AIBoM as a JSON file
        aibom_file = f"/app/results/{job_uuid}/aibom.json"
        with open(aibom_file, "w", encoding="utf-8") as f: # type: SupportsWrite[str]
            json.dump(aibom, f, indent=4)

        return {
            "status": "Training completed",
            "dataset_hash": dataset_hash,
            "model_used": model_name,
            "aibom": aibom_file
        }

    except Exception as e:
        return {"error": f"An error occurred during training: {str(e)}"}

def compute_dataset_hash(dataset):
    """Compute a hash of the dataset (e.g., based on its content)."""
    sha256 = hashlib.sha256()
    for example in dataset:
        sha256.update(str(example).encode("utf-8"))
    return sha256.hexdigest()

def generate_aibom(model_name, dataset_name, dataset_hash, training_params, model_used, training_time):
    """Generate the AI Bill of Materials (AIBoM)"""
    aibom = {
        "model_name": model_name,
        "dataset_name": dataset_name,
        "dataset_hash": dataset_hash,
        "training_parameters": training_params,
        "model_used": model_used,
        "training_time": training_time,
        "generated_at": datetime.now().isoformat(),
    }
    return aibom

def load_private_key():
    """Load a private key for signing the AIBoM"""
    # private_key_path = "/path/to/private_key.pem"
    #
    # with open(private_key_path, "rb") as key_file:
    #     private_key = serialization.load_pem_private_key(
    #         key_file.read(),
    #         password=None,
    #         backend=default_backend()
    #     )

    # for now just generate it each time
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    return private_key

def sign_aibom(aibom):
    """Sign the AIBoM using a private key"""
    # Serialize AIBoM (ensure it's in a stable format)
    aibom_json = json.dumps(aibom, sort_keys=True)

    # Hash the serialized AIBoM
    aibom_hash = hashlib.sha256(aibom_json.encode("utf-8")).digest()

    # Load the private key and sign the hash
    private_key = load_private_key()

    signature = private_key.sign(
        aibom_hash,
        padding.PSS(
            mgf=padding.MGF1(crypt_hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        algorithm=hashes.SHA256()
    )

    return signature