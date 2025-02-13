"""Routing-related domain models"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal

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
