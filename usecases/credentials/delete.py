"""Delete credential usecase"""
from datetime import datetime, UTC
from typing import Optional
from pydantic import BaseModel, ConfigDict

from ...domain import Credential
from ...types import RepoSet

class DeleteCredentialResponse(BaseModel):
    """Response model for credential deletion"""
    model_config = ConfigDict(extra="forbid")
    
    credential_id: str
    deleted_at: datetime
    success: bool
    error: Optional[str] = None

class DeleteCredential:
    """Remove stored credentials"""
    
    def __init__(self, reposet: RepoSet):
        self.credential_repo = reposet["credential_repository"]
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, credential_id: str) -> DeleteCredentialResponse:
        """Delete a credential and clean up references"""
        try:
            # Check credential exists
            credential = self.credential_repo.get_credential(credential_id)
            if not credential:
                raise ValueError(f"Credential not found: {credential_id}")
                
            # Check for actions using this credential
            dependent_actions = self.action_repo.list_actions(credential_id=credential_id)
            if dependent_actions:
                action_ids = [a.id for a in dependent_actions]
                raise ValueError(
                    f"Credential in use by actions: {', '.join(action_ids)}"
                )
                
            # Delete the credential
            self.credential_repo.delete_credential(credential_id)
            
            # Record audit event
            self.event_repo.record_event(
                action_id=credential_id,
                direction="system",
                content={"operation": "delete_credential"},
                content_type="audit",
                metadata={
                    "credential_id": credential_id,
                    "protocol_id": credential.protocol.id
                }
            )
            
            return DeleteCredentialResponse(
                credential_id=credential_id,
                deleted_at=datetime.now(UTC),
                success=True
            )
            
        except Exception as e:
            return DeleteCredentialResponse(
                credential_id=credential_id,
                deleted_at=datetime.now(UTC),
                success=False,
                error=str(e)
            )
