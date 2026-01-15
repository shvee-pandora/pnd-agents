"""
Base Agent Module

Provides the abstract base class interface that all agents should implement.
This ensures consistent behavior and interface across all agents in the system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentResult:
    """
    Standardized result from agent execution.
    
    All agents should return this type from their run() method.
    """
    status: str  # "success", "error", "skipped", "pending_approval"
    data: Dict[str, Any] = field(default_factory=dict)
    next: Optional[str] = None  # Suggested next agent to call
    error: Optional[str] = None
    duration_ms: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status,
            "data": self.data,
            "next": self.next,
            "error": self.error,
            "duration_ms": self.duration_ms
        }
    
    @classmethod
    def success(cls, data: Dict[str, Any], next_agent: Optional[str] = None) -> "AgentResult":
        """Create a success result."""
        return cls(status="success", data=data, next=next_agent)
    
    @classmethod
    def error(cls, message: str, data: Optional[Dict[str, Any]] = None) -> "AgentResult":
        """Create an error result."""
        return cls(status="error", error=message, data=data or {})
    
    @classmethod
    def skipped(cls, reason: str) -> "AgentResult":
        """Create a skipped result."""
        return cls(status="skipped", data={"reason": reason})


@dataclass
class AgentContext:
    """
    Context passed to agents during execution.
    
    Contains all information an agent needs to perform its task.
    """
    task_description: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    workflow_id: Optional[str] = None
    agent_name: Optional[str] = None
    
    @property
    def repo_context(self) -> Optional[Dict[str, Any]]:
        """Get repository context from metadata (Code Singularity pattern)."""
        return self.metadata.get("repo_context")
    
    @property
    def repo_name(self) -> Optional[str]:
        """Get repository name from metadata."""
        return self.metadata.get("repo_name")
    
    @property
    def previous_output(self) -> Dict[str, Any]:
        """Get output from previous agent in pipeline."""
        return self.input_data.get("previous_output", {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task": self.task_description,
            "input": self.input_data,
            "metadata": self.metadata,
            "workflow_id": self.workflow_id,
            "agent_name": self.agent_name,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContext":
        """Create from dictionary (e.g., from workflow engine)."""
        return cls(
            task_description=data.get("task", ""),
            input_data=data.get("input", {}),
            metadata=data.get("metadata", {}),
            workflow_id=data.get("workflow_id"),
            agent_name=data.get("agent_name"),
        )


class BaseAgent(ABC):
    """
    Abstract base class for all PND agents.
    
    All agents should inherit from this class and implement the required methods.
    This ensures consistent interface and behavior across the agent ecosystem.
    
    Example:
        class MyAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "my_agent"
            
            @property
            def description(self) -> str:
                return "Does something useful"
            
            def run(self, context: AgentContext) -> AgentResult:
                # Agent logic here
                return AgentResult.success({"output": "done"})
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for this agent.
        
        Should be lowercase with underscores (e.g., "unit_test", "code_review").
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description of what this agent does.
        
        Used in documentation and tool registration.
        """
        pass
    
    @property
    def scope(self) -> str:
        """
        Agent scope: "universal" or "platform".
        
        Universal agents work in any repository.
        Platform agents are specific to Pandora infrastructure.
        """
        return "universal"
    
    @property
    def category(self) -> str:
        """
        Agent category for organization.
        
        One of: orchestration, development, quality, performance,
        product_management, analytics, commerce, cms
        """
        return "development"
    
    @property
    def tools(self) -> List[str]:
        """
        List of MCP tool names this agent provides.
        
        Used for automatic tool registration.
        """
        return []
    
    @property
    def dependencies(self) -> List[str]:
        """
        List of agent names this agent depends on.
        
        Used for pipeline ordering and validation.
        """
        return []
    
    @abstractmethod
    def run(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's main logic.
        
        Args:
            context: AgentContext with task description, input data, and metadata.
            
        Returns:
            AgentResult with status, data, and optional next agent suggestion.
        """
        pass
    
    def validate_input(self, context: AgentContext) -> Optional[str]:
        """
        Validate input before running.
        
        Override this method to add input validation.
        
        Args:
            context: AgentContext to validate.
            
        Returns:
            Error message if validation fails, None if valid.
        """
        return None
    
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get agent manifest for registration and discovery.
        
        Returns:
            Dictionary with agent metadata.
        """
        return {
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
            "category": self.category,
            "tools": self.tools,
            "dependencies": self.dependencies,
        }


__all__ = [
    "AgentResult",
    "AgentContext",
    "BaseAgent",
]
