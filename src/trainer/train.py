import os
import logging
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
import sys

# Logging setup
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()

# Environment variables
model_name = os.getenv("MODEL_NAME", "bert-base-uncased")
d_p = os.getenv("DATASET_PATH", "/mnt/dataset/imdb")

# Check dataset existence
if not os.path.exists(d_p):
    logger.error(f"Dataset path does not exist: {d_p}")
    raise ValueError("Dataset path does not exist.")

def load_arrow_dataset(dataset_path):
    """Loads an Arrow dataset based on the provided files."""
    # Check for expected files in the directory
    train_file = None
    test_file = None

    # Log the files in the dataset directory
    logger.info(f"Checking dataset directory: {dataset_path}")
    logger.info(f"Files in directory: {os.listdir(dataset_path)}")

    # Look for specific Arrow dataset files
    for file in os.listdir(dataset_path):
        if "train" in file and file.endswith(".arrow"):
            train_file = os.path.join(dataset_path, file)
        elif "test" in file and file.endswith(".arrow"):
            test_file = os.path.join(dataset_path, file)

    if train_file and test_file:
        # Load the dataset with the train and test splits
        return load_dataset("arrow", data_files={"train": train_file, "test": test_file})
    elif train_file:
        # If only the train file exists, load it
        return load_dataset("arrow", data_files={"train": train_file})
    else:
        raise ValueError("No valid Arrow dataset files found.")

# Load dataset
dataset = load_arrow_dataset(d_p)
logger.info(f"Loaded dataset with {len(dataset['train'])} training samples.")

# Model & Tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
logger.info(f"Loaded model: {model_name}")

# Training arguments
output_dir = "/mnt/trained_model"  # Output directory inside container
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=int(os.getenv("EPOCHS", 3)),
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    evaluation_strategy="epoch",
    learning_rate=float(os.getenv("LEARNING_RATE", 0.0001)),
    logging_dir="/logs",  # Logs directory inside container
    logging_steps=10
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset.get("test", None)
)

# Start training
trainer.train()

# Save model
trainer.save_model(output_dir)
logger.info(f"Model saved at {output_dir}")
