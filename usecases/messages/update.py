"""Update system message usecase"""
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from ...domain.messages import Message, MessageLevel, MessageTarget
from ...types import RepoSet
from ...interfaces.requests import UpdateMessageRequest

class UpdateMessageResponse(BaseModel):
    """Response model for message update"""
    model_config = ConfigDict(extra="forbid")
    
    message: Message
    updated: bool
    update_time: datetime

class UpdateMessage:
    """Update an existing system message"""
    
    def __init__(self, reposet: RepoSet):
        self.message_repo = reposet["message_repository"]
        
    def execute(self, request: UpdateMessageRequest) -> UpdateMessageResponse:
        """Update message with new values"""
        try:
            # Get existing message
            message = self.message_repo.get_message(request.message_id)
            if not message:
                raise ValueError(f"Message not found: {request.message_id}")
            
            # Validate level if provided
            if request.level and not MessageLevel.is_valid(request.level):
                raise ValueError(f"Invalid message level: {request.level}")
            
            # Build update data
            updates = {}
            if request.title is not None:
                updates["title"] = request.title
            if request.content is not None:
                updates["content"] = request.content
            if request.level is not None:
                updates["level"] = request.level
            if request.expires_at is not None:
                updates["expires_at"] = request.expires_at
            if request.metadata is not None:
                updates["metadata"] = request.metadata
                
            # Only update if there are changes
            if not updates:
                return UpdateMessageResponse(
                    message=message,
                    updated=False,
                    update_time=datetime.now(UTC)
                )
                
            # Apply updates
            updated_message = self.message_repo.update_message(
                message_id=request.message_id,
                updates=updates
            )
            
            return UpdateMessageResponse(
                message=updated_message,
                updated=True,
                update_time=datetime.now(UTC)
            )
            
        except Exception as e:
            raise ValueError(f"Error updating message: {str(e)}")
