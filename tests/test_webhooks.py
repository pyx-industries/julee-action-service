"""Tests for webhook handling usecases"""
from datetime import datetime, UTC
from typing import Dict, Optional
from unittest.mock import Mock, patch
import pytest
from uuid import UUID
from types import MappingProxyType

from ..usecases.webhooks import ReceiveWebhook, GetWebhookStatus
from ..interfaces.requests import WebhookRequest
from ..interfaces.responses import WebhookAcceptedResponse
from ..types import RepoSet

class MockWebhookRepo:
    def __init__(self, webhooks=None):
        self.webhooks = webhooks or {
            "test-webhook": {"key": "test-key"}
        }
        
    def get_webhook(self, webhook_id):
        if webhook_id in self.webhooks:
            return Mock(
                id=webhook_id,
                key=self.webhooks[webhook_id]["key"]
            )
        return None

class MockEventStatus:
    """Mock double for event status"""
    def __init__(self, state: str, correlation_id: str, error: Optional[str] = None):
        self.state = state
        self.correlation_id = correlation_id
        self.error = error

class MockWebhookResult:
    """Mock double for webhook result"""
    def __init__(self, success: bool, result: Optional[Dict] = None, error: Optional[str] = None):
        self.success = success
        self.result = result
        self.error = error

class InMemoryEventRepository:
    """Test implementation of EventRepository"""
    def __init__(self):
        self.events = {}
        self.statuses = {}
        
    def record_received(
        self,
        webhook_id: str,
        raw_headers: str,
        raw_body: str,
        content_type: str,
        correlation_id: Optional[str] = None
    ) -> str:
        response_id = str(UUID(int=len(self.events) + 1))
        self.events[response_id] = {
            "webhook_id": webhook_id,
            "headers": raw_headers,
            "raw_body": raw_body,
            "content_type": content_type,
            "correlation_id": correlation_id,
            "timestamp": datetime.now(UTC)
        }
        self.statuses[response_id] = "pending"
        return response_id
        
    def get_status(self, response_id: str) -> Optional[MockEventStatus]:
        if response_id not in self.statuses:
            return None
        return MockEventStatus(
            state=self.statuses[response_id],
            correlation_id=self.events[response_id].get("correlation_id"),
            error=self.events[response_id].get("error")
        )
        
    def update_status(self, response_id: str, status: str):
        if response_id in self.statuses:
            self.statuses[response_id] = status

class InMemoryResultRepository:
    """Test implementation of ResultRepository"""
    def __init__(self):
        self.results = {}
        
    def get_result(self, response_id: str) -> Optional[MockWebhookResult]:
        if response_id not in self.results:
            return None
        result_data = self.results[response_id]
        return MockWebhookResult(**result_data)
        
    def store_result(self, response_id: str, success: bool, result: Optional[Dict] = None, error: Optional[str] = None):
        self.results[response_id] = {
            "success": success,
            "result": result,
            "error": error
        }

@pytest.fixture
def mock_repos():
    """Create repository test doubles"""
    return MappingProxyType({
        "webhook_repository": MockWebhookRepo(),
        "event_repository": InMemoryEventRepository(),
        "result_repository": InMemoryResultRepository()
    })

@pytest.fixture 
def failed_webhook_result():
    """Create a failed webhook result"""
    return MockWebhookResult(
        success=False,
        error="Processing failed"
    )

@pytest.fixture
def failed_webhook_repo(failed_webhook_result):
    """Create repository with failed webhook"""
    repo = InMemoryResultRepository()
    repo.results["test-response-3"] = {
        "success": False,
        "error": "Processing failed"
    }
    return repo

def test_receive_webhook_json_payload(mock_repos):
    """Test successful webhook reception with JSON payload"""
    usecase = ReceiveWebhook(mock_repos)
    
    webhook_request = WebhookRequest(
        payload={"test": "data"},
        content_type="application/json",
        correlation_id="test-123"
    )
    
    # Convert JSON payload to bytes for storage
    import json
    raw_body = json.dumps(webhook_request.payload).encode('utf-8')
    
    result = usecase.execute(
        webhook_id="test-webhook",
        key="test-key", 
        request=webhook_request
    )
    
    assert isinstance(result, WebhookAcceptedResponse)
    assert result.status == "accepted"
    assert result.response_id
    assert result.correlation_id == "test-123"

def test_receive_webhook_binary_payload(mock_repos):
    """Test successful webhook reception with binary payload"""
    usecase = ReceiveWebhook(mock_repos)
    
    test_bytes = b"binary test data"
    webhook_request = WebhookRequest(
        raw_data=test_bytes,
        content_type="application/octet-stream",
        correlation_id="test-124"
    )
    
    result = usecase.execute(
        webhook_id="test-webhook",
        key="test-key",
        request=webhook_request
    )
    
    assert isinstance(result, WebhookAcceptedResponse)
    assert result.status == "accepted"
    assert result.correlation_id == "test-124"

def test_receive_webhook_multipart(mock_repos):
    """Test successful webhook reception with multipart form data"""
    usecase = ReceiveWebhook(mock_repos)
    
    test_file_content = b"file content"
    webhook_request = WebhookRequest(
        raw_data=test_file_content,
        content_type="multipart/form-data",
        metadata={"filename": "test.txt"},
        correlation_id="test-125"
    )
    
    result = usecase.execute(
        webhook_id="test-webhook",
        key="test-key",
        request=webhook_request
    )
    
    assert isinstance(result, WebhookAcceptedResponse)
    assert result.status == "accepted"
    assert result.correlation_id == "test-125"

