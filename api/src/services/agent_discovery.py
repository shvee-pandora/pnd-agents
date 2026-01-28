"""
Agent Discovery Service.

Scans the src/agents directory for agent.yaml files and provides
methods to query and filter agents.
"""

import json
from pathlib import Path
from typing import Optional

import yaml

from ..models.agent import (
    AgentSummary,
    AgentDetail,
    AgentInput,
    AgentOutput,
    AgentExample,
    AgentConstraints,
    AgentRequirements,
)


class AgentDiscoveryService:
    """
    Service for discovering and querying agent metadata.
    
    Scans agent.yaml files from src/agents/ and merges with
    runtime configuration from mcp-config/agents.config.json.
    """
    
    def __init__(self, agents_dir: Optional[Path] = None, config_path: Optional[Path] = None):
        """
        Initialize the discovery service.
        
        Args:
            agents_dir: Path to the agents directory. Defaults to src/agents relative to repo root.
            config_path: Path to agents.config.json. Defaults to mcp-config/agents.config.json.
        """
        # Determine repo root (api/src/services -> api/src -> api -> repo root)
        self._repo_root = Path(__file__).parent.parent.parent.parent
        self._agents_dir = agents_dir or self._repo_root / "src" / "agents"
        self._config_path = config_path or self._repo_root / "mcp-config" / "agents.config.json"
        
        # Cache for loaded agents
        self._agents_cache: dict[str, AgentDetail] = {}
        self._runtime_config_cache: dict[str, dict] = {}
        
        # Load agents on initialization
        self._load_agents()
        self._load_runtime_config()
    
    def _load_agents(self) -> None:
        """Scan and load all agent.yaml files."""
        self._agents_cache.clear()
        
        if not self._agents_dir.exists():
            return
        
        for agent_dir in self._agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            agent_yaml = agent_dir / "agent.yaml"
            if not agent_yaml.exists():
                continue
            
            try:
                with open(agent_yaml, "r") as f:
                    data = yaml.safe_load(f)
                
                if data and "id" in data:
                    agent = self._parse_agent_yaml(data)
                    self._agents_cache[agent.id] = agent
            except Exception as e:
                # Log error but continue loading other agents
                print(f"Error loading {agent_yaml}: {e}")
    
    def _load_runtime_config(self) -> None:
        """Load runtime configuration from agents.config.json."""
        self._runtime_config_cache.clear()
        
        if not self._config_path.exists():
            return
        
        try:
            with open(self._config_path, "r") as f:
                config = json.load(f)
            
            for agent in config.get("agents", []):
                agent_id = agent.get("id")
                if agent_id:
                    self._runtime_config_cache[agent_id] = agent
        except Exception as e:
            print(f"Error loading runtime config: {e}")
    
    def _parse_agent_yaml(self, data: dict) -> AgentDetail:
        """Parse agent.yaml data into AgentDetail model."""
        inputs = [
            AgentInput(**inp) for inp in data.get("inputs", [])
        ]
        outputs = [
            AgentOutput(**out) for out in data.get("outputs", [])
        ]
        examples = [
            AgentExample(**ex) for ex in data.get("examples", [])
        ]
        
        constraints = None
        if "constraints" in data:
            constraints = AgentConstraints(**data["constraints"])
        
        requirements = None
        if "requirements" in data:
            requirements = AgentRequirements(**data["requirements"])
        
        return AgentDetail(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            long_description=data.get("long_description"),
            version=data["version"],
            author=data.get("author"),
            category=data.get("category"),
            icon=data.get("icon"),
            status=data.get("status", "stable"),
            visibility=data.get("visibility", "public"),
            tags=data.get("tags", []),
            inputs=inputs,
            outputs=outputs,
            examples=examples,
            documentation_url=data.get("documentation_url"),
            repository_url=data.get("repository_url"),
            constraints=constraints,
            requirements=requirements,
        )
    
    def _to_summary(self, agent: AgentDetail) -> AgentSummary:
        """Convert AgentDetail to AgentSummary."""
        return AgentSummary(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            version=agent.version,
            category=agent.category,
            icon=agent.icon,
            status=agent.status,
            tags=agent.tags,
        )
    
    def list_agents(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[AgentSummary]:
        """
        List agents with optional filtering.
        
        Args:
            category: Filter by category
            status: Filter by status
            tag: Filter by tag
            search: Search in name and description
            
        Returns:
            List of agent summaries matching the filters
        """
        agents = list(self._agents_cache.values())
        
        # Filter by visibility (only show public agents)
        agents = [a for a in agents if a.visibility == "public"]
        
        if category:
            agents = [a for a in agents if a.category and a.category.lower() == category.lower()]
        
        if status:
            agents = [a for a in agents if a.status.lower() == status.lower()]
        
        if tag:
            tag_lower = tag.lower()
            agents = [a for a in agents if any(t.lower() == tag_lower for t in a.tags)]
        
        if search:
            search_lower = search.lower()
            agents = [
                a for a in agents
                if search_lower in a.name.lower() or search_lower in a.description.lower()
            ]
        
        # Sort by name
        agents.sort(key=lambda a: a.name)
        
        return [self._to_summary(a) for a in agents]
    
    def get_agent(self, agent_id: str) -> Optional[AgentDetail]:
        """
        Get detailed information about a specific agent.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            AgentDetail if found, None otherwise
        """
        return self._agents_cache.get(agent_id)
    
    def get_agent_runtime_config(self, agent_id: str) -> Optional[dict]:
        """
        Get merged runtime configuration for an agent.
        
        Combines agent.yaml metadata with agents.config.json runtime settings.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Merged configuration dict if found, None otherwise
        """
        agent = self._agents_cache.get(agent_id)
        if agent is None:
            return None
        
        runtime = self._runtime_config_cache.get(agent_id, {})
        
        return {
            "metadata": agent.model_dump(),
            "runtime": runtime,
        }
    
    def list_categories(self) -> list[str]:
        """Get all unique categories."""
        categories = set()
        for agent in self._agents_cache.values():
            if agent.category:
                categories.add(agent.category)
        return sorted(categories)
    
    def list_tags(self) -> list[str]:
        """Get all unique tags."""
        tags = set()
        for agent in self._agents_cache.values():
            tags.update(agent.tags)
        return sorted(tags)
    
    def reload(self) -> None:
        """Reload all agent metadata from disk."""
        self._load_agents()
        self._load_runtime_config()
