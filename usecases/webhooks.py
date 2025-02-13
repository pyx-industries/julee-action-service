"""Webhook handling usecases"""
from datetime import datetime, UTC
from typing import Optional
from uuid import uuid4
import json

from ..interfaces.requests import WebhookRequest
from ..interfaces.responses import WebhookAcceptedResponse, WebhookStatusResponse, WebhookErrorResponse
from ..types import RepoSet

class ReceiveWebhook:
    """Handle incoming webhook requests"""
    
    def __init__(self, reposet: RepoSet):
        self.webhook_repo = reposet["webhook_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, webhook_id: str, key: str, request: WebhookRequest) -> Optional[WebhookAcceptedResponse]:
        """Process incoming webhook synchronously"""
        # Validate webhook exists
        webhook = self.webhook_repo.get_webhook(webhook_id)
        if not webhook or webhook.key != key:
            return None
            
        # Convert payload to raw bytes if needed
        if request.raw_data is not None:
            raw_body = request.raw_data
        elif request.payload is not None:
            raw_body = json.dumps(request.payload).encode('utf-8')
        else:
            raw_body = b''
            
        # Store raw request and get response ID
        response_id = self.event_repo.record_received(
            webhook_id=webhook_id,
            raw_headers=request.headers,
            raw_body=raw_body,
            content_type=request.content_type,
            correlation_id=request.correlation_id
        )
        
        # Queue for async processing
        self._queue_processing(webhook_id, response_id)
        
        # Return synchronous response
        return WebhookAcceptedResponse(
            response_id=response_id,
            status="accepted",
            correlation_id=request.correlation_id,
            timestamp=datetime.now(UTC)
        )

    def _validate_webhook(self, webhook_id: str, key: str) -> bool:
        """Validate webhook ID and key"""
        return self.webhook_repo.validate_key(webhook_id, key)
        
    def _queue_processing(self, webhook_id: str, response_id: str) -> None:
        """Queue webhook for async processing"""
        # Implementation depends on message queue choice

class GetWebhookStatus:
    """Get status of webhook processing"""
    
    def __init__(self, reposet: RepoSet):
        self.event_repo = reposet["event_repository"]
        self.result_repo = reposet["result_repository"]
        
    def execute(self, response_id: str) -> WebhookStatusResponse:
        """Get current status"""
        try:
            # Get latest event status
            status = self.event_repo.get_status(response_id)
            if not status:
                raise ValueError(f"Unknown response ID: {response_id}")
                
            result = None
            error = None
            
            # Get result based on status
            if status.state in ["completed", "failed"]:
                webhook_result = self.result_repo.get_result(response_id)
                if webhook_result:
                    result = webhook_result.result
                    error = webhook_result.error
            
            # Use status error as fallback
            if not error and status.error:
                error = status.error

            return WebhookStatusResponse(
                response_id=response_id,
                status=status.state,
                result=result,
                error=error,
                correlation_id=status.correlation_id,
                timestamp=datetime.now(UTC)
            )
            
        except Exception as e:
            raise # Let API layer handle error response
