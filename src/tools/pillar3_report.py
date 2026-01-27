"""
Pillar 3 Report Generator

Generates Pillar 3 status reports from JIRA data with support for:
- Confluence publishing
- Editable PDF generation

The report follows the Pandora Pillar 3 template structure:
- PL (Product Line)
- Team/Initiative
- Type (Milestone/Outcome/Hybrid)
- Objectives
- Key Results
- Status (RAG indicators for Resources, Timing, Budget, Scope)
- Key Milestones with dates and status
- Outcomes and Progress
- Route to Green & Key Watchouts
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger("pnd_agents.pillar3_report")


# ==================== Data Models ====================

class RAGStatus(Enum):
    """RAG status indicator."""
    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"
    NOT_SPECIFIED = "Not specified"


class ReportType(Enum):
    """Pillar 3 report type."""
    MILESTONE = "Milestone"
    OUTCOME = "Outcome"
    HYBRID = "Hybrid"


@dataclass
class Milestone:
    """A key milestone with date and status."""
    name: str
    date: str
    status: str  # "Not started", "In progress", "Completed", "Blocked"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "date": self.date,
            "status": self.status
        }


@dataclass
class Outcome:
    """An outcome with progress description."""
    name: str
    progress: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "progress": self.progress
        }


@dataclass
class StatusRAG:
    """RAG status for different dimensions."""
    resources: RAGStatus = RAGStatus.NOT_SPECIFIED
    timing: RAGStatus = RAGStatus.NOT_SPECIFIED
    budget: RAGStatus = RAGStatus.NOT_SPECIFIED
    scope: RAGStatus = RAGStatus.NOT_SPECIFIED
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "resources": self.resources.value,
            "timing": self.timing.value,
            "budget": self.budget.value,
            "scope": self.scope.value
        }


@dataclass
class Pillar3Report:
    """Complete Pillar 3 report data structure."""
    # Header
    product_line: str = "TBD"
    team_initiative: str = "TBD"
    report_type: ReportType = ReportType.HYBRID
    
    # Content sections
    objectives: List[str] = field(default_factory=list)
    key_results: List[str] = field(default_factory=list)
    status: StatusRAG = field(default_factory=StatusRAG)
    milestones: List[Milestone] = field(default_factory=list)
    outcomes: List[Outcome] = field(default_factory=list)
    route_to_green: List[str] = field(default_factory=list)
    
    # Progress sections (required by Pillar 3 template)
    progress_last_month: List[str] = field(default_factory=list)
    plan_this_month: List[str] = field(default_factory=list)
    
    # Metadata
    generated_at: str = ""
    source_epic_key: str = ""
    source_initiative_key: str = ""
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_line": self.product_line,
            "team_initiative": self.team_initiative,
            "report_type": self.report_type.value,
            "objectives": self.objectives,
            "key_results": self.key_results,
            "status": self.status.to_dict(),
            "milestones": [m.to_dict() for m in self.milestones],
            "outcomes": [o.to_dict() for o in self.outcomes],
            "route_to_green": self.route_to_green,
            "progress_last_month": self.progress_last_month,
            "plan_this_month": self.plan_this_month,
            "generated_at": self.generated_at,
            "source_epic_key": self.source_epic_key,
            "source_initiative_key": self.source_initiative_key
        }


# ==================== JIRA Field Mappings ====================

# Custom field IDs for Pillar 3 data (configurable via environment)
PILLAR3_FIELD_MAPPINGS = {
    "product_line": os.environ.get("JIRA_FIELD_PRODUCT_LINE", "customfield_10100"),
    "report_type": os.environ.get("JIRA_FIELD_REPORT_TYPE", "customfield_10101"),
    "rag_resources": os.environ.get("JIRA_FIELD_RAG_RESOURCES", "customfield_10102"),
    "rag_timing": os.environ.get("JIRA_FIELD_RAG_TIMING", "customfield_10103"),
    "rag_budget": os.environ.get("JIRA_FIELD_RAG_BUDGET", "customfield_10104"),
    "rag_scope": os.environ.get("JIRA_FIELD_RAG_SCOPE", "customfield_10105"),
    "key_results": os.environ.get("JIRA_FIELD_KEY_RESULTS", "customfield_10106"),
    "route_to_green": os.environ.get("JIRA_FIELD_ROUTE_TO_GREEN", "customfield_10107"),
}


# ==================== Pillar 3 Report Generator ====================

class Pillar3ReportGenerator:
    """
    Generates Pillar 3 status reports from JIRA data.
    
    Fetches Epic/Initiative data from JIRA and maps it to the Pillar 3 template.
    Supports output to Confluence or editable PDF.
    """
    
    def __init__(
        self,
        jira_base_url: Optional[str] = None,
        jira_email: Optional[str] = None,
        jira_api_token: Optional[str] = None
    ):
        """Initialize the report generator with JIRA credentials."""
        self.jira_base_url = jira_base_url or os.environ.get("JIRA_BASE_URL", "")
        self.jira_email = jira_email or os.environ.get("JIRA_EMAIL", "")
        self.jira_api_token = jira_api_token or os.environ.get("JIRA_API_TOKEN", "")
        self._client: Optional[httpx.Client] = None
    
    @property
    def client(self) -> httpx.Client:
        """Get or create JIRA HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=f"{self.jira_base_url.rstrip('/')}/rest/api/3/",
                auth=(self.jira_email, self.jira_api_token),
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
    
    # ==================== JIRA Data Fetching ====================
    
    def get_issue(self, issue_key: str, expand: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch a JIRA issue by key."""
        try:
            params = {}
            if expand:
                params["expand"] = expand
            
            response = self.client.get(f"issue/{issue_key}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Issue {issue_key} not found")
                return None
            logger.error(f"Failed to get issue {issue_key}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get issue {issue_key}: {e}")
            raise
    
    def search_issues(self, jql: str, max_results: int = 100, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for issues using JQL.
        
        Uses the newer /search/jql endpoint which is the recommended approach
        for JIRA Cloud REST API v3.
        """
        try:
            # Build query parameters for GET request to /search/jql
            params = {
                "jql": jql,
                "maxResults": max_results,
            }
            if fields:
                params["fields"] = ",".join(fields) if isinstance(fields, list) else fields
            
            # Try the newer /search/jql endpoint first (GET method)
            try:
                response = self.client.get("search/jql", params=params)
                response.raise_for_status()
                return response.json().get("issues", [])
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Fall back to legacy POST /search endpoint
                    logger.info("Falling back to legacy /search endpoint")
                    payload = {
                        "jql": jql,
                        "maxResults": max_results,
                    }
                    if fields:
                        payload["fields"] = fields
                    response = self.client.post("search", json=payload)
                    response.raise_for_status()
                    return response.json().get("issues", [])
                raise
        except Exception as e:
            logger.error(f"Failed to search issues: {e}")
            raise
    
    def get_linked_issues(self, issue_key: str, link_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get issues linked to the given issue."""
        issue = self.get_issue(issue_key)
        if not issue:
            return []
        
        links = issue.get("fields", {}).get("issuelinks", [])
        linked_issues = []
        
        for link in links:
            # Filter by link type if specified
            if link_type and link.get("type", {}).get("name") != link_type:
                continue
            
            # Get the linked issue (could be inward or outward)
            linked = link.get("inwardIssue") or link.get("outwardIssue")
            if linked:
                linked_issues.append(linked)
        
        return linked_issues
    
    def get_child_issues(self, parent_key: str) -> List[Dict[str, Any]]:
        """Get child issues (stories/tasks) under an Epic."""
        jql = f'"Epic Link" = {parent_key} OR parent = {parent_key}'
        return self.search_issues(jql)
    
    # ==================== Data Extraction ====================
    
    def _extract_text_from_adf(self, adf: Any) -> str:
        """Extract plain text from Atlassian Document Format."""
        if not adf:
            return ""
        
        if isinstance(adf, str):
            return adf
        
        if isinstance(adf, dict):
            if adf.get("type") == "text":
                return adf.get("text", "")
            
            content = adf.get("content", [])
            texts = []
            for item in content:
                texts.append(self._extract_text_from_adf(item))
            return " ".join(texts)
        
        if isinstance(adf, list):
            return " ".join(self._extract_text_from_adf(item) for item in adf)
        
        return ""
    
    def _parse_rag_status(self, value: Any) -> RAGStatus:
        """Parse RAG status from JIRA field value."""
        if not value:
            return RAGStatus.NOT_SPECIFIED
        
        value_str = str(value).lower()
        if "green" in value_str:
            return RAGStatus.GREEN
        elif "amber" in value_str or "yellow" in value_str:
            return RAGStatus.AMBER
        elif "red" in value_str:
            return RAGStatus.RED
        
        return RAGStatus.NOT_SPECIFIED
    
    def _derive_rag_from_issues(self, issues: List[Dict[str, Any]]) -> StatusRAG:
        """Derive RAG status from child issue statuses."""
        if not issues:
            return StatusRAG(
                resources=RAGStatus.GREEN,
                timing=RAGStatus.GREEN,
                budget=RAGStatus.GREEN,
                scope=RAGStatus.GREEN
            )
        
        # Count issues by status category
        total = len(issues)
        blocked = 0
        in_progress = 0
        done = 0
        
        for issue in issues:
            status = issue.get("fields", {}).get("status", {})
            category = status.get("statusCategory", {}).get("name", "").lower()
            
            if category == "done":
                done += 1
            elif category == "in progress":
                in_progress += 1
            
            # Check for blocked status
            status_name = status.get("name", "").lower()
            if "blocked" in status_name or "impediment" in status_name:
                blocked += 1
        
        # Derive timing RAG based on progress
        completion_rate = done / total if total > 0 else 0
        
        if blocked > 0:
            timing_rag = RAGStatus.RED
        elif completion_rate < 0.3 and in_progress < total * 0.5:
            timing_rag = RAGStatus.AMBER
        else:
            timing_rag = RAGStatus.GREEN
        
        # Default other dimensions to GREEN unless explicitly set
        return StatusRAG(
            resources=RAGStatus.GREEN,
            timing=timing_rag,
            budget=RAGStatus.GREEN,
            scope=RAGStatus.GREEN
        )
    
    def _extract_milestones_from_issues(self, issues: List[Dict[str, Any]]) -> List[Milestone]:
        """Extract milestones from child issues with due dates."""
        milestones = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            due_date = fields.get("duedate")
            
            # Only include issues with due dates as milestones
            if not due_date:
                continue
            
            summary = fields.get("summary", "")
            status = fields.get("status", {}).get("name", "")
            status_category = fields.get("status", {}).get("statusCategory", {}).get("name", "")
            
            # Map JIRA status to milestone status
            if status_category == "Done":
                milestone_status = "Completed"
            elif status_category == "In Progress":
                milestone_status = "In progress"
            elif "blocked" in status.lower():
                milestone_status = "Blocked"
            else:
                milestone_status = "Not started"
            
            milestones.append(Milestone(
                name=summary,
                date=due_date,
                status=milestone_status
            ))
        
        # Sort by date
        milestones.sort(key=lambda m: m.date)
        return milestones[:10]  # Limit to 10 milestones
    
    def _extract_outcomes_from_issues(self, issues: List[Dict[str, Any]]) -> List[Outcome]:
        """Extract outcomes from completed or in-progress issues."""
        outcomes = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            status_category = fields.get("status", {}).get("statusCategory", {}).get("name", "")
            
            # Only include done or in-progress items as outcomes
            if status_category not in ["Done", "In Progress"]:
                continue
            
            summary = fields.get("summary", "")
            status = fields.get("status", {}).get("name", "")
            
            # Build progress description
            if status_category == "Done":
                progress = "Completed"
            else:
                progress = f"In progress - {status}"
            
            outcomes.append(Outcome(
                name=summary,
                progress=progress
            ))
        
        return outcomes[:8]  # Limit to 8 outcomes
    
    def _extract_objectives_from_description(self, description: Any) -> List[str]:
        """Extract objectives from Epic/Initiative description."""
        text = self._extract_text_from_adf(description)
        if not text:
            return []
        
        objectives = []
        
        # Look for bullet points or numbered items
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            # Match bullet points or numbered items
            if re.match(r'^[-*]\s+', line) or re.match(r'^\d+\.\s+', line):
                # Clean up the line
                clean = re.sub(r'^[-*\d.]+\s+', '', line).strip()
                if clean and len(clean) > 10:  # Filter out very short items
                    objectives.append(clean)
        
        # If no bullet points found, try to extract sentences
        if not objectives:
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences[:5]:  # Take first 5 sentences
                sentence = sentence.strip()
                if sentence and len(sentence) > 20:
                    objectives.append(sentence)
        
        return objectives[:6]  # Limit to 6 objectives
    
    # ==================== Report Generation ====================
    
    def generate_report_from_epic(self, epic_key: str) -> Pillar3Report:
        """
        Generate a Pillar 3 report from a JIRA Epic.
        
        Args:
            epic_key: JIRA Epic key (e.g., "PROJ-123")
            
        Returns:
            Pillar3Report with data populated from JIRA
        """
        logger.info(f"Generating Pillar 3 report from Epic: {epic_key}")
        
        # Fetch the Epic
        epic = self.get_issue(epic_key)
        if not epic:
            raise ValueError(f"Epic {epic_key} not found")
        
        fields = epic.get("fields", {})
        
        # Get child issues (stories/tasks)
        child_issues = self.get_child_issues(epic_key)
        
        # Extract data
        report = Pillar3Report(
            source_epic_key=epic_key,
            team_initiative=fields.get("summary", "TBD"),
            product_line=self._get_product_line(fields),
            report_type=self._get_report_type(fields),
            objectives=self._extract_objectives_from_description(fields.get("description")),
            key_results=self._extract_key_results(fields, child_issues),
            status=self._derive_rag_from_issues(child_issues),
            milestones=self._extract_milestones_from_issues(child_issues),
            outcomes=self._extract_outcomes_from_issues(child_issues),
            route_to_green=self._extract_route_to_green(fields, child_issues),
            progress_last_month=self._extract_progress_last_month(child_issues),
            plan_this_month=self._extract_plan_this_month(child_issues)
        )
        
        # If no objectives found, use child issue summaries
        if not report.objectives:
            report.objectives = [
                issue.get("fields", {}).get("summary", "")
                for issue in child_issues[:4]
                if issue.get("fields", {}).get("summary")
            ]
        
        return report
    
    def generate_report_from_initiative(self, initiative_key: str) -> Pillar3Report:
        """
        Generate a Pillar 3 report from a JIRA Initiative.
        
        Args:
            initiative_key: JIRA Initiative key
            
        Returns:
            Pillar3Report with data populated from JIRA
        """
        logger.info(f"Generating Pillar 3 report from Initiative: {initiative_key}")
        
        # Fetch the Initiative
        initiative = self.get_issue(initiative_key)
        if not initiative:
            raise ValueError(f"Initiative {initiative_key} not found")
        
        fields = initiative.get("fields", {})
        
        # Get linked Epics
        linked_epics = self.get_linked_issues(initiative_key)
        
        # Get all child issues from linked Epics
        all_child_issues = []
        for epic in linked_epics:
            epic_key = epic.get("key")
            if epic_key:
                children = self.get_child_issues(epic_key)
                all_child_issues.extend(children)
        
        # Extract data
        report = Pillar3Report(
            source_initiative_key=initiative_key,
            team_initiative=fields.get("summary", "TBD"),
            product_line=self._get_product_line(fields),
            report_type=self._get_report_type(fields),
            objectives=self._extract_objectives_from_description(fields.get("description")),
            key_results=self._extract_key_results(fields, all_child_issues),
            status=self._derive_rag_from_issues(all_child_issues),
            milestones=self._extract_milestones_from_issues(all_child_issues),
            outcomes=self._extract_outcomes_from_issues(all_child_issues),
            route_to_green=self._extract_route_to_green(fields, all_child_issues),
            progress_last_month=self._extract_progress_last_month(all_child_issues),
            plan_this_month=self._extract_plan_this_month(all_child_issues)
        )
        
        # If no objectives found, use Epic summaries
        if not report.objectives:
            report.objectives = [
                epic.get("fields", {}).get("summary", "")
                for epic in linked_epics[:4]
                if epic.get("fields", {}).get("summary")
            ]
        
        return report
    
    def generate_report_from_jql(self, jql: str, team_name: str = "TBD") -> Pillar3Report:
        """
        Generate a Pillar 3 report from a JQL query.
        
        Args:
            jql: JQL query to fetch issues
            team_name: Team/Initiative name for the report
            
        Returns:
            Pillar3Report with data populated from query results
        """
        logger.info(f"Generating Pillar 3 report from JQL: {jql}")
        
        issues = self.search_issues(jql)
        if not issues:
            raise ValueError(f"No issues found for JQL: {jql}")
        
        # Extract data from issues
        report = Pillar3Report(
            team_initiative=team_name,
            product_line="Online",  # Default
            report_type=ReportType.HYBRID,
            objectives=self._extract_objectives_from_issues(issues),
            key_results=self._extract_key_results_from_issues(issues),
            status=self._derive_rag_from_issues(issues),
            milestones=self._extract_milestones_from_issues(issues),
            outcomes=self._extract_outcomes_from_issues(issues),
            route_to_green=self._extract_route_to_green_from_issues(issues),
            progress_last_month=self._extract_progress_last_month(issues),
            plan_this_month=self._extract_plan_this_month(issues)
        )
        
        return report
    
    # ==================== Helper Methods ====================
    
    def _get_product_line(self, fields: Dict[str, Any]) -> str:
        """Extract product line from JIRA fields."""
        # Try custom field first
        pl_field = PILLAR3_FIELD_MAPPINGS.get("product_line")
        if pl_field and fields.get(pl_field):
            value = fields.get(pl_field)
            if isinstance(value, dict):
                return value.get("value", "TBD")
            return str(value)
        
        # Try project name
        project = fields.get("project", {})
        project_name = project.get("name", "")
        
        # Map common project names to product lines
        if "online" in project_name.lower():
            return "Online"
        elif "retail" in project_name.lower():
            return "Retail"
        
        return "TBD"
    
    def _get_report_type(self, fields: Dict[str, Any]) -> ReportType:
        """Extract report type from JIRA fields."""
        type_field = PILLAR3_FIELD_MAPPINGS.get("report_type")
        if type_field and fields.get(type_field):
            value = str(fields.get(type_field)).lower()
            if "milestone" in value:
                return ReportType.MILESTONE
            elif "outcome" in value:
                return ReportType.OUTCOME
        
        return ReportType.HYBRID
    
    def _extract_key_results(self, fields: Dict[str, Any], child_issues: List[Dict[str, Any]]) -> List[str]:
        """Extract key results from fields or derive from child issues."""
        # Try custom field first
        kr_field = PILLAR3_FIELD_MAPPINGS.get("key_results")
        if kr_field and fields.get(kr_field):
            text = self._extract_text_from_adf(fields.get(kr_field))
            if text:
                return [line.strip() for line in text.split("\n") if line.strip()][:6]
        
        # Derive from child issues
        return self._extract_key_results_from_issues(child_issues)
    
    def _extract_key_results_from_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Derive key results from issue summaries."""
        key_results = []
        
        # Group by status category
        done_issues = []
        in_progress_issues = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            status_category = fields.get("status", {}).get("statusCategory", {}).get("name", "")
            summary = fields.get("summary", "")
            
            if status_category == "Done":
                done_issues.append(summary)
            elif status_category == "In Progress":
                in_progress_issues.append(summary)
        
        # Create key results from completed and in-progress items
        for summary in done_issues[:3]:
            key_results.append(f"{summary} (Completed)")
        
        for summary in in_progress_issues[:3]:
            key_results.append(f"{summary} (In Progress)")
        
        return key_results[:6]
    
    def _extract_objectives_from_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Extract objectives from issue summaries."""
        objectives = []
        
        for issue in issues[:6]:
            summary = issue.get("fields", {}).get("summary", "")
            if summary:
                objectives.append(summary)
        
        return objectives
    
    def _extract_route_to_green(self, fields: Dict[str, Any], child_issues: List[Dict[str, Any]]) -> List[str]:
        """Extract route to green and key watchouts."""
        # Try custom field first
        rtg_field = PILLAR3_FIELD_MAPPINGS.get("route_to_green")
        if rtg_field and fields.get(rtg_field):
            text = self._extract_text_from_adf(fields.get(rtg_field))
            if text:
                return [line.strip() for line in text.split("\n") if line.strip()][:6]
        
        # Derive from blocked/at-risk issues
        return self._extract_route_to_green_from_issues(child_issues)
    
    def _extract_route_to_green_from_issues(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Derive route to green from blocked or at-risk issues."""
        watchouts = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            status = fields.get("status", {}).get("name", "").lower()
            summary = fields.get("summary", "")
            
            # Check for blocked issues
            if "blocked" in status or "impediment" in status:
                watchouts.append(f"Blocked: {summary}")
            
            # Check for overdue issues
            due_date = fields.get("duedate")
            if due_date:
                try:
                    due = datetime.strptime(due_date, "%Y-%m-%d")
                    if due < datetime.now():
                        status_cat = fields.get("status", {}).get("statusCategory", {}).get("name", "")
                        if status_cat != "Done":
                            watchouts.append(f"Overdue: {summary}")
                except ValueError:
                    pass
        
        # Add generic watchouts if none found
        if not watchouts:
            watchouts = ["No critical blockers identified"]
        
        return watchouts[:6]
    
    def _extract_progress_last_month(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Extract progress from last month based on recently completed issues."""
        progress = []
        
        # Get issues completed in the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        for issue in issues:
            fields = issue.get("fields", {})
            status_cat = fields.get("status", {}).get("statusCategory", {}).get("name", "")
            summary = fields.get("summary", "")
            
            # Check if issue was completed recently
            if status_cat == "Done":
                # Try to get resolution date
                resolution_date = fields.get("resolutiondate")
                if resolution_date:
                    try:
                        resolved = datetime.fromisoformat(resolution_date.replace("Z", "+00:00"))
                        if resolved.replace(tzinfo=None) >= thirty_days_ago:
                            progress.append(f"Completed: {summary}")
                    except (ValueError, TypeError):
                        # If we can't parse date, include it anyway
                        progress.append(f"Completed: {summary}")
                else:
                    # No resolution date, include if status is Done
                    progress.append(f"Completed: {summary}")
            
            # Also include issues that moved to In Progress
            elif status_cat == "In Progress":
                updated = fields.get("updated")
                if updated:
                    try:
                        update_date = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                        if update_date.replace(tzinfo=None) >= thirty_days_ago:
                            progress.append(f"In progress: {summary}")
                    except (ValueError, TypeError):
                        pass
        
        if not progress:
            progress = ["Work continued on planned deliverables"]
        
        return progress[:5]
    
    def _extract_plan_this_month(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Extract plan for this month based on upcoming/in-progress issues."""
        plan = []
        
        # Get current date info
        now = datetime.now()
        next_month = now + timedelta(days=30)
        
        for issue in issues:
            fields = issue.get("fields", {})
            status_cat = fields.get("status", {}).get("statusCategory", {}).get("name", "")
            summary = fields.get("summary", "")
            
            # Include issues that are in progress or to do
            if status_cat in ["In Progress", "To Do"]:
                due_date = fields.get("duedate")
                if due_date:
                    try:
                        due = datetime.strptime(due_date, "%Y-%m-%d")
                        # Include if due within next 30 days
                        if due <= next_month:
                            plan.append(f"Complete: {summary}")
                    except ValueError:
                        plan.append(f"Continue: {summary}")
                else:
                    # No due date, include if in progress
                    if status_cat == "In Progress":
                        plan.append(f"Continue: {summary}")
                    else:
                        plan.append(f"Start: {summary}")
        
        if not plan:
            plan = ["Continue work on planned deliverables"]
        
        return plan[:5]
    
    # ==================== Output Formatting ====================
    
    def to_markdown(self, report: Pillar3Report) -> str:
        """Convert report to Markdown format for Confluence."""
        md = []
        
        # Header
        md.append(f"# Pillar 3 Report: {report.team_initiative}")
        md.append("")
        md.append(f"**PL:** {report.product_line}")
        md.append(f"**Type:** {report.report_type.value}")
        md.append(f"**Generated:** {report.generated_at[:10]}")
        md.append("")
        
        # Objectives
        md.append("## Objectives")
        if report.objectives:
            for obj in report.objectives:
                md.append(f"- {obj}")
        else:
            md.append("- TBD")
        md.append("")
        
        # Key Results
        md.append("## Key Results")
        if report.key_results:
            for kr in report.key_results:
                md.append(f"- {kr}")
        else:
            md.append("- TBD")
        md.append("")
        
        # Status
        md.append("## Status")
        md.append("")
        md.append("| Dimension | RAG |")
        md.append("|-----------|-----|")
        md.append(f"| Resources | {report.status.resources.value} |")
        md.append(f"| Timing | {report.status.timing.value} |")
        md.append(f"| Budget | {report.status.budget.value} |")
        md.append(f"| Scope | {report.status.scope.value} |")
        md.append("")
        
        # Outcomes
        if report.outcomes:
            md.append("## Outcomes & Progress")
            md.append("")
            md.append("| Outcome | Progress |")
            md.append("|---------|----------|")
            for outcome in report.outcomes:
                md.append(f"| {outcome.name} | {outcome.progress} |")
            md.append("")
        
        # Milestones
        if report.milestones:
            md.append("## Key Milestones")
            md.append("")
            md.append("| Milestone | Date | Status |")
            md.append("|-----------|------|--------|")
            for milestone in report.milestones:
                md.append(f"| {milestone.name} | {milestone.date} | {milestone.status} |")
            md.append("")
        
        # Route to Green
        md.append("## Route to Green & Key Watchouts")
        if report.route_to_green:
            for item in report.route_to_green:
                md.append(f"- {item}")
        else:
            md.append("- No critical issues identified")
        md.append("")
        
        # Footer
        md.append("---")
        md.append("*Generated by PG AI Squad - Analytics & Reporting Agent*")
        
        return "\n".join(md)
    
    def to_json(self, report: Pillar3Report) -> str:
        """Convert report to JSON format."""
        return json.dumps(report.to_dict(), indent=2)


# ==================== PDF Generation ====================

def generate_pillar3_pdf(report: Pillar3Report, output_path: str, editable: bool = True) -> str:
    """
    Generate a PDF from a Pillar 3 report matching the Pillar 3 template 2026 HYBRID v2 format.
    
    Args:
        report: Pillar3Report data
        output_path: Path for the output PDF file
        editable: If True, creates an editable PDF with form fields
        
    Returns:
        Path to the generated PDF
    """
    try:
        from reportlab.lib.pagesizes import landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib import colors
    except ImportError:
        raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
    
    # Page dimensions (960x540 - widescreen presentation format)
    PAGE_WIDTH = 960
    PAGE_HEIGHT = 540
    
    # Layout constants - two column layout
    LEFT_MARGIN = 30
    RIGHT_MARGIN = 30
    COLUMN_GAP = 20
    LEFT_COL_WIDTH = 450
    RIGHT_COL_X = LEFT_MARGIN + LEFT_COL_WIDTH + COLUMN_GAP
    RIGHT_COL_WIDTH = PAGE_WIDTH - RIGHT_COL_X - RIGHT_MARGIN
    
    # Colors matching Pandora brand
    PANDORA_PINK = HexColor('#E91E8C')
    DARK_GRAY = HexColor('#333333')
    LIGHT_GRAY = HexColor('#666666')
    VERY_LIGHT_GRAY = HexColor('#CCCCCC')
    GREEN = HexColor('#00A651')
    AMBER = HexColor('#FFC107')
    RED = HexColor('#DC3545')
    WHITE = HexColor('#FFFFFF')
    
    def get_rag_color(rag: RAGStatus):
        if rag == RAGStatus.GREEN:
            return GREEN
        elif rag == RAGStatus.AMBER:
            return AMBER
        elif rag == RAGStatus.RED:
            return RED
        return LIGHT_GRAY
    
    def draw_rag_indicator(c, x, y, rag: RAGStatus, size=14):
        c.setFillColor(get_rag_color(rag))
        c.circle(x + size/2, y + size/2, size/2, fill=1, stroke=0)
    
    def draw_section_header(c, x, y, text, width=200):
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(PANDORA_PINK)
        c.drawString(x, y, text)
    
    def truncate_text(text, max_len):
        if len(text) > max_len:
            return text[:max_len-3] + "..."
        return text
    
    c = canvas.Canvas(output_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    
    # ==================== HEADER ====================
    y_header = PAGE_HEIGHT - 30
    
    # PL label
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(LIGHT_GRAY)
    c.drawString(LEFT_MARGIN, y_header, "PL:")
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK_GRAY)
    c.drawString(LEFT_MARGIN + 25, y_header, report.product_line)
    
    # TEAM/INITIATIVE label (center)
    team_x = 200
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(LIGHT_GRAY)
    c.drawString(team_x, y_header, "TEAM/INITIATIVE:")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(PANDORA_PINK)
    c.drawString(team_x + 110, y_header, report.team_initiative.upper())
    
    # TYPE label (right)
    type_x = PAGE_WIDTH - 180
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(LIGHT_GRAY)
    c.drawString(type_x, y_header, "TYPE:")
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK_GRAY)
    c.drawString(type_x + 40, y_header, report.report_type.value.upper())
    
    # ==================== LEFT COLUMN ====================
    
    # --- Objectives Section ---
    y_pos = PAGE_HEIGHT - 60
    draw_section_header(c, LEFT_MARGIN, y_pos, "Objectives")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    y_pos -= 16
    for obj in report.objectives[:4]:
        display_obj = truncate_text(obj, 70)
        c.drawString(LEFT_MARGIN, y_pos, f"• {display_obj}")
        y_pos -= 14
    
    # --- Status Section (RAG indicators) ---
    y_pos -= 10
    draw_section_header(c, LEFT_MARGIN, y_pos, "Status")
    
    # RAG header
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(LIGHT_GRAY)
    c.drawString(LEFT_MARGIN + 100, y_pos, "RAG")
    c.drawString(LEFT_MARGIN + 250, y_pos, "RAG")
    
    y_pos -= 18
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    
    # Row 1: Resources and Timing
    c.drawString(LEFT_MARGIN, y_pos, "Resources")
    draw_rag_indicator(c, LEFT_MARGIN + 95, y_pos - 4, report.status.resources)
    c.drawString(LEFT_MARGIN + 150, y_pos, "Timing")
    draw_rag_indicator(c, LEFT_MARGIN + 245, y_pos - 4, report.status.timing)
    
    y_pos -= 20
    # Row 2: Budget and Scope
    c.drawString(LEFT_MARGIN, y_pos, "Budget")
    draw_rag_indicator(c, LEFT_MARGIN + 95, y_pos - 4, report.status.budget)
    c.drawString(LEFT_MARGIN + 150, y_pos, "Scope")
    draw_rag_indicator(c, LEFT_MARGIN + 245, y_pos - 4, report.status.scope)
    
    # --- Route to Green & Key Watchouts ---
    y_pos -= 25
    draw_section_header(c, LEFT_MARGIN, y_pos, "Route to Green & Key Watchouts")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    y_pos -= 14
    for item in report.route_to_green[:4]:
        display_item = truncate_text(item, 70)
        c.drawString(LEFT_MARGIN, y_pos, f"• {display_item}")
        y_pos -= 13
    
    # --- Progress last month ---
    y_pos -= 10
    draw_section_header(c, LEFT_MARGIN, y_pos, "Progress last month")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    y_pos -= 14
    if report.progress_last_month:
        for item in report.progress_last_month[:3]:
            display_item = truncate_text(item, 70)
            c.drawString(LEFT_MARGIN, y_pos, f"• {display_item}")
            y_pos -= 13
    else:
        c.drawString(LEFT_MARGIN, y_pos, "• TBD")
        y_pos -= 13
    
    # --- Plan for this month ---
    y_pos -= 10
    draw_section_header(c, LEFT_MARGIN, y_pos, "Plan for this month")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    y_pos -= 14
    if report.plan_this_month:
        for item in report.plan_this_month[:3]:
            display_item = truncate_text(item, 70)
            c.drawString(LEFT_MARGIN, y_pos, f"• {display_item}")
            y_pos -= 13
    else:
        c.drawString(LEFT_MARGIN, y_pos, "• TBD")
        y_pos -= 13
    
    # ==================== RIGHT COLUMN ====================
    
    # --- Key Results Section ---
    y_pos = PAGE_HEIGHT - 60
    draw_section_header(c, RIGHT_COL_X, y_pos, "Key Results")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    y_pos -= 16
    for kr in report.key_results[:4]:
        display_kr = truncate_text(kr, 55)
        c.drawString(RIGHT_COL_X, y_pos, f"• {display_kr}")
        y_pos -= 14
    
    # --- Outcomes Table ---
    y_pos -= 15
    draw_section_header(c, RIGHT_COL_X, y_pos, "Outcomes")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(PANDORA_PINK)
    c.drawString(RIGHT_COL_X + 250, y_pos, "Progress")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    y_pos -= 16
    
    for outcome in report.outcomes[:4]:
        name = truncate_text(outcome.name, 35)
        progress = truncate_text(outcome.progress, 30)
        c.drawString(RIGHT_COL_X, y_pos, name)
        c.drawString(RIGHT_COL_X + 250, y_pos, progress)
        y_pos -= 14
    
    # --- Key Milestones Table ---
    y_pos -= 15
    draw_section_header(c, RIGHT_COL_X, y_pos, "Key Milestone")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(PANDORA_PINK)
    c.drawString(RIGHT_COL_X + 250, y_pos, "Date")
    c.drawString(RIGHT_COL_X + 350, y_pos, "Status")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    y_pos -= 16
    
    for milestone in report.milestones[:5]:
        name = truncate_text(milestone.name, 35)
        c.drawString(RIGHT_COL_X, y_pos, name)
        c.drawString(RIGHT_COL_X + 250, y_pos, milestone.date)
        
        # Color code status
        status_lower = milestone.status.lower()
        if "completed" in status_lower or "done" in status_lower:
            c.setFillColor(GREEN)
        elif "progress" in status_lower:
            c.setFillColor(AMBER)
        elif "blocked" in status_lower or "not started" in status_lower:
            c.setFillColor(RED)
        else:
            c.setFillColor(DARK_GRAY)
        c.drawString(RIGHT_COL_X + 350, y_pos, milestone.status)
        c.setFillColor(DARK_GRAY)
        y_pos -= 14
    
    # ==================== FOOTER ====================
    # Team/Initiative name in bottom left
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(PANDORA_PINK)
    c.drawString(LEFT_MARGIN, 15, report.team_initiative)
    
    # Classification in center
    c.setFont("Helvetica", 9)
    c.setFillColor(LIGHT_GRAY)
    c.drawCentredString(PAGE_WIDTH / 2, 15, "Classification: Pandora Internal")
    
    c.save()
    logger.info(f"Generated PDF: {output_path}")
    
    return output_path


# ==================== Confluence Publishing ====================

def publish_pillar3_to_confluence(
    report: Pillar3Report,
    space_key: str,
    page_title: Optional[str] = None,
    parent_page_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publish a Pillar 3 report to Confluence.
    
    Args:
        report: Pillar3Report data
        space_key: Confluence space key
        page_title: Optional page title (defaults to report team/initiative name)
        parent_page_id: Optional parent page ID
        
    Returns:
        Dictionary with page URL and status
    """
    # Import the Confluence publisher from sprint_ai_report
    from tools.sprint_ai_report import ConfluencePublisher
    
    generator = Pillar3ReportGenerator()
    markdown_content = generator.to_markdown(report)
    
    title = page_title or f"Pillar 3 Report: {report.team_initiative}"
    
    with ConfluencePublisher() as publisher:
        result = publisher.publish_or_update(
            space_key=space_key,
            title=title,
            content=markdown_content,
            parent_id=parent_page_id
        )
    
    return result


# ==================== Convenience Functions ====================

def generate_pillar3_report(
    epic_key: Optional[str] = None,
    initiative_key: Optional[str] = None,
    jql: Optional[str] = None,
    team_name: str = "TBD",
    output_format: str = "markdown"
) -> Dict[str, Any]:
    """
    Generate a Pillar 3 report from JIRA data.
    
    Args:
        epic_key: JIRA Epic key to generate report from
        initiative_key: JIRA Initiative key to generate report from
        jql: JQL query to fetch issues
        team_name: Team name (used with JQL)
        output_format: "markdown", "json", or "pdf"
        
    Returns:
        Dictionary with report data and formatted output
    """
    with Pillar3ReportGenerator() as generator:
        if epic_key:
            report = generator.generate_report_from_epic(epic_key)
        elif initiative_key:
            report = generator.generate_report_from_initiative(initiative_key)
        elif jql:
            report = generator.generate_report_from_jql(jql, team_name)
        else:
            raise ValueError("Must provide epic_key, initiative_key, or jql")
        
        result = {
            "report": report.to_dict(),
            "format": output_format
        }
        
        if output_format == "markdown":
            result["content"] = generator.to_markdown(report)
        elif output_format == "json":
            result["content"] = generator.to_json(report)
        elif output_format == "pdf":
            output_path = f"/tmp/pillar3_report_{report.team_initiative.replace(' ', '_')}.pdf"
            generate_pillar3_pdf(report, output_path)
            result["pdf_path"] = output_path
        
        return result


def generate_and_publish_pillar3_report(
    epic_key: Optional[str] = None,
    initiative_key: Optional[str] = None,
    jql: Optional[str] = None,
    team_name: str = "TBD",
    space_key: Optional[str] = None,
    page_title: Optional[str] = None,
    parent_page_id: Optional[str] = None,
    also_generate_pdf: bool = False
) -> Dict[str, Any]:
    """
    Generate a Pillar 3 report and publish to Confluence.
    
    Args:
        epic_key: JIRA Epic key
        initiative_key: JIRA Initiative key
        jql: JQL query
        team_name: Team name (used with JQL)
        space_key: Confluence space key
        page_title: Optional page title
        parent_page_id: Optional parent page ID
        also_generate_pdf: If True, also generates a PDF
        
    Returns:
        Dictionary with report data, Confluence URL, and optional PDF path
    """
    with Pillar3ReportGenerator() as generator:
        if epic_key:
            report = generator.generate_report_from_epic(epic_key)
        elif initiative_key:
            report = generator.generate_report_from_initiative(initiative_key)
        elif jql:
            report = generator.generate_report_from_jql(jql, team_name)
        else:
            raise ValueError("Must provide epic_key, initiative_key, or jql")
        
        result = {
            "report": report.to_dict(),
            "markdown": generator.to_markdown(report)
        }
        
        # Publish to Confluence
        confluence_space = space_key or os.environ.get("CONFLUENCE_SPACE_KEY", "")
        if confluence_space:
            confluence_result = publish_pillar3_to_confluence(
                report=report,
                space_key=confluence_space,
                page_title=page_title,
                parent_page_id=parent_page_id
            )
            result["confluence"] = confluence_result
        
        # Generate PDF if requested
        if also_generate_pdf:
            output_path = f"/tmp/pillar3_report_{report.team_initiative.replace(' ', '_')}.pdf"
            generate_pillar3_pdf(report, output_path)
            result["pdf_path"] = output_path
        
        return result
