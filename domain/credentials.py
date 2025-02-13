"""Credential-related domain models"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Dict, Optional, Literal
from .protocols import Protocol

@dataclass(frozen=True)
class Secret:
    """A single secret value with metadata"""
    key: str
    value: str  # Always encrypted at rest
    type: Literal["token", "password", "api_key", "private_key", "certificate"]
    description: Optional[str] = None
    expires_at: Optional[datetime] = None

    def __str__(self) -> str:
        """Prevent accidental secret exposure in logs/output"""
        return f"Secret(key='{self.key}', type='{self.type}')"

    def __repr__(self) -> str:
        """Prevent accidental secret exposure in logs/output"""
        return self.__str__()

@dataclass(frozen=True)
class SecretCollection:
    """A validated collection of secrets"""
    secrets: Dict[str, Secret]
    
    def __post_init__(self):
        # Validate secret names match their keys
        for key, secret in self.secrets.items():
            if key != secret.key:
                raise ValueError(f"Secret key mismatch: {key} != {secret.key}")

    def get_secret(self, key: str) -> Optional[Secret]:
        """Safely access a secret by key"""
        return self.secrets.get(key)

    def __str__(self) -> str:
        """Safe string representation"""
        return f"SecretCollection(keys={list(self.secrets.keys())})"

@dataclass(frozen=True)
class Credential:
    """Authentication details for external services"""
    id: str
    name: str
    protocol: Protocol
    secrets: SecretCollection
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get_secret(self, key: str) -> Optional[Secret]:
        """Safely access a secret"""
        return self.secrets.get_secret(key)
