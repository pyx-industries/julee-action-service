# Creating New Protocols: A Chicken Protection System Example

## Understanding Protocols and Actions

The Action Service enables agents (such as Julee) to interact with the physical world through well-defined protocols and actions. This guide demonstrates protocol development using a practical example: protecting robot-managed chickens from predator threats.

### System Overview

This example implements two complementary protocols that form a complete sense-and-respond system:

**Fox Detection Protocol (Sensory/Afferent)**
- Receives webhook notifications from sentry cameras
- Validates and processes detection reports
- Routes verified threats for assessment

**Chicken Defense Protocol (Motor/Efferent)**
- Receives threat coordinates and assessment
- Controls defensive systems (hypersonic mud-flinger)
- Reports defense outcomes and chicken safety status

These protocols remain independent and reusable:
- The Fox Detection Protocol could trigger other responses (lights, alarms)
- The Chicken Defense Protocol could respond to other threats (hawks, raccoons)

### Protocol Developer Tasks

To implement new protocols, developers must:
1. Define integration patterns with external systems
2. Implement connection handling and data validation
3. Create reusable configuration schemas
4. Ensure reliable and maintainable implementations

This guide walks through creating both protocols, demonstrating:
- Protocol separation and independence
- Clear responsibility boundaries
- Reusable configuration patterns
- Robust error handling
- Comprehensive testing approaches

---

## Implementation Overview

The chicken protection system requires:
1. Processing detection events from sentry cameras
2. Validating and assessing threat levels
3. Coordinating defensive responses
4. Monitoring system effectiveness

This two-protocol design provides:
- Clear separation of concerns
- Independent scaling and maintenance
- Flexible response options
- Comprehensive monitoring

## Step 1: Define Protocol Configuration

First, create a configuration schema that defines what information your protocol needs:

```python
from action_service.domain import (
    PropertyDefinition, ValidationRule, ProtocolConfigSchema
)

FOX_DETECTION_SCHEMA = ProtocolConfigSchema(
    properties={
        "endpoint_url": PropertyDefinition(
            type="str", 
            description="URL to receive detection webhooks",
            required=True,
            validation_rules=[
                ValidationRule(
                    rule_type="pattern",
                    value=r"^https?://[\w\-\.]+(:\d+)?(/[\w\-/]*)?$",
                    message="Must be a valid HTTP/HTTPS URL"
                )
            ]
        ),
        "auth_token": PropertyDefinition(
            type="str",
            description="Bearer token for webhook authentication",
            required=True
        ),
        "verify_ssl": PropertyDefinition(
            type="bool",
            description="Whether to verify SSL certificates",
            default=True
        ),
        "threat_threshold": PropertyDefinition(
            type="float",
            description="Minimum confidence score to consider as threat",
            default=0.85,
            validation_rules=[
                ValidationRule(
                    rule_type="range",
                    value=(0.0, 1.0),
                    message="Threshold must be between 0 and 1"
                )
            ]
        )
    },
    required=["endpoint_url", "auth_token"],
    description="Configuration for fox detection webhooks"
)
```

## Step 2: Create Protocol Handler

Create a new file `action_service/protocols/fox_detection/protocol.py`:

```python
from typing import Dict, Any, Optional
import json
from ...pdk import ProtocolHandler
from ...domain import Action, ActionResult

class FoxDetectionProtocol(ProtocolHandler):
    """Handler for fox detection events from sentry cameras"""
    
    def validate_config(self) -> bool:
        try:
            required = ['endpoint_url', 'auth_token']
            if not all(key in self.config for key in required):
                self.last_error = f"Missing required config: {required}"
                return False
                
            # Validate threat threshold
            threshold = float(self.config.get('threat_threshold', 0.85))
            if not 0 <= threshold <= 1:
                self.last_error = "Threat threshold must be between 0 and 1" 
                return False
                
            return True
            
        except Exception as e:
            self.last_error = str(e)
            return False
            
    def test_connection(self) -> bool:
        """Test endpoint connection"""
        try:
            import httpx
            response = httpx.get(
                f"{self.config['endpoint_url']}/health",
                headers={"Authorization": f"Bearer {self.config['auth_token']}"}
            )
            return response.status_code == 200
            
        except Exception as e:
            self.last_error = f"Connection failed: {str(e)}"
            return False
            
    def execute(self, action: Action) -> ActionResult:
        """Process fox detection events"""
        try:
            import httpx
            
            # Get detection events from webhook endpoint
            response = httpx.post(
                self.config['endpoint_url'],
                headers={
                    "Authorization": f"Bearer {self.config['auth_token']}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise ValueError(f"API returned {response.status_code}")
                
            events = response.json()
            
            # Filter by threat threshold
            detection_events = [
                event for event in events
                if event['confidence'] >= self.config.get('threat_threshold', 0.85)
            ]
                        
            return ActionResult(
                action_id=action.id,
                request_id=str(uuid.uuid4()),
                success=True,
                result={
                    'events': detection_events,
                    'count': len(detection_events)
                }
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action.id,
                request_id=str(uuid.uuid4()),
                success=False,
                error=str(e)
            )
```

