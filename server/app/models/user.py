# Azure Cosmos DB user model
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class User(BaseModel):
    """User model for Cosmos DB"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "id": "user-123",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2025-11-24T10:00:00Z",
                "updated_at": "2025-11-24T10:00:00Z"
            }
        }

