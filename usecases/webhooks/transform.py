"""Transform webhook data usecase"""
from typing import Dict, Any, Optional
from datetime import datetime, UTC

from ...domain import Webhook
from ...types import RepoSet

class TransformWebhookData:
    """Convert webhook data to internal format"""
    
    def __init__(self, reposet: RepoSet):
        self.webhook_repo = reposet["webhook_repository"]
        
    def execute(self, webhook_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform webhook payload using configured rules.
        
        Args:
            webhook_id: ID of webhook configuration to use
            payload: The webhook payload to transform
            
        Returns:
            Dict containing transformed data
            
        Raises:
            ValueError: If webhook_id not found
        """
        # Get webhook config
        webhook = self.webhook_repo.get_webhook(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook not found: {webhook_id}")
            
        try:
            # Get transform rules from config
            transform_rules = webhook.config.get("transform_rules", {})
            
            # Initialize result with original payload
            result = payload.copy()
            
            # Apply field mappings
            field_maps = transform_rules.get("field_mappings", {})
            for source, target in field_maps.items():
                if source in payload:
                    result[target] = payload[source]
                    # Remove original field if different name
                    if source != target:
                        result.pop(source, None)
            
            # Apply value transformations
            value_transforms = transform_rules.get("value_transforms", {})
            for field, transform in value_transforms.items():
                if field in result:
                    result[field] = self._transform_value(result[field], transform)
            
            # Add metadata
            result["_metadata"] = {
                "webhook_id": webhook_id,
                "transformed_at": datetime.now(UTC).isoformat(),
                "original_fields": list(payload.keys())
            }
            
            return result
            
        except Exception as e:
            raise ValueError(f"Transform failed: {str(e)}")
    
    def _transform_value(self, value: Any, transform: Dict[str, Any]) -> Any:
        """Apply a value transformation rule"""
        transform_type = transform.get("type")
        
        if transform_type == "string":
            return str(value)
        elif transform_type == "integer":
            return int(float(value))
        elif transform_type == "float":
            return float(value)
        elif transform_type == "boolean":
            return bool(value)
        elif transform_type == "map":
            # Map specific values to others
            mapping = transform.get("mapping", {})
            return mapping.get(str(value), value)
        elif transform_type == "format":
            # Apply string format
            template = transform.get("template", "{}")
            return template.format(value)
            
        return value  # No transform or unknown type
