"""
Jira Client

Shared client for interacting with Jira REST APIs.
Used by analytics_agent, prd_to_jira_agent, and other Jira-integrated agents.

Usage:
    from src.agents.core.clients.jira_client import JiraClient
    
    client = JiraClient(email="your@email.com", token="your_token")
    issues = client.get_sprint_issues(board_id=123, sprint_id=456)
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pnd_agents.core.clients.jira")


@dataclass
class JiraIssue:
    """A Jira issue."""
    key: str
    summary: str
    status: str = ""
    issue_type: str = ""
    assignee: Optional[str] = None
    story_points: Optional[float] = None
    labels: List[str] = field(default_factory=list)
    created: str = ""
    updated: str = ""


@dataclass
class JiraSprint:
    """A Jira sprint."""
    id: int
    name: str
    state: str = ""  # active, closed, future
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    goal: str = ""


class JiraClient:
    """
    Client for Jira REST API.
    
    Provides methods for fetching issues, sprints, and boards.
    """
    
    def __init__(
        self,
        email: Optional[str] = None,
        token: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize the Jira client.
        
        Args:
            email: Jira account email (defaults to JIRA_EMAIL env var)
            token: Jira API token (defaults to JIRA_API_TOKEN env var)
            base_url: Jira base URL (defaults to JIRA_BASE_URL env var)
        """
        self.email = email or os.environ.get("JIRA_EMAIL", "")
        self.token = token or os.environ.get("JIRA_API_TOKEN", "")
        self.base_url = (base_url or os.environ.get("JIRA_BASE_URL", "")).rstrip("/")
    
    def get_issue(self, issue_key: str) -> JiraIssue:
        """
        Get a single Jira issue.
        
        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            
        Returns:
            JiraIssue with issue details.
        """
        raise NotImplementedError("JiraClient.get_issue() not yet implemented")
    
    def get_sprint_issues(
        self,
        board_id: int,
        sprint_id: Optional[int] = None
    ) -> List[JiraIssue]:
        """
        Get issues in a sprint.
        
        Args:
            board_id: Jira board ID
            sprint_id: Sprint ID (uses active sprint if not specified)
            
        Returns:
            List of JiraIssue objects.
        """
        raise NotImplementedError("JiraClient.get_sprint_issues() not yet implemented")
    
    def get_active_sprint(self, board_id: int) -> Optional[JiraSprint]:
        """
        Get the active sprint for a board.
        
        Args:
            board_id: Jira board ID
            
        Returns:
            JiraSprint if active sprint exists, None otherwise.
        """
        raise NotImplementedError("JiraClient.get_active_sprint() not yet implemented")
    
    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Story",
        description: str = "",
        labels: Optional[List[str]] = None
    ) -> JiraIssue:
        """
        Create a new Jira issue.
        
        Args:
            project_key: Project key (e.g., "PROJ")
            summary: Issue summary
            issue_type: Issue type (Story, Task, Bug, etc.)
            description: Issue description
            labels: Issue labels
            
        Returns:
            Created JiraIssue.
        """
        raise NotImplementedError("JiraClient.create_issue() not yet implemented")


__all__ = ["JiraClient", "JiraIssue", "JiraSprint"]
