"""Action result storage usecase"""
from typing import Dict, Any, Optional
from datetime import datetime, UTC
import uuid

from ...domain import Action, ActionResult
from ...types import RepoSet

class StoreActionResult:
    """Store and manage action execution results
    
    This usecase handles storing action execution results, including success/failure 
    status, result data, error details, and execution metrics. It manages result 
    persistence and handles any required post-processing or notifications.
    """
    
    def __init__(self, reposet: RepoSet):
        self.result_repo = reposet["result_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(
        self, 
        action_id: str,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> ActionResult:
        """
        Store an action execution result.
        
        Args:
            action_id: ID of the action that was executed
            success: Whether execution was successful
            result: Optional result data for successful executions
            error: Optional error message for failed executions
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            ActionResult containing stored result details
        """
        try:
            # Create result record
            action_result = ActionResult(
                action_id=action_id,
                request_id=correlation_id or str(uuid.uuid4()),
                success=success,
                result=result,
                error=error,
                created_at=datetime.now(UTC)
            )
            
            # Store the result
            self.result_repo.store_result(action_result)
            
            # Record result event
            self.event_repo.record_event(
                action_id=action_id,
                direction="system",
                content={
                    "success": success,
                    "result": result,
                    "error": error
                },
                content_type="result",
                metadata={
                    "correlation_id": correlation_id,
                    "stored_at": datetime.now(UTC).isoformat()
                }
            )
            
            return action_result
            
        except Exception as e:
            # Record storage failure
            self.event_repo.record_event(
                action_id=action_id,
                direction="system",
                content={"error": str(e)},
                content_type="result_error",
                metadata={
                    "correlation_id": correlation_id,
                    "error_at": datetime.now(UTC).isoformat()
                }
            )
            raise
