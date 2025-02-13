"""Public API specific settings"""
from functools import lru_cache
import os

from ..types import RepoSet
from ..base_settings import get_base_reposet, validate_base_settings
from ..repositories.s3 import S3WebhookRepository

@lru_cache()
def get_reposet() -> RepoSet:
    """Get repository set for API, overriding webhook repo with S3 implementation"""
    repos = get_base_reposet()
    # Override webhook repository with S3 implementation
    repos["webhook_repository"] = S3WebhookRepository(
        endpoint_url=os.getenv('MINIO_ENDPOINT', 'http://minio:9000'),
        aws_access_key_id=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
        aws_secret_access_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
        bucket=os.getenv('MINIO_BUCKET', 'webhooks'),
        use_ssl=os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
    )
    return repos

def validate_settings() -> None:
    """Validate all required settings including API-specific ones"""
    validate_base_settings()
    # Add API-specific validation
    api_required = [
        'MINIO_ENDPOINT',
        'MINIO_ACCESS_KEY',
        'MINIO_SECRET_KEY',
        'MINIO_BUCKET'
    ]
    missing = [var for var in api_required if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing API-specific variables: {', '.join(missing)}")
