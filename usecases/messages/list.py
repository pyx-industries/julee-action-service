"""List system messages usecase"""
from datetime import datetime, UTC
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from ...domain.messages import Message, MessageLevelType, MessageTargetType
from ...types import RepoSet

class ListMessagesRequest(BaseModel):
    """Request model for listing system messages"""
    model_config = ConfigDict(extra="forbid")
    
    level: Optional[MessageLevelType] = None
    target_type: Optional[MessageTargetType] = None
    target_id: Optional[str] = None
    acknowledged: Optional[bool] = None
    expired: Optional[bool] = None
    page: int = 1
    page_size: int = 50

class ListMessagesResponse(BaseModel):
    """Response model for message listing"""
    model_config = ConfigDict(extra="forbid")
    
    messages: List[Message]
    total: int
    page: int
    page_size: int
    error: Optional[str] = None

class ListMessages:
    """Query and filter system messages"""
    
    def __init__(self, reposet: RepoSet):
        self.message_repo = reposet["message_repository"]
        
    def execute(self, request: ListMessagesRequest) -> ListMessagesResponse:
        """List messages with optional filters"""
        try:
            # Calculate pagination
            offset = (request.page - 1) * request.page_size
            
            # Build filter criteria
            filters = {}
            if request.level:
                filters["level"] = request.level
            if request.target_type:
                filters["target_type"] = request.target_type
            if request.target_id:
                filters["target_id"] = request.target_id
            if request.acknowledged is not None:
                filters["acknowledged"] = request.acknowledged
                
            # Add expiry filter if requested
            now = datetime.now(UTC)
            if request.expired is not None:
                if request.expired:
                    filters["expires_at_lt"] = now
                else:
                    filters["expires_at_gt"] = now
            
            # Query messages
            messages = self.message_repo.list_messages(
                filters=filters,
                offset=offset,
                limit=request.page_size
            )
            
            # Get total count
            total = self.message_repo.count_messages(filters=filters)
            
            return ListMessagesResponse(
                messages=messages,
                total=total,
                page=request.page,
                page_size=request.page_size
            )
            
        except Exception as e:
            return ListMessagesResponse(
                messages=[],
                total=0,
                page=request.page,
                page_size=request.page_size,
                error=str(e)
            )
