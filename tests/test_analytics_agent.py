"""
Unit tests for the Analytics Agent.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analytics_agent import AnalyticsAgent, TaskMetrics, TaskStatus


class TestTaskMetrics:
    """Tests for TaskMetrics dataclass."""
    
    def test_to_dict(self):
        """Test TaskMetrics to_dict conversion."""
        metrics = TaskMetrics(
            agent_name="test_agent",
            task_name="Test Task",
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T00:01:00",
            duration_ms=60000,
            iterations=2,
            errors=["error1"],
            effectiveness_score=85.0,
            requires_human_review=False,
            confidence_score=0.95,
            jira_task_id="EPA-123",
            status="completed",
        )
        
        result = metrics.to_dict()
        
        assert result["agentName"] == "test_agent"
        assert result["taskName"] == "Test Task"
        assert result["duration"] == 60000
        assert result["iterations"] == 2
        assert result["errors"] == ["error1"]
        assert result["effectivenessScore"] == 85.0
        assert result["jiraTaskId"] == "EPA-123"
        assert result["status"] == "completed"
    
    def test_from_dict(self):
        """Test TaskMetrics from_dict creation."""
        data = {
            "agentName": "test_agent",
            "taskName": "Test Task",
            "startTime": "2024-01-01T00:00:00",
            "endTime": "2024-01-01T00:01:00",
            "duration": 60000,
            "iterations": 2,
            "errors": ["error1"],
            "effectivenessScore": 85.0,
            "requiresHumanReview": True,
            "confidenceScore": 0.95,
            "jiraTaskId": "EPA-123",
            "status": "completed",
        }
        
        metrics = TaskMetrics.from_dict(data)
        
        assert metrics.agent_name == "test_agent"
        assert metrics.task_name == "Test Task"
        assert metrics.duration_ms == 60000
        assert metrics.iterations == 2
        assert metrics.errors == ["error1"]
        assert metrics.effectiveness_score == 85.0
        assert metrics.requires_human_review is True
        assert metrics.jira_task_id == "EPA-123"


class TestAnalyticsAgent:
    """Tests for AnalyticsAgent class."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def agent(self, temp_log_dir):
        """Create an AnalyticsAgent with temporary log directory."""
        return AnalyticsAgent(log_dir=temp_log_dir)
    
    def test_init(self, temp_log_dir):
        """Test AnalyticsAgent initialization."""
        agent = AnalyticsAgent(log_dir=temp_log_dir)
        
        assert agent.log_dir == Path(temp_log_dir)
        assert agent.config is not None
        assert "jira_comment_enabled" in agent.config
    
    def test_on_task_started(self, agent):
        """Test on_task_started method."""
        metrics = agent.on_task_started(
            agent_name="Frontend Agent",
            task_description="Create component",
            jira_task_id="EPA-123",
        )
        
        assert metrics.agent_name == "Frontend Agent"
        assert metrics.task_name == "Create component"
        assert metrics.jira_task_id == "EPA-123"
        assert metrics.status == TaskStatus.STARTED.value
        assert metrics.start_time != ""
    
    def test_on_task_completed(self, agent):
        """Test on_task_completed method."""
        agent.on_task_started(
            agent_name="Frontend Agent",
            task_description="Create component",
            jira_task_id="EPA-123",
        )
        
        metrics = agent.on_task_completed(
            agent_name="Frontend Agent",
            jira_task_id="EPA-123",
            metrics={
                "duration": 5000,
                "iterations": 2,
                "errors": ["minor error"],
                "effectivenessScore": 90.0,
            },
        )
        
        assert metrics.status == TaskStatus.COMPLETED.value
        assert metrics.duration_ms == 5000
        assert metrics.iterations == 2
        assert metrics.errors == ["minor error"]
        assert metrics.effectiveness_score == 90.0
    
    def test_on_task_failed(self, agent):
        """Test on_task_failed method."""
        agent.on_task_started(
            agent_name="Frontend Agent",
            task_description="Create component",
            jira_task_id="EPA-123",
        )
        
        metrics = agent.on_task_failed(
            agent_name="Frontend Agent",
            jira_task_id="EPA-123",
            errors=["Critical error", "Another error"],
        )
        
        assert metrics.status == TaskStatus.FAILED.value
        assert metrics.errors == ["Critical error", "Another error"]
        assert metrics.effectiveness_score == 0.0
        assert metrics.requires_human_review is True
    
    def test_calculate_effectiveness_score(self, agent):
        """Test effectiveness score calculation."""
        metrics = TaskMetrics(
            agent_name="test",
            iterations=3,
            errors=["e1", "e2"],
            requires_human_review=True,
        )
        
        score = agent._calculate_effectiveness_score(metrics)
        
        assert score < 100
        assert score >= 0
    
    def test_format_duration(self, agent):
        """Test duration formatting."""
        assert agent._format_duration(500) == "500ms"
        assert agent._format_duration(5000) == "5.0s"
        assert agent._format_duration(65000) == "1m 5s"
        assert agent._format_duration(3700000) == "1.0h"
    
    def test_list_analytics(self, agent):
        """Test list_analytics method."""
        agent.on_task_started("Agent1", "Task 1")
        agent.on_task_completed("Agent1", metrics={"duration": 1000})
        
        agent.on_task_started("Agent2", "Task 2")
        agent.on_task_completed("Agent2", metrics={"duration": 2000})
        
        analytics = agent.list_analytics(days=1)
        
        assert len(analytics) >= 2
    
    def test_generate_json_report(self, agent):
        """Test JSON report generation."""
        agent.on_task_started("Agent1", "Task 1")
        agent.on_task_completed("Agent1", metrics={"duration": 1000})
        
        report = agent.generate_json_report(days=1)
        
        assert "reportType" in report
        assert "sprint" in report
        assert "agents" in report
        assert "tasks" in report
    
    def test_generate_markdown_report(self, agent):
        """Test markdown report generation."""
        agent.on_task_started("Agent1", "Task 1")
        agent.on_task_completed("Agent1", metrics={"duration": 1000})
        
        report = agent.generate_markdown_report(days=1)
        
        assert "# AI Productivity Report" in report
        assert "Summary" in report
    
    def test_run_track_start(self, agent):
        """Test run method with track_start action."""
        context = {
            "task_description": "Test task",
            "input_data": {
                "action": "track_start",
                "agent_name": "Test Agent",
                "task_description": "Test task",
            },
        }
        
        result = agent.run(context)
        
        assert result["status"] == "success"
        assert "data" in result
    
    def test_run_track_end(self, agent):
        """Test run method with track_end action."""
        agent.on_task_started("Test Agent", "Test task")
        
        context = {
            "task_description": "Test task",
            "input_data": {
                "action": "track_end",
                "agent_name": "Test Agent",
                "metrics": {"duration": 1000},
            },
        }
        
        result = agent.run(context)
        
        assert result["status"] == "success"
    
    def test_run_report(self, agent):
        """Test run method with report action."""
        context = {
            "task_description": "Generate report",
            "input_data": {
                "action": "report",
                "days": 7,
            },
        }
        
        result = agent.run(context)
        
        assert result["status"] == "success"
        assert "data" in result
    
    def test_run_list(self, agent):
        """Test run method with list action."""
        context = {
            "task_description": "List analytics",
            "input_data": {
                "action": "list",
                "days": 7,
            },
        }
        
        result = agent.run(context)
        
        assert result["status"] == "success"
        assert "data" in result
        assert "tasks" in result["data"]
    
    def test_run_unknown_action(self, agent):
        """Test run method with unknown action."""
        context = {
            "task_description": "Unknown",
            "input_data": {
                "action": "unknown_action",
            },
        }
        
        result = agent.run(context)
        
        assert result["status"] == "error"
        assert "Unknown action" in result["error"]


