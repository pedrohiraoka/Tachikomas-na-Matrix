"""
Main FastAPI Application - Tachikoma Matrix API.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    # Startup
    logger.info("Tachikoma Matrix API starting up...")
    
    yield
    
    # Shutdown
    logger.info("Tachikoma Matrix API shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Tachikoma Matrix API",
        description="""
        API for the Tachikoma Matrix simulation - a network of AI agents 
        inspired by Ghost in the Shell operating in a Matrix-like environment.
        
        ## Features
        
        * **Tachikoma Units**: Register and manage AI agent units
        * **Experience Tracking**: Record and share experiences between units
        * **Reflection Cycles**: Trigger existential reflection processes
        * **Collective Memory**: Search shared memory using semantic embeddings
        * **Real-time Events**: WebSocket stream for network events
        
        ## Ethics
        
        This is a conceptual experiment. All autonomy and consciousness features
        are simulated for exploration of philosophical concepts.
        """,
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router)
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {"status": "healthy", "service": "tachikoma-matrix-api"}
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict:
        return {
            "message": "Welcome to Tachikoma Matrix API",
            "docs": "/docs",
            "network_live": "/network/live",
        }
    
    logger.info("FastAPI application created successfully")
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
