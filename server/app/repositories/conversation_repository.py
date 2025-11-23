# Repository for conversation and message CRUD operations
from sqlalchemy.orm import Session
from app.models.conversation import Conversation, Message
from typing import List, Optional
from datetime import datetime
import uuid


class ConversationRepository:
    """Repository for managing conversations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(self, user_id: Optional[str] = None) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        citations: Optional[List[dict]] = None
    ) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations=citations,
            timestamp=datetime.utcnow()
        )
        self.db.add(message)
        
        # Update conversation updated_at
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation ordered by timestamp"""
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
            .all()
        )
    
    def get_conversation_with_messages(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation with all messages"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            # SQLAlchemy will automatically load messages due to relationship
            return conversation
        return None