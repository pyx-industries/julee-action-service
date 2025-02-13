"""Validation rules and related domain concepts"""
from dataclasses import dataclass
from typing import Any, Optional, List, Literal

@dataclass(frozen=True)
class ValidationRule:
    """Definition of a validation rule"""
    rule_type: Literal["required", "type", "pattern", "range", "choices", "custom"]
    value: Any  # The validation constraint (e.g. regex pattern, list of choices, etc)
    message: Optional[str] = None  # Custom error message
    
    def __post_init__(self):
        # Validate rule_type is one of the allowed literals
        valid_types = ["required", "type", "pattern", "range", "choices", "custom"]
        if self.rule_type not in valid_types:
            raise ValueError(f"Invalid rule_type. Must be one of: {valid_types}")

@dataclass(frozen=True)
class ValidationResult:
    """Result of applying validation rules"""
    success: bool
    errors: List[str] = None
    field_name: Optional[str] = None
    rule: Optional[ValidationRule] = None

    def __post_init__(self):
        # Initialize empty list if None
        object.__setattr__(self, 'errors', self.errors or [])
