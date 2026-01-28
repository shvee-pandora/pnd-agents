"""
Pydantic models for agent metadata.

These models match the canonical schema defined in schemas/agent.schema.yaml.
"""

from typing import Optional, Any

from pydantic import BaseModel, Field


class AgentOwner(BaseModel):
    """Owner information for an agent."""
    team: str
    contact: Optional[str] = None


class AgentEntrypoint(BaseModel):
    """Execution entrypoint for an agent."""
    type: str  # python, node, shell
    command: str


class AgentInput(BaseModel):
    """Input parameter for an agent."""
    name: str
    type: str  # string, number, boolean, repo, branch, file, json
    required: bool
    description: Optional[str] = None
    default: Optional[Any] = None


class AgentOutput(BaseModel):
    """Output produced by an agent."""
    type: str  # site, json, markdown, text, pr, report
    path: Optional[str] = None
    description: Optional[str] = None


class AgentDependencies(BaseModel):
    """Runtime dependencies for an agent."""
    python: list[str] = Field(default_factory=list)
    node: list[str] = Field(default_factory=list)


class AgentSummary(BaseModel):
    """
    Summary view of an agent for marketplace listing.
    
    Contains only the fields needed for card display.
    """
    id: str
    name: str
    description: str
    category: str
    maturity: str
    icon: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    version: str = "0.1.0"


class AgentDetail(BaseModel):
    """
    Full agent details for the agent detail page.
    
    Matches the canonical schema in schemas/agent.schema.yaml.
    """
    # Required fields
    id: str
    name: str
    description: str
    category: str
    maturity: str
    owner: AgentOwner
    entrypoint: AgentEntrypoint
    
    # Optional fields
    subCategory: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    visibility: str = "internal"
    inputs: list[AgentInput] = Field(default_factory=list)
    outputs: list[AgentOutput] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    dependencies: Optional[AgentDependencies] = None
    installable: bool = True
    version: str = "0.1.0"
    icon: Optional[str] = None
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None


class AgentListResponse(BaseModel):
    """Response for agent listing endpoint."""
    agents: list[AgentSummary]
    total: int


class ValidationError(BaseModel):
    """Schema validation error."""
    agent_id: str
    agent_path: str
    errors: list[str]


class ValidationResult(BaseModel):
    """Result of schema validation."""
    valid: bool
    total_agents: int
    valid_agents: int
    errors: list[ValidationError] = Field(default_factory=list)
