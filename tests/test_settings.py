"""Tests for settings configuration across services"""
import os
import pytest
from unittest import mock
from typing import Dict, Any
from inspect import isclass

from ..types import RepoSet
from ..base_settings import get_base_reposet, validate_base_settings
from ..public_api.settings import get_reposet as get_api_reposet, validate_settings as validate_api_settings
from ..worker_service.settings import get_reposet as get_worker_reposet, validate_settings as validate_worker_settings, get_worker_config
from ..interfaces.repositories import (
    ActionRepository,
    WebhookRepository,
    EventRepository,
    ResultRepository,
    BehaviourRepository,
    CredentialRepository
)

class TestBaseSettings:
    def test_get_api_reposet_extends_base(self, mocker):
        """API reposet should extend base with additional repositories"""
        # Mock boto3 client creation
        mock_boto3 = mocker.patch('boto3.client')
        mock_s3_client = mocker.Mock()
        mock_boto3.return_value = mock_s3_client
        
        # Mock head_bucket to prevent actual S3 calls
        mock_s3_client.head_bucket.return_value = {}
        
        # Now get the reposet
        repos = get_api_reposet()
        
        # Verify base repositories are present and implement correct interfaces
        base_interfaces = {
            "webhook_repository": WebhookRepository,
            "event_repository": EventRepository,
            "result_repository": ResultRepository,
            "action_repository": ActionRepository
        }
        
        for repo_name, interface in base_interfaces.items():
            assert repo_name in repos, f"Missing base repository: {repo_name}"
            assert isinstance(repos[repo_name], interface) or (
                isclass(repos[repo_name]) and issubclass(repos[repo_name], interface)
            ), f"{repo_name} does not implement {interface.__name__}"

    def test_validate_base_settings_with_missing_vars(self):
        """Should raise error when required base vars are missing"""
        # Clear any existing env vars
        required_vars = ['DATABASE_URL', 'REDIS_URL', 'LOG_LEVEL']
        original_env = {}
        for var in required_vars:
            original_env[var] = os.environ.pop(var, None)
            
        with pytest.raises(ValueError) as exc:
            validate_base_settings()
        
        # Restore env vars
        for var, value in original_env.items():
            if value is not None:
                os.environ[var] = value
                
        assert "Missing required environment variables" in str(exc.value)

    def test_validate_base_settings_with_all_vars(self):
        """Should not raise error when all base vars are present"""
        os.environ.update({
            'DATABASE_URL': 'postgresql://localhost/test',
            'REDIS_URL': 'redis://localhost',
            'LOG_LEVEL': 'INFO'
        })
        
        try:
            validate_base_settings()
        except ValueError as e:
            pytest.fail(f"Validation failed unexpectedly: {e}")

class TestPublicApiSettings:
    def test_get_api_reposet_extends_base(self, mocker):
        """API reposet should extend base with additional repositories"""
        # Mock S3WebhookRepository to prevent actual S3 connection attempts
        mock_s3_repo = mocker.patch('action_service.repositories.s3.S3WebhookRepository')
        mock_s3_repo.return_value = mocker.Mock(spec=WebhookRepository)
        
        repos = get_api_reposet()
        
        # Verify base repositories are present and implement correct interfaces
        base_interfaces = {
            "webhook_repository": WebhookRepository,
            "event_repository": EventRepository,
            "result_repository": ResultRepository,
            "action_repository": ActionRepository
        }
        
        for repo_name, interface in base_interfaces.items():
            assert repo_name in repos, f"Missing base repository: {repo_name}"
            assert isinstance(repos[repo_name], interface) or (
                isclass(repos[repo_name]) and issubclass(repos[repo_name], interface)
            ), f"{repo_name} does not implement {interface.__name__}"

    def test_validate_api_settings_with_missing_vars(self):
        """Should raise error when API-specific vars are missing"""
        # Set base vars but clear API vars
        os.environ.update({
            'DATABASE_URL': 'postgresql://localhost/test',
            'REDIS_URL': 'redis://localhost',
            'LOG_LEVEL': 'INFO'
        })
        
        api_vars = ['MINIO_ENDPOINT', 'MINIO_ACCESS_KEY', 'MINIO_SECRET_KEY', 'MINIO_BUCKET']
        original_env = {}
        for var in api_vars:
            original_env[var] = os.environ.pop(var, None)
            
        with pytest.raises(ValueError) as exc:
            validate_api_settings()
            
        # Restore env vars
        for var, value in original_env.items():
            if value is not None:
                os.environ[var] = value
                
        assert "Missing API-specific variables" in str(exc.value)

