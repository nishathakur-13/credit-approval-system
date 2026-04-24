# Use the official Python image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files 
# and to ensure logs are sent straight to the terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for PostgreSQL and building Python packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app/

# The command to run the application using Gunicorn
# This binds the app to port 10000, which is what Render expects
CMD ["gunicorn", "credit_approval.wsgi:application", "--bind", "0.0.0.0:10000"]