def test_receive_webhook_payload_size_limit(mock_repos):
    """Test webhook rejection when payload exceeds size limit"""
    usecase = ReceiveWebhook(mock_repos)
    
    # Create payload larger than 1MB
    large_data = b"x" * (1_000_001)
    
    with pytest.raises(ValueError) as exc:
        webhook_request = WebhookRequest(
            raw_data=large_data,
            content_type="application/octet-stream"
        )
    assert "Data exceeds 1MB size limit" in str(exc.value)

def test_receive_webhook_invalid_content_type(mock_repos):
    """Test webhook handling with non-standard content type"""
    usecase = ReceiveWebhook(mock_repos)
    
    webhook_request = WebhookRequest(
        payload={"test": "data"},
        content_type="invalid/type",
        correlation_id="test-126"
    )
    
    result = usecase.execute("test-webhook", "test-key", webhook_request)
    
    assert isinstance(result, WebhookAcceptedResponse)
    assert result.status == "accepted"
    assert result.correlation_id == "test-126"

def test_receive_webhook_missing_required_field(mock_repos):
    """Test webhook rejection when required field is missing"""
    usecase = ReceiveWebhook(mock_repos)
    
    # Try to create request without required content_type
    with pytest.raises(ValueError):
        WebhookRequest(
            payload={"test": "data"}
        )

def test_receive_webhook_usecase_invalid_key(mock_repos):
    """Test webhook rejection with invalid key at usecase level"""
    usecase = ReceiveWebhook(mock_repos)
    
    webhook_request = WebhookRequest(
        headers={"Content-Type": "application/json"},
        payload={"test": "data"},
        content_type="application/json"
    )
    
    result = usecase.execute("test-webhook", "wrong-key", webhook_request)
    assert result is None

def test_receive_webhook_unknown_id(mock_repos):
    """Test webhook with unknown ID"""
    usecase = ReceiveWebhook(mock_repos)
    
    request = WebhookRequest(
        headers={"Content-Type": "application/json"},  # Use headers instead of raw_headers
        payload={"test": "data"},  # Use payload instead of raw_body
        content_type="application/json"
    )
    
    result = usecase.execute("unknown-webhook", "any-key", request)
    assert result is None  # Should return None for invalid webhook ID/key

def test_get_webhook_status_pending(mock_repos):
    """Test getting status of pending webhook"""
    # Setup
    event_repo = mock_repos["event_repository"]
    response_id = event_repo.record_received(
        webhook_id="test-webhook",
        raw_headers={"Content-Type": "application/json"},
        raw_body=b'{"test": "data"}',
        content_type="application/json",
        correlation_id="test-123"
    )
    
    usecase = GetWebhookStatus(mock_repos)
    response = usecase.execute(response_id)  # Use the actual response_id returned
    
    assert response.response_id == response_id  # Compare against actual response_id
    assert response.status == "pending"
    assert response.correlation_id == "test-123"
    assert response.result is None
    assert response.error is None

def test_get_webhook_status_completed(mock_repos):
    """Test getting status of completed webhook"""
    # Setup
    event_repo = mock_repos["event_repository"]
    result_repo = mock_repos["result_repository"]
    
    # Get actual response_id from record_received
    response_id = event_repo.record_received(
        webhook_id="test-webhook",
        raw_headers='{"Content-Type": "application/json"}',
        raw_body='{"test": "data"}',
        content_type="application/json",
        correlation_id="test-123"
    )
    
    # Use the actual response_id instead of hardcoded value
    event_repo.update_status(response_id, "completed")
    
    result_repo.store_result(
        response_id=response_id,  # Use actual response_id here too
        success=True,
        result={"processed": True}
    )
    
    usecase = GetWebhookStatus(mock_repos)
    response = usecase.execute(response_id)  # Use actual response_id here
    
    assert response.response_id == response_id  # Compare against actual response_id
    assert response.status == "completed"
    assert response.result == {"processed": True}
    assert response.error is None

def test_get_webhook_status_failed(mock_repos):
    """Test getting status of failed webhook"""
    # Setup
    event_repo = mock_repos["event_repository"]
    result_repo = mock_repos["result_repository"]
    
    response_id = event_repo.record_received(
        webhook_id="test-webhook",
        raw_headers='{"Content-Type": "application/json"}',
        raw_body='{"test": "data"}',
        content_type="application/json",
        correlation_id="test-123"
    )
    
    # Use the actual response_id
    event_repo.update_status(response_id, "failed")
    
    result_repo.store_result(
        response_id=response_id,
        success=False,
        error="Processing failed"
    )
    
    usecase = GetWebhookStatus(mock_repos)
    response = usecase.execute(response_id)
    
    assert response.response_id == response_id
    assert response.status == "failed"
    assert response.result is None
    assert response.error == "Processing failed"

def test_get_webhook_status_unknown(mock_repos):
    """Test getting status of unknown response ID"""
    usecase = GetWebhookStatus(mock_repos)
    
    with pytest.raises(ValueError) as exc:
        usecase.execute("unknown-response")
    assert "Unknown response ID" in str(exc.value)
