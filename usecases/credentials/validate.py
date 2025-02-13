"""Credential validation usecase"""
from typing import Optional
from datetime import datetime

from ...domain import Credential
from ...types import RepoSet

class ValidateCredential:
    """Test if stored credentials are valid"""
    
    def __init__(self, reposet: RepoSet):
        self.credential_repo = reposet["credential_repository"]
        self.protocol_repo = reposet["protocol_repository"]
        
    def execute(self, credential_id: str) -> bool:
        """
        Validate stored credentials against their protocol.
        
        Args:
            credential_id: ID of credentials to validate
            
        Returns:
            bool: True if credentials are valid, False otherwise
            
        Raises:
            ValueError: If credential_id is not found
        """
        # Get credential
        credential = self.credential_repo.get_credential(credential_id)
        if not credential:
            raise ValueError(f"Credential not found: {credential_id}")
            
        # Get protocol handler
        protocol = self.protocol_repo.get_protocol(credential.protocol.id)
        if not protocol:
            raise ValueError(f"Protocol not found: {credential.protocol.id}")
            
        try:
            # Get protocol handler
            handler = self.protocol_repo.get_protocol_handler(protocol)
            
            # Attempt validation
            return handler.validate_credentials(credential)
            
        except Exception:
            return False
