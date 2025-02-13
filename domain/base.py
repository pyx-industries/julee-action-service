"""Base types used throughout the domain model."""

from dataclasses import dataclass
from typing import Union, Optional, Any

@dataclass(frozen=True)
class Metric:
    """A single named value with optional description"""
    name: str
    value: Union[str, int, float, bool]
    description: Optional[str] = None

@dataclass(frozen=True)
class MetadataField:
    """A strongly-typed metadata field with context"""
    name: str
    value: Any
    category: str  # e.g. "system", "user", "audit"
    description: Optional[str] = None

__all__ = ['Metric', 'MetadataField']
"""Base domain types used across other domain models"""

from dataclasses import dataclass
from typing import Any, Dict, Union, Optional

@dataclass(frozen=True)
class Metric:
    """A single named value with optional description"""
    name: str
    value: Union[str, int, float, bool]
    description: Optional[str] = None

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
class TransformRule:
    """A data transformation rule"""
    name: str
    transform_type: str  # e.g. "map", "filter", "aggregate"
    config: Dict[str, Any]
    description: Optional[str] = None
"""Base domain types used across other modules"""
from dataclasses import dataclass
from typing import Any, Optional, Union

@dataclass(frozen=True)
class Metric:
    """A single named value with optional description"""
    name: str
    value: Union[str, int, float, bool]
    description: Optional[str] = None

@dataclass(frozen=True)
class MetadataField:
    """A strongly-typed metadata field with context"""
    name: str
    value: Any
    category: str  # e.g. "system", "user", "audit"
    description: Optional[str] = None
