FROM python:3.8-slim

WORKDIR /app

COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Install cryptography package
RUN pip install cryptography

# Command to run the application
CMD ["gunicorn", "-w", "1", "flask_app:app", "-b", "0.0.0.0:5000"]
