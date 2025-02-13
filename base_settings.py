"""Base settings shared across Action Service components"""
from functools import lru_cache
from typing import Dict, Any, Optional
import os
from types import MappingProxyType

from .types import RepoSet
from .repositories.memory import (
    InMemoryWebhookRepository,
    InMemoryEventRepository,
    InMemoryResultRepository,
    InMemoryActionRepository
)

def create_reposet(**repos) -> RepoSet:
    """Create a new immutable repository set with arbitrary repositories"""
    return MappingProxyType(repos)

def create_mutable_reposet(**repos) -> Dict[str, Any]:
    """Create a new mutable repository set with arbitrary repositories"""
    return dict(repos)

@lru_cache()
def get_base_reposet() -> Dict[str, Any]:  # Change return type from RepoSet
    """Get default repository set shared across components"""
    webhook_repo = InMemoryWebhookRepository()
    event_repo = InMemoryEventRepository()
    result_repo = InMemoryResultRepository()
    action_repo = InMemoryActionRepository()
    
    return {  # Return mutable dict instead of MappingProxyType
        "webhook_repository": webhook_repo,
        "event_repository": event_repo,
        "result_repository": result_repo,
        "action_repository": action_repo
    }

def validate_base_settings() -> None:
    """Validate common required environment variables"""
    required_vars = [
        'DATABASE_URL',
        'REDIS_URL',
        'LOG_LEVEL'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
