FROM tensorflow/tensorflow:2.11.0-gpu

WORKDIR /app

COPY test/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV TF_CPP_MIN_LOG_LEVEL=2

COPY test/train.py /app/train.py

CMD ["python", "train.py"]