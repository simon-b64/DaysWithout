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

# Copy config file if it exists (optional)
# Uncomment the next line if you have an instance/config.py file
# COPY instance/config.py ./instance/config.py

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Initialize the database
RUN flask --app app init-db

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0"]

