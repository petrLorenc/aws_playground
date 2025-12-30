from dataclasses import dataclass


@dataclass
class APIEndpoints:    
    # Chat endpoints
    BACKEND_CHAT: str = "/chat"
    BACKEND_CHAT_STREAM: str = "/chat/stream"

    # Database endpoints
    DATABASE_CHAT_STREAM: str = "/chat/stream"
