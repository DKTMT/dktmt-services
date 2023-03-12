# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Set environment variables to ensure the application runs in a production-like environment
ENV DJANGO_SETTINGS_MODULE=predict_service.settings
ENV PYTHONUNBUFFERED=1

# Install required packages and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Expose the port 8000 for the Django development server
EXPOSE 8000

# Define the command to run the application
CMD python manage.py makemigrations\
    && python manage.py migrate\
    && python manage.py runserver 0.0.0.0:8000
