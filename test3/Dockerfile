FROM tensorflow/tensorflow:2.11.0-gpu

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    inotify-tools \
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY test3/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV GIT_PYTHON_REFRESH=quiet

COPY test3/train.py /app/train.py
COPY test3/train_wrapper.py /app/train_wrapper.py

# Ensure output directory exists
RUN mkdir -p /output

# Expose port for potential MLflow UI or other purposes
EXPOSE 5000

# Run training through the wrapper
CMD ["python", "train_wrapper.py"]