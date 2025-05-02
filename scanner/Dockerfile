FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Docker CLI and dependencies
RUN apt-get update && apt-get install -y docker.io curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY ./scanner/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the shared directory
COPY ./shared /app/shared

# Copy the scanner code
COPY ./scanner /app