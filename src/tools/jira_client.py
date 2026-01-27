"""
JIRA Client Tool

Provides integration with Atlassian JIRA REST API v3 for the Analytics Agent.
Supports adding comments, updating custom fields, and querying issues.
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

import httpx

logger = logging.getLogger("pnd_agents.jira_client")


@dataclass
class JiraConfig:
    """Configuration for JIRA API connection."""
    base_url: str
    email: str
    api_token: str
    cloud_id: Optional[str] = None
    
    # Custom field IDs (to be configured per JIRA instance)
    field_ai_used: str = "customfield_ai_used"
    field_agent_name: str = "customfield_agent_name"
    field_efficiency_score: str = "customfield_ai_efficiency_score"
    field_duration: str = "customfield_ai_duration"
    
    # Retry and rate limiting configuration
    max_retries: int = 3
    retry_delay_ms: int = 1000
    timeout_ms: int = 30000
    
    # Debug options
    debug: bool = False
    on_request: Optional[Callable[[str, str, Any], None]] = field(default=None, repr=False)
    on_response: Optional[Callable[[str, str, int, int], None]] = field(default=None, repr=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JiraConfig":
        """Create config from dictionary."""
        return cls(
            base_url=data.get("base_url", ""),
            email=data.get("email", ""),
            api_token=data.get("api_token", ""),
            cloud_id=data.get("cloud_id"),
            field_ai_used=data.get("field_ai_used", "customfield_ai_used"),
            field_agent_name=data.get("field_agent_name", "customfield_agent_name"),
            field_efficiency_score=data.get("field_efficiency_score", "customfield_ai_efficiency_score"),
            field_duration=data.get("field_duration", "customfield_ai_duration"),
            max_retries=data.get("max_retries", 3),
            retry_delay_ms=data.get("retry_delay_ms", 1000),
            timeout_ms=data.get("timeout_ms", 30000),
            debug=data.get("debug", False),
        )
    
    @classmethod
    def from_env(cls) -> "JiraConfig":
        """Create config from environment variables."""
        return cls(
            base_url=os.environ.get("JIRA_BASE_URL", ""),
            email=os.environ.get("JIRA_EMAIL", ""),
            api_token=os.environ.get("JIRA_API_TOKEN", ""),
            cloud_id=os.environ.get("JIRA_CLOUD_ID"),
            field_ai_used=os.environ.get("JIRA_FIELD_AI_USED", "customfield_ai_used"),
            field_agent_name=os.environ.get("JIRA_FIELD_AGENT_NAME", "customfield_agent_name"),
            field_efficiency_score=os.environ.get("JIRA_FIELD_EFFICIENCY_SCORE", "customfield_ai_efficiency_score"),
            field_duration=os.environ.get("JIRA_FIELD_DURATION", "customfield_ai_duration"),
            max_retries=int(os.environ.get("JIRA_MAX_RETRIES", "3")),
            retry_delay_ms=int(os.environ.get("JIRA_RETRY_DELAY_MS", "1000")),
            timeout_ms=int(os.environ.get("JIRA_TIMEOUT_MS", "30000")),
            debug=os.environ.get("JIRA_DEBUG", "").lower() in ("true", "1", "yes"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (without sensitive data)."""
        return {
            "base_url": self.base_url,
            "email": self.email,
            "cloud_id": self.cloud_id,
            "field_ai_used": self.field_ai_used,
            "field_agent_name": self.field_agent_name,
            "field_efficiency_score": self.field_efficiency_score,
            "field_duration": self.field_duration,
        }


@dataclass
class JiraIssue:
    """Represents a JIRA issue."""
    key: str
    id: str
    summary: str
    status: str
    issue_type: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    priority: Optional[str] = None
    labels: List[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "JiraIssue":
        """Create issue from API response."""
        fields = data.get("fields", {})
        return cls(
            key=data.get("key", ""),
            id=data.get("id", ""),
            summary=fields.get("summary", ""),
            status=fields.get("status", {}).get("name", ""),
            issue_type=fields.get("issuetype", {}).get("name", ""),
            description=fields.get("description"),
            assignee=fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            priority=fields.get("priority", {}).get("name") if fields.get("priority") else None,
            labels=fields.get("labels", []),
        )


class JiraClient:
    """
    Client for interacting with JIRA REST API v3.
    
    Provides methods for:
    - Adding comments to issues
    - Updating custom fields
    - Querying issues
    - Managing AI-related metadata
    """
    
    API_VERSION = "3"
    
    def __init__(
        self,
        config: Optional[JiraConfig] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize the JIRA client.
        
        Args:
            config: JiraConfig object
            config_path: Path to jira.config.json file
        """
        self.config = config or self._load_config(config_path)
        self._client: Optional[httpx.Client] = None
        
        if not self.config.base_url or not self.config.email or not self.config.api_token:
            logger.warning("JIRA configuration incomplete - some features may not work")
    
    def _load_config(self, config_path: Optional[str] = None) -> JiraConfig:
        """Load configuration from file or environment."""
        # Try config file first
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    # Handle API token from environment for security
                    if not data.get("api_token"):
                        data["api_token"] = os.environ.get("JIRA_API_TOKEN", "")
                    return JiraConfig.from_dict(data)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        # Try default config location
        default_path = Path(__file__).parent.parent / "config" / "jira.config.json"
        if default_path.exists():
            try:
                with open(default_path, "r") as f:
                    data = json.load(f)
                    if not data.get("api_token"):
                        data["api_token"] = os.environ.get("JIRA_API_TOKEN", "")
                    return JiraConfig.from_dict(data)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load config from {default_path}: {e}")
        
        # Fall back to environment variables
        return JiraConfig.from_env()
    
    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self._get_api_base_url(),
                auth=(self.config.email, self.config.api_token),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout_ms / 1000.0,
            )
        return self._client
    
    def _get_api_base_url(self) -> str:
        """Get the API base URL."""
        base = self.config.base_url.rstrip("/")
        return f"{base}/rest/api/{self.API_VERSION}/"
    
    def _calculate_backoff(self, retry_count: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        import random
        base_delay = self.config.retry_delay_ms / 1000.0
        delay = min(base_delay * (2 ** retry_count) + random.random(), 30.0)
        return delay
    
    def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        retry_count: int = 0,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic and rate limit handling."""
        start_time = time.time()
        url = f"{self._get_api_base_url()}{endpoint}"
        
        if self.config.debug:
            logger.debug(f"[JIRA] {method} {endpoint}")
        if self.config.on_request:
            self.config.on_request(method, url, kwargs.get("json"))
        
        try:
            response = getattr(self.client, method.lower())(endpoint, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            
            if self.config.debug:
                logger.debug(f"[JIRA] {method} {endpoint} -> {response.status_code} ({duration_ms}ms)")
            if self.config.on_response:
                self.config.on_response(method, url, response.status_code, duration_ms)
            
            if response.status_code == 429:
                if retry_count < self.config.max_retries:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        delay = int(retry_after)
                    else:
                        delay = self._calculate_backoff(retry_count)
                    logger.warning(f"Rate limited, retrying in {delay}s...")
                    time.sleep(delay)
                    return self._request_with_retry(method, endpoint, retry_count + 1, **kwargs)
                raise httpx.HTTPStatusError(
                    f"Rate limit exceeded after {self.config.max_retries} retries",
                    request=response.request,
                    response=response
                )
            
            if response.status_code >= 500 and retry_count < self.config.max_retries:
                delay = self._calculate_backoff(retry_count)
                logger.warning(f"Server error {response.status_code}, retrying in {delay}s...")
                time.sleep(delay)
                return self._request_with_retry(method, endpoint, retry_count + 1, **kwargs)
            
            return response
        except httpx.TimeoutException:
            if retry_count < self.config.max_retries:
                delay = self._calculate_backoff(retry_count)
                logger.warning(f"Request timeout, retrying in {delay}s...")
                time.sleep(delay)
                return self._request_with_retry(method, endpoint, retry_count + 1, **kwargs)
            raise
        except httpx.RequestError as e:
            if retry_count < self.config.max_retries:
                delay = self._calculate_backoff(retry_count)
                logger.warning(f"Request error: {e}, retrying in {delay}s...")
                time.sleep(delay)
                return self._request_with_retry(method, endpoint, retry_count + 1, **kwargs)
            raise
    
    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ==================== Issue Operations ====================
    
    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None) -> Optional[JiraIssue]:
        """
        Get a JIRA issue by key.
        
        Args:
            issue_key: Issue key (e.g., "EPA-123")
            fields: Optional list of fields to retrieve
            
        Returns:
            JiraIssue object or None if not found
        """
        try:
            params = {}
            if fields:
                params["fields"] = ",".join(fields)
            
            response = self.client.get(f"issue/{issue_key}", params=params)
            response.raise_for_status()
            
            return JiraIssue.from_api_response(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Issue {issue_key} not found")
                return None
            logger.error(f"Failed to get issue {issue_key}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get issue {issue_key}: {e}")
            raise
    
    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
        fields: Optional[List[str]] = None
    ) -> List[JiraIssue]:
        """
        Search for issues using JQL.
        
        Uses the newer /search/jql endpoint which is the recommended approach
        for JIRA Cloud REST API v3. Falls back to legacy /search endpoint if needed.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results
            fields: Optional list of fields to retrieve
            
        Returns:
            List of JiraIssue objects
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
                response = self._request_with_retry("GET", "search/jql", params=params)
                response.raise_for_status()
                data = response.json()
                return [JiraIssue.from_api_response(issue) for issue in data.get("issues", [])]
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
                    response = self._request_with_retry("POST", "search", json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return [JiraIssue.from_api_response(issue) for issue in data.get("issues", [])]
                raise
        except Exception as e:
            logger.error(f"Failed to search issues: {e}")
            raise
    
    def get_issues(
        self,
        issue_keys: List[str],
        fields: Optional[List[str]] = None
    ) -> Dict[str, Optional[JiraIssue]]:
        """
        Get multiple JIRA issues by keys efficiently using batch JQL query.
        
        Args:
            issue_keys: List of issue keys (e.g., ["EPA-123", "EPA-456"])
            fields: Optional list of fields to retrieve
            
        Returns:
            Dictionary mapping issue keys to JiraIssue objects (or None if not found)
        """
        if not issue_keys:
            return {}
        
        results: Dict[str, Optional[JiraIssue]] = {}
        batch_size = 50
        
        for i in range(0, len(issue_keys), batch_size):
            batch = issue_keys[i:i + batch_size]
            quoted_keys = [f'"{k}"' for k in batch]
            jql = f'key in ({",".join(quoted_keys)})'
            
            try:
                issues = self.search_issues(jql, max_results=len(batch), fields=fields)
                for issue in issues:
                    results[issue.key] = issue
                
                for key in batch:
                    if key not in results:
                        results[key] = None
            except Exception as e:
                logger.error(f"Failed to batch fetch issues: {e}")
                for key in batch:
                    results[key] = None
        
        return results
    
    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        priority: Optional[str] = None,
        components: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> Optional[JiraIssue]:
        """
        Create a new JIRA issue.

        Args:
            project_key: Project key (e.g., "PANDORA")
            summary: Issue summary/title
            issue_type: Issue type name (e.g., "Task", "Bug", "TestCase")
            description: Issue description (supports markdown)
            labels: List of labels to add
            priority: Priority name (e.g., "High", "Medium")
            components: List of component names
            custom_fields: Dictionary of custom field IDs to values

        Returns:
            JiraIssue object or None if creation failed
        """
        try:
            fields: Dict[str, Any] = {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
            }

            if description:
                fields["description"] = self._markdown_to_adf(description)

            if labels:
                fields["labels"] = labels

            if priority:
                fields["priority"] = {"name": priority}

            if components:
                fields["components"] = [{"name": c} for c in components]

            if custom_fields:
                fields.update(custom_fields)

            payload = {"fields": fields}

            response = self.client.post("issue", json=payload)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Created issue {data.get('key')}")

            # Fetch the full issue to return
            return self.get_issue(data.get("key"))
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to create issue: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return None

    def create_test_case(
        self,
        project_key: str,
        summary: str,
        description: str,
        labels: Optional[List[str]] = None,
        priority: str = "Medium",
        components: Optional[List[str]] = None,
        test_type: Optional[str] = None,
        test_level: Optional[str] = None,
        testing_cycle: Optional[str] = None,
    ) -> Optional[JiraIssue]:
        """
        Create a TestCase issue in JIRA.

        Args:
            project_key: Project key (e.g., "PANDORA")
            summary: Test case summary (should start with "POC - Validate that")
            description: Full test case description in Gherkin format
            labels: List of labels (e.g., ["qAIn", "Login"])
            priority: Priority (Highest, High, Medium, Low, Lowest)
            components: Component names (UI, API, E2E)
            test_type: Functional or Non-Functional
            test_level: FT-UI, FT-API, SIT, E2E, UAT, A11Y, Performance, Security
            testing_cycle: Smoke, Sanity, Regression, Exploratory

        Returns:
            JiraIssue object or None if creation failed
        """
        # Ensure qAIn label is present
        if labels is None:
            labels = []
        if "qAIn" not in labels:
            labels.append("qAIn")

        # Build custom fields based on your JIRA configuration
        custom_fields = {}
        # Note: You may need to adjust these field IDs based on your JIRA setup
        # custom_fields["customfield_test_type"] = test_type
        # custom_fields["customfield_test_level"] = test_level
        # custom_fields["customfield_testing_cycle"] = testing_cycle

        return self.create_issue(
            project_key=project_key,
            summary=summary,
            issue_type="TestCase",  # Adjust if your issue type has a different name
            description=description,
            labels=labels,
            priority=priority,
            components=components,
            custom_fields=custom_fields if custom_fields else None,
        )

    def link_issues(
        self,
        inward_issue: str,
        outward_issue: str,
        link_type: str = "Tests",
        add_qain_label: bool = True,
    ) -> bool:
        """
        Create a link between two JIRA issues.

        Args:
            inward_issue: The issue key that receives the inward link (e.g., test case)
            outward_issue: The issue key that receives the outward link (e.g., story)
            link_type: Type of link (e.g., "Tests", "Blocks", "Relates", "is tested by")
            add_qain_label: If True (default), adds qAIn label to the outward issue (story)

        Returns:
            True if successful
        """
        try:
            payload = {
                "type": {"name": link_type},
                "inwardIssue": {"key": inward_issue},
                "outwardIssue": {"key": outward_issue},
            }

            response = self.client.post("issueLink", json=payload)
            response.raise_for_status()

            logger.info(f"Linked {inward_issue} to {outward_issue} with '{link_type}'")

            # MANDATORY: Add qAIn label to the story when linking test cases
            if add_qain_label:
                self.ensure_qain_label(outward_issue)

            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to link issues: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Failed to link issues: {e}")
            return False

    def get_issue_links(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get all links for an issue.

        Args:
            issue_key: Issue key (e.g., "PANDORA-123")

        Returns:
            List of issue links
        """
        try:
            response = self.client.get(
                f"issue/{issue_key}",
                params={"fields": "issuelinks"}
            )
            response.raise_for_status()

            data = response.json()
            return data.get("fields", {}).get("issuelinks", [])
        except Exception as e:
            logger.error(f"Failed to get issue links for {issue_key}: {e}")
            return []

    def search_test_cases(
        self,
        project_key: str,
        summary_contains: Optional[str] = None,
        labels: Optional[List[str]] = None,
        max_results: int = 50,
    ) -> List[JiraIssue]:
        """
        Search for existing test cases in a project.

        Args:
            project_key: Project key (e.g., "PANDORA")
            summary_contains: Text to search in summary
            labels: Labels to filter by
            max_results: Maximum results to return

        Returns:
            List of matching test cases
        """
        jql_parts = [
            f'project = "{project_key}"',
            'issuetype = "TestCase"',
        ]

        if summary_contains:
            jql_parts.append(f'summary ~ "{summary_contains}"')

        if labels:
            label_conditions = [f'labels = "{label}"' for label in labels]
            jql_parts.append(f"({' OR '.join(label_conditions)})")

        jql = " AND ".join(jql_parts)

        return self.search_issues(jql, max_results=max_results)

    # ==================== Label Operations ====================

    # Mandatory label for all qAIn agent interactions
    QAIN_LABEL = "qAIn"

    def add_label(
        self,
        issue_key: str,
        label: str,
    ) -> bool:
        """
        Add a label to a JIRA issue if not already present.

        Args:
            issue_key: Issue key (e.g., "EPA-123")
            label: Label to add

        Returns:
            True if successful
        """
        try:
            # Use the update endpoint with add operation for labels
            payload = {
                "update": {
                    "labels": [{"add": label}]
                }
            }

            response = self.client.put(f"issue/{issue_key}", json=payload)
            response.raise_for_status()

            logger.info(f"Added label '{label}' to {issue_key}")
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # Label might already exist or field not editable
                logger.warning(f"Could not add label to {issue_key}: {e.response.text}")
                return False
            logger.error(f"Failed to add label to {issue_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to add label to {issue_key}: {e}")
            return False

    def ensure_qain_label(self, issue_key: str) -> bool:
        """
        Ensure the qAIn label is present on a JIRA issue.

        This is MANDATORY for all qAIn agent interactions (comments, test cases).

        Args:
            issue_key: Issue key (e.g., "EPA-123")

        Returns:
            True if label is present (added or already existed)
        """
        try:
            # First check if label already exists
            issue = self.get_issue(issue_key, fields=["labels"])
            if issue and self.QAIN_LABEL in issue.labels:
                logger.debug(f"qAIn label already exists on {issue_key}")
                return True

            # Add the label
            return self.add_label(issue_key, self.QAIN_LABEL)
        except Exception as e:
            logger.warning(f"Could not ensure qAIn label on {issue_key}: {e}")
            return False

    # ==================== Comment Operations ====================

    def add_comment(
        self,
        issue_key: str,
        body: str,
        visibility: Optional[Dict[str, str]] = None,
        add_qain_label: bool = True,
    ) -> Dict[str, Any]:
        """
        Add a comment to a JIRA issue.

        Args:
            issue_key: Issue key (e.g., "EPA-123")
            body: Comment body (supports markdown)
            visibility: Optional visibility restriction
            add_qain_label: If True (default), adds the qAIn label to the ticket

        Returns:
            API response data
        """
        try:
            # MANDATORY: Add qAIn label to the ticket when commenting
            if add_qain_label:
                self.ensure_qain_label(issue_key)

            # Convert markdown to Atlassian Document Format (ADF)
            payload = {
                "body": self._markdown_to_adf(body)
            }

            if visibility:
                payload["visibility"] = visibility

            response = self.client.post(f"issue/{issue_key}/comment", json=payload)
            response.raise_for_status()

            logger.info(f"Added comment to {issue_key} (qAIn label: {add_qain_label})")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to add comment to {issue_key}: {e}")
            raise
    
    def _markdown_to_adf(self, markdown: str) -> Dict[str, Any]:
        """
        Convert markdown text to Atlassian Document Format (ADF).
        
        Supports: headings, bold, italic, strikethrough, links, code blocks,
        blockquotes, bullet lists, and ordered lists.
        """
        paragraphs = markdown.strip().split("\n\n")
        content = []
        
        for para in paragraphs:
            lines = para.split("\n")
            
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', lines[0]) if lines else None
            if heading_match and len(lines) == 1:
                level = len(heading_match.group(1))
                content.append({
                    "type": "heading",
                    "attrs": {"level": level},
                    "content": self._parse_inline_formatting(heading_match.group(2))
                })
                continue
            
            if lines[0].startswith("```"):
                language = lines[0][3:].strip() or None
                code_lines = []
                i = 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                code_block: Dict[str, Any] = {
                    "type": "codeBlock",
                    "content": [{"type": "text", "text": "\n".join(code_lines)}]
                }
                if language:
                    code_block["attrs"] = {"language": language}
                content.append(code_block)
                continue
            
            if all(line.strip().startswith("- ") for line in lines if line.strip()):
                list_items = []
                for line in lines:
                    if line.strip().startswith("- "):
                        text = line.strip()[2:]
                        list_items.append({
                            "type": "listItem",
                            "content": [{
                                "type": "paragraph",
                                "content": self._parse_inline_formatting(text)
                            }]
                        })
                if list_items:
                    content.append({
                        "type": "bulletList",
                        "content": list_items
                    })
                continue
            
            if all(re.match(r'^\d+\.\s+', line.strip()) for line in lines if line.strip()):
                list_items = []
                for line in lines:
                    match = re.match(r'^\d+\.\s+(.+)$', line.strip())
                    if match:
                        list_items.append({
                            "type": "listItem",
                            "content": [{
                                "type": "paragraph",
                                "content": self._parse_inline_formatting(match.group(1))
                            }]
                        })
                if list_items:
                    content.append({
                        "type": "orderedList",
                        "content": list_items
                    })
                continue
            
            if all(line.startswith(">") or not line.strip() for line in lines):
                quote_content = []
                for line in lines:
                    if line.strip():
                        quote_text = re.sub(r'^>\s?', '', line)
                        quote_content.append({
                            "type": "paragraph",
                            "content": self._parse_inline_formatting(quote_text)
                        })
                if quote_content:
                    content.append({
                        "type": "blockquote",
                        "content": quote_content
                    })
                continue
            
            text_content: List[Dict[str, Any]] = []
            for line in lines:
                if text_content:
                    text_content.append({"type": "hardBreak"})
                text_content.extend(self._parse_inline_formatting(line))
            
            if text_content:
                content.append({
                    "type": "paragraph",
                    "content": text_content
                })
        
        return {
            "type": "doc",
            "version": 1,
            "content": content
        }
    
    def _parse_inline_formatting(self, text: str) -> List[Dict[str, Any]]:
        """Parse inline markdown formatting (bold, italic, links, strikethrough, code)."""
        nodes: List[Dict[str, Any]] = []
        remaining = text
        
        while remaining:
            link_match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', remaining)
            if link_match:
                nodes.append({
                    "type": "text",
                    "text": link_match.group(1),
                    "marks": [{"type": "link", "attrs": {"href": link_match.group(2)}}]
                })
                remaining = remaining[len(link_match.group(0)):]
                continue
            
            bold_match = re.match(r'\*\*(.+?)\*\*', remaining)
            if bold_match:
                nodes.append({
                    "type": "text",
                    "text": bold_match.group(1),
                    "marks": [{"type": "strong"}]
                })
                remaining = remaining[len(bold_match.group(0)):]
                continue
            
            italic_match = re.match(r'\*(.+?)\*', remaining)
            if italic_match:
                nodes.append({
                    "type": "text",
                    "text": italic_match.group(1),
                    "marks": [{"type": "em"}]
                })
                remaining = remaining[len(italic_match.group(0)):]
                continue
            
            strike_match = re.match(r'~~(.+?)~~', remaining)
            if strike_match:
                nodes.append({
                    "type": "text",
                    "text": strike_match.group(1),
                    "marks": [{"type": "strike"}]
                })
                remaining = remaining[len(strike_match.group(0)):]
                continue
            
            code_match = re.match(r'`([^`]+)`', remaining)
            if code_match:
                nodes.append({
                    "type": "text",
                    "text": code_match.group(1),
                    "marks": [{"type": "code"}]
                })
                remaining = remaining[len(code_match.group(0)):]
                continue
            
            next_special = len(remaining)
            for pattern in [r'\[', r'\*\*', r'\*', r'~~', r'`']:
                match = re.search(pattern, remaining[1:])
                if match:
                    next_special = min(next_special, match.start() + 1)
            
            if next_special > 0:
                nodes.append({"type": "text", "text": remaining[:next_special]})
                remaining = remaining[next_special:]
            else:
                nodes.append({"type": "text", "text": remaining})
                break
        
        return nodes if nodes else [{"type": "text", "text": ""}]
    
    # ==================== Custom Field Operations ====================
    
    def update_fields(
        self,
        issue_key: str,
        fields: Dict[str, Any]
    ) -> bool:
        """
        Update fields on a JIRA issue.
        
        Args:
            issue_key: Issue key (e.g., "EPA-123")
            fields: Dictionary of field names/IDs to values
            
        Returns:
            True if successful
        """
        try:
            payload = {"fields": fields}
            
            response = self.client.put(f"issue/{issue_key}", json=payload)
            response.raise_for_status()
            
            logger.info(f"Updated fields on {issue_key}")
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # Field might not exist
                logger.warning(f"Failed to update fields on {issue_key}: {e.response.text}")
                return False
            raise
        except Exception as e:
            logger.error(f"Failed to update fields on {issue_key}: {e}")
            raise
    
    def update_ai_fields(
        self,
        issue_key: str,
        ai_used: bool = True,
        agent_name: Optional[str] = None,
        efficiency_score: Optional[float] = None,
        duration_ms: Optional[float] = None
    ) -> bool:
        """
        Update AI-related custom fields on a JIRA issue.
        
        Args:
            issue_key: Issue key (e.g., "EPA-123")
            ai_used: Whether AI was used
            agent_name: Name of the agent
            efficiency_score: Effectiveness score (0-100)
            duration_ms: Duration in milliseconds
            
        Returns:
            True if successful
        """
        fields: Dict[str, Any] = {}
        
        if self.config.field_ai_used:
            fields[self.config.field_ai_used] = ai_used
        
        if agent_name and self.config.field_agent_name:
            fields[self.config.field_agent_name] = agent_name
        
        if efficiency_score is not None and self.config.field_efficiency_score:
            fields[self.config.field_efficiency_score] = efficiency_score
        
        if duration_ms is not None and self.config.field_duration:
            # Convert to seconds for readability
            fields[self.config.field_duration] = duration_ms / 1000
        
        if not fields:
            logger.warning("No AI fields configured to update")
            return False
        
        return self.update_fields(issue_key, fields)
    
    # ==================== Transition Operations ====================
    
    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get available transitions for an issue.
        
        Args:
            issue_key: Issue key (e.g., "EPA-123")
            
        Returns:
            List of available transitions
        """
        try:
            response = self.client.get(f"issue/{issue_key}/transitions")
            response.raise_for_status()
            
            return response.json().get("transitions", [])
        except Exception as e:
            logger.error(f"Failed to get transitions for {issue_key}: {e}")
            raise
    
    def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        fields: Optional[Dict[str, Any]] = None,
        comment: Optional[str] = None
    ) -> bool:
        """
        Transition an issue to a new status.
        
        Args:
            issue_key: Issue key (e.g., "EPA-123")
            transition_id: ID of the transition to perform
            fields: Optional fields to update during transition
            comment: Optional comment to add
            
        Returns:
            True if successful
        """
        try:
            payload: Dict[str, Any] = {
                "transition": {"id": transition_id}
            }
            
            if fields:
                payload["fields"] = fields
            
            if comment:
                payload["update"] = {
                    "comment": [{
                        "add": {"body": self._markdown_to_adf(comment)}
                    }]
                }
            
            response = self.client.post(f"issue/{issue_key}/transitions", json=payload)
            response.raise_for_status()
            
            logger.info(f"Transitioned {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to transition {issue_key}: {e}")
            raise
    
    # ==================== Project Operations ====================
    
    def get_project(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        Get project details.
        
        Args:
            project_key: Project key (e.g., "EPA")
            
        Returns:
            Project data or None if not found
        """
        try:
            response = self.client.get(f"project/{project_key}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Failed to get project {project_key}: {e}")
            raise
    
    def get_project_issue_types(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Get issue types for a project.
        
        Args:
            project_key: Project key (e.g., "EPA")
            
        Returns:
            List of issue type data
        """
        try:
            response = self.client.get(
                f"issue/createmeta/{project_key}/issuetypes"
            )
            response.raise_for_status()
            return response.json().get("issueTypes", [])
        except Exception as e:
            logger.error(f"Failed to get issue types for {project_key}: {e}")
            raise
    
    # ==================== Utility Methods ====================
    
    def test_connection(self) -> bool:
        """
        Test the JIRA connection.
        
        Returns:
            True if connection is successful
        """
        try:
            response = self.client.get("myself")
            response.raise_for_status()
            user = response.json()
            logger.info(f"Connected to JIRA as {user.get('displayName', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"JIRA connection test failed: {e}")
            return False
    
    def get_field_ids(self) -> Dict[str, str]:
        """
        Get all field IDs and names.
        
        Useful for finding custom field IDs.
        
        Returns:
            Dictionary mapping field names to IDs
        """
        try:
            response = self.client.get("field")
            response.raise_for_status()
            
            fields = response.json()
            return {f["name"]: f["id"] for f in fields}
        except Exception as e:
            logger.error(f"Failed to get field IDs: {e}")
            raise


def generate_custom_fields_readme() -> str:
    """
    Generate README content for creating custom fields in JIRA.
    
    Returns:
        Markdown content with instructions
    """
    return """# JIRA Custom Fields Setup for AI Analytics

This document describes the custom fields required for AI analytics tracking in JIRA.

## Required Custom Fields

Create the following custom fields in your JIRA project:

### 1. AI Used (customfield_ai_used)
- **Type:** Checkbox or Yes/No
- **Description:** Indicates whether AI was used to complete this task
- **Default Value:** No

### 2. Agent Name (customfield_agent_name)
- **Type:** Short Text
- **Description:** Name of the AI agent that worked on this task
- **Example Values:** Frontend Engineer Agent, Unit Test Agent, Code Review Agent

### 3. AI Efficiency Score (customfield_ai_efficiency_score)
- **Type:** Number
- **Description:** Effectiveness score of the AI agent (0-100)
- **Validation:** Min 0, Max 100

### 4. AI Duration (customfield_ai_duration)
- **Type:** Number
- **Description:** Time taken by AI agent in seconds
- **Unit:** Seconds

## Setup Instructions

### For JIRA Cloud (Team-Managed Projects)

1. Go to **Project Settings** > **Issue Types**
2. Select the issue type you want to add fields to
3. Click **Add field** and search for or create each custom field
4. Configure the field type and description as specified above

### For JIRA Cloud (Company-Managed Projects)

1. Go to **Settings** (gear icon) > **Issues** > **Custom fields**
2. Click **Create custom field**
3. Select the appropriate field type
4. Enter the name and description
5. Associate with the appropriate screens

### For JIRA Server/Data Center

1. Go to **Administration** > **Issues** > **Custom fields**
2. Click **Add custom field**
3. Select the field type
4. Configure name, description, and context

## Configuration

After creating the fields, update your `jira.config.json` with the actual field IDs:

```json
{
  "base_url": "https://your-instance.atlassian.net",
  "email": "your-email@example.com",
  "field_ai_used": "customfield_10XXX",
  "field_agent_name": "customfield_10XXX",
  "field_efficiency_score": "customfield_10XXX",
  "field_duration": "customfield_10XXX"
}
```

To find your custom field IDs:
1. Use the JIRA REST API: `GET /rest/api/3/field`
2. Or check the field configuration in JIRA admin

## Environment Variables

Alternatively, configure via environment variables:

```bash
export JIRA_BASE_URL="https://your-instance.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_FIELD_AI_USED="customfield_10XXX"
export JIRA_FIELD_AGENT_NAME="customfield_10XXX"
export JIRA_FIELD_EFFICIENCY_SCORE="customfield_10XXX"
export JIRA_FIELD_DURATION="customfield_10XXX"
```

## API Token

Generate a JIRA API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**
3. Give it a descriptive name
4. Copy the token and store it securely

---
*Generated by AI Productivity Tracker Agent v1.0*
"""
