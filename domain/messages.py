"""Domain models for inbound message handling"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

@dataclass(frozen=True)
class InboundMessageRequest:
    """External system sending data to Action Service"""
    endpoint: str
    payload: Dict[str, Any]
    api_key: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class InboundMessageResponse:
    """Acknowledgment to external system"""
    message_id: str
    received_at: datetime
    validation_status: str  # "accepted", "invalid", "error"
    validation_details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None

@dataclass(frozen=True)
class WorkerProcessingRequest:
    """Validated message ready for processing"""
    message_id: str
    protocol_id: str
    validated_payload: Dict[str, Any]
    metadata: Dict[str, Any]
    correlation_id: Optional[str] = None

@dataclass(frozen=True)
class WorkerProcessingResponse:
    """Processing outcome"""
    message_id: str
    processing_id: str
    status: str  # "processed", "failed", "deferred"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    next_actions: List[str] = None
"""Message-related domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Dict, Optional, Any, List, Literal
from .direction import ActionDirection, ActionDirectionType

# Define literal types
MessageLevelType = Literal["error", "warning", "info"]
MessageTargetType = Literal["global", "action", "protocol"]

@dataclass(frozen=True)
class MessageLevel:
    """Valid message severity levels"""
    ERROR: MessageLevelType = "error"
    WARNING: MessageLevelType = "warning"
    INFO: MessageLevelType = "info"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate message level"""
        return value in {cls.ERROR, cls.WARNING, cls.INFO}

@dataclass(frozen=True)
class MessageTarget:
    """Message targeting types"""
    GLOBAL: MessageTargetType = "global"
    ACTION: MessageTargetType = "action"
    PROTOCOL: MessageTargetType = "protocol"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate message target"""
        return value in {cls.GLOBAL, cls.ACTION, cls.PROTOCOL}

@dataclass
class Message:
    """System message/notification"""
    id: str
    level: MessageLevelType
    title: str
    content: str
    source: str
    target_type: Optional[MessageTargetType] = None
    target_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    acknowledgment_notes: Optional[str] = None
    expires_at: Optional[datetime] = None
    direction: Optional[ActionDirectionType] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        """Validate enum fields"""
        if self.direction and not ActionDirection.is_valid(self.direction):
            raise ValueError(f"Invalid direction: {self.direction}")
        if not MessageLevel.is_valid(self.level):
            raise ValueError(f"Invalid message level: {self.level}")
        
        if self.target_type is not None and not MessageTarget.is_valid(self.target_type):
            raise ValueError(f"Invalid target type: {self.target_type}")
