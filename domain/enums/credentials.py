"""Credential-related enumeration types"""
from dataclasses import dataclass
from typing import Literal

SecretType = Literal["token", "password", "api_key", "private_key", "certificate"]

@dataclass(frozen=True)
class SecretTypes:
    """Valid secret types"""
    TOKEN: SecretType = "token"
    PASSWORD: SecretType = "password"
    API_KEY: SecretType = "api_key"
    PRIVATE_KEY: SecretType = "private_key"
    CERTIFICATE: SecretType = "certificate"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate secret type"""
        return value in {cls.TOKEN, cls.PASSWORD, cls.API_KEY, 
                        cls.PRIVATE_KEY, cls.CERTIFICATE}
