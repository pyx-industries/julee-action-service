FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY api_service/requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Expose API port
EXPOSE 8000

# Start FastAPI server with hot reload for development
CMD ["uvicorn", "api_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
