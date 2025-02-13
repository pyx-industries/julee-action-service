import pytest
from ..repositories.behaviour import HardcodedBehaviourCatalogue

@pytest.fixture
def catalogue():
    return HardcodedBehaviourCatalogue()

def test_action_types(catalogue):
    """Test action type retrieval"""
    types = catalogue.get_action_types()
    assert len(types) > 0
    
    # Test specific type lookup
    fetch = catalogue.get_action_type("fetch")
    assert fetch is not None
    assert fetch.name == "Fetch Data"
    assert fetch.category == "input"
    
    # Test nonexistent type
    assert catalogue.get_action_type("nonexistent") is None

def test_protocols(catalogue):
    """Test protocol retrieval"""
    protocols = catalogue.get_protocols()
    assert len(protocols) > 0
    
    # Test specific protocol lookup
    http = catalogue.get_protocol("http")
    assert http is not None
    assert http.name == "HTTP/REST"
    assert "HttpProtocol" in http.handler_class
    
    # Test nonexistent protocol
    assert catalogue.get_protocol("nonexistent") is None

def test_connection_statuses(catalogue):
    """Test connection status retrieval"""
    statuses = catalogue.get_connection_statuses()
    assert len(statuses) > 0
    
    # Test specific status lookup
    active = catalogue.get_connection_status("active")
    assert active is not None
    assert active.name == "Active"
    assert active.severity == 0
    
    # Test nonexistent status
    assert catalogue.get_connection_status("nonexistent") is None

def test_protocol_config_schema(catalogue):
    """Test protocol configuration schema retrieval"""
    # Test getting schema for HTTP protocol
    http_schema = catalogue.get_protocol_config_schema("http")
    assert http_schema is not None
    assert "url" in http_schema  # Basic HTTP config should have URL field
    
    # Test nonexistent protocol
    assert catalogue.get_protocol_config_schema("nonexistent") is None
