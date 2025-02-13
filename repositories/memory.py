"""In-memory implementations of repositories required by public API"""
from typing import Dict, Optional, Any, List
from datetime import datetime, UTC
from uuid import uuid4
from ..log_utils import ActionServiceLogger
from ..domain.direction import ActionDirection

from ..domain import (
    Webhook, WebhookResult, EventStatus, Action, ActionType, Protocol,
    ActionResult, Event, Credential, Message
)
from ..interfaces.repositories import (
    ActionRepository, WebhookRepository, EventRepository, ResultRepository,
    CredentialRepository, MessageRepository
)

from ..interfaces.repositories import (
    ActionRepository, WebhookRepository, EventRepository, ResultRepository,
    CredentialRepository
)

class InMemoryActionRepository(ActionRepository):
    """In-memory implementation of action repository"""
    
    def __init__(self):
        self._actions: Dict[str, Action] = {}
        
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
        action_id = str(uuid4())
        action = Action(
            id=action_id,
            name=name,
            description=description,
            action_type=action_type,
            protocol=protocol,
            config=config,
            credential_id=credential_id,
            schedule=schedule,
            input_template=input_template,
            output_template=output_template,
            created_at=datetime.now()
        )
        self._actions[action_id] = action
        return action

    def get_action(self, action_id: str) -> Optional[Action]:
        """Get action by ID"""
        return self._actions.get(action_id)
    
    def list_actions(self, 
        action_type: Optional[ActionType] = None,
        protocol: Optional[Protocol] = None
    ) -> List[Action]:
        """List actions, optionally filtered"""
        actions = list(self._actions.values())
        
        if action_type:
            actions = [a for a in actions if a.action_type.id == action_type.id]
            
        if protocol:
            actions = [a for a in actions if a.protocol.id == protocol.id]
            
        return actions

    def update_action(self, action_id: str, updates: Dict[str, Any]) -> Action:
        """Update an action's configuration"""
        if action_id not in self._actions:
            raise ValueError(f"Action not found: {action_id}")
            
        action = self._actions[action_id]
        
        # Update allowed fields
        for field, value in updates.items():
            if hasattr(action, field):
                setattr(action, field, value)
                
        return action

    def delete_action(self, action_id: str) -> None:
        """Delete an action"""
        if action_id in self._actions:
            del self._actions[action_id]

