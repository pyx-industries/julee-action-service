"""Create system message usecase"""
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from ...domain.messages import Message, MessageLevel, MessageTarget
from ...types import RepoSet
from ...interfaces.requests import CreateSystemMessageRequest


class CreateSystemMessageResponse(BaseModel):
    """Response model for system message creation"""
    model_config = ConfigDict(extra="forbid")
    
    message_id: str
    status: str
    created_at: datetime
    error: Optional[str] = None

class CreateSystemMessage:
    """Create a new system notification message"""
    
    def __init__(self, reposet: RepoSet):
        self.message_repo = reposet["message_repository"]
        
    def execute(self, request: CreateSystemMessageRequest) -> CreateSystemMessageResponse:
        """Create a new system message"""
        try:
            # Validate message level
            if not MessageLevel.is_valid(request.level):
                return CreateSystemMessageResponse(
                    message_id="",
                    status="error",
                    created_at=datetime.now(UTC),
                    error=f"Invalid message level: {request.level}"
                )
            
            # Validate target type if provided
            if request.target_type and not MessageTarget.is_valid(request.target_type):
                return CreateSystemMessageResponse(
                    message_id="",
                    status="error",
                    created_at=datetime.now(UTC),
                    error=f"Invalid target type: {request.target_type}"
                )
            
            # Create message
            message = Message(
                id=self.message_repo.generate_id(),
                level=request.level,
                title=request.title,
                content=request.content,
                source=request.source,
                target_type=request.target_type,
                target_id=request.target_id,
                metadata=request.metadata,
                expires_at=request.expires_at,
                created_at=datetime.now(UTC)
            )
            
            # Store message
            self.message_repo.create_message(message)
            
            return CreateSystemMessageResponse(
                message_id=message.id,
                status="success",
                created_at=message.created_at
            )
            
        except Exception as e:
            return CreateSystemMessageResponse(
                message_id="",
                status="error",
                created_at=datetime.now(UTC),
                error=f"Error creating message: {str(e)}"
            )
