"""Template-related domain models"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class TransformRule:
    """A data transformation rule"""
    name: str
    transform_type: str  # e.g. "map", "filter", "aggregate"
    config: Dict[str, Any]
    description: Optional[str] = None

@dataclass(frozen=True)
class ActionTemplate:
    """Template for transforming action data"""
    content: str  # Jinja2 template content
    content_type: str = "text/jinja2"  # Default to Jinja2
    description: Optional[str] = None
