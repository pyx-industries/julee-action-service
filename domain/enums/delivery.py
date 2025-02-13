"""Delivery-related enumeration types"""
from dataclasses import dataclass
from typing import Literal

DeliveryPatternType = Literal["push", "pull", "batch", "stream"]

@dataclass(frozen=True)
class DeliveryPatternTypes:
    """Valid delivery pattern types"""
    PUSH: DeliveryPatternType = "push"
    PULL: DeliveryPatternType = "pull"
    BATCH: DeliveryPatternType = "batch"
    STREAM: DeliveryPatternType = "stream"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate delivery pattern type"""
        return value in {cls.PUSH, cls.PULL, cls.BATCH, cls.STREAM}
