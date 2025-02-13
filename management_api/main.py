"""Management API for Action Service"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
import uuid

from .routers import actions, credentials, protocols, monitoring
from ..log_utils import ActionServiceLogger

app = FastAPI(title="Action Service Management API")
logger = ActionServiceLogger(debug_mode=True)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    error_id = str(uuid.uuid4())
    
    # Log the full error details internally
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "error_id": error_id,
            "url": str(request.url),
            "method": request.method,
        }
    )
    
    # Return a sanitized error response
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "reference_id": error_id
            }
        }
    )

# Include routers
app.include_router(actions.router)
app.include_router(credentials.router)
app.include_router(protocols.router)
app.include_router(monitoring.router)

@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")
