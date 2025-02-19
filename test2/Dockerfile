FROM python:3.8-slim

WORKDIR /app

COPY test2/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY test2/train.py /app/train.py

CMD ["python", "train.py"]