"""
Agent Discovery Service.

Scans the src/agents directory for agent.yaml files and provides
methods to query and filter agents. Validates agents against the
canonical schema on startup.
"""

import json
import re
from pathlib import Path
from typing import Optional

import yaml

from ..models.agent import (
    AgentSummary,
    AgentDetail,
    AgentInput,
    AgentOutput,
    AgentOwner,
    AgentEntrypoint,
    AgentDependencies,
    ValidationError,
    ValidationResult,
)


# Schema validation constants
REQUIRED_FIELDS = ["id", "name", "description", "category", "maturity", "owner", "entrypoint"]
VALID_CATEGORIES = ["frontend", "backend", "qa", "security", "performance", "devex", "architecture", "analytics", "platform"]
VALID_MATURITY = ["alpha", "beta", "stable", "deprecated"]
VALID_VISIBILITY = ["public", "internal", "private"]
VALID_ENTRYPOINT_TYPES = ["python", "node", "shell"]
VALID_INPUT_TYPES = ["string", "number", "boolean", "repo", "branch", "file", "json"]
VALID_OUTPUT_TYPES = ["site", "json", "markdown", "text", "pr", "report"]
ID_PATTERN = re.compile(r"^[a-z0-9-]+$")


class SchemaValidationError(Exception):
    """Raised when agent.yaml fails schema validation."""
    pass


class AgentDiscoveryService:
    """
    Service for discovering and querying agent metadata.
    
    Scans agent.yaml files from src/agents/ and merges with
    runtime configuration from mcp-config/agents.config.json.
    Validates all agents against the canonical schema on startup.
    """
    
    def __init__(
        self,
        agents_dir: Optional[Path] = None,
        config_path: Optional[Path] = None,
        fail_on_validation_error: bool = True,
    ):
        """
        Initialize the discovery service.
        
        Args:
            agents_dir: Path to the agents directory. Defaults to src/agents relative to repo root.
            config_path: Path to agents.config.json. Defaults to mcp-config/agents.config.json.
            fail_on_validation_error: If True, raise exception on validation errors. Default True.
        """
        self._repo_root = Path(__file__).parent.parent.parent.parent
        self._agents_dir = agents_dir or self._repo_root / "src" / "agents"
        self._config_path = config_path or self._repo_root / "mcp-config" / "agents.config.json"
        self._fail_on_validation_error = fail_on_validation_error
        
        self._agents_cache: dict[str, AgentDetail] = {}
        self._runtime_config_cache: dict[str, dict] = {}
        self._validation_errors: list[ValidationError] = []
        
        self._load_agents()
        self._load_runtime_config()
    
    def _validate_agent_yaml(self, data: dict, file_path: Path) -> list[str]:
        """Validate agent.yaml data against the canonical schema."""
        errors = []
        
        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if "id" in data:
            if not isinstance(data["id"], str):
                errors.append("Field 'id' must be a string")
            elif not ID_PATTERN.match(data["id"]):
                errors.append(f"Field 'id' must be kebab-case: got '{data['id']}'")
        
        if "description" in data:
            if not isinstance(data["description"], str):
                errors.append("Field 'description' must be a string")
            elif len(data["description"]) > 200:
                errors.append(f"Field 'description' exceeds 200 characters: {len(data['description'])}")
        
        if "category" in data and data["category"] not in VALID_CATEGORIES:
            errors.append(f"Invalid category '{data['category']}'")
        
        if "maturity" in data and data["maturity"] not in VALID_MATURITY:
            errors.append(f"Invalid maturity '{data['maturity']}'")
        
        if "owner" in data:
            if not isinstance(data["owner"], dict):
                errors.append("Field 'owner' must be an object")
            elif "team" not in data["owner"]:
                errors.append("Field 'owner.team' is required")
        
        if "entrypoint" in data:
            if not isinstance(data["entrypoint"], dict):
                errors.append("Field 'entrypoint' must be an object")
            else:
                if "type" not in data["entrypoint"]:
                    errors.append("Field 'entrypoint.type' is required")
                elif data["entrypoint"]["type"] not in VALID_ENTRYPOINT_TYPES:
                    errors.append(f"Invalid entrypoint.type '{data['entrypoint']['type']}'")
                if "command" not in data["entrypoint"]:
                    errors.append("Field 'entrypoint.command' is required")
        
        if "visibility" in data and data["visibility"] not in VALID_VISIBILITY:
            errors.append(f"Invalid visibility '{data['visibility']}'")
        
        if "inputs" in data and isinstance(data["inputs"], list):
            for i, inp in enumerate(data["inputs"]):
                if isinstance(inp, dict):
                    if "name" not in inp:
                        errors.append(f"inputs[{i}].name is required")
                    if "type" not in inp:
                        errors.append(f"inputs[{i}].type is required")
                    elif inp["type"] not in VALID_INPUT_TYPES:
                        errors.append(f"inputs[{i}].type '{inp['type']}' is invalid")
                    if "required" not in inp:
                        errors.append(f"inputs[{i}].required is required")
        
        if "outputs" in data and isinstance(data["outputs"], list):
            for i, out in enumerate(data["outputs"]):
                if isinstance(out, dict):
                    if "type" not in out:
                        errors.append(f"outputs[{i}].type is required")
                    elif out["type"] not in VALID_OUTPUT_TYPES:
                        errors.append(f"outputs[{i}].type '{out['type']}' is invalid")
        
        return errors
    
    def _load_agents(self) -> None:
        """Scan and load all agent.yaml files with validation."""
        self._agents_cache.clear()
        self._validation_errors.clear()
        
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
                
                if not data:
                    continue
                
                validation_errors = self._validate_agent_yaml(data, agent_yaml)
                
                if validation_errors:
                    agent_id = data.get("id", agent_dir.name)
                    error = ValidationError(
                        agent_id=agent_id,
                        agent_path=str(agent_yaml),
                        errors=validation_errors,
                    )
                    self._validation_errors.append(error)
                    
                    if self._fail_on_validation_error:
                        error_msg = f"Validation failed for {agent_yaml}:\n" + "\n".join(f"  - {e}" for e in validation_errors)
                        raise SchemaValidationError(error_msg)
                    continue
                
                agent = self._parse_agent_yaml(data)
                self._agents_cache[agent.id] = agent
                
            except SchemaValidationError:
                raise
            except Exception as e:
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
        owner = AgentOwner(team=data["owner"]["team"], contact=data["owner"].get("contact"))
        entrypoint = AgentEntrypoint(type=data["entrypoint"]["type"], command=data["entrypoint"]["command"])
        
        inputs = [
            AgentInput(
                name=inp["name"],
                type=inp["type"],
                required=inp["required"],
                description=inp.get("description"),
                default=inp.get("default"),
            )
            for inp in data.get("inputs", [])
        ]
        
        outputs = [
            AgentOutput(
                type=out["type"],
                path=out.get("path"),
                description=out.get("description"),
            )
            for out in data.get("outputs", [])
        ]
        
        dependencies = None
        if "dependencies" in data:
            dependencies = AgentDependencies(
                python=data["dependencies"].get("python", []),
                node=data["dependencies"].get("node", []),
            )
        
        return AgentDetail(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=data["category"],
            maturity=data["maturity"],
            owner=owner,
            entrypoint=entrypoint,
            subCategory=data.get("subCategory"),
            tags=data.get("tags", []),
            visibility=data.get("visibility", "internal"),
            inputs=inputs,
            outputs=outputs,
            capabilities=data.get("capabilities", []),
            dependencies=dependencies,
            installable=data.get("installable", True),
            version=data.get("version", "0.1.0"),
            icon=data.get("icon"),
            documentation_url=data.get("documentation_url"),
            repository_url=data.get("repository_url"),
        )
    
    def _to_summary(self, agent: AgentDetail) -> AgentSummary:
        """Convert AgentDetail to AgentSummary."""
        return AgentSummary(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            category=agent.category,
            maturity=agent.maturity,
            icon=agent.icon,
            tags=agent.tags,
            version=agent.version,
        )
    
    def get_validation_result(self) -> ValidationResult:
        """Get the validation result from the last load."""
        total = len(self._agents_cache) + len(self._validation_errors)
        return ValidationResult(
            valid=len(self._validation_errors) == 0,
            total_agents=total,
            valid_agents=len(self._agents_cache),
            errors=self._validation_errors,
        )
    
    def list_agents(
        self,
        category: Optional[str] = None,
        maturity: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> list[AgentSummary]:
        """
        List agents with optional filtering.
        
        Args:
            category: Filter by category
            maturity: Filter by maturity level
            tag: Filter by tag
            search: Search in name and description
            visibility: Filter by visibility (default: show internal and public)
            
        Returns:
            List of agent summaries matching the filters
        """
        agents = list(self._agents_cache.values())
        
        # Filter by visibility (default: show internal and public, not private)
        if visibility:
            agents = [a for a in agents if a.visibility == visibility]
        else:
            agents = [a for a in agents if a.visibility in ("public", "internal")]
        
        if category:
            agents = [a for a in agents if a.category.lower() == category.lower()]
        
        if maturity:
            agents = [a for a in agents if a.maturity.lower() == maturity.lower()]
        
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
