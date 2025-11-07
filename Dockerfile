# Use an official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY app/ ./app/
COPY pyproject.toml .

# Create instance directory for the SQLite database
RUN mkdir -p /app/instance

# Initialize the database
RUN flask --app app init-db

# Expose port 5000
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=4", "app:app"]

