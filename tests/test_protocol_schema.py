import pytest
from ..domain import ProtocolConfigSchema, PropertyDefinition

def test_protocol_config_schema_creation():
    """Test creating valid protocol config schemas"""
    # Valid schema
    schema = ProtocolConfigSchema(
        properties={
            'url': PropertyDefinition(type="str", description="Target URL"),
            'method': PropertyDefinition(type="str", description="HTTP method"),
            'headers': PropertyDefinition(type="dict", description="HTTP headers")
        },
        required=['url'],
        description='Test schema'
    )
    assert schema.description == 'Test schema'
    assert 'url' in schema.required
    
    # Schema with missing required field
    with pytest.raises(ValueError) as exc:
        ProtocolConfigSchema(
            properties={
                'method': PropertyDefinition(type="str")
            },
            required=['url'],  # url not in properties
            description='Invalid schema'
        )
    assert "Required fields missing from properties" in str(exc.value)
    
    # Schema with invalid property definition
    with pytest.raises(ValueError) as exc:
        ProtocolConfigSchema(
            properties={
                'url': {'description': 'Missing type'}  # Not a PropertyDefinition
            },
            required=['url'],
            description='Invalid schema'
        )
    assert "Field url must use PropertyDefinition" in str(exc.value)

def test_protocol_config_validation():
    """Test validating configs against schema"""
    schema = ProtocolConfigSchema(
        properties={
            'url': PropertyDefinition(type="str"),
            'method': PropertyDefinition(type="str"), 
            'timeout': PropertyDefinition(type="int")
        },
        required=['url']
    )
    
    # Valid config
    schema.validate_config({
        'url': 'http://test.com',
        'method': 'GET',
        'timeout': 30
    })
    
    # Missing required field
    with pytest.raises(ValueError) as exc:
        schema.validate_config({'method': 'GET'})
    assert "Missing required fields" in str(exc.value)
    
    # Invalid type
    with pytest.raises(ValueError) as exc:
        schema.validate_config({
            'url': 'http://test.com',
            'timeout': '30'  # Should be int
        })
    assert "must be of type" in str(exc.value)
    
    # Unknown field
    with pytest.raises(ValueError) as exc:
        schema.validate_config({
            'url': 'http://test.com',
            'invalid': 'value'
        })
    assert "Unknown field" in str(exc.value)
