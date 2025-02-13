"""Delete system message usecase"""
from datetime import datetime, UTC
from typing import Optional
from pydantic import BaseModel, ConfigDict

from ...domain.messages import Message
from ...types import RepoSet

class DeleteMessageRequest(BaseModel):
    """Request model for deleting system message"""
    model_config = ConfigDict(extra="forbid")
    
    message_id: str
    force: bool = False  # Force delete even if not expired
    deletion_notes: Optional[str] = None

class DeleteMessageResponse(BaseModel):
    """Response model for message deletion"""
    model_config = ConfigDict(extra="forbid")
    
    message_id: str
    deleted: bool
    deletion_time: datetime
    error: Optional[str] = None

class DeleteMessage:
    """Delete an existing system message"""
    
    def __init__(self, reposet: RepoSet):
        self.message_repo = reposet["message_repository"]
        
    def execute(self, request: DeleteMessageRequest) -> DeleteMessageResponse:
        """Delete specified message"""
        try:
            # Get existing message
            message = self.message_repo.get_message(request.message_id)
            if not message:
                return DeleteMessageResponse(
                    message_id=request.message_id,
                    deleted=False,
                    deletion_time=datetime.now(UTC),
                    error="Message not found"
                )
            
            # Check if message can be deleted
            now = datetime.now(UTC)
            if not request.force:
                if message.expires_at and message.expires_at > now:
                    return DeleteMessageResponse(
                        message_id=request.message_id,
                        deleted=False,
                        deletion_time=now,
                        error="Message has not expired yet"
                    )
            
            # Delete the message
            deleted = self.message_repo.delete_message(
                message_id=request.message_id,
                deletion_notes=request.deletion_notes
            )
            
            return DeleteMessageResponse(
                message_id=request.message_id,
                deleted=deleted,
                deletion_time=datetime.now(UTC)
            )
            
        except Exception as e:
            return DeleteMessageResponse(
                message_id=request.message_id,
                deleted=False,
                deletion_time=datetime.now(UTC),
                error=str(e)
            )
