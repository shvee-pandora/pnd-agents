"""
Unit tests for the Analytics Store.
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.analytics_store import AnalyticsStore, AnalyticsEvent, record_event


class TestAnalyticsEvent:
    """Tests for AnalyticsEvent dataclass."""
    
    def test_to_dict(self):
        """Test AnalyticsEvent to_dict conversion."""
        event = AnalyticsEvent(
            event_id="test-123",
            event_type="task_completed",
            agent_name="Test Agent",
            timestamp="2024-01-01T00:00:00",
            data={"duration": 5000, "status": "success"},
        )
        
        result = event.to_dict()
        
        assert result["eventId"] == "test-123"
        assert result["eventType"] == "task_completed"
        assert result["agentName"] == "Test Agent"
        assert result["timestamp"] == "2024-01-01T00:00:00"
        assert result["data"]["duration"] == 5000
    
    def test_from_dict(self):
        """Test AnalyticsEvent from_dict creation."""
        data = {
            "eventId": "test-456",
            "eventType": "task_started",
            "agentName": "Another Agent",
            "timestamp": "2024-01-02T00:00:00",
            "data": {"task": "Test task"},
        }
        
        event = AnalyticsEvent.from_dict(data)
        
        assert event.event_id == "test-456"
        assert event.event_type == "task_started"
        assert event.agent_name == "Another Agent"
        assert event.data["task"] == "Test task"


class TestAnalyticsStore:
    """Tests for AnalyticsStore class."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def store(self, temp_log_dir):
        """Create an AnalyticsStore with temporary log directory."""
        return AnalyticsStore(log_dir=temp_log_dir)
    
    def test_init(self, temp_log_dir):
        """Test AnalyticsStore initialization."""
        store = AnalyticsStore(log_dir=temp_log_dir)
        
        assert store.log_dir == Path(temp_log_dir)
        assert store.retention_days == 90
    
    def test_init_custom_retention(self, temp_log_dir):
        """Test AnalyticsStore with custom retention."""
        store = AnalyticsStore(log_dir=temp_log_dir, retention_days=30)
        
        assert store.retention_days == 30
    
    def test_store_event(self, store):
        """Test store_event method."""
        event = AnalyticsEvent(
            event_id="test-event-1",
            event_type="task_started",
            agent_name="Test Agent",
            timestamp=datetime.utcnow().isoformat(),
            data={"task": "Test task"},
        )
        
        result = store.store_event(event)
        
        assert result is True
    
    def test_get_event(self, store):
        """Test get_event method."""
        timestamp = datetime.utcnow().isoformat()
        event = AnalyticsEvent(
            event_id="test-event-2",
            event_type="task_completed",
            agent_name="Test Agent",
            timestamp=timestamp,
            data={"duration": 5000},
        )
        
        store.store_event(event)
        retrieved = store.get_event("test-event-2")
        
        assert retrieved is not None
        assert retrieved.event_id == "test-event-2"
        assert retrieved.event_type == "task_completed"
    
    def test_get_event_not_found(self, store):
        """Test get_event for non-existent event."""
        retrieved = store.get_event("non-existent-event")
        
        assert retrieved is None
    
    def test_query_events(self, store):
        """Test query_events method."""
        timestamp = datetime.utcnow().isoformat()
        
        for i in range(5):
            event = AnalyticsEvent(
                event_id=f"query-test-{i}",
                event_type="task_completed" if i % 2 == 0 else "task_started",
                agent_name="Agent A" if i < 3 else "Agent B",
                timestamp=timestamp,
                data={"index": i},
            )
            store.store_event(event)
        
        all_events = store.query_events()
        assert len(all_events) >= 5
        
        completed_events = store.query_events(event_type="task_completed")
        assert all(e.event_type == "task_completed" for e in completed_events)
        
        agent_a_events = store.query_events(agent_name="Agent A")
        assert all(e.agent_name == "Agent A" for e in agent_a_events)
    
    def test_store_task_metrics(self, store):
        """Test store_task_metrics method."""
        metrics = {
            "agentName": "Test Agent",
            "taskName": "Test Task",
            "startTime": datetime.utcnow().isoformat(),
            "duration": 5000,
            "status": "completed",
        }
        
        result = store.store_task_metrics("task-123", metrics)
        
        assert result is True
    
    def test_get_task_metrics(self, store):
        """Test get_task_metrics method."""
        metrics = {
            "agentName": "Test Agent",
            "taskName": "Test Task",
            "startTime": datetime.utcnow().isoformat(),
            "duration": 5000,
            "status": "completed",
        }
        
        store.store_task_metrics("task-456", metrics)
        retrieved = store.get_task_metrics("task-456")
        
        assert retrieved is not None
        assert retrieved["agentName"] == "Test Agent"
        assert retrieved["duration"] == 5000
    
    def test_query_task_metrics(self, store):
        """Test query_task_metrics method."""
        for i in range(3):
            metrics = {
                "agentName": f"Agent {i % 2}",
                "taskName": f"Task {i}",
                "startTime": datetime.utcnow().isoformat(),
                "duration": 1000 * (i + 1),
                "status": "completed" if i < 2 else "failed",
            }
            store.store_task_metrics(f"query-task-{i}", metrics)
        
        all_metrics = store.query_task_metrics(days=1)
        assert len(all_metrics) >= 3
        
        agent_0_metrics = store.query_task_metrics(days=1, agent_name="Agent 0")
        assert all(m["agentName"] == "Agent 0" for m in agent_0_metrics)
        
        completed_metrics = store.query_task_metrics(days=1, status="completed")
        assert all(m["status"] == "completed" for m in completed_metrics)
    
    def test_get_agent_summary(self, store):
        """Test get_agent_summary method."""
        for i in range(3):
            metrics = {
                "agentName": "Summary Agent",
                "taskName": f"Task {i}",
                "startTime": datetime.utcnow().isoformat(),
                "duration": 1000 * (i + 1),
                "status": "completed",
                "effectivenessScore": 90 - i * 5,
                "errors": [],
            }
            store.store_task_metrics(f"summary-task-{i}", metrics)
        
        summary = store.get_agent_summary("Summary Agent", days=1)
        
        assert summary["agentName"] == "Summary Agent"
        assert summary["totalTasks"] >= 3
        assert summary["completedTasks"] >= 3
    
    def test_get_daily_summary(self, store):
        """Test get_daily_summary method."""
        for i in range(2):
            metrics = {
                "agentName": f"Daily Agent {i}",
                "taskName": f"Daily Task {i}",
                "startTime": datetime.utcnow().isoformat(),
                "duration": 1000,
                "status": "completed",
            }
            store.store_task_metrics(f"daily-task-{i}", metrics)
        
        summary = store.get_daily_summary()
        
        assert "date" in summary
        assert "totalTasks" in summary
        assert "agentDistribution" in summary
    
    def test_get_trend_data(self, store):
        """Test get_trend_data method."""
        metrics = {
            "agentName": "Trend Agent",
            "taskName": "Trend Task",
            "startTime": datetime.utcnow().isoformat(),
            "duration": 1000,
            "status": "completed",
        }
        store.store_task_metrics("trend-task-1", metrics)
        
        trend = store.get_trend_data(days=7)
        
        assert len(trend) == 7
        assert all("date" in d for d in trend)
        assert all("totalTasks" in d for d in trend)
    
    def test_get_storage_stats(self, store):
        """Test get_storage_stats method."""
        metrics = {
            "agentName": "Stats Agent",
            "taskName": "Stats Task",
            "startTime": datetime.utcnow().isoformat(),
            "duration": 1000,
            "status": "completed",
        }
        store.store_task_metrics("stats-task-1", metrics)
        
        stats = store.get_storage_stats()
        
        assert "totalFiles" in stats
        assert "totalSizeBytes" in stats
        assert "retentionDays" in stats
    
    def test_extract_date(self, store):
        """Test _extract_date helper method."""
        timestamp = "2024-01-15T10:30:00"
        date = store._extract_date(timestamp)
        
        assert date == "2024-01-15"
    
    def test_extract_date_invalid(self, store):
        """Test _extract_date with invalid timestamp."""
        date = store._extract_date("invalid")
        
        assert date == datetime.utcnow().strftime("%Y-%m-%d")


