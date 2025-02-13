"""Process and validate responses received after webhook delivery

Business Logic:
1. Validate webhook exists and is active
2. Extract expected fields from response using webhook config
3. Check for success/failure indicators
4. Record result and any relevant metrics
5. Return processed result with extracted data
"""
from typing import Dict, Any, Optional
from datetime import datetime, UTC

from ...domain import Webhook, WebhookResult
from ...types import RepoSet

class ProcessWebhookCallback:
    """Process responses from external webhook endpoints
    
    This usecase handles processing callback responses received from external systems
    after webhook delivery. It validates the response format, extracts relevant data,
    and records the results.
    """
    
    def __init__(self, reposet: RepoSet):
        self.webhook_repo = reposet["webhook_repository"]
        self.result_repo = reposet["result_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, webhook_id: str, response_data: Dict[str, Any]) -> WebhookResult:
        """Process a webhook callback response"""
        try:
            # Get and validate webhook
            webhook = self.webhook_repo.get_webhook(webhook_id)
            if not webhook:
                return WebhookResult(
                    result={},
                    error=f"Webhook not found: {webhook_id}"
                )
            if not webhook.enabled:
                return WebhookResult(
                    result={},
                    error=f"Webhook {webhook_id} is disabled"
                )

            # Extract expected fields
            result = {}
            expected_fields = webhook.config.get("callback_fields", [])
            
            for field in expected_fields:
                if field in response_data:
                    result[field] = str(response_data[field])
                    
            # Check for success indicators
            success_field = webhook.config.get("success_field")
            success_value = webhook.config.get("success_value")
            
            if success_field and success_field in response_data:
                actual = str(response_data[success_field])
                if actual != str(success_value):
                    error = f"Callback indicated failure: {actual}"
                    self._record_failure(webhook_id, error, response_data)
                    return WebhookResult(result=result, error=error)
                    
            # Record successful callback
            self._record_success(webhook_id, result, response_data)
            return WebhookResult(result=result)
            
        except Exception as e:
            error = f"Failed to process callback: {str(e)}"
            self._record_failure(webhook_id, error, response_data)
            return WebhookResult(result={}, error=error)
            
    def _record_success(self, webhook_id: str, result: Dict[str, str], raw_data: Dict[str, Any]) -> None:
        """Record successful callback processing"""
        self.event_repo.record_event(
            action_id=webhook_id,
            direction="inbound",
            content=raw_data,
            content_type="callback",
            metadata={
                "processed_at": datetime.now(UTC).isoformat(),
                "status": "success",
                "result": result
            }
        )
        
    def _record_failure(self, webhook_id: str, error: str, raw_data: Dict[str, Any]) -> None:
        """Record failed callback processing"""
        self.event_repo.record_event(
            action_id=webhook_id,
            direction="inbound", 
            content=raw_data,
            content_type="callback",
            metadata={
                "processed_at": datetime.now(UTC).isoformat(),
                "status": "error",
                "error": error
            }
        )
