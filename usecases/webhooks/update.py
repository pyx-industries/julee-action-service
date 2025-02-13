"""Update webhook usecase"""
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from ...domain import Webhook
from ...types import RepoSet

class UpdateWebhookRequest(BaseModel):
    """Request model for webhook updates"""
    model_config = ConfigDict(extra="forbid")
    
    webhook_id: str
    config: Optional[Dict[str, Any]] = None  # Optional webhook configuration updates
    key: Optional[str] = None  # Optional key update
    enabled: Optional[bool] = None  # Optional enabled state update
    description: Optional[str] = None

class UpdateWebhookResponse(BaseModel):
    """Response model for webhook updates"""
    model_config = ConfigDict(extra="forbid")
    
    webhook_id: str
    status: str
    message: Optional[str] = None
    updated_at: datetime

class UpdateWebhook:
    """Update an existing webhook configuration"""
    
    def __init__(self, reposet: RepoSet):
        self.webhook_repo = reposet["webhook_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, request: UpdateWebhookRequest) -> UpdateWebhookResponse:
        """Update webhook configuration"""
        try:
            # Get existing webhook
            webhook = self.webhook_repo.get_webhook(request.webhook_id)
            if not webhook:
                return UpdateWebhookResponse(
                    webhook_id=request.webhook_id,
                    status="not_found",
                    message=f"Webhook not found: {request.webhook_id}",
                    updated_at=datetime.now(UTC)
                )
            
            # Build update dictionary with only provided fields
            updates = {}
            if request.config is not None:
                updates["config"] = request.config
            if request.key is not None:
                updates["key"] = request.key
            if request.enabled is not None:
                updates["enabled"] = request.enabled
                
            # Update webhook
            updated_webhook = self.webhook_repo.update_webhook(
                webhook_id=request.webhook_id,
                updates=updates
            )
            
            # Record audit event
            self.event_repo.record_event(
                action_id=request.webhook_id,
                direction="system",
                content={
                    "updates": updates,
                    "previous_config": webhook.config,
                    "previous_enabled": webhook.enabled
                },
                content_type="webhook_update",
                metadata={
                    "type": "configuration_change",
                    "resource_type": "webhook"
                }
            )
            
            return UpdateWebhookResponse(
                webhook_id=request.webhook_id,
                status="success",
                message="Webhook updated successfully",
                updated_at=datetime.now(UTC)
            )
            
        except Exception as e:
            return UpdateWebhookResponse(
                webhook_id=request.webhook_id,
                status="error",
                message=f"Error updating webhook: {str(e)}",
                updated_at=datetime.now(UTC)
            )
