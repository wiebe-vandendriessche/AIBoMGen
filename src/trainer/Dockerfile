FROM python:3.12-slim

WORKDIR /trainer

COPY src/trainer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/trainer/ .

CMD ["python", "train.py"]
