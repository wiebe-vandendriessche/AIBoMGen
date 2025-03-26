from celery_config import celery_app
import os
import tensorflow as tf
import time

UPLOAD_DIR = "/app/uploads"  # Shared volume location

@celery_app.task(name="tasks.run_training", time_limit=3600)
def run_training(model_filename, dataset_filename):
    """Training task"""
    try:
        model_path = os.path.join(UPLOAD_DIR, model_filename)
        dataset_path = os.path.join(UPLOAD_DIR, dataset_filename)

        time.sleep(2)

        print(model_filename)
        print(dataset_filename)
        print(f"Model path: {model_path}")
        print(f"Dataset path: {dataset_path}")
        print(f"Model file permissions: {oct(os.stat(model_path).st_mode)}")
        print(f"Dataset file permissions: {oct(os.stat(dataset_path).st_mode)}")

        # Ensure files exists
        if not os.path.exists(model_path):
            return {"error": "Model file not found", "model": model_path}
        if not os.path.exists(dataset_path):
            return {"error": "Dataset file not found", "dataset": dataset_path}

        # Load model in save mode (DON'T ALLOW FOR LAMBDA LAYERS)
        try:
            model = tf.keras.models.load_model(model_path, safe_mode=True)
        except Exception as e:
            return {"error": f"Model loading failed: {str(e)}"}

        model.summary()

        # Load TFRecord dataset
        dataset = _load_tfrecord(dataset_path)


            # Determine fit parameters based on dataset type
        batch_size = 32  # Example, this could also be dynamic
        epochs = 10  # Example, this can also be set from an API parameter
        steps_per_epoch = None  # This could be calculated based on the dataset

        # model.fit(
        #     x=None, # data (could be: numpy array, tensor, dict mapping, tf.data.Dataset, keras.utils.PyDataset)
        #     y=None, # label (could be: numpy array, (if x is dataset,generator or pydataset, y should not be specified))
        #     batch_size=None, # Number of samples per gradient update, default 32 (if x is dataset,generator or pydataset, batch_size should not be specified)
        #     epochs=1, # Number of epochs to train
        #     verbose='auto', # 0: silent, 1: progress bar, 2: one line per epoch (when writing to file)
        #     callbacks=None, # (tensorboard)
        #     validation_split=0.0, # Fraction of train data used to validate (if x is dataset,generator or pydataset, validation_split should not be specified)
        #     validation_data=None, # data to val (could be: numpy array, tensor, dict mapping, tf.data.Dataset, keras.utils.PyDataset)
        #     shuffle=True, # shuffle x after each epoch (if x is dataset,generator or pydataset, shuffle should not be specified)
        #     class_weight=None, # Optional dictionary mapping class indices (integers) to a weight (float) value, used for weighting the loss function (during training only). This can be useful to tell the model to "pay more attention" to samples from an under-represented class.
        #     sample_weight=None, # Optional NumPy array of weights for the training samples, used for weighting the loss function (during training only). Y
        #     initial_epoch=0, # Epoch at which to start training (useful for resuming a previous training run).
        #     steps_per_epoch=None, # Total number of steps (batches of samples) before declaring one epoch finished and starting the next epoch. Epoch at which to start training (useful for resuming a previous training run).
        #     validation_steps=None, # Only relevant if validation_data is provided. Total number of steps (batches of samples) to draw before stopping when performing validation at the end of every epoch.
        #     validation_batch_size=None, # Number of samples per validation batch.
        #     validation_freq=1 # Specifies how many training epochs to run before a new validation run is performed
        # )

        model.fit(
            x=dataset,  # Automatically use the preprocessed dataset
            epochs=epochs,
            batch_size=batch_size,
            steps_per_epoch=steps_per_epoch,
            verbose=1
        )

        return {"status": "Training completed", "model": model_filename, "dataset": dataset_filename}
    except Exception as e:
        return {"error": f"An error occurred during training: {str(e)}"}
    finally:
        # Cleanup: Delete the files after processing (always occurs, even if there is an error)
        if os.path.exists(model_path):
            try:
                os.remove(model_path)
                print(f"Model file {model_filename} removed.")
            except Exception as e:
                print(f"Error removing model file {model_filename}: {str(e)}")

        if os.path.exists(dataset_path):
            try:
                os.remove(dataset_path)
                print(f"Dataset file {dataset_filename} removed.")
            except Exception as e:
                print(f"Error removing dataset file {dataset_filename}: {str(e)}")

def _load_tfrecord(file_path, batch_size=32):
    """Helper function to load a TFRecord file and return a tf.data.Dataset."""
    raw_dataset = tf.data.TFRecordDataset(file_path)

    # Define the feature description to match the TFRecord dataset generated above
    feature_description = {
        'feature': tf.io.FixedLenFeature([10], tf.float32),  # 10 features (10 float values)
        'label': tf.io.FixedLenFeature([1], tf.int64),  # 1 label (binary classification)
    }

    def _parse_function(proto):
        # Parse the input tf.Example proto using the feature description
        parsed_features = tf.io.parse_single_example(proto, feature_description)
        return parsed_features['feature'], parsed_features['label']  # Return feature and label

    # Parse the TFRecord file and create a dataset
    dataset = raw_dataset.map(_parse_function)

    # Batch the dataset and shuffle it for training
    dataset = dataset.batch(batch_size).shuffle(buffer_size=1000)

    return dataset