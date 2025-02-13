"""Action management endpoints"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from ...log_utils import ActionServiceLogger
from ...types import RepoSet
from ...usecases.actions import (
    CreateAction, ListActions,
    CreateActionRequest, ListActionsRequest,
    ActionResponse, ActionListResponse
)
from ..settings import get_reposet

router = APIRouter(prefix="/actions", tags=["actions"])
logger = ActionServiceLogger(debug_mode=True)

@router.post("/", response_model=ActionResponse)
async def create_action(
    request: CreateActionRequest,
    reposet: RepoSet = Depends(get_reposet)
):
    """Create a new action"""
    usecase = CreateAction(reposet)
    try:
        return usecase.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=ActionListResponse)
async def list_actions(
    action_type: Optional[str] = None,
    protocol: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    reposet: RepoSet = Depends(get_reposet)
):
    """List actions with optional filters"""
    usecase = ListActions(reposet)
    request = ListActionsRequest(
        action_type=action_type,
        protocol=protocol,
        page=page,
        page_size=page_size
    )
    return usecase.execute(request)
