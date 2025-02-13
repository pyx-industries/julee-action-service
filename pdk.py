"""
Protocol Development Kit (PDK) - The building blocks for creating new protocols
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from types import MappingProxyType
from pydantic import BaseModel, ConfigDict

from .domain import ConfigValue

from .domain import Action, ActionResult, Protocol

class ProtocolConfig(BaseModel):
    """Base configuration for all protocols"""
    model_config = ConfigDict(
        extra='forbid',  # Prevent unknown fields
        frozen=True,     # Make configs immutable
        validate_assignment=True  # Validate on attribute assignment
    )

class ProtocolHandler(ABC):
    """Base class for all protocol implementations"""
    
    def __init__(self, config: Union[List[ConfigValue], Dict[str, Any]]):
        # Convert list of ConfigValue to dict if needed
        if isinstance(config, list):
            config_dict = {v.name: v.value for v in config}
        else:
            config_dict = config

        # Create dynamic model with frozen config
        ConfigModel = type('ConfigModel', (BaseModel,), {
            '__annotations__': {k: type(v) for k, v in config_dict.items()},
            'model_config': ConfigDict(frozen=True)  # Use ConfigDict instead of class Config
        })
        
        # Store as immutable model
        self._config = ConfigModel(**config_dict)
        self.last_error: Optional[str] = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get config as immutable dictionary"""
        return MappingProxyType(self._config.model_dump())
    
    @abstractmethod
    def execute(self, action: Action) -> ActionResult:
        """Execute an action using this protocol"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the protocol configuration"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the service"""
        pass
        
    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return self.last_error

class ExampleProtocol(ProtocolHandler):
    """Example implementation showing protocol structure"""
    
    def connect_to_service(self, config: Dict[str, Any]) -> Any:
        """Example connection logic"""
        import httpx
        return httpx.Client(
            base_url=config.get('base_url'),
            headers=config.get('headers', {})
        )
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """Example config validation"""
        required = ['base_url', 'method']
        missing = [key for key in required if key not in config]
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")
    
    def execute(self, action: Action) -> ActionResult:
        """Example execution flow"""
        try:
            # Validate configuration
            self.validate_config(action.config)
            
            # Connect to service
            client = self.connect_to_service(action.config)
            
            # Execute action
            response = client.request(
                method=action.config['method'],
                url=action.config['url']
            )
            
            # Return result
            return ActionResult(
                action_id=action.id,
                success=True,
                result=response.json()
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action.id,
                success=False,
                error=str(e)
            )
