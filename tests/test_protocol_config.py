from unittest.mock import Mock
import pytest
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel, ValidationError

from ..domain import ConfigValue, ProtocolConfig, ProtocolConfigSchema

from ..domain import Protocol, ActionResult, ProtocolConfig, ProtocolConfigSchema, PropertyDefinition
from ..interfaces.protocol import ProtocolHandler
from ..testing.protocol_helper import ProtocolTestHelper

def test_protocol_repository_mapping(catalogue):  # Add catalogue parameter
    """Document protocol -> repository configuration"""
    from ..worker_service.settings import PROTOCOL_REPOSITORIES
    
    # Get HTTP protocol from catalogue
    http_protocol = catalogue.get_protocol("http")
    assert http_protocol is not None  # Verify we got it
    
    # Verify HTTP protocol is configured
    assert http_protocol.id in PROTOCOL_REPOSITORIES
    config = PROTOCOL_REPOSITORIES[http_protocol.id]
    
    # Verify expected repository keys exist
    assert 'action_repo' in config
    assert 'event_repo' in config
    
    # Verify repository paths are properly formatted
    assert 'action_service.repositories' in config['action_repo']
    assert 'action_service.repositories' in config['event_repo']

def test_protocol_handler_validation(catalogue):
    """Verify protocol handler implementation requirements"""
    class ConfigModel(BaseModel):
        url: str
        method: str = "GET"
    
    class ExampleProtocol(ProtocolHandler):
        def validate_config(self) -> bool:
            try:
                # Access the values field of ProtocolConfig and convert to dict
                if isinstance(self.config, ProtocolConfig):
                    config_dict = {v.name: v.value for v in self.config.values}
                elif isinstance(self.config, list):
                    config_dict = {v.name: v.value for v in self.config}
                else:
                    config_dict = self.config
                    
                ConfigModel(**config_dict)
                self.last_error = None  # Clear error state on success
                return True
            except ValidationError as e:
                self.last_error = str(e)
                return False
        
        def test_connection(self) -> bool:
            try:
                # Simulate connection test
                if isinstance(self.config, ProtocolConfig):
                    config_dict = {v.name: v.value for v in self.config.values}
                elif isinstance(self.config, list):
                    config_dict = {v.name: v.value for v in self.config}
                else:
                    config_dict = self.config

                if config_dict.get('url') == 'http://fail.test':
                    raise ConnectionError("Failed to connect")
                self.last_error = None  # Clear error state on success
                return True
            except Exception as e:
                self.last_error = str(e)
                return False
            
        def execute(self, action):
            try:
                # First validate config
                if not self.validate_config():
                    raise ValueError(f"Invalid configuration: {self.last_error}")
                    
                # Then test connection
                if not self.test_connection():
                    raise ConnectionError(self.last_error or "Connection failed")
                    
                return ActionResult(
                    action_id=action.id,
                    request_id=str(uuid.uuid4()),
                    success=True,
                    result={"status": "ok"}
                )
            except Exception as e:
                return ActionResult(
                    action_id=action.id,
                    request_id=str(uuid.uuid4()),
                    success=False,
                    error=str(e)
                )
    
    helper = ProtocolTestHelper(catalogue)  # Pass catalogue to helper
    
    # Should validate successfully
    assert helper.validate_protocol_handler(ExampleProtocol)
    
    # Test with valid config
    config = ProtocolConfig(
        values=[
            ConfigValue(name="url", value="http://test.com"),
            ConfigValue(name="method", value="GET")
        ],
        schema=ProtocolConfigSchema(
            properties={
                "url": PropertyDefinition(type="str", required=True),
                "method": PropertyDefinition(type="str", default="GET")
            },
            required=["url"]
        )
    )
    protocol = ExampleProtocol(config)
    assert protocol.validate_config() == True
    assert protocol.get_last_error() is None
    
    # Test with invalid config
    try:
        config = ProtocolConfig(
            values=[
                ConfigValue(name="method", value="GET")  # Missing required url
            ],
            schema=ProtocolConfigSchema(
                properties={
                    "url": PropertyDefinition(type="str", required=True),
                    "method": PropertyDefinition(type="str", default="GET")
                },
                required=["url"]
            )
        )
        pytest.fail("Should have raised ValueError")
    except ValueError:
        # Expected - config validation failed
        pass

def test_execute_action_request():
    """Test ExecuteActionRequest validation"""
    from ..interfaces.requests import ExecuteActionRequest
    
    # Test valid request
    request = ExecuteActionRequest(
        action_id="test-1",
        content={"message": "test"},
        correlation_id="corr-1",
        priority=5,
        deadline=datetime.now() + timedelta(minutes=5)
    )
    assert request.action_id == "test-1"
    assert request.priority == 5
    
    # Test priority bounds
    with pytest.raises(ValidationError):
        ExecuteActionRequest(
            action_id="test-1",
            content={},
            correlation_id="corr-1",
            priority=10  # Too high
        )
        
    with pytest.raises(ValidationError):
        ExecuteActionRequest(
            action_id="test-1",
            content={},
            correlation_id="corr-1",
            priority=-1  # Too low
        )

    # Test protocol validation with direct dict instead
    class TestProtocol(ProtocolHandler):
        def validate_config(self) -> bool:
            if 'url' not in self.config:
                self.last_error = "Missing required field: url"
                return False
            return True
            
        def test_connection(self) -> bool:
            try:
                if isinstance(self.config, ProtocolConfig):
                    config_dict = {v.name: v.value for v in self.config.values}
                elif isinstance(self.config, list):
                    config_dict = {v.name: v.value for v in self.config}
                else:
                    config_dict = self.config

                if config_dict.get('url') == 'http://fail.test':
                    raise ConnectionError("Failed to connect")
                self.last_error = None  # Clear error state on success
                return True
            except Exception as e:
                self.last_error = str(e)
                return False
            
        def execute(self, action):
            return ActionResult(
                action_id=action.id,
                request_id=str(uuid.uuid4()),
                success=False,
                error="Test error"
            )
    
    protocol = TestProtocol({"method": "GET"})  # Missing required url
    assert protocol.validate_config() == False
    assert protocol.get_last_error() is not None
    assert "url" in protocol.get_last_error().lower()
    
    # Test error handling during execution
    config = ProtocolConfig(
        values=[
            ConfigValue(name="url", value="http://fail.test"),
            ConfigValue(name="method", value="GET")
        ],
        schema=ProtocolConfigSchema(
            properties={
                "url": PropertyDefinition(type="str", required=True),
                "method": PropertyDefinition(type="str", default="GET")
            },
            required=["url"]
        )
    )
    protocol = TestProtocol(config)
    result = protocol.execute(Mock(id="test-1"))
    assert result.success == False
    assert result.error is not None
    
    # Test connection failure handling
    assert protocol.test_connection() == False
    assert "Failed to connect" in protocol.get_last_error()
