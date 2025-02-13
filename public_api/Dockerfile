FROM python:3.11-slim

WORKDIR /app

# Only copy and install requirements
COPY public_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The rest will come from the volume mount
CMD ["uvicorn", "action_service.public_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
