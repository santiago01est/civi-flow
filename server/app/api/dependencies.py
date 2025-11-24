"""Shared dependencies for API endpoints.

Provide access to the initialized Cosmos client / containers.
This module expects that `app.db.session.init_cosmos()` was called at app startup.
"""
from typing import Callable
from fastapi import HTTPException
from app.db.session import get_db_client, get_container

def get_cosmos_client():
    client = get_db_client()
    if client is None:
        raise HTTPException(status_code=500, detail="Cosmos DB not initialized")
    return client

def make_container_dep(container_name: str) -> Callable:
    def _get_container():
        try:
            return get_container(container_name)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))
    return _get_container
# Shared dependencies