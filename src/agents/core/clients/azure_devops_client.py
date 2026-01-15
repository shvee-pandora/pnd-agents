"""
Azure DevOps Client

Shared client for interacting with Azure DevOps REST APIs.
Used by pr_review_agent and other Azure DevOps-integrated agents.

Usage:
    from src.agents.core.clients.azure_devops_client import AzureDevOpsClient
    
    client = AzureDevOpsClient(pat="your_pat", organization="your_org")
    pr = client.get_pull_request(project="MyProject", repo="MyRepo", pr_id=123)
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pnd_agents.core.clients.azure_devops")


@dataclass
class PullRequestFile:
    """A file changed in a pull request."""
    path: str
    change_type: str  # add, edit, delete
    content: Optional[str] = None
    diff: Optional[str] = None


@dataclass
class PullRequestData:
    """Data for a pull request."""
    id: int
    title: str
    description: str = ""
    source_branch: str = ""
    target_branch: str = ""
    status: str = ""
    author: str = ""
    created_date: str = ""
    files: List[PullRequestFile] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)


class AzureDevOpsClient:
    """
    Client for Azure DevOps REST API.
    
    Provides methods for fetching pull requests, work items, and repository data.
    """
    
    def __init__(
        self,
        pat: Optional[str] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None
    ):
        """
        Initialize the Azure DevOps client.
        
        Args:
            pat: Personal Access Token (defaults to AZURE_DEVOPS_PAT env var)
            organization: Azure DevOps organization (defaults to AZURE_DEVOPS_ORG env var)
            project: Default project (defaults to AZURE_DEVOPS_PROJECT env var)
        """
        self.pat = pat or os.environ.get("AZURE_DEVOPS_PAT", "")
        self.organization = organization or os.environ.get("AZURE_DEVOPS_ORG", "")
        self.project = project or os.environ.get("AZURE_DEVOPS_PROJECT", "")
        self.base_url = f"https://dev.azure.com/{self.organization}"
    
    def get_pull_request(
        self,
        project: Optional[str] = None,
        repo: str = "",
        pr_id: int = 0
    ) -> PullRequestData:
        """
        Get pull request data.
        
        Args:
            project: Project name (uses default if not specified)
            repo: Repository name
            pr_id: Pull request ID
            
        Returns:
            PullRequestData with PR details and files.
        """
        raise NotImplementedError("AzureDevOpsClient.get_pull_request() not yet implemented")
    
    def get_pull_request_files(
        self,
        project: Optional[str] = None,
        repo: str = "",
        pr_id: int = 0
    ) -> List[PullRequestFile]:
        """
        Get files changed in a pull request.
        
        Args:
            project: Project name
            repo: Repository name
            pr_id: Pull request ID
            
        Returns:
            List of PullRequestFile objects.
        """
        raise NotImplementedError("AzureDevOpsClient.get_pull_request_files() not yet implemented")
    
    def parse_pr_url(self, url: str) -> Dict[str, Any]:
        """
        Parse an Azure DevOps PR URL to extract components.
        
        Args:
            url: Full Azure DevOps PR URL
            
        Returns:
            Dictionary with organization, project, repo, pr_id
        """
        raise NotImplementedError("AzureDevOpsClient.parse_pr_url() not yet implemented")


__all__ = ["AzureDevOpsClient", "PullRequestData", "PullRequestFile"]