class InMemoryWebhookRepository(WebhookRepository):
    """In-memory implementation of webhook repository"""
    
    def __init__(self):
        self._webhooks: Dict[str, Webhook] = {}
        self._received: Dict[str, Dict] = {}
        self._statuses: Dict[str, EventStatus] = {}
        self._results: Dict[str, WebhookResult] = {}
        
        # Pre-populate with test webhook
        self._webhooks["test"] = Webhook(
            id="test",
            key="secret",
            config={}
        )
        
    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID"""
        return self._webhooks.get(webhook_id)
        
    def validate_key(self, webhook_id: str, key: str) -> bool:
        """Validate webhook key"""
        webhook = self.get_webhook(webhook_id)
        return webhook is not None and webhook.key == key

    def record_received(
        self,
        webhook_id: str,
        response_id: str,
        raw_headers: Dict[str, str],
        raw_body: bytes,
        content_type: str,
        correlation_id: Optional[str]
    ) -> None:
        """Record received webhook data"""
        self._received[response_id] = {
            "webhook_id": webhook_id,
            "headers": raw_headers,
            "body": raw_body,
            "content_type": content_type,
            "correlation_id": correlation_id,
            "timestamp": datetime.now()
        }
        self._statuses[response_id] = EventStatus(
            id=response_id,
            state="received",
            correlation_id=correlation_id
        )

    def get_status(self, response_id: str) -> Optional[EventStatus]:
        """Get current processing status"""
        return self._statuses.get(response_id)

    def get_result(self, response_id: str) -> Optional[WebhookResult]:
        """Get webhook processing result"""
        return self._results.get(response_id)

class InMemoryEventRepository(EventRepository):
    """In-memory implementation of event repository"""
    
    def __init__(self):
        self._events: Dict[str, Event] = {}
        self._statuses: Dict[str, EventStatus] = {}
        self.logger = ActionServiceLogger()
        
    def record_event(self,
        action_id: str,
        direction: str,
        content: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Event:
        """Record a new event"""
        self.logger.debug(
            f"Recording event for action {action_id}: direction={direction}, type={content_type}, "
            f"metadata_keys={list(metadata.keys())}, content_length={len(str(content))}"
        )
        if not ActionDirection.is_valid(direction):
            self.logger.error(f"Invalid direction '{direction}' for action {action_id}")
            raise ValueError(f"Invalid direction: {direction}")
            
        direction = ActionDirection.normalize(direction)
        
        event_id = str(uuid4())
        event = Event(
            id=event_id,
            action_id=action_id,
            direction=direction,
            content=content,
            content_type=content_type,
            metadata=metadata,
            timestamp=datetime.now()
        )
        self._events[event_id] = event
        return event

    def record_received(self,
        webhook_id: str,
        response_id: str,
        raw_headers: Dict[str, str],
        raw_body: bytes,
        content_type: str,
        key_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Record received webhook data"""
        self._events[response_id] = {
            "webhook_id": webhook_id,
            "headers": raw_headers,
            "body": raw_body,
            "content_type": content_type,
            "key_id": key_id,
            "correlation_id": correlation_id,
            "timestamp": datetime.now()
        }
        self._statuses[response_id] = EventStatus(
            id=response_id,
            state="received",
            correlation_id=correlation_id
        )

    def get_received_webhook(self,
        webhook_id: str,
        response_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get received webhook data"""
        event = self._events.get(response_id)
        if event and event.get("webhook_id") == webhook_id:
            return event
        return None

    def get_status(self, response_id: str) -> Optional[EventStatus]:
        """Get current status"""
        return self._statuses.get(response_id)

    def update_event_status(self,
        event_id: str,
        status: str,
        error: Optional[str] = None
    ) -> Event:
        """Update event status"""
        self.logger.debug(
            f"Updating event {event_id}: new_status={status}, current_status="
            f"{self._events[event_id]['status'] if event_id in self._events else 'N/A'}, "
            f"has_error={'yes' if error else 'no'}"
        )
        if event_id not in self._events:
            self.logger.error(f"Event not found: {event_id}")
            raise ValueError(f"Event not found: {event_id}")
        
        event = self._events[event_id]
        event["status"] = status
        if error:
            event["error"] = error
        return event

    def list_events(self,
        action_id: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Event]:
        """Query events with filters"""
        matching_events = [e for e in self._events.values() 
                         if (not action_id or e.get("action_id") == action_id)
                         and (not status or e.get("status") == status)
                         and (not start_time or e.get("timestamp") >= start_time)
                         and (not end_time or e.get("timestamp") <= end_time)]
        
        self.logger.debug(
            f"Listing events: filter_action={action_id}, filter_status={status}, "
            f"total_events={len(self._events)}, matching_events={len(matching_events)}, "
            f"date_range={start_time and start_time.isoformat()} to {end_time and end_time.isoformat()}"
        )
        events = []
        for event in self._events.values():
            if action_id and event.get("action_id") != action_id:
                continue
            if status and event.get("status") != status:
                continue
            if start_time and event.get("timestamp") < start_time:
                continue
            if end_time and event.get("timestamp") > end_time:
                continue
            events.append(event)
        return events

class InMemoryCredentialRepository(CredentialRepository):
    """In-memory implementation of credential repository"""
    
    def __init__(self):
        self._credentials: Dict[str, Credential] = {}
        
    def store_credential(self,
        name: str,
        protocol: Protocol,
        secrets: Dict[str, str]
    ) -> Credential:
        """Store new credentials (encrypting secrets)"""
        credential_id = str(uuid4())
        credential = Credential(
            id=credential_id,
            name=name,
            protocol=protocol,
            secrets=secrets,  # In a real impl, these would be encrypted
            created_at=datetime.now()
        )
        self._credentials[credential_id] = credential
        return credential

    def get_credential(self, credential_id: str) -> Optional[Credential]:
        """Retrieve credentials (decrypting secrets)"""
        return self._credentials.get(credential_id)

    def list_credentials(self, protocol: Optional[Protocol] = None) -> List[Credential]:
        """List credentials, optionally filtered by protocol"""
        credentials = list(self._credentials.values())
        if protocol:
            credentials = [c for c in credentials if c.protocol.id == protocol.id]
        return credentials

    def delete_credential(self, credential_id: str) -> None:
        """Delete credentials"""
        if credential_id in self._credentials:
            del self._credentials[credential_id]

class InMemoryResultRepository(ResultRepository):
    """In-memory implementation of result repository"""
    
    def __init__(self):
        self._results: Dict[str, WebhookResult] = {}
        
    def store_result(self,
        action_id: str,
        success: bool,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Store execution result"""
        action_result = ActionResult(
            action_id=action_id,
            success=success,
            result=result,
            error=error,
            metadata=metadata,
            timestamp=datetime.now()
        )
        self._results[action_id] = action_result
        return action_result

    def get_result(self, response_id: str) -> Optional[WebhookResult]:
        """Get webhook processing result"""
        return self._results.get(response_id)
        
    def list_results(self,
        action_id: str,
        success: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ActionResult]:
        """Query results with filters"""
        results = []
        for result in self._results.values():
            if result.action_id != action_id:
                continue
            if success is not None and result.success != success:
                continue
            if start_time and result.timestamp < start_time:
                continue
            if end_time and result.timestamp > end_time:
                continue
            results.append(result)
        return results

class InMemoryMessageRepository(MessageRepository):
    """In-memory implementation of message repository"""
    
    def __init__(self):
        self._messages: Dict[str, Message] = {}
        
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
        message_id = str(uuid4())
        message = Message(
            id=message_id,
            level=level,
            title=title,
            content=content,
            source=source,
            target_type=target_type,
            target_id=target_id,
            expires_at=expires_at,
            metadata=metadata
        )
        self._messages[message_id] = message
        return message

    def get_message(self, message_id: str) -> Optional[Message]:
        """Retrieve a specific message"""
        return self._messages.get(message_id)

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
        messages = []
        now = datetime.now(UTC)
        
        for msg in self._messages.values():
            # Apply filters
            if level and msg.level != level:
                continue
            if source and msg.source != source:
                continue
            if target_type and msg.target_type != target_type:
                continue
            if target_id and msg.target_id != target_id:
                continue
            if not include_expired and msg.expires_at and msg.expires_at < now:
                continue
            if not include_acknowledged and msg.acknowledged_at:
                continue
            if start_time and msg.created_at < start_time:
                continue
            if end_time and msg.created_at > end_time:
                continue
                
            messages.append(msg)
            if len(messages) >= limit:
                break
                
        return messages

    def acknowledge_message(self,
        message_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None
    ) -> Message:
        """Mark message as acknowledged"""
        if message_id not in self._messages:
            raise ValueError(f"Message not found: {message_id}")
            
        message = self._messages[message_id]
        
        # Create new message with acknowledgment
        updated = Message(
            **{**message.__dict__,
               'acknowledged_by': acknowledged_by,
               'acknowledged_at': datetime.now(UTC),
               'acknowledgment_notes': notes}
        )
        self._messages[message_id] = updated
        return updated

    def update_message(self,
        message_id: str,
        updates: Dict[str, Any]
    ) -> Message:
        """Update message fields"""
        if message_id not in self._messages:
            raise ValueError(f"Message not found: {message_id}")
            
        message = self._messages[message_id]
        updated = Message(**{**message.__dict__, **updates})
        self._messages[message_id] = updated
        return updated

    def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        if message_id in self._messages:
            del self._messages[message_id]
            return True
        return False

    def cleanup_expired(self) -> int:
        """Remove expired messages"""
        now = datetime.now(UTC)
        expired = [
            msg_id for msg_id, msg in self._messages.items()
            if msg.expires_at and msg.expires_at < now
        ]
        for msg_id in expired:
            del self._messages[msg_id]
        return len(expired)

    def get_unacknowledged_count(self,
        level: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None
    ) -> int:
        """Count unacknowledged messages"""
        count = 0
        for msg in self._messages.values():
            if msg.acknowledged_at:
                continue
            if level and msg.level != level:
                continue
            if target_type and msg.target_type != target_type:
                continue
            if target_id and msg.target_id != target_id:
                continue
            count += 1
        return count