class TestRecordEventFunction:
    """Tests for record_event convenience function."""
    
    def test_record_event_started(self):
        """Test record_event for task_started."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(
                    "tools.analytics_store.AnalyticsStore.__init__",
                    lambda self, **kwargs: setattr(self, "log_dir", Path(tmpdir)) or setattr(self, "retention_days", 90)
                )
                
                result = record_event(
                    event_type="task_started",
                    agent_name="Test Agent",
                    task_description="Test task",
                )
                
                assert result is True
    
    def test_record_event_completed(self):
        """Test record_event for task_completed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(
                    "tools.analytics_store.AnalyticsStore.__init__",
                    lambda self, **kwargs: setattr(self, "log_dir", Path(tmpdir)) or setattr(self, "retention_days", 90)
                )
                
                result = record_event(
                    event_type="task_completed",
                    agent_name="Test Agent",
                    task_description="Test task",
                    metrics={"duration": 5000},
                )
                
                assert result is True
    
    def test_record_event_failed(self):
        """Test record_event for task_failed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(
                    "tools.analytics_store.AnalyticsStore.__init__",
                    lambda self, **kwargs: setattr(self, "log_dir", Path(tmpdir)) or setattr(self, "retention_days", 90)
                )
                
                result = record_event(
                    event_type="task_failed",
                    agent_name="Test Agent",
                    task_description="Test task",
                    errors=["Error 1", "Error 2"],
                )
                
                assert result is True
