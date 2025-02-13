from typing import Dict
import uuid
from ..domain import Action, ActionResult, Protocol
from .settings import get_repositories

class ExecuteAction:
    """Execute an action using protocol-specific repositories."""
    
    def __init__(self, action: Action):
        repos = get_repositories(action.protocol.id)
        self.action_repo = repos['action_repo']
        self.event_repo = repos['event_repo']
        self.action = action

    def execute(self) -> ActionResult:
        """Execute the action and return the result."""
        try:
            # Execute using protocol-specific repository
            result = self.action_repo.execute(self.action)
            
            # Record the event
            self.event_repo.record_success(self.action.id, result)
            
            return ActionResult(
                action_id=self.action.id,
                request_id=str(uuid.uuid4()),
                success=True,
                result=result
            )
            
        except Exception as e:
            # Record failure event
            self.event_repo.record_failure(self.action.id, str(e))
            
            return ActionResult(
                action_id=self.action.id,
                request_id=str(uuid.uuid4()),
                success=False,
                error=str(e)
            )
