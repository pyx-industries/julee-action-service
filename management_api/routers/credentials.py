"""Credential management endpoints"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from ...log_utils import ActionServiceLogger
from ...types import RepoSet
from ...domain import Credential
from ..settings import get_reposet

router = APIRouter(prefix="/credentials", tags=["credentials"])
logger = ActionServiceLogger(debug_mode=True)

@router.post("/", response_model=Credential)
async def create_credential(
    name: str,
    protocol: str,
    secrets: dict,
    reposet: RepoSet = Depends(get_reposet)
):
    """Store new credentials"""
    try:
        protocol_obj = reposet["behaviour_repository"].get_protocol(protocol)
        if not protocol_obj:
            raise HTTPException(status_code=400, detail="Invalid protocol")
            
        return reposet["credential_repository"].store_credential(
            name=name,
            protocol=protocol_obj,
            secrets=secrets
        )
    except Exception as e:
        logger.error(f"Failed to store credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{credential_id}", response_model=Credential)
async def get_credential(
    credential_id: str,
    reposet: RepoSet = Depends(get_reposet)
):
    """Get credential details"""
    try:
        cred = reposet["credential_repository"].get_credential(credential_id)
        if not cred:
            raise HTTPException(status_code=404, detail="Credential not found")
        return cred
    except Exception as e:
        logger.error(f"Failed to get credential: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Credential])
async def list_credentials(
    protocol: Optional[str] = None,
    reposet: RepoSet = Depends(get_reposet)
):
    """List credentials with optional protocol filter"""
    try:
        protocol_obj = None
        if protocol:
            protocol_obj = reposet.behaviour_repo.get_protocol(protocol)
            if not protocol_obj:
                raise HTTPException(status_code=400, detail="Invalid protocol")
                
        return reposet["credential_repository"].list_credentials(protocol=protocol_obj)
    except Exception as e:
        logger.error(f"Failed to list credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
