"""Celery worker configuration"""
from celery import Celery
from .settings import get_reposet

# Initialize Celery app
app = Celery('action_service')

# Configure Celery
app.conf.update(
    broker_url='redis://redis:6379/0',
    result_backend='redis://redis:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import tasks
from .tasks import process_action  # noqa

if __name__ == '__main__':
    app.start()
