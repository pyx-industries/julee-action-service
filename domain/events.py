"""Event-related domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, List, Optional, Literal
from .metadata import MetadataField

@dataclass
class Event:
    """A message flowing through the system"""
    id: str
    action_id: str
    direction: Literal["incoming", "outgoing"]
    content: Any
    content_type: str
    status: str
    metadata: List[MetadataField] = field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed_at: Optional[datetime] = None
"""Event-related domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, List, Optional, Literal
from .metadata import MetadataField

@dataclass
class Event:
    """A message flowing through the system"""
    id: str
    action_id: str
    direction: Literal["incoming", "outgoing"]
    content: Any
    content_type: str
    status: str
    metadata: List[MetadataField] = field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed_at: Optional[datetime] = None
"""Event-related domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from .direction import ActionDirectionType
from .metadata import MetadataField
from .metrics import Metric

@dataclass
class Webhook:
    """Represents a configured webhook endpoint"""
    id: str
    key: str
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class EventStatus:
    """Status of a webhook event"""
    state: str  # e.g. "pending", "completed", "failed"
    correlation_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass
class Event:
    """Message flowing through the system"""
    id: str
    action_id: str
    direction: ActionDirectionType
    content: Any
    content_type: str
    metadata: List[MetadataField] = field(default_factory=list)
    metrics: List[Metric] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    # Webhook-specific fields
    webhook_key: Optional[str] = None
    correlation_id: Optional[str] = None
    state: Optional[str] = None  # For webhook status tracking

@dataclass
class WebhookResult:
    """Result of webhook processing"""
    result: Dict[str, str]  # The processed result data as string key-value pairs
    error: Optional[str] = None  # Any error message
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
"""Event domain models"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Event:
    """Base event model"""
    id: str
    timestamp: datetime
    event_type: str
    metadata: Dict[str, Any]

@dataclass 
class WebhookKey:
    """Webhook authentication key"""
    key_id: str
    key: str
    created_at: datetime
    single_use: bool
    used_at: Optional[datetime] = None
    response_id: Optional[str] = None  # Links to the webhook response that used this key

@dataclass
class WebhookEvent(Event):
    """Webhook received event"""
    webhook_id: str
    response_id: str
    content_type: str
    correlation_id: Optional[str]
    key_id: Optional[str]
