"""FastAPI application entry point for TradingAgents WebUI."""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Allow running directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from .config import get_settings
from .routers import providers, analysis, markets, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()
    print(f"Starting {settings.app_name}...")
    yield
    print("Shutting down...")


app = FastAPI(
    title="TradingAgents WebUI API",
    description="Web interface for TradingAgents multi-agent stock analysis system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(markets.router, prefix="/api/markets", tags=["markets"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TradingAgents WebUI API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
