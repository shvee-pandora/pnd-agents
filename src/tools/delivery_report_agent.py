"""
Delivery Report Agent - Multi-Sprint Velocity Reports

This module provides the DeliveryReportAgent class for generating
multi-sprint velocity reports with ASCII charts and cross-workspace support.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import base64
import json
import logging
import os

import httpx

from .sprint_ai_report import (
    SprintReportConfig,
    SprintInfo,
    SprintAIReportGenerator,
    ConfluencePublisher,
)

logger = logging.getLogger(__name__)


@dataclass
class SprintVelocityData:
    """Velocity data for a single sprint."""
    sprint_id: int
    sprint_name: str
    start_date: str
    end_date: str
    state: str  # closed, active, future
    
    # Commitment metrics (like the user's chart)
    rollover_story_points: float = 0.0  # Carryover from previous sprint (teal bar)
    initial_commitment: float = 0.0  # Initial commitment (gray bar)
    delivered_story_points: float = 0.0  # Delivered (green bar)
    
    # Scope changes
    added_work: float = 0.0  # Added during sprint (pink bar)
    removed_work: float = 0.0  # Removed during sprint (dark blue bar)
    
    # Issue counts
    total_issues: int = 0
    completed_issues: int = 0
    carryover_issues: int = 0
    
    # AI metrics
    ai_assisted_issues: int = 0
    ai_commits_count: int = 0
    time_saved_hours: float = 0.0
    
    @property
    def total_commitment(self) -> float:
        """Total commitment = rollover + initial + added - removed."""
        return self.rollover_story_points + self.initial_commitment + self.added_work - self.removed_work
    
    @property
    def delivery_rate(self) -> float:
        """Delivery rate as percentage."""
        if self.total_commitment == 0:
            return 0.0
        return round((self.delivered_story_points / self.total_commitment) * 100, 1)


@dataclass
class MultiSprintVelocityReport:
    """Multi-sprint velocity report data."""
    report_title: str
    workspace_name: str
    project_keys: List[str]
    
    # Date range
    start_date: str
    end_date: str
    
    # Sprint data
    sprints: List[SprintVelocityData] = field(default_factory=list)
    
    # Aggregated metrics
    total_delivered_sp: float = 0.0
    total_committed_sp: float = 0.0
    total_rollover_sp: float = 0.0
    total_added_work: float = 0.0
    total_removed_work: float = 0.0
    
    # Average metrics
    avg_velocity: float = 0.0
    avg_delivery_rate: float = 0.0
    
    # AI contribution
    total_ai_assisted_issues: int = 0
    total_ai_commits: int = 0
    total_time_saved_hours: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_title": self.report_title,
            "workspace_name": self.workspace_name,
            "project_keys": self.project_keys,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "sprints": [
                {
                    "sprint_id": s.sprint_id,
                    "sprint_name": s.sprint_name,
                    "start_date": s.start_date,
                    "end_date": s.end_date,
                    "state": s.state,
                    "rollover_story_points": s.rollover_story_points,
                    "initial_commitment": s.initial_commitment,
                    "delivered_story_points": s.delivered_story_points,
                    "added_work": s.added_work,
                    "removed_work": s.removed_work,
                    "total_commitment": s.total_commitment,
                    "delivery_rate": s.delivery_rate,
                    "total_issues": s.total_issues,
                    "completed_issues": s.completed_issues,
                    "ai_assisted_issues": s.ai_assisted_issues,
                    "ai_commits_count": s.ai_commits_count,
                    "time_saved_hours": s.time_saved_hours,
                }
                for s in self.sprints
            ],
            "total_delivered_sp": self.total_delivered_sp,
            "total_committed_sp": self.total_committed_sp,
            "total_rollover_sp": self.total_rollover_sp,
            "total_added_work": self.total_added_work,
            "total_removed_work": self.total_removed_work,
            "avg_velocity": self.avg_velocity,
            "avg_delivery_rate": self.avg_delivery_rate,
            "total_ai_assisted_issues": self.total_ai_assisted_issues,
            "total_ai_commits": self.total_ai_commits,
            "total_time_saved_hours": self.total_time_saved_hours,
        }


class DeliveryReportAgent:
    """
    Delivery Report Agent - Generates multi-sprint velocity reports.
    
    Features:
    - Aggregates data from multiple closed sprints
    - Supports multiple projects/workspaces
    - ASCII horizontal bar charts for visualization
    - Per-sprint breakdown over time
    - Commitment vs delivery tracking (rollover, initial, added, removed, delivered)
    """
    
    def __init__(self, config: Optional[SprintReportConfig] = None):
        self.config = config or SprintReportConfig.from_env()
        self._jira_client: Optional[httpx.Client] = None
        self._azure_client: Optional[httpx.Client] = None
    
    @property
    def jira_client(self) -> httpx.Client:
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
        if self._azure_client is None:
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
        if self._jira_client:
            self._jira_client.close()
        if self._azure_client:
            self._azure_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_closed_sprints(
        self,
        board_id: int,
        num_sprints: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[SprintInfo]:
        """
        Get closed sprints from a board.
        
        Args:
            board_id: JIRA board ID
            num_sprints: Number of recent closed sprints to fetch (default: all)
            start_date: Filter sprints starting after this date (YYYY-MM-DD)
            end_date: Filter sprints ending before this date (YYYY-MM-DD)
        
        Returns:
            List of SprintInfo objects for closed sprints
        """
        try:
            all_sprints = []
            start_at = 0
            max_results = 50
            
            while True:
                response = self.jira_client.get(
                    f"agile/1.0/board/{board_id}/sprint",
                    params={
                        "state": "closed",
                        "startAt": start_at,
                        "maxResults": max_results
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                sprints = data.get("values", [])
                for s in sprints:
                    sprint_info = SprintInfo(
                        id=s["id"],
                        name=s["name"],
                        state=s["state"],
                        start_date=s.get("startDate", ""),
                        end_date=s.get("endDate", ""),
                        goal=s.get("goal", ""),
                    )
                    
                    # Apply date filters
                    if start_date and sprint_info.start_date:
                        sprint_start = sprint_info.start_date[:10]
                        if sprint_start < start_date:
                            continue
                    
                    if end_date and sprint_info.end_date:
                        sprint_end = sprint_info.end_date[:10]
                        if sprint_end > end_date:
                            continue
                    
                    all_sprints.append(sprint_info)
                
                if len(sprints) < max_results:
                    break
                start_at += max_results
            
            # Sort by start date (most recent first)
            all_sprints.sort(key=lambda x: x.start_date or "", reverse=True)
            
            # Limit to num_sprints if specified
            if num_sprints:
                all_sprints = all_sprints[:num_sprints]
            
            # Reverse to chronological order for display
            all_sprints.reverse()
            
            return all_sprints
        except Exception as e:
            logger.error(f"Failed to get closed sprints: {e}")
            raise
    
    def get_sprint_velocity_data(
        self,
        sprint: SprintInfo,
        project_keys: Optional[List[str]] = None,
        include_ai_metrics: bool = True
    ) -> SprintVelocityData:
        """
        Get velocity data for a single sprint.
        
        Args:
            sprint: SprintInfo object
            project_keys: Optional list of project keys to filter
            include_ai_metrics: Include AI contribution metrics
        
        Returns:
            SprintVelocityData object
        """
        try:
            # Get sprint issues
            response = self.jira_client.get(
                f"agile/1.0/sprint/{sprint.id}/issue",
                params={
                    "maxResults": 500,
                    "fields": "summary,status,issuetype,customfield_10022,project,labels"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            issues = data.get("issues", [])
            
            # Filter by project keys if specified
            if project_keys:
                issues = [
                    i for i in issues
                    if i.get("fields", {}).get("project", {}).get("key") in project_keys
                ]
            
            # Calculate metrics
            velocity_data = SprintVelocityData(
                sprint_id=sprint.id,
                sprint_name=sprint.name,
                start_date=sprint.start_date[:10] if sprint.start_date else "",
                end_date=sprint.end_date[:10] if sprint.end_date else "",
                state=sprint.state,
            )
            
            for issue in issues:
                fields = issue.get("fields", {})
                status_category = fields.get("status", {}).get("statusCategory", {}).get("name", "")
                story_points = fields.get("customfield_10022") or 0
                labels = fields.get("labels", [])
                
                velocity_data.total_issues += 1
                
                # Check for rollover label (common convention)
                is_rollover = any(l.lower() in ["rollover", "carryover", "carried-over"] for l in labels)
                
                if is_rollover:
                    velocity_data.rollover_story_points += story_points
                else:
                    velocity_data.initial_commitment += story_points
                
                if status_category == "Done":
                    velocity_data.delivered_story_points += story_points
                    velocity_data.completed_issues += 1
                else:
                    velocity_data.carryover_issues += 1
            
            # Get AI metrics if enabled
            if include_ai_metrics and self.config.azure_pat:
                ai_start_date = sprint.start_date[:10] if sprint.start_date else ""
                ai_end_date = sprint.end_date[:10] if sprint.end_date else ""
                if ai_start_date and ai_end_date:
                    try:
                        generator = SprintAIReportGenerator(self.config)
                        ai_commits = generator.identify_ai_commits(ai_start_date, ai_end_date)
                        velocity_data.ai_commits_count = len(ai_commits)
                        velocity_data.time_saved_hours = round(
                            len(ai_commits) * self.config.time_saved_per_ai_commit_hours, 1
                        )
                        
                        # Count AI-assisted issues
                        ai_issue_keys = set()
                        for commit in ai_commits:
                            if commit.linked_issue:
                                ai_issue_keys.add(commit.linked_issue)
                        
                        for issue in issues:
                            if issue.get("key") in ai_issue_keys:
                                velocity_data.ai_assisted_issues += 1
                        
                        generator.close()
                    except Exception as e:
                        logger.warning(f"Failed to get AI metrics for sprint {sprint.id}: {e}")
            
            return velocity_data
        except Exception as e:
            logger.error(f"Failed to get velocity data for sprint {sprint.id}: {e}")
            raise
    
    def generate_report(
        self,
        board_ids: List[int],
        workspace_name: str = "Default Workspace",
        project_keys: Optional[List[str]] = None,
        num_sprints: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_ai_metrics: bool = True,
        output_format: str = "markdown"
    ) -> str:
        """
        Generate multi-sprint velocity report.
        
        Args:
            board_ids: List of JIRA board IDs
            workspace_name: Name for the workspace/report
            project_keys: Optional list of project keys to filter
            num_sprints: Number of recent closed sprints (default: all in date range)
            start_date: Filter sprints starting after this date (YYYY-MM-DD)
            end_date: Filter sprints ending before this date (YYYY-MM-DD)
            include_ai_metrics: Include AI contribution metrics
            output_format: "markdown", "markdown_with_charts", or "json"
        
        Returns:
            Formatted report string
        """
        # Collect all sprints from all boards
        all_sprint_data: List[SprintVelocityData] = []
        seen_sprint_ids = set()
        
        for board_id in board_ids:
            sprints = self.get_closed_sprints(
                board_id=board_id,
                num_sprints=num_sprints,
                start_date=start_date,
                end_date=end_date
            )
            
            for sprint in sprints:
                if sprint.id in seen_sprint_ids:
                    continue
                seen_sprint_ids.add(sprint.id)
                
                velocity_data = self.get_sprint_velocity_data(
                    sprint=sprint,
                    project_keys=project_keys,
                    include_ai_metrics=include_ai_metrics
                )
                all_sprint_data.append(velocity_data)
        
        # Sort by start date
        all_sprint_data.sort(key=lambda x: x.start_date)
        
        # Calculate aggregated metrics
        report = MultiSprintVelocityReport(
            report_title=f"{workspace_name} - Velocity Report",
            workspace_name=workspace_name,
            project_keys=project_keys or [],
            start_date=all_sprint_data[0].start_date if all_sprint_data else "",
            end_date=all_sprint_data[-1].end_date if all_sprint_data else "",
            sprints=all_sprint_data,
        )
        
        for sprint_data in all_sprint_data:
            report.total_delivered_sp += sprint_data.delivered_story_points
            report.total_committed_sp += sprint_data.total_commitment
            report.total_rollover_sp += sprint_data.rollover_story_points
            report.total_added_work += sprint_data.added_work
            report.total_removed_work += sprint_data.removed_work
            report.total_ai_assisted_issues += sprint_data.ai_assisted_issues
            report.total_ai_commits += sprint_data.ai_commits_count
            report.total_time_saved_hours += sprint_data.time_saved_hours
        
        if all_sprint_data:
            report.avg_velocity = round(report.total_delivered_sp / len(all_sprint_data), 1)
            delivery_rates = [s.delivery_rate for s in all_sprint_data if s.total_commitment > 0]
            report.avg_delivery_rate = round(sum(delivery_rates) / len(delivery_rates), 1) if delivery_rates else 0.0
        
        if output_format == "json":
            return json.dumps(report.to_dict(), indent=2)
        elif output_format == "markdown_with_charts":
            return self._format_markdown_with_charts(report)
        else:
            return self._format_markdown(report)
    
    def _format_markdown(self, report: MultiSprintVelocityReport) -> str:
        """Format report as markdown with tables."""
        lines = [
            f"# {report.report_title}",
            "",
            f"**Workspace:** {report.workspace_name}",
            f"**Period:** {report.start_date} to {report.end_date}",
            f"**Sprints Analyzed:** {len(report.sprints)}",
        ]
        
        if report.project_keys:
            lines.append(f"**Projects:** {', '.join(report.project_keys)}")
        
        lines.extend([
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Delivered SP | **{report.total_delivered_sp:.0f}** |",
            f"| Total Committed SP | {report.total_committed_sp:.0f} |",
            f"| Average Velocity | **{report.avg_velocity:.1f} SP/sprint** |",
            f"| Average Delivery Rate | **{report.avg_delivery_rate:.1f}%** |",
            f"| Total Rollover SP | {report.total_rollover_sp:.0f} |",
            "",
        ])
        
        # Sprint-by-sprint breakdown
        lines.extend([
            "## Sprint-by-Sprint Breakdown",
            "",
            "| Sprint | Rollover | Initial | Delivered | Delivery % | Issues |",
            "|--------|----------|---------|-----------|------------|--------|",
        ])
        
        for sprint in report.sprints:
            sprint_name_display = sprint.sprint_name[:30] + ('...' if len(sprint.sprint_name) > 30 else '')
            lines.append(
                f"| {sprint_name_display} | "
                f"{sprint.rollover_story_points:.0f} | "
                f"{sprint.initial_commitment:.0f} | "
                f"**{sprint.delivered_story_points:.0f}** | "
                f"{sprint.delivery_rate:.0f}% | "
                f"{sprint.completed_issues}/{sprint.total_issues} |"
            )
        
        lines.append("")
        
        # AI Contribution
        if report.total_ai_commits > 0 or report.total_ai_assisted_issues > 0:
            lines.extend([
                "## AI Contribution Summary",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Total AI-Assisted Issues | {report.total_ai_assisted_issues} |",
                f"| Total AI Commits | {report.total_ai_commits} |",
                f"| Estimated Time Saved | **{report.total_time_saved_hours:.1f} hours** |",
                "",
            ])
        
        lines.extend([
            "---",
            "",
            "*Generated by PND Agents Delivery Report Agent*",
        ])
        
        return "\n".join(lines)
    
    def _format_markdown_with_charts(self, report: MultiSprintVelocityReport) -> str:
        """Format report as markdown with ASCII horizontal bar charts."""
        lines = [
            f"# {report.report_title}",
            "",
            f"**Workspace:** {report.workspace_name}",
            f"**Period:** {report.start_date} to {report.end_date}",
            f"**Sprints Analyzed:** {len(report.sprints)}",
        ]
        
        if report.project_keys:
            lines.append(f"**Projects:** {', '.join(report.project_keys)}")
        
        lines.extend([
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Delivered SP | **{report.total_delivered_sp:.0f}** |",
            f"| Total Committed SP | {report.total_committed_sp:.0f} |",
            f"| Average Velocity | **{report.avg_velocity:.1f} SP/sprint** |",
            f"| Average Delivery Rate | **{report.avg_delivery_rate:.1f}%** |",
            "",
        ])
        
        # ASCII Velocity Chart
        lines.extend([
            "## Cross-Sprint Velocity Chart",
            "",
            "```",
            "Story Points",
        ])
        
        # Find max value for scaling
        max_sp = max(
            max(s.delivered_story_points, s.initial_commitment, s.rollover_story_points)
            for s in report.sprints
        ) if report.sprints else 1
        
        chart_width = 40
        
        for sprint in report.sprints:
            sprint_label = sprint.sprint_name[:20].ljust(20)
            
            # Rollover bar (teal - using #)
            rollover_width = int((sprint.rollover_story_points / max_sp) * chart_width) if max_sp > 0 else 0
            rollover_bar = "#" * rollover_width
            
            # Initial commitment bar (gray - using =)
            initial_width = int((sprint.initial_commitment / max_sp) * chart_width) if max_sp > 0 else 0
            initial_bar = "=" * initial_width
            
            # Delivered bar (green - using +)
            delivered_width = int((sprint.delivered_story_points / max_sp) * chart_width) if max_sp > 0 else 0
            delivered_bar = "+" * delivered_width
            
            lines.extend([
                f"{sprint_label}",
                f"  Rollover:   |{rollover_bar.ljust(chart_width)}| {sprint.rollover_story_points:.0f} SP",
                f"  Commitment: |{initial_bar.ljust(chart_width)}| {sprint.initial_commitment:.0f} SP",
                f"  Delivered:  |{delivered_bar.ljust(chart_width)}| {sprint.delivered_story_points:.0f} SP",
                "",
            ])
        
        lines.extend([
            "Legend: # = Rollover, = = Initial Commitment, + = Delivered",
            "```",
            "",
        ])
        
        # Delivery Rate Trend
        lines.extend([
            "## Delivery Rate Trend",
            "",
            "```",
        ])
        
        for sprint in report.sprints:
            sprint_label = sprint.sprint_name[:20].ljust(20)
            rate = sprint.delivery_rate
            bar_width = int(rate / 2.5)  # Scale to 40 chars for 100%
            bar = "*" * bar_width
            status = "OK" if rate >= 80 else "LOW"
            lines.append(f"{sprint_label} |{bar.ljust(40)}| {rate:.0f}% [{status}]")
        
        lines.extend([
            "```",
            "",
        ])
        
        # Sprint-by-sprint table
        lines.extend([
            "## Sprint-by-Sprint Breakdown",
            "",
            "| Sprint | Rollover | Initial | Delivered | Rate | Issues |",
            "|--------|----------|---------|-----------|------|--------|",
        ])
        
        for sprint in report.sprints:
            sprint_name_display = sprint.sprint_name[:25] + ('...' if len(sprint.sprint_name) > 25 else '')
            lines.append(
                f"| {sprint_name_display} | "
                f"{sprint.rollover_story_points:.0f} | "
                f"{sprint.initial_commitment:.0f} | "
                f"**{sprint.delivered_story_points:.0f}** | "
                f"{sprint.delivery_rate:.0f}% | "
                f"{sprint.completed_issues}/{sprint.total_issues} |"
            )
        
        lines.append("")
        
        # AI Contribution
        if report.total_ai_commits > 0 or report.total_ai_assisted_issues > 0:
            lines.extend([
                "## AI Contribution Summary",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Total AI-Assisted Issues | {report.total_ai_assisted_issues} |",
                f"| Total AI Commits | {report.total_ai_commits} |",
                f"| Estimated Time Saved | **{report.total_time_saved_hours:.1f} hours** |",
                "",
                "### AI Contribution by Sprint",
                "",
                "```",
            ])
            
            max_ai = max(s.ai_commits_count for s in report.sprints) if report.sprints else 1
            for sprint in report.sprints:
                sprint_label = sprint.sprint_name[:20].ljust(20)
                ai_width = int((sprint.ai_commits_count / max_ai) * 30) if max_ai > 0 else 0
                ai_bar = "@" * ai_width
                lines.append(f"{sprint_label} |{ai_bar.ljust(30)}| {sprint.ai_commits_count} commits ({sprint.time_saved_hours:.1f}h saved)")
            
            lines.extend([
                "```",
                "",
            ])
        
        lines.extend([
            "---",
            "",
            "*Generated by PND Agents Delivery Report Agent*",
        ])
        
        return "\n".join(lines)


# ==================== Delivery Report Agent Functions ====================

def generate_delivery_report(
    board_ids: List[int],
    workspace_name: str = "Default Workspace",
    project_keys: Optional[List[str]] = None,
    num_sprints: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_ai_metrics: bool = True,
    output_format: str = "markdown"
) -> str:
    """
    Generate multi-sprint velocity report for delivery managers.
    
    Args:
        board_ids: List of JIRA board IDs
        workspace_name: Name for the workspace/report
        project_keys: Optional list of project keys to filter
        num_sprints: Number of recent closed sprints (default: all in date range)
        start_date: Filter sprints starting after this date (YYYY-MM-DD)
        end_date: Filter sprints ending before this date (YYYY-MM-DD)
        include_ai_metrics: Include AI contribution metrics
        output_format: "markdown", "markdown_with_charts", or "json"
    
    Returns:
        Formatted report string
    """
    with DeliveryReportAgent() as agent:
        return agent.generate_report(
            board_ids=board_ids,
            workspace_name=workspace_name,
            project_keys=project_keys,
            num_sprints=num_sprints,
            start_date=start_date,
            end_date=end_date,
            include_ai_metrics=include_ai_metrics,
            output_format=output_format,
        )


def generate_and_publish_delivery_report(
    board_ids: List[int],
    workspace_name: str = "Default Workspace",
    project_keys: Optional[List[str]] = None,
    num_sprints: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    space_key: Optional[str] = None,
    page_title: Optional[str] = None,
    parent_page_id: Optional[str] = None,
    include_ai_metrics: bool = True,
    include_charts: bool = True
) -> Dict[str, Any]:
    """
    Generate multi-sprint velocity report and publish to Confluence.
    
    Args:
        board_ids: List of JIRA board IDs
        workspace_name: Name for the workspace/report
        project_keys: Optional list of project keys to filter
        num_sprints: Number of recent closed sprints
        start_date: Filter sprints starting after this date
        end_date: Filter sprints ending before this date
        space_key: Confluence space key
        page_title: Page title (auto-generated if not provided)
        parent_page_id: Optional parent page ID
        include_ai_metrics: Include AI contribution metrics
        include_charts: Include ASCII charts in output
    
    Returns:
        Dictionary with report content and Confluence page URL
    """
    output_format = "markdown_with_charts" if include_charts else "markdown"
    
    with DeliveryReportAgent() as agent:
        report_content = agent.generate_report(
            board_ids=board_ids,
            workspace_name=workspace_name,
            project_keys=project_keys,
            num_sprints=num_sprints,
            start_date=start_date,
            end_date=end_date,
            include_ai_metrics=include_ai_metrics,
            output_format=output_format,
        )
    
    # Determine space key
    confluence_space = space_key or os.environ.get("CONFLUENCE_SPACE_KEY", "")
    if not confluence_space:
        raise ValueError("Confluence space key not provided. Set CONFLUENCE_SPACE_KEY env var or pass space_key parameter.")
    
    # Determine page title
    title = page_title or f"{workspace_name} - Delivery Report"
    
    # Publish to Confluence
    with ConfluencePublisher() as publisher:
        result = publisher.publish_or_update(
            space_key=confluence_space,
            title=title,
            content=report_content,
            parent_id=parent_page_id
        )
    
    return {
        "workspace_name": workspace_name,
        "report_content": report_content,
        "confluence_page": result
    }
