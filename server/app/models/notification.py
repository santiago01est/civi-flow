# Azure Cosmos DB notification model
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Notification(BaseModel):
    """Notification model for Cosmos DB"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    title: str
    message: str
    type: str = "info"  # info, warning, success, error
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "id": "notif-123",
                "user_id": "user123",
                "title": "New Update",
                "message": "City council meeting scheduled",
                "type": "info",
                "read": False,
                "created_at": "2025-11-24T10:00:00Z",
                "updated_at": "2025-11-24T10:00:00Z"
            }
        }

