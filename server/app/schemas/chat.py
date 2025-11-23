# Chat request/response schemas
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    """Message role enum matching frontend"""
    USER = "user"
    ASSISTANT = "model"


class CitationSchema(BaseModel):
    """Citation/Source schema"""
    id: str
    title: str
    uri: str
    type: Optional[str] = None  # PDF, Web, etc.
    size: Optional[str] = None


class MessageSchema(BaseModel):
    """Message schema matching frontend Message interface"""
    id: str
    role: Role
    content: str
    timestamp: datetime
    citations: Optional[List[CitationSchema]] = None
    isThinking: Optional[bool] = False
    
    class Config:
        from_attributes = True


class ChatMessageRequest(BaseModel):
    """Request to send a new chat message"""
    content: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None  # If None, create new conversation


class ChatMessageResponse(BaseModel):
    """Response after sending a chat message"""
    user_message: MessageSchema
    assistant_message: MessageSchema
    conversation_id: str


class ConversationHistoryResponse(BaseModel):
    """Response for conversation history"""
    conversation_id: str
    messages: List[MessageSchema]
    created_at: datetime
    updated_at: datetime