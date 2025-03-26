FROM python:3.9

RUN mkdir -p /app /app/logs /app/results /app/uploads


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure all files and directories are fully accessible
RUN chmod -R 777 /app

# No CMD since Celery is handled via docker-compose
