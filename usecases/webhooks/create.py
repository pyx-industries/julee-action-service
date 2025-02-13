"""Create webhook usecase"""
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from uuid import uuid4

from ...domain import Webhook
from ...types import RepoSet

class CreateWebhookRequest(BaseModel):
    """Request model for webhook creation"""
    model_config = ConfigDict(extra="forbid")
    
    key: str  # Authentication key for the webhook
    config: Dict[str, Any]  # Webhook configuration (endpoints, headers, etc)
    description: Optional[str] = None
    enabled: bool = True

class CreateWebhookResponse(BaseModel):
    """Response model for webhook creation"""
    model_config = ConfigDict(extra="forbid")
    
    webhook_id: str
    status: str
    message: Optional[str] = None
    created_at: datetime

class CreateWebhook:
    """Create a new webhook endpoint"""
    
    def __init__(self, reposet: RepoSet):
        self.webhook_repo = reposet["webhook_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, request: CreateWebhookRequest) -> CreateWebhookResponse:
        """Create a new webhook"""
        try:
            # Generate unique webhook ID
            webhook_id = str(uuid4())
            
            # Create webhook object
            webhook = Webhook(
                id=webhook_id,
                key=request.key,
                config=request.config,
                enabled=request.enabled
            )
            
            # Store webhook
            self.webhook_repo.create_webhook(webhook)
            
            # Record audit event
            self.event_repo.record_event(
                action_id=webhook_id,  # Use webhook ID as action ID for audit
                direction="system",
                content={
                    "config": request.config,
                    "enabled": request.enabled
                },
                content_type="webhook_create",
                metadata={
                    "type": "configuration_change",
                    "resource_type": "webhook"
                }
            )
            
            return CreateWebhookResponse(
                webhook_id=webhook_id,
                status="success",
                message="Webhook created successfully",
                created_at=datetime.now(UTC)
            )
            
        except Exception as e:
            return CreateWebhookResponse(
                webhook_id="",
                status="error",
                message=f"Error creating webhook: {str(e)}",
                created_at=datetime.now(UTC)
            )
