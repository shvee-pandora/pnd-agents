"""
Analytics Store Tool

Provides persistent storage and retrieval of analytics data for the Analytics Agent.
Supports JSON file-based storage with date-based partitioning.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("pnd_agents.analytics_store")


@dataclass
class AnalyticsEvent:
    """Represents a single analytics event."""
    event_id: str
    event_type: str  # task_started, task_completed, task_failed
    agent_name: str
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "eventId": self.event_id,
            "eventType": self.event_type,
            "agentName": self.agent_name,
            "timestamp": self.timestamp,
            "data": self.data,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalyticsEvent":
        """Create event from dictionary."""
        return cls(
            event_id=data.get("eventId", ""),
            event_type=data.get("eventType", ""),
            agent_name=data.get("agentName", ""),
            timestamp=data.get("timestamp", ""),
            data=data.get("data", {}),
        )


class AnalyticsStore:
    """
    Persistent storage for analytics data.
    
    Features:
    - Date-based file partitioning
    - Automatic log rotation
    - Query support with filtering
    - Aggregation helpers
    """
    
    DEFAULT_LOG_DIR = "logs/agent-analytics"
    
    def __init__(
        self,
        log_dir: Optional[str] = None,
        retention_days: int = 90
    ):
        """
        Initialize the analytics store.
        
        Args:
            log_dir: Directory for storing analytics logs
            retention_days: Number of days to retain logs
        """
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            base_dir = Path(__file__).parent.parent
            self.log_dir = base_dir / "logs" / "agent-analytics"
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        
        logger.info(f"Analytics store initialized at {self.log_dir}")
    
    # ==================== Event Storage ====================
    
    def store_event(self, event: AnalyticsEvent) -> bool:
        """
        Store an analytics event.
        
        Args:
            event: AnalyticsEvent to store
            
        Returns:
            True if successful
        """
        try:
            # Get date-based log file
            date_str = self._extract_date(event.timestamp)
            log_file = self.log_dir / f"events_{date_str}.json"
            
            # Load existing events
            events = self._load_file(log_file)
            
            # Add or update event
            existing_idx = next(
                (i for i, e in enumerate(events) if e.get("eventId") == event.event_id),
                None
            )
            
            if existing_idx is not None:
                events[existing_idx] = event.to_dict()
            else:
                events.append(event.to_dict())
            
            # Save events
            self._save_file(log_file, events)
            
            logger.debug(f"Stored event {event.event_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store event: {e}")
            return False
    
    def get_event(self, event_id: str, date: Optional[str] = None) -> Optional[AnalyticsEvent]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: Event ID to retrieve
            date: Optional date hint (YYYY-MM-DD) for faster lookup
            
        Returns:
            AnalyticsEvent or None if not found
        """
        if date:
            dates = [date]
        else:
            # Search recent dates
            dates = [
                (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(7)
            ]
        
        for date_str in dates:
            log_file = self.log_dir / f"events_{date_str}.json"
            if log_file.exists():
                events = self._load_file(log_file)
                for event_data in events:
                    if event_data.get("eventId") == event_id:
                        return AnalyticsEvent.from_dict(event_data)
        
        return None
    
    def query_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_type: Optional[str] = None,
        agent_name: Optional[str] = None,
        limit: int = 100
    ) -> List[AnalyticsEvent]:
        """
        Query events with filters.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            event_type: Filter by event type
            agent_name: Filter by agent name
            limit: Maximum number of results
            
        Returns:
            List of matching AnalyticsEvent objects
        """
        # Default to last 7 days
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        results: List[AnalyticsEvent] = []
        
        # Iterate through date range
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current <= end and len(results) < limit:
            date_str = current.strftime("%Y-%m-%d")
            log_file = self.log_dir / f"events_{date_str}.json"
            
            if log_file.exists():
                events = self._load_file(log_file)
                for event_data in events:
                    if len(results) >= limit:
                        break
                    
                    # Apply filters
                    if event_type and event_data.get("eventType") != event_type:
                        continue
                    if agent_name and event_data.get("agentName") != agent_name:
                        continue
                    
                    results.append(AnalyticsEvent.from_dict(event_data))
            
            current += timedelta(days=1)
        
        return results
    
    # ==================== Task Metrics Storage ====================
    
    def store_task_metrics(
        self,
        task_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Store task metrics.
        
        Args:
            task_id: Unique task identifier
            metrics: Metrics dictionary
            
        Returns:
            True if successful
        """
        try:
            # Get date from metrics or use current date
            timestamp = metrics.get("startTime", datetime.utcnow().isoformat())
            date_str = self._extract_date(timestamp)
            log_file = self.log_dir / f"analytics_{date_str}.json"
            
            # Load existing metrics
            all_metrics = self._load_file(log_file)
            
            # Add task ID to metrics
            metrics["taskId"] = task_id
            
            # Add or update metrics
            existing_idx = next(
                (i for i, m in enumerate(all_metrics) if m.get("taskId") == task_id),
                None
            )
            
            if existing_idx is not None:
                all_metrics[existing_idx] = metrics
            else:
                all_metrics.append(metrics)
            
            # Save metrics
            self._save_file(log_file, all_metrics)
            
            logger.debug(f"Stored metrics for task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store task metrics: {e}")
            return False
    
    def get_task_metrics(
        self,
        task_id: str,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific task.
        
        Args:
            task_id: Task ID to retrieve
            date: Optional date hint (YYYY-MM-DD)
            
        Returns:
            Metrics dictionary or None if not found
        """
        if date:
            dates = [date]
        else:
            dates = [
                (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(7)
            ]
        
        for date_str in dates:
            log_file = self.log_dir / f"analytics_{date_str}.json"
            if log_file.exists():
                all_metrics = self._load_file(log_file)
                for metrics in all_metrics:
                    if metrics.get("taskId") == task_id:
                        return metrics
        
        return None
    
    def query_task_metrics(
        self,
        days: int = 7,
        agent_name: Optional[str] = None,
        status: Optional[str] = None,
        jira_task_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query task metrics with filters.
        
        Args:
            days: Number of days to include
            agent_name: Filter by agent name
            status: Filter by status
            jira_task_id: Filter by JIRA task ID
            
        Returns:
            List of metrics dictionaries
        """
        results: List[Dict[str, Any]] = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            log_file = self.log_dir / f"analytics_{date_str}.json"
            
            if log_file.exists():
                all_metrics = self._load_file(log_file)
                for metrics in all_metrics:
                    # Apply filters
                    if agent_name and metrics.get("agentName") != agent_name:
                        continue
                    if status and metrics.get("status") != status:
                        continue
                    if jira_task_id and metrics.get("jiraTaskId") != jira_task_id:
                        continue
                    
                    results.append(metrics)
        
        return results
    
    # ==================== Aggregation ====================
    
    def get_agent_summary(
        self,
        agent_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get aggregated summary for an agent.
        
        Args:
            agent_name: Agent name
            days: Number of days to include
            
        Returns:
            Summary dictionary
        """
        metrics = self.query_task_metrics(days=days, agent_name=agent_name)
        
        if not metrics:
            return {
                "agentName": agent_name,
                "totalTasks": 0,
                "completedTasks": 0,
                "failedTasks": 0,
                "averageDuration": 0,
                "averageEffectiveness": 0,
                "totalErrors": 0,
            }
        
        completed = [m for m in metrics if m.get("status") == "completed"]
        failed = [m for m in metrics if m.get("status") == "failed"]
        
        total_duration = sum(m.get("duration", 0) for m in completed)
        total_effectiveness = sum(m.get("effectivenessScore", 0) for m in completed)
        total_errors = sum(len(m.get("errors", [])) for m in metrics)
        
        return {
            "agentName": agent_name,
            "totalTasks": len(metrics),
            "completedTasks": len(completed),
            "failedTasks": len(failed),
            "averageDuration": total_duration / len(completed) if completed else 0,
            "averageEffectiveness": total_effectiveness / len(completed) if completed else 0,
            "totalErrors": total_errors,
        }
    
    def get_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary for a specific day.
        
        Args:
            date: Date (YYYY-MM-DD), defaults to today
            
        Returns:
            Daily summary dictionary
        """
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        log_file = self.log_dir / f"analytics_{date}.json"
        
        if not log_file.exists():
            return {
                "date": date,
                "totalTasks": 0,
                "completedTasks": 0,
                "failedTasks": 0,
                "agentDistribution": {},
            }
        
        metrics = self._load_file(log_file)
        
        completed = [m for m in metrics if m.get("status") == "completed"]
        failed = [m for m in metrics if m.get("status") == "failed"]
        
        # Agent distribution
        agent_dist: Dict[str, int] = {}
        for m in metrics:
            agent = m.get("agentName", "unknown")
            agent_dist[agent] = agent_dist.get(agent, 0) + 1
        
        return {
            "date": date,
            "totalTasks": len(metrics),
            "completedTasks": len(completed),
            "failedTasks": len(failed),
            "agentDistribution": agent_dist,
        }
    
    def get_trend_data(self, days: int = 14) -> List[Dict[str, Any]]:
        """
        Get trend data for the specified period.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of daily summaries
        """
        trend = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            summary = self.get_daily_summary(date_str)
            trend.append(summary)
        
        # Reverse to get chronological order
        trend.reverse()
        return trend
    
    # ==================== Maintenance ====================
    
    def cleanup_old_logs(self) -> int:
        """
        Remove logs older than retention period.
        
        Returns:
            Number of files removed
        """
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        removed = 0
        
        for log_file in self.log_dir.glob("*.json"):
            try:
                # Extract date from filename
                name = log_file.stem
                date_part = name.split("_")[-1]
                file_date = datetime.strptime(date_part, "%Y-%m-%d")
                
                if file_date < cutoff:
                    log_file.unlink()
                    removed += 1
                    logger.info(f"Removed old log file: {log_file.name}")
            except (ValueError, IndexError):
                continue
        
        return removed
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Statistics dictionary
        """
        total_files = 0
        total_size = 0
        oldest_date = None
        newest_date = None
        
        for log_file in self.log_dir.glob("*.json"):
            total_files += 1
            total_size += log_file.stat().st_size
            
            try:
                name = log_file.stem
                date_part = name.split("_")[-1]
                file_date = datetime.strptime(date_part, "%Y-%m-%d")
                
                if oldest_date is None or file_date < oldest_date:
                    oldest_date = file_date
                if newest_date is None or file_date > newest_date:
                    newest_date = file_date
            except (ValueError, IndexError):
                continue
        
        return {
            "totalFiles": total_files,
            "totalSizeBytes": total_size,
            "totalSizeMB": round(total_size / (1024 * 1024), 2),
            "oldestDate": oldest_date.strftime("%Y-%m-%d") if oldest_date else None,
            "newestDate": newest_date.strftime("%Y-%m-%d") if newest_date else None,
            "retentionDays": self.retention_days,
        }
    
    # ==================== Helper Methods ====================
    
    def _extract_date(self, timestamp: str) -> str:
        """Extract date from ISO timestamp."""
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return datetime.utcnow().strftime("%Y-%m-%d")
    
    def _load_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load JSON file."""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load {file_path}: {e}")
            return []
    
    def _save_file(self, file_path: Path, data: List[Dict[str, Any]]):
        """Save JSON file."""
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save {file_path}: {e}")
            raise


# Convenience function for recording events
def record_event(
    event_type: str,
    agent_name: str,
    task_description: str = "",
    jira_task_id: Optional[str] = None,
    metrics: Optional[Dict[str, Any]] = None,
    errors: Optional[List[str]] = None
) -> bool:
    """
    Convenience function for recording analytics events.
    
    Can be imported and used by other agents:
        from tools.analytics_store import record_event
        record_event("task_started", "frontend", "Create component", "EPA-123")
    
    Args:
        event_type: One of "task_started", "task_completed", "task_failed"
        agent_name: Name of the agent
        task_description: Description of the task
        jira_task_id: Optional JIRA issue key
        metrics: Optional metrics dictionary
        errors: Optional error list
        
    Returns:
        True if successful
    """
    store = AnalyticsStore()
    
    event_id = f"{agent_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    if jira_task_id:
        event_id = f"{agent_name}_{jira_task_id}"
    
    event_data: Dict[str, Any] = {
        "taskDescription": task_description,
        "jiraTaskId": jira_task_id,
    }
    
    if metrics:
        event_data.update(metrics)
    
    if errors:
        event_data["errors"] = errors
    
    event = AnalyticsEvent(
        event_id=event_id,
        event_type=event_type,
        agent_name=agent_name,
        timestamp=datetime.utcnow().isoformat(),
        data=event_data,
    )
    
    return store.store_event(event)
