import os
from datasets import Dataset
from transformers import BertForSequenceClassification, Trainer, TrainingArguments
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Define the dataset path inside the container
dataset_path = os.getenv("DATASET_PATH", "/dataset")
logger.info(f"Dataset path: {dataset_path}")

# Check if dataset_path is a directory or a single file
try:
    if os.path.isdir(dataset_path):
        # If it's a directory, load the entire dataset (e.g., using Dataset.from_parquet or other methods)
        dataset_files = [os.path.join(dataset_path, f) for f in os.listdir(dataset_path) if f.endswith(".parquet")]
        if not dataset_files:
            raise ValueError("No parquet files found in the specified directory.")
        dataset = Dataset.from_parquet(dataset_files)  # Example of loading multiple files
        logger.info(f"Loaded dataset with {len(dataset)} examples.")
    else:
        # If it's a single file, load it directly
        dataset = Dataset.from_parquet(dataset_path)
        logger.info(f"Loaded dataset from file: {dataset_path}.")

except Exception as e:
    logger.error(f"Error loading dataset: {e}")
    raise

# Load the model
try:
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
    logger.info(f"Model loaded successfully: bert-base-uncased")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

# Define training arguments with explicit logging
output_model_path = os.getenv("MODEL_SAVE_PATH", "/output/trained_model")  # Define the save path inside the mounted volume
logger.info(f"Saving model to: {output_model_path}")

# Ensure the save directory exists
os.makedirs(output_model_path, exist_ok=True)
logger.info(f"Ensured model save path exists at {output_model_path}.")

training_args = TrainingArguments(
    output_dir='./results',  # Temporary local directory inside the container
    num_train_epochs=int(os.getenv("epochs", 3)),
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    evaluation_strategy="epoch",
    learning_rate=float(os.getenv("learning_rate", 0.001)),
    logging_dir='./logs',  # Directory for logs
    logging_steps=10,  # Log every 10 steps
    logging_first_step=True,  # Log the first step
    report_to="tensorboard",  # Enable reporting to TensorBoard (optional)
)

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset
)

# Train the model
try:
    logger.info("Starting training...")
    trainer.train()
    logger.info("Training complete.")

    # Check if the model is saved to the mounted folder
    logger.info("Saving model to the mounted folder...")
    trainer.save_model(output_model_path)  # Save to the mounted folder

    # Verify if the model is saved
    if os.path.exists(output_model_path):
        logger.info(f"Model saved successfully at {output_model_path}.")
    else:
        logger.error(f"Model saving failed. No model found at {output_model_path}.")

except Exception as e:
    logger.error(f"Error during training: {e}")
    raise
