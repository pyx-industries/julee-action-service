"""Publisher-related domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from .routing import RoutingConfiguration
from .templates import TransformRule

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
