"""Delivery semantics and related domain concepts"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Literal
from .validation import ValidationRule

@dataclass(frozen=True)
class DeliverySemantic:
    """Definition of a delivery guarantee"""
    id: str  # Identifier like "at_most_once"
    name: str  # Display name like "At Most Once"
    description: str  # Detailed description
    requires_ack: bool  # Whether acknowledgment is required
    allows_retry: bool  # Whether retries are permitted
    preserves_order: bool  # Whether ordering must be maintained
    requires_dedup: bool  # Whether deduplication is required

@dataclass(frozen=True)
class DeliveryPolicy:
    """Concrete delivery configuration"""
    semantic: DeliverySemantic
    max_retries: Optional[int] = None  # None = unlimited
    retry_delay: timedelta = timedelta(seconds=30)
    expiry: Optional[timedelta] = None  # None = never expires

    def __post_init__(self):
        # Validate policy matches semantic constraints
        if not self.semantic.allows_retry and self.max_retries != 0:
            raise ValueError(f"{self.semantic.name} delivery cannot have retries")
            
        if self.semantic.requires_dedup and not self.semantic.requires_ack:
            raise ValueError(f"{self.semantic.name} delivery requires acknowledgment")

@dataclass
class DeliveryPattern:
    """Defines how content should be delivered"""
    pattern_type: Literal["push", "pull", "batch", "stream"]
    config: Dict[str, Any]
    validation_rules: List[ValidationRule]

@dataclass
class BatchConfig:
    """Configuration for batch delivery"""
    max_size: int
    window: timedelta
    partial_delivery: bool
    ordering_required: bool

@dataclass
class ResponseConfig:
    """Expected response configuration"""
    timeout: int
    required_fields: List[str]
    success_conditions: List[ValidationRule]
    error_mapping: Dict[str, str]

@dataclass
class DeliveryAttempt:
    """Record of a delivery attempt"""
    timestamp: datetime
    success: bool
    error: Optional[str] = None
    retry_count: int = 0
