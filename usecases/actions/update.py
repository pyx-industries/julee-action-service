"""Update action configuration usecase"""
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from ...domain import Action
from ...types import RepoSet

class UpdateActionRequest(BaseModel):
    """Request model for updating action configuration"""
    model_config = ConfigDict(extra="forbid")
    
    action_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    credential_id: Optional[str] = None
    schedule: Optional[str] = None
    input_transform: Optional[Dict[str, Any]] = None
    output_transform: Optional[Dict[str, Any]] = None

class UpdateActionResponse(BaseModel):
    """Response model for action update"""
    model_config = ConfigDict(extra="forbid")
    
    action: Optional[Action] = None
    status: str
    message: Optional[str] = None

class UpdateAction:
    """Update an existing action's configuration"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, request: UpdateActionRequest) -> UpdateActionResponse:
        """Update action configuration"""
        try:
            # Get existing action
            action = self.action_repo.get_action(request.action_id)
            if not action:
                return UpdateActionResponse(
                    action=None,
                    status="not_found",
                    message=f"Action not found: {request.action_id}"
                )

            # Build update dictionary with only provided fields
            updates = {}
            if request.name is not None:
                updates["name"] = request.name
            if request.description is not None:
                updates["description"] = request.description
            if request.config is not None:
                updates["config"] = request.config
            if request.credential_id is not None:
                updates["credential_id"] = request.credential_id
            if request.schedule is not None:
                updates["schedule"] = request.schedule
            if request.input_transform is not None:
                updates["input_transform"] = request.input_transform
            if request.output_transform is not None:
                updates["output_transform"] = request.output_transform
                
            # Add updated timestamp
            updates["updated_at"] = datetime.now(UTC)

            # Update action
            updated_action = self.action_repo.update_action(request.action_id, updates)
            
            # Record audit event
            self.event_repo.record_event(
                action_id=request.action_id,
                direction="system",
                content={"updates": updates},
                content_type="action_update",
                metadata={"type": "configuration_change"}
            )
            
            return UpdateActionResponse(
                action=updated_action,
                status="success",
                message="Action updated successfully"
            )
            
        except Exception as e:
            return UpdateActionResponse(
                action=None,
                status="error",
                message=f"Error updating action: {str(e)}"
            )
