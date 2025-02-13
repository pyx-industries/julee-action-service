"""Tests for S3WebhookRepository"""
from __future__ import annotations

# Configure warnings before any other imports
import warnings
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*utcnow.*",
    module="botocore.*"
)

from datetime import UTC
import pytest
import boto3
from moto import mock_aws
from botocore.client import Config

from action_service.domain import Webhook
from action_service.repositories.s3 import S3WebhookRepository

@pytest.fixture
def s3_client():
    """Create mocked S3 client"""
    with mock_aws():
        s3 = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
        # Create the test bucket right here in the fixture
        s3.create_bucket(Bucket='test-bucket')
        yield s3

@pytest.fixture
def webhook_repo(s3_client):
    """Create repository instance with mocked S3"""
    repo = S3WebhookRepository(
        endpoint_url=None,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        bucket='test-bucket',
        use_ssl=False
    )
    repo.client = s3_client  # Use the mocked client directly
    return repo

def test_get_webhook_not_found(webhook_repo):
    """Should return None for non-existent webhook"""
    assert webhook_repo.get_webhook('missing') is None

def test_store_and_get_webhook(webhook_repo):
    """Should store and retrieve webhook correctly"""
    # Create test webhook
    webhook = Webhook(
        id='test-hook',
        key='secret-key',
        config={'url': 'http://test.com'}
    )
    
    # Store webhook
    webhook_repo.store_webhook(webhook)
    
    # Retrieve webhook
    retrieved = webhook_repo.get_webhook('test-hook')
    assert retrieved is not None
    assert retrieved.id == webhook.id
    assert retrieved.key == webhook.key
    assert retrieved.config == webhook.config

def test_validate_key(webhook_repo):
    """Should validate webhook key correctly"""
    # Create test webhook
    webhook = Webhook(
        id='test-hook',
        key='secret-key',
        config={}
    )
    webhook_repo.store_webhook(webhook)
    
    # Test validation
    assert webhook_repo.validate_key('test-hook', 'secret-key') is True
    assert webhook_repo.validate_key('test-hook', 'wrong-key') is False
    assert webhook_repo.validate_key('missing', 'any-key') is False

def test_delete_webhook(webhook_repo):
    """Should delete webhook correctly"""
    # Create test webhook
    webhook = Webhook(
        id='test-hook',
        key='secret-key',
        config={}
    )
    webhook_repo.store_webhook(webhook)
    
    # Delete webhook
    webhook_repo.delete_webhook('test-hook')
    
    # Verify deletion
    assert webhook_repo.get_webhook('test-hook') is None

def test_list_webhooks(webhook_repo):
    """Should list all webhooks correctly"""
    # Create test webhooks
    webhooks = [
        Webhook(id='hook1', key='key1', config={}),
        Webhook(id='hook2', key='key2', config={})
    ]
    for webhook in webhooks:
        webhook_repo.store_webhook(webhook)
    
    # List webhooks
    listed = webhook_repo.list_webhooks()
    assert len(listed) == 2
    assert {w.id for w in listed} == {'hook1', 'hook2'}
