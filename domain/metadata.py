"""Metadata-related domain models"""
from dataclasses import dataclass
from typing import Any, Optional, Union

@dataclass(frozen=True)
class MetadataField:
    """A strongly-typed metadata field with context"""
    name: str
    value: Any
    category: str  # e.g. "system", "user", "audit"
    description: Optional[str] = None

@dataclass(frozen=True)
class Metric:
    """A single named value with optional description"""
    name: str
    value: Union[str, int, float, bool]
    description: Optional[str] = None