## Step 3: Register the Protocol

Add the protocol definition to `action_service/repositories/behaviour.py`:

```python
_PROTOCOLS.append(
    Protocol(
        id="fox_detection",
        name="Fox Detection Monitor",
        description="Monitor fox detection events from sentry cameras",
        category="security",
        handler_class="action_service.protocols.fox_detection.protocol.FoxDetectionProtocol"
    )
)
```

## Step 4: Create Action Configuration

Configure an action that uses your protocol:

```python
action = Action(
    id="protect-chickens-1",
    name="Monitor Fox Threats",
    description="Monitor sentry cameras for fox intrusions",
    action_type=catalogue.get_action_type("poll"),
    protocol=catalogue.get_protocol("fox_detection"),
    config=[
        ConfigValue(
            name="endpoint_url",
            value="https://sentry-api.example.com/detections"
        ),
        ConfigValue(
            name="auth_token",
            value="sk_test_123..."
        ),
        ConfigValue(
            name="threat_threshold",
            value=0.90
        )
    ],
    schedule="*/1 * * * *"  # Check every minute
)
```

## Step 5: Add Tests

Create `action_service/tests/test_fox_detection.py`:

```python
import pytest
from unittest.mock import Mock, patch
from ..protocols.fox_detection.protocol import FoxDetectionProtocol

def test_fox_detection_config_validation():
    """Test configuration validation"""
    valid_config = {
        "kafka_bootstrap_servers": "kafka:9092",
        "topic": "sentry.fox.detections",
        "group_id": "test-group",
        "threat_threshold": 0.9
    }
    
    protocol = FoxDetectionProtocol(valid_config)
    assert protocol.validate_config() == True
    
    # Test invalid config
    invalid_config = {
        "topic": "sentry.fox.detections"  # Missing required fields
    }
    protocol = FoxDetectionProtocol(invalid_config)
    assert protocol.validate_config() == False
    assert "Missing required config" in protocol.last_error

@pytest.mark.integration
def test_fox_detection_kafka_integration():
    """Integration test with Kafka"""
    protocol = FoxDetectionProtocol({
        "kafka_bootstrap_servers": "kafka:9092",
        "topic": "sentry.fox.detections",
        "group_id": "test-group"
    })
    
    # Should connect successfully
    assert protocol.test_connection() == True
```

## Step 6: Deployment

1. Install Dependencies:
   ```bash
   pip install httpx
   ```

2. Configure API Access:
   - Ensure the sentry API endpoint is accessible
   - Configure authentication token
   - Set up SSL certificates if needed

3. Deploy Action Configuration:
   ```python
   # Using the action service API
   from action_service.client import ActionServiceClient
   
   client = ActionServiceClient()
   client.create_action(action)
   ```

## Step 7: Integration with Julee

1. Configure the action's output transformation to match Julee's target designation format:
   ```python
   action.output_transform = TransformRule(
       name="prepare-target",
       transform_type="map",
       config={
           "template": {
               "target_type": "fox",
               "confidence": "{{ event.confidence }}",
               "coordinates": "{{ event.location }}",
               "visual_reference": "{{ event.image_url }}",
               "priority": "high",
               "response_type": "mud_flinger"
           }
       }
   )
   ```

2. Set up a routing rule to send verified threats to Julee:
   ```python
   action.routing = RoutingConfiguration(
       rules=[
           RoutingRule(
               name="high-threat",
               destination="julee.target.designation",
               condition="event.confidence >= 0.95",
               priority=10
           ),
           RoutingRule(
               name="medium-threat",
               destination="julee.target.review",
               condition="event.confidence >= 0.90",
               priority=5
           )
       ],
       strategy="first-match",
       fallback=RoutingRule(
           name="low-threat",
           destination="julee.monitoring.log"
       )
   )
   ```

## Testing Your Deployment

1. Verify Kafka Connection:
   ```bash
   # Test producing a detection event
   kafka-console-producer.sh --broker-list kafka:9092 --topic sentry.fox.detections
   ```

2. Monitor Action Execution:
   ```python
   # Check action results
   results = client.get_action_results("protect-chickens-1")
   print(f"Processed {len(results)} detection events")
   ```

3. Verify Julee Integration:
   - Check Julee's target designation pipeline
   - Confirm mud-flinger activation on high-threat events
   - Review response effectiveness metrics

## Maintenance Considerations

1. Monitor API health:
   - Check response times
   - Monitor error rates
   - Set up alerts for API outages

2. Tune Configuration:
   - Adjust threat threshold based on false positive rates
   - Optimize polling frequency
   - Fine-tune routing rules

3. Regular Testing:
   - Conduct periodic end-to-end tests
   - Validate mud-flinger response time
   - Update threat detection models

Your chicken protection system is now ready to detect and respond to fox threats automatically!
