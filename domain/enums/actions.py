"""Action-related enumeration types"""
from dataclasses import dataclass
from typing import Literal

ActionPatternType = Literal["single", "stream", "batch"]
ActionDirectionType = Literal["efferent", "afferent"]

@dataclass(frozen=True)
class ActionPattern:
    """Valid action patterns"""
    SINGLE: ActionPatternType = "single"
    STREAM: ActionPatternType = "stream"
    BATCH: ActionPatternType = "batch"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate action pattern"""
        return value in {cls.SINGLE, cls.STREAM, cls.BATCH}

@dataclass(frozen=True)
class ActionDirection:
    """Valid action directions"""
    EFFERENT: ActionDirectionType = "efferent"
    AFFERENT: ActionDirectionType = "afferent"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate action direction"""
        return value in {cls.EFFERENT, cls.AFFERENT}
