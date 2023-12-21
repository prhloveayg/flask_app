FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# Install cryptography package
RUN pip install cryptography

CMD ["python", "subscriber.py"]


