from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: ChatMessage
    conversation_id: Optional[str] = None
    stream: bool = True


class DatabaseChatRequest(BaseModel):
    query: ChatMessage
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    message: ChatMessage
    conversation_id: str
    sources: Optional[List[str]] = None


class StreamChunk(BaseModel):
    content: str
    done: bool = False
    error: Optional[str] = None
