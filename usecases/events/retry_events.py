"""Failed event retry usecase"""
from typing import Dict, Any, List
from datetime import datetime, UTC, timedelta

from ...domain import Event, ActionResult
from ...types import RepoSet

class RetryFailedEvents:
    """Retry processing of failed events
    
    This usecase handles retrying events that previously failed processing,
    following configured retry policies and tracking retry attempts.
    It implements exponential backoff and respects maximum retry limits.
    """
    
    def __init__(self, reposet: RepoSet):
        self.event_repo = reposet["event_repository"]
        self.action_repo = reposet["action_repository"]
        self.result_repo = reposet["result_repository"]
        
    def execute(self, max_retries: int = 3, batch_size: int = 50) -> Dict[str, Any]:
        """
        Retry processing of failed events.
        
        Args:
            max_retries: Maximum number of retry attempts per event
            batch_size: Maximum number of events to retry in this batch
            
        Returns:
            Dict containing retry statistics:
                retried: Number of events retried
                succeeded: Number of successful retries
                failed: Number of failed retries
                max_attempts: Number that hit max retries
        """
        # Get batch of failed events eligible for retry
        events = self.event_repo.get_failed_events(
            max_retry_count=max_retries,
            limit=batch_size
        )
        
        stats = {
            "retried": 0,
            "succeeded": 0,
            "failed": 0,
            "max_attempts": 0
        }
        
        # Process each failed event
        for event in events:
            try:
                # Check retry count
                retry_count = self.event_repo.get_retry_count(event.id)
                if retry_count >= max_retries:
                    stats["max_attempts"] += 1
                    continue
                    
                # Calculate backoff delay
                backoff = self._calculate_backoff(retry_count)
                if not self._should_retry_now(event, backoff):
                    continue
                    
                # Get associated action
                action = self.action_repo.get_action(event.action_id)
                if not action:
                    self._handle_permanent_failure(event, "Action not found")
                    stats["failed"] += 1
                    continue
                    
                # Attempt retry
                result = self.action_repo.execute(action, event.content)
                
                if result.success:
                    self._handle_success(event, result)
                    stats["succeeded"] += 1
                else:
                    self._handle_failure(event, result.error, retry_count + 1)
                    stats["failed"] += 1
                    
                stats["retried"] += 1
                
            except Exception as e:
                self._handle_failure(event, str(e), retry_count + 1)
                stats["failed"] += 1
                stats["retried"] += 1
                
        return stats
        
    def _calculate_backoff(self, retry_count: int) -> timedelta:
        """Calculate exponential backoff delay"""
        # Base delay of 30 seconds with exponential increase
        delay_seconds = 30 * (2 ** retry_count)
        # Cap at 1 hour
        return timedelta(seconds=min(delay_seconds, 3600))
        
    def _should_retry_now(self, event: Event, backoff: timedelta) -> bool:
        """Check if enough time has passed for retry"""
        if not event.processed_at:
            return True
            
        return datetime.now(UTC) - event.processed_at >= backoff
        
    def _handle_success(self, event: Event, result: ActionResult) -> None:
        """Handle successful retry"""
        self.event_repo.update_status(
            event.id,
            status="completed",
            processed_at=datetime.now(UTC)
        )
        
        self.result_repo.store_result(
            event_id=event.id,
            success=True,
            result=result.result
        )
        
    def _handle_failure(self, event: Event, error: str, retry_count: int) -> None:
        """Handle failed retry attempt"""
        self.event_repo.update_status(
            event.id,
            status="failed",
            processed_at=datetime.now(UTC),
            error=error,
            retry_count=retry_count
        )
        
    def _handle_permanent_failure(self, event: Event, error: str) -> None:
        """Handle permanent failure (no more retries)"""
        self.event_repo.update_status(
            event.id,
            status="failed",
            processed_at=datetime.now(UTC),
            error=error
        )
        
        self.result_repo.store_result(
            event_id=event.id,
            success=False,
            error=error
        )
