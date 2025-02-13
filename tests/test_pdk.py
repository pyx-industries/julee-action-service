from typing import Dict, Any, Optional
import pytest
import uuid
from pydantic import BaseModel, ConfigDict
from unittest.mock import Mock, patch

from ..domain import Action, ActionType, Protocol, ActionResult
from ..pdk import ProtocolHandler
from ..testing.protocol_helper import ProtocolTestHelper

class ProtocolTestConfig(BaseModel):
    """Example config for testing"""
    model_config = ConfigDict(
        extra='forbid',
        frozen=True,  # Add frozen=True to match main config behavior
        validate_assignment=True  # Validate on attribute assignment
    )
    url: str
    method: str = "GET"
    headers: Dict[str, str] = {}

class ExampleTestProtocol(ProtocolHandler):
    """Test protocol implementation"""
    
    def validate_config(self) -> bool:
        try:
            ProtocolTestConfig(**self.config)
            self.last_error = None  # Explicitly clear error state on success
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
            
    def test_connection(self) -> bool:
        try:
            # Simulate connection test
            if self.config.get('url') == 'http://fail.test':
                raise ConnectionError("Failed to connect")
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
            
    def execute(self, action: Action) -> ActionResult:
        try:
            # Validate config first
            if not self.validate_config():
                raise ValueError(f"Invalid config: {self.last_error}")
                
            # Simulate execution
            if action.config['url'] == 'http://error.test':
                raise RuntimeError("Execution failed")
                
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

def test_protocol_handler_initialization():
    """Test protocol handler initialization"""
    config = {
        "url": "http://test.com",
        "method": "GET"
    }
    
    handler = ExampleTestProtocol(config)
    assert handler.config == config
    assert handler.last_error is None

def test_protocol_config_validation_success():
    """Test successful config validation"""
    handler = ExampleTestProtocol({
        "url": "http://test.com",
        "method": "GET",
        "headers": {"Authorization": "Bearer token"}
    })
    
    assert handler.validate_config() == True
    assert handler.last_error is None

def test_protocol_config_validation_failure():
    """Test failed config validation"""
    handler = ExampleTestProtocol({
        "method": "GET"  # Missing required url
    })
    
    assert handler.validate_config() == False
    assert handler.last_error is not None
    assert "url" in handler.last_error.lower()

def test_protocol_connection_test_success():
    """Test successful connection test"""
    handler = ExampleTestProtocol({
        "url": "http://test.com",
        "method": "GET"
    })
    
    assert handler.test_connection() == True
    assert handler.last_error is None

def test_protocol_connection_test_failure():
    """Test failed connection test"""
    handler = ExampleTestProtocol({
        "url": "http://fail.test",
        "method": "GET"
    })
    
    assert handler.test_connection() == False
    assert handler.last_error is not None
    assert "failed to connect" in handler.last_error.lower()

def test_protocol_execution_success(catalogue):  # Add catalogue fixture
    """Test successful action execution"""
    protocol = catalogue.get_protocol("http")  # Get protocol first
    action = Action(
        id="test-1",
        name="Test Action",
        description="Test action",
        action_type=catalogue.get_action_type("fetch"),  # Get from catalogue
        protocol=protocol,  # Use protocol variable
        config={
            "url": "http://test.com",
            "method": "GET"
        },
        delivery_policy=protocol.default_policy
    )
    
    handler = ExampleTestProtocol(action.config)
    result = handler.execute(action)
    
    assert result.success == True
    assert result.action_id == action.id
    assert result.result == {"status": "ok"}
    assert result.error is None

def test_protocol_execution_invalid_config(catalogue):
    """Test execution with invalid config"""
    protocol = catalogue.get_protocol("http")  # Get protocol first
    action = Action(
        id="test-2",
        name="Test Action",
        description="Test action",
        action_type=catalogue.get_action_type("fetch"),
        protocol=protocol,  # Use protocol variable
        config={
            "method": "GET"  # Missing url
        },
        delivery_policy=protocol.default_policy
    )
    
    handler = ExampleTestProtocol(action.config)
    result = handler.execute(action)
    
    assert result.success == False
    assert result.action_id == action.id
    assert "invalid config" in result.error.lower()

def test_protocol_execution_runtime_error(catalogue):
    """Test execution with runtime error"""
    protocol = catalogue.get_protocol("http")  # Get protocol first
    action = Action(
        id="test-3",
        name="Test Action",
        description="Test action",
        action_type=catalogue.get_action_type("fetch"),
        protocol=protocol,  # Use protocol variable
        config={
            "url": "http://error.test",
            "method": "GET"
        },
        delivery_policy=protocol.default_policy
    )
    
    handler = ExampleTestProtocol(action.config)
    result = handler.execute(action)
    
    assert result.success == False
    assert result.action_id == action.id
    assert "execution failed" in result.error.lower()

def test_protocol_helper(catalogue):
    """Test the protocol test helper"""
    helper = ProtocolTestHelper(catalogue)
    
    # Test action creation
    action = helper.create_test_action(
        protocol=catalogue.get_protocol("http"),
        config={"url": "http://test.com", "method": "GET"}
    )
    assert action.protocol == catalogue.get_protocol("http")
    assert action.config["url"] == "http://test.com"
    
    # Test protocol validation
    assert helper.validate_protocol_handler(ExampleTestProtocol) == True
    
    # Test invalid protocol handler
    class InvalidProtocol:
        pass
        
    with pytest.raises(ValueError) as exc:
        helper.validate_protocol_handler(InvalidProtocol)
    assert "missing required methods" in str(exc.value).lower()
    
    # Test mock response creation
    mock_resp = helper.create_mock_response(
        success=True,
        data={"test": "data"},
        error=None
    )
    assert mock_resp.success == True
    assert mock_resp.data == {"test": "data"}
    assert mock_resp.error is None

def test_protocol_error_handling():
    """Test protocol error handling and state management"""
    handler = ExampleTestProtocol({
        "url": "http://test.com",
        "method": "GET"
    })
    
    # Test error state clearing
    handler.last_error = "Previous error"
    assert handler.validate_config() == True
    assert handler.last_error is None
    
    # Test error state persistence
    handler = ExampleTestProtocol({"method": "GET"})
    assert handler.validate_config() == False
    previous_error = handler.last_error
    assert handler.validate_config() == False
    assert handler.last_error == previous_error

def test_protocol_config_immutability():
    """Test that protocol config is effectively immutable"""
    initial_config = {
        "url": "http://test.com",
        "method": "GET",
        "headers": {"Authorization": "Bearer token"}
    }
    
    handler = ExampleTestProtocol(initial_config)
    
    # Attempt to modify config
    with pytest.raises(Exception):
        handler.config["url"] = "http://modified.com"
    
    # Verify config unchanged
    assert handler.config["url"] == "http://test.com"
