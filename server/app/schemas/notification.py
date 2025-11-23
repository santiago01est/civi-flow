# Notification schemas
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationSchema(BaseModel):
    """Notification schema"""
    id: str
    title: str
    message: str
    type: str = "info"
    read: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationCreateRequest(BaseModel):
    """Request to create a notification"""
    title: str
    message: str
    type: str = "info"
    user_id: Optional[str] = None


class NotificationListResponse(BaseModel):
    """Response for list of notifications"""
    notifications: list[NotificationSchema]
    total: int