# app/repositories/notification_repository.py
from typing import List, Optional
from app.models.notification import Notification
from app.repositories.base_repository import BaseRepository

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self):
        super().__init__("notifications", Notification)

    def create_notification(
        self,
        title: str,
        message: str,
        type: str = "info",
        user_id: Optional[str] = None
    ) -> Notification:
        notification = Notification(
            title=title,
            message=message,
            type=type,
            user_id=user_id,
            read=False
        )
        return self.create(notification)

    def get_all_notifications(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Notification]:
        if user_id:
            query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.created_at DESC OFFSET 0 LIMIT @limit"
            parameters = [
                {"name": "@user_id", "value": user_id},
                {"name": "@limit", "value": limit}
            ]
        else:
            query = "SELECT * FROM c ORDER BY c.created_at DESC OFFSET 0 LIMIT @limit"
            parameters = [{"name": "@limit", "value": limit}]
        
        return self.query(query, parameters)

    def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        notification = self.get(notification_id, notification_id)
        if notification:
            notification.read = True
            return self.update(notification_id, notification_id, notification.dict())
        return None
