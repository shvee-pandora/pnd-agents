"""
Azure DevOps PR Client

A client for fetching Pull Request data from Azure DevOps REST API.
Supports fetching PR metadata, changed files, diffs, and comments.

Used by the PR Review Agent to analyze PRs without cloning the repository.
"""

import base64
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger("pnd_agents.azure_devops_pr_client")


class PRStatus(Enum):
    """Pull Request status."""
    ACTIVE = "active"
    ABANDONED = "abandoned"
    COMPLETED = "completed"
    ALL = "all"


class MergeStatus(Enum):
    """Pull Request merge status."""
    NOT_SET = "notSet"
    QUEUED = "queued"
    CONFLICTS = "conflicts"
    SUCCEEDED = "succeeded"
    REJECTED_BY_POLICY = "rejectedByPolicy"
    FAILURE = "failure"


@dataclass
class PRReviewer:
    """Pull Request reviewer information."""
    id: str
    display_name: str
    unique_name: str
    vote: int
    is_required: bool = False
    
    @property
    def vote_status(self) -> str:
        """Get human-readable vote status."""
        vote_map = {
            10: "Approved",
            5: "Approved with suggestions",
            0: "No vote",
            -5: "Waiting for author",
            -10: "Rejected",
        }
        return vote_map.get(self.vote, "Unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "displayName": self.display_name,
            "uniqueName": self.unique_name,
            "vote": self.vote,
            "voteStatus": self.vote_status,
            "isRequired": self.is_required,
        }


@dataclass
class PRFileChange:
    """Represents a file change in a Pull Request."""
    path: str
    original_path: Optional[str]
    change_type: str
    content: Optional[str] = None
    original_content: Optional[str] = None
    
    @property
    def extension(self) -> str:
        """Get file extension."""
        if "." in self.path:
            return self.path.rsplit(".", 1)[-1].lower()
        return ""
    
    @property
    def is_added(self) -> bool:
        return self.change_type.lower() in ["add", "added"]
    
    @property
    def is_deleted(self) -> bool:
        return self.change_type.lower() in ["delete", "deleted"]
    
    @property
    def is_modified(self) -> bool:
        return self.change_type.lower() in ["edit", "modified", "rename"]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "originalPath": self.original_path,
            "changeType": self.change_type,
            "extension": self.extension,
            "hasContent": self.content is not None,
        }


@dataclass
class PRDiff:
    """Represents a diff for a file in a Pull Request."""
    path: str
    original_path: Optional[str]
    change_type: str
    blocks: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "originalPath": self.original_path,
            "changeType": self.change_type,
            "blocks": self.blocks,
        }


@dataclass
class PRMetadata:
    """Pull Request metadata."""
    pr_id: int
    title: str
    description: str
    status: str
    created_by: str
    created_date: str
    source_branch: str
    target_branch: str
    repository_name: str
    repository_id: str
    project_name: str
    organization: str
    url: str
    merge_status: str
    is_draft: bool
    reviewers: List[PRReviewer] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    work_items: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prId": self.pr_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "createdBy": self.created_by,
            "createdDate": self.created_date,
            "sourceBranch": self.source_branch,
            "targetBranch": self.target_branch,
            "repositoryName": self.repository_name,
            "repositoryId": self.repository_id,
            "projectName": self.project_name,
            "organization": self.organization,
            "url": self.url,
            "mergeStatus": self.merge_status,
            "isDraft": self.is_draft,
            "reviewers": [r.to_dict() for r in self.reviewers],
            "labels": self.labels,
            "workItems": self.work_items,
        }


@dataclass
class PRReviewData:
    """Complete PR data for review."""
    metadata: PRMetadata
    files: List[PRFileChange] = field(default_factory=list)
    diffs: List[PRDiff] = field(default_factory=list)
    
    @property
    def total_files_changed(self) -> int:
        return len(self.files)
    
    @property
    def files_added(self) -> int:
        return sum(1 for f in self.files if f.is_added)
    
    @property
    def files_modified(self) -> int:
        return sum(1 for f in self.files if f.is_modified)
    
    @property
    def files_deleted(self) -> int:
        return sum(1 for f in self.files if f.is_deleted)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "files": [f.to_dict() for f in self.files],
            "diffs": [d.to_dict() for d in self.diffs],
            "summary": {
                "totalFilesChanged": self.total_files_changed,
                "filesAdded": self.files_added,
                "filesModified": self.files_modified,
                "filesDeleted": self.files_deleted,
            },
        }


