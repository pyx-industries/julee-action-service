"""Acknowledge system message usecase"""
from datetime import datetime, UTC
from typing import Optional
from pydantic import BaseModel, ConfigDict

from ...domain.messages import Message
from ...types import RepoSet

class AcknowledgeMessageRequest(BaseModel):
    """Request model for acknowledging system message"""
    model_config = ConfigDict(extra="forbid")
    
    message_id: str
    acknowledged_by: str
    acknowledgment_notes: Optional[str] = None

class AcknowledgeMessageResponse(BaseModel):
    """Response model for message acknowledgment"""
    model_config = ConfigDict(extra="forbid")
    
    message_id: str
    acknowledged: bool
    acknowledged_at: datetime
    acknowledged_by: str
    error: Optional[str] = None

class AcknowledgeMessage:
    """Mark a system message as acknowledged"""
    
    def __init__(self, reposet: RepoSet):
        self.message_repo = reposet["message_repository"]
        
    def execute(self, request: AcknowledgeMessageRequest) -> AcknowledgeMessageResponse:
        """Acknowledge specified message"""
        try:
            # Get existing message
            message = self.message_repo.get_message(request.message_id)
            if not message:
                return AcknowledgeMessageResponse(
                    message_id=request.message_id,
                    acknowledged=False,
                    acknowledged_at=datetime.now(UTC),
                    acknowledged_by=request.acknowledged_by,
                    error="Message not found"
                )
            
            # Check if already acknowledged
            if message.acknowledged_at:
                return AcknowledgeMessageResponse(
                    message_id=request.message_id,
                    acknowledged=False,
                    acknowledged_at=datetime.now(UTC),
                    acknowledged_by=request.acknowledged_by,
                    error="Message already acknowledged"
                )
            
            # Acknowledge the message
            acknowledged = self.message_repo.acknowledge_message(
                message_id=request.message_id,
                acknowledged_by=request.acknowledged_by,
                acknowledgment_notes=request.acknowledgment_notes
            )
            
            return AcknowledgeMessageResponse(
                message_id=request.message_id,
                acknowledged=acknowledged,
                acknowledged_at=datetime.now(UTC),
                acknowledged_by=request.acknowledged_by
            )
            
        except Exception as e:
            return AcknowledgeMessageResponse(
                message_id=request.message_id,
                acknowledged=False,
                acknowledged_at=datetime.now(UTC),
                acknowledged_by=request.acknowledged_by,
                error=str(e)
            )
