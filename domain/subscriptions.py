"""Subscription and Publisher domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from .templates import TransformRule
from .routing import RoutingConfiguration
from .direction import ActionDirection, ActionDirectionType
from .direction import ActionDirection, ActionDirectionType

@dataclass
class Subscription:
    """Continuous inbound data feed configuration"""
    id: str
    action_id: str
    connection_id: str
    filters: TransformRule   # What data to receive
    transform: TransformRule # How to process it
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        """Implicitly inbound-only"""
        object.__setattr__(self, 'direction', ActionDirection.AFFERENT)

@dataclass
class Publisher:
    """Continuous outbound data feed configuration"""
    id: str
    action_id: str
    connection_id: str
    routing: RoutingConfiguration  # Complete routing strategy
    transform: TransformRule      # Single transform rule
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

