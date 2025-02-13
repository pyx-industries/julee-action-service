"""
Core business logic for handling actions, callbacks and inbound messages.
"""
import uuid
from typing import Optional
from datetime import datetime, UTC

from ..interfaces.repositories import (
    BehaviourRepository,
    ActionRepository,
    EventRepository,
    MessageRepository
)
from ..interfaces.requests import ActionCallbackRequest, ProcessActionRequest
from ..domain import ActionResult
from ..domain.messages import (
    InboundMessageRequest,
    InboundMessageResponse,
    WorkerProcessingRequest,
    WorkerProcessingResponse
)
from ..domain.config import ProtocolConfigSchema

class HandleInboundMessage:
    """Handle incoming messages from external systems"""
    
    def __init__(
        self,
        behaviour_repo: BehaviourRepository,
        message_repo: MessageRepository,
        event_repo: EventRepository
    ):
        self.behaviour_repo = behaviour_repo
        self.message_repo = message_repo
        self.event_repo = event_repo

    def execute(self, request: InboundMessageRequest) -> InboundMessageResponse:
        """Handle stage 1 of inbound message processing"""
        try:
            # Basic request validation
            if not request.endpoint or not request.payload:
                return InboundMessageResponse(
                    message_id="",
                    received_at=datetime.now(UTC),
                    validation_status="invalid",
                    validation_details={"error": "Missing endpoint or payload"},
                    correlation_id=request.correlation_id
                )

            # Store message and get ID
            message_id = self.message_repo.store_message(
                endpoint=request.endpoint,
                payload=request.payload,
                metadata=request.metadata
            )

            # Record receipt event
            self.event_repo.record_received(
                message_id=message_id,
                correlation_id=request.correlation_id
            )

            return InboundMessageResponse(
                message_id=message_id,
                received_at=datetime.now(UTC),
                validation_status="accepted",
                correlation_id=request.correlation_id
            )

        except Exception as e:
            return InboundMessageResponse(
                message_id="",
                received_at=datetime.now(UTC),
                validation_status="error",
                validation_details={"error": str(e)},
                correlation_id=request.correlation_id
            )

class ProcessInboundMessage:
    """Process validated inbound messages"""
    
    def __init__(
        self,
        behaviour_repo: BehaviourRepository,
        message_repo: MessageRepository,
        event_repo: EventRepository
    ):
        self.behaviour_repo = behaviour_repo
        self.message_repo = message_repo
        self.event_repo = event_repo

    def execute(self, request: WorkerProcessingRequest) -> WorkerProcessingResponse:
        """Handle stage 2 of inbound message processing"""
        try:
            # Get protocol handler
            protocol = self.behaviour_repo.get_protocol(request.protocol_id)
            if not protocol:
                raise ValueError(f"Unknown protocol: {request.protocol_id}")

            # Process via protocol handler
            handler = self.behaviour_repo.get_protocol_handler(
                protocol,
                request.validated_payload
            )
            result = handler.execute(request.validated_payload)

            # Record success
            self.event_repo.record_success(
                message_id=request.message_id,
                result=result
            )

            return WorkerProcessingResponse(
                message_id=request.message_id,
                processing_id=str(uuid.uuid4()),
                status="processed",
                result=result,
                next_actions=result.get("next_actions", [])
            )

        except Exception as e:
            # Record failure
            self.event_repo.record_failure(
                message_id=request.message_id,
                error=str(e)
            )

            return WorkerProcessingResponse(
                message_id=request.message_id,
                processing_id=str(uuid.uuid4()),
                status="failed",
                error=str(e)
            )

class HandleCallback:
    """Handle incoming webhook/callback requests"""
    
    def __init__(
        self,
        behaviour_repo: BehaviourRepository,
        action_repo: ActionRepository,
        event_repo: EventRepository
    ):
        self.behaviour_repo = behaviour_repo
        self.action_repo = action_repo
        self.event_repo = event_repo

    def execute(self, request: ActionCallbackRequest) -> ActionResult:
        # Validate protocol exists and is configured correctly
        protocol = self.behaviour_repo.get_protocol(request.protocol_id)
        if not protocol:
            raise ValueError(f"Unknown protocol: {request.protocol_id}")
            
        # Validate action type is supported for this protocol
        action_type = self.behaviour_repo.get_action_type(request.action_type_id)
        if not action_type:
            raise ValueError(f"Unknown action type: {request.action_type_id}")
            
        # Validate configuration against protocol requirements
        config_schema = ProtocolConfigSchema(protocol.config_schema)
        if not config_schema.validate(request.payload):
            raise ValueError("Invalid protocol configuration")
            
        # Create action record
        action = self.action_repo.create(
            action_type=action_type,
            protocol=protocol,
            config=request.payload,
            metadata=request.metadata
        )
        
        # Record event
        self.event_repo.record_received(
            action_id=action.id,
            payload=request.payload
        )
        
        return ActionResult(
            action_id=action.id,
            success=True,
            result={"status": "accepted"}
        )

class ProcessAction:
    """Process an action using its configured protocol"""
    
    def __init__(
        self,
        behaviour_repo: BehaviourRepository,
        action_repo: ActionRepository,
        event_repo: EventRepository
    ):
        self.behaviour_repo = behaviour_repo
        self.action_repo = action_repo
        self.event_repo = event_repo

    def execute(self, request: ProcessActionRequest) -> Optional[ActionResult]:
        # Get action details
        action = self.action_repo.get(request.action_id)
        if not action:
            raise ValueError(f"Unknown action: {request.action_id}")
            
        # Get protocol handler
        protocol = self.behaviour_repo.get_protocol(action.protocol.id)
        if not protocol:
            raise ValueError(f"Protocol not found: {action.protocol.id}")
            
        try:
            # Execute via protocol handler
            handler = self.behaviour_repo.get_protocol_handler(protocol, action.config)
            result = handler.execute(action)
            
            # Record success
            self.event_repo.record_success(
                action_id=action.id,
                result=result
            )
            
            return result
            
        except Exception as e:
            # Record failure
            self.event_repo.record_failure(
                action_id=action.id,
                error=str(e),
                retry_count=request.retry_count
            )
            
            # Let caller handle retry logic
            raise
"""Action management usecases"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from ..domain import Action, ActionType, Protocol
from ..types import RepoSet

class CreateActionRequest(BaseModel):
    """Request model for action creation"""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    description: str
    action_type: str
    protocol: str
    config: Dict[str, Any]
    credential_id: Optional[str] = None
    schedule: Optional[str] = None
    input_template: Optional[Dict] = None
    output_template: Optional[Dict] = None

class ActionResponse(BaseModel):
    """Standard response for action operations"""
    model_config = ConfigDict(extra="forbid")
    
    action: Action
    status: str
    message: Optional[str] = None

class ActionListResponse(BaseModel):
    """Response for action listing"""
    model_config = ConfigDict(extra="forbid")
    
    actions: List[Action]
    total: int
    filtered: Optional[int] = None

class CreateAction:
    """Create a new action definition"""
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.behaviour_repo = reposet["behaviour_repository"]
        
    def execute(self, request: CreateActionRequest) -> ActionResponse:
        # Get and validate action type
        action_type = self.behaviour_repo.get_action_type(request.action_type)
        if not action_type:
            raise ValueError(f"Invalid action type: {request.action_type}")
            
        # Get and validate protocol
        protocol = self.behaviour_repo.get_protocol(request.protocol)
        if not protocol:
            raise ValueError(f"Invalid protocol: {request.protocol}")
            
        # Validate protocol config
        if not self.behaviour_repo.validate_protocol_config(protocol, request.config):
            raise ValueError("Invalid protocol configuration")
            
        action = self.action_repo.create_action(
            name=request.name,
            description=request.description,
            action_type=action_type,
            protocol=protocol,
            config=request.config,
            credential_id=request.credential_id,
            schedule=request.schedule,
            input_template=request.input_template,
            output_template=request.output_template
        )
        
        return ActionResponse(
            action=action,
            status="created",
            message="Action created successfully"
        )

class ListActionsRequest(BaseModel):
    """Request model for listing actions"""
    model_config = ConfigDict(extra="forbid")
    
    action_type: Optional[str] = None
    protocol: Optional[str] = None
    page: int = 1
    page_size: int = 50

class ListActions:
    """List actions with optional filters"""
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.behaviour_repo = reposet["behaviour_repository"]
        
    def execute(self, request: ListActionsRequest) -> ActionListResponse:
        # Resolve action type if provided
        action_type_obj = None
        if request.action_type:
            action_type_obj = self.behaviour_repo.get_action_type(request.action_type)
            if not action_type_obj:
                raise ValueError(f"Invalid action type: {request.action_type}")
                
        # Resolve protocol if provided
        protocol_obj = None
        if request.protocol:
            protocol_obj = self.behaviour_repo.get_protocol(request.protocol)
            if not protocol_obj:
                raise ValueError(f"Invalid protocol: {request.protocol}")
                
        actions = self.action_repo.list_actions(
            action_type=action_type_obj,
            protocol=protocol_obj
        )
        
        return ActionListResponse(
            actions=actions,
            total=len(actions)
        )
