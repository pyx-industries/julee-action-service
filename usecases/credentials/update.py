"""Update credential usecase"""
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from ...domain import Credential, Protocol, SecretCollection
from ...types import RepoSet

class UpdateCredentialRequest(BaseModel):
    """Request model for credential updates"""
    model_config = ConfigDict(extra="forbid")
    
    name: Optional[str] = None
    secrets: Optional[Dict[str, str]] = None  # New secret values
    metadata: Optional[Dict[str, Any]] = None

class UpdateCredentialResponse(BaseModel):
    """Response model for credential updates"""
    model_config = ConfigDict(extra="forbid")
    
    credential: Credential
    updated_at: datetime
    error: Optional[str] = None

class UpdateCredential:
    """Update existing credential details"""
    
    def __init__(self, reposet: RepoSet):
        self.credential_repo = reposet["credential_repository"]
        self.protocol_repo = reposet["protocol_repository"]
        
    def execute(self, credential_id: str, request: UpdateCredentialRequest) -> UpdateCredentialResponse:
        """Update credential with new details"""
        try:
            # Get existing credential
            credential = self.credential_repo.get_credential(credential_id)
            if not credential:
                raise ValueError(f"Credential not found: {credential_id}")
                
            # Get protocol for validation
            protocol = self.protocol_repo.get_protocol(credential.protocol.id)
            if not protocol:
                raise ValueError(f"Protocol not found: {credential.protocol.id}")
                
            # Build update data
            updates = {}
            if request.name:
                updates["name"] = request.name
            if request.metadata:
                updates["metadata"] = request.metadata
                
            # Handle secret updates if provided
            if request.secrets:
                # Validate secrets against protocol requirements
                if not protocol.validate_secrets(request.secrets):
                    raise ValueError("Invalid secrets for protocol")
                    
                # Create new secret collection
                updates["secrets"] = SecretCollection(secrets=request.secrets)
            
            # Update credential
            updated = self.credential_repo.update_credential(
                credential_id=credential_id,
                updates=updates
            )
            
            return UpdateCredentialResponse(
                credential=updated,
                updated_at=datetime.now(UTC)
            )
            
        except Exception as e:
            return UpdateCredentialResponse(
                credential=credential,  # Return original credential
                updated_at=datetime.now(UTC),
                error=str(e)
            )
