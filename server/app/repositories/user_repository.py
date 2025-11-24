# app/repositories/user_repository.py
from typing import Optional
from app.models.user import User
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, container=None):
        super().__init__("users", User, container=container)

    def get_user_by_email(self, email: str) -> Optional[User]:
        query = "SELECT * FROM c WHERE c.email = @email"
        parameters = [{"name": "@email", "value": email}]
        users = self.query(query, parameters)
        return users[0] if users else None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.get(user_id, user_id)

    def create_user(self, user: User) -> User:
        return self.create(user)
