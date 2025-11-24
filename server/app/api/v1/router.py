# Main API router
# app/api/v1/router.py

from fastapi import APIRouter
from app.api.v1.endpoints import chat, notifications, webhooks, users

api_router = APIRouter()

# Include chat endpoints
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

# Include notification endpoints
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"]
)

# Include user endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# webhooks endpoints
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

@api_router.get("/")
async def root():
    return {"message": "Welcome to Civi Chat API v1"}