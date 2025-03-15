FROM python:3.12-slim

WORKDIR /trainer

COPY requirements.txt /trainer/

# Install dependencies directly (since trainer files are mounted)
RUN pip install --no-cache-dir -r /trainer/requirements.txt

COPY . /trainer/

CMD ["python", "/trainer/train.py"]
