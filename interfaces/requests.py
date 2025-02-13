"""
Request models for the Action Service API.

This module defines the data structures for incoming API requests,
using Pydantic models to ensure validation and type safety.
"""

from typing import Dict, Optional, Any, Literal, Union, List, get_args
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

class ExecuteActionRequest(BaseModel):
    """Request to execute an action on behalf of Julee"""
    model_config = ConfigDict(extra="forbid")  # Be strict!
    
    action_id: str = Field(..., description="ID of the pre-configured action to execute")
    content: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Content to be delivered (single item or batch)")
    correlation_id: str = Field(..., description="For tracking the request through the system")
    priority: Optional[int] = Field(default=0, ge=0, le=9, description="Execution priority (0-9)")
    deadline: Optional[datetime] = Field(None, description="When this must complete by")
    idempotency_key: Optional[str] = Field(None, description="Client-provided deduplication key")
    delivery_pattern: Optional[str] = Field(None, description="Delivery pattern to use")
    batch_config: Optional[Dict] = Field(None, description="Batch delivery configuration")
    response_config: Optional[Dict] = Field(None, description="Response handling configuration")
    ordering_key: Optional[str] = Field(None, description="Key for ordered delivery")

class ActionAcceptedResponse(BaseModel):
    """Immediate response confirming action acceptance"""
    model_config = ConfigDict(extra="forbid")
    
    request_id: str = Field(..., description="Server-assigned request tracking ID")
    status: Literal["accepted"] = "accepted"
    estimated_completion: Optional[datetime] = None

class ActionStatusResponse(BaseModel):
    """Status check response"""
    model_config = ConfigDict(extra="forbid")
    
    request_id: str = Field(..., description="Server-assigned request tracking ID") 
    correlation_id: str = Field(..., description="Client's correlation ID")
    status: Literal["pending", "processing", "completed", "failed", "partial"]
    completion_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    delivery_pattern: Optional[str] = Field(None, description="Pattern used for delivery")
    partial_delivery: Optional[bool] = Field(None, description="Whether this is a partial delivery")
    sequence_info: Optional[Dict] = Field(None, description="Ordering/sequencing information")
    response_validation: Optional[Dict] = Field(None, description="Response validation results")

class WebhookRequest(BaseModel):
    """Incoming webhook request"""
    model_config = ConfigDict(extra="forbid")
    
    payload: Optional[Dict[str, Any]] = Field(None, description="JSON payload")
    raw_data: Optional[bytes] = Field(None, description="Raw binary data")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    content_type: str = Field(..., description="Content-Type of the payload")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    correlation_id: Optional[str] = Field(None, description="Client correlation ID")
    
    @field_validator('raw_data')
    def validate_data_size(cls, v):
        """Enforce data size limit"""
        if v and len(v) > 1_000_000:  # 1MB limit
            raise ValueError("Data exceeds 1MB size limit")
        return v

class WebhookStatusRequest(BaseModel):
    """Request to check webhook processing status"""
    model_config = ConfigDict(extra="forbid")
    
    response_id: str = Field(..., description="Response ID from webhook submission")

class ActionCallbackRequest(BaseModel):
    """Internal callback request from trusted sources"""
    model_config = ConfigDict(extra="forbid")
    
    protocol_id: str = Field(..., description="Protocol identifier")
    action_type_id: str = Field(..., description="Action type identifier")
    payload: Dict[str, Any] = Field(..., description="Callback payload")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

    @field_validator('payload')
    def validate_confidence(cls, v):
        """Validate confidence is between 0 and 1"""
        if 'confidence' in v:
            confidence = v['confidence']
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                raise ValueError("Confidence must be a number between 0 and 1")
        return v

class ProcessActionRequest(BaseModel):
    """Internal request to process an action"""
    model_config = ConfigDict(extra="forbid")
    
    action_id: str = Field(..., description="Action identifier")
    retry_count: int = Field(0, description="Number of retry attempts")

class CreateActionRequest(BaseModel):
    """Request to create a new action definition"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Name of the action")
    description: str = Field(..., description="Description of the action")
    action_type: str = Field(..., description="Action type identifier")
    protocol: str = Field(..., description="Protocol identifier")
    config: Dict[str, Any] = Field(..., description="Protocol-specific configuration")
    credential_id: Optional[str] = Field(None, description="Associated credential ID")
    schedule: Optional[str] = Field(None, description="Cron schedule if periodic")
    input_template: Optional[Dict] = Field(None, description="Input transformation template")
    output_template: Optional[Dict] = Field(None, description="Output transformation template")

class ListActionsRequest(BaseModel):
    """Request to list actions with filters"""
    model_config = ConfigDict(extra="forbid")
    
    action_type: Optional[str] = Field(None, description="Filter by action type")
    protocol: Optional[str] = Field(None, description="Filter by protocol")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")

class ListEventsRequest(BaseModel):
    """Request to list events with filters"""
    model_config = ConfigDict(extra="forbid")
    
    action_id: Optional[str] = Field(None, description="Filter by action")
    status: Optional[str] = Field(None, description="Filter by status")
    start_time: Optional[datetime] = Field(None, description="Filter from time")
    end_time: Optional[datetime] = Field(None, description="Filter to time")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")

MessageLevelType = Literal["error", "warning", "info"]
MessageTargetType = Literal["global", "action", "protocol"]

class CreateSystemMessageRequest(BaseModel):
    """Request model for system message creation"""
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(..., description="Message title/summary")
    content: str = Field(..., description="Full message content")
    level: MessageLevelType = Field(..., description="Message severity level")
    source: str = Field(..., description="System component that generated message")
    target_type: Optional[MessageTargetType] = Field(None, description="Type of target this message is for")
    target_id: Optional[str] = Field(None, description="ID of the target resource")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")
    expires_at: Optional[datetime] = Field(None, description="When this message should expire")
    
    @field_validator('title')
    def validate_title_length(cls, v):
        if len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v
    
    @field_validator('content')
    def validate_content_length(cls, v):
        if len(v) > 5000:
            raise ValueError("Content must be 5000 characters or less")
        return v
    
    @field_validator('target_id')
    def validate_target_id(cls, v, values):
        if v and not values.data.get('target_type'):
            raise ValueError("target_id requires target_type to be set")
        return v

class CreateCredentialRequest(BaseModel):
    """Request to store new credentials"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Name for the credentials")
    protocol: str = Field(..., description="Protocol identifier")
    secrets: Dict[str, str] = Field(..., description="Protocol-specific secrets")


class UpdateMessageRequest(BaseModel):
    """Request model for updating system message"""
    model_config = ConfigDict(extra="forbid")
    
    message_id: str = Field(..., description="ID of message to update")
    title: Optional[str] = Field(None, description="New message title")
    content: Optional[str] = Field(None, description="New message content")
    level: Optional[MessageLevelType] = Field(None, description="New message severity level")
    expires_at: Optional[datetime] = Field(None, description="New expiration time")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    
    @field_validator('title')
    def validate_title_length(cls, v):
        if v and len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v
    
    @field_validator('content') 
    def validate_content_length(cls, v):
        if v and len(v) > 5000:
            raise ValueError("Content must be 5000 characters or less")
        return v

class CreateStreamRequest(BaseModel):
    """Request model for creating a new stream."""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Name of the stream")
    type: str = Field(..., description="Stream type (afferent/efferent)")
    config: Dict = Field(..., description="Stream configuration")


class UpdateStreamStatusRequest(BaseModel):
    """Request model for updating stream status."""
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(..., description="New status value")


class CreateTemplateRequest(BaseModel):
    """Request model for creating an action template."""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    stream_type: str = Field(..., description="Stream type this template is for")
    config_template: Dict = Field(..., description="Template configuration")


class UpdateTemplateRequest(BaseModel):
    """Request model for updating an action template."""
    model_config = ConfigDict(extra="forbid")
    
    name: Optional[str] = Field(None, description="New template name")
    description: Optional[str] = Field(None, description="New description")
    config_template: Optional[Dict] = Field(None, description="New configuration")


class UpdateMonitorMetricsRequest(BaseModel):
    """Request model for updating stream metrics."""
    model_config = ConfigDict(extra="forbid")
    
    metrics: Dict = Field(..., description="New metrics data")


class UpdateMonitorStatusRequest(BaseModel):
    """Request model for updating monitor status."""
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(..., description="New status")
    error_count: int = Field(..., description="Current error count")
