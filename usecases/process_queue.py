"""Event queue processing usecase"""
from typing import Dict, Any, List, Optional
from datetime import datetime, UTC

from ..domain import Event, ActionResult
from ..types import RepoSet

class ProcessEventQueue:
    """Process events from the queue
    
    This usecase handles processing batches of events from the event queue,
    executing the appropriate actions for each event, and managing retries
    and error handling according to configured policies.
    """
    
    def __init__(self, reposet: RepoSet):
        self.event_repo = reposet["event_repository"]
        self.action_repo = reposet["action_repository"]
        self.result_repo = reposet["result_repository"]
        
    def execute(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        Process a batch of events from the queue.
        
        Args:
            batch_size: Maximum number of events to process in this batch
            
        Returns:
            Dict containing processing statistics:
                processed: Number of events processed
                succeeded: Number of successful events
                failed: Number of failed events
                retry_scheduled: Number of events scheduled for retry
        """
        # Get batch of events
        events = self.event_repo.get_pending_events(limit=batch_size)
        
        stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "retry_scheduled": 0
        }
        
        # Process each event
        for event in events:
            try:
                # Get associated action
                action = self.action_repo.get_action(event.action_id)
                if not action:
                    self._handle_failure(event, "Action not found")
                    stats["failed"] += 1
                    continue
                    
                # Execute action
                result = self.action_repo.execute(action, event.content)
                
                if result.success:
                    self._handle_success(event, result)
                    stats["succeeded"] += 1
                else:
                    retry = self._handle_failure(event, result.error)
                    if retry:
                        stats["retry_scheduled"] += 1
                    else:
                        stats["failed"] += 1
                        
                stats["processed"] += 1
                
            except Exception as e:
                retry = self._handle_failure(event, str(e))
                if retry:
                    stats["retry_scheduled"] += 1
                else:
                    stats["failed"] += 1
                stats["processed"] += 1
                
        return stats
        
    def _handle_success(self, event: Event, result: ActionResult) -> None:
        """Handle successful event processing"""
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
        
    def _handle_failure(self, event: Event, error: str) -> bool:
        """Handle failed event processing, returns True if retry scheduled"""
        self.event_repo.update_status(
            event.id,
            status="failed",
            processed_at=datetime.now(UTC),
            error=error
        )
        
        # Check retry policy
        retry_count = self.event_repo.get_retry_count(event.id)
        max_retries = 3  # TODO: Get from config
        
        if retry_count < max_retries:
            self.event_repo.schedule_retry(event.id)
            return True
            
        self.result_repo.store_result(
            event_id=event.id,
            success=False,
            error=error
        )
        return False
