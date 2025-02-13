"""Implementation of the behaviour catalogue using hardcoded data"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..interfaces.repositories import BehaviourRepository
from ..domain import (
    ActionType, Protocol, ConnectionStatus,
    PropertyDefinition, ValidationRule,
    DeliverySemantic, DeliveryPolicy
)

# Private hardcoded data - not for direct access!
# This data should only be accessed through the HardcodedBehaviourCatalogue class
# to maintain repository encapsulation and allow for alternative implementations
_ACTION_TYPES = [
    ActionType(
        id="fetch",
        name="Fetch Data",
        description="Retrieve data from external system",
        category="input"
    ),
    ActionType(
        id="publish",
        name="Publish Data",
        description="Send data to external system",
        category="output"
    ),
    ActionType(
        id="poll",
        name="Poll for Changes",
        description="Regularly check for updates",
        category="input"
    ),
    ActionType(
        id="subscribe",
        name="Subscribe to Updates",
        description="Listen for pushed updates",
        category="input"
    )
]

# Define delivery semantics
_AT_LEAST_ONCE = DeliverySemantic(
    id="at_least_once",
    name="At Least Once", 
    description="Message will be delivered one or more times",
    requires_ack=True,
    allows_retry=True,
    preserves_order=False,
    requires_dedup=False
)

_STREAMING = DeliverySemantic(
    id="streaming",
    name="Streaming",
    description="Continuous stream of messages with backpressure",
    requires_ack=True,
    allows_retry=False,
    preserves_order=True,
    requires_dedup=False
)

_BATCH = DeliverySemantic(
    id="batch",
    name="Batch Processing",
    description="Grouped message delivery with all-or-nothing semantics",
    requires_ack=True,
    allows_retry=True,
    preserves_order=True,
    requires_dedup=True
)

_EXACTLY_ONCE = DeliverySemantic(
    id="exactly_once",
    name="Exactly Once",
    description="Message will be delivered exactly once",
    requires_ack=True,
    allows_retry=True,
    preserves_order=True,
    requires_dedup=True
)

# Define default policies
_DEFAULT_HTTP_POLICY = DeliveryPolicy(
    semantic=_AT_LEAST_ONCE,
    max_retries=3,
    retry_delay=timedelta(seconds=30)
)

_DEFAULT_EMAIL_POLICY = DeliveryPolicy(
    semantic=_AT_LEAST_ONCE,
    max_retries=5,
    retry_delay=timedelta(minutes=5)
)

_DEFAULT_GITHUB_POLICY = DeliveryPolicy(
    semantic=_EXACTLY_ONCE,
    max_retries=3,
    retry_delay=timedelta(minutes=1)
)

_DEFAULT_KAFKA_POLICY = DeliveryPolicy(
    semantic=_AT_LEAST_ONCE,
    max_retries=None,  # Unlimited retries
    retry_delay=timedelta(seconds=10)
)

_PROTOCOLS = [
    Protocol(
        id="http",
        name="HTTP/REST",
        description="HTTP-based REST APIs",
        category="web",
        handler_class="action_service.protocols.http.HttpProtocol",
        supported_semantics=[_AT_LEAST_ONCE],
        default_policy=_DEFAULT_HTTP_POLICY
    ),
    Protocol(
        id="smtp",
        name="Email (SMTP)", 
        description="Send emails via SMTP",
        category="email",
        handler_class="action_service.protocols.email.SmtpProtocol",
        supported_semantics=[_AT_LEAST_ONCE],
        default_policy=_DEFAULT_EMAIL_POLICY
    ),
    Protocol(
        id="github",
        name="GitHub",
        description="GitHub Issues and PRs",
        category="development",
        handler_class="action_service.protocols.github.GithubProtocol",
        supported_semantics=[_EXACTLY_ONCE],
        default_policy=_DEFAULT_GITHUB_POLICY
    ),
    Protocol(
        id="kafka",
        name="Apache Kafka",
        description="Kafka message streams",
        category="messaging",
        handler_class="action_service.protocols.kafka.KafkaProtocol",
        supported_semantics=[_AT_LEAST_ONCE],
        default_policy=_DEFAULT_KAFKA_POLICY
    )
]

_CONNECTION_STATUSES = [
    ConnectionStatus(
        id="active",
        name="Active",
        description="Connection is active and healthy",
        can_retry=False,
        severity=0
    ),
    ConnectionStatus(
        id="disconnected",
        name="Disconnected",
        description="Connection is currently down",
        can_retry=True,
        severity=1
    ),
    ConnectionStatus(
        id="error",
        name="Error",
        description="Connection encountered an error",
        can_retry=True,
        severity=2
    ),
    ConnectionStatus(
        id="disabled",
        name="Disabled",
        description="Connection is administratively disabled",
        can_retry=False,
        severity=0
    )
]

class HardcodedBehaviourCatalogue(BehaviourRepository):
    """Provides access to hardcoded behaviour definitions"""
    
    def get_action_types(self) -> List[ActionType]:
        return _ACTION_TYPES
        
    def get_action_type(self, type_id: str) -> Optional[ActionType]:
        return next((t for t in _ACTION_TYPES if t.id == type_id), None)
        
    def get_protocols(self) -> List[Protocol]:
        return _PROTOCOLS
        
    def get_protocol(self, protocol_id: str) -> Optional[Protocol]:
        return next((p for p in _PROTOCOLS if p.id == protocol_id), None)
        
    def get_connection_statuses(self) -> List[ConnectionStatus]:
        return _CONNECTION_STATUSES
        
    def get_connection_status(self, status_id: str) -> Optional[ConnectionStatus]:
        return next((s for s in _CONNECTION_STATUSES if s.id == status_id), None)

    def get_delivery_semantics(self) -> List[DeliverySemantic]:
        """Get all supported delivery semantics"""
        return [_AT_LEAST_ONCE, _EXACTLY_ONCE]
    
    def get_delivery_semantic(self, semantic_id: str) -> Optional[DeliverySemantic]:
        """Get delivery semantic by ID"""
        semantics = {
            "at_least_once": _AT_LEAST_ONCE,
            "exactly_once": _EXACTLY_ONCE
        }
        return semantics.get(semantic_id)

    def get_protocol_handler(self, protocol: Protocol, config: Dict[str, Any]) -> Any:
        """Get configured protocol handler instance"""
        # Import the handler class dynamically
        module_path, class_name = protocol.handler_class.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        handler_class = getattr(module, class_name)
        
        # Create and return handler instance
        return handler_class(config)

    def get_protocol_config_schema(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration schema for a protocol"""
        protocol = self.get_protocol(protocol_id)
        if not protocol:
            return None
            
        # Return basic schema for now - could be enhanced to load from protocol handlers
        if protocol_id == "http":
            return {
                "url": PropertyDefinition(
                    type="str",
                    description="The endpoint URL",
                    required=True,
                    validation_rules=[
                        ValidationRule(
                            rule_type="pattern",
                            value=r"^https?://.*",
                            message="URL must start with http:// or https://"
                        )
                    ]
                ),
                "method": PropertyDefinition(
                    type="str",
                    description="HTTP method to use",
                    default="GET",
                    validation_rules=[
                        ValidationRule(
                            rule_type="choices",
                            value=["GET", "POST", "PUT", "DELETE"]
                        )
                    ]
                ),
                "headers": PropertyDefinition(
                    type="dict",
                    description="HTTP headers",
                    default={}
                )
            }
        return None

    def validate_protocol_config(self, protocol_id: str, config: Dict[str, Any]) -> bool:
        """Validate protocol configuration against schema"""
        schema = self.get_protocol_config_schema(protocol_id)
        if not schema:
            return False  # Invalid protocol ID
            
        # Check all required fields are present
        for field_name, field_def in schema.items():
            if isinstance(field_def, PropertyDefinition):
                if field_def.required and field_name not in config:
                    return False
                
                # If field is present, validate it
                if field_name in config:
                    field_value = config[field_name]
                    
                    # Check validation rules if they exist
                    if hasattr(field_def, 'validation_rules'):
                        for rule in field_def.validation_rules:
                            if rule.rule_type == "pattern":
                                import re
                                if not re.match(rule.value, str(field_value)):
                                    return False
                            elif rule.rule_type == "choices":
                                if field_value not in rule.value:
                                    return False
                    
        return True
