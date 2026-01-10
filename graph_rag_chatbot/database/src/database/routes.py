import json
from typing import AsyncGenerator

from database.dependencies import get_llm, get_graph
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from langchain_neo4j import GraphCypherQAChain

from interfaces.models import DatabaseChatRequest, StreamChunk
from interfaces.endpoints import APIEndpoints

router = APIRouter()


async def generate_stream_response(
    msg: DatabaseChatRequest, graph, llm
) -> AsyncGenerator[str, None]:
    """
    Generate streaming response chunks.
    This is a placeholder - will be replaced with actual database/LLM call.
    """
    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        allow_dangerous_requests=True,
        verbose=True,  # Enable verbose mode to see the generated query
    )
    chain = llm

    # Use astream() for streaming responses instead of ainvoke()
    response_stream = chain.astream(msg.query.content)  # testing purposes

    async for chunk in response_stream:
        print("Generated chunk:", chunk)
        stream_chunk = StreamChunk(content=chunk.content, done=False)
        yield f"data: {json.dumps(stream_chunk.model_dump())}\n\n"

    # Send final chunk
    final_chunk = StreamChunk(content="", done=True)
    yield f"data: {json.dumps(final_chunk.model_dump())}\n\n"


@router.post(APIEndpoints.DATABASE_CHAT_STREAM)
async def chat_stream(
    request: Request,
    database_request: DatabaseChatRequest,
    graph=Depends(get_graph),
    llm=Depends(get_llm),
) -> StreamingResponse:
    """
    Handle streaming chat requests.
    """
    print("Received database chat stream request:", database_request)
    return StreamingResponse(
        generate_stream_response(database_request, graph, llm),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint - no auth required."""
    return {"status": "healthy"}
