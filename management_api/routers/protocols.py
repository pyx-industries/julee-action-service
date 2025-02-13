"""Protocol and behavior management endpoints"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from ...log_utils import ActionServiceLogger
from ...types import RepoSet
from ...domain import Protocol, ActionType
from ..settings import get_reposet

router = APIRouter(tags=["protocols"])
logger = ActionServiceLogger(debug_mode=True)

@router.get("/protocols/", response_model=List[Protocol])
async def list_protocols(
    reposet: RepoSet = Depends(get_reposet)
):
    """List available protocols"""
    try:
        return reposet["behaviour_repository"].get_protocols()
    except Exception as e:
        logger.error(f"Failed to list protocols: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/protocols/{protocol_id}", response_model=Protocol)
async def get_protocol(
    protocol_id: str,
    reposet: RepoSet = Depends(get_reposet)
):
    """Get protocol details"""
    try:
        protocol = reposet["behaviour_repository"].get_protocol(protocol_id)
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")
        return protocol
    except Exception as e:
        logger.error(f"Failed to get protocol: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/action-types/", response_model=List[ActionType])
async def list_action_types(
    reposet: RepoSet = Depends(get_reposet)
):
    """List available action types"""
    try:
        return reposet["behaviour_repository"].get_action_types()
    except Exception as e:
        logger.error(f"Failed to list action types: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
