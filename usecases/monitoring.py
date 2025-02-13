"""Monitoring usecases"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from ..domain import Action, ActionResult, Metric
from ..interfaces.repositories import ActionRepository, EventRepository
from ..types import RepoSet

class TrackDeliveryMetrics:
    """Track metrics for message delivery"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"] 
        self.event_repo = reposet["event_repository"]
        
    def record_attempt(self, action: Action, success: bool, duration: float) -> None:
        """Record a delivery attempt"""
        metrics = [
            Metric(name="delivery_success", value=success),
            Metric(name="delivery_duration", value=duration)
        ]
        
        self.event_repo.record_event(
            action_id=action.id,
            direction="outbound",
            content={"metrics": metrics},
            content_type="metrics",
            metadata={"type": "delivery_attempt"}
        )
        
    def get_metrics(self, action: Action) -> List[Metric]:
        """Get current metrics"""
        events = self.event_repo.list_events(
            action_id=action.id,
            content_type="metrics"
        )
        
        metrics = []
        for event in events:
            if event.content and "metrics" in event.content:
                metrics.extend(event.content["metrics"])
        return metrics

class MonitorStreamHealth:
    """Monitor health of a message stream"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        
    def check_health(self, stream_id: str) -> Dict[str, Any]:
        """Check stream health status"""
        events = self.event_repo.list_events(
            action_id=stream_id,
            start_time=datetime.now() - timedelta(minutes=5)
        )
        
        return {
            "total_events": len(events),
            "success_rate": self._calculate_success_rate(events),
            "error_count": self._count_errors(events),
            "avg_duration": self._calculate_avg_duration(events)
        }
        
    def record_error(self, stream_id: str, error: str) -> None:
        """Record a stream error"""
        self.event_repo.record_event(
            action_id=stream_id,
            direction="system",
            content={"error": error},
            content_type="error",
            metadata={"type": "stream_error"}
        )
        
    def _calculate_success_rate(self, events: List[Dict]) -> float:
        if not events:
            return 0.0
        successes = sum(1 for e in events if e.get("success", False))
        return successes / len(events)
        
    def _count_errors(self, events: List[Dict]) -> int:
        return sum(1 for e in events if e.get("error"))
        
    def _calculate_avg_duration(self, events: List[Dict]) -> float:
        durations = [e.get("duration", 0) for e in events if "duration" in e]
        return sum(durations) / len(durations) if durations else 0

class CollectProtocolMetrics:
    """Collect metrics for a protocol"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        
    def collect(self, protocol_id: str) -> List[Metric]:
        """Collect current protocol metrics"""
        events = self.event_repo.list_events(
            metadata={"protocol_id": protocol_id},
            start_time=datetime.now() - timedelta(hours=1)
        )
        
        return [
            Metric(name="total_events", value=len(events)),
            Metric(name="success_rate", value=self._calculate_success_rate(events)),
            Metric(name="error_rate", value=self._calculate_error_rate(events)),
            Metric(name="avg_duration", value=self._calculate_avg_duration(events))
        ]
        
    def _calculate_success_rate(self, events: List[Dict]) -> float:
        if not events:
            return 0.0
        successes = sum(1 for e in events if e.get("success", False))
        return successes / len(events)
        
    def _calculate_error_rate(self, events: List[Dict]) -> float:
        if not events:
            return 0.0
        errors = sum(1 for e in events if e.get("error"))
        return errors / len(events)
        
    def _calculate_avg_duration(self, events: List[Dict]) -> float:
        durations = [e.get("duration", 0) for e in events if "duration" in e]
        return sum(durations) / len(durations) if durations else 0
