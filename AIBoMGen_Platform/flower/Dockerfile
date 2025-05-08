FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only the dependencies required for Flower
RUN pip install --no-cache-dir celery flower python-dotenv

# Expose the Flower port
EXPOSE 5555

# Copy the flower code
COPY ./flower /app

# Default command for Flower
ENTRYPOINT ["celery", "-A", "celery_config", "flower"]