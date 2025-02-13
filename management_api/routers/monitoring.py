"""Event monitoring and result tracking endpoints"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from ...log_utils import ActionServiceLogger
from ...types import RepoSet
from ...domain import Event, ActionResult
from ..settings import get_reposet

router = APIRouter(tags=["monitoring"])
logger = ActionServiceLogger(debug_mode=True)

@router.get("/events/", response_model=List[Event])
async def list_events(
    action_id: Optional[str] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    reposet: RepoSet = Depends(get_reposet)
):
    """List events with filters"""
    try:
        return reposet["event_repository"].list_events(
            action_id=action_id,
            status=status,
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        logger.error(f"Failed to list events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}/status", response_model=str)
async def get_event_status(
    event_id: str,
    reposet: RepoSet = Depends(get_reposet)
):
    """Get event status"""
    try:
        status = reposet["event_repository"].get_status(event_id)
        if not status:
            raise HTTPException(status_code=404, detail="Event not found")
        return status
    except Exception as e:
        logger.error(f"Failed to get event status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{action_id}", response_model=List[ActionResult])
async def get_action_results(
    action_id: str,
    success: Optional[bool] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    reposet: RepoSet = Depends(get_reposet)
):
    """Get results for an action"""
    try:
        return reposet["result_repository"].list_results(
            action_id=action_id,
            success=success,
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        logger.error(f"Failed to get results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
