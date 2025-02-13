"""Remove webhook endpoints and clean up associated resources

Business Logic:
1. Validate webhook exists
2. Check for active connections unless force delete requested
3. Remove webhook configuration
4. Clean up any associated resources
5. Record audit event for deletion
"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime, UTC

from ...domain import Webhook
from ...types import RepoSet

class DeleteWebhookRequest(BaseModel):
    """Request model for webhook deletion"""
    model_config = ConfigDict(extra="forbid")
    
    webhook_id: str
    force: bool = False  # Whether to force delete even if active connections exist

class DeleteWebhookResponse(BaseModel):
    """Response model for webhook deletion"""
    model_config = ConfigDict(extra="forbid")
    
    webhook_id: str
    status: str
    message: Optional[str] = None
    active_connections: Optional[List[str]] = None  # List of active connection IDs if any
    deleted_at: datetime

class DeleteWebhook:
    """Remove an existing webhook endpoint"""
    
    def __init__(self, reposet: RepoSet):
        self._webhook_repo = reposet["webhook_repository"]
        self._event_repo = reposet["event_repository"]
        
    def execute(self, request: DeleteWebhookRequest) -> DeleteWebhookResponse:
        """Delete a webhook"""
        try:
            # Check webhook exists
            webhook = self.webhook_repo.get_webhook(request.webhook_id)
            if not webhook:
                return DeleteWebhookResponse(
                    webhook_id=request.webhook_id,
                    status="not_found",
                    message=f"Webhook not found: {request.webhook_id}",
                    deleted_at=datetime.now(UTC)
                )
            
            # Check for active connections unless force delete
            if not request.force:
                active_connections = self.webhook_repo.get_active_connections(request.webhook_id)
                if active_connections:
                    return DeleteWebhookResponse(
                        webhook_id=request.webhook_id,
                        status="has_connections",
                        message="Webhook has active connections",
                        active_connections=active_connections,
                        deleted_at=datetime.now(UTC)
                    )
            
            # Delete the webhook
            self.webhook_repo.delete_webhook(request.webhook_id)
            
            # Record audit event
            self.event_repo.record_event(
                action_id=request.webhook_id,
                direction="system",
                content={
                    "force_delete": request.force,
                    "previous_config": webhook.config,
                    "previous_enabled": webhook.enabled
                },
                content_type="webhook_delete",
                metadata={
                    "type": "configuration_change",
                    "resource_type": "webhook"
                }
            )
            
            return DeleteWebhookResponse(
                webhook_id=request.webhook_id,
                status="success",
                message="Webhook deleted successfully",
                deleted_at=datetime.now(UTC)
            )
            
        except Exception as e:
            return DeleteWebhookResponse(
                webhook_id=request.webhook_id,
                status="error", 
                message=f"Error deleting webhook: {str(e)}",
                deleted_at=datetime.now(UTC)
            )
