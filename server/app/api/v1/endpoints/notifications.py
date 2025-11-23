# User notification preferences
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.notification import (
    NotificationSchema,
    NotificationListResponse,
    NotificationCreateRequest
)
from app.repositories.notification_repository import NotificationRepository
from app.db.session import get_db
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    user_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get all notifications, optionally filtered by user
    """
    try:
        notification_repo = NotificationRepository(db)
        notifications = notification_repo.get_all_notifications(user_id=user_id, limit=limit)
        
        notification_schemas = [
            NotificationSchema.model_validate(notification)
            for notification in notifications
        ]
        
        return NotificationListResponse(
            notifications=notification_schemas,
            total=len(notification_schemas)
        )
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=NotificationSchema)
async def create_notification(
    request: NotificationCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new notification
    """
    try:
        notification_repo = NotificationRepository(db)
        notification = notification_repo.create_notification(
            title=request.title,
            message=request.message,
            type=request.type,
            user_id=request.user_id
        )
        
        return NotificationSchema.model_validate(notification)
        
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/{notification_id}/read", response_model=NotificationSchema)
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    """
    try:
        notification_repo = NotificationRepository(db)
        notification = notification_repo.mark_as_read(notification_id)
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return NotificationSchema.model_validate(notification)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")