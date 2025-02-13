"""Message cleanup usecase"""
from typing import Dict, Any
from datetime import datetime, timedelta, UTC

from ...domain import Message
from ...types import RepoSet

class CleanupExpiredMessages:
    """Remove expired system messages
    
    This usecase handles cleaning up old system messages based on retention policies
    and expiration settings. It removes messages that are no longer needed while
    preserving important notifications and acknowledged messages as needed.
    """
    
    def __init__(self, reposet: RepoSet):
        self.message_repo = reposet["message_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, retention_days: int = 30) -> Dict[str, Any]:
        """
        Clean up expired messages.
        
        Args:
            retention_days: Number of days to retain messages (default 30)
            
        Returns:
            Dict containing cleanup statistics:
                deleted: Number of messages deleted
                retained: Number of messages retained
                errors: Number of deletion errors
        """
        # Calculate cutoff date
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        
        stats = {
            "deleted": 0,
            "retained": 0,
            "errors": 0
        }
        
        # Get expired messages
        messages = self.message_repo.list_messages(end_time=cutoff)
        
        for message in messages:
            try:
                # Check if message can be deleted
                if self._can_delete(message):
                    # Delete the message
                    self.message_repo.delete_message(message.id)
                    stats["deleted"] += 1
                    
                    # Record deletion event
                    self.event_repo.record_event(
                        action_id="system",
                        direction="system",
                        content={"message_id": message.id},
                        content_type="message_deleted",
                        metadata={
                            "reason": "expired",
                            "deleted_at": datetime.now(UTC).isoformat()
                        }
                    )
                else:
                    stats["retained"] += 1
                    
            except Exception as e:
                stats["errors"] += 1
                self.event_repo.record_error(
                    "system",
                    f"Message cleanup failed: {str(e)}"
                )
                
        return stats
        
    def _can_delete(self, message: Message) -> bool:
        """Check if a message can be safely deleted"""
        # Don't delete if explicit expiry set and not reached
        if message.expires_at and message.expires_at > datetime.now(UTC):
            return False
            
        # Don't delete unacknowledged error messages
        if message.level == "error" and not message.acknowledged_at:
            return False
            
        # Don't delete messages marked for retention
        if any(field.name == "retain" and field.value 
               for field in message.metadata):
            return False
            
        return True
