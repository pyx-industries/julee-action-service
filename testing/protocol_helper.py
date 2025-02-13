"""
Testing utilities for protocol implementations.
"""
from typing import Any, Dict, Optional, Type
from unittest.mock import Mock
import uuid
import httpx

from ..domain import Action, Protocol, ActionType, ActionResult, ProtocolConfigSchema
from ..pdk import ProtocolHandler
from ..interfaces.behaviour import BehaviourCatalogue

class ProtocolTestHelper:
    """Makes testing new protocols easier"""
    
    def __init__(self, catalogue: BehaviourCatalogue):
        """Initialize with a behaviour catalogue"""
        self.catalogue = catalogue
    
    def create_test_action(
        self,
        protocol: Protocol,
        config: Dict[str, Any],
        action_type_id: str = "fetch",
        action_id: Optional[str] = None
    ) -> Action:
        """Create an Action instance for testing"""
        action_type = self.catalogue.get_action_type(action_type_id)
        if action_type is None:
            raise ValueError(f"Unknown action type: {action_type_id}")
            
        return Action(
            id=action_id or str(uuid.uuid4()),
            name="Test Action",
            description="Test action for protocol validation",
            action_type=action_type,
            protocol=protocol,
            config=config,
            delivery_policy=protocol.default_policy
        )
    
    def create_mock_response(
        self,
        success: bool = True,
        data: Optional[Dict] = None,
        error: Optional[str] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ) -> Mock:
        """Create a realistic mock response for testing"""
        mock = Mock()
        mock.success = success
        mock.status_code = status_code
        mock.headers = headers or {
            'Content-Type': 'application/json',
            'Server': 'TestMock/1.0'
        }
        mock.data = data or {"status": "ok", "timestamp": "2023-01-01T00:00:00Z"}
        mock.error = error
        mock.raise_for_status = Mock(
            side_effect=httpx.HTTPError if status_code >= 400 else None
        )
        return mock

    def mock_external_service(self, protocol: Protocol) -> Mock:
        """Returns appropriate mock for external service"""
        if protocol == Protocol.HTTP:
            mock = Mock()
            mock.status_code = 200
            mock.json = lambda: {"status": "ok"}
            return mock
        elif protocol == Protocol.SMTP:
            return Mock(sendmail=Mock(return_value=None))
        elif protocol == Protocol.WEBSOCKET:
            mock = Mock()
            mock.send = Mock(return_value=None)
            mock.receive = Mock(return_value='{"status": "connected"}')
            return mock
        else:
            return Mock()  # Generic mock for other protocols

    def validate_protocol_handler(self, handler_class: Type[ProtocolHandler]) -> bool:
        """Validate that a protocol handler implements required methods and schema"""
        # Check required methods
        required_methods = ['validate_config', 'test_connection', 'execute']
        
        missing = []
        for method in required_methods:
            if not hasattr(handler_class, method):
                missing.append(method)
            elif not callable(getattr(handler_class, method)):
                missing.append(f"{method} (not callable)")
                
        if missing:
            raise ValueError(
                f"Protocol handler missing required methods: {', '.join(missing)}"
            )

        # Validate config schema if defined
        if hasattr(handler_class, 'CONFIG_SCHEMA'):
            if not isinstance(handler_class.CONFIG_SCHEMA, ProtocolConfigSchema):
                raise ValueError("CONFIG_SCHEMA must be a ProtocolConfigSchema instance")
            
        return True

    def validate_protocol_config(self, handler: ProtocolHandler) -> None:
        """Validate protocol configuration"""
        if not handler.validate_config():
            raise ValueError(
                f"Invalid protocol configuration: {handler.get_last_error()}"
            )
