FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY test/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the training script into the container
COPY test/train.py /app/train.py

# Set the command to run the training script
CMD ["python", "train.py"]