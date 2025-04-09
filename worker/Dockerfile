FROM python:3.9

# Create the necessary directory for shared volume
RUN mkdir -p /app /app/uploads

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy the application code
COPY . .

# Run as root (default user in Docker)
ENTRYPOINT ["/app/entrypoint.sh"]