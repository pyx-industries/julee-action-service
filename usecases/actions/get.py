"""Get action details usecase"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

from ...domain import Action
from ...types import RepoSet

class GetActionRequest(BaseModel):
    """Request model for getting action details"""
    model_config = ConfigDict(extra="forbid")
    
    action_id: str

class GetActionResponse(BaseModel):
    """Response model for action details"""
    model_config = ConfigDict(extra="forbid")
    
    action: Optional[Action] = None
    status: str
    message: Optional[str] = None

class GetAction:
    """Get details for a single action"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        
    def execute(self, request: GetActionRequest) -> GetActionResponse:
        """Get action details by ID"""
        try:
            # Get action from repository
            action = self.action_repo.get_action(request.action_id)
            
            if not action:
                return GetActionResponse(
                    action=None,
                    status="not_found",
                    message=f"Action not found: {request.action_id}"
                )
                
            return GetActionResponse(
                action=action,
                status="success",
                message="Action retrieved successfully"
            )
            
        except Exception as e:
            return GetActionResponse(
                action=None,
                status="error",
                message=f"Error retrieving action: {str(e)}"
            )
