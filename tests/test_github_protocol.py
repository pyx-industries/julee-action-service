import os
import pytest
from unittest.mock import Mock, patch
from ..protocols.github import GithubProtocol
from ..domain import (
    Action, ActionType, Protocol, ConfigValue,
    ProtocolConfigSchema, PropertyDefinition
)

def test_github_protocol_config_validation(catalogue):
    """Test GitHub protocol configuration validation"""
    valid_config = [
        ConfigValue(name="repo_owner", value="test-org"),
        ConfigValue(name="repo_name", value="test-repo"),
        ConfigValue(name="title", value="Test Issue"),
        ConfigValue(name="body", value="Test content"),
        ConfigValue(name="labels", value=["bug"]),
        ConfigValue(name="assignees", value=["testuser"]),
        ConfigValue(name="token", value="ghp_test123")
    ]
    
    protocol = GithubProtocol(valid_config)
    assert protocol.validate_config() == True
    
    # Test invalid config
    invalid_config = [
        ConfigValue(name="title", value="Test Issue")  # Missing required fields
    ]
    protocol = GithubProtocol(invalid_config)
    assert protocol.validate_config() == False
    assert "Missing required config" in protocol.last_error

def test_github_template_loading(catalogue):
    """Test template loading and rendering"""
    protocol = GithubProtocol({
        "repo_owner": "test-org",
        "repo_name": "test-repo",
        "token": "ghp_test123"
    })
    
    # Verify template directory exists
    template_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'protocols/github/templates'
    )
    assert os.path.exists(template_dir)
    
    # Verify templates exist
    assert os.path.exists(os.path.join(template_dir, 'issue.jinja'))
    assert os.path.exists(os.path.join(template_dir, 'pull_request.jinja'))
    assert os.path.exists(os.path.join(template_dir, 'comment.jinja'))

def test_github_issue_creation(catalogue):
    """Test GitHub issue creation flow"""
    with patch('httpx.post') as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "number": 1,
            "html_url": "https://github.com/test-org/test-repo/issues/1"
        }
        
        protocol = catalogue.get_protocol("github")
        action = Action(
            id="test-1",
            name="Create Test Issue",
            description="Test issue creation",
            action_type=catalogue.get_action_type("publish"),
            protocol=protocol,
            config=[
                ConfigValue(name="repo_owner", value="test-org"),
                ConfigValue(name="repo_name", value="test-repo"),
                ConfigValue(name="title", value="Test Issue"),
                ConfigValue(name="body", value="Test content"),
                ConfigValue(name="labels", value=["bug"]),
                ConfigValue(name="assignees", value=["testuser"]),
                ConfigValue(name="token", value="ghp_test123")
            ],
            schema=ProtocolConfigSchema(
                properties={
                    "repo_owner": PropertyDefinition(type="str"),
                    "repo_name": PropertyDefinition(type="str"),
                    "title": PropertyDefinition(type="str"),
                    "body": PropertyDefinition(type="str"),
                    "labels": PropertyDefinition(type="list"),
                    "assignees": PropertyDefinition(type="list"),
                    "token": PropertyDefinition(type="str")
                },
                required=["repo_owner", "repo_name", "title", "token"]
            ),
            delivery_policy=protocol.default_policy
        )
        
        protocol = GithubProtocol(action.config)
        result = protocol.execute(action)
        
        assert result.success == True
        assert result.result["status"] == "created"
