"""Public API for webhook handling"""
import asyncio
from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.encoders import jsonable_encoder
from datetime import datetime, UTC
from typing import Dict, Optional
from json.decoder import JSONDecodeError

from ..log_utils import ActionServiceLogger, log_execution_time

def normalize_content_type(content_type: str) -> str:
    """Extract base content type without parameters"""
    return content_type.split(';')[0].strip().lower()

from ..types import RepoSet

from ..interfaces.requests import WebhookRequest, ActionCallbackRequest
from ..interfaces.responses import (
    WebhookAcceptedResponse,
    WebhookStatusResponse,
    WebhookErrorResponse
)
from ..usecases.webhooks import ReceiveWebhook, GetWebhookStatus
from .settings import get_reposet

app = FastAPI(title="Action Service Public API")
logger = ActionServiceLogger(debug_mode=True)  # Configure via environment/settings
 
@app.post(
    "/webhooks/{webhook_id}",
    response_model=WebhookAcceptedResponse,
    responses={
        401: {"model": WebhookErrorResponse},
        400: {"model": WebhookErrorResponse}
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "additionalProperties": True
                    },
                    "example": {"key": "value"}
                },
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "file": {
                                "type": "string",
                                "format": "binary"
                            }
                        }
                    }
                },
                "application/octet-stream": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            }
        }
    }
)
@log_execution_time(logger)
async def receive_webhook(
    webhook_id: str,
    request: Request,
    key: str,
    x_correlation_id: Optional[str] = Header(None),
    content_type: str = Header("application/json"),
    reposet: RepoSet = Depends(get_reposet)
) -> WebhookAcceptedResponse:
    """
    Handle incoming webhook with support for:
    - JSON payloads (application/json)
    - File uploads (multipart/form-data) 
    - Raw data (application/octet-stream)
    
    Parameters:
        webhook_id: Unique identifier for the webhook
        key: Authentication key for the webhook
        x_correlation_id: Optional correlation ID for request tracking
        content_type: Content type of the payload (json, form-data, or octet-stream)
    """
    logger.debug(
        f"Processing webhook {webhook_id}",
        correlation_id=x_correlation_id
    )

    try:
        # Normalize content type
        content_type = normalize_content_type(content_type)
        headers = dict(request.headers)

        # Handle different content types
        if content_type == "application/json":
            try:
                data = await request.json()
            except JSONDecodeError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid JSON payload"
                )
            webhook_request = WebhookRequest(
                payload=data,
                headers=headers,
                content_type=content_type,
                correlation_id=x_correlation_id
            )
        elif content_type == "multipart/form-data":
            form = await request.form()
            file = form.get("file")
            if file:
                data = await file.read()
                webhook_request = WebhookRequest(
                    raw_data=data,
                    headers=dict(request.headers),
                    content_type=content_type,
                    metadata={"filename": file.filename},
                    correlation_id=x_correlation_id
                )
            else:
                raise HTTPException(status_code=400, detail="No file found in form data")
        else:
            # Handle raw data
            data = await request.body()
            webhook_request = WebhookRequest(
                raw_data=data,
                headers=dict(request.headers),
                content_type=content_type,
                correlation_id=x_correlation_id
            )

        logger.debug(
            f"Processed webhook data of type {content_type}",
            correlation_id=x_correlation_id
        )
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", correlation_id=x_correlation_id)
        raise
   
    # Execute synchronous usecase
    usecase = ReceiveWebhook(reposet)
    result = usecase.execute(webhook_id, key, webhook_request)
    
    if not result:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid webhook ID or key"}
        )
    
    return WebhookAcceptedResponse(
        response_id=result.response_id,
        status="accepted",
        correlation_id=x_correlation_id,
        timestamp=datetime.now(UTC)
    )

@app.get("/status/{response_id}", response_model=WebhookStatusResponse)
async def get_status(
    response_id: str,
    x_correlation_id: Optional[str] = Header(None),
    reposet: RepoSet = Depends(get_reposet)
) -> WebhookStatusResponse:
    """Get webhook processing status"""
    try:
        # Execute synchronous usecase
        usecase = GetWebhookStatus(reposet)
        return usecase.execute(response_id)
        
    except ValueError as e:
        logger.error(f"Status lookup failed: {str(e)}", correlation_id=x_correlation_id)
        raise HTTPException(
            status_code=404,
            detail=f"Response ID not found: {response_id}"
        )
    except Exception as e:
        logger.error(f"Status check error: {str(e)}", correlation_id=x_correlation_id, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error checking status"
        )

@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Convert exceptions to WebhookErrorResponse format"""
    error_response = WebhookErrorResponse(
        error="validation_error" if exc.status_code == 400 else "server_error",
        message=exc.detail,
        timestamp=datetime.now(UTC)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response.model_dump())
    )
