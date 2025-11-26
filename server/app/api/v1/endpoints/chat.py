# Conversational endpoints
from fastapi import APIRouter, Depends, HTTPException
from azure.cosmos.aio import DatabaseProxy
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationHistoryResponse,
    MessageSchema,
    CitationSchema,
    Role
)
from app.services.azure_ai_service import AzureOpenAIService
from app.services.search_service import SearchService
from app.repositories.conversation_repository import ConversationRepository
from app.db.mongodb import get_database
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    db: DatabaseProxy = Depends(get_database)
):
    """
    Send a chat message and get AI response with citations
    """
    try:
        # Initialize services
        ai_service = AzureOpenAIService()
        search_service = SearchService()
        conversation_repo = ConversationRepository(db)
        
        # Get or create conversation
        # Handle empty strings, "null" literals, and None
        conversation_id = request.conversation_id
        if conversation_id and conversation_id.strip() and conversation_id.lower() != "null":
            conversation = await conversation_repo.get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = await conversation_repo.create_conversation()
        
        # Save user message
        logger.info(f"Saving user message for conversation {conversation.id}")
        user_message = await conversation_repo.add_message(
            conversation_id=conversation.id,
            role=Role.USER.value,
            content=request.content
        )
        logger.info(f"User message saved: {user_message.id}")
        
        # Search for relevant documents
        logger.info("Searching for relevant documents...")
        documents = await search_service.search_documents(request.content)
        citations = search_service.create_citations(documents)
        logger.info(f"Found {len(citations)} citations")
        
        # Get conversation history for context
        logger.info("Getting conversation history...")
        previous_messages = await conversation_repo.get_conversation_messages(conversation.id)
        message_history = [
            {"role": msg.role, "content": msg.content}
            for msg in previous_messages[:-1]  # Exclude the just-added user message
        ]
        message_history.append({"role": "user", "content": request.content})
        logger.info(f"Message history has {len(message_history)} messages")
        
        # Get AI response with context
        logger.info("Getting AI response...")
        ai_response = await ai_service.get_chat_completion(
            messages=message_history,
            context_documents=documents
        )
        logger.info(f"AI response received: {ai_response[:100]}...")
        
        # Save assistant message with citations
        logger.info("Saving assistant message...")
        assistant_message = await conversation_repo.add_message(
            conversation_id=conversation.id,
            role=Role.ASSISTANT.value,
            content=ai_response,
            citations=citations
        )
        logger.info(f"Assistant message saved: {assistant_message.id}")
        
        # Convert to response schemas
        user_msg_schema = MessageSchema(
            id=user_message.id,
            role=Role(user_message.role),
            content=user_message.content,
            timestamp=user_message.timestamp,
            citations=None,
            isThinking=False
        )
        
        assistant_msg_schema = MessageSchema(
            id=assistant_message.id,
            role=Role(assistant_message.role),
            content=assistant_message.content,
            timestamp=assistant_message.timestamp,
            citations=[CitationSchema(**c) for c in citations] if citations else None,
            isThinking=False
        )
        
        return ChatMessageResponse(
            user_message=user_msg_schema,
            assistant_message=assistant_msg_schema,
            conversation_id=conversation.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/history/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    db: DatabaseProxy = Depends(get_database)
):
    """
    Get conversation history with all messages
    """
    try:
        logger.info(f"Getting history for conversation: {conversation_id}")
        conversation_repo = ConversationRepository(db)
        result = await conversation_repo.get_conversation_with_messages(conversation_id)
        
        logger.info(f"Result: {result is not None}")
        if not result:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation = result["conversation"]
        messages = result["messages"]
        
        # Convert messages to schemas
        message_schemas = []
        for msg in messages:
            citations = None
            if msg.citations:
                citations = [CitationSchema(**c) for c in msg.citations]
            
            message_schemas.append(MessageSchema(
                id=msg.id,
                role=Role(msg.role),
                content=msg.content,
                timestamp=msg.timestamp,
                citations=citations,
                isThinking=False
            ))
        
        return ConversationHistoryResponse(
            conversation_id=conversation.id,
            messages=message_schemas,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")