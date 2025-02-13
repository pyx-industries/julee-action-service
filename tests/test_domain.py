from datetime import datetime
import pytest
from ..domain import (
    Action, Protocol, Connection, ConnectionStatus,
    ProtocolConfig, ProtocolConfigSchema, ActionTemplate,
    Metric, ConfigValue, PropertyDefinition,
    RoutingRule, RoutingConfiguration
)

@pytest.fixture
def sample_action(catalogue):  # Use the catalogue fixture
    """Create a sample action for testing"""
    protocol = catalogue.get_protocol("http")
    return Action(
        id="test-1",
        name="Daily Weather Update",
        description="Fetch weather data every morning",
        action_type=catalogue.get_action_type("poll"),
        protocol=protocol,
        config=ProtocolConfig(
            values=[
                ConfigValue(name="url", value="https://api.weather.com/daily"),
                ConfigValue(name="method", value="GET")
            ],
            schema=ProtocolConfigSchema(
                properties={
                    "url": PropertyDefinition(
                        type="str",
                        description="The endpoint URL",
                        required=True
                    ),
                    "method": PropertyDefinition(
                        type="str",
                        description="HTTP method",
                        default="GET"
                    )
                },
                required=["url"]
            )
        ),
        schedule="0 7 * * *",
        delivery_policy=protocol.default_policy
    )

def test_action_lifecycle(catalogue, sample_action):  # Use fixtures
    """Document core action concepts through tests"""
    # Use the sample action
    action = sample_action
    
    # Get expected types from catalogue
    poll_type = catalogue.get_action_type("poll")
    http_protocol = catalogue.get_protocol("http")
    
    # Test the action properties
    assert action.action_type == poll_type
    assert action.protocol == http_protocol
    assert action.schedule == "0 7 * * *"

def test_connection_states(catalogue):  # Add catalogue here too for consistency
    """Document connection lifecycle and state transitions"""
    conn = Connection(
        id="conn-1",
        protocol=catalogue.get_protocol("kafka"),
        status=catalogue.get_connection_status("active"),
        config={"bootstrap_servers": ["kafka:9092"]},
        metrics=[
            Metric(
                name="messages_processed",
                value=0,
                description="Total messages processed"
            )
        ]
    )
    
    # Get status from catalogue for comparison
    active_status = catalogue.get_connection_status("active")
    error_status = catalogue.get_connection_status("error")
    
    assert conn.status == active_status
    
    # Document state transitions
    conn.status = error_status
    conn.last_error = "Connection refused"
    assert conn.status == error_status

def test_routing_configuration():
    """Test routing configuration functionality"""
    # Create some routing rules
    rule1 = RoutingRule(
        name="high-priority",
        destination="queue-1",
        condition="priority > 5",
        priority=10
    )
    
    rule2 = RoutingRule(
        name="normal",
        destination="queue-2",
        priority=5
    )
    
    fallback = RoutingRule(
        name="fallback",
        destination="dead-letter-queue",
        description="Handle unroutable messages"
    )
    
    # Test routing configuration
    routing = RoutingConfiguration(
        rules=[rule1, rule2],
        strategy="priority",
        fallback=fallback,
        description="Test routing strategy"
    )
    
    assert len(routing.rules) == 2
    assert routing.strategy == "priority"
    assert routing.fallback.destination == "dead-letter-queue"

def test_action_templates():
    """Test action template functionality"""
    template = ActionTemplate(
        content="Hello {{ name }}!",
        description="Basic greeting template"
    )
    
    assert template.content == "Hello {{ name }}!"
    assert template.content_type == "text/jinja2"  # Default value
    assert template.description == "Basic greeting template"
    
    # Test with custom content type
    custom_template = ActionTemplate(
        content="<greeting>Hello {{ name }}!</greeting>",
        content_type="text/xml+jinja2",
        description="XML greeting template"
    )
    assert custom_template.content_type == "text/xml+jinja2"
