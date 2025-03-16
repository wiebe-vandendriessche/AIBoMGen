FROM python:3.9

RUN mkdir -p /app


WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Add non-root user to the worker container
RUN useradd -m aibomgen && chown -R aibomgen:aibomgen /app
USER aibomgen

COPY . .