class TestJiraCommentFormatting:
    """Tests for JIRA comment formatting."""
    
    @pytest.fixture
    def agent(self):
        """Create an AnalyticsAgent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield AnalyticsAgent(log_dir=tmpdir)
    
    def test_format_jira_comment(self, agent):
        """Test JIRA comment formatting."""
        metrics = TaskMetrics(
            agent_name="Frontend Agent",
            task_name="Create Header Component",
            duration_ms=208000,
            iterations=4,
            errors=["minor error"],
            effectiveness_score=92.0,
            requires_human_review=False,
        )
        
        comment = agent._format_jira_comment(metrics)
        
        assert "Frontend Agent" in comment
        assert "Create Header Component" in comment
        assert "Completed" in comment
        assert "92%" in comment
        assert "4" in comment
        assert "1 (auto-fixed)" in comment
    
    def test_format_jira_failure_comment(self, agent):
        """Test JIRA failure comment formatting."""
        metrics = TaskMetrics(
            agent_name="Frontend Agent",
            task_name="Create Header Component",
            duration_ms=60000,
            iterations=3,
            errors=["Error 1", "Error 2"],
            effectiveness_score=0.0,
            requires_human_review=True,
        )
        
        comment = agent._format_jira_failure_comment(metrics)
        
        assert "Frontend Agent" in comment
        assert "Failed" in comment
        assert "Error 1" in comment
        assert "Human Review Required: Yes" in comment
