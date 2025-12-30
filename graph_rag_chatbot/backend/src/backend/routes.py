import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

import httpx
from interfaces.models import ChatRequest, ChatResponse, StreamChunk, DatabaseChatRequest, ChatMessage, MessageRole
from interfaces.endpoints import APIEndpoints

from backend.auth import verify_api_key
from backend.rate_limiter import rate_limiter
from backend.conversation_history import conversation_history
from backend.config import get_settings

router = APIRouter()

async def check_rate_limit(request: Request):
    """Dependency to check rate limit."""
    await rate_limiter.check_rate_limit(request)
    return rate_limiter.get_remaining_requests()


async def generate_stream_response(message: str, conversation_id: str) -> AsyncGenerator[str, None]:
    """
    Generate streaming response chunks.
    This is a placeholder - will be replaced with actual database/LLM call.
    """
    previous_messages = conversation_history.get_history(conversation_id)
    conversation_history.add_message(
        conversation_id,
        ChatMessage(role=MessageRole.USER, content=message),
    )
    request = DatabaseChatRequest(
            query=ChatMessage(role=MessageRole.USER, content=message),
            history=previous_messages,
        )
        
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{get_settings().database_url}{APIEndpoints.DATABASE_PREFIX}{APIEndpoints.DATABASE_CHAT_STREAM}",
            json=request.model_dump(),
            headers={"X-API-Key": get_settings().database_api_key},
            timeout=60.0,
        ) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                stream_chunk = StreamChunk(
                    content=f"Error: {response.status_code} - {error_text.decode()}",
                    done=True,
                    error=None,
                )
                yield f"data: {json.dumps(stream_chunk.model_dump())}\n\n"
                return
            
            full_message = ""
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    chunk = StreamChunk(**data)
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"
                    if chunk.content:
                        full_message += chunk.content
            # Update conversation history with assistant's response
            conversation_history.add_message(
                conversation_id,
                ChatMessage(role=MessageRole.ASSISTANT, content=full_message),
            )
            
    

@router.post(APIEndpoints.BACKEND_CHAT, response_model=ChatResponse)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    api_key: str = Depends(verify_api_key),
    rate_limit: int = Depends(check_rate_limit),
) -> ChatResponse:
    """
    Handle non-streaming chat requests.
    
    Authorization and rate limiting are applied before processing.
    Will query database in the next step.
    """
    conversation_id = chat_request.conversation_id or str(uuid.uuid4())
    
    # Placeholder response - will be replaced with database query
    response_message = f"Received: {chat_request.message}. Database integration coming soon!"
    
    return ChatResponse(
        message=ChatMessage(role=MessageRole.ASSISTANT, content=response_message),
        conversation_id=conversation_id,
        sources=None,  # Will be populated from database
    )


@router.post(APIEndpoints.BACKEND_CHAT_STREAM)
async def chat_stream(
    request: Request,
    chat_request: ChatRequest,
    api_key: str = Depends(verify_api_key),
    rate_limit: int = Depends(check_rate_limit),
) -> StreamingResponse: 
    """
    Handle streaming chat requests.
    
    Authorization and rate limiting are applied before processing.
    Returns Server-Sent Events (SSE) stream.
    """
    conversation_id = chat_request.conversation_id or str(uuid.uuid4())
    
    return StreamingResponse(
        generate_stream_response(chat_request.message.content, conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-ID": conversation_id,
        },
    )


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint - no auth required."""
    return {"status": "healthy"}