@dataclass
class AzureDevOpsConfig:
    """Configuration for Azure DevOps API access."""
    organization: str = ""
    project: str = ""
    pat: str = ""
    
    @classmethod
    def from_env(cls) -> "AzureDevOpsConfig":
        """Create config from environment variables."""
        return cls(
            organization=os.environ.get("AZURE_DEVOPS_ORG", "pandora-jewelry"),
            project=os.environ.get("AZURE_DEVOPS_PROJECT", "Spark"),
            pat=os.environ.get("AZURE_DEVOPS_PAT", "") or os.environ.get("AZURE_DEVOPS_TOKEN", ""),
        )


class AzureDevOpsPRClient:
    """
    Client for fetching Pull Request data from Azure DevOps.
    
    Supports:
    - Fetching PR metadata (title, description, reviewers, etc.)
    - Fetching changed files list
    - Fetching file diffs
    - Fetching file contents
    
    Example usage:
        client = AzureDevOpsPRClient()
        pr_data = client.get_pr_for_review(
            "https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034"
        )
    """
    
    API_VERSION = "7.0"
    
    def __init__(self, config: Optional[AzureDevOpsConfig] = None):
        """
        Initialize the Azure DevOps PR client.
        
        Args:
            config: Azure DevOps configuration. If not provided, reads from environment.
        """
        self.config = config or AzureDevOpsConfig.from_env()
        self._client: Optional[httpx.Client] = None
    
    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            if not self.config.pat:
                raise ValueError(
                    "Azure DevOps PAT not configured. "
                    "Set AZURE_DEVOPS_PAT or AZURE_DEVOPS_TOKEN environment variable."
                )
            credentials = base64.b64encode(f":{self.config.pat}".encode()).decode()
            self._client = httpx.Client(
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
                follow_redirects=False,
            )
        return self._client
    
    def _handle_response(self, response: httpx.Response, url: str) -> None:
        """Handle HTTP response and raise appropriate errors."""
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get("Location", "")
            if "_signin" in location or "login" in location.lower():
                raise PermissionError(
                    f"Authentication failed for Azure DevOps API. "
                    f"The PAT may not have access to this project/repository, "
                    f"or the PAT has expired. URL: {url}"
                )
            raise httpx.HTTPStatusError(
                f"Redirect response '{response.status_code}' for url '{url}'. "
                f"Redirect location: '{location}'",
                request=response.request,
                response=response,
            )
        response.raise_for_status()
    
    def close(self):
        """Close HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def parse_pr_url(self, url: str) -> Tuple[str, str, str, int]:
        """
        Parse Azure DevOps PR URL to extract components.
        
        Args:
            url: PR URL like https://dev.azure.com/org/project/_git/repo/pullrequest/123
            
        Returns:
            Tuple of (organization, project, repository, pr_id)
            
        Raises:
            ValueError: If URL format is invalid
        """
        patterns = [
            r"https://dev\.azure\.com/([^/]+)/([^/]+)/_git/([^/]+)/pullrequest/(\d+)",
            r"https://([^.]+)\.visualstudio\.com/([^/]+)/_git/([^/]+)/pullrequest/(\d+)",
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                org, project, repo, pr_id = match.groups()
                return org, project, repo, int(pr_id)
        
        raise ValueError(
            f"Invalid Azure DevOps PR URL format: {url}. "
            "Expected format: https://dev.azure.com/org/project/_git/repo/pullrequest/123"
        )
    
    def _get_api_base(self, organization: str, project: str) -> str:
        """Get API base URL for a specific org/project."""
        return f"https://dev.azure.com/{organization}/{project}/_apis"
    
    def get_pr_metadata(
        self,
        organization: str,
        project: str,
        repository: str,
        pr_id: int,
    ) -> PRMetadata:
        """
        Fetch PR metadata from Azure DevOps.
        
        Args:
            organization: Azure DevOps organization
            project: Project name
            repository: Repository name
            pr_id: Pull Request ID
            
        Returns:
            PRMetadata object with PR details
        """
        api_base = self._get_api_base(organization, project)
        url = f"{api_base}/git/repositories/{repository}/pullrequests/{pr_id}"
        
        response = self.client.get(url, params={"api-version": self.API_VERSION})
        self._handle_response(response, url)
        data = response.json()
        
        reviewers = []
        for reviewer in data.get("reviewers", []):
            reviewers.append(PRReviewer(
                id=reviewer.get("id", ""),
                display_name=reviewer.get("displayName", ""),
                unique_name=reviewer.get("uniqueName", ""),
                vote=reviewer.get("vote", 0),
                is_required=reviewer.get("isRequired", False),
            ))
        
        labels = [label.get("name", "") for label in data.get("labels", [])]
        
        source_branch = data.get("sourceRefName", "").replace("refs/heads/", "")
        target_branch = data.get("targetRefName", "").replace("refs/heads/", "")
        
        return PRMetadata(
            pr_id=data.get("pullRequestId", pr_id),
            title=data.get("title", ""),
            description=data.get("description", ""),
            status=data.get("status", ""),
            created_by=data.get("createdBy", {}).get("displayName", ""),
            created_date=data.get("creationDate", ""),
            source_branch=source_branch,
            target_branch=target_branch,
            repository_name=data.get("repository", {}).get("name", repository),
            repository_id=data.get("repository", {}).get("id", ""),
            project_name=project,
            organization=organization,
            url=data.get("url", ""),
            merge_status=data.get("mergeStatus", ""),
            is_draft=data.get("isDraft", False),
            reviewers=reviewers,
            labels=labels,
            work_items=[],
        )
    
    def get_pr_iterations(
        self,
        organization: str,
        project: str,
        repository: str,
        pr_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Get PR iterations (commits/updates).
        
        Args:
            organization: Azure DevOps organization
            project: Project name
            repository: Repository name
            pr_id: Pull Request ID
            
        Returns:
            List of iteration data
        """
        api_base = self._get_api_base(organization, project)
        url = f"{api_base}/git/repositories/{repository}/pullrequests/{pr_id}/iterations"
        
        response = self.client.get(url, params={"api-version": self.API_VERSION})
        self._handle_response(response, url)
        data = response.json()
        
        return data.get("value", [])
    
    def get_pr_changes(
        self,
        organization: str,
        project: str,
        repository: str,
        pr_id: int,
        iteration_id: Optional[int] = None,
    ) -> List[PRFileChange]:
        """
        Get list of changed files in a PR.
        
        Args:
            organization: Azure DevOps organization
            project: Project name
            repository: Repository name
            pr_id: Pull Request ID
            iteration_id: Optional iteration ID (defaults to latest)
            
        Returns:
            List of PRFileChange objects
        """
        if iteration_id is None:
            iterations = self.get_pr_iterations(organization, project, repository, pr_id)
            if iterations:
                iteration_id = iterations[-1].get("id")
        
        if iteration_id is None:
            return []
        
        api_base = self._get_api_base(organization, project)
        url = f"{api_base}/git/repositories/{repository}/pullrequests/{pr_id}/iterations/{iteration_id}/changes"
        
        response = self.client.get(url, params={"api-version": self.API_VERSION})
        self._handle_response(response, url)
        data = response.json()
        
        changes = []
        for change_entry in data.get("changeEntries", []):
            item = change_entry.get("item", {})
            changes.append(PRFileChange(
                path=item.get("path", ""),
                original_path=change_entry.get("originalPath"),
                change_type=change_entry.get("changeType", ""),
            ))
        
        return changes
    
    def get_file_content(
        self,
        organization: str,
        project: str,
        repository: str,
        path: str,
        version: str,
        version_type: str = "branch",
    ) -> Optional[str]:
        """
        Get file content from repository.
        
        Args:
            organization: Azure DevOps organization
            project: Project name
            repository: Repository name
            path: File path
            version: Branch name or commit ID
            version_type: "branch" or "commit"
            
        Returns:
            File content as string, or None if not found
        """
        api_base = self._get_api_base(organization, project)
        url = f"{api_base}/git/repositories/{repository}/items"
        
        params = {
            "path": path,
            "api-version": self.API_VERSION,
            "includeContent": "true",
        }
        
        if version_type == "branch":
            params["versionDescriptor.version"] = version
            params["versionDescriptor.versionType"] = "branch"
        else:
            params["versionDescriptor.version"] = version
            params["versionDescriptor.versionType"] = "commit"
        
        try:
            response = self.client.get(url, params=params)
            self._handle_response(response, url)
            return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except PermissionError:
            raise
    
    def get_pr_diff(
        self,
        organization: str,
        project: str,
        repository: str,
        pr_id: int,
        base_version: Optional[str] = None,
        target_version: Optional[str] = None,
    ) -> List[PRDiff]:
        """
        Get diffs for all changed files in a PR.
        
        This fetches the actual diff content for each changed file.
        
        Args:
            organization: Azure DevOps organization
            project: Project name
            repository: Repository name
            pr_id: Pull Request ID
            base_version: Base version (defaults to target branch)
            target_version: Target version (defaults to source branch)
            
        Returns:
            List of PRDiff objects with diff blocks
        """
        metadata = self.get_pr_metadata(organization, project, repository, pr_id)
        changes = self.get_pr_changes(organization, project, repository, pr_id)
        
        if base_version is None:
            base_version = metadata.target_branch
        if target_version is None:
            target_version = metadata.source_branch
        
        diffs = []
        for change in changes:
            if change.is_deleted:
                original_content = self.get_file_content(
                    organization, project, repository,
                    change.path, base_version, "branch"
                )
                diffs.append(PRDiff(
                    path=change.path,
                    original_path=change.original_path,
                    change_type=change.change_type,
                    blocks=[{
                        "type": "deleted",
                        "content": original_content or "",
                    }],
                ))
            elif change.is_added:
                new_content = self.get_file_content(
                    organization, project, repository,
                    change.path, target_version, "branch"
                )
                diffs.append(PRDiff(
                    path=change.path,
                    original_path=change.original_path,
                    change_type=change.change_type,
                    blocks=[{
                        "type": "added",
                        "content": new_content or "",
                    }],
                ))
            else:
                original_content = self.get_file_content(
                    organization, project, repository,
                    change.original_path or change.path, base_version, "branch"
                )
                new_content = self.get_file_content(
                    organization, project, repository,
                    change.path, target_version, "branch"
                )
                diffs.append(PRDiff(
                    path=change.path,
                    original_path=change.original_path,
                    change_type=change.change_type,
                    blocks=[{
                        "type": "modified",
                        "originalContent": original_content or "",
                        "newContent": new_content or "",
                    }],
                ))
        
        return diffs
    
    def get_pr_for_review(
        self,
        pr_url: str,
        include_diffs: bool = True,
        include_content: bool = True,
    ) -> PRReviewData:
        """
        Get complete PR data for review.
        
        This is the main entry point for the PR Review Agent.
        
        Args:
            pr_url: Azure DevOps PR URL
            include_diffs: Whether to fetch file diffs
            include_content: Whether to fetch file contents
            
        Returns:
            PRReviewData object with all PR information
        """
        organization, project, repository, pr_id = self.parse_pr_url(pr_url)
        
        logger.info(f"Fetching PR #{pr_id} from {organization}/{project}/{repository}")
        
        metadata = self.get_pr_metadata(organization, project, repository, pr_id)
        changes = self.get_pr_changes(organization, project, repository, pr_id)
        
        diffs = []
        if include_diffs:
            diffs = self.get_pr_diff(organization, project, repository, pr_id)
        
        if include_content:
            for i, change in enumerate(changes):
                if not change.is_deleted:
                    content = self.get_file_content(
                        organization, project, repository,
                        change.path, metadata.source_branch, "branch"
                    )
                    changes[i] = PRFileChange(
                        path=change.path,
                        original_path=change.original_path,
                        change_type=change.change_type,
                        content=content,
                    )
        
        return PRReviewData(
            metadata=metadata,
            files=changes,
            diffs=diffs,
        )


def get_pr_for_review(pr_url: str) -> Dict[str, Any]:
    """
    Convenience function to get PR data for review.
    
    Args:
        pr_url: Azure DevOps PR URL
        
    Returns:
        Dictionary with PR review data
    """
    with AzureDevOpsPRClient() as client:
        pr_data = client.get_pr_for_review(pr_url)
        return pr_data.to_dict()
