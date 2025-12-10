"""
Analytics & Reporting Agent

A dedicated agent for tracking agent performance metrics, integrating with JIRA,
and generating comprehensive reports for the PG AI Squad.

Responsibilities:
- Listen to task events from other agents in the squad
- Track metrics about agent performance
- Persist structured logs for each task
- Update JIRA issues using Atlassian REST API
- Provide endpoints for Claude to call via MCP
- Generate weekly or per-task dashboards/reports
"""

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger("pnd_agents.analytics")


class TaskStatus(Enum):
    """Status of a tracked task."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskMetrics:
    """Metrics collected for a single task execution."""
    ai_used: bool = True
    agent_name: str = ""
    task_name: str = ""
    start_time: str = ""
    end_time: str = ""
    duration_ms: float = 0
    iterations: int = 1
    errors: List[str] = field(default_factory=list)
    effectiveness_score: float = 100.0
    requires_human_review: bool = False
    confidence_score: float = 1.0
    jira_task_id: Optional[str] = None
    workflow_id: Optional[str] = None
    status: str = TaskStatus.STARTED.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "aiUsed": self.ai_used,
            "agentName": self.agent_name,
            "taskName": self.task_name,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "duration": self.duration_ms,
            "iterations": self.iterations,
            "errors": self.errors,
            "effectivenessScore": self.effectiveness_score,
            "requiresHumanReview": self.requires_human_review,
            "confidenceScore": self.confidence_score,
            "jiraTaskId": self.jira_task_id,
            "workflowId": self.workflow_id,
            "status": self.status,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskMetrics":
        """Create TaskMetrics from dictionary."""
        return cls(
            ai_used=data.get("aiUsed", True),
            agent_name=data.get("agentName", ""),
            task_name=data.get("taskName", ""),
            start_time=data.get("startTime", ""),
            end_time=data.get("endTime", ""),
            duration_ms=data.get("duration", 0),
            iterations=data.get("iterations", 1),
            errors=data.get("errors", []),
            effectiveness_score=data.get("effectivenessScore", 100.0),
            requires_human_review=data.get("requiresHumanReview", False),
            confidence_score=data.get("confidenceScore", 1.0),
            jira_task_id=data.get("jiraTaskId"),
            workflow_id=data.get("workflowId"),
            status=data.get("status", TaskStatus.STARTED.value),
        )


@dataclass
class AgentReport:
    """Aggregated report for agent performance."""
    agent_name: str
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_duration_ms: float = 0
    average_effectiveness_score: float = 0
    total_errors: int = 0
    tasks_requiring_review: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "agentName": self.agent_name,
            "totalTasks": self.total_tasks,
            "completedTasks": self.completed_tasks,
            "failedTasks": self.failed_tasks,
            "averageDurationMs": self.average_duration_ms,
            "averageEffectivenessScore": self.average_effectiveness_score,
            "totalErrors": self.total_errors,
            "tasksRequiringReview": self.tasks_requiring_review,
        }


@dataclass
class SprintReport:
    """Sprint-level analytics report."""
    sprint_name: str
    start_date: str
    end_date: str
    total_ai_tasks: int = 0
    average_effectiveness_score: float = 0
    time_saved_hours: float = 0
    agent_distribution: Dict[str, int] = field(default_factory=dict)
    tasks_requiring_review: int = 0
    trend_data: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "sprintName": self.sprint_name,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "totalAiTasks": self.total_ai_tasks,
            "averageEffectivenessScore": self.average_effectiveness_score,
            "timeSavedHours": self.time_saved_hours,
            "agentDistribution": self.agent_distribution,
            "tasksRequiringReview": self.tasks_requiring_review,
            "trendData": self.trend_data,
        }


class AnalyticsAgent:
    """
    Analytics & Reporting Agent for the PG AI Squad.
    
    Tracks agent performance metrics, integrates with JIRA,
    and generates comprehensive reports.
    """
    
    # Default log directory
    DEFAULT_LOG_DIR = "/logs/agent-analytics"
    
    # Estimated time saved per task (in hours) - configurable
    ESTIMATED_TIME_SAVED_PER_TASK = 2.0
    
    def __init__(
        self,
        log_dir: Optional[str] = None,
        jira_client: Optional[Any] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Analytics Agent.
        
        Args:
            log_dir: Directory for storing analytics logs
            jira_client: Optional JIRA client instance
            config_path: Path to analytics configuration file
        """
        # Determine log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            base_dir = Path(__file__).parent.parent.parent
            self.log_dir = base_dir / "logs" / "agent-analytics"
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # JIRA client (lazy loaded)
        self._jira_client = jira_client
        
        # In-memory cache of active tasks
        self._active_tasks: Dict[str, TaskMetrics] = {}
        
        # Event callbacks
        self._on_task_started: Optional[Callable[[TaskMetrics], None]] = None
        self._on_task_completed: Optional[Callable[[TaskMetrics], None]] = None
        self._on_task_failed: Optional[Callable[[TaskMetrics], None]] = None
        
        logger.info(f"Analytics Agent initialized with log directory: {self.log_dir}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load analytics configuration."""
        default_config = {
            "estimated_time_saved_per_task": 2.0,
            "jira_comment_enabled": True,
            "jira_custom_fields_enabled": True,
            "auto_update_jira": True,
            "log_retention_days": 90,
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
        
        return default_config
    
    @property
    def jira_client(self) -> Optional[Any]:
        """Get or create JIRA client."""
        if self._jira_client is None:
            try:
                from tools.jira_client import JiraClient
                self._jira_client = JiraClient()
            except ImportError:
                logger.warning("JIRA client not available")
        return self._jira_client
    
    def set_callbacks(
        self,
        on_task_started: Optional[Callable[[TaskMetrics], None]] = None,
        on_task_completed: Optional[Callable[[TaskMetrics], None]] = None,
        on_task_failed: Optional[Callable[[TaskMetrics], None]] = None
    ):
        """Set event callbacks for task lifecycle events."""
        self._on_task_started = on_task_started
        self._on_task_completed = on_task_completed
        self._on_task_failed = on_task_failed
    
    # ==================== Task Event Handlers ====================
    
    def on_task_started(
        self,
        agent_name: str,
        task_description: str,
        jira_task_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> TaskMetrics:
        """
        Record the start of a task.
        
        Args:
            agent_name: Name of the agent starting the task
            task_description: Description of the task
            jira_task_id: Optional JIRA issue key
            workflow_id: Optional workflow ID for correlation
            
        Returns:
            TaskMetrics object for the started task
        """
        metrics = TaskMetrics(
            agent_name=agent_name,
            task_name=task_description,
            start_time=datetime.utcnow().isoformat(),
            jira_task_id=jira_task_id,
            workflow_id=workflow_id,
            status=TaskStatus.STARTED.value,
        )
        
        # Generate task ID for tracking
        task_id = self._generate_task_id(agent_name, jira_task_id)
        self._active_tasks[task_id] = metrics
        
        # Persist to log
        self._save_task_log(task_id, metrics)
        
        # Trigger callback
        if self._on_task_started:
            self._on_task_started(metrics)
        
        logger.info(f"Task started: {agent_name} - {task_description[:50]}...")
        
        return metrics
    
    def on_task_completed(
        self,
        agent_name: str,
        jira_task_id: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> TaskMetrics:
        """
        Record the completion of a task.
        
        Args:
            agent_name: Name of the agent completing the task
            jira_task_id: Optional JIRA issue key
            metrics: Optional metrics dictionary with:
                - duration: Duration in milliseconds
                - iterations: Number of attempts
                - errors: List of error messages
                - effectivenessScore: Score 0-100
                
        Returns:
            Updated TaskMetrics object
        """
        task_id = self._generate_task_id(agent_name, jira_task_id)
        
        # Get or create task metrics
        if task_id in self._active_tasks:
            task_metrics = self._active_tasks[task_id]
        else:
            task_metrics = TaskMetrics(
                agent_name=agent_name,
                jira_task_id=jira_task_id,
            )
        
        # Update with completion data
        task_metrics.end_time = datetime.utcnow().isoformat()
        task_metrics.status = TaskStatus.COMPLETED.value
        
        if metrics:
            task_metrics.duration_ms = metrics.get("duration", 0)
            task_metrics.iterations = metrics.get("iterations", 1)
            task_metrics.errors = metrics.get("errors", [])
            task_metrics.effectiveness_score = metrics.get("effectivenessScore", 100.0)
            task_metrics.requires_human_review = metrics.get("requiresHumanReview", False)
            task_metrics.confidence_score = metrics.get("confidenceScore", 1.0)
        
        # Calculate duration if not provided
        if task_metrics.duration_ms == 0 and task_metrics.start_time:
            try:
                start = datetime.fromisoformat(task_metrics.start_time)
                end = datetime.fromisoformat(task_metrics.end_time)
                task_metrics.duration_ms = (end - start).total_seconds() * 1000
            except (ValueError, TypeError):
                pass
        
        # Calculate effectiveness score if not provided
        if task_metrics.effectiveness_score == 100.0:
            task_metrics.effectiveness_score = self._calculate_effectiveness_score(task_metrics)
        
        # Persist to log
        self._save_task_log(task_id, task_metrics)
        
        # Update JIRA if configured
        if self.config.get("auto_update_jira") and jira_task_id:
            self._update_jira_on_completion(jira_task_id, task_metrics)
        
        # Remove from active tasks
        if task_id in self._active_tasks:
            del self._active_tasks[task_id]
        
        # Trigger callback
        if self._on_task_completed:
            self._on_task_completed(task_metrics)
        
        logger.info(f"Task completed: {agent_name} - Score: {task_metrics.effectiveness_score:.1f}%")
        
        return task_metrics
    
    def on_task_failed(
        self,
        agent_name: str,
        jira_task_id: Optional[str] = None,
        errors: Optional[List[str]] = None
    ) -> TaskMetrics:
        """
        Record the failure of a task.
        
        Args:
            agent_name: Name of the agent that failed
            jira_task_id: Optional JIRA issue key
            errors: List of error messages
            
        Returns:
            Updated TaskMetrics object
        """
        task_id = self._generate_task_id(agent_name, jira_task_id)
        
        # Get or create task metrics
        if task_id in self._active_tasks:
            task_metrics = self._active_tasks[task_id]
        else:
            task_metrics = TaskMetrics(
                agent_name=agent_name,
                jira_task_id=jira_task_id,
            )
        
        # Update with failure data
        task_metrics.end_time = datetime.utcnow().isoformat()
        task_metrics.status = TaskStatus.FAILED.value
        task_metrics.errors = errors or []
        task_metrics.effectiveness_score = 0.0
        task_metrics.requires_human_review = True
        
        # Calculate duration
        if task_metrics.start_time:
            try:
                start = datetime.fromisoformat(task_metrics.start_time)
                end = datetime.fromisoformat(task_metrics.end_time)
                task_metrics.duration_ms = (end - start).total_seconds() * 1000
            except (ValueError, TypeError):
                pass
        
        # Persist to log
        self._save_task_log(task_id, task_metrics)
        
        # Update JIRA if configured
        if self.config.get("auto_update_jira") and jira_task_id:
            self._update_jira_on_failure(jira_task_id, task_metrics)
        
        # Remove from active tasks
        if task_id in self._active_tasks:
            del self._active_tasks[task_id]
        
        # Trigger callback
        if self._on_task_failed:
            self._on_task_failed(task_metrics)
        
        logger.warning(f"Task failed: {agent_name} - Errors: {len(task_metrics.errors)}")
        
        return task_metrics
    
    # ==================== JIRA Integration ====================
    
    def _update_jira_on_completion(self, jira_task_id: str, metrics: TaskMetrics):
        """Update JIRA issue on task completion."""
        if not self.jira_client:
            logger.warning("JIRA client not available, skipping update")
            return
        
        try:
            # Add comment
            if self.config.get("jira_comment_enabled"):
                comment = self._format_jira_comment(metrics)
                self.jira_client.add_comment(jira_task_id, comment)
            
            # Update custom fields
            if self.config.get("jira_custom_fields_enabled"):
                self.jira_client.update_ai_fields(
                    jira_task_id,
                    ai_used=True,
                    agent_name=metrics.agent_name,
                    efficiency_score=metrics.effectiveness_score,
                    duration_ms=metrics.duration_ms,
                )
        except Exception as e:
            logger.error(f"Failed to update JIRA {jira_task_id}: {e}")
    
    def _update_jira_on_failure(self, jira_task_id: str, metrics: TaskMetrics):
        """Update JIRA issue on task failure."""
        if not self.jira_client:
            logger.warning("JIRA client not available, skipping update")
            return
        
        try:
            # Add failure comment
            if self.config.get("jira_comment_enabled"):
                comment = self._format_jira_failure_comment(metrics)
                self.jira_client.add_comment(jira_task_id, comment)
        except Exception as e:
            logger.error(f"Failed to update JIRA {jira_task_id}: {e}")
    
    def _format_jira_comment(self, metrics: TaskMetrics) -> str:
        """Format JIRA comment for task completion."""
        duration_str = self._format_duration(metrics.duration_ms)
        error_str = f"{len(metrics.errors)} (auto-fixed)" if metrics.errors else "0"
        
        return f"""AI Agent Update - PG AI Squad

Agent: {metrics.agent_name}
Task: {metrics.task_name}
Status: Completed

Metrics:
- Duration: {duration_str}
- Iterations: {metrics.iterations}
- Errors: {error_str}
- Effectiveness Score: {metrics.effectiveness_score:.0f}%
- Human Review Required: {'Yes' if metrics.requires_human_review else 'No'}

AI Productivity Tracker Agent v1.0"""
    
    def _format_jira_failure_comment(self, metrics: TaskMetrics) -> str:
        """Format JIRA comment for task failure."""
        duration_str = self._format_duration(metrics.duration_ms)
        errors_list = "\n".join([f"  - {e}" for e in metrics.errors[:5]])
        
        return f"""AI Agent Update - PG AI Squad

Agent: {metrics.agent_name}
Task: {metrics.task_name}
Status: Failed

Metrics:
- Duration: {duration_str}
- Iterations: {metrics.iterations}
- Errors: {len(metrics.errors)}
{errors_list}
- Human Review Required: Yes

AI Productivity Tracker Agent v1.0"""
    
    # ==================== Reporting ====================
    
    def generate_agent_report(self, agent_name: str, days: int = 7) -> AgentReport:
        """
        Generate a performance report for a specific agent.
        
        Args:
            agent_name: Name of the agent
            days: Number of days to include in report
            
        Returns:
            AgentReport with aggregated metrics
        """
        tasks = self._load_tasks_for_period(days)
        agent_tasks = [t for t in tasks if t.agent_name == agent_name]
        
        if not agent_tasks:
            return AgentReport(agent_name=agent_name)
        
        completed = [t for t in agent_tasks if t.status == TaskStatus.COMPLETED.value]
        failed = [t for t in agent_tasks if t.status == TaskStatus.FAILED.value]
        
        total_duration = sum(t.duration_ms for t in completed)
        total_effectiveness = sum(t.effectiveness_score for t in completed)
        total_errors = sum(len(t.errors) for t in agent_tasks)
        review_count = sum(1 for t in agent_tasks if t.requires_human_review)
        
        return AgentReport(
            agent_name=agent_name,
            total_tasks=len(agent_tasks),
            completed_tasks=len(completed),
            failed_tasks=len(failed),
            average_duration_ms=total_duration / len(completed) if completed else 0,
            average_effectiveness_score=total_effectiveness / len(completed) if completed else 0,
            total_errors=total_errors,
            tasks_requiring_review=review_count,
        )
    
    def generate_sprint_report(
        self,
        sprint_name: str = "Current Sprint",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> SprintReport:
        """
        Generate a sprint-level analytics report.
        
        Args:
            sprint_name: Name of the sprint
            start_date: Start date (ISO format), defaults to 14 days ago
            end_date: End date (ISO format), defaults to today
            
        Returns:
            SprintReport with aggregated metrics
        """
        # Default to last 14 days if not specified
        if not end_date:
            end_date = datetime.utcnow().isoformat()
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=14)).isoformat()
        
        tasks = self._load_tasks_for_date_range(start_date, end_date)
        
        if not tasks:
            return SprintReport(
                sprint_name=sprint_name,
                start_date=start_date,
                end_date=end_date,
            )
        
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED.value]
        
        # Calculate agent distribution
        agent_dist: Dict[str, int] = {}
        for task in tasks:
            agent_dist[task.agent_name] = agent_dist.get(task.agent_name, 0) + 1
        
        # Calculate time saved
        time_saved = len(completed) * self.config.get("estimated_time_saved_per_task", 2.0)
        
        # Calculate average effectiveness
        total_effectiveness = sum(t.effectiveness_score for t in completed)
        avg_effectiveness = total_effectiveness / len(completed) if completed else 0
        
        # Generate trend data (daily)
        trend_data = self._generate_trend_data(tasks, start_date, end_date)
        
        return SprintReport(
            sprint_name=sprint_name,
            start_date=start_date,
            end_date=end_date,
            total_ai_tasks=len(tasks),
            average_effectiveness_score=avg_effectiveness,
            time_saved_hours=time_saved,
            agent_distribution=agent_dist,
            tasks_requiring_review=sum(1 for t in tasks if t.requires_human_review),
            trend_data=trend_data,
        )
    
    def list_analytics(
        self,
        days: int = 7,
        agent_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List stored analytics data.
        
        Args:
            days: Number of days to include
            agent_name: Optional filter by agent name
            status: Optional filter by status
            
        Returns:
            List of task metrics dictionaries
        """
        tasks = self._load_tasks_for_period(days)
        
        if agent_name:
            tasks = [t for t in tasks if t.agent_name == agent_name]
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return [t.to_dict() for t in tasks]
    
    def generate_markdown_report(self, days: int = 14) -> str:
        """
        Generate a markdown report suitable for Confluence upload.
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Markdown formatted report string
        """
        sprint_report = self.generate_sprint_report()
        
        # Get individual agent reports
        agent_names = list(sprint_report.agent_distribution.keys())
        agent_reports = [self.generate_agent_report(name, days) for name in agent_names]
        
        # Build markdown
        md = f"""# AI Productivity Report - {sprint_report.sprint_name}

**Report Period:** {sprint_report.start_date[:10]} to {sprint_report.end_date[:10]}

## Summary

| Metric | Value |
|--------|-------|
| Total AI Tasks | {sprint_report.total_ai_tasks} |
| Average Effectiveness | {sprint_report.average_effectiveness_score:.1f}% |
| Time Saved | {sprint_report.time_saved_hours:.1f} hours |
| Tasks Requiring Review | {sprint_report.tasks_requiring_review} |

## Agent Distribution

| Agent | Tasks |
|-------|-------|
"""
        for agent, count in sprint_report.agent_distribution.items():
            md += f"| {agent} | {count} |\n"
        
        md += "\n## Agent Performance\n\n"
        
        for report in agent_reports:
            md += f"""### {report.agent_name}

- Total Tasks: {report.total_tasks}
- Completed: {report.completed_tasks}
- Failed: {report.failed_tasks}
- Average Duration: {self._format_duration(report.average_duration_ms)}
- Average Effectiveness: {report.average_effectiveness_score:.1f}%
- Total Errors: {report.total_errors}

"""
        
        md += "\n---\n*Generated by AI Productivity Tracker Agent v1.0*\n"
        
        return md
    
    def generate_json_report(self, days: int = 14) -> Dict[str, Any]:
        """
        Generate a JSON report for API consumption.
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Dictionary with report data
        """
        sprint_report = self.generate_sprint_report()
        
        agent_names = list(sprint_report.agent_distribution.keys())
        agent_reports = [self.generate_agent_report(name, days) for name in agent_names]
        
        return {
            "reportType": "sprint",
            "generatedAt": datetime.utcnow().isoformat(),
            "sprint": sprint_report.to_dict(),
            "agents": [r.to_dict() for r in agent_reports],
            "tasks": self.list_analytics(days),
        }
    
    # ==================== Helper Methods ====================
    
    def _generate_task_id(self, agent_name: str, jira_task_id: Optional[str] = None) -> str:
        """Generate a unique task ID."""
        if jira_task_id:
            return f"{agent_name}_{jira_task_id}"
        return f"{agent_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    def _calculate_effectiveness_score(self, metrics: TaskMetrics) -> float:
        """
        Calculate effectiveness score based on metrics.
        
        Score is based on:
        - Number of iterations (fewer is better)
        - Number of errors (fewer is better)
        - Whether human review is required
        """
        score = 100.0
        
        # Deduct for iterations (max 30 points)
        if metrics.iterations > 1:
            score -= min((metrics.iterations - 1) * 10, 30)
        
        # Deduct for errors (max 40 points)
        if metrics.errors:
            score -= min(len(metrics.errors) * 10, 40)
        
        # Deduct for human review requirement
        if metrics.requires_human_review:
            score -= 20
        
        return max(score, 0)
    
    def _save_task_log(self, task_id: str, metrics: TaskMetrics):
        """Save task metrics to log file."""
        # Use date-based log files
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"analytics_{date_str}.json"
        
        # Load existing logs
        logs: List[Dict[str, Any]] = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
            except (json.JSONDecodeError, IOError):
                logs = []
        
        # Add or update task
        task_data = metrics.to_dict()
        task_data["taskId"] = task_id
        
        # Check if task already exists
        existing_idx = next(
            (i for i, t in enumerate(logs) if t.get("taskId") == task_id),
            None
        )
        
        if existing_idx is not None:
            logs[existing_idx] = task_data
        else:
            logs.append(task_data)
        
        # Save logs
        try:
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save task log: {e}")
    
    def _load_tasks_for_period(self, days: int) -> List[TaskMetrics]:
        """Load tasks from the last N days."""
        tasks: List[TaskMetrics] = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            log_file = self.log_dir / f"analytics_{date_str}.json"
            
            if log_file.exists():
                try:
                    with open(log_file, "r") as f:
                        logs = json.load(f)
                        for log in logs:
                            tasks.append(TaskMetrics.from_dict(log))
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load log file {log_file}: {e}")
        
        return tasks
    
    def _load_tasks_for_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[TaskMetrics]:
        """Load tasks within a date range."""
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            return []
        
        days = (end - start).days + 1
        all_tasks = self._load_tasks_for_period(days + 1)
        
        # Filter by date range
        filtered = []
        for task in all_tasks:
            if task.start_time:
                try:
                    task_date = datetime.fromisoformat(task.start_time.replace("Z", "+00:00"))
                    if start <= task_date <= end:
                        filtered.append(task)
                except ValueError:
                    continue
        
        return filtered
    
    def _generate_trend_data(
        self,
        tasks: List[TaskMetrics],
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Generate daily trend data."""
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            return []
        
        trend: List[Dict[str, Any]] = []
        current = start
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            day_tasks = [
                t for t in tasks
                if t.start_time and t.start_time.startswith(date_str)
            ]
            
            completed = [t for t in day_tasks if t.status == TaskStatus.COMPLETED.value]
            
            trend.append({
                "date": date_str,
                "totalTasks": len(day_tasks),
                "completedTasks": len(completed),
                "averageEffectiveness": (
                    sum(t.effectiveness_score for t in completed) / len(completed)
                    if completed else 0
                ),
            })
            
            current += timedelta(days=1)
        
        return trend
    
    def _format_duration(self, duration_ms: float) -> str:
        """Format duration in human-readable format."""
        if duration_ms < 1000:
            return f"{duration_ms:.0f}ms"
        elif duration_ms < 60000:
            return f"{duration_ms / 1000:.1f}s"
        elif duration_ms < 3600000:
            minutes = duration_ms / 60000
            seconds = (duration_ms % 60000) / 1000
            return f"{minutes:.0f}m {seconds:.0f}s"
        else:
            hours = duration_ms / 3600000
            return f"{hours:.1f}h"
    
    # ==================== MCP Tool Interface ====================
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the analytics agent with the given context.
        
        This is the main entry point for workflow integration.
        
        Args:
            context: Dictionary with task_description and input_data
            
        Returns:
            Dictionary with status and data
        """
        task_description = context.get("task_description", "")
        input_data = context.get("input_data", {})
        
        # Determine action based on input
        action = input_data.get("action", "report")
        
        if action == "track_start":
            metrics = self.on_task_started(
                agent_name=input_data.get("agent_name", "unknown"),
                task_description=input_data.get("task_description", task_description),
                jira_task_id=input_data.get("jira_task_id"),
                workflow_id=input_data.get("workflow_id"),
            )
            return {
                "status": "success",
                "data": metrics.to_dict(),
            }
        
        elif action == "track_end":
            metrics = self.on_task_completed(
                agent_name=input_data.get("agent_name", "unknown"),
                jira_task_id=input_data.get("jira_task_id"),
                metrics=input_data.get("metrics"),
            )
            return {
                "status": "success",
                "data": metrics.to_dict(),
            }
        
        elif action == "track_failure":
            metrics = self.on_task_failed(
                agent_name=input_data.get("agent_name", "unknown"),
                jira_task_id=input_data.get("jira_task_id"),
                errors=input_data.get("errors"),
            )
            return {
                "status": "success",
                "data": metrics.to_dict(),
            }
        
        elif action == "report":
            report = self.generate_json_report(
                days=input_data.get("days", 14)
            )
            return {
                "status": "success",
                "data": report,
            }
        
        elif action == "list":
            analytics = self.list_analytics(
                days=input_data.get("days", 7),
                agent_name=input_data.get("agent_name"),
                status=input_data.get("status"),
            )
            return {
                "status": "success",
                "data": {"tasks": analytics},
            }
        
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
            }


# Convenience functions for direct usage
def record_event(
    event_type: str,
    agent_name: str,
    task_description: str = "",
    jira_task_id: Optional[str] = None,
    metrics: Optional[Dict[str, Any]] = None,
    errors: Optional[List[str]] = None
) -> TaskMetrics:
    """
    Convenience function for recording analytics events.
    
    Can be imported and used by other agents:
        from agents.analytics_agent import record_event
        record_event("start", "frontend", "Create component", "EPA-123")
    
    Args:
        event_type: One of "start", "complete", "fail"
        agent_name: Name of the agent
        task_description: Description of the task
        jira_task_id: Optional JIRA issue key
        metrics: Optional metrics for completion
        errors: Optional error list for failure
        
    Returns:
        TaskMetrics object
    """
    agent = AnalyticsAgent()
    
    if event_type == "start":
        return agent.on_task_started(agent_name, task_description, jira_task_id)
    elif event_type == "complete":
        return agent.on_task_completed(agent_name, jira_task_id, metrics)
    elif event_type == "fail":
        return agent.on_task_failed(agent_name, jira_task_id, errors)
    else:
        raise ValueError(f"Unknown event type: {event_type}")
