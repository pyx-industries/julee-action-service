"""Result cleanup usecase"""
from typing import Dict, Any
from datetime import datetime, timedelta, UTC

from ...domain import ActionResult
from ...types import RepoSet

class CleanupOldResults:
    """Remove expired action results
    
    This usecase handles cleaning up old action results based on retention policies.
    It removes results that are no longer needed while respecting any retention
    requirements for audit/compliance purposes.
    """
    
    def __init__(self, reposet: RepoSet):
        self.result_repo = reposet["result_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, retention_days: int = 30) -> Dict[str, Any]:
        """
        Clean up expired results.
        
        Args:
            retention_days: Number of days to retain results (default 30)
            
        Returns:
            Dict containing cleanup statistics:
                deleted: Number of results deleted
                retained: Number of results retained
                errors: Number of deletion errors
        """
        # Calculate cutoff date
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        
        stats = {
            "deleted": 0,
            "retained": 0,
            "errors": 0
        }
        
        # Get expired results
        results = self.result_repo.list_results(end_time=cutoff)
        
        for result in results:
            try:
                # Check if result can be deleted
                if self._can_delete(result):
                    # Delete the result
                    self.result_repo.delete_result(result.action_id)
                    stats["deleted"] += 1
                else:
                    stats["retained"] += 1
                    
            except Exception as e:
                stats["errors"] += 1
                self.event_repo.record_error(
                    result.action_id,
                    f"Result cleanup failed: {str(e)}"
                )
                
        return stats
        
    def _can_delete(self, result: ActionResult) -> bool:
        """Check if a result can be safely deleted"""
        # Don't delete results marked for retention
        if any(metric.name == "retain" and metric.value 
               for metric in result.history):
            return False
            
        # Don't delete results that are part of active retries
        retry_count = self.event_repo.get_retry_count(result.action_id)
        if retry_count > 0 and retry_count < 3:  # Max retries
            return False
            
        return True
