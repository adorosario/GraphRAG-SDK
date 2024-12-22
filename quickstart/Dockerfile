FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/logs /app/runs

# Copy the rest of the application
COPY . .

# Set permissions for the directories
RUN chmod -R 777 /app/logs /app/runs

# Drop into bash
CMD ["/bin/bash"]
