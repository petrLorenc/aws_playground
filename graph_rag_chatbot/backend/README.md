# Backend Service

A FastAPI-based backend service for the Graph RAG Chatbot.

## Features

- **Authorization**: API key-based authentication via `X-API-Key` header
- **Rate Limiting**: Configurable request limits per time window
- **Streaming Responses**: Server-Sent Events (SSE) for chat streaming
- **Shared Interfaces**: Uses the shared `interfaces` module for request/response models

## Quick Start

### Run the server

```bash
cd backend
# handle ports
uv run --env-file .env uvicorn backend.main:app --reload --port 9001
# or load from .env file
uv run --env-file .env python ./src/backend/main.py --reload
```

Or from the workspace root:

```bash
uv run --package backend uvicorn backend.main:app --reload
```

The server will start at `http://localhost:8000`.

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```