"""Event status usecase"""
from typing import Dict, Any, Optional
from datetime import datetime, UTC

from ...domain import Event, EventStatus
from ...types import RepoSet

class GetDetailedEventStatus:
    """Get detailed status information for an event
    
    This usecase provides comprehensive status information about an event,
    including its current state, processing history, and any error details.
    It aggregates data from multiple repositories to build a complete
    status picture.
    """
    
    def __init__(self, reposet: RepoSet):
        self.event_repo = reposet["event_repository"]
        self.result_repo = reposet["result_repository"]
        
    def execute(self, event_id: str) -> Dict[str, Any]:
        """
        Get detailed status for an event.
        
        Args:
            event_id: ID of the event to check
            
        Returns:
            Dict containing detailed status information
            
        Raises:
            ValueError: If event_id not found
        """
        # Get event details
        event = self.event_repo.get_event(event_id)
        if not event:
            raise ValueError(f"Event not found: {event_id}")
            
        # Get latest status
        status = self.event_repo.get_status(event_id)
        if not status:
            status = EventStatus(
                state="unknown",
                timestamp=event.created_at
            )
            
        # Get processing result if available
        result = None
        if status.state in ["completed", "failed"]:
            result = self.result_repo.get_result(event_id)
            
        # Build detailed status response
        return {
            "event_id": event_id,
            "current_state": status.state,
            "created_at": event.created_at.isoformat(),
            "last_updated": status.timestamp.isoformat(),
            "correlation_id": status.correlation_id,
            "direction": event.direction,
            "content_type": event.content_type,
            "error": status.error or (result.error if result else None),
            "result": result.result if result else None,
            "metadata": {
                field.name: field.value 
                for field in event.metadata
            } if event.metadata else {},
            "metrics": {
                metric.name: metric.value
                for metric in event.metrics
            } if event.metrics else {}
        }
