# Azure Cosmos DB repository for notification CRUD operations
from azure.cosmos.aio import DatabaseProxy
from app.models.notification import Notification
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Repository for managing notifications with Azure Cosmos DB"""
    
    def __init__(self, db: DatabaseProxy):
        self.db = db
        self.container = db.get_container_client("notifications")
    
    async def create_notification(
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
            user_id=user_id or "system"  # Default partition key
        )
        notification_dict = notification.model_dump(mode='json')
        
        await self.container.create_item(body=notification_dict)
        
        return notification
    
    async def get_all_notifications(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Notification]:
        """Get all notifications, optionally filtered by user"""
        if user_id:
            query = f"SELECT TOP @limit * FROM c WHERE c.user_id = @user_id ORDER BY c.created_at DESC"
            parameters = [
                {"name": "@user_id", "value": user_id},
                {"name": "@limit", "value": limit}
            ]
            notifications = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters,
                partition_key=user_id
            ):
                notifications.append(Notification(**item))
        else:
            query = f"SELECT TOP @limit * FROM c ORDER BY c.created_at DESC"
            parameters = [{"name": "@limit", "value": limit}]
            notifications = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ):
                notifications.append(Notification(**item))
        
        return notifications
    
    async def get_notification(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        try:
            item = await self.container.read_item(
                item=notification_id,
                partition_key=user_id
            )
            return Notification(**item)
        except Exception as e:
            logger.error(f"Error getting notification {notification_id}: {str(e)}")
            return None
    
    async def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        """Mark notification as read"""
        try:
            # Query to find the notification (needs cross-partition since we don't have user_id)
            query = "SELECT * FROM c WHERE c.id = @id"
            parameters = [{"name": "@id", "value": notification_id}]
            
            async for item in self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ):
                notification = Notification(**item)
                notification.read = True
                notification.updated_at = datetime.utcnow()
                notification_dict = notification.model_dump(mode='json')
                
                await self.container.replace_item(
                    item=item["id"],
                    body=notification_dict,
                    partition_key=item["user_id"]
                )
                
                return notification
            
            return None
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
            return None
    
    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        try:
            await self.container.delete_item(
                item=notification_id,
                partition_key=user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting notification {notification_id}: {str(e)}")
            return False
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        query = "SELECT VALUE COUNT(1) FROM c WHERE c.user_id = @user_id AND c.read = false"
        parameters = [{"name": "@user_id", "value": user_id}]
        
        async for item in self.container.query_items(
            query=query,
            parameters=parameters,
            partition_key=user_id
        ):
            return item
        
        return 0

