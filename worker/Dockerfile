FROM python:3.9


RUN mkdir -p /app /app/logs /app/results /app/uploads

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Add a non-root user with a specific UID and GID for better security
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID aibomgen && \
    useradd -m -u $UID -g $GID aibomgen && \
    chown -R aibomgen:aibomgen /app/uploads

# Ensure the worker has full permissions to the necessary directories
RUN chmod -R 770 /app/logs /app/results /app/uploads


# Copy the entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Switch to the non-root user
USER aibomgen

# Copy the application code
COPY . .


# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]