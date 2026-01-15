"""
SonarCloud/SonarQube Client

Shared client for interacting with SonarCloud and SonarQube APIs.
Used by sonar_validation_agent and other quality-focused agents.

Usage:
    from src.agents.core.clients.sonar_client import SonarClient
    
    client = SonarClient(token="your_token", organization="your_org")
    metrics = client.get_project_metrics("project_key")
    issues = client.get_issues("project_key", severities=["CRITICAL", "BLOCKER"])
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pnd_agents.core.clients.sonar")


@dataclass
class SonarMetrics:
    """Metrics from SonarCloud/SonarQube."""
    coverage: float = 0.0
    bugs: int = 0
    vulnerabilities: int = 0
    code_smells: int = 0
    duplicated_lines_density: float = 0.0
    reliability_rating: str = "A"
    security_rating: str = "A"
    maintainability_rating: str = "A"


@dataclass
class SonarIssue:
    """A single issue from SonarCloud/SonarQube."""
    key: str
    rule: str
    severity: str
    component: str
    line: Optional[int] = None
    message: str = ""
    effort: str = ""
    type: str = ""


class SonarClient:
    """
    Client for SonarCloud/SonarQube API.
    
    Provides methods for fetching project metrics, issues, and quality gate status.
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        organization: Optional[str] = None,
        base_url: str = "https://sonarcloud.io"
    ):
        """
        Initialize the SonarCloud client.
        
        Args:
            token: SonarCloud API token (defaults to SONAR_TOKEN env var)
            organization: SonarCloud organization (defaults to SONAR_ORG env var)
            base_url: Base URL for SonarCloud API
        """
        self.token = token or os.environ.get("SONAR_TOKEN", "")
        self.organization = organization or os.environ.get("SONAR_ORG", "")
        self.base_url = base_url.rstrip("/")
        
    def get_project_metrics(self, project_key: str) -> SonarMetrics:
        """
        Get metrics for a project.
        
        Args:
            project_key: The SonarCloud project key.
            
        Returns:
            SonarMetrics with coverage, bugs, vulnerabilities, etc.
        """
        raise NotImplementedError("SonarClient.get_project_metrics() not yet implemented")
    
    def get_issues(
        self,
        project_key: str,
        severities: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        resolved: bool = False
    ) -> List[SonarIssue]:
        """
        Get issues for a project.
        
        Args:
            project_key: The SonarCloud project key.
            severities: Filter by severity (BLOCKER, CRITICAL, MAJOR, MINOR, INFO)
            types: Filter by type (BUG, VULNERABILITY, CODE_SMELL)
            resolved: Include resolved issues
            
        Returns:
            List of SonarIssue objects.
        """
        raise NotImplementedError("SonarClient.get_issues() not yet implemented")
    
    def get_quality_gate_status(self, project_key: str) -> Dict[str, Any]:
        """
        Get quality gate status for a project.
        
        Args:
            project_key: The SonarCloud project key.
            
        Returns:
            Dictionary with quality gate status and conditions.
        """
        raise NotImplementedError("SonarClient.get_quality_gate_status() not yet implemented")


__all__ = ["SonarClient", "SonarMetrics", "SonarIssue"]
