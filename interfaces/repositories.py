"""
Repository interfaces for the Action Service.
Following Interface Segregation Principle by splitting into focused interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..domain import (
    Action, Credential, Event, ActionResult, Protocol, ActionType,
    Webhook, EventStatus, WebhookResult, Message
)

class ActionExecutor(ABC):
    """Interface for executing actions"""
    
    @abstractmethod
    def execute(self, action: Action) -> dict:
        """Execute an action and return the result"""
        pass

class AsyncActionRepository(ABC):
    """Repository for accessing webhook configurations"""
    
    @abstractmethod
    async def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook configuration by ID"""
        pass

class AsyncEventRepository(ABC):
    """Repository for managing webhook events"""
    
    @abstractmethod
    async def record_received(
        self,
        webhook_id: str,
        raw_headers: Dict[str, str],
        raw_body: bytes,
        content_type: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Record received webhook data"""
        pass

    @abstractmethod
    async def get_status(self, response_id: str) -> Optional[EventStatus]:
        """Get current processing status"""
        pass

class AsyncResultRepository(ABC):
    """Repository for webhook processing results"""
    
    @abstractmethod
    async def get_result(self, response_id: str) -> Optional[WebhookResult]:
        """Get webhook processing result"""
        pass

class BehaviourRepository(ABC):
    """Repository for accessing behaviour definitions and handlers"""
    
    @abstractmethod
    def get_protocol(self, protocol_id: str) -> Optional[Protocol]:
        """Get protocol definition by ID"""
        pass
        
    @abstractmethod
    def get_action_type(self, type_id: str) -> Optional[ActionType]:
        """Get action type definition by ID"""
        pass
        
    @abstractmethod
    def get_protocol_handler(self, protocol: Protocol, config: Dict[str, Any]) -> Any:
        """Get configured protocol handler instance"""
        pass
        
    @abstractmethod
    def validate_protocol_config(self, protocol: Protocol, config: Dict[str, Any]) -> bool:
        """Validate protocol configuration"""
        pass

class ActionRepository(ABC):
    """Manages action definitions"""
    
    @abstractmethod
    def create_action(self, 
        name: str,
        description: str,
        action_type: ActionType,
        protocol: Protocol,
        config: Dict[str, Any],
        credential_id: Optional[str] = None,
        schedule: Optional[str] = None,
        input_template: Optional[Dict] = None,
        output_template: Optional[Dict] = None
    ) -> Action:
        """Create a new action definition"""
        pass

    @abstractmethod
    def get_action(self, action_id: str) -> Optional[Action]:
        """Get action by ID"""
        pass
    
    @abstractmethod
    def list_actions(self, 
        action_type: Optional[ActionType] = None,
        protocol: Optional[Protocol] = None
    ) -> List[Action]:
        """List actions, optionally filtered"""
        pass

    @abstractmethod
    def update_action(self, action_id: str, updates: Dict[str, Any]) -> Action:
        """Update an action's configuration"""
        pass

    @abstractmethod
    def delete_action(self, action_id: str) -> None:
        """Delete an action"""
        pass

class CredentialRepository(ABC):
    """Manages service credentials"""
    
    @abstractmethod
    def store_credential(self,
        name: str,
        protocol: Protocol,
        secrets: Dict[str, str]
    ) -> Credential:
        """Store new credentials (encrypting secrets)"""
        pass

    @abstractmethod
    def get_credential(self, credential_id: str) -> Optional[Credential]:
        """Retrieve credentials (decrypting secrets)"""
        pass

    @abstractmethod
    def list_credentials(self, protocol: Optional[Protocol] = None) -> List[Credential]:
        """List credentials, optionally filtered by protocol"""
        pass

    @abstractmethod
    def delete_credential(self, credential_id: str) -> None:
        """Delete credentials"""
        pass

class WebhookRepository(ABC):
    """Repository for managing webhooks"""
    
    @abstractmethod
    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook configuration by ID"""
        pass

    @abstractmethod
    def validate_key(self, webhook_id: str, key: str) -> bool:
        """Validate webhook key"""
        pass

    @abstractmethod
    def record_received(
        self,
        webhook_id: str,
        raw_headers: Dict[str, str],
        raw_body: bytes,
        content_type: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Record received webhook data and return response ID"""
        pass

    @abstractmethod
    def get_status(self, response_id: str) -> Optional[EventStatus]:
        """Get current processing status"""
        pass

    @abstractmethod
    def get_result(self, response_id: str) -> Optional[WebhookResult]:
        """Get webhook processing result"""
        pass

class EventRepository(ABC):
    """Manages event flow through the system"""
    
    @abstractmethod
    def record_event(self,
        action_id: str,
        direction: str,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Event:
        """Record a new event"""
        pass

    @abstractmethod
    def record_received(self,
        webhook_id: str,
        response_id: str,
        raw_headers: Dict[str, str],
        raw_body: bytes,
        content_type: str,
        key_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Record received webhook data with content type handling"""
        pass

    @abstractmethod
    def get_received_webhook(self,
        webhook_id: str,
        response_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get received webhook data including metadata and payload"""
        pass

    @abstractmethod
    def get_status(self, response_id: str) -> Optional[EventStatus]:
        """Get current status of event processing"""
        pass

    @abstractmethod
    def update_event_status(self,
        event_id: str,
        status: str,
        error: Optional[str] = None
    ) -> Event:
        """Update event processing status"""
        pass

    @abstractmethod
    def list_events(self,
        action_id: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Event]:
        """Query events with filters"""
        pass

class ResultRepository(ABC):
    """Manages action execution results"""
    
    @abstractmethod
    def store_result(self,
        action_id: str,
        success: bool,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Store execution result"""
        pass

    @abstractmethod
    def get_result(self, response_id: str) -> Optional[WebhookResult]:
        """Get webhook processing result"""
        pass

    @abstractmethod
    def list_results(self,
        action_id: str,
        success: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ActionResult]:
        """Query results with filters"""
        pass

class MessageRepository(ABC):
    """Repository for managing system messages and notifications"""
    
    @abstractmethod
    def create_message(self,
        level: str,
        title: str,
        content: str,
        source: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Create a new system message"""
        pass

    @abstractmethod
    def get_message(self, message_id: str) -> Optional[Message]:
        """Retrieve a specific message by ID"""
        pass

    @abstractmethod
    def list_messages(self,
        level: Optional[str] = None,
        source: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        include_expired: bool = False,
        include_acknowledged: bool = True,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Message]:
        """Query messages with filters"""
        pass

    @abstractmethod
    def acknowledge_message(self,
        message_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None
    ) -> Message:
        """Mark message as acknowledged"""
        pass

    @abstractmethod
    def update_message(self,
        message_id: str,
        updates: Dict[str, Any]
    ) -> Message:
        """Update message content or metadata"""
        pass

    @abstractmethod
    def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        pass

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove expired messages"""
        pass

    @abstractmethod
    def get_unacknowledged_count(self,
        level: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None
    ) -> int:
        """Get count of unacknowledged messages matching filters"""
        pass
