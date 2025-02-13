"""
Behaviour catalogue interface for the Action Service.
Defines the contract for accessing system-wide behaviour definitions.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..domain import ActionType, Protocol, ConnectionStatus, DeliverySemantic

class BehaviourCatalogue(ABC):
    """Interface for accessing behaviour definitions"""
    
    @abstractmethod
    def get_action_types(self) -> List[ActionType]:
        """Get all supported action types"""
        pass
        
    @abstractmethod
    def get_action_type(self, type_id: str) -> Optional[ActionType]:
        """Get action type by ID"""
        pass
        
    @abstractmethod
    def get_protocols(self) -> List[Protocol]:
        """Get all supported protocols"""
        pass
        
    @abstractmethod
    def get_protocol(self, protocol_id: str) -> Optional[Protocol]:
        """Get protocol by ID"""
        pass
        
    @abstractmethod
    def get_connection_statuses(self) -> List[ConnectionStatus]:
        """Get all possible connection statuses"""
        pass
        
    @abstractmethod
    def get_connection_status(self, status_id: str) -> Optional[ConnectionStatus]:
        """Get connection status by ID"""
        pass

    @abstractmethod
    def get_protocol_config_schema(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration schema for a protocol"""
        pass
        
    @abstractmethod
    def get_delivery_semantics(self) -> List[DeliverySemantic]:
        """Get all supported delivery semantics"""
        pass
        
    @abstractmethod
    def get_delivery_semantic(self, semantic_id: str) -> Optional[DeliverySemantic]:
        """Get delivery semantic by ID"""
        pass
