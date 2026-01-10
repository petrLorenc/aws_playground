import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv
from neo4j import GraphDatabase, RoutingControl, Driver


from database.config import get_settings
from database.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Setup and teardown logic goes here.
    """
    # Startup, just for loggin purposes, prepared for database connections etc.
    settings = get_settings()
    print(f"Starting {settings.api_title} v{settings.api_version}")
    
    load_dotenv()
    
    # Create connections to database and LLM
    app.state.driver = GraphDatabase.driver(
        os.getenv("GRAPH_DATABASE_URI", "bolt://localhost:7687"),
        auth=(os.getenv("GRAPH_DATABASE_USERNAME", ""), os.getenv("GRAPH_DATABASE_PASSWORD", "")),
    )
    
    app.state.llm = AzureChatOpenAI(
        openai_api_type="azure",
        azure_endpoint=os.getenv("API_BASE_URL"),
        api_version="2024-10-21",
        api_key=SecretStr(secret_value=os.getenv("API_KEY", "")),
        azure_deployment="gpt-5-chat-2025-08-07",
        streaming=True,
    )

    yield
    
    # Shutdown
    print("Shutting down...")
    # Shutdown - close connections
    if hasattr(app.state.graph, "close"):
        app.state.graph.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # CORS middleware for frontend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router)
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=get_settings().port, reload=get_settings().debug) 