# app/models/conversation.py
from typing import List, Optional
from pydantic import Field
from app.db.base import Base
from datetime import datetime

class Message(Base):
    role: str
    content: str
    citations: Optional[List[dict]] = None
    is_thinking: str = "false"

class Conversation(Base):
    user_id: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
