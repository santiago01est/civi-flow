# app/repositories/conversation_repository.py
from typing import List, Optional
from app.models.conversation import Conversation, Message
from app.repositories.base_repository import BaseRepository
from datetime import datetime

class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, container=None):
        super().__init__("conversations", Conversation, container=container)

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self.get(conversation_id, conversation_id)

    def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Conversation:
        conversation = Conversation(id=conversation_id, user_id=user_id, messages=[])
        return self.create(conversation)

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        citations: Optional[List[dict]] = None
    ) -> Optional[Conversation]:
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        message = Message(
            role=role,
            content=content,
            citations=citations,
            timestamp=datetime.utcnow()
        )
        conversation.messages.append(message)
        conversation.updated_at = datetime.utcnow()
        
        return self.update(conversation.id, conversation.id, conversation.dict())

    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        conversation = self.get_conversation(conversation_id)
        return conversation.messages if conversation else []

    def get_conversation_with_messages(self, conversation_id: str) -> Optional[Conversation]:
        return self.get_conversation(conversation_id)