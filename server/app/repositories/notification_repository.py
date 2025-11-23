# Repository for notification CRUD operations
from sqlalchemy.orm import Session
from app.models.notification import Notification
from typing import List, Optional
from datetime import datetime


class NotificationRepository:
    """Repository for managing notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        title: str,
        message: str,
        type: str = "info",
        user_id: Optional[str] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            title=title,
            message=message,
            type=type,
            user_id=user_id
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def get_all_notifications(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Notification]:
        """Get all notifications, optionally filtered by user"""
        query = self.db.query(Notification)
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.read = True
            notification.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        return notification