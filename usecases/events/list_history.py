"""Event history usecase"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ...domain import Event
from ...types import RepoSet

class ListEventHistory:
    """List historical event data with filtering options
    
    This usecase provides access to historical event data with flexible filtering
    options including date ranges, event types, and status filters. It supports
    pagination for handling large result sets efficiently.
    """
    
    def __init__(self, reposet: RepoSet):
        self.event_repo = reposet["event_repository"]
        
    def execute(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[str]] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        List historical events with filtering.
        
        Args:
            start_time: Optional start of time range
            end_time: Optional end of time range
            event_types: Optional list of event types to include
            status: Optional status filter
            page: Page number (1-based)
            page_size: Number of results per page
            
        Returns:
            Dict containing:
                events: List of matching events
                total: Total number of matching events
                page: Current page number
                pages: Total number of pages
        """
        # Default time range if not specified
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(days=7)  # Default to last 7 days
            
        # Get events with filters
        events = self.event_repo.list_events(
            start_time=start_time,
            end_time=end_time,
            event_types=event_types,
            status=status
        )
        
        # Calculate pagination
        total = len(events)
        total_pages = (total + page_size - 1) // page_size
        
        # Get requested page
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_events = events[start_idx:end_idx]
        
        return {
            "events": [self._format_event(e) for e in page_events],
            "total": total,
            "page": page,
            "pages": total_pages
        }
        
    def _format_event(self, event: Event) -> Dict[str, Any]:
        """Format event for API response"""
        return {
            "id": event.id,
            "action_id": event.action_id,
            "direction": event.direction,
            "content_type": event.content_type,
            "created_at": event.created_at.isoformat(),
            "processed_at": event.processed_at.isoformat() if event.processed_at else None,
            "status": event.status,
            "error": event.error,
            "metadata": {
                field.name: field.value
                for field in event.metadata
            } if event.metadata else {}
        }
