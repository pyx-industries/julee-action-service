"""Protocol-related domain models"""
from dataclasses import dataclass
from typing import List
from .delivery import DeliverySemantic, DeliveryPolicy

@dataclass(frozen=True)
class Protocol:
    """Supported protocols for actions"""
    id: str
    name: str
    description: str
    category: str
    handler_class: str  # Full path to handler class
    supported_semantics: List[DeliverySemantic]  # Delivery guarantees this protocol can provide
    default_policy: DeliveryPolicy  # Default delivery configuration

@dataclass(frozen=True)
class ActionType:
    """Categories of actions the service can perform"""
    id: str
    name: str 
    description: str
    category: str = "default"
