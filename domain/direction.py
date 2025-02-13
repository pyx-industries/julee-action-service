"""Direction-related domain models"""
from dataclasses import dataclass
from typing import Literal

ActionDirectionType = Literal["efferent", "afferent", "inbound", "outbound"]

@dataclass(frozen=True)
class ActionDirection:
    """Valid action directions"""
    EFFERENT: ActionDirectionType = "efferent"
    OUTBOUND: ActionDirectionType = "outbound"  # Alias for efferent
    AFFERENT: ActionDirectionType = "afferent"
    INBOUND: ActionDirectionType = "inbound"    # Alias for afferent

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate direction including aliases"""
        return value in {cls.EFFERENT, cls.OUTBOUND, cls.AFFERENT, cls.INBOUND}

    @classmethod
    def normalize(cls, value: str) -> str:
        """Convert aliases to canonical values"""
        if value in {cls.OUTBOUND, cls.EFFERENT}:
            return cls.EFFERENT
        elif value in {cls.INBOUND, cls.AFFERENT}:
            return cls.AFFERENT
        raise ValueError(f"Invalid direction: {value}")
"""Direction-related domain models"""
from dataclasses import dataclass
from typing import Literal

ActionDirectionType = Literal["efferent", "afferent", "inbound", "outbound"]

@dataclass(frozen=True)
class ActionDirection:
    """Valid action directions"""
    EFFERENT: ActionDirectionType = "efferent"
    OUTBOUND: ActionDirectionType = "outbound"  # Alias for efferent
    AFFERENT: ActionDirectionType = "afferent"
    INBOUND: ActionDirectionType = "inbound"    # Alias for afferent

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate direction including aliases"""
        return value in {cls.EFFERENT, cls.OUTBOUND, cls.AFFERENT, cls.INBOUND}

    @classmethod
    def normalize(cls, value: str) -> str:
        """Convert aliases to canonical values"""
        if value in {cls.OUTBOUND, cls.EFFERENT}:
            return cls.EFFERENT
        elif value in {cls.INBOUND, cls.AFFERENT}:
            return cls.AFFERENT
        raise ValueError(f"Invalid direction: {value}")
