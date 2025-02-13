"""Stream-related domain models"""
from dataclasses import dataclass
from typing import Dict, Optional
from .direction import ActionDirection, ActionDirectionType
from .direction import ActionDirection, ActionDirectionType

@dataclass
class AfferentStream:
    """Incoming data stream configuration"""
    id: str
    name: str
    config: Dict
    status: str = "inactive"
    description: Optional[str] = None

    def __post_init__(self):
        """Implicitly inbound-only"""
        object.__setattr__(self, 'direction', ActionDirection.AFFERENT)

@dataclass 
class EfferentStream:
    """Outgoing data stream configuration"""
    id: str
    name: str
    config: Dict
    status: str = "inactive"
    description: Optional[str] = None

@dataclass
class StreamMonitor:
    """Stream health monitoring data"""
    stream_id: str
    status: str
    error_count: int = 0
    metrics: Dict = None
