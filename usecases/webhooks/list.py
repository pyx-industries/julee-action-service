"""List webhooks usecase"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from ...domain import Webhook
from ...types import RepoSet

class ListWebhooksRequest(BaseModel):
    """Request model for webhook listing"""
    model_config = ConfigDict(extra="forbid")
    
    enabled: Optional[bool] = None  # Filter by enabled status
    page: int = 1
    page_size: int = 50
    sort_by: str = "created_at"
    sort_desc: bool = True

class ListWebhooksResponse(BaseModel):
    """Response model for webhook listing"""
    model_config = ConfigDict(extra="forbid")
    
    webhooks: List[Webhook]
    total: int
    page: int
    page_size: int
    total_pages: int

class ListWebhooks:
    """Get list of configured webhooks"""
    
    def __init__(self, reposet: RepoSet):
        self.webhook_repo = reposet["webhook_repository"]
        
    def execute(self, request: ListWebhooksRequest) -> ListWebhooksResponse:
        """List webhooks with optional filtering and pagination"""
        try:
            # Calculate pagination
            offset = (request.page - 1) * request.page_size
            
            # Get webhooks with filters
            webhooks = self.webhook_repo.list_webhooks(
                enabled=request.enabled,
                offset=offset,
                limit=request.page_size,
                sort_by=request.sort_by,
                sort_desc=request.sort_desc
            )
            
            # Get total count for pagination
            total = self.webhook_repo.count_webhooks(enabled=request.enabled)
            total_pages = (total + request.page_size - 1) // request.page_size
            
            return ListWebhooksResponse(
                webhooks=webhooks,
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise ValueError(f"Error listing webhooks: {str(e)}")
