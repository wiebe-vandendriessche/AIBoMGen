FROM tensorflow/tensorflow:2.11.0-gpu

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    inotify-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY test3/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV TF_CPP_MIN_LOG_LEVEL=2

# Copy training script
COPY test3/train.py /app/train.py

# Ensure output directory exists
RUN mkdir -p /output

# Run training
CMD ["python", "train.py"]