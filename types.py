"""Type definitions used across the Action Service"""
from typing import Dict, Any, Mapping, TypeAlias
from types import MappingProxyType

# Type alias for repository sets - using MappingProxyType for immutability
RepoSet: TypeAlias = MappingProxyType[str, Any]
