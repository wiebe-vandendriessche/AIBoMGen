FROM python:3.9

RUN mkdir -p /app /app/logs /app/results


WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Add non-root user to the worker container
RUN useradd -m aibomgen && chown -R aibomgen:aibomgen /app
RUN chmod -R 777 /app/logs /app/results

USER aibomgen

COPY . .
RUN chmod -R 777 /app/logs /app/results
