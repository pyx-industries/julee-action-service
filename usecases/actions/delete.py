"""Delete action usecase"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

from ...domain import Action
from ...types import RepoSet

class DeleteActionRequest(BaseModel):
    """Request model for deleting an action"""
    model_config = ConfigDict(extra="forbid")
    
    action_id: str
    force: bool = False  # Whether to force delete even if dependencies exist

class DeleteActionResponse(BaseModel):
    """Response model for action deletion"""
    model_config = ConfigDict(extra="forbid")
    
    status: str
    message: Optional[str] = None
    dependencies: Optional[list[str]] = None  # List of dependent resource IDs if any

class DeleteAction:
    """Remove an existing action"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, request: DeleteActionRequest) -> DeleteActionResponse:
        """Delete an action"""
        try:
            # Check action exists
            action = self.action_repo.get_action(request.action_id)
            if not action:
                return DeleteActionResponse(
                    status="not_found",
                    message=f"Action not found: {request.action_id}"
                )
                
            # Check for dependencies unless force delete
            if not request.force:
                dependencies = self.action_repo.get_dependencies(request.action_id)
                if dependencies:
                    return DeleteActionResponse(
                        status="has_dependencies",
                        message="Action has active dependencies",
                        dependencies=dependencies
                    )
            
            # Delete the action
            self.action_repo.delete_action(request.action_id)
            
            # Record audit event
            self.event_repo.record_event(
                action_id=request.action_id,
                direction="system",
                content={"force_delete": request.force},
                content_type="action_delete",
                metadata={"type": "configuration_change"}
            )
            
            return DeleteActionResponse(
                status="success",
                message="Action deleted successfully"
            )
            
        except Exception as e:
            return DeleteActionResponse(
                status="error",
                message=f"Error deleting action: {str(e)}"
            )
