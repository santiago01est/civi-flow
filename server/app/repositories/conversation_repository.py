# Azure Cosmos DB repository for conversation and message CRUD operations
from azure.cosmos.aio import DatabaseProxy
from app.models.conversation import Conversation, Message
from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Repository for managing conversations with Azure Cosmos DB"""
    
    def __init__(self, db: DatabaseProxy):
        self.db = db
        self.conversations_container = db.get_container_client("conversations")
        self.messages_container = db.get_container_client("messages")
    
    async def create_conversation(self, user_id: Optional[str] = None) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(user_id=user_id)
        conversation_dict = conversation.model_dump(mode='json')
        
        await self.conversations_container.create_item(body=conversation_dict)
        
        return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        try:
            logger.info(f"Looking for conversation: {conversation_id}")
            item = await self.conversations_container.read_item(
                item=conversation_id,
                partition_key=conversation_id
            )
            logger.info(f"Conversation found: {item.get('id')}")
            return Conversation(**item)
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {str(e)}")
            return None
    
    async def add_message(
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
        message_dict = message.model_dump(mode='json')
        
        await self.messages_container.create_item(body=message_dict)
        
        # Update conversation updated_at and message_count
        try:
            conv = await self.get_conversation(conversation_id)
            if conv:
                conv.updated_at = datetime.utcnow()
                conv.message_count += 1
                await self.conversations_container.replace_item(
                    item=conversation_id,
                    body=conv.model_dump(mode='json'),
                    partition_key=conversation_id
                )
        except Exception as e:
            logger.warning(f"Could not update conversation {conversation_id}: {str(e)}")
        
        return message
    
    async def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation ordered by timestamp"""
        query = f"SELECT * FROM c WHERE c.conversation_id = @conversation_id ORDER BY c.timestamp ASC"
        parameters = [{"name": "@conversation_id", "value": conversation_id}]
        
        messages = []
        async for item in self.messages_container.query_items(
            query=query,
            parameters=parameters,
            partition_key=conversation_id
        ):
            messages.append(Message(**item))
        
        return messages
    
    async def get_conversation_with_messages(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation with all messages"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        messages = await self.get_conversation_messages(conversation_id)
        
        return {
            "conversation": conversation,
            "messages": messages
        }
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        try:
            # Delete all messages
            query = f"SELECT * FROM c WHERE c.conversation_id = @conversation_id"
            parameters = [{"name": "@conversation_id", "value": conversation_id}]
            
            async for item in self.messages_container.query_items(
                query=query,
                parameters=parameters,
                partition_key=conversation_id
            ):
                await self.messages_container.delete_item(
                    item=item["id"],
                    partition_key=item["conversation_id"]
                )
            
            # Delete conversation
            await self.conversations_container.delete_item(
                item=conversation_id,
                partition_key=conversation_id
            )
            
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
            return False
    
    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user"""
        query = f"SELECT TOP @limit * FROM c WHERE c.user_id = @user_id ORDER BY c.updated_at DESC"
        parameters = [
            {"name": "@user_id", "value": user_id},
            {"name": "@limit", "value": limit}
        ]
        
        conversations = []
        async for item in self.conversations_container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ):
            conversations.append(Conversation(**item))
        
        return conversations

