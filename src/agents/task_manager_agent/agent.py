"""
Task Manager Agent

Orchestrates the PG AI Squad by detecting task types, building workflow plans,
executing agents in sequence or parallel, and producing final deliverables.

Supports:
- Sequential execution (default)
- Parallel execution for independent agents
- Cross-agent communication
- Comprehensive summary output with trace events
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.workflow_engine import (
    WorkflowEngine,
    WorkflowContext,
    TaskType,
    AgentResult
)
from workflows.agent_dispatcher import AgentDispatcher, get_dispatcher

logger = logging.getLogger("pnd_agents.task_manager")


class TaskManagerAgent:
    """
    Task Manager Agent (Scrum Master) for the PG AI Squad.
    
    Responsible for:
    - Detecting task type from natural language descriptions
    - Building workflow plans
    - Executing agents in sequence or parallel
    - Passing outputs between agents
    - Cross-agent communication coordination
    - Storing state for recovery
    - Producing comprehensive final summaries
    """
    
    PARALLEL_GROUPS = {
        "figma": [["figma"], ["frontend"], ["review"], ["unit_test", "performance"], ["sonar"]],
        "frontend": [["frontend"], ["review"], ["unit_test", "performance"], ["sonar"]],
        "backend": [["backend"], ["review"], ["unit_test"], ["sonar"]],
        "amplience": [["amplience"], ["frontend"], ["review"], ["unit_test"], ["sonar"]],
        "qa": [["unit_test"], ["sonar"]],
        "unit_test": [["unit_test"], ["sonar"]],
        "sonar": [["sonar"], ["review"]],
        "code_review": [["review"], ["sonar"]],
        "performance": [["performance"], ["frontend"], ["review"]],
        "default": [["frontend"], ["review"], ["unit_test"], ["sonar"]],
    }
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize the Task Manager Agent.
        
        Args:
            rules_file: Path to workflow_rules.json. If not provided,
                       uses default path.
        """
        if rules_file is None:
            # Go up from src/agents to repo root, then into workflows/
            src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            repo_root = os.path.dirname(src_dir)
            rules_file = os.path.join(repo_root, "workflows", "workflow_rules.json")
        
        self.engine = WorkflowEngine(rules_file)
        self.dispatcher = get_dispatcher()
        self._rules_file = rules_file
        
        for agent_name in self.dispatcher.list_agents():
            handler = self.dispatcher.get_handler(agent_name)
            if handler:
                self.engine.register_agent(agent_name, handler)
        
        self._on_stage_start: Optional[Callable[[str, WorkflowContext], None]] = None
        self._on_stage_complete: Optional[Callable[[str, AgentResult, WorkflowContext], None]] = None
        
        self._load_parallel_groups_from_rules()
    
    def _load_parallel_groups_from_rules(self):
        """Load parallel groups from workflow_rules.json if available."""
        try:
            if os.path.exists(self._rules_file):
                with open(self._rules_file, "r") as f:
                    rules = json.load(f)
                    if "parallel_groups" in rules:
                        self.PARALLEL_GROUPS.update(rules["parallel_groups"])
                        logger.info(f"Loaded parallel groups from {self._rules_file}")
        except Exception as e:
            logger.warning(f"Could not load parallel groups from rules file: {e}")
    
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
        
        context = self.engine.run_workflow(context, on_start, on_complete)
        
        if verbose:
            self._print_summary(context)
        
        return context
    
    def run_task_parallel(
        self,
        task_description: str,
        metadata: Optional[Dict[str, Any]] = None,
        verbose: bool = True,
        max_workers: int = 4
    ) -> WorkflowContext:
        """
        Run a task workflow with parallel execution support.
        
        Agents within the same group run in parallel, groups run sequentially.
        
        Args:
            task_description: Natural language task description.
            metadata: Optional metadata (ticket ID, branch name, etc.)
            verbose: Whether to print progress updates.
            max_workers: Maximum number of parallel workers.
            
        Returns:
            WorkflowContext with results from all stages.
        """
        context = self.engine.create_workflow(task_description, metadata)
        
        task_type_key = context.task_type.value
        parallel_groups = self.PARALLEL_GROUPS.get(task_type_key, self.PARALLEL_GROUPS["default"])
        
        if verbose:
            self._print_plan(context, parallel_groups)
        
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
        
        context = self.engine.run_workflow_parallel(
            context,
            parallel_groups=parallel_groups,
            on_stage_start=on_start,
            on_stage_complete=on_complete,
            max_workers=max_workers
        )
        
        if verbose:
            self._print_comprehensive_summary(context)
        
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
    
    def _print_plan(self, context: WorkflowContext, parallel_groups: Optional[List[List[str]]] = None):
        """Print the workflow plan."""
        print("\n" + "=" * 60)
        print("TASK MANAGER AGENT - Workflow Plan")
        print("=" * 60)
        print(f"\nTask: \"{context.task_description[:80]}{'...' if len(context.task_description) > 80 else ''}\"")
        print(f"Detected Type: {context.task_type.value}")
        print(f"Workflow ID: {context.workflow_id}")
        
        if parallel_groups:
            print(f"\nExecution Mode: PARALLEL")
            print("\nParallel Groups:")
            for i, group in enumerate(parallel_groups):
                if len(group) == 1:
                    print(f"  Group {i + 1}: {group[0].capitalize()}Agent (sequential)")
                else:
                    agents = " + ".join([a.capitalize() + "Agent" for a in group])
                    print(f"  Group {i + 1}: {agents} (parallel)")
        else:
            print(f"\nExecution Mode: SEQUENTIAL")
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
    
    def _print_comprehensive_summary(self, context: WorkflowContext):
        """Print a comprehensive workflow summary with all details."""
        summary = context.get_summary()
        
        print("\n" + "=" * 60)
        print("TASK MANAGER AGENT - Comprehensive Summary")
        print("=" * 60)
        
        print(f"\nWorkflow ID: {summary['workflow_id']}")
        print(f"Task: \"{summary['task_description'][:80]}{'...' if len(summary['task_description']) > 80 else ''}\"")
        print(f"Type: {summary['task_type']}")
        print(f"Status: {summary['status'].upper()}")
        print(f"Total Duration: {summary['total_duration_ms']:.0f}ms")
        
        print("\n--- Agents Used ---")
        for agent in summary['agents_used']:
            print(f"  - {agent.capitalize()}Agent")
        
        print("\n--- Tasks Executed ---")
        for task in summary['tasks_executed']:
            status_icon = "✓" if task['status'] == "completed" else "✗" if task['status'] in ["error", "failed"] else "○"
            print(f"  {status_icon} {task['agent'].capitalize()}Agent: {task['status']} ({task['duration_ms']:.0f}ms)")
        
        if summary['files_changed']:
            print("\n--- Files Changed/Generated ---")
            for f in summary['files_changed'][:10]:
                print(f"  - {f}")
            if len(summary['files_changed']) > 10:
                print(f"  ... and {len(summary['files_changed']) - 10} more files")
        
        if summary['errors']:
            print("\n--- Errors ---")
            for error in summary['errors']:
                print(f"  ✗ {error['agent'].capitalize()}Agent: {error['error']}")
        
        if summary['recommendations']:
            print("\n--- Recommendations ---")
            for rec in summary['recommendations'][:5]:
                print(f"  - {rec}")
            if len(summary['recommendations']) > 5:
                print(f"  ... and {len(summary['recommendations']) - 5} more recommendations")
        
        if summary['trace']:
            print("\n--- Execution Trace ---")
            for event in summary['trace'][-10:]:
                print(f"  [{event['timestamp'][-12:-4]}] {event['agent']}: {event['event_type']} -> {event['status']}")
        
        print("\n" + "=" * 60)
    
    def _get_agent_description(self, agent_name: str) -> str:
        """Get a description for an agent."""
        descriptions = {
            "figma": "Extract component structure from Figma design",
            "frontend": "Generate React components",
            "backend": "Create API endpoints and server components",
            "amplience": "Generate Amplience content type schemas",
            "review": "Validate code against standards",
            "unit_test": "Generate unit tests with 100% coverage target",
            "sonar": "Validate against SonarCloud quality gates",
            "qa": "Generate E2E and integration tests",
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
