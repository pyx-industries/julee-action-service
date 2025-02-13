"""
Response models for the Action Service API.

This module defines the data structures for API responses,
using Pydantic models to ensure consistent output formatting.
"""

from typing import Dict, List, Optional, Union, Any, Literal
from datetime import datetime, UTC
from pydantic import BaseModel, Field, ConfigDict

class RateLimitInfo(BaseModel):
    """Rate limit information included in responses"""
    model_config = ConfigDict(extra="forbid")
    
    limit: int = Field(..., description="Rate limit ceiling")
    remaining: int = Field(..., description="Remaining requests")
    reset: datetime = Field(..., description="When limit resets")
from datetime import datetime, UTC
from pydantic import BaseModel, Field, ConfigDict

from ..domain import ActionTemplate

class ActionStatusResponse(BaseModel):
    """Status check response"""
    model_config = ConfigDict(extra="forbid")
    
    request_id: str = Field(..., description="Server-assigned request tracking ID") 
    correlation_id: str = Field(..., description="Client's correlation ID")
    status: str = Field(..., description="Current status")
    completion_time: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

class StreamResponse(BaseModel):
    """Base response model for stream operations."""
    model_config = ConfigDict(extra="forbid")
    
    action: Dict = Field(..., description="Action details")
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Additional information")

class StreamListResponse(BaseModel):
    """Response model for listing streams."""
    model_config = ConfigDict(extra="forbid")
    
    actions: List[Dict] = Field(..., description="List of stream actions")
    total: int = Field(..., description="Total number of streams")

class TemplateResponse(BaseModel):
    """Response model for template operations."""
    model_config = ConfigDict(extra="forbid")
    
    template: ActionTemplate = Field(..., description="Template details")
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Additional information")

class TemplateListResponse(BaseModel):
    """Response model for listing templates."""
    model_config = ConfigDict(extra="forbid")
    
    templates: List[ActionTemplate] = Field(..., description="List of templates")
    total: int = Field(..., description="Total number of templates")

class MonitorResponse(BaseModel):
    """Response model for monitor operations."""
    model_config = ConfigDict(extra="forbid")
    
    metrics: Dict = Field(..., description="Monitoring metrics")
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Additional information")

class WebhookAcceptedResponse(BaseModel):
    """Response to webhook submission"""
    model_config = ConfigDict(extra="forbid")
    
    response_id: str = Field(..., description="Unique response ID for status checking")
    status: Literal["accepted"] = "accepted"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class WebhookStatusResponse(BaseModel):
    """Response to status check"""
    model_config = ConfigDict(extra="forbid")
    
    response_id: str = Field(..., description="Response ID being checked")
    status: Literal["pending", "processing", "completed", "failed"] = Field(..., description="Current status")
    result: Optional[Dict[str, Any]] = Field(None, description="Processing result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")
    correlation_id: Optional[str] = Field(None, description="Client correlation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    rate_limit: Optional[RateLimitInfo] = Field(None, description="Rate limit details")

class WebhookAcceptedResponse(BaseModel):
    """Response to webhook submission"""
    model_config = ConfigDict(extra="forbid")
    
    response_id: str = Field(..., description="Response ID for status checking")
    status: Literal["accepted"] = "accepted"
    correlation_id: Optional[str] = Field(None, description="Client correlation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    rate_limit: Optional[RateLimitInfo] = Field(None, description="Rate limit details")

class WebhookErrorResponse(BaseModel):
    """Standard error response for webhook API"""
    model_config = ConfigDict(extra="forbid")
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    correlation_id: Optional[str] = Field(None, description="Client correlation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    rate_limit: Optional[RateLimitInfo] = Field(None, description="Rate limit details")

class CallbackAcceptedResponse(BaseModel):
    """Response to internal callback submission"""
    model_config = ConfigDict(extra="forbid")
    
    callback_id: str = Field(..., description="Callback identifier")
    status: Literal["accepted"] = "accepted"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class ActionResponse(BaseModel):
    """Response for action operations"""
    model_config = ConfigDict(extra="forbid")
    
    action_id: str = Field(..., description="Action identifier")
    name: str = Field(..., description="Action name")
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Optional status message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class ActionListResponse(BaseModel):
    """Response for action listing"""
    model_config = ConfigDict(extra="forbid")
    
    actions: List[Dict[str, Any]] = Field(..., description="List of actions")
    total: int = Field(..., description="Total number of actions")
    filtered: Optional[int] = Field(None, description="Number after filtering")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")

class EventListResponse(BaseModel):
    """Response for event listing"""
    model_config = ConfigDict(extra="forbid")
    
    events: List[Dict[str, Any]] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events")
    filtered: Optional[int] = Field(None, description="Number after filtering")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")

class CredentialResponse(BaseModel):
    """Response for credential operations"""
    model_config = ConfigDict(extra="forbid")
    
    credential_id: str = Field(..., description="Credential identifier")
    name: str = Field(..., description="Credential name")
    protocol: str = Field(..., description="Protocol identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    status: str = Field(..., description="Operation status")

class CredentialListResponse(BaseModel):
    """Response for credential listing"""
    model_config = ConfigDict(extra="forbid")
    
    credentials: List[Dict[str, Any]] = Field(..., description="List of credentials")
    total: int = Field(..., description="Total number of credentials")
