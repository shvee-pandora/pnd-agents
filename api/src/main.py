"""
PND Agents Marketplace API

FastAPI application providing read-only access to agent metadata
for the marketplace UI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import agents

app = FastAPI(
    title="PND Agents Marketplace API",
    description="API for discovering and running PND Agents",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pnd-agents-api"}
