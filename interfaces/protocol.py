"""
Protocol Development Kit (PDK) - Core interfaces and helpers for protocol implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

from ..domain import Action, ActionResult

class ProtocolConfig(BaseModel):
    """Base class for protocol-specific configuration validation"""
    model_config = ConfigDict(extra="forbid")  # Prevent unknown fields

class ProtocolHandler(ABC):
    """Base class for all protocol implementations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.last_error: Optional[str] = None
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate protocol configuration"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if configuration can establish connection"""
        pass
    
    @abstractmethod
    def execute(self, action: Action) -> ActionResult:
        """Execute the actual action"""
        pass

    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return self.last_error
