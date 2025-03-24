FROM python:3.9

RUN mkdir -p /app /app/logs /app/results /app/uploads


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add non-root user to the worker container
RUN useradd -m aibomgen && chown -R aibomgen:aibomgen /app
RUN chmod -R 777 /app/logs /app/results /app/uploads

USER aibomgen

COPY . .
