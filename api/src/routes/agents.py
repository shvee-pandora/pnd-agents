"""
Agents API routes.

Provides read-only access to agent metadata from agent.yaml files.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..services.agent_discovery import AgentDiscoveryService
from ..models.agent import AgentSummary, AgentDetail, AgentListResponse

router = APIRouter(tags=["agents"])

# Initialize the discovery service
discovery_service = AgentDiscoveryService()


@router.get("/agents", response_model=AgentListResponse)
async def list_agents(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (stable, beta, experimental)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in name and description"),
) -> AgentListResponse:
    """
    List all available agents with optional filtering.
    
    Returns agent summaries suitable for marketplace card display.
    """
    agents = discovery_service.list_agents(
        category=category,
        status=status,
        tag=tag,
        search=search,
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