class TestWorkerSettings:
    def test_get_worker_reposet_extends_base(self):
        """Worker reposet should extend base with behaviour and credential repos"""
        repos = get_worker_reposet()
        
        # Verify base repositories
        base_interfaces = {
            "webhook_repository": WebhookRepository,
            "event_repository": EventRepository,
            "result_repository": ResultRepository,
            "action_repository": ActionRepository
        }
        
        for repo_name, interface in base_interfaces.items():
            assert repo_name in repos, f"Missing base repository: {repo_name}"
            assert isinstance(repos[repo_name], interface) or (
                isclass(repos[repo_name]) and issubclass(repos[repo_name], interface)
            ), f"{repo_name} does not implement {interface.__name__}"
            
        # Verify worker-specific repositories
        worker_interfaces = {
            "behaviour_repository": BehaviourRepository,
            "credential_repository": CredentialRepository
        }
        
        for repo_name, interface in worker_interfaces.items():
            assert repo_name in repos, f"Missing worker repository: {repo_name}"
            assert isinstance(repos[repo_name], interface) or (
                isclass(repos[repo_name]) and issubclass(repos[repo_name], interface)
            ), f"{repo_name} does not implement {interface.__name__}"

    def test_validate_worker_settings_with_missing_vars(self):
        """Should raise error when worker-specific vars are missing"""
        # Set base vars but clear worker vars
        os.environ.update({
            'DATABASE_URL': 'postgresql://localhost/test',
            'REDIS_URL': 'redis://localhost',
            'LOG_LEVEL': 'INFO'
        })
        
        worker_vars = ['CELERY_BROKER_URL', 'WORKER_CONCURRENCY', 'WORKER_QUEUE_NAME']
        original_env = {}
        for var in worker_vars:
            original_env[var] = os.environ.pop(var, None)
            
        with pytest.raises(ValueError) as exc:
            validate_worker_settings()
            
        # Restore env vars
        for var, value in original_env.items():
            if value is not None:
                os.environ[var] = value
                
        assert "Missing worker-specific variables" in str(exc.value)

    def test_get_worker_config_returns_defaults(self):
        """Worker config should use defaults for missing optional vars"""
        # Clear any existing worker env vars
        worker_vars = ['WORKER_CONCURRENCY', 'WORKER_QUEUE_NAME', 'MAX_RETRIES', 'RETRY_DELAY']
        original_env = {}
        for var in worker_vars:
            original_env[var] = os.environ.pop(var, None)
            
        os.environ['CELERY_BROKER_URL'] = 'redis://localhost'
        
        config = get_worker_config()
        
        # Restore env vars
        for var, value in original_env.items():
            if value is not None:
                os.environ[var] = value
                
        assert config['concurrency'] == 4  # Default value
        assert config['queue_name'] == 'actions'  # Default value
        assert config['max_retries'] == 3  # Default value
        assert config['retry_delay'] == 300  # Default value

    @pytest.fixture
    def mock_env(self) -> Dict[str, Any]:
        """Fixture to set up test environment variables"""
        original_env = {}
        test_env = {
            'DATABASE_URL': 'postgresql://localhost/test',
            'REDIS_URL': 'redis://localhost',
            'LOG_LEVEL': 'INFO',
            'CELERY_BROKER_URL': 'redis://localhost:6379/0',
            'WORKER_CONCURRENCY': '2',
            'WORKER_QUEUE_NAME': 'test_queue',
            'MAX_RETRIES': '5',
            'RETRY_DELAY': '60'
        }
        
        # Save original env vars and set test values
        for key, value in test_env.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
            
        yield test_env
        
        # Restore original env vars
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

    def test_get_worker_config_uses_env_vars(self, mock_env):
        """Worker config should use environment variables when present"""
        config = get_worker_config()
        
        assert config['broker_url'] == mock_env['CELERY_BROKER_URL']
        assert config['concurrency'] == int(mock_env['WORKER_CONCURRENCY'])
        assert config['queue_name'] == mock_env['WORKER_QUEUE_NAME']
        assert config['max_retries'] == int(mock_env['MAX_RETRIES'])
        assert config['retry_delay'] == int(mock_env['RETRY_DELAY'])
