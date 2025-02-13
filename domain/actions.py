"""Action-related domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import List, Optional, Any

from .config import ConfigValue, ProtocolConfigSchema
from .delivery import DeliveryAttempt, DeliveryPolicy
from .metadata import MetadataField 
from .metrics import Metric
from .protocols import ActionType, Protocol
from .templates import TransformRule

@dataclass
class Action:
    """Definition of something the service can do"""
    id: str
    name: str
    description: str
    action_type: ActionType
    protocol: Protocol
    config: List[ConfigValue]  # Configuration values with validation
    delivery_policy: DeliveryPolicy  # How to handle message delivery
    schema: Optional[ProtocolConfigSchema] = None  # Schema for config validation
    metadata: List[MetadataField] = field(default_factory=list)  # Metadata fields
    credential_id: Optional[str] = None  # Optional credential reference
    schedule: Optional[str] = None  # Cron expression for polling/subscriptions
    input_transform: Optional[TransformRule] = None  # Transformation rules
    output_transform: Optional[TransformRule] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass
class ActionResult:
    """Result of executing an action"""
    action_id: str
    request_id: str  # For tracing/correlation
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    delivery_attempts: List[DeliveryAttempt] = field(default_factory=list)
    history: List[Metric] = field(default_factory=list)
    limits: List[Metric] = field(default_factory=list)
    context: List[Metric] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
