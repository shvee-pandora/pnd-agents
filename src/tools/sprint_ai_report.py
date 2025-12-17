"""
Sprint AI Report Tool

Generates scrum-master friendly reports combining:
- JIRA sprint data (issues, PRs, status)
- Azure DevOps commits (metadata, AI signatures)
- Analytics metrics (effectiveness, time saved)

This tool allows non-coders to get AI contribution reports without cloning repos.
"""

import base64
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("pnd_agents.sprint_ai_report")


# ==================== Configuration ====================

@dataclass
class SprintReportConfig:
    """Configuration for Sprint AI Report generation."""

    # JIRA settings
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""

    # Azure DevOps settings
    azure_org: str = ""
    azure_project: str = ""
    azure_repo: str = ""
    azure_pat: str = ""  # Personal Access Token

    # Report settings
    time_saved_per_ai_commit_hours: float = 2.0

    @classmethod
    def from_env(cls) -> "SprintReportConfig":
        """Create config from environment variables."""
        return cls(
            jira_base_url=os.environ.get("JIRA_BASE_URL", ""),
            jira_email=os.environ.get("JIRA_EMAIL", ""),
            jira_api_token=os.environ.get("JIRA_API_TOKEN", ""),
            azure_org=os.environ.get("AZURE_DEVOPS_ORG", "pandora-jewelry"),
            azure_project=os.environ.get("AZURE_DEVOPS_PROJECT", "Spark"),
            azure_repo=os.environ.get("AZURE_DEVOPS_REPO", "pandora-group"),
            azure_pat=os.environ.get("AZURE_DEVOPS_PAT", ""),
            time_saved_per_ai_commit_hours=float(
                os.environ.get("AI_TIME_SAVED_PER_COMMIT", "2.0")
            ),
        )


# ==================== Data Models ====================

@dataclass
class SprintInfo:
    """Sprint metadata from JIRA."""
    id: int
    name: str
    state: str
    start_date: str
    end_date: str
    goal: str = ""


@dataclass
class SprintIssue:
    """Issue data from JIRA sprint."""
    key: str
    summary: str
    status: str
    status_category: str  # To Do, In Progress, Done
    assignee: str
    issue_type: str
    story_points: Optional[float] = None
    has_pr: bool = False
    pr_count: int = 0


@dataclass
class AICommit:
    """AI-generated commit data from Azure DevOps."""
    commit_id: str
    message: str
    author: str
    author_email: str
    date: str
    ai_model: str = "Claude"
    linked_issue: Optional[str] = None


@dataclass
class SprintAIReport:
    """Complete sprint AI report data."""
    # Sprint info
    sprint_name: str
    sprint_id: int
    start_date: str
    end_date: str

    # Issue metrics
    total_issues: int = 0
    completed_issues: int = 0
    in_progress_issues: int = 0
    todo_issues: int = 0

    # AI metrics
    total_commits: int = 0
    ai_commits_count: int = 0
    ai_contribution_percent: float = 0.0
    issues_with_ai_commits: List[str] = field(default_factory=list)
    time_saved_hours: float = 0.0

    # Breakdown
    ai_commits: List[Dict[str, Any]] = field(default_factory=list)
    issues_by_status: Dict[str, List[str]] = field(default_factory=dict)
    ai_by_author: Dict[str, int] = field(default_factory=dict)
    ai_by_type: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sprint_name": self.sprint_name,
            "sprint_id": self.sprint_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_issues": self.total_issues,
            "completed_issues": self.completed_issues,
            "in_progress_issues": self.in_progress_issues,
            "todo_issues": self.todo_issues,
            "total_commits": self.total_commits,
            "ai_commits_count": self.ai_commits_count,
            "ai_contribution_percent": self.ai_contribution_percent,
            "issues_with_ai_commits": self.issues_with_ai_commits,
            "time_saved_hours": self.time_saved_hours,
            "ai_commits": self.ai_commits,
            "issues_by_status": self.issues_by_status,
            "ai_by_author": self.ai_by_author,
            "ai_by_type": self.ai_by_type,
        }


# ==================== AI Signature Detection ====================

AI_SIGNATURES = [
    "Generated with [Claude Code]",
    "Co-Authored-By: Claude",
    "Co-Authored-By:.*Anthropic",
    "pnd-agents",
]

AI_MODEL_PATTERNS = {
    "Claude Opus 4.5": "Opus 4.5",
    "Claude Sonnet": "Sonnet",
    "Claude": "Claude",
}


def is_ai_commit(message: str) -> bool:
    """Check if commit message indicates AI generation."""
    if not message:
        return False
    message_lower = message.lower()
    return any(sig.lower() in message_lower for sig in AI_SIGNATURES)


def extract_ai_model(message: str) -> str:
    """Extract AI model name from commit message."""
    for pattern, model in AI_MODEL_PATTERNS.items():
        if pattern in message:
            return model
    return "Claude"


def extract_issue_key(message: str) -> Optional[str]:
    """Extract JIRA issue key from commit message (e.g., INS-1234)."""
    import re
    match = re.search(r'([A-Z]+-\d+)', message)
    return match.group(1) if match else None


def categorize_commit(message: str) -> str:
    """Categorize commit by type based on conventional commit prefix."""
    message_lower = message.lower()
    if message_lower.startswith("feat"):
        return "Feature"
    elif message_lower.startswith("fix"):
        return "Bug Fix"
    elif message_lower.startswith("test"):
        return "Unit Tests"
    elif message_lower.startswith("refactor"):
        return "Refactoring"
    elif message_lower.startswith("docs"):
        return "Documentation"
    elif "sonar" in message_lower or "coverage" in message_lower:
        return "Code Quality"
    else:
        return "Other"


# ==================== Sprint AI Report Generator ====================

class SprintAIReportGenerator:
    """
    Generates comprehensive sprint reports combining JIRA, Azure DevOps, and analytics.

    Designed for scrum masters and non-technical stakeholders.
    """

    def __init__(self, config: Optional[SprintReportConfig] = None):
        """Initialize the report generator."""
        self.config = config or SprintReportConfig.from_env()
        self._jira_client: Optional[httpx.Client] = None
        self._azure_client: Optional[httpx.Client] = None

    @property
    def jira_client(self) -> httpx.Client:
        """Get or create JIRA HTTP client."""
        if self._jira_client is None:
            self._jira_client = httpx.Client(
                base_url=f"{self.config.jira_base_url.rstrip('/')}/rest/",
                auth=(self.config.jira_email, self.config.jira_api_token),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._jira_client

    @property
    def azure_client(self) -> httpx.Client:
        """Get or create Azure DevOps HTTP client."""
        if self._azure_client is None:
            # Azure DevOps uses Basic Auth with empty username and PAT as password
            credentials = base64.b64encode(f":{self.config.azure_pat}".encode()).decode()
            self._azure_client = httpx.Client(
                base_url=f"https://dev.azure.com/{self.config.azure_org}/{self.config.azure_project}/_apis/",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._azure_client

    def close(self):
        """Close HTTP clients."""
        if self._jira_client:
            self._jira_client.close()
        if self._azure_client:
            self._azure_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ==================== JIRA Operations ====================

    def get_active_sprint(self, board_id: int) -> Optional[SprintInfo]:
        """Get the active sprint for a board."""
        try:
            response = self.jira_client.get(
                f"agile/1.0/board/{board_id}/sprint",
                params={"state": "active"}
            )
            response.raise_for_status()
            data = response.json()

            sprints = data.get("values", [])
            if sprints:
                s = sprints[0]
                return SprintInfo(
                    id=s["id"],
                    name=s["name"],
                    state=s["state"],
                    start_date=s.get("startDate", ""),
                    end_date=s.get("endDate", ""),
                    goal=s.get("goal", ""),
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get active sprint: {e}")
            raise

    def get_sprint_by_id(self, sprint_id: int) -> Optional[SprintInfo]:
        """Get sprint by ID."""
        try:
            response = self.jira_client.get(f"agile/1.0/sprint/{sprint_id}")
            response.raise_for_status()
            s = response.json()

            return SprintInfo(
                id=s["id"],
                name=s["name"],
                state=s["state"],
                start_date=s.get("startDate", ""),
                end_date=s.get("endDate", ""),
                goal=s.get("goal", ""),
            )
        except Exception as e:
            logger.error(f"Failed to get sprint {sprint_id}: {e}")
            raise

    def get_sprint_issues(self, sprint_id: int) -> List[SprintIssue]:
        """Get all issues in a sprint."""
        try:
            response = self.jira_client.get(
                f"agile/1.0/sprint/{sprint_id}/issue",
                params={"maxResults": 200}
            )
            response.raise_for_status()
            data = response.json()

            issues = []
            for issue_data in data.get("issues", []):
                fields = issue_data.get("fields", {})
                status = fields.get("status", {})
                status_category = status.get("statusCategory", {})

                # Check for PR info in development field
                dev_info = fields.get("customfield_10000", "")
                has_pr = "pullrequest" in str(dev_info).lower() if dev_info else False

                issues.append(SprintIssue(
                    key=issue_data.get("key", ""),
                    summary=fields.get("summary", ""),
                    status=status.get("name", ""),
                    status_category=status_category.get("name", ""),
                    assignee=fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
                    issue_type=fields.get("issuetype", {}).get("name", ""),
                    story_points=fields.get("customfield_10022"),  # Story points field
                    has_pr=has_pr,
                ))

            return issues
        except Exception as e:
            logger.error(f"Failed to get sprint issues: {e}")
            raise

    # ==================== Azure DevOps Operations ====================

    def get_commits_by_date_range(
        self,
        start_date: str,
        end_date: str,
        branch: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get commits from Azure DevOps in a date range.

        Args:
            start_date: ISO format date (YYYY-MM-DD)
            end_date: ISO format date (YYYY-MM-DD)
            branch: Branch name (default: None = all branches)

        Returns:
            List of commit data
        """
        if not self.config.azure_pat:
            logger.warning("Azure DevOps PAT not configured - skipping commit analysis")
            return []

        try:
            params = {
                "searchCriteria.fromDate": start_date,
                "searchCriteria.toDate": end_date,
                "$top": 500,
                "api-version": "7.0",
            }
            # Only filter by branch if explicitly specified
            if branch:
                params["searchCriteria.itemVersion.version"] = branch

            response = self.azure_client.get(
                f"git/repositories/{self.config.azure_repo}/commits",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            return data.get("value", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"Azure DevOps API error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Failed to get Azure commits: {e}")
            return []

    def get_commit_details(self, commit_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed commit information including full message."""
        if not self.config.azure_pat:
            return None

        try:
            response = self.azure_client.get(
                f"git/repositories/{self.config.azure_repo}/commits/{commit_id}",
                params={"api-version": "7.0"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get commit {commit_id}: {e}")
            return None

    def identify_ai_commits(
        self,
        start_date: str,
        end_date: str
    ) -> List[AICommit]:
        """
        Identify AI-generated commits in a date range.

        Returns commits with Claude Code signature.
        Note: Azure DevOps list API only returns first line of commit message,
        so we need to fetch full details for each commit to check for AI signature.
        """
        commits = self.get_commits_by_date_range(start_date, end_date)
        ai_commits = []

        for commit in commits:
            comment = commit.get("comment", "")
            commit_id = commit.get("commitId", "")

            # Check main message first (in case full message is in list)
            if is_ai_commit(comment):
                ai_commits.append(AICommit(
                    commit_id=commit_id[:8],
                    message=comment.split("\n")[0][:100],
                    author=commit.get("author", {}).get("name", ""),
                    author_email=commit.get("author", {}).get("email", ""),
                    date=commit.get("author", {}).get("date", "")[:10],
                    ai_model=extract_ai_model(comment),
                    linked_issue=extract_issue_key(comment),
                ))
                continue

            # Azure DevOps list API only returns first line of commit message
            # Fetch full details for commits that might be AI-related:
            # - Conventional commit prefixes (feat, fix, test, etc.)
            # - JIRA issue keys (INS-, EPA-, etc.)
            # - Keywords suggesting component/test work
            comment_lower = comment.lower()
            might_be_ai = (
                any(comment_lower.startswith(prefix) for prefix in ["feat", "fix", "test", "refactor", "docs", "chore"]) or
                "component" in comment_lower or
                "unit test" in comment_lower or
                "react |" in comment_lower or
                "amp |" in comment_lower or
                comment_lower.startswith("add ") or
                comment_lower.startswith("create ") or
                comment_lower.startswith("implement ")
            )
            if might_be_ai:
                details = self.get_commit_details(commit_id)
                if details:
                    full_comment = details.get("comment", "")
                    if is_ai_commit(full_comment):
                        ai_commits.append(AICommit(
                            commit_id=commit_id[:8],
                            message=comment.split("\n")[0][:100],
                            author=commit.get("author", {}).get("name", ""),
                            author_email=commit.get("author", {}).get("email", ""),
                            date=commit.get("author", {}).get("date", "")[:10],
                            ai_model=extract_ai_model(full_comment),
                            linked_issue=extract_issue_key(comment),
                        ))

        return ai_commits

    # ==================== Report Generation ====================

    def generate_report(
        self,
        sprint_id: Optional[int] = None,
        board_id: Optional[int] = None,
        include_commits: bool = True,
        output_format: str = "markdown"
    ) -> str:
        """
        Generate comprehensive sprint AI report.

        Args:
            sprint_id: JIRA sprint ID (if known)
            board_id: JIRA board ID (to find active sprint)
            include_commits: Whether to fetch Azure DevOps commits
            output_format: "markdown" or "json"

        Returns:
            Formatted report string
        """
        # Get sprint info
        if sprint_id:
            sprint = self.get_sprint_by_id(sprint_id)
        elif board_id:
            sprint = self.get_active_sprint(board_id)
        else:
            raise ValueError("Either sprint_id or board_id must be provided")

        if not sprint:
            return "Sprint not found"

        # Get sprint issues
        issues = self.get_sprint_issues(sprint.id)

        # Initialize report
        report = SprintAIReport(
            sprint_name=sprint.name,
            sprint_id=sprint.id,
            start_date=sprint.start_date[:10] if sprint.start_date else "",
            end_date=sprint.end_date[:10] if sprint.end_date else "",
            total_issues=len(issues),
        )

        # Categorize issues
        for issue in issues:
            cat = issue.status_category
            if cat == "Done":
                report.completed_issues += 1
                report.issues_by_status.setdefault("Done", []).append(issue.key)
            elif cat == "In Progress":
                report.in_progress_issues += 1
                report.issues_by_status.setdefault("In Progress", []).append(issue.key)
            else:
                report.todo_issues += 1
                report.issues_by_status.setdefault("To Do", []).append(issue.key)

        # Get AI commits if configured
        if include_commits and self.config.azure_pat:
            ai_commits = self.identify_ai_commits(
                report.start_date,
                report.end_date
            )

            # Get total commit count
            all_commits = self.get_commits_by_date_range(
                report.start_date,
                report.end_date
            )
            report.total_commits = len(all_commits)
            report.ai_commits_count = len(ai_commits)

            if report.total_commits > 0:
                report.ai_contribution_percent = round(
                    (report.ai_commits_count / report.total_commits) * 100, 1
                )

            # Process AI commits
            for ac in ai_commits:
                report.ai_commits.append({
                    "id": ac.commit_id,
                    "message": ac.message,
                    "author": ac.author,
                    "date": ac.date,
                    "model": ac.ai_model,
                    "issue": ac.linked_issue,
                    "type": categorize_commit(ac.message),
                })

                if ac.linked_issue:
                    if ac.linked_issue not in report.issues_with_ai_commits:
                        report.issues_with_ai_commits.append(ac.linked_issue)

                # Count by author
                report.ai_by_author[ac.author] = report.ai_by_author.get(ac.author, 0) + 1

                # Count by type
                commit_type = categorize_commit(ac.message)
                report.ai_by_type[commit_type] = report.ai_by_type.get(commit_type, 0) + 1

            # Calculate time saved
            report.time_saved_hours = round(
                report.ai_commits_count * self.config.time_saved_per_ai_commit_hours, 1
            )

        # Format output
        if output_format == "json":
            return json.dumps(report.to_dict(), indent=2)
        else:
            return self._format_markdown(report)

    def _format_markdown(self, report: SprintAIReport) -> str:
        """Format report as markdown for scrum masters."""
        lines = [
            f"# Sprint AI Report: {report.sprint_name}",
            "",
            f"**Period:** {report.start_date} to {report.end_date}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Issues | {report.total_issues} |",
            f"| Completed | {report.completed_issues} ({self._percent(report.completed_issues, report.total_issues)}%) |",
            f"| In Progress | {report.in_progress_issues} |",
            f"| To Do | {report.todo_issues} |",
            "",
        ]

        if report.total_commits > 0:
            lines.extend([
                "## AI Contribution",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Total Commits | {report.total_commits} |",
                f"| AI-Generated Commits | {report.ai_commits_count} |",
                f"| AI Contribution | **{report.ai_contribution_percent}%** |",
                f"| Issues with AI Commits | {len(report.issues_with_ai_commits)} |",
                f"| Estimated Time Saved | **{report.time_saved_hours} hours** |",
                "",
            ])

            if report.ai_by_type:
                lines.extend([
                    "### AI Commits by Type",
                    "",
                    "| Type | Count |",
                    "|------|-------|",
                ])
                for commit_type, count in sorted(report.ai_by_type.items(), key=lambda x: -x[1]):
                    lines.append(f"| {commit_type} | {count} |")
                lines.append("")

            if report.ai_by_author:
                lines.extend([
                    "### AI Commits by Author",
                    "",
                    "| Author | AI Commits |",
                    "|--------|------------|",
                ])
                for author, count in sorted(report.ai_by_author.items(), key=lambda x: -x[1]):
                    lines.append(f"| {author} | {count} |")
                lines.append("")

            if report.issues_with_ai_commits:
                lines.extend([
                    "### Issues with AI-Generated Code",
                    "",
                ])
                for issue_key in report.issues_with_ai_commits:
                    lines.append(f"- {issue_key}")
                lines.append("")

            if report.ai_commits:
                lines.extend([
                    "### AI Commit Details",
                    "",
                    "| Date | Hash | Author | Type | Message |",
                    "|------|------|--------|------|---------|",
                ])
                for commit in report.ai_commits[:20]:  # Limit to 20
                    lines.append(
                        f"| {commit['date']} | `{commit['id']}` | {commit['author']} | {commit['type']} | {commit['message'][:50]}... |"
                    )
                if len(report.ai_commits) > 20:
                    lines.append(f"| ... | ... | ... | ... | *({len(report.ai_commits) - 20} more commits)* |")
                lines.append("")
        else:
            lines.extend([
                "## AI Contribution",
                "",
                "*Commit analysis not available. Configure Azure DevOps PAT to enable.*",
                "",
            ])

        lines.extend([
            "---",
            "",
            "*Generated by PND Agents Sprint AI Report Tool*",
        ])

        return "\n".join(lines)

    @staticmethod
    def _percent(part: int, total: int) -> int:
        """Calculate percentage safely."""
        if total == 0:
            return 0
        return round((part / total) * 100)


# ==================== Convenience Functions ====================

def generate_sprint_report(
    sprint_id: Optional[int] = None,
    board_id: Optional[int] = None,
    include_commits: bool = True,
    output_format: str = "markdown"
) -> str:
    """
    Generate a sprint AI report.

    Convenience function for MCP tool registration.
    """
    with SprintAIReportGenerator() as generator:
        return generator.generate_report(
            sprint_id=sprint_id,
            board_id=board_id,
            include_commits=include_commits,
            output_format=output_format,
        )


def identify_ai_commits_in_range(
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    Identify AI commits in a date range.

    Convenience function for MCP tool registration.
    """
    with SprintAIReportGenerator() as generator:
        commits = generator.identify_ai_commits(start_date, end_date)
        return [
            {
                "id": c.commit_id,
                "message": c.message,
                "author": c.author,
                "date": c.date,
                "model": c.ai_model,
                "issue": c.linked_issue,
            }
            for c in commits
        ]


# ==================== Confluence Publishing ====================

@dataclass
class ConfluenceConfig:
    """Configuration for Confluence API connection."""
    base_url: str = ""
    email: str = ""
    api_token: str = ""
    default_space_key: str = ""

    @classmethod
    def from_env(cls) -> "ConfluenceConfig":
        """Create config from environment variables."""
        return cls(
            base_url=os.environ.get("CONFLUENCE_BASE_URL", os.environ.get("JIRA_BASE_URL", "")),
            email=os.environ.get("CONFLUENCE_EMAIL", os.environ.get("JIRA_EMAIL", "")),
            api_token=os.environ.get("CONFLUENCE_API_TOKEN", os.environ.get("JIRA_API_TOKEN", "")),
            default_space_key=os.environ.get("CONFLUENCE_SPACE_KEY", ""),
        )


class ConfluencePublisher:
    """
    Publishes content to Confluence pages.

    Supports creating and updating pages with markdown content.
    """

    def __init__(self, config: Optional[ConfluenceConfig] = None):
        """Initialize the Confluence publisher."""
        self.config = config or ConfluenceConfig.from_env()
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create Confluence HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=f"{self.config.base_url.rstrip('/')}/wiki/api/v2/",
                auth=(self.config.email, self.config.api_token),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    def close(self):
        """Close HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _markdown_to_adf(self, markdown: str) -> Dict[str, Any]:
        """
        Convert markdown to Atlassian Document Format (ADF).

        This is a simplified conversion that handles common markdown elements.
        """
        content = []
        lines = markdown.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Headers
            if line.startswith("# "):
                content.append({
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": line[2:].strip()}]
                })
            elif line.startswith("## "):
                content.append({
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": line[3:].strip()}]
                })
            elif line.startswith("### "):
                content.append({
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": line[4:].strip()}]
                })
            # Horizontal rule
            elif line.strip() == "---":
                content.append({"type": "rule"})
            # Table
            elif line.strip().startswith("|"):
                table_rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    row_line = lines[i].strip()
                    # Skip separator rows (|---|---|)
                    if not all(c in "|-: " for c in row_line):
                        cells = [c.strip() for c in row_line.split("|")[1:-1]]
                        table_rows.append(cells)
                    i += 1
                i -= 1  # Adjust for outer loop increment

                if table_rows:
                    table_content = []
                    for row_idx, row in enumerate(table_rows):
                        cell_type = "tableHeader" if row_idx == 0 else "tableCell"
                        row_content = {
                            "type": "tableRow",
                            "content": [
                                {
                                    "type": cell_type,
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": self._parse_inline_text(cell)
                                        }
                                    ]
                                }
                                for cell in row
                            ]
                        }
                        table_content.append(row_content)

                    content.append({
                        "type": "table",
                        "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
                        "content": table_content
                    })
            # Bullet list
            elif line.strip().startswith("- "):
                list_items = []
                while i < len(lines) and lines[i].strip().startswith("- "):
                    item_text = lines[i].strip()[2:]
                    list_items.append({
                        "type": "listItem",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": self._parse_inline_text(item_text)
                            }
                        ]
                    })
                    i += 1
                i -= 1  # Adjust for outer loop increment

                content.append({
                    "type": "bulletList",
                    "content": list_items
                })
            # Regular paragraph
            else:
                content.append({
                    "type": "paragraph",
                    "content": self._parse_inline_text(line)
                })

            i += 1

        return {
            "type": "doc",
            "version": 1,
            "content": content
        }

    def _parse_inline_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse inline text with bold, italic, code formatting."""
        result = []
        current_text = ""
        i = 0

        while i < len(text):
            # Bold text **text**
            if text[i:i+2] == "**":
                if current_text:
                    result.append({"type": "text", "text": current_text})
                    current_text = ""
                end = text.find("**", i + 2)
                if end != -1:
                    result.append({
                        "type": "text",
                        "text": text[i+2:end],
                        "marks": [{"type": "strong"}]
                    })
                    i = end + 2
                    continue
            # Inline code `code`
            elif text[i] == "`":
                if current_text:
                    result.append({"type": "text", "text": current_text})
                    current_text = ""
                end = text.find("`", i + 1)
                if end != -1:
                    result.append({
                        "type": "text",
                        "text": text[i+1:end],
                        "marks": [{"type": "code"}]
                    })
                    i = end + 1
                    continue
            # Italic text *text*
            elif text[i] == "*" and (i == 0 or text[i-1] != "*") and (i + 1 < len(text) and text[i+1] != "*"):
                if current_text:
                    result.append({"type": "text", "text": current_text})
                    current_text = ""
                end = text.find("*", i + 1)
                if end != -1 and text[end-1:end+1] != "**":
                    result.append({
                        "type": "text",
                        "text": text[i+1:end],
                        "marks": [{"type": "em"}]
                    })
                    i = end + 1
                    continue

            current_text += text[i]
            i += 1

        if current_text:
            result.append({"type": "text", "text": current_text})

        return result if result else [{"type": "text", "text": " "}]

    def get_space_id(self, space_key: str) -> Optional[str]:
        """Get space ID from space key."""
        try:
            response = self.client.get(
                "spaces",
                params={"keys": space_key, "limit": 1}
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            if results:
                return results[0].get("id")
            return None
        except Exception as e:
            logger.error(f"Failed to get space ID for {space_key}: {e}")
            return None

    def find_page_by_title(self, space_id: str, title: str) -> Optional[Dict[str, Any]]:
        """Find a page by title in a space."""
        try:
            response = self.client.get(
                "pages",
                params={
                    "space-id": space_id,
                    "title": title,
                    "limit": 1
                }
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"Failed to find page '{title}': {e}")
            return None

    def create_page(
        self,
        space_key: str,
        title: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Confluence page.

        Args:
            space_key: Confluence space key (e.g., "SHAM")
            title: Page title
            content: Markdown content
            parent_id: Optional parent page ID

        Returns:
            Created page data including URL
        """
        space_id = self.get_space_id(space_key)
        if not space_id:
            raise ValueError(f"Space '{space_key}' not found")

        # Convert markdown to ADF
        adf_content = self._markdown_to_adf(content)

        payload = {
            "spaceId": space_id,
            "status": "current",
            "title": title,
            "body": {
                "representation": "atlas_doc_format",
                "value": json.dumps(adf_content)
            }
        }

        if parent_id:
            payload["parentId"] = parent_id

        try:
            response = self.client.post("pages", json=payload)
            response.raise_for_status()
            page_data = response.json()

            return {
                "id": page_data.get("id"),
                "title": page_data.get("title"),
                "url": f"{self.config.base_url}/wiki{page_data.get('_links', {}).get('webui', '')}",
                "status": "created"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to create page: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to create page: {e}")
            raise

    def update_page(
        self,
        page_id: str,
        title: str,
        content: str,
        version: int
    ) -> Dict[str, Any]:
        """
        Update an existing Confluence page.

        Args:
            page_id: Page ID to update
            title: New page title
            content: New markdown content
            version: Current page version (will be incremented)

        Returns:
            Updated page data including URL
        """
        # Convert markdown to ADF
        adf_content = self._markdown_to_adf(content)

        payload = {
            "id": page_id,
            "status": "current",
            "title": title,
            "body": {
                "representation": "atlas_doc_format",
                "value": json.dumps(adf_content)
            },
            "version": {
                "number": version + 1
            }
        }

        try:
            response = self.client.put(f"pages/{page_id}", json=payload)
            response.raise_for_status()
            page_data = response.json()

            return {
                "id": page_data.get("id"),
                "title": page_data.get("title"),
                "url": f"{self.config.base_url}/wiki{page_data.get('_links', {}).get('webui', '')}",
                "status": "updated",
                "version": version + 1
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to update page: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to update page: {e}")
            raise

    def publish_or_update(
        self,
        space_key: str,
        title: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create or update a Confluence page.

        If a page with the same title exists in the space, it will be updated.
        Otherwise, a new page will be created.

        Args:
            space_key: Confluence space key
            title: Page title
            content: Markdown content
            parent_id: Optional parent page ID

        Returns:
            Page data including URL and status (created/updated)
        """
        space_id = self.get_space_id(space_key)
        if not space_id:
            raise ValueError(f"Space '{space_key}' not found")

        # Check if page exists
        existing_page = self.find_page_by_title(space_id, title)

        if existing_page:
            # Update existing page
            return self.update_page(
                page_id=existing_page["id"],
                title=title,
                content=content,
                version=existing_page.get("version", {}).get("number", 1)
            )
        else:
            # Create new page
            return self.create_page(
                space_key=space_key,
                title=title,
                content=content,
                parent_id=parent_id
            )


# ==================== Combined Report + Publish Functions ====================

def generate_and_publish_sprint_report(
    sprint_id: Optional[int] = None,
    board_id: Optional[int] = None,
    space_key: Optional[str] = None,
    page_title: Optional[str] = None,
    parent_page_id: Optional[str] = None,
    include_commits: bool = True
) -> Dict[str, Any]:
    """
    Generate a sprint AI report and publish it to Confluence.

    Args:
        sprint_id: JIRA sprint ID
        board_id: JIRA board ID (to find active sprint)
        space_key: Confluence space key (uses CONFLUENCE_SPACE_KEY env var if not provided)
        page_title: Page title (auto-generated from sprint name if not provided)
        parent_page_id: Optional parent page ID
        include_commits: Include Azure DevOps commit analysis

    Returns:
        Dictionary with report content and Confluence page URL
    """
    # Generate the report
    with SprintAIReportGenerator() as generator:
        if sprint_id:
            sprint = generator.get_sprint_by_id(sprint_id)
        elif board_id:
            sprint = generator.get_active_sprint(board_id)
        else:
            raise ValueError("Either sprint_id or board_id must be provided")

        if not sprint:
            raise ValueError("Sprint not found")

        report_content = generator.generate_report(
            sprint_id=sprint.id,
            include_commits=include_commits,
            output_format="markdown"
        )

    # Determine space key
    confluence_space = space_key or os.environ.get("CONFLUENCE_SPACE_KEY", "")
    if not confluence_space:
        raise ValueError("Confluence space key not provided. Set CONFLUENCE_SPACE_KEY env var or pass space_key parameter.")

    # Determine page title
    title = page_title or f"Sprint AI Report: {sprint.name}"

    # Publish to Confluence
    with ConfluencePublisher() as publisher:
        result = publisher.publish_or_update(
            space_key=confluence_space,
            title=title,
            content=report_content,
            parent_id=parent_page_id
        )

    return {
        "sprint_name": sprint.name,
        "sprint_id": sprint.id,
        "report_content": report_content,
        "confluence_page": result
    }


def publish_to_confluence(
    content: str,
    space_key: str,
    title: str,
    parent_page_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publish markdown content to a Confluence page.

    Args:
        content: Markdown content to publish
        space_key: Confluence space key
        title: Page title
        parent_page_id: Optional parent page ID

    Returns:
        Dictionary with page URL and status
    """
    with ConfluencePublisher() as publisher:
        return publisher.publish_or_update(
            space_key=space_key,
            title=title,
            content=content,
            parent_id=parent_page_id
        )
