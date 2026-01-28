"""
Agents API routes.

Provides read-only access to agent metadata from agent.yaml files.
Validates agents against the canonical schema on startup.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..services.agent_discovery import AgentDiscoveryService, SchemaValidationError
from ..models.agent import AgentDetail, AgentListResponse, ValidationResult

router = APIRouter(tags=["agents"])

# Initialize the discovery service (validates agents on startup)
# Set fail_on_validation_error=False to allow API to start even with invalid agents
discovery_service = AgentDiscoveryService(fail_on_validation_error=False)


@router.get("/agents", response_model=AgentListResponse)
async def list_agents(
    category: Optional[str] = Query(None, description="Filter by category"),
    maturity: Optional[str] = Query(None, description="Filter by maturity (alpha, beta, stable, deprecated)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    visibility: Optional[str] = Query(None, description="Filter by visibility (public, internal, private)"),
) -> AgentListResponse:
    """
    List all available agents with optional filtering.
    
    Returns agent summaries suitable for marketplace card display.
    """
    agents = discovery_service.list_agents(
        category=category,
        maturity=maturity,
        tag=tag,
        search=search,
        visibility=visibility,
    )
    return AgentListResponse(
        agents=agents,
        total=len(agents),
    )


@router.get("/agents/{agent_id}", response_model=AgentDetail)
async def get_agent(agent_id: str) -> AgentDetail:
    """
    Get detailed information about a specific agent.
    
    Returns full agent metadata including inputs, outputs, and examples.
    """
    agent = discovery_service.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent


@router.get("/agents/{agent_id}/config")
async def get_agent_runtime_config(agent_id: str):
    """
    Get runtime configuration for an agent.
    
    Merges agent.yaml metadata with mcp-config/agents.config.json runtime settings.
    """
    config = discovery_service.get_agent_runtime_config(agent_id)
    if config is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return config


@router.get("/categories")
async def list_categories():
    """
    List all available agent categories.
    """
    categories = discovery_service.list_categories()
    return {"categories": categories}


@router.get("/tags")
async def list_tags():
    """
    List all available agent tags.
    """
    tags = discovery_service.list_tags()
    return {"tags": tags}


@router.get("/validation", response_model=ValidationResult)
async def get_validation_result() -> ValidationResult:
    """
    Get the schema validation result for all agents.
    
    Returns information about which agents passed/failed validation.
    """
    return discovery_service.get_validation_result()
