"""
Pydantic models for agent metadata.
"""

from typing import Optional, Any

from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """Input parameter for an agent."""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None


class AgentOutput(BaseModel):
    """Output produced by an agent."""
    name: str
    type: str
    description: Optional[str] = None


class AgentExample(BaseModel):
    """Example use case for an agent."""
    title: str
    description: Optional[str] = None
    input: Optional[dict[str, Any]] = None
    expected_output: Optional[str] = None


class AgentConstraints(BaseModel):
    """Safety and operational constraints."""
    read_only: bool = False
    human_approval_required: bool = False
    max_execution_time: Optional[int] = None


class AgentRequirements(BaseModel):
    """Runtime requirements."""
    python_version: Optional[str] = None
    env_vars: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class AgentSummary(BaseModel):
    """
    Summary view of an agent for marketplace listing.
    
    Contains only the fields needed for card display.
    """
    id: str
    name: str
    description: str
    version: str
    category: Optional[str] = None
    icon: Optional[str] = None
    status: str = "stable"
    tags: list[str] = Field(default_factory=list)


class AgentDetail(BaseModel):
    """
    Full agent details for the agent detail page.
    
    Includes all metadata from agent.yaml.
    """
    id: str
    name: str
    description: str
    long_description: Optional[str] = None
    version: str
    author: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    status: str = "stable"
    visibility: str = "public"
    tags: list[str] = Field(default_factory=list)
    inputs: list[AgentInput] = Field(default_factory=list)
    outputs: list[AgentOutput] = Field(default_factory=list)
    examples: list[AgentExample] = Field(default_factory=list)
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None
    constraints: Optional[AgentConstraints] = None
    requirements: Optional[AgentRequirements] = None


class AgentListResponse(BaseModel):
    """Response for agent listing endpoint."""
    agents: list[AgentSummary]
    total: int
