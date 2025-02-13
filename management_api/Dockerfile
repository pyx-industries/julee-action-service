FROM python:3.11-slim

WORKDIR /app

COPY management_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/action_service/

ENV PYTHONPATH=/app

CMD ["uvicorn", "action_service.management_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
