"""
Task Manager Agent

Orchestrates the PG AI Squad by detecting task types, building workflow plans,
executing agents in sequence, and producing final deliverables.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.workflow_engine import (
    WorkflowEngine,
    WorkflowContext,
    TaskType,
    AgentResult
)
from workflow.agent_dispatcher import AgentDispatcher, get_dispatcher


class TaskManagerAgent:
    """
    Task Manager Agent (Scrum Master) for the PG AI Squad.
    
    Responsible for:
    - Detecting task type from natural language descriptions
    - Building workflow plans
    - Executing agents in sequence
    - Passing outputs between agents
    - Storing state for recovery
    - Producing final deliverables
    """
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize the Task Manager Agent.
        
        Args:
            rules_file: Path to workflow_rules.json. If not provided,
                       uses default path.
        """
        if rules_file is None:
            # Default to workflow/workflow_rules.json
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_file = os.path.join(base_dir, "workflow", "workflow_rules.json")
        
        self.engine = WorkflowEngine(rules_file)
        self.dispatcher = get_dispatcher()
        
        # Register dispatcher handlers with engine
        for agent_name in self.dispatcher.list_agents():
            handler = self.dispatcher.get_handler(agent_name)
            if handler:
                self.engine.register_agent(agent_name, handler)
        
        # Callbacks for progress reporting
        self._on_stage_start: Optional[Callable[[str, WorkflowContext], None]] = None
        self._on_stage_complete: Optional[Callable[[str, AgentResult, WorkflowContext], None]] = None
    
    def set_callbacks(
        self,
        on_stage_start: Optional[Callable[[str, WorkflowContext], None]] = None,
        on_stage_complete: Optional[Callable[[str, AgentResult, WorkflowContext], None]] = None
    ):
        """Set callbacks for progress reporting."""
        self._on_stage_start = on_stage_start
        self._on_stage_complete = on_stage_complete
    
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Analyze a task and return the workflow plan.
        
        Args:
            task_description: Natural language task description.
            
        Returns:
            Dictionary with task analysis and workflow plan.
        """
        task_type = self.engine.detect_task_type(task_description)
        pipeline = self.engine.build_pipeline(task_type)
        
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
    
    def run_task(
        self,
        task_description: str,
        metadata: Optional[Dict[str, Any]] = None,
        verbose: bool = True
    ) -> WorkflowContext:
        """
        Run a complete task workflow.
        
        Args:
            task_description: Natural language task description.
            metadata: Optional metadata (ticket ID, branch name, etc.)
            verbose: Whether to print progress updates.
            
        Returns:
            WorkflowContext with results from all stages.
        """
        # Create workflow context
        context = self.engine.create_workflow(task_description, metadata)
        
        if verbose:
            self._print_plan(context)
        
        # Define progress callbacks
        def on_start(agent_name: str, ctx: WorkflowContext):
            if verbose:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting: {agent_name.capitalize()}Agent")
            if self._on_stage_start:
                self._on_stage_start(agent_name, ctx)
        
        def on_complete(agent_name: str, result: AgentResult, ctx: WorkflowContext):
            if verbose:
                status_icon = "✓" if result.status == "success" else "✗" if result.status == "error" else "○"
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {status_icon} Completed: {agent_name.capitalize()}Agent ({result.duration_ms:.0f}ms)")
                if result.error:
                    print(f"    Error: {result.error}")
            if self._on_stage_complete:
                self._on_stage_complete(agent_name, result, ctx)
        
        # Run the workflow
        context = self.engine.run_workflow(context, on_start, on_complete)
        
        if verbose:
            self._print_summary(context)
        
        return context
    
    def resume_task(self, verbose: bool = True) -> Optional[WorkflowContext]:
        """
        Resume a previously interrupted task.
        
        Args:
            verbose: Whether to print progress updates.
            
        Returns:
            WorkflowContext if a task was resumed, None otherwise.
        """
        context = self.engine.load_context()
        if not context:
            if verbose:
                print("No interrupted task found.")
            return None
        
        if context.status == "completed":
            if verbose:
                print("Previous task already completed.")
            return context
        
        if verbose:
            print(f"Resuming task: {context.task_description[:50]}...")
            print(f"Current stage: {context.current_agent}")
        
        # Find where to resume
        resume_from = None
        for agent in context.pipeline:
            stage = context.stages.get(agent)
            if stage and stage.status in ["pending", "in_progress"]:
                resume_from = agent
                break
        
        if not resume_from:
            if verbose:
                print("All stages completed.")
            return context
        
        # Continue from resume point
        resume_idx = context.pipeline.index(resume_from)
        remaining_pipeline = context.pipeline[resume_idx:]
        
        # Get last output for input
        current_input = context.get_last_output()
        if not current_input:
            current_input = {
                "task": context.task_description,
                "metadata": context.metadata
            }
        
        for agent_name in remaining_pipeline:
            if verbose:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running: {agent_name.capitalize()}Agent")
            
            result = self.engine.execute_agent(agent_name, context, current_input)
            
            if verbose:
                status_icon = "✓" if result.status == "success" else "✗"
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {status_icon} Completed: {agent_name.capitalize()}Agent")
            
            if result.status == "error":
                context.status = "failed"
                break
            
            if result.data:
                current_input = {
                    **current_input,
                    "previous_agent": agent_name,
                    "previous_output": result.data
                }
        
        if context.status != "failed":
            context.status = "completed"
        
        context.completed_at = datetime.utcnow().isoformat()
        self.engine.save_context(context)
        
        if verbose:
            self._print_summary(context)
        
        return context
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get the status of the current/last task.
        
        Returns:
            Dictionary with task status, or None if no task exists.
        """
        context = self.engine.load_context()
        if not context:
            return None
        
        return {
            "workflow_id": context.workflow_id,
            "task": context.task_description,
            "type": context.task_type.value,
            "status": context.status,
            "current_agent": context.current_agent,
            "started_at": context.started_at,
            "completed_at": context.completed_at,
            "stages": {
                name: {
                    "status": stage.status,
                    "error": stage.error
                }
                for name, stage in context.stages.items()
            }
        }
    
    def clear_task(self):
        """Clear the current task context."""
        self.engine.clear_context()
    
    def _print_plan(self, context: WorkflowContext):
        """Print the workflow plan."""
        print("\n" + "=" * 60)
        print("TASK MANAGER AGENT - Workflow Plan")
        print("=" * 60)
        print(f"\nTask: \"{context.task_description[:80]}{'...' if len(context.task_description) > 80 else ''}\"")
        print(f"Detected Type: {context.task_type.value}")
        print(f"Workflow ID: {context.workflow_id}")
        print("\nPipeline:")
        for i, agent in enumerate(context.pipeline):
            print(f"  {i + 1}. {agent.capitalize()}Agent -> {self._get_agent_description(agent)}")
        print("\n" + "-" * 60)
    
    def _print_summary(self, context: WorkflowContext):
        """Print the workflow summary."""
        print("\n" + "=" * 60)
        print("TASK MANAGER AGENT - Workflow Summary")
        print("=" * 60)
        print(f"\nStatus: {context.status.upper()}")
        print(f"Duration: {self._calculate_duration(context)}")
        print("\nStage Results:")
        
        for agent in context.pipeline:
            stage = context.stages.get(agent)
            if stage:
                status_icon = {
                    "completed": "✓",
                    "failed": "✗",
                    "skipped": "○",
                    "pending": "·",
                    "in_progress": "→"
                }.get(stage.status, "?")
                print(f"  {status_icon} {agent.capitalize()}Agent: {stage.status}")
                if stage.error:
                    print(f"      Error: {stage.error}")
        
        # Print final output summary
        last_output = context.get_last_output()
        if last_output:
            print("\nFinal Output:")
            if "files_to_generate" in last_output:
                print("  Files to generate:")
                for f in last_output["files_to_generate"][:5]:
                    print(f"    - {f}")
            if "test_files" in last_output:
                print("  Test files:")
                for f in last_output["test_files"][:5]:
                    print(f"    - {f}")
            if "recommendations" in last_output:
                print("  Recommendations:")
                for r in last_output["recommendations"][:3]:
                    print(f"    - {r}")
        
        print("\n" + "=" * 60)
    
    def _get_agent_description(self, agent_name: str) -> str:
        """Get a description for an agent."""
        descriptions = {
            "figma": "Extract component structure from Figma design",
            "frontend": "Generate React components",
            "backend": "Create API endpoints and server components",
            "amplience": "Generate Amplience content type schemas",
            "review": "Validate code against standards",
            "qa": "Generate unit and integration tests",
            "performance": "Run performance analysis and optimization checks"
        }
        return descriptions.get(agent_name, f"Execute {agent_name} agent")
    
    def _calculate_duration(self, context: WorkflowContext) -> str:
        """Calculate the workflow duration."""
        if not context.completed_at:
            return "In progress"
        
        try:
            start = datetime.fromisoformat(context.started_at)
            end = datetime.fromisoformat(context.completed_at)
            duration = (end - start).total_seconds()
            
            if duration < 60:
                return f"{duration:.1f}s"
            elif duration < 3600:
                return f"{duration / 60:.1f}m"
            else:
                return f"{duration / 3600:.1f}h"
        except Exception:
            return "Unknown"
    
    def to_dict(self, context: WorkflowContext) -> Dict[str, Any]:
        """Convert workflow context to dictionary for JSON output."""
        return context.to_dict()


# Convenience function for running tasks
def run_task(task_description: str, metadata: Optional[Dict[str, Any]] = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Run a task through the Task Manager Agent.
    
    Args:
        task_description: Natural language task description.
        metadata: Optional metadata (ticket ID, branch name, etc.)
        verbose: Whether to print progress updates.
        
    Returns:
        Dictionary with workflow results.
    """
    agent = TaskManagerAgent()
    context = agent.run_task(task_description, metadata, verbose)
    return agent.to_dict(context)


def analyze_task(task_description: str) -> Dict[str, Any]:
    """
    Analyze a task and return the workflow plan without executing.
    
    Args:
        task_description: Natural language task description.
        
    Returns:
        Dictionary with task analysis and workflow plan.
    """
    agent = TaskManagerAgent()
    return agent.analyze_task(task_description)
