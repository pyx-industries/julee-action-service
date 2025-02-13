FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY worker_service/requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Start Celery worker with auto-reload for development
CMD ["watchmedo", "auto-restart", "--directory=/app/", "--pattern=*.py", "--recursive", "--", "celery", "-A", "worker_service.main", "worker", "-l", "INFO"]
FROM python:3.11-slim

WORKDIR /app

# Only copy and install requirements
COPY worker_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The rest will come from the volume mount
CMD ["watchmedo", "auto-restart", "--directory=/app/", "--pattern=*.py", "--ignore-patterns=*~", "--recursive", "--", "celery", "-A", "action_service.worker_service.worker", "worker", "-l", "INFO"]
