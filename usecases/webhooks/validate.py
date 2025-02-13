"""Webhook payload validation usecase"""
from typing import Dict, Any, Optional
from datetime import datetime, UTC

from ...domain import Webhook
from ...types import RepoSet

class ValidateWebhookPayload:
    """Verify incoming webhook data"""
    
    def __init__(self, reposet: RepoSet):
        self.webhook_repo = reposet["webhook_repository"]
        
    def execute(self, webhook_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate webhook payload against configured rules.
        
        Args:
            webhook_id: ID of webhook configuration to use
            payload: The webhook payload to validate
            
        Returns:
            Dict containing validation results
            
        Raises:
            ValueError: If webhook_id not found
        """
        # Get webhook config
        webhook = self.webhook_repo.get_webhook(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook not found: {webhook_id}")
            
        validation_results = {
            "valid": True,
            "timestamp": datetime.now(UTC),
            "errors": []
        }
        
        try:
            # Check required fields
            required_fields = webhook.config.get("required_fields", [])
            for field in required_fields:
                if field not in payload:
                    validation_results["errors"].append(f"Missing required field: {field}")
            
            # Check field types
            field_types = webhook.config.get("field_types", {})
            for field, expected_type in field_types.items():
                if field in payload:
                    actual_value = payload[field]
                    if not self._validate_type(actual_value, expected_type):
                        validation_results["errors"].append(
                            f"Invalid type for {field}: expected {expected_type}"
                        )
            
            # Check custom validation rules
            validation_rules = webhook.config.get("validation_rules", [])
            for rule in validation_rules:
                if not self._evaluate_rule(rule, payload):
                    validation_results["errors"].append(f"Failed validation rule: {rule}")
                    
            # Update valid flag based on errors
            validation_results["valid"] = len(validation_results["errors"]) == 0
            
            return validation_results
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
            return validation_results
            
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value matches expected type"""
        try:
            if expected_type == "str":
                return isinstance(value, str)
            elif expected_type == "int":
                return isinstance(value, int)
            elif expected_type == "float":
                return isinstance(value, (int, float))
            elif expected_type == "bool":
                return isinstance(value, bool)
            elif expected_type == "list":
                return isinstance(value, list)
            elif expected_type == "dict":
                return isinstance(value, dict)
            return False
        except Exception:
            return False
            
    def _evaluate_rule(self, rule: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """Evaluate a custom validation rule"""
        try:
            rule_type = rule.get("type")
            field = rule.get("field")
            value = rule.get("value")
            
            if not all([rule_type, field, value]):
                return False
                
            if field not in payload:
                return False
                
            actual = payload[field]
            
            if rule_type == "equals":
                return actual == value
            elif rule_type == "not_equals":
                return actual != value
            elif rule_type == "greater_than":
                return actual > value
            elif rule_type == "less_than":
                return actual < value
            elif rule_type == "in_list":
                return actual in value
            elif rule_type == "not_in_list":
                return actual not in value
            
            return False
            
        except Exception:
            return False
