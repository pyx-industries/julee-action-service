"""Management API specific settings"""
from functools import lru_cache
import os

from ..types import RepoSet
from ..base_settings import get_base_reposet, validate_base_settings

@lru_cache()
def get_reposet() -> RepoSet:
    """Get repository set for Management API"""
    return get_base_reposet()

def validate_settings() -> None:
    """Validate all required settings including Management API-specific ones"""
    validate_base_settings()
    # Add Management API-specific validation if needed
    api_required = [
        # Add any Management API specific environment variables here
    ]
    missing = [var for var in api_required if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing API-specific variables: {', '.join(missing)}")
