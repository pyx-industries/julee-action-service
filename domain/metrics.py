"""Metric-related domain models"""
from dataclasses import dataclass
from typing import Union, Optional

@dataclass(frozen=True)
class Metric:
    """A single named value with optional description"""
    name: str
    value: Union[str, int, float, bool]
    description: Optional[str] = None
