"""Action execution usecases"""
from typing import Optional
from datetime import datetime

from ..domain import Action, ActionResult
from ..interfaces.requests import ExecuteActionRequest 
from ..interfaces.responses import ActionStatusResponse
from ..types import RepoSet

class ExecuteAction:
    """Execute a single action"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        self.behaviour_repo = reposet["behaviour_repository"]
        self.credential_repo = reposet["credential_repository"]
        
    def execute(self, request: ExecuteActionRequest) -> ActionStatusResponse:
        """Execute an action based on the request.
        
        Args:
            request: The execution request containing action details
            
        Returns:
            ActionStatusResponse with execution result details
        """
        try:
            # Get action from repository using action_id from request
            action = self.action_repo.get_action(request.action_id)
            if not action:
                return ActionStatusResponse(
                    request_id=request.action_id,
                    correlation_id=request.correlation_id,
                    status="failed",
                    error="Action not found"
                )

            # Get protocol handler
            handler = self.behaviour_repo.get_protocol_handler(
                action.protocol,
                action.config
            )
            
            # Add credentials if needed
            if action.credential_id and self.credential_repo:
                credential = self.credential_repo.get_credential(action.credential_id)
                if credential:
                    handler.add_credentials(credential)

            # Try to execute via action repository
            try:
                result = handler.execute(action)
                
                # Record event based on result
                if result.success:
                    self.event_repo.record_success(action.id, result.result)
                    return ActionStatusResponse(
                        request_id=request.action_id,
                        correlation_id=request.correlation_id,
                        status="completed",
                        result=result.result,
                        completion_time=datetime.now()
                    )
                else:
                    self.event_repo.record_failure(action.id, result.error)
                    return ActionStatusResponse(
                        request_id=request.action_id,
                        correlation_id=request.correlation_id,
                        status="failed",
                        error=result.error,
                        completion_time=datetime.now()
                    )

            except Exception as e:
                # Record failure and return failed result
                error = f"Action execution failed: {str(e)}"
                self.event_repo.record_failure(action.id, error)
                return ActionStatusResponse(
                    request_id=request.id,
                    correlation_id=request.correlation_id,
                    status="failed",
                    error=error,
                    completion_time=datetime.now()
                )
                
        except Exception as e:
            # Handle any other errors
            error = f"Action setup failed: {str(e)}"
            self.event_repo.record_failure(action.id, error)
            return ActionStatusResponse(
                request_id=request.action_id,
                correlation_id=request.correlation_id,
                status="failed", 
                error=error,
                completion_time=datetime.now()
            )
"""Action execution usecases"""
from typing import Optional
from datetime import datetime

from ..domain import Action, ActionResult
from ..worker_service.settings import RepoSet

class ExecuteAction:
    """Execute a single action"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        self.behaviour_repo = reposet["behaviour_repository"]
        self.credential_repo = reposet["credential_repository"]
        
    def execute(self, request: ExecuteActionRequest) -> ActionStatusResponse:
        try:
            # Get action from repository using request ID
            action = self.action_repo.get_action(request.action_id)
            if not action:
                return ActionStatusResponse(
                    request_id=request.action_id,
                    correlation_id=request.correlation_id,
                    status="failed",
                    error="Action not found"
                )

            # Try to execute via action repository
            try:
                self.action_repo.execute(action)
            except Exception as e:
                # Record failure and return failed result
                error = f"Action execution failed: {str(e)}"
                self.event_repo.record_failure(action.id, error)
                return ActionStatusResponse(
                    request_id=request.action_id,
                    correlation_id=request.correlation_id,
                    status="failed",
                    error=error,
                    completion_time=datetime.now()
                )

            # If we get here, execution succeeded
            result = {
                "status": "ok",
                "details": "Action executed successfully"
            }
            self.event_repo.record_success(action.id, result)
            
            return ActionStatusResponse(
                request_id=request.action_id,
                correlation_id=request.correlation_id,
                status="completed",
                result=result,
                completion_time=datetime.now()
            )
                
        except Exception as e:
            # Handle any other errors
            error = f"Action setup failed: {str(e)}"
            self.event_repo.record_failure(request.action_id, error)
            return ActionStatusResponse(
                request_id=request.id,
                correlation_id=request.correlation_id,
                status="failed", 
                error=error,
                completion_time=datetime.now()
            )
