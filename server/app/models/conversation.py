# Azure Cosmos DB conversation and message models
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Message(Base):
    role: str
    content: str
    citations: Optional[List[dict]] = None
    is_thinking: str = "false"

class Message(BaseModel):
    """Message model for Cosmos DB"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    role: str  # "user" or "model"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    citations: Optional[List[dict]] = None
    is_thinking: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "id": "msg-123",
                "conversation_id": "conv-456",
                "role": "user",
                "content": "What are the zoning regulations?",
                "timestamp": "2025-11-24T10:00:00Z",
                "citations": None,
                "is_thinking": False
            }
        }


class Conversation(BaseModel):
    """Conversation model for Cosmos DB"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "id": "conv-123",
                "user_id": "user123",
                "created_at": "2025-11-24T10:00:00Z",
                "updated_at": "2025-11-24T10:05:00Z",
                "message_count": 4
            }
        }

