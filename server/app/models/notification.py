# app/models/notification.py
from typing import Optional
from app.db.base import Base

class Notification(Base):
    user_id: Optional[str] = None
    title: str
    message: str
    type: str = "info"
    read: bool = False
