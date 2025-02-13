"""Worker service specific settings"""
from functools import lru_cache
import os

from ..types import RepoSet
from ..base_settings import get_base_reposet, validate_base_settings
from ..repositories.behaviour import HardcodedBehaviourCatalogue

# Map protocols to their repository implementations
PROTOCOL_REPOSITORIES = {
    'http': {
        'action_repo': 'action_service.repositories.http.HttpActionRepository',
        'event_repo': 'action_service.repositories.http.HttpEventRepository'
    },
    's3': {
        'action_repo': 'action_service.repositories.s3.S3WebhookRepository',
        'event_repo': 'action_service.repositories.events.EventRepository'
    },
    'postgres': {
        'action_repo': 'action_service.repositories.postgres.PostgresStreamRepository',
        'event_repo': 'action_service.repositories.events.EventRepository'
    }
}

@lru_cache()
def get_reposet() -> RepoSet:
    """Get repository set for worker, extending base repos"""
    repos = dict(get_base_reposet())  # Convert to mutable dict
    
    # Add worker-specific repositories
    repos["behaviour_repository"] = HardcodedBehaviourCatalogue()
    
    # Add credential repository
    from ..repositories.memory import InMemoryCredentialRepository
    repos["credential_repository"] = InMemoryCredentialRepository()
    
    return repos

def validate_settings() -> None:
    """Validate all required settings including worker-specific ones"""
    validate_base_settings()
    # Add worker-specific validation
    worker_required = [
        'CELERY_BROKER_URL',
        'WORKER_CONCURRENCY',
        'WORKER_QUEUE_NAME'
    ]
    missing = [var for var in worker_required if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing worker-specific variables: {', '.join(missing)}")

def get_worker_config() -> dict:
    """Get worker-specific configuration"""
    return {
        'broker_url': os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),  # Updated default value
        'concurrency': int(os.getenv('WORKER_CONCURRENCY', '4')),
        'queue_name': os.getenv('WORKER_QUEUE_NAME', 'actions'),
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'retry_delay': int(os.getenv('RETRY_DELAY', '300'))  # seconds
    }
