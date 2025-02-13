"""Event-related enumeration types"""
from dataclasses import dataclass
from typing import Literal

DirectionType = Literal["incoming", "outgoing"]

@dataclass(frozen=True)
class Direction:
    """Message direction types"""
    INCOMING: DirectionType = "incoming"
    OUTGOING: DirectionType = "outgoing"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate direction type"""
        return value in {cls.INCOMING, cls.OUTGOING}
