# Azure Cosmos DB repository for user CRUD operations
from azure.cosmos.aio import DatabaseProxy
from app.models.user import User
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for managing users with Azure Cosmos DB"""
    
    def __init__(self, db: DatabaseProxy):
        self.db = db
        self.container = db.get_container_client("users")
    
    async def create_user(
        self,
        email: str,
        full_name: Optional[str] = None,
        hashed_password: Optional[str] = None
    ) -> User:
        """Create a new user"""
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password
        )
        user_dict = user.model_dump(mode='json')
        
        await self.container.create_item(body=user_dict)
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            item = await self.container.read_item(
                item=user_id,
                partition_key=user_id
            )
            return User(**item)
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            query = "SELECT * FROM c WHERE c.email = @email"
            parameters = [{"name": "@email", "value": email}]
            
            async for item in self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ):
                return User(**item)
            
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update user information"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None
            
            update_data["updated_at"] = datetime.utcnow()
            user_dict = user.model_dump(mode='json')
            user_dict.update(update_data)
            
            await self.container.replace_item(
                item=user_id,
                body=user_dict,
                partition_key=user_id
            )
            
            return User(**user_dict)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return None
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.last_login = datetime.utcnow()
            user_dict = user.model_dump(mode='json')
            
            await self.container.replace_item(
                item=user_id,
                body=user_dict,
                partition_key=user_id
            )
            
            return True
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {str(e)}")
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            await self.container.delete_item(
                item=user_id,
                partition_key=user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            return False
    
    async def get_all_users(self, limit: int = 100, skip: int = 0) -> List[User]:
        """Get all users with pagination"""
        query = f"SELECT * FROM c OFFSET @skip LIMIT @limit"
        parameters = [
            {"name": "@skip", "value": skip},
            {"name": "@limit", "value": limit}
        ]
        
        users = []
        async for item in self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ):
            users.append(User(**item))
        
        return users
    
    async def count_users(self) -> int:
        """Get total count of users"""
        query = "SELECT VALUE COUNT(1) FROM c"
        
        async for item in self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ):
            return item
        
        return 0

