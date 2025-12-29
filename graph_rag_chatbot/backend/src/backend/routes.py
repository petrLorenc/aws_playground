import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from interfaces.models import ChatRequest, ChatResponse, StreamChunk
from interfaces.endpoints import APIEndpoints

from backend.auth import verify_api_key
from backend.rate_limiter import rate_limiter

router = APIRouter(prefix=APIEndpoints.BACKEND_PREFIX)


async def check_rate_limit(request: Request):
    """Dependency to check rate limit."""
    await rate_limiter.check_rate_limit(request)
    return rate_limiter.get_remaining_requests()


async def generate_stream_response(message: str, conversation_id: str) -> AsyncGenerator[str, None]:
    """
    Generate streaming response chunks.
    This is a placeholder - will be replaced with actual database/LLM call.
    """
    import asyncio
    import json
    
    # Placeholder response chunks - will be replaced with database query results
    chunks = [
        "I received your message: ",
        f'"{message}". ',
        "This response will be powered by the database in the next step. ",
        "Stay tuned!"
    ]
    
    for chunk in chunks:
        await asyncio.sleep(0.1)  # Simulate processing delay
        stream_chunk = StreamChunk(content=chunk, done=False)
        yield f"data: {json.dumps(stream_chunk.model_dump())}\n\n"
    
    # Send final chunk
    final_chunk = StreamChunk(content="", done=True)
    yield f"data: {json.dumps(final_chunk.model_dump())}\n\n"


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
        message=response_message,
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
        generate_stream_response(chat_request.message, conversation_id),
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

