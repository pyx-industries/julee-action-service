from typing import Any, Optional
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pytest
from pydantic import ValidationError
from ..interfaces.requests import (
    ExecuteActionRequest, ActionCallbackRequest,
    ActionAcceptedResponse, ActionStatusResponse
)
from ..domain import Action, ActionType, Protocol, ActionResult
from ..types import RepoSet
from ..usecases.execute import ExecuteAction

class MockCredentialRepo:
    """Test double demonstrating credential repository contract"""
    def get_credential(self, credential_id: str):
        return None

class MockActionRepo:
    """Test double demonstrating action repository contract"""
    def __init__(self):
        self.actions = {}  # Store actions by ID
        
    def add_action(self, action: Action):
        """Helper method to add test actions"""
        self.actions[action.id] = action
        
    def get_action(self, action_id: str) -> Optional[Action]:
        return self.actions.get(action_id)
        
    def execute(self, action: Action) -> dict:
        return {
            'status': 200,
            'data': {
                'message': 'Mock successful response'
            }
        }

class MockEventRepo:
    """Test double demonstrating event repository contract"""
    def record_success(self, action_id: str, result: Any):
        pass
    
    def record_failure(self, action_id: str, error: str):
        pass

def test_execute_action_success(catalogue):  # Add catalogue parameter
    """Document successful action execution flow"""
    # Arrange
    protocol = catalogue.get_protocol("http")
    action = Action(
        id="test-1",
        name="Test Action",
        description="Test action for unit tests",
        action_type=catalogue.get_action_type("fetch"),  # Use catalogue
        protocol=protocol,  # Use catalogue
        config={
            "url": "https://test.example.com/api",
            "method": "GET"
        },
        delivery_policy=protocol.default_policy
    )

    # Create mock repositories using RepoSet
    mock_action_repo = MockActionRepo()
    mock_action_repo.add_action(action)  # Store action in mock repo
    
    mock_repos = RepoSet({
        'action_repository': mock_action_repo,
        'event_repository': MockEventRepo(),
        'behaviour_repository': catalogue,
        'credential_repository': MockCredentialRepo()
    })

    # Create request object
    request = ExecuteActionRequest(
        action_id=action.id,
        correlation_id="test-corr-1",
        content={"test": "data"}
    )

    # Act
    usecase = ExecuteAction(mock_repos)
    result = usecase.execute(request)

    # Assert
    assert result.status == "completed"
    assert result.request_id == action.id

def test_execute_action_failure(catalogue):  # Add catalogue parameter
    """Document error handling in action execution"""
    protocol = catalogue.get_protocol("http")
    action = Action(
        id="test-2", 
        name="Failing Action",
        description="Test action that fails",
        action_type=catalogue.get_action_type("fetch"),  # Use catalogue
        protocol=protocol,  # Use catalogue
        config={
            "url": "https://test.example.com/api",
            "method": "GET"
        },
        delivery_policy=protocol.default_policy
    )

    # Mock repository that raises error
    class FailingRepo(MockActionRepo):
        def execute(self, action):
            raise ConnectionError("Failed to connect")

    # Create mock repositories using RepoSet
    failing_repo = FailingRepo()
    failing_repo.add_action(action)  # Store action in mock repo
    
    mock_repos = RepoSet({
        'action_repository': failing_repo,
        'event_repository': MockEventRepo(),
        'behaviour_repository': catalogue,
        'credential_repository': MockCredentialRepo()
    })

    # Create request object
    request = ExecuteActionRequest(
        action_id=action.id,
        correlation_id="test-corr-2",
        content={"test": "data"}
    )

    usecase = ExecuteAction(mock_repos)
    result = usecase.execute(request)

    assert result.status == "failed"
    assert "Failed to connect" in result.error

def test_afferent_message_processing():
    """Test complete inbound message processing flow"""
    request = ActionCallbackRequest(
        protocol_id="http",
        action_type_id="fetch",
        payload={"detected_threat": "fox", "confidence": 0.95},
        metadata={"camera_id": "CAM-001", "timestamp": "2024-01-01T10:00:00Z"}
    )
    
    # Test message state transitions
    assert request.protocol_id == "http"
    assert request.payload["confidence"] > 0.90  # Critical threat

def test_message_validation_rules():
    """Test message validation and categorization"""
    # Test valid high-priority message
    with pytest.raises(ValidationError):
        ActionCallbackRequest(
            protocol_id="http",
            action_type_id="fetch",
            payload={"detected_threat": "fox", "confidence": 1.5},  # Invalid confidence
            metadata={"camera_id": "CAM-001"}
        )

def test_delivery_semantics():
    """Test different delivery semantic implementations"""
    # Test at-most-once delivery
    request = ExecuteActionRequest(
        action_id="sensor-1",
        content={"temperature": 22.5},
        correlation_id="temp-reading-1",
        priority=1,
        deadline=None  # No strict deadline for sensor readings
    )
    
    # Test at-least-once delivery
    critical_request = ExecuteActionRequest(
        action_id="alert-1", 
        content={"alert": "Security breach"},
        correlation_id="alert-001",
        priority=9,
        deadline=datetime.now() + timedelta(minutes=5),
        idempotency_key="alert-001-retry-0"  # For deduplication
    )

def test_message_expiry():
    """Test message expiry handling"""
    # Test expired message
    expired_request = ExecuteActionRequest(
        action_id="test-1",
        content={"data": "test"},
        correlation_id="corr-1",
        deadline=datetime.now() - timedelta(minutes=5)  # Already expired
    )
    
    # Test near-expiry message
    urgent_request = ExecuteActionRequest(
        action_id="test-2",
        content={"data": "urgent"},
        correlation_id="corr-2",
        deadline=datetime.now() + timedelta(seconds=30)  # Almost expired
    )

def test_action_execution_response():
    """Test action execution response handling"""
    # Test successful execution
    response = ActionAcceptedResponse(
        request_id="req-001",
        estimated_completion=datetime.now() + timedelta(minutes=1)
    )
    assert response.status == "accepted"
    
    # Test status updates
    status = ActionStatusResponse(
        request_id="req-001",
        correlation_id="corr-001",
        status="completed",
        completion_time=datetime.now(),
        result={"action": "completed", "details": "Success"}
    )
    assert status.status == "completed"

def test_action_failure_handling():
    """Test action failure scenarios"""
    # Test temporary failure
    temp_failure = ActionStatusResponse(
        request_id="req-002",
        correlation_id="corr-002",
        status="failed",
        error="Temporary connection error"
    )
    assert temp_failure.status == "failed"
    
    # Test permanent failure
    perm_failure = ActionStatusResponse(
        request_id="req-003",
        correlation_id="corr-003",
        status="failed",
        error="Invalid configuration",
        completion_time=datetime.now()
    )
    assert perm_failure.error is not None

def test_action_priority_handling():
    """Test priority-based action handling"""
    # Test high priority action
    high_priority = ExecuteActionRequest(
        action_id="critical-1",
        content={"defense": "activate_system"},
        correlation_id="def-001",
        priority=9,
        deadline=datetime.now() + timedelta(minutes=1)
    )
    assert high_priority.priority == 9
    
    # Test normal priority action
    normal_priority = ExecuteActionRequest(
        action_id="routine-1",
        content={"maintenance": "check_status"},
        correlation_id="maint-001",
        priority=5
    )
    assert normal_priority.priority == 5

def test_push_delivery_pattern():
    """Test push-based delivery mechanism"""
    request = ExecuteActionRequest(
        action_id="push-1",
        content={"message": "test"},
        correlation_id="push-001",
        delivery_pattern="push",
        response_config={
            "target_endpoint": "https://example.com/webhook",
            "timeout": 30,
            "required_fields": ["status"]
        }
    )
    assert request.delivery_pattern == "push"
    assert "target_endpoint" in request.response_config

def test_pull_delivery_pattern():
    """Test pull-based delivery mechanism"""
    request = ExecuteActionRequest(
        action_id="pull-1", 
        content={"data": "test"},
        correlation_id="pull-001",
        delivery_pattern="pull",
        deadline=datetime.now() + timedelta(hours=24)
    )
    assert request.delivery_pattern == "pull"
    assert request.deadline is not None

def test_batch_delivery():
    """Test batch delivery functionality"""
    batch_request = ExecuteActionRequest(
        action_id="batch-1",
        content=[{"id": 1}, {"id": 2}],
        correlation_id="batch-001",
        delivery_pattern="batch",
        batch_config={
            "size": 100,
            "window": "1h",
            "partial_delivery": True
        }
    )
    assert batch_request.delivery_pattern == "batch"
    assert batch_request.batch_config["size"] == 100

def test_synchronous_delivery():
    """Test synchronous delivery requirements"""
    request = ExecuteActionRequest(
        action_id="sync-1",
        content={"command": "restart"},
        correlation_id="sync-001",
        delivery_pattern="synchronous",
        response_config={
            "timeout": 30,
            "required_fields": ["status", "message"]
        }
    )
    assert request.delivery_pattern == "synchronous"
    assert request.response_config["timeout"] == 30

def test_ordered_delivery():
    """Test ordered delivery guarantees"""
    requests = [
        ExecuteActionRequest(
            action_id=f"ord-{i}",
            content={"seq": i},
            correlation_id=f"ord-{i}",
            delivery_pattern="ordered",
            ordering_key="test-group"
        ) for i in range(3)
    ]
    assert all(r.delivery_pattern == "ordered" for r in requests)
    assert all(r.ordering_key == "test-group" for r in requests)

def test_response_processing():
    """Test response handling"""
    response = ActionStatusResponse(
        request_id="req-001",
        correlation_id="corr-001",
        status="completed",
        result={
            "status": "success",
            "code": 200,
            "headers": {"Content-Type": "application/json"}
        },
        response_validation={
            "success": True,
            "validated_fields": ["status", "code"]
        }
    )
    assert response.status == "completed"
    assert response.response_validation["success"] == True

def test_partial_response():
    """Test partial response handling"""
    response = ActionStatusResponse(
        request_id="req-001",
        correlation_id="corr-001",
        status="partial",
        result={
            "completed_items": 5,
            "total_items": 10,
            "partial_results": [{"id": i} for i in range(5)]
        },
        partial_delivery=True,
        sequence_info={
            "current_batch": 1,
            "total_batches": 2
        }
    )
    assert response.status == "partial"
    assert response.partial_delivery == True
    assert response.sequence_info["current_batch"] == 1

def test_action_validation():
    """Test action request validation"""
    # Test invalid priority
    with pytest.raises(ValidationError):
        ExecuteActionRequest(
            action_id="test-1",
            content={},
            correlation_id="corr-1",
            priority=10  # Invalid - too high
        )
    
    # Test missing required fields
    with pytest.raises(ValidationError):
        ExecuteActionRequest(
            action_id="test-1",
            correlation_id="corr-1"
            # Missing required 'content' field
        )
