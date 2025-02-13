"""Tests for repository set functionality"""
import pytest
from types import MappingProxyType
from typing import Dict, Any

from ..base_settings import create_reposet, get_base_reposet
from ..repositories.memory import (
    InMemoryWebhookRepository,
    InMemoryEventRepository,
    InMemoryResultRepository,
    InMemoryActionRepository
)

class TestRepoSet:
    def test_create_reposet_empty(self):
        """Should create empty immutable repo set"""
        repos = create_reposet()
        
        # Test immutability
        with pytest.raises((TypeError, AttributeError)):
            repos['new_key'] = 'value'
            
        assert len(repos) == 0

    def test_create_reposet_with_repos(self):
        """Should create repo set with provided repos"""
        webhook_repo = InMemoryWebhookRepository()
        event_repo = InMemoryEventRepository()
        
        repos = create_reposet(
            webhook_repository=webhook_repo,
            event_repository=event_repo
        )
        
        assert isinstance(repos, (dict, MappingProxyType))
        assert len(repos) == 2
        assert repos["webhook_repository"] == webhook_repo
        assert repos["event_repository"] == event_repo

    def test_get_base_reposet(self):
        """Should return cached repo set with all base repos"""
        repos = get_base_reposet()
        
        # Check all required repos are present
        assert "webhook_repository" in repos
        assert "event_repository" in repos
        assert "result_repository" in repos
        assert "action_repository" in repos
        
        # Check repo types
        assert isinstance(repos["webhook_repository"], InMemoryWebhookRepository)
        assert isinstance(repos["event_repository"], InMemoryEventRepository)
        assert isinstance(repos["result_repository"], InMemoryResultRepository)
        assert isinstance(repos["action_repository"], InMemoryActionRepository)

    def test_reposet_dict_operations(self):
        """Should support standard dict operations"""
        repos = create_reposet(
            test_repo="test"
        )
        
        # Test get
        assert repos.get("test_repo") == "test"
        assert repos.get("missing", "default") == "default"
        
        # Test in operator
        assert "test_repo" in repos
        assert "missing" not in repos
        
        # Test dict access
        assert repos["test_repo"] == "test"
        with pytest.raises(KeyError):
            _ = repos["missing"]

    def test_reposet_immutability(self):
        """Should prevent modification after creation"""
        repos = create_reposet(test_repo="test")
        
        # Test adding new key
        with pytest.raises(TypeError):
            repos["new_key"] = "value"
            
        # Test modifying existing key
        with pytest.raises(TypeError):
            repos["test_repo"] = "new_value"
            
        # Test deleting key
        with pytest.raises(TypeError):
            del repos["test_repo"]

    def test_reposet_caching(self):
        """Should cache base reposet"""
        repos1 = get_base_reposet()
        repos2 = get_base_reposet()
        
        # Should return same instance
        assert repos1 is repos2
