"""
Workflow Engine

Orchestrates multi-agent pipelines by detecting task types,
building workflow plans, and executing agents in sequence.
"""

import json
import os
import re
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict


class TaskType(Enum):
    """Types of tasks that can be detected."""
    FIGMA = "figma"
    FRONTEND = "frontend"
    BACKEND = "backend"
    AMPLIENCE = "amplience"
    UNIT_TEST = "unit_test"
    SONAR = "sonar"
    QA = "qa"
    CODE_REVIEW = "code_review"
    PERFORMANCE = "performance"
    DEFAULT = "default"


# Keywords for task type detection
TASK_KEYWORDS: Dict[TaskType, List[str]] = {
    TaskType.FIGMA: [
        "figma", "design", "frame", "component", "ui spec",
        "figma.com", "from design", "design file"
    ],
    TaskType.FRONTEND: [
        "react", "component", "tsx", "ui", "frontend",
        "next.js", "nextjs", "jsx", "styled", "css"
    ],
    TaskType.BACKEND: [
        "api", "endpoint", "server", "route", "integration",
        "backend", "rest", "graphql", "database"
    ],
    TaskType.AMPLIENCE: [
        "content type", "cms", "schema", "amplience",
        "content model", "dynamic content"
    ],
    TaskType.UNIT_TEST: [
        "unit test", "unit tests", "100% coverage", "jest test",
        "jest tests", "vitest", "test coverage", "write tests", "generate tests"
    ],
    TaskType.SONAR: [
        "sonar", "sonarcloud", "sonarqube", "quality gate",
        "code quality", "duplication", "code smells", "vulnerabilities"
    ],
    TaskType.QA: [
        "e2e", "integration tests", "automation", "playwright",
        "acceptance tests", "test cases", "end to end"
    ],
    TaskType.CODE_REVIEW: [
        "review", "lint", "standards", "refactor",
        "code quality", "eslint", "prettier"
    ],
    TaskType.PERFORMANCE: [
        "har", "performance", "optimize", "slow",
        "lighthouse", "web vitals", "speed"
    ],
}


@dataclass
class AgentResult:
    """Result from an agent execution."""
    status: str  # "success", "error", "skipped"
    data: Dict[str, Any] = field(default_factory=dict)
    next: Optional[str] = None  # Next agent to call (optional override)
    error: Optional[str] = None
    duration_ms: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "data": self.data,
            "next": self.next,
            "error": self.error,
            "duration_ms": self.duration_ms
        }


@dataclass
class WorkflowStage:
    """Represents a stage in the workflow."""
    agent_name: str
    status: str = "pending"  # pending, in_progress, completed, failed, skipped
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error
        }


@dataclass
class WorkflowContext:
    """Context for a workflow execution."""
    workflow_id: str
    task_description: str
    task_type: TaskType
    pipeline: List[str]
    stages: Dict[str, WorkflowStage] = field(default_factory=dict)
    started_at: str = ""
    completed_at: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed
    current_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.utcnow().isoformat()
        # Initialize stages for each agent in pipeline
        for agent in self.pipeline:
            if agent not in self.stages:
                self.stages[agent] = WorkflowStage(agent_name=agent)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "task_description": self.task_description,
            "task_type": self.task_type.value,
            "pipeline": self.pipeline,
            "stages": {k: v.to_dict() for k, v in self.stages.items()},
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "current_agent": self.current_agent,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowContext":
        """Create WorkflowContext from dictionary."""
        stages = {}
        for agent, stage_data in data.get("stages", {}).items():
            stages[agent] = WorkflowStage(
                agent_name=stage_data["agent_name"],
                status=stage_data["status"],
                started_at=stage_data.get("started_at"),
                completed_at=stage_data.get("completed_at"),
                input_data=stage_data.get("input_data", {}),
                output_data=stage_data.get("output_data", {}),
                error=stage_data.get("error")
            )
        
        return cls(
            workflow_id=data["workflow_id"],
            task_description=data["task_description"],
            task_type=TaskType(data["task_type"]),
            pipeline=data["pipeline"],
            stages=stages,
            started_at=data["started_at"],
            completed_at=data.get("completed_at"),
            status=data["status"],
            current_agent=data.get("current_agent"),
            metadata=data.get("metadata", {})
        )
    
    def get_last_output(self) -> Dict[str, Any]:
        """Get the output from the last completed stage."""
        for agent in reversed(self.pipeline):
            stage = self.stages.get(agent)
            if stage and stage.status == "completed" and stage.output_data:
                return stage.output_data
        return {}


