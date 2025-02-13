"""Event cleanup usecase"""
from typing import Dict, Any
from datetime import datetime, timedelta, UTC

from ...domain import Event
from ...types import RepoSet

class CleanupExpiredEvents:
    """Remove old event data based on retention policies
    
    This usecase handles cleaning up expired event data according to configured 
    retention policies. It removes old events, results, and associated metadata
    while respecting any legal/compliance retention requirements.
    """
    
    def __init__(self, reposet: RepoSet):
        self.event_repo = reposet["event_repository"]
        self.result_repo = reposet["result_repository"]
        
    def execute(self, retention_days: int = 90) -> Dict[str, Any]:
        """
        Clean up expired events.
        
        Args:
            retention_days: Number of days to retain events (default 90)
            
        Returns:
            Dict containing cleanup statistics:
                deleted: Number of events deleted
                retained: Number of events retained
                errors: Number of deletion errors
        """
        # Calculate cutoff date
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        
        stats = {
            "deleted": 0,
            "retained": 0,
            "errors": 0
        }
        
        # Get expired events
        events = self.event_repo.list_events(end_time=cutoff)
        
        for event in events:
            try:
                # Check if event can be deleted
                if self._can_delete(event):
                    # Delete associated result first
                    self.result_repo.delete_result(event.id)
                    
                    # Then delete the event
                    self.event_repo.delete_event(event.id)
                    stats["deleted"] += 1
                else:
                    stats["retained"] += 1
                    
            except Exception as e:
                stats["errors"] += 1
                self.event_repo.record_error(
                    event.id,
                    f"Cleanup failed: {str(e)}"
                )
                
        return stats
        
    def _can_delete(self, event: Event) -> bool:
        """Check if an event can be safely deleted"""
        # Don't delete events that haven't been processed
        if event.status == "pending":
            return False
            
        # Don't delete events marked for retention
        if any(field.name == "retain" and field.value 
               for field in event.metadata):
            return False
            
        # Don't delete events with active retries
        retry_count = self.event_repo.get_retry_count(event.id)
        if retry_count > 0 and retry_count < 3:  # Max retries
            return False
            
        return True
