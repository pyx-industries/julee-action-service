"""Configuration-related enumeration types"""
from dataclasses import dataclass
from typing import Literal

PropertyType = Literal["str", "int", "bool", "float"]

@dataclass(frozen=True)
class PropertyTypes:
    """Valid property types"""
    STRING: PropertyType = "str"
    INTEGER: PropertyType = "int"
    BOOLEAN: PropertyType = "bool"
    FLOAT: PropertyType = "float"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate property type"""
        return value in {cls.STRING, cls.INTEGER, cls.BOOLEAN, cls.FLOAT}
