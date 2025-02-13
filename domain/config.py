"""Configuration related domain classes."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Literal

@dataclass(frozen=True)
class ConfigValue:
    """A strongly-typed configuration value"""
    name: str
    value: Union[str, int, bool, float]  # Only primitive scalar types
    description: Optional[str] = None

@dataclass(frozen=True)
class ValidationRule:
    """Defines validation rules for configuration values"""
    rule_type: str  # e.g. "min", "max", "pattern", "choices", "range"
    value: Any  # The validation constraint value
    message: Optional[str] = None  # Custom error message

@dataclass(frozen=True)
class PropertyDefinition:
    """Schema definition for a single configuration property"""
    type: Literal["str", "int", "bool", "float"]  # Only allow specific primitive types
    description: Optional[str] = None
    default: Optional[Any] = None
    required: bool = False
    validation_rules: List[ValidationRule] = field(default_factory=list)

@dataclass(frozen=True)
class ProtocolConfigSchema:
    """Schema definition for protocol configuration"""
    properties: Dict[str, PropertyDefinition]
    required: List[str]
    description: Optional[str] = None
    
    def __post_init__(self):
        # Validate that required fields exist in properties
        missing = [field for field in self.required if field not in self.properties]
        if missing:
            raise ValueError(f"Required fields missing from properties: {', '.join(missing)}")
        
        # Validate property definitions
        for field_name, field_def in self.properties.items():
            if not isinstance(field_def, PropertyDefinition):
                raise ValueError(f"Field {field_name} must use PropertyDefinition")

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate a configuration against this schema"""
        # Check required fields
        missing = [field for field in self.required if field not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
            
        # Validate field types
        for field_name, value in config.items():
            if field_name not in self.properties:
                raise ValueError(f"Unknown field: {field_name}")
                
            prop_def = self.properties[field_name]
            expected_type = eval(prop_def.type)  # Safe since type is from Literal
            if not isinstance(value, expected_type):
                raise ValueError(f"Field {field_name} must be of type {prop_def.type}")
            
            # Apply validation rules if any
            for rule in prop_def.validation_rules:
                if not self._validate_rule(value, rule):
                    raise ValueError(
                        rule.message or f"Field {field_name} failed validation rule: {rule.rule_type}"
                    )

    def _validate_rule(self, value: Any, rule: ValidationRule) -> bool:
        """Apply a validation rule to a value"""
        if rule.rule_type == "min":
            return value >= rule.value
        elif rule.rule_type == "max":
            return value <= rule.value
        elif rule.rule_type == "pattern":
            import re
            return bool(re.match(rule.value, str(value)))
        elif rule.rule_type == "choices":
            return value in rule.value
        elif rule.rule_type == "range":
            min_val, max_val = rule.value
            return min_val <= value <= max_val
        return False  # Unknown rule type

__all__ = ['ConfigValue', 'ValidationRule', 'PropertyDefinition', 'ProtocolConfigSchema']
"""Configuration-related domain classes"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Literal

@dataclass(frozen=True)
class ValidationRule:
    """Defines validation rules for configuration values"""
    rule_type: str  # e.g. "min", "max", "pattern", "choices", "range"
    value: Any  # The validation constraint value
    message: Optional[str] = None  # Custom error message

@dataclass(frozen=True)
class ConfigValue:
    """A strongly-typed configuration value"""
    name: str
    value: Union[str, int, bool, float]  # Only primitive scalar types
    description: Optional[str] = None

@dataclass(frozen=True)
class PropertyDefinition:
    """Schema definition for a single configuration property"""
    type: Literal["str", "int", "bool", "float"]  # Only allow specific primitive types
    description: Optional[str] = None
    default: Optional[Any] = None
    required: bool = False
    validation_rules: List[ValidationRule] = field(default_factory=list)

@dataclass(frozen=True)
class ProtocolConfigSchema:
    """Schema definition for protocol configuration"""
    properties: Dict[str, PropertyDefinition]  # Use PropertyDefinition instead of Dict[str, Any]
    required: List[str]  # Required field names
    description: Optional[str] = None
    supported_patterns: List[str] = field(default_factory=lambda: ["single"])  # single, stream, batch
    pattern_config: Dict[str, Dict[str, PropertyDefinition]] = field(default_factory=dict)  # Pattern-specific config
    
    def __post_init__(self):
        # Validate that required fields exist in properties
        missing = [field for field in self.required if field not in self.properties]
        if missing:
            raise ValueError(f"Required fields missing from properties: {', '.join(missing)}")
        
        # Validate property definitions
        for field_name, field_def in self.properties.items():
            if not isinstance(field_def, PropertyDefinition):
                raise ValueError(f"Field {field_name} must use PropertyDefinition")

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate a configuration against this schema"""
        # Check required fields
        missing = [field for field in self.required if field not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
            
        # Validate field types
        for field_name, value in config.items():
            if field_name not in self.properties:
                raise ValueError(f"Unknown field: {field_name}")
                
            prop_def = self.properties[field_name]
            expected_type = eval(prop_def.type)  # Safe since type is from Literal
            if not isinstance(value, expected_type):
                raise ValueError(f"Field {field_name} must be of type {prop_def.type}")
            
            # Apply validation rules if any
            for rule in prop_def.validation_rules:
                if not self._validate_rule(value, rule):
                    raise ValueError(
                        rule.message or f"Field {field_name} failed validation rule: {rule.rule_type}"
                    )

    def _validate_rule(self, value: Any, rule: ValidationRule) -> bool:
        """Apply a validation rule to a value"""
        if rule.rule_type == "min":
            return value >= rule.value
        elif rule.rule_type == "max":
            return value <= rule.value
        elif rule.rule_type == "pattern":
            import re
            return bool(re.match(rule.value, str(value)))
        elif rule.rule_type == "choices":
            return value in rule.value
        elif rule.rule_type == "range":
            min_val, max_val = rule.value
            return min_val <= value <= max_val
        return False  # Unknown rule type

@dataclass(frozen=True)
class ProtocolConfig:
    """Configuration for a protocol instance"""
    values: List[ConfigValue]
    schema: ProtocolConfigSchema

    def __post_init__(self):
        """Validate config against schema on creation"""
        config_dict = {v.name: v.value for v in self.values}
        self.schema.validate_config(config_dict)
"""Configuration-related domain models"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Literal

@dataclass(frozen=True)
class ValidationRule:
    """Defines validation rules for configuration values"""
    rule_type: str  # e.g. "min", "max", "pattern", "choices", "range"
    value: Any  # The validation constraint value
    message: Optional[str] = None  # Custom error message

@dataclass(frozen=True)
class ConfigValue:
    """A strongly-typed configuration value"""
    name: str
    value: Union[str, int, bool, float]  # Only primitive scalar types
    description: Optional[str] = None

@dataclass(frozen=True)
class PropertyDefinition:
    """Schema definition for a single configuration property"""
    type: Literal["str", "int", "bool", "float"]  # Only allow specific primitive types
    description: Optional[str] = None
    default: Optional[Any] = None
    required: bool = False
    validation_rules: List[ValidationRule] = field(default_factory=list)

@dataclass(frozen=True)
class ProtocolConfigSchema:
    """Schema definition for protocol configuration"""
    properties: Dict[str, PropertyDefinition]  # Use PropertyDefinition instead of Dict[str, Any]
    required: List[str]  # Required field names
    description: Optional[str] = None
    
    def __post_init__(self):
        # Validate that required fields exist in properties
        missing = [field for field in self.required if field not in self.properties]
        if missing:
            raise ValueError(f"Required fields missing from properties: {', '.join(missing)}")
        
        # Validate property definitions
        for field_name, field_def in self.properties.items():
            if not isinstance(field_def, PropertyDefinition):
                raise ValueError(f"Field {field_name} must use PropertyDefinition")

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate a configuration against this schema"""
        # Check required fields
        missing = [field for field in self.required if field not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
            
        # Validate field types
        for field_name, value in config.items():
            if field_name not in self.properties:
                raise ValueError(f"Unknown field: {field_name}")
                
            prop_def = self.properties[field_name]
            expected_type = eval(prop_def.type)  # Safe since type is from Literal
            if not isinstance(value, expected_type):
                raise ValueError(f"Field {field_name} must be of type {prop_def.type}")
            
            # Apply validation rules if any
            for rule in prop_def.validation_rules:
                if not self._validate_rule(value, rule):
                    raise ValueError(
                        rule.message or f"Field {field_name} failed validation rule: {rule.rule_type}"
                    )

    def _validate_rule(self, value: Any, rule: ValidationRule) -> bool:
        """Apply a validation rule to a value"""
        if rule.rule_type == "min":
            return value >= rule.value
        elif rule.rule_type == "max":
            return value <= rule.value
        elif rule.rule_type == "pattern":
            import re
            return bool(re.match(rule.value, str(value)))
        elif rule.rule_type == "choices":
            return value in rule.value
        elif rule.rule_type == "range":
            min_val, max_val = rule.value
            return min_val <= value <= max_val
        return False  # Unknown rule type
"""Configuration-related domain models"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Literal

@dataclass(frozen=True)
class ValidationRule:
    """Defines validation rules for configuration values"""
    rule_type: str  # e.g. "min", "max", "pattern", "choices", "range"
    value: Any  # The validation constraint value
    message: Optional[str] = None  # Custom error message

@dataclass(frozen=True)
class ConfigValue:
    """A strongly-typed configuration value"""
    name: str
    value: Union[str, int, bool, float]  # Only primitive scalar types
    description: Optional[str] = None

@dataclass(frozen=True)
class PropertyDefinition:
    """Schema definition for a single configuration property"""
    type: Literal["str", "int", "bool", "float"]  # Only allow specific primitive types
    description: Optional[str] = None
    default: Optional[Any] = None
    required: bool = False
    validation_rules: List[ValidationRule] = field(default_factory=list)

@dataclass(frozen=True)
class ProtocolConfigSchema:
    """Schema definition for protocol configuration"""
    properties: Dict[str, PropertyDefinition]  # Use PropertyDefinition instead of Dict[str, Any]
    required: List[str]  # Required field names
    description: Optional[str] = None
    
    def __post_init__(self):
        # Validate that required fields exist in properties
        missing = [field for field in self.required if field not in self.properties]
        if missing:
            raise ValueError(f"Required fields missing from properties: {', '.join(missing)}")
        
        # Validate property definitions
        for field_name, field_def in self.properties.items():
            if not isinstance(field_def, PropertyDefinition):
                raise ValueError(f"Field {field_name} must use PropertyDefinition")

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate a configuration against this schema"""
        # Check required fields
        missing = [field for field in self.required if field not in config]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
            
        # Validate field types
        for field_name, value in config.items():
            if field_name not in self.properties:
                raise ValueError(f"Unknown field: {field_name}")
                
            prop_def = self.properties[field_name]
            expected_type = eval(prop_def.type)  # Safe since type is from Literal
            if not isinstance(value, expected_type):
                raise ValueError(f"Field {field_name} must be of type {prop_def.type}")
            
            # Apply validation rules if any
            for rule in prop_def.validation_rules:
                if not self._validate_rule(value, rule):
                    raise ValueError(
                        rule.message or f"Field {field_name} failed validation rule: {rule.rule_type}"
                    )

    def _validate_rule(self, value: Any, rule: ValidationRule) -> bool:
        """Apply a validation rule to a value"""
        if rule.rule_type == "min":
            return value >= rule.value
        elif rule.rule_type == "max":
            return value <= rule.value
        elif rule.rule_type == "pattern":
            import re
            return bool(re.match(rule.value, str(value)))
        elif rule.rule_type == "choices":
            return value in rule.value
        elif rule.rule_type == "range":
            min_val, max_val = rule.value
            return min_val <= value <= max_val
        return False  # Unknown rule type