class WorkflowEngine:
    """
    Engine for orchestrating multi-agent workflows.
    
    The workflow engine:
    1. Detects task type from description
    2. Builds the appropriate pipeline
    3. Executes agents in sequence
    4. Passes outputs between agents
    5. Stores state for recovery
    """
    
    CONTEXT_FILE = "/tmp/pnd_agent_context.json"
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize the workflow engine.
        
        Args:
            rules_file: Path to workflow_rules.json. If not provided,
                       uses default rules.
        """
        self.rules = self._load_rules(rules_file)
        self._agent_handlers: Dict[str, Callable] = {}
    
    def _load_rules(self, rules_file: Optional[str]) -> Dict[str, List[str]]:
        """Load workflow rules from file or use defaults."""
        default_rules = {
            "figma": ["figma", "frontend", "review", "qa", "performance"],
            "frontend": ["frontend", "review", "qa", "performance"],
            "backend": ["backend", "review", "qa"],
            "amplience": ["amplience", "frontend", "review", "qa"],
            "qa": ["qa", "review"],
            "code_review": ["review"],
            "performance": ["performance", "frontend", "review"],
            "default": ["frontend", "review", "qa"]
        }
        
        if rules_file and os.path.exists(rules_file):
            try:
                with open(rules_file, "r") as f:
                    loaded_rules = json.load(f)
                    return loaded_rules.get("workflows", loaded_rules)
            except Exception:
                pass
        
        return default_rules
    
    def register_agent(self, name: str, handler: Callable[[Dict[str, Any]], AgentResult]):
        """
        Register an agent handler function.
        
        Args:
            name: Agent name (e.g., "figma", "frontend")
            handler: Function that takes context dict and returns AgentResult
        """
        self._agent_handlers[name] = handler
    
    def detect_task_type(self, task_description: str) -> TaskType:
        """
        Detect the task type from the description.
        
        Args:
            task_description: The task description text.
            
        Returns:
            The detected TaskType.
        """
        description_lower = task_description.lower()
        
        # Check for Figma URLs first (highest priority)
        if "figma.com" in description_lower:
            return TaskType.FIGMA
        
        # Score each task type based on keyword matches
        scores: Dict[TaskType, int] = {t: 0 for t in TaskType}
        
        for task_type, keywords in TASK_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    scores[task_type] += 1
        
        # Find the task type with highest score
        max_score = 0
        detected_type = TaskType.DEFAULT
        
        for task_type, score in scores.items():
            if score > max_score:
                max_score = score
                detected_type = task_type
        
        return detected_type
    
    def build_pipeline(self, task_type: TaskType) -> List[str]:
        """
        Build the agent pipeline for a task type.
        
        Args:
            task_type: The detected task type.
            
        Returns:
            List of agent names in execution order.
        """
        type_key = task_type.value
        if type_key in self.rules:
            return self.rules[type_key].copy()
        return self.rules.get("default", ["frontend", "review", "qa"]).copy()
    
    def create_workflow(self, task_description: str, metadata: Optional[Dict[str, Any]] = None) -> WorkflowContext:
        """
        Create a new workflow context for a task.
        
        Args:
            task_description: The task description.
            metadata: Optional metadata (ticket ID, branch name, etc.)
            
        Returns:
            WorkflowContext for the workflow.
        """
        import uuid
        
        task_type = self.detect_task_type(task_description)
        pipeline = self.build_pipeline(task_type)
        
        context = WorkflowContext(
            workflow_id=str(uuid.uuid4())[:8],
            task_description=task_description,
            task_type=task_type,
            pipeline=pipeline,
            metadata=metadata or {}
        )
        
        return context
    
    def save_context(self, context: WorkflowContext):
        """Save workflow context to file."""
        try:
            with open(self.CONTEXT_FILE, "w") as f:
                json.dump(context.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save context: {e}")
    
    def load_context(self) -> Optional[WorkflowContext]:
        """Load workflow context from file."""
        if not os.path.exists(self.CONTEXT_FILE):
            return None
        
        try:
            with open(self.CONTEXT_FILE, "r") as f:
                data = json.load(f)
                return WorkflowContext.from_dict(data)
        except Exception:
            return None
    
    def clear_context(self):
        """Clear the saved context file."""
        if os.path.exists(self.CONTEXT_FILE):
            os.remove(self.CONTEXT_FILE)
    
    def execute_agent(
        self,
        agent_name: str,
        context: WorkflowContext,
        input_data: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute a single agent.
        
        Args:
            agent_name: Name of the agent to execute.
            context: The workflow context.
            input_data: Input data for the agent.
            
        Returns:
            AgentResult from the agent.
        """
        import time
        
        # Update stage status
        stage = context.stages.get(agent_name)
        if stage:
            stage.status = "in_progress"
            stage.started_at = datetime.utcnow().isoformat()
            stage.input_data = input_data
        
        context.current_agent = agent_name
        self.save_context(context)
        
        start_time = time.time()
        
        # Check if handler is registered
        handler = self._agent_handlers.get(agent_name)
        if not handler:
            # Return a placeholder result if no handler
            result = AgentResult(
                status="skipped",
                data={"message": f"No handler registered for agent: {agent_name}"},
                error=None
            )
        else:
            try:
                # Execute the handler
                result = handler({
                    "task": context.task_description,
                    "input": input_data,
                    "metadata": context.metadata,
                    "workflow_id": context.workflow_id,
                    "agent_name": agent_name
                })
            except Exception as e:
                result = AgentResult(
                    status="error",
                    error=str(e)
                )
        
        result.duration_ms = (time.time() - start_time) * 1000
        
        # Update stage with result
        if stage:
            stage.status = "completed" if result.status == "success" else result.status
            stage.completed_at = datetime.utcnow().isoformat()
            stage.output_data = result.data
            if result.error:
                stage.error = result.error
        
        self.save_context(context)
        
        return result
    
    def run_workflow(
        self,
        context: WorkflowContext,
        on_stage_start: Optional[Callable[[str, WorkflowContext], None]] = None,
        on_stage_complete: Optional[Callable[[str, AgentResult, WorkflowContext], None]] = None
    ) -> WorkflowContext:
        """
        Run a complete workflow.
        
        Args:
            context: The workflow context.
            on_stage_start: Callback when a stage starts.
            on_stage_complete: Callback when a stage completes.
            
        Returns:
            Updated WorkflowContext.
        """
        context.status = "running"
        self.save_context(context)
        
        # Start with task description as initial input
        current_input = {
            "task": context.task_description,
            "metadata": context.metadata
        }
        
        for agent_name in context.pipeline:
            # Call stage start callback
            if on_stage_start:
                on_stage_start(agent_name, context)
            
            # Execute the agent
            result = self.execute_agent(agent_name, context, current_input)
            
            # Call stage complete callback
            if on_stage_complete:
                on_stage_complete(agent_name, result, context)
            
            # Check for errors
            if result.status == "error":
                context.status = "failed"
                context.completed_at = datetime.utcnow().isoformat()
                self.save_context(context)
                return context
            
            # Prepare input for next agent
            if result.data:
                current_input = {
                    **current_input,
                    "previous_agent": agent_name,
                    "previous_output": result.data
                }
            
            # Check if agent wants to override next agent
            if result.next:
                # Find the next agent in pipeline and skip to it
                try:
                    next_idx = context.pipeline.index(result.next)
                    current_idx = context.pipeline.index(agent_name)
                    # Skip agents between current and next
                    for skip_agent in context.pipeline[current_idx + 1:next_idx]:
                        skip_stage = context.stages.get(skip_agent)
                        if skip_stage:
                            skip_stage.status = "skipped"
                except ValueError:
                    pass  # Agent not in pipeline, continue normally
        
        context.status = "completed"
        context.completed_at = datetime.utcnow().isoformat()
        self.save_context(context)
        
        return context
    
    def get_workflow_plan(self, task_description: str) -> Dict[str, Any]:
        """
        Get the workflow plan for a task without executing it.
        
        Args:
            task_description: The task description.
            
        Returns:
            Dictionary with task type and pipeline.
        """
        task_type = self.detect_task_type(task_description)
        pipeline = self.build_pipeline(task_type)
        
        return {
            "task": task_description,
            "detected_type": task_type.value,
            "pipeline": pipeline,
            "stages": [
                {
                    "step": i + 1,
                    "agent": agent,
                    "description": self._get_agent_description(agent)
                }
                for i, agent in enumerate(pipeline)
            ]
        }
    
    def _get_agent_description(self, agent_name: str) -> str:
        """Get a description for an agent."""
        descriptions = {
            "figma": "Extract component structure from Figma design",
            "frontend": "Generate React components",
            "backend": "Create API endpoints and server components",
            "amplience": "Generate Amplience content type schemas",
            "review": "Validate code against standards",
            "unit_test": "Generate unit tests with 100% coverage target",
            "sonar": "Validate against SonarCloud quality gates (0 errors, 0 duplication)",
            "qa": "Generate E2E and integration tests",
            "performance": "Run performance analysis and optimization checks"
        }
        return descriptions.get(agent_name, f"Execute {agent_name} agent")
    
    def print_plan(self, task_description: str):
        """Print the workflow plan for a task."""
        plan = self.get_workflow_plan(task_description)
        
        print(f"\nTask Identified: \"{task_description[:80]}{'...' if len(task_description) > 80 else ''}\"")
        print(f"Detected Type: {plan['detected_type']}")
        print("\nPipeline:")
        for stage in plan["stages"]:
            print(f"  {stage['step']}. {stage['agent'].capitalize()}Agent -> {stage['description']}")
        print()
