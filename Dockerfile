# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*  # Clean up unnecessary apt files to reduce image size

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install the Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# Copy the rest of the application code
COPY . .

# Run the application using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5006", "login_service:app"]
