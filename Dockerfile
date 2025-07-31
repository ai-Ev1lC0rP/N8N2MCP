# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies, skipping triton if it fails
RUN pip install --no-cache-dir -r requirements.txt || \
    (grep -v "triton" requirements.txt > /tmp/requirements.txt && \
     pip install --no-cache-dir -r /tmp/requirements.txt)

# Copy the rest of the application's code into the container at /app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run main.py when the container launches
CMD ["python", "main.py"]
