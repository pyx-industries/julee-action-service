"""Connection-related domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import List, Optional
from .protocols import Protocol
from .config import ConfigValue
from .metrics import Metric

@dataclass(frozen=True)
class ConnectionStatus:
    """Status of a connection to an external service"""
    id: str
    name: str
    description: str
    can_retry: bool = True
    severity: int = 0  # 0=normal, 1=warning, 2=error

@dataclass
class Connection:
    """Protocol-specific connection details and state"""
    id: str
    protocol: Protocol 
    status: ConnectionStatus
    config: List[ConfigValue]  # Protocol configuration with validation
    metrics: List[Metric] = field(default_factory=list)  # Connection health/stats
    last_error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
