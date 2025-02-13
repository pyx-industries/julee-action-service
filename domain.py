"""Domain models for the Action Service."""
from __future__ import absolute_import, unicode_literals
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any, Union, Literal

from .actions import Action, ActionResult
from .metadata import MetadataField, Metric
from .config import (
    ValidationRule, ConfigValue, PropertyDefinition, 
    ProtocolConfigSchema
)
from .connections import Connection, ConnectionStatus
from .credentials import Credential, Secret, SecretCollection
from .events import Event
from .metadata import MetadataField
from .metrics import Metric
from .protocols import Protocol, ActionType
from .routing import RoutingRule, RoutingConfiguration
from .templates import TransformRule, ActionTemplate

@dataclass(frozen=True)
class ValidationRule:
    """Defines validation rules for configuration values"""
    rule_type: str  # e.g. "min", "max", "pattern", "choices", "range"
    value: Any  # The validation constraint value
    message: Optional[str] = None  # Custom error message

@dataclass(frozen=True)
class ConfigValue:
    """A strongly-typed configuration value"""
    name: str
    value: Union[str, int, bool, float]  # Only primitive scalar types
    description: Optional[str] = None

@dataclass(frozen=True)
class MetadataField:
    """A strongly-typed metadata field with context"""
    name: str
    value: Any
    category: str  # e.g. "system", "user", "audit"
    description: Optional[str] = None


@dataclass(frozen=True)
class ActionType:
    """Categories of actions the service can perform"""
    id: str
    name: str 
    description: str
    category: str = "default"

@dataclass(frozen=True)
class ConnectionStatus:
    """Status of a connection to an external service"""
    id: str
    name: str
    description: str
    can_retry: bool = True
    severity: int = 0  # 0=normal, 1=warning, 2=error

@dataclass(frozen=True)
class Protocol:
    """Supported protocols for actions"""
    id: str
    name: str
    description: str
    category: str
    handler_class: str  # Full path to handler class


@dataclass
class Action:
    """Definition of something the service can do"""
    id: str
    name: str
    description: str
    action_type: ActionType
    protocol: Protocol
    config: List[ConfigValue]  # Configuration values with validation
    schema: Optional[ProtocolConfigSchema] = None  # Schema for config validation
    metadata: List[MetadataField] = field(default_factory=list)  # Metadata fields
    credential_id: Optional[str] = None  # Optional credential reference
    schedule: Optional[str] = None  # Cron expression for polling/subscriptions
    input_transform: Optional[TransformRule] = None  # Transformation rules
    output_transform: Optional[TransformRule] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))



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

@dataclass(frozen=True)
class PropertyDefinition:
    """Schema definition for a single configuration property"""
    type: Literal["str", "int", "bool", "float"]  # Only allow specific primitive types
    description: Optional[str] = None
    default: Optional[Any] = None
    required: bool = False
    validation_rules: List[ValidationRule] = field(default_factory=list)

@dataclass(frozen=True)
class ProtocolConfigSchema:
    """Schema definition for protocol configuration"""
    properties: Dict[str, PropertyDefinition]  # Use PropertyDefinition instead of Dict[str, Any]
    required: List[str]  # Required field names
    description: Optional[str] = None
    
    def __post_init__(self):
        # Validate that required fields exist in properties
        missing = [field for field in self.required if field not in self.properties]
        if missing:
            raise ValueError(f"Required fields missing from properties: {', '.join(missing)}")
        
        # Validate property definitions
        for field_name, field_def in self.properties.items():
            if not isinstance(field_def, PropertyDefinition):
                raise ValueError(f"Field {field_name} must use PropertyDefinition")

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate a configuration against this schema"""
        # Check required fields
        missing = [field for field in self.required if field not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
            
        # Validate field types
        for field_name, value in config.items():
            if field_name not in self.properties:
                raise ValueError(f"Unknown field: {field_name}")
                
            prop_def = self.properties[field_name]
            expected_type = eval(prop_def.type)  # Safe since type is from Literal
            if not isinstance(value, expected_type):
                raise ValueError(f"Field {field_name} must be of type {prop_def.type}")
            
            # Apply validation rules if any
            for rule in prop_def.validation_rules:
                if not self._validate_rule(value, rule):
                    raise ValueError(
                        rule.message or f"Field {field_name} failed validation rule: {rule.rule_type}"
                    )

    def _validate_rule(self, value: Any, rule: ValidationRule) -> bool:
        """Apply a validation rule to a value"""
        if rule.rule_type == "min":
            return value >= rule.value
        elif rule.rule_type == "max":
            return value <= rule.value
        elif rule.rule_type == "pattern":
            import re
            return bool(re.match(rule.value, str(value)))
        elif rule.rule_type == "choices":
            return value in rule.value
        elif rule.rule_type == "range":
            min_val, max_val = rule.value
            return min_val <= value <= max_val
        return False  # Unknown rule type

@dataclass(frozen=True)
class RoutingRule:
    """Single rule for determining message destination"""
    name: str
    destination: str  # The target endpoint/queue/topic
    condition: Optional[str] = None  # Expression determining when to use this route
    priority: int = 0  # Higher priority routes are tried first
    config: Dict[str, Any] = field(default_factory=dict)  # Additional routing config
    description: Optional[str] = None

@dataclass(frozen=True)
class RoutingConfiguration:
    """Complete routing strategy for a publisher"""
    rules: List[RoutingRule]
    strategy: Literal["first-match", "all-matching", "priority"] = "first-match"
    fallback: Optional[RoutingRule] = None
    description: Optional[str] = None

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

@dataclass(frozen=True)
class Metric:
    """A single named value with optional description"""
    name: str
    value: Union[str, int, float, bool]
    description: Optional[str] = None

@dataclass
class ActionResult:
    """Result of executing an action"""
    action_id: str
    request_id: str  # For tracing/correlation
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    
    # Historical measurements taken during execution
    # Examples: execution time, bytes processed, cache hits
    history: List[Metric] = field(default_factory=list)
    
    # Constraints affecting future executions
    # Examples: rate limits remaining, quota resets, cooldown periods
    limits: List[Metric] = field(default_factory=list)
    
    # Environmental and situational information
    # Examples: server region, protocol version, client configuration
    context: List[Metric] = field(default_factory=list)
    
    # Timestamp applying to all metrics in this result
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
