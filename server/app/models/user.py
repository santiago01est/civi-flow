# app/models/user.py
from typing import Optional
from app.db.base import Base

class User(Base):
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
