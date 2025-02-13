"""Domain models for the Action Service."""

from .base import *
from .config import *
from .actions import *
from .direction import ActionDirection, ActionDirectionType
from .protocols import *
from .connections import *
from .events import *
from .routing import *
from .templates import *

__all__ = (
    'Metric',
    'MetadataField',
    'ConfigValue',
    'ValidationRule',
    'PropertyDefinition',
    'ProtocolConfigSchema',
    'ActionType',
    'Action',
    'ActionResult',
    'Protocol',
    'ConnectionStatus',
    'Connection',
    'Event',
    'RoutingRule',
    'RoutingConfiguration',
    'TransformRule',
    'ActionTemplate'
)
"""
Domain models for the Action Service.

This package contains the core domain models organized into submodules:
- base: Common base classes and types
- actions: Action-related models
- protocols: Protocol-related models  
- connections: Connection-related models
- events: Event-related models
- routing: Routing-related models
- templates: Template-related models
"""

from .base import *
from .actions import *
from .protocols import *
from .connections import *
from .events import *
from .routing import *
from .templates import *

# Re-export commonly used types
__all__ = [
    # Base types
    'Metric',
    'ValidationRule',
    'ConfigValue',
    'MetadataField',
    'TransformRule',
    
    # Core models
    'Action',
    'Protocol',
    'Connection',
    'Event',
    'ActionResult',
    
    # Supporting types
    'ActionType',
    'ConnectionStatus',
    'ProtocolConfig',
    'ProtocolConfigSchema',
    'ActionTemplate',
    'RoutingRule',
    'RoutingConfiguration',
    'WebhookResult'
]
"""Domain models for the Action Service"""

from .base import Metric, MetadataField
from .config import (
    ValidationRule, ConfigValue, PropertyDefinition,
    ProtocolConfigSchema, ProtocolConfig
)
from .actions import Action, ActionResult

__all__ = [
    'Metric',
    'MetadataField',
    'ValidationRule',
    'ConfigValue',
    'PropertyDefinition', 
    'ProtocolConfigSchema',
    'ProtocolConfig',
    'Action',
    'ActionResult'
]
"""Domain models for the Action Service"""
from .protocols import Protocol, ActionType
from .connections import Connection, ConnectionStatus
from .credentials import Credential, Secret, SecretCollection
from .events import Event
from .subscriptions import Subscription, Publisher
from .metadata import MetadataField, Metric
from .config import (
    ValidationRule, ConfigValue, PropertyDefinition,
    ProtocolConfigSchema, ProtocolConfig
)
from .templates import TransformRule, ActionTemplate
from .routing import RoutingRule, RoutingConfiguration

__all__ = [
    'Protocol',
    'ActionType',
    'Connection',
    'ConnectionStatus',
    'Credential',
    'Secret', 
    'SecretCollection',
    'Event',
    'Subscription',
    'Publisher',
    'Metric',
    'ValidationRule',
    'ConfigValue',
    'MetadataField',
    'TransformRule',
    'ActionTemplate',
    'ProtocolConfig',
    'ProtocolConfigSchema',
    'PropertyDefinition',
    'RoutingRule',
    'RoutingConfiguration',
    'Webhook',
    'EventStatus',
    'WebhookResult'
]
"""Domain models for the Action Service"""
from .actions import *
from .config import *
from .connections import *
from .credentials import *
from .direction import ActionDirection, ActionDirectionType
from .events import *
from .metadata import *
from .protocols import *
from .publishers import *
from .routing import *
from .templates import *
from .messages import Message, MessageLevel, MessageTarget
