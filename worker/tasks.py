from celery_config import celery_app
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset
import hashlib

@celery_app.task(name="tasks.run_training", time_limit=3600)
def run_training(job_params, expected_hash):
    """Training task - verifies dataset integrity before training"""

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
            output_dir="/app/results",
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
            logging_dir="/app/logs",
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

        trainer.train()

        trainer.save_model("/app/results")

        return {
            "status": "Training completed",
            "dataset_hash": dataset_hash,
            "model_used": model_name
        }

    except Exception as e:
        return {"error": f"An error occurred during training: {str(e)}"}

def compute_dataset_hash(dataset):
    """Compute a hash of the dataset (e.g., based on its content)."""
    sha256 = hashlib.sha256()
    for example in dataset:
        sha256.update(str(example).encode("utf-8"))
    return sha256.hexdigest()
