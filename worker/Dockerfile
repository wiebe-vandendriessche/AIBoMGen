FROM python:3.9

WORKDIR /app

# Copy requirements and install dependencies
COPY ./worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the shared directory
COPY ./shared /app/shared

# Copy the worker code
COPY ./worker /app

# Run as root (default user in Docker)
ENTRYPOINT ["/app/entrypoint.sh"]