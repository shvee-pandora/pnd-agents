"""
MCP Tool Registry

Registers all PG AI Squad tools with the MCP server.
"""

from mcp import types
from mcp.server import Server
from typing import Any

from .filesystem import FilesystemTool
from .command_runner import CommandRunner
from .figma_parser import FigmaParser
from .amplience_api import AmplienceAPI
from .har_analyzer import HARAnalyzer

# Import Figma Reader Agent (for API-based Figma reading)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.figma_reader_agent import FigmaReaderAgent
from agents.commerce_agent import CommerceAgent
from agents.broken_experience_detector_agent import BrokenExperienceDetectorAgent
from agents.unit_test_agent import UnitTestAgent
from agents.qa_agent import QAAgent
from agents.sonar_validation_agent import SonarValidationAgent, validate_for_pr
from agents.analytics_agent import AnalyticsAgent
from agents.task_manager_agent import TaskManagerAgent
from tools.jira_client import JiraClient, JiraConfig
from tools.sprint_ai_report import SprintAIReportGenerator, generate_sprint_report, identify_ai_commits_in_range


def register_tools(server: Server) -> None:
    """
    Register all PG AI Squad tools with the MCP server.

    Args:
        server: The MCP server instance to register tools with.
    """

    # Initialize tool instances
    fs_tool = FilesystemTool()
    cmd_runner = CommandRunner()
    figma_parser = FigmaParser()
    amplience_api = AmplienceAPI()
    har_analyzer = HARAnalyzer()

    # Register list_tools handler
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List all available tools."""
        return [
            # Filesystem Tools
            types.Tool(
                name="fs_read_file",
                description="Read the contents of a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        }
                    },
                    "required": ["path"]
                }
            ),
            types.Tool(
                name="fs_write_file",
                description="Write content to a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        },
                        "create_dirs": {
                            "type": "boolean",
                            "description": "Create parent directories if needed (default: true)",
                            "default": True
                        }
                    },
                    "required": ["path", "content"]
                }
            ),
            types.Tool(
                name="fs_list_directory",
                description="List files and directories in a path",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the directory to list"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "List recursively (default: false)",
                            "default": False
                        }
                    },
                    "required": ["path"]
                }
            ),
            types.Tool(
                name="fs_read_json",
                description="Read and parse a JSON file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        }
                    },
                    "required": ["path"]
                }
            ),
            types.Tool(
                name="fs_write_json",
                description="Write data to a JSON file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        },
                        "data": {
                            "type": "object",
                            "description": "Data to write (object or array)"
                        },
                        "indent": {
                            "type": "integer",
                            "description": "JSON indentation level (default: 2)",
                            "default": 2
                        }
                    },
                    "required": ["path", "data"]
                }
            ),

            # Command Runner Tools
            types.Tool(
                name="cmd_run",
                description="Run a shell command",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute"
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Command arguments",
                            "default": []
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds (default: 300)",
                            "default": 300
                        }
                    },
                    "required": ["command"]
                }
            ),
            types.Tool(
                name="cmd_run_eslint",
                description="Run ESLint on specified paths",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Paths to lint"
                        },
                        "fix": {
                            "type": "boolean",
                            "description": "Auto-fix issues (default: false)",
                            "default": False
                        }
                    },
                    "required": ["paths"]
                }
            ),
            types.Tool(
                name="cmd_run_prettier",
                description="Run Prettier code formatter",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Paths to format"
                        },
                        "check": {
                            "type": "boolean",
                            "description": "Check without writing (default: false)",
                            "default": False
                        }
                    },
                    "required": ["paths"]
                }
            ),
            types.Tool(
                name="cmd_run_tests",
                description="Run test suite",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "coverage": {
                            "type": "boolean",
                            "description": "Generate coverage report (default: false)",
                            "default": False
                        }
                    }
                }
            ),

            # Figma Parser Tools
            types.Tool(
                name="figma_parse_file",
                description="Parse a Figma design file and extract component information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Figma JSON export file"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            types.Tool(
                name="figma_extract_colors",
                description="Extract color palette from Figma file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Figma JSON export file"
                        }
                    },
                    "required": ["file_path"]
                }
            ),

            # Figma Reader Agent Tools (API-based)
            types.Tool(
                name="figma_read",
                description="Read a Figma design via the Figma API and extract component metadata, design tokens, variants, and assets. Returns normalized JSON for the Frontend Engineer Agent. Requires FIGMA_ACCESS_TOKEN environment variable.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url_or_file_key": {
                            "type": "string",
                            "description": "Figma file URL (e.g., https://www.figma.com/file/ABC123/Design), node URL with node-id parameter, or just the file key"
                        },
                        "node_id": {
                            "type": "string",
                            "description": "Optional specific node ID to read (if not included in URL)"
                        }
                    },
                    "required": ["url_or_file_key"]
                }
            ),

            # Amplience API Tools
            types.Tool(
                name="amplience_fetch_by_key",
                description="Fetch content from Amplience by delivery key",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Content delivery key"
                        },
                        "vse": {
                            "type": "string",
                            "description": "Virtual staging environment ID (for preview)",
                        }
                    },
                    "required": ["key"]
                }
            ),
            types.Tool(
                name="amplience_fetch_by_id",
                description="Fetch content from Amplience by content ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "vse": {
                            "type": "string",
                            "description": "Virtual staging environment ID (for preview)",
                        }
                    },
                    "required": ["id"]
                }
            ),

            # HAR Analyzer Tools
            types.Tool(
                name="har_parse_file",
                description="Parse and analyze a HAR (HTTP Archive) file for performance insights",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to HAR file"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            types.Tool(
                name="har_get_performance_metrics",
                description="Extract performance metrics from HAR file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to HAR file"
                        }
                    },
                    "required": ["file_path"]
                }
            ),

            # Commerce Agent Tools
            types.Tool(
                name="commerce_find_product_and_prepare_cart",
                description="Find a product matching a natural language shopping goal and prepare cart-add metadata. Understands goals like 'silver bracelet under 700 DKK' or 'heart charms under 400 DKK'. Filters by price, material, and category. Returns product details ready for cart addition.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "Natural language shopping goal (e.g., 'silver bracelet under 700 DKK', 'heart charms under 400 DKK')"
                        },
                        "currency": {
                            "type": "string",
                            "description": "Optional currency override (DKK, GBP, EUR, USD). Defaults to currency detected in goal or DKK.",
                            "enum": ["DKK", "GBP", "EUR", "USD"]
                        }
                    },
                    "required": ["goal"]
                }
            ),

            # Broken Experience Detector Agent Tools
            types.Tool(
                name="broken_experience_detector_scan_site",
                description="Scan a website URL for broken experiences including performance issues, UI/UX problems, accessibility violations, SEO issues, broken links, missing images, and JavaScript errors. Returns a comprehensive JSON report with a score (0-100) and a human-readable markdown summary. Use this to detect issues on any Pandora environment (e.g., https://us.pandora.net) or localhost.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to scan (e.g., 'https://us.pandora.net', 'http://localhost:3000')"
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Output format: 'json' for machine-readable, 'markdown' for human-readable, 'both' for both formats (default: 'both')",
                            "enum": ["json", "markdown", "both"],
                            "default": "both"
                        }
                    },
                    "required": ["url"]
                }
            ),

            # Unit Test Agent Tools
            types.Tool(
                name="unit_test_generate",
                description="Generate comprehensive unit tests for source files with 100% coverage target. Can be used independently without Task Manager. Analyzes source code and generates Jest/Vitest tests for React components, utility functions, hooks, and API routes following Pandora coding standards.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_file": {
                            "type": "string",
                            "description": "Path to the source file to generate tests for"
                        },
                        "content": {
                            "type": "string",
                            "description": "Optional source code content (if file path is not accessible)"
                        },
                        "framework": {
                            "type": "string",
                            "description": "Test framework to use (jest or vitest)",
                            "enum": ["jest", "vitest"],
                            "default": "jest"
                        }
                    },
                    "required": ["source_file"]
                }
            ),
            types.Tool(
                name="unit_test_analyze",
                description="Analyze a source file to identify testable elements including functions, components, hooks, classes, and branches. Returns analysis results for test planning.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_file": {
                            "type": "string",
                            "description": "Path to the source file to analyze"
                        },
                        "content": {
                            "type": "string",
                            "description": "Optional source code content (if file path is not accessible)"
                        }
                    },
                    "required": ["source_file"]
                }
            ),

            # QA Agent Tools
            types.Tool(
                name="qa_validate",
                description="Validate implementation against test cases and acceptance criteria. Gets test cases from user input or validates against provided criteria. Returns validation status, pass rate, and recommendations.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "test_cases": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "type": {"type": "string"}
                                }
                            },
                            "description": "List of test cases to validate against"
                        },
                        "code_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Paths to code files to validate"
                        },
                        "acceptance_criteria": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of acceptance criteria to validate"
                        }
                    },
                    "required": []
                }
            ),

            # Sonar Validation Agent Tools
            types.Tool(
                name="sonar_validate",
                description="Validate code against SonarCloud quality gates. Fetches issues, coverage, duplications, and generates fix plans. Returns comprehensive validation results with quality gate status, issues by severity/type, coverage metrics, and prioritized fix plans. Requires SONAR_TOKEN environment variable.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "branch": {
                            "type": "string",
                            "description": "Branch to validate (default: master)",
                            "default": "master"
                        },
                        "project_key": {
                            "type": "string",
                            "description": "SonarCloud project key (default: pandora-jewelry_spark_pandora-group)",
                            "default": "pandora-jewelry_spark_pandora-group"
                        },
                        "repo_path": {
                            "type": "string",
                            "description": "Optional path to repository for pipeline analysis"
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="sonar_get_issues",
                description="Fetch issues from SonarCloud filtered by severity and type. Returns list of issues with file locations, messages, and rules.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "branch": {
                            "type": "string",
                            "description": "Branch to check (default: master)",
                            "default": "master"
                        },
                        "project_key": {
                            "type": "string",
                            "description": "SonarCloud project key (default: pandora-jewelry_spark_pandora-group)",
                            "default": "pandora-jewelry_spark_pandora-group"
                        },
                        "severities": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]},
                            "description": "Filter by severity levels (e.g., ['BLOCKER', 'CRITICAL'])"
                        },
                        "types": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["BUG", "VULNERABILITY", "CODE_SMELL", "SECURITY_HOTSPOT"]},
                            "description": "Filter by issue types (e.g., ['BUG', 'VULNERABILITY'])"
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="sonar_get_coverage",
                description="Fetch code coverage metrics from SonarCloud including line coverage, branch coverage, and uncovered lines/conditions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "branch": {
                            "type": "string",
                            "description": "Branch to check (default: master)",
                            "default": "master"
                        },
                        "project_key": {
                            "type": "string",
                            "description": "SonarCloud project key (default: pandora-jewelry_spark_pandora-group)",
                            "default": "pandora-jewelry_spark_pandora-group"
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="sonar_get_quality_gate",
                description="Fetch quality gate status from SonarCloud including pass/fail status and condition details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "branch": {
                            "type": "string",
                            "description": "Branch to check (default: master)",
                            "default": "master"
                        },
                        "project_key": {
                            "type": "string",
                            "description": "SonarCloud project key (default: pandora-jewelry_spark_pandora-group)",
                            "default": "pandora-jewelry_spark_pandora-group"
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="sonar_validate_for_pr",
                description="Validate code for PR readiness. Returns validation results, a markdown checklist for PR, and whether the code is ready for PR based on quality gate status.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "branch": {
                            "type": "string",
                            "description": "Branch to validate (default: master)",
                            "default": "master"
                        },
                        "project_key": {
                            "type": "string",
                            "description": "SonarCloud project key (default: pandora-jewelry_spark_pandora-group)",
                            "default": "pandora-jewelry_spark_pandora-group"
                        },
                        "repo_path": {
                            "type": "string",
                            "description": "Optional path to repository for pipeline analysis"
                        }
                    },
                    "required": []
                }
            ),
            # Analytics Agent Tools
            types.Tool(
                name="analytics_track_task_start",
                description="Record the start of an AI agent task. Call this when an agent begins working on a task to track metrics.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Name of the agent starting the task (e.g., 'Frontend Engineer Agent', 'Unit Test Agent')"
                        },
                        "task_description": {
                            "type": "string",
                            "description": "Description of the task being started"
                        },
                        "jira_task_id": {
                            "type": "string",
                            "description": "Optional JIRA issue key (e.g., 'EPA-123')"
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "Optional workflow ID for correlation"
                        }
                    },
                    "required": ["agent_name", "task_description"]
                }
            ),
            types.Tool(
                name="analytics_track_task_end",
                description="Record the completion of an AI agent task. Call this when an agent finishes a task to record metrics and optionally update JIRA.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Name of the agent completing the task"
                        },
                        "jira_task_id": {
                            "type": "string",
                            "description": "Optional JIRA issue key (e.g., 'EPA-123')"
                        },
                        "duration": {
                            "type": "number",
                            "description": "Duration in milliseconds"
                        },
                        "iterations": {
                            "type": "integer",
                            "description": "Number of attempts/iterations made",
                            "default": 1
                        },
                        "errors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of error messages encountered (empty if none)"
                        },
                        "effectiveness_score": {
                            "type": "number",
                            "description": "Effectiveness score (0-100), calculated automatically if not provided"
                        },
                        "requires_human_review": {
                            "type": "boolean",
                            "description": "Whether the task requires human review",
                            "default": False
                        }
                    },
                    "required": ["agent_name"]
                }
            ),
            types.Tool(
                name="analytics_track_task_failure",
                description="Record the failure of an AI agent task. Call this when an agent fails to complete a task.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Name of the agent that failed"
                        },
                        "jira_task_id": {
                            "type": "string",
                            "description": "Optional JIRA issue key (e.g., 'EPA-123')"
                        },
                        "errors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of error messages"
                        }
                    },
                    "required": ["agent_name", "errors"]
                }
            ),
            types.Tool(
                name="analytics_generate_report",
                description="Generate an analytics report for agent performance. Returns JSON or markdown format.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to include in report",
                            "default": 14
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Optional filter by specific agent name"
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format (json or markdown)",
                            "enum": ["json", "markdown"],
                            "default": "json"
                        }
                    }
                }
            ),
            types.Tool(
                name="analytics_list",
                description="List stored analytics data with optional filters. Shows completed, failed, and in-progress tasks.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to include",
                            "default": 7
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Optional filter by agent name"
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional filter by status",
                            "enum": ["started", "completed", "failed"]
                        }
                    }
                }
            ),
            types.Tool(
                name="analytics_update_jira_task",
                description="Update a JIRA issue with AI agent metrics. Adds a formatted comment and updates custom fields. Supports optional JIRA config overrides for different boards/instances.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "jira_task_id": {
                            "type": "string",
                            "description": "JIRA issue key (e.g., 'EPA-123')"
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Name of the agent that completed the task"
                        },
                        "task_name": {
                            "type": "string",
                            "description": "Name/description of the task"
                        },
                        "status": {
                            "type": "string",
                            "description": "Task status (Completed, Failed, etc.)"
                        },
                        "duration_ms": {
                            "type": "number",
                            "description": "Duration in milliseconds"
                        },
                        "iterations": {
                            "type": "integer",
                            "description": "Number of iterations/attempts",
                            "default": 1
                        },
                        "errors": {
                            "type": "integer",
                            "description": "Number of errors encountered",
                            "default": 0
                        },
                        "effectiveness_score": {
                            "type": "number",
                            "description": "Effectiveness score (0-100)"
                        },
                        "requires_human_review": {
                            "type": "boolean",
                            "description": "Whether human review is required",
                            "default": False
                        },
                        "jira_base_url": {
                            "type": "string",
                            "description": "Override JIRA base URL (e.g., 'https://pandoradigital.atlassian.net'). If not provided, uses JIRA_BASE_URL env var."
                        },
                        "jira_email": {
                            "type": "string",
                            "description": "Override JIRA account email. If not provided, uses JIRA_EMAIL env var."
                        }
                    },
                    "required": ["jira_task_id", "agent_name", "status"]
                }
            ),
            types.Tool(
                name="analytics_get_config",
                description="Get the current analytics configuration settings.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="analytics_update_config",
                description="Update analytics configuration settings.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_directory": {
                            "type": "string",
                            "description": "Directory for analytics logs"
                        },
                        "retention_days": {
                            "type": "integer",
                            "description": "Number of days to retain logs"
                        },
                        "default_time_saved_hours": {
                            "type": "number",
                            "description": "Default hours saved per task"
                        },
                        "jira_enabled": {
                            "type": "boolean",
                            "description": "Whether JIRA integration is enabled"
                        }
                    }
                }
            ),

            # JIRA Status Management Tools
            types.Tool(
                name="jira_get_issue",
                description="Get details of a JIRA issue including summary, status, and description.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "JIRA issue key (e.g., 'EPA-123', 'INS-456')"
                        }
                    },
                    "required": ["issue_key"]
                }
            ),
            types.Tool(
                name="jira_get_transitions",
                description="Get available status transitions for a JIRA issue. Returns list of transitions with IDs and names.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "JIRA issue key (e.g., 'EPA-123', 'INS-456')"
                        }
                    },
                    "required": ["issue_key"]
                }
            ),
            types.Tool(
                name="jira_transition_issue",
                description="Transition a JIRA issue to a new status. Use jira_get_transitions first to get available transition IDs.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "JIRA issue key (e.g., 'EPA-123', 'INS-456')"
                        },
                        "transition_id": {
                            "type": "string",
                            "description": "ID of the transition to perform (from jira_get_transitions)"
                        },
                        "comment": {
                            "type": "string",
                            "description": "Optional comment to add with the transition"
                        }
                    },
                    "required": ["issue_key", "transition_id"]
                }
            ),

            # Task Manager Agent Tools
            types.Tool(
                name="task_manager_analyze",
                description="Analyze a task and return the workflow plan without executing. Shows which agents will be used and in what order.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Natural language task description (e.g., 'Create a ProductCard component from Figma design')"
                        }
                    },
                    "required": ["task_description"]
                }
            ),
            types.Tool(
                name="task_manager_run",
                description="Run a complete task workflow through the Task Manager Agent. Orchestrates multiple agents in sequence based on task type.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Natural language task description"
                        },
                        "jira_task_id": {
                            "type": "string",
                            "description": "Optional JIRA issue key for tracking"
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Optional Git branch name"
                        },
                        "parallel": {
                            "type": "boolean",
                            "description": "Run agents in parallel where possible (default: false)",
                            "default": False
                        }
                    },
                    "required": ["task_description"]
                }
            ),
            types.Tool(
                name="task_manager_status",
                description="Get the status of the current or last task workflow.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="task_manager_resume",
                description="Resume a previously interrupted task workflow.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="task_manager_clear",
                description="Clear the current task context to start fresh.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            # Sprint AI Report Tools
            types.Tool(
                name="sprint_ai_report",
                description="Generate a comprehensive sprint report showing AI contribution metrics. Fetches data from JIRA and Azure DevOps to identify AI-generated commits. Designed for scrum masters and non-technical stakeholders - no repo cloning required.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sprint_id": {
                            "type": "integer",
                            "description": "JIRA sprint ID (e.g., 16597)"
                        },
                        "board_id": {
                            "type": "integer",
                            "description": "JIRA board ID to find active sprint (e.g., 795). Use if sprint_id not known."
                        },
                        "include_commits": {
                            "type": "boolean",
                            "description": "Include Azure DevOps commit analysis (default: true)",
                            "default": True
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format: markdown (for display) or json (for processing)",
                            "enum": ["markdown", "json"],
                            "default": "markdown"
                        }
                    }
                }
            ),
            types.Tool(
                name="sprint_ai_commits",
                description="Identify AI-generated commits in a date range by detecting Claude Code signatures. Returns list of commits with author, date, type, and linked JIRA issues.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in ISO format (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in ISO format (YYYY-MM-DD)"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            ),
            # Confluence Publishing Tools
            types.Tool(
                name="confluence_publish_sprint_report",
                description="Generate a sprint AI report and automatically publish it to a Confluence page. Combines sprint_ai_report generation with Confluence publishing in one step.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sprint_id": {
                            "type": "integer",
                            "description": "JIRA sprint ID"
                        },
                        "board_id": {
                            "type": "integer",
                            "description": "JIRA board ID to find active sprint. Use if sprint_id not known."
                        },
                        "space_key": {
                            "type": "string",
                            "description": "Confluence space key (e.g., 'SHAM'). Uses CONFLUENCE_SPACE_KEY env var if not provided."
                        },
                        "page_title": {
                            "type": "string",
                            "description": "Page title. Auto-generated from sprint name if not provided."
                        },
                        "parent_page_id": {
                            "type": "string",
                            "description": "Optional parent page ID to nest the report under."
                        },
                        "include_commits": {
                            "type": "boolean",
                            "description": "Include Azure DevOps commit analysis (default: true)",
                            "default": True
                        }
                    }
                }
            ),
            types.Tool(
                name="confluence_publish_page",
                description="Publish any markdown content to a Confluence page. Creates a new page or updates existing one with the same title.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Markdown content to publish"
                        },
                        "space_key": {
                            "type": "string",
                            "description": "Confluence space key (e.g., 'SHAM')"
                        },
                        "title": {
                            "type": "string",
                            "description": "Page title"
                        },
                        "parent_page_id": {
                            "type": "string",
                            "description": "Optional parent page ID"
                        }
                    },
                    "required": ["content", "space_key", "title"]
                }
            ),
            # Value Delivered Report Tools
            types.Tool(
                name="sprint_value_delivered_report",
                description="Generate end-of-sprint value delivered report with Initiative/OKR linking, reliability metrics (commitment vs delivery, carryover, bug ratio), team breakdown, and AI contribution metrics. Designed for sprint retrospectives and stakeholder reporting.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sprint_id": {
                            "type": "integer",
                            "description": "JIRA sprint ID"
                        },
                        "board_id": {
                            "type": "integer",
                            "description": "JIRA board ID to find active sprint. Use if sprint_id not known."
                        },
                        "team_filter": {
                            "type": "string",
                            "description": "Optional team/project key to filter results (e.g., 'EPA', 'INS')"
                        },
                        "include_ai_metrics": {
                            "type": "boolean",
                            "description": "Include AI contribution metrics (default: true)",
                            "default": True
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format: markdown (for display) or json (for processing)",
                            "enum": ["markdown", "json"],
                            "default": "markdown"
                        }
                    }
                }
            ),
            types.Tool(
                name="confluence_publish_value_delivered_report",
                description="Generate end-of-sprint value delivered report and publish to Confluence. Includes Initiative/OKR linking, reliability metrics, team breakdown, and AI contribution.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sprint_id": {
                            "type": "integer",
                            "description": "JIRA sprint ID"
                        },
                        "board_id": {
                            "type": "integer",
                            "description": "JIRA board ID to find active sprint. Use if sprint_id not known."
                        },
                        "team_filter": {
                            "type": "string",
                            "description": "Optional team/project key to filter results"
                        },
                        "space_key": {
                            "type": "string",
                            "description": "Confluence space key. Uses CONFLUENCE_SPACE_KEY env var if not provided."
                        },
                        "page_title": {
                            "type": "string",
                            "description": "Page title. Auto-generated from sprint name if not provided."
                        },
                        "parent_page_id": {
                            "type": "string",
                            "description": "Optional parent page ID to nest the report under."
                        },
                        "include_ai_metrics": {
                            "type": "boolean",
                            "description": "Include AI contribution metrics (default: true)",
                            "default": True
                        }
                    }
                }
            ),
            types.Tool(
                name="multi_board_value_delivered_report",
                description="Generate value delivered report for multiple boards with comparison. Produces full value delivered report per board (Initiative/OKR, reliability metrics, carryover, AI contribution) plus cross-board comparison section with ASCII charts. Ideal for comparing Online vs Retail or multiple team boards.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board_configs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "board_id": {
                                        "type": "integer",
                                        "description": "JIRA board ID"
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "Display name for the board (e.g., 'FIND - Board 847')"
                                    },
                                    "sprint_id": {
                                        "type": "integer",
                                        "description": "Optional specific sprint ID (uses active sprint if not provided)"
                                    }
                                },
                                "required": ["board_id"]
                            },
                            "description": "List of board configurations to generate reports for"
                        },
                        "include_ai_metrics": {
                            "type": "boolean",
                            "description": "Include AI contribution metrics (default: true)",
                            "default": True
                        },
                        "include_charts": {
                            "type": "boolean",
                            "description": "Include ASCII comparison charts (default: true)",
                            "default": True
                        }
                    },
                    "required": ["board_configs"]
                }
            ),
            # Delivery Report Agent Tools
            types.Tool(
                name="delivery_report_generate",
                description="Generate multi-sprint velocity report for delivery managers. Aggregates data from multiple closed sprints with ASCII horizontal bar charts showing rollover, commitment, and delivered story points. Supports cross-workspace reporting (Online/Retail) and per-sprint trend breakdown.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of JIRA board IDs to aggregate data from"
                        },
                        "workspace_name": {
                            "type": "string",
                            "description": "Name for the workspace/report (e.g., 'Online', 'Retail')",
                            "default": "Default Workspace"
                        },
                        "project_keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of project keys to filter (e.g., ['EPA', 'INS'])"
                        },
                        "num_sprints": {
                            "type": "integer",
                            "description": "Number of recent closed sprints to include (default: all in date range)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Filter sprints starting after this date (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Filter sprints ending before this date (YYYY-MM-DD)"
                        },
                        "include_ai_metrics": {
                            "type": "boolean",
                            "description": "Include AI contribution metrics (default: true)",
                            "default": True
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Output format: markdown, markdown_with_charts, or json",
                            "enum": ["markdown", "markdown_with_charts", "json"],
                            "default": "markdown_with_charts"
                        }
                    },
                    "required": ["board_ids"]
                }
            ),
            types.Tool(
                name="delivery_report_publish",
                description="Generate multi-sprint velocity report and publish to Confluence. Includes ASCII charts, cross-workspace aggregation, and per-sprint breakdown for delivery managers.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of JIRA board IDs to aggregate data from"
                        },
                        "workspace_name": {
                            "type": "string",
                            "description": "Name for the workspace/report (e.g., 'Online', 'Retail')",
                            "default": "Default Workspace"
                        },
                        "project_keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of project keys to filter"
                        },
                        "num_sprints": {
                            "type": "integer",
                            "description": "Number of recent closed sprints to include"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Filter sprints starting after this date (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Filter sprints ending before this date (YYYY-MM-DD)"
                        },
                        "space_key": {
                            "type": "string",
                            "description": "Confluence space key. Uses CONFLUENCE_SPACE_KEY env var if not provided."
                        },
                        "page_title": {
                            "type": "string",
                            "description": "Page title. Auto-generated if not provided."
                        },
                        "parent_page_id": {
                            "type": "string",
                            "description": "Optional parent page ID to nest the report under."
                        },
                        "include_ai_metrics": {
                            "type": "boolean",
                            "description": "Include AI contribution metrics (default: true)",
                            "default": True
                        },
                        "include_charts": {
                            "type": "boolean",
                            "description": "Include ASCII charts in output (default: true)",
                            "default": True
                        }
                    },
                    "required": ["board_ids"]
                }
            ),
            types.Tool(
                name="delivery_report_compare",
                description="Generate comparison report with full report per board plus cross-board comparison table. Each board gets its own section with charts, tables, and AI metrics, followed by a final comparison section showing side-by-side metrics.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board_configs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "board_id": {
                                        "type": "integer",
                                        "description": "JIRA board ID"
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "Display name for the board (e.g., 'Board 847 - Inspire')"
                                    },
                                    "project_keys": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Optional list of project keys to filter"
                                    }
                                },
                                "required": ["board_id"]
                            },
                            "description": "List of board configurations to compare"
                        },
                        "num_sprints": {
                            "type": "integer",
                            "description": "Number of recent closed sprints per board"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Filter sprints starting after this date (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Filter sprints ending before this date (YYYY-MM-DD)"
                        },
                        "include_ai_metrics": {
                            "type": "boolean",
                            "description": "Include AI contribution metrics (default: true)",
                            "default": True
                        }
                    },
                    "required": ["board_configs"]
                }
            ),

            # PR Review Agent Tools
            types.Tool(
                name="pr_review",
                description="Review an Azure DevOps Pull Request with structured, role-aware feedback. Automatically detects tech stack (Frontend, Backend, QA, Infra) and provides comprehensive review including summary, code quality, risk analysis, test coverage, architecture assessment, and actionable recommendations. Supports different review roles: fe (Frontend), qa (QA/Cypress), platform (Infrastructure), backend, or general.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pr_url": {
                            "type": "string",
                            "description": "Azure DevOps PR URL (e.g., https://dev.azure.com/org/project/_git/repo/pullrequest/123)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Review role/persona: 'fe' (Frontend), 'qa' (QA/Cypress), 'platform' (Infrastructure), 'backend', or 'general' (default). If not specified, role is auto-detected from tech stack.",
                            "enum": ["fe", "qa", "platform", "backend", "general"]
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Output format: 'json' for machine-readable, 'markdown' for human-readable (default: 'markdown')",
                            "enum": ["json", "markdown"],
                            "default": "markdown"
                        }
                    },
                    "required": ["pr_url"]
                }
            ),
            types.Tool(
                name="pr_review_get_pr_data",
                description="Fetch raw PR data from Azure DevOps without performing a review. Returns PR metadata, changed files, and diffs. Useful for custom analysis or when you need PR data for other purposes.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pr_url": {
                            "type": "string",
                            "description": "Azure DevOps PR URL (e.g., https://dev.azure.com/org/project/_git/repo/pullrequest/123)"
                        },
                        "include_diffs": {
                            "type": "boolean",
                            "description": "Whether to include file diffs (default: true)",
                            "default": True
                        },
                        "include_content": {
                            "type": "boolean",
                            "description": "Whether to include file contents (default: true)",
                            "default": True
                        }
                    },
                    "required": ["pr_url"]
                }
            ),
            types.Tool(
                name="pr_review_detect_tech_stack",
                description="Detect the technology stack from an Azure DevOps PR. Returns detected stacks (Frontend, Backend, QA, Infra), primary stack, confidence score, and evidence. Useful for understanding what technologies a PR touches.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pr_url": {
                            "type": "string",
                            "description": "Azure DevOps PR URL (e.g., https://dev.azure.com/org/project/_git/repo/pullrequest/123)"
                        }
                    },
                    "required": ["pr_url"]
                }
            ),

            # Technical Debt Agent Tools
            types.Tool(
                name="tech_debt_analyze",
                description="Analyze a repository for technical debt. Identifies TODO/FIXME comments, deprecated code, high complexity, large files/functions, test coverage gaps, dependency issues, and architecture problems. Returns a comprehensive report with severity ratings, impact assessment, and prioritized recommendations. Optionally integrates with SonarCloud for enhanced analysis.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to the repository to analyze (default: current working directory)"
                        },
                        "include_sonarcloud": {
                            "type": "boolean",
                            "description": "Whether to include SonarCloud data if SONAR_TOKEN is available (default: true)",
                            "default": True
                        },
                        "sonar_project_key": {
                            "type": "string",
                            "description": "SonarCloud project key (optional, uses default if not provided)"
                        },
                        "sonar_branch": {
                            "type": "string",
                            "description": "Branch to analyze in SonarCloud (default: main)",
                            "default": "main"
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Output format: 'json' for machine-readable, 'markdown' for human-readable, 'both' for both formats (default: 'both')",
                            "enum": ["json", "markdown", "both"],
                            "default": "both"
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="tech_debt_summary",
                description="Generate an executive summary of technical debt for leadership. Provides high-level risk assessment, key findings, and recommended actions in a concise format suitable for stakeholder communication.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to the repository to analyze (default: current working directory)"
                        },
                        "include_sonarcloud": {
                            "type": "boolean",
                            "description": "Whether to include SonarCloud data if SONAR_TOKEN is available (default: true)",
                            "default": True
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="tech_debt_register",
                description="Generate a detailed technical debt register (inventory). Lists all identified debt items in a tabular format with ID, title, category, severity, effort, and location. Useful for tracking and sprint planning.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to the repository to analyze (default: current working directory)"
                        },
                        "include_sonarcloud": {
                            "type": "boolean",
                            "description": "Whether to include SonarCloud data if SONAR_TOKEN is available (default: true)",
                            "default": True
                        }
                    },
                    "required": []
                }
            ),
        ]

    # Register call_tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        """Handle tool calls."""

        try:
            # Filesystem tools
            if name == "fs_read_file":
                result = fs_tool.read_file(
                    arguments["path"],
                    arguments.get("encoding", "utf-8")
                )
                return [types.TextContent(type="text", text=result)]

            elif name == "fs_write_file":
                result = fs_tool.write_file(
                    arguments["path"],
                    arguments["content"],
                    arguments.get("encoding", "utf-8"),
                    arguments.get("create_dirs", True)
                )
                return [types.TextContent(type="text", text=f"File written: {result}")]

            elif name == "fs_list_directory":
                result = fs_tool.list_directory(
                    arguments["path"],
                    arguments.get("recursive", False)
                )
                files = [f.path for f in result]
                return [types.TextContent(type="text", text="\n".join(files))]

            elif name == "fs_read_json":
                result = fs_tool.read_json(arguments["path"])
                import json
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "fs_write_json":
                result = fs_tool.write_json(
                    arguments["path"],
                    arguments["data"],
                    arguments.get("indent", 2)
                )
                return [types.TextContent(type="text", text=f"JSON written: {result}")]

            # Command runner tools
            elif name == "cmd_run":
                result = cmd_runner.run(
                    arguments["command"],
                    arguments.get("args", []),
                    arguments.get("timeout", 300)
                )
                output = f"Exit code: {result.exit_code}\n\nStdout:\n{result.stdout}\n\nStderr:\n{result.stderr}"
                return [types.TextContent(type="text", text=output)]

            elif name == "cmd_run_eslint":
                result = cmd_runner.run_eslint(
                    arguments["paths"],
                    arguments.get("fix", False)
                )
                output = f"Exit code: {result.exit_code}\n\n{result.stdout}"
                return [types.TextContent(type="text", text=output)]

            elif name == "cmd_run_prettier":
                result = cmd_runner.run_prettier(
                    arguments["paths"],
                    arguments.get("check", False)
                )
                output = f"Exit code: {result.exit_code}\n\n{result.stdout}"
                return [types.TextContent(type="text", text=output)]

            elif name == "cmd_run_tests":
                result = cmd_runner.test(arguments.get("coverage", False))
                output = f"Exit code: {result.exit_code}\n\n{result.stdout}"
                return [types.TextContent(type="text", text=output)]

            # Figma parser tools
            elif name == "figma_parse_file":
                result = figma_parser.parse_file(arguments["file_path"])
                import json
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "figma_extract_colors":
                result = figma_parser.extract_colors(arguments["file_path"])
                import json
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            # Figma Reader Agent tools (API-based)
            elif name == "figma_read":
                import json
                try:
                    figma_reader = FigmaReaderAgent()
                    result = figma_reader.get_component_for_frontend_agent(
                        arguments["url_or_file_key"],
                        arguments.get("node_id")
                    )
                    figma_reader.close()
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except ValueError as ve:
                    return [types.TextContent(type="text", text=f"Figma Reader Error: {str(ve)}")]

            # Amplience API tools
            elif name == "amplience_fetch_by_key":
                result = amplience_api.fetch_by_key(
                    arguments["key"],
                    arguments.get("vse")
                )
                import json
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "amplience_fetch_by_id":
                result = amplience_api.fetch_by_id(
                    arguments["id"],
                    arguments.get("vse")
                )
                import json
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            # HAR analyzer tools
            elif name == "har_parse_file":
                result = har_analyzer.parse_file(arguments["file_path"])
                import json
                return [types.TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]

            elif name == "har_get_performance_metrics":
                result = har_analyzer.get_performance_metrics(arguments["file_path"])
                import json
                return [types.TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]

            # Commerce Agent tools
            elif name == "commerce_find_product_and_prepare_cart":
                import json
                try:
                    commerce_agent = CommerceAgent()
                    result = commerce_agent.find_product_and_prepare_cart(
                        arguments["goal"],
                        arguments.get("currency")
                    )
                    commerce_agent.close()
                    return [types.TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]
                except Exception as ce:
                    return [types.TextContent(type="text", text=f"Commerce Agent Error: {str(ce)}")]

            # Broken Experience Detector Agent tools
            elif name == "broken_experience_detector_scan_site":
                import json
                try:
                    bx_agent = BrokenExperienceDetectorAgent(headless=True)
                    # Use await directly since call_tool is already async
                    report = await bx_agent.scan_site(arguments["url"])
                    
                    output_format = arguments.get("output_format", "both")
                    
                    if output_format == "json":
                        return [types.TextContent(type="text", text=json.dumps(report.to_dict(), indent=2))]
                    elif output_format == "markdown":
                        return [types.TextContent(type="text", text=report.to_markdown())]
                    else:  # both
                        result = {
                            "json": report.to_dict(),
                            "markdown": report.to_markdown()
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as bx_error:
                    return [types.TextContent(type="text", text=f"Broken Experience Detector Error: {str(bx_error)}")]

            # Unit Test Agent tools
            elif name == "unit_test_generate":
                import json
                try:
                    from agents.unit_test_agent import UnitTestAgent, TestFramework
                    
                    framework_str = arguments.get("framework", "jest")
                    framework = TestFramework.JEST if framework_str == "jest" else TestFramework.VITEST
                    
                    agent = UnitTestAgent(framework=framework)
                    test_file = agent.generate_test_file(
                        arguments["source_file"],
                        arguments.get("content")
                    )
                    test_code = agent.generate_test_code(test_file)
                    
                    result = {
                        "testFile": test_file.to_dict(),
                        "testCode": test_code,
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as ut_error:
                    return [types.TextContent(type="text", text=f"Unit Test Agent Error: {str(ut_error)}")]

            elif name == "unit_test_analyze":
                import json
                try:
                    from agents.unit_test_agent import UnitTestAgent
                    
                    agent = UnitTestAgent()
                    analysis = agent.analyze_file(
                        arguments["source_file"],
                        arguments.get("content")
                    )
                    return [types.TextContent(type="text", text=json.dumps(analysis, indent=2))]
                except Exception as ut_error:
                    return [types.TextContent(type="text", text=f"Unit Test Agent Error: {str(ut_error)}")]

            # QA Agent tools
            elif name == "qa_validate":
                import json
                try:
                    from agents.qa_agent import QAAgent
                    
                    agent = QAAgent()
                    result = agent.validate_implementation(
                        test_cases=arguments.get("test_cases", []),
                        code_paths=arguments.get("code_paths", []),
                        acceptance_criteria=arguments.get("acceptance_criteria", []),
                    )
                    return [types.TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]
                except Exception as qa_error:
                    return [types.TextContent(type="text", text=f"QA Agent Error: {str(qa_error)}")]

            # Sonar Validation Agent tools
            elif name == "sonar_validate":
                import json
                try:
                    project_key = arguments.get("project_key", "pandora-jewelry_spark_pandora-group")
                    branch = arguments.get("branch", "master")
                    repo_path = arguments.get("repo_path")
                    
                    agent = SonarValidationAgent(project_key=project_key)
                    result = agent.validate(branch, repo_path)
                    
                    return [types.TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]
                except Exception as sonar_error:
                    return [types.TextContent(type="text", text=f"Sonar Validation Error: {str(sonar_error)}")]

            elif name == "sonar_get_issues":
                import json
                try:
                    project_key = arguments.get("project_key", "pandora-jewelry_spark_pandora-group")
                    branch = arguments.get("branch", "master")
                    severities = arguments.get("severities")
                    types_filter = arguments.get("types")
                    
                    agent = SonarValidationAgent(project_key=project_key)
                    issues = agent.fetch_issues(branch, severities, types_filter)
                    
                    issues_data = [issue.to_dict() for issue in issues]
                    return [types.TextContent(type="text", text=json.dumps(issues_data, indent=2))]
                except Exception as sonar_error:
                    return [types.TextContent(type="text", text=f"Sonar Issues Error: {str(sonar_error)}")]

            elif name == "sonar_get_coverage":
                import json
                try:
                    project_key = arguments.get("project_key", "pandora-jewelry_spark_pandora-group")
                    branch = arguments.get("branch", "master")
                    
                    agent = SonarValidationAgent(project_key=project_key)
                    coverage = agent.fetch_coverage(branch)
                    
                    return [types.TextContent(type="text", text=json.dumps(coverage.to_dict(), indent=2))]
                except Exception as sonar_error:
                    return [types.TextContent(type="text", text=f"Sonar Coverage Error: {str(sonar_error)}")]

            elif name == "sonar_get_quality_gate":
                import json
                try:
                    project_key = arguments.get("project_key", "pandora-jewelry_spark_pandora-group")
                    branch = arguments.get("branch", "master")
                    
                    agent = SonarValidationAgent(project_key=project_key)
                    status = agent.fetch_project_status(branch)
                    
                    return [types.TextContent(type="text", text=json.dumps(status, indent=2))]
                except Exception as sonar_error:
                    return [types.TextContent(type="text", text=f"Sonar Quality Gate Error: {str(sonar_error)}")]

            elif name == "sonar_validate_for_pr":
                import json
                try:
                    project_key = arguments.get("project_key", "pandora-jewelry_spark_pandora-group")
                    branch = arguments.get("branch", "master")
                    repo_path = arguments.get("repo_path")
                    
                    result = validate_for_pr(branch, repo_path, project_key)
                    
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as sonar_error:
                    return [types.TextContent(type="text", text=f"Sonar PR Validation Error: {str(sonar_error)}")]

            # Analytics Agent tools
            elif name == "analytics_track_task_start":
                import json
                try:
                    analytics_agent = AnalyticsAgent()
                    metrics = analytics_agent.on_task_started(
                        agent_name=arguments["agent_name"],
                        task_description=arguments["task_description"],
                        jira_task_id=arguments.get("jira_task_id"),
                        workflow_id=arguments.get("workflow_id"),
                    )
                    result = {
                        "status": "success",
                        "message": f"Task started for {arguments['agent_name']}",
                        "metrics": metrics.to_dict(),
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as analytics_error:
                    return [types.TextContent(type="text", text=f"Analytics Error: {str(analytics_error)}")]

            elif name == "analytics_track_task_end":
                import json
                try:
                    analytics_agent = AnalyticsAgent()
                    metrics_input = {
                        "duration": arguments.get("duration", 0),
                        "iterations": arguments.get("iterations", 1),
                        "errors": arguments.get("errors", []),
                        "effectivenessScore": arguments.get("effectiveness_score"),
                        "requiresHumanReview": arguments.get("requires_human_review", False),
                        "confidenceScore": arguments.get("confidence_score", 1.0),
                    }
                    metrics = analytics_agent.on_task_completed(
                        agent_name=arguments["agent_name"],
                        jira_task_id=arguments.get("jira_task_id"),
                        metrics=metrics_input,
                    )
                    result = {
                        "status": "success",
                        "message": f"Task completed for {arguments['agent_name']}",
                        "metrics": metrics.to_dict(),
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as analytics_error:
                    return [types.TextContent(type="text", text=f"Analytics Error: {str(analytics_error)}")]

            elif name == "analytics_track_task_failure":
                import json
                try:
                    analytics_agent = AnalyticsAgent()
                    metrics = analytics_agent.on_task_failed(
                        agent_name=arguments["agent_name"],
                        jira_task_id=arguments.get("jira_task_id"),
                        errors=arguments.get("errors", []),
                    )
                    result = {
                        "status": "success",
                        "message": f"Task failure recorded for {arguments['agent_name']}",
                        "metrics": metrics.to_dict(),
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as analytics_error:
                    return [types.TextContent(type="text", text=f"Analytics Error: {str(analytics_error)}")]

            elif name == "analytics_generate_report":
                import json
                try:
                    analytics_agent = AnalyticsAgent()
                    output_format = arguments.get("format", "json")
                    days = arguments.get("days", 14)
                    
                    if output_format == "markdown":
                        report = analytics_agent.generate_markdown_report(days=days)
                        return [types.TextContent(type="text", text=report)]
                    else:
                        report = analytics_agent.generate_json_report(days=days)
                        return [types.TextContent(type="text", text=json.dumps(report, indent=2))]
                except Exception as analytics_error:
                    return [types.TextContent(type="text", text=f"Analytics Error: {str(analytics_error)}")]

            elif name == "analytics_list":
                import json
                try:
                    analytics_agent = AnalyticsAgent()
                    analytics = analytics_agent.list_analytics(
                        days=arguments.get("days", 7),
                        agent_name=arguments.get("agent_name"),
                        status=arguments.get("status"),
                    )
                    result = {
                        "status": "success",
                        "count": len(analytics),
                        "tasks": analytics,
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as analytics_error:
                    return [types.TextContent(type="text", text=f"Analytics Error: {str(analytics_error)}")]

            elif name == "analytics_update_jira_task":
                import json
                import os
                try:
                    # Build JIRA config with optional overrides
                    jira_base_url = arguments.get("jira_base_url") or os.environ.get("JIRA_BASE_URL", "")
                    jira_email = arguments.get("jira_email") or os.environ.get("JIRA_EMAIL", "")
                    jira_api_token = os.environ.get("JIRA_API_TOKEN", "")
                    
                    jira_config = JiraConfig(
                        base_url=jira_base_url,
                        email=jira_email,
                        api_token=jira_api_token,
                    )
                    jira_client = JiraClient(config=jira_config)
                    
                    duration_ms = arguments.get("duration_ms", 0)
                    if duration_ms < 60000:
                        duration_str = f"{duration_ms / 1000:.1f}s"
                    else:
                        minutes = duration_ms / 60000
                        seconds = (duration_ms % 60000) / 1000
                        duration_str = f"{minutes:.0f}m {seconds:.0f}s"
                    
                    errors_count = arguments.get("errors", 0)
                    error_str = f"{errors_count} (auto-fixed)" if errors_count > 0 else "0"
                    
                    comment = f"""AI Agent Update - PG AI Squad

Agent: {arguments['agent_name']}
Task: {arguments.get('task_name', 'N/A')}
Status: {arguments['status']}

Metrics:
- Duration: {duration_str}
- Iterations: {arguments.get('iterations', 1)}
- Errors: {error_str}
- Effectiveness Score: {arguments.get('effectiveness_score', 'N/A')}%
- Human Review Required: {'Yes' if arguments.get('requires_human_review') else 'No'}

AI Productivity Tracker Agent v1.0"""
                    
                    jira_client.add_comment(arguments["jira_task_id"], comment)
                    
                    if arguments.get("effectiveness_score") is not None:
                        jira_client.update_ai_fields(
                            arguments["jira_task_id"],
                            ai_used=True,
                            agent_name=arguments["agent_name"],
                            efficiency_score=arguments.get("effectiveness_score"),
                            duration_ms=duration_ms,
                        )
                    
                    result = {
                        "status": "success",
                        "message": f"JIRA issue {arguments['jira_task_id']} updated",
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as jira_error:
                    return [types.TextContent(type="text", text=f"JIRA Update Error: {str(jira_error)}")]

            elif name == "analytics_get_config":
                import json
                try:
                    analytics_agent = AnalyticsAgent()
                    result = {
                        "status": "success",
                        "config": analytics_agent.config,
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as analytics_error:
                    return [types.TextContent(type="text", text=f"Analytics Error: {str(analytics_error)}")]

            elif name == "analytics_update_config":
                import json
                try:
                    analytics_agent = AnalyticsAgent()
                    for key, value in arguments.items():
                        if key in analytics_agent.config:
                            analytics_agent.config[key] = value
                    
                    result = {
                        "status": "success",
                        "message": "Configuration updated",
                        "config": analytics_agent.config,
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as analytics_error:
                    return [types.TextContent(type="text", text=f"Analytics Error: {str(analytics_error)}")]

            # JIRA Status Management tools
            elif name == "jira_get_issue":
                import json
                try:
                    jira_client = JiraClient()
                    issue = jira_client.get_issue(arguments["issue_key"])
                    if issue:
                        result = {
                            "key": issue.key,
                            "summary": issue.summary,
                            "status": issue.status,
                            "issue_type": issue.issue_type,
                            "description": issue.description,
                            "assignee": issue.assignee,
                            "priority": issue.priority,
                            "labels": issue.labels,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                    else:
                        return [types.TextContent(type="text", text=f"Issue {arguments['issue_key']} not found")]
                except Exception as jira_error:
                    return [types.TextContent(type="text", text=f"JIRA Error: {str(jira_error)}")]

            elif name == "jira_get_transitions":
                import json
                try:
                    jira_client = JiraClient()
                    transitions = jira_client.get_transitions(arguments["issue_key"])
                    result = {
                        "issue_key": arguments["issue_key"],
                        "transitions": [
                            {"id": t["id"], "name": t["name"]}
                            for t in transitions
                        ]
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as jira_error:
                    return [types.TextContent(type="text", text=f"JIRA Error: {str(jira_error)}")]

            elif name == "jira_transition_issue":
                import json
                try:
                    jira_client = JiraClient()
                    success = jira_client.transition_issue(
                        issue_key=arguments["issue_key"],
                        transition_id=arguments["transition_id"],
                        comment=arguments.get("comment")
                    )
                    if success:
                        # Fetch updated issue to confirm new status
                        updated_issue = jira_client.get_issue(arguments["issue_key"])
                        result = {
                            "status": "success",
                            "message": f"Issue {arguments['issue_key']} transitioned successfully",
                            "new_status": updated_issue.status if updated_issue else "Unknown"
                        }
                    else:
                        result = {
                            "status": "failed",
                            "message": f"Failed to transition issue {arguments['issue_key']}"
                        }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as jira_error:
                    return [types.TextContent(type="text", text=f"JIRA Error: {str(jira_error)}")]

            # Task Manager Agent tools
            elif name == "task_manager_analyze":
                import json
                try:
                    task_manager = TaskManagerAgent()
                    result = task_manager.analyze_task(arguments["task_description"])
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as tm_error:
                    return [types.TextContent(type="text", text=f"Task Manager Error: {str(tm_error)}")]

            elif name == "task_manager_run":
                import json
                try:
                    task_manager = TaskManagerAgent()
                    metadata = {}
                    if arguments.get("jira_task_id"):
                        metadata["jira_task_id"] = arguments["jira_task_id"]
                    if arguments.get("branch_name"):
                        metadata["branch_name"] = arguments["branch_name"]
                    
                    if arguments.get("parallel", False):
                        context = task_manager.run_task_parallel(
                            arguments["task_description"],
                            metadata=metadata if metadata else None,
                            verbose=False
                        )
                    else:
                        context = task_manager.run_task(
                            arguments["task_description"],
                            metadata=metadata if metadata else None,
                            verbose=False
                        )
                    result = task_manager.to_dict(context)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as tm_error:
                    return [types.TextContent(type="text", text=f"Task Manager Error: {str(tm_error)}")]

            elif name == "task_manager_status":
                import json
                try:
                    task_manager = TaskManagerAgent()
                    status = task_manager.get_status()
                    if status:
                        return [types.TextContent(type="text", text=json.dumps(status, indent=2))]
                    else:
                        return [types.TextContent(type="text", text=json.dumps({"status": "no_task", "message": "No task found"}, indent=2))]
                except Exception as tm_error:
                    return [types.TextContent(type="text", text=f"Task Manager Error: {str(tm_error)}")]

            elif name == "task_manager_resume":
                import json
                try:
                    task_manager = TaskManagerAgent()
                    context = task_manager.resume_task(verbose=False)
                    if context:
                        result = task_manager.to_dict(context)
                        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                    else:
                        return [types.TextContent(type="text", text=json.dumps({"status": "no_task", "message": "No interrupted task found"}, indent=2))]
                except Exception as tm_error:
                    return [types.TextContent(type="text", text=f"Task Manager Error: {str(tm_error)}")]

            elif name == "task_manager_clear":
                import json
                try:
                    task_manager = TaskManagerAgent()
                    task_manager.clear_task()
                    return [types.TextContent(type="text", text=json.dumps({"status": "success", "message": "Task context cleared"}, indent=2))]
                except Exception as tm_error:
                    return [types.TextContent(type="text", text=f"Task Manager Error: {str(tm_error)}")]

            # Sprint AI Report Tools
            elif name == "sprint_ai_report":
                import json
                try:
                    sprint_id = arguments.get("sprint_id")
                    board_id = arguments.get("board_id")
                    include_commits = arguments.get("include_commits", True)
                    output_format = arguments.get("format", "markdown")

                    if not sprint_id and not board_id:
                        return [types.TextContent(type="text", text="Error: Either sprint_id or board_id must be provided")]

                    report = generate_sprint_report(
                        sprint_id=sprint_id,
                        board_id=board_id,
                        include_commits=include_commits,
                        output_format=output_format
                    )
                    return [types.TextContent(type="text", text=report)]
                except Exception as report_error:
                    return [types.TextContent(type="text", text=f"Sprint Report Error: {str(report_error)}")]

            elif name == "sprint_ai_commits":
                import json
                try:
                    start_date = arguments["start_date"]
                    end_date = arguments["end_date"]

                    commits = identify_ai_commits_in_range(start_date, end_date)
                    result = {
                        "status": "success",
                        "count": len(commits),
                        "commits": commits
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as commits_error:
                    return [types.TextContent(type="text", text=f"AI Commits Error: {str(commits_error)}")]

            # Confluence Publishing Tools
            elif name == "confluence_publish_sprint_report":
                import json
                try:
                    from .sprint_ai_report import generate_and_publish_sprint_report

                    sprint_id = arguments.get("sprint_id")
                    board_id = arguments.get("board_id")

                    if not sprint_id and not board_id:
                        return [types.TextContent(type="text", text="Error: Either sprint_id or board_id must be provided")]

                    result = generate_and_publish_sprint_report(
                        sprint_id=sprint_id,
                        board_id=board_id,
                        space_key=arguments.get("space_key"),
                        page_title=arguments.get("page_title"),
                        parent_page_id=arguments.get("parent_page_id"),
                        include_commits=arguments.get("include_commits", True)
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as publish_error:
                    return [types.TextContent(type="text", text=f"Confluence Publish Error: {str(publish_error)}")]

            elif name == "confluence_publish_page":
                import json
                try:
                    from .sprint_ai_report import publish_to_confluence

                    result = publish_to_confluence(
                        content=arguments["content"],
                        space_key=arguments["space_key"],
                        title=arguments["title"],
                        parent_page_id=arguments.get("parent_page_id")
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as publish_error:
                    return [types.TextContent(type="text", text=f"Confluence Publish Error: {str(publish_error)}")]

            # Value Delivered Report Tools
            elif name == "sprint_value_delivered_report":
                import json
                try:
                    from .sprint_ai_report import generate_value_delivered_report

                    sprint_id = arguments.get("sprint_id")
                    board_id = arguments.get("board_id")

                    if not sprint_id and not board_id:
                        return [types.TextContent(type="text", text="Error: Either sprint_id or board_id must be provided")]

                    result = generate_value_delivered_report(
                        sprint_id=sprint_id,
                        board_id=board_id,
                        team_filter=arguments.get("team_filter"),
                        include_ai_metrics=arguments.get("include_ai_metrics", True),
                        output_format=arguments.get("format", "markdown")
                    )
                    return [types.TextContent(type="text", text=result)]
                except Exception as report_error:
                    return [types.TextContent(type="text", text=f"Value Delivered Report Error: {str(report_error)}")]

            elif name == "confluence_publish_value_delivered_report":
                import json
                try:
                    from .sprint_ai_report import generate_and_publish_value_delivered_report

                    sprint_id = arguments.get("sprint_id")
                    board_id = arguments.get("board_id")

                    if not sprint_id and not board_id:
                        return [types.TextContent(type="text", text="Error: Either sprint_id or board_id must be provided")]

                    result = generate_and_publish_value_delivered_report(
                        sprint_id=sprint_id,
                        board_id=board_id,
                        team_filter=arguments.get("team_filter"),
                        space_key=arguments.get("space_key"),
                        page_title=arguments.get("page_title"),
                        parent_page_id=arguments.get("parent_page_id"),
                        include_ai_metrics=arguments.get("include_ai_metrics", True)
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as publish_error:
                    return [types.TextContent(type="text", text=f"Value Delivered Report Publish Error: {str(publish_error)}")]

            elif name == "multi_board_value_delivered_report":
                try:
                    from .sprint_ai_report import generate_multi_board_value_delivered_report

                    board_configs = arguments.get("board_configs", [])
                    if not board_configs:
                        return [types.TextContent(type="text", text="Error: board_configs is required")]

                    result = generate_multi_board_value_delivered_report(
                        board_configs=board_configs,
                        include_ai_metrics=arguments.get("include_ai_metrics", True),
                        include_charts=arguments.get("include_charts", True)
                    )
                    return [types.TextContent(type="text", text=result)]
                except Exception as report_error:
                    return [types.TextContent(type="text", text=f"Multi-Board Value Delivered Report Error: {str(report_error)}")]

            # Delivery Report Agent Tools
            elif name == "delivery_report_generate":
                import json
                try:
                    from .delivery_report_agent import generate_delivery_report

                    board_ids = arguments.get("board_ids", [])
                    if not board_ids:
                        return [types.TextContent(type="text", text="Error: board_ids is required")]

                    result = generate_delivery_report(
                        board_ids=board_ids,
                        workspace_name=arguments.get("workspace_name", "Default Workspace"),
                        project_keys=arguments.get("project_keys"),
                        num_sprints=arguments.get("num_sprints"),
                        start_date=arguments.get("start_date"),
                        end_date=arguments.get("end_date"),
                        include_ai_metrics=arguments.get("include_ai_metrics", True),
                        output_format=arguments.get("output_format", "markdown_with_charts")
                    )
                    return [types.TextContent(type="text", text=result)]
                except Exception as report_error:
                    return [types.TextContent(type="text", text=f"Delivery Report Error: {str(report_error)}")]

            elif name == "delivery_report_publish":
                import json
                try:
                    from .delivery_report_agent import generate_and_publish_delivery_report

                    board_ids = arguments.get("board_ids", [])
                    if not board_ids:
                        return [types.TextContent(type="text", text="Error: board_ids is required")]

                    result = generate_and_publish_delivery_report(
                        board_ids=board_ids,
                        workspace_name=arguments.get("workspace_name", "Default Workspace"),
                        project_keys=arguments.get("project_keys"),
                        num_sprints=arguments.get("num_sprints"),
                        start_date=arguments.get("start_date"),
                        end_date=arguments.get("end_date"),
                        space_key=arguments.get("space_key"),
                        page_title=arguments.get("page_title"),
                        parent_page_id=arguments.get("parent_page_id"),
                        include_ai_metrics=arguments.get("include_ai_metrics", True),
                        include_charts=arguments.get("include_charts", True)
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as publish_error:
                    return [types.TextContent(type="text", text=f"Delivery Report Publish Error: {str(publish_error)}")]

            elif name == "delivery_report_compare":
                try:
                    from .delivery_report_agent import generate_delivery_report_comparison

                    board_configs = arguments.get("board_configs", [])
                    if not board_configs:
                        return [types.TextContent(type="text", text="Error: board_configs is required")]

                    result = generate_delivery_report_comparison(
                        board_configs=board_configs,
                        num_sprints=arguments.get("num_sprints"),
                        start_date=arguments.get("start_date"),
                        end_date=arguments.get("end_date"),
                        include_ai_metrics=arguments.get("include_ai_metrics", True)
                    )
                    return [types.TextContent(type="text", text=result)]
                except Exception as compare_error:
                    return [types.TextContent(type="text", text=f"Delivery Report Compare Error: {str(compare_error)}")]

            elif name == "unit_test_advisor":
                import json
                try:
                    from agents.unit_test_advisor import UnitTestAdvisorAgent
                    
                    agent = UnitTestAdvisorAgent()
                    result = agent.run({
                        "task_description": arguments.get("task", "Analyze and provide recommendations"),
                        "input_data": {
                            "files": [arguments["source_file"]] if arguments.get("source_file") else [],
                        }
                    })
                    # Convert result to dict if it has to_dict method (generated agents return dataclass)
                    if hasattr(result, "to_dict"):
                        result = result.to_dict()
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as e:
                    return [types.TextContent(type="text", text=f"UnitTestAdvisor Agent Error: {str(e)}")]

            # PR Review Agent Tools
            elif name == "pr_review":
                import json
                try:
                    from agents.pr_review_agent import PRReviewAgent, ReviewRole
                    
                    pr_url = arguments.get("pr_url")
                    if not pr_url:
                        return [types.TextContent(type="text", text="Error: pr_url is required")]
                    
                    role_str = arguments.get("role", "general")
                    role_map = {
                        "fe": ReviewRole.FRONTEND,
                        "frontend": ReviewRole.FRONTEND,
                        "qa": ReviewRole.QA,
                        "platform": ReviewRole.PLATFORM,
                        "backend": ReviewRole.BACKEND,
                        "general": ReviewRole.GENERAL,
                    }
                    role = role_map.get(role_str.lower(), ReviewRole.GENERAL)
                    
                    output_format = arguments.get("output_format", "markdown")
                    
                    agent = PRReviewAgent()
                    result = agent.review_pr(pr_url, role)
                    agent.close()
                    
                    if output_format == "json":
                        return [types.TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]
                    else:
                        return [types.TextContent(type="text", text=result.to_markdown())]
                except Exception as pr_error:
                    return [types.TextContent(type="text", text=f"PR Review Agent Error: {str(pr_error)}")]

            elif name == "pr_review_get_pr_data":
                import json
                try:
                    from tools.azure_devops_pr_client import AzureDevOpsPRClient
                    
                    pr_url = arguments.get("pr_url")
                    if not pr_url:
                        return [types.TextContent(type="text", text="Error: pr_url is required")]
                    
                    include_diffs = arguments.get("include_diffs", True)
                    include_content = arguments.get("include_content", True)
                    
                    client = AzureDevOpsPRClient()
                    pr_data = client.get_pr_for_review(pr_url, include_diffs, include_content)
                    client.close()
                    
                    return [types.TextContent(type="text", text=json.dumps(pr_data.to_dict(), indent=2))]
                except Exception as pr_error:
                    return [types.TextContent(type="text", text=f"PR Data Fetch Error: {str(pr_error)}")]

            elif name == "pr_review_detect_tech_stack":
                import json
                try:
                    from agents.pr_review_agent import PRReviewAgent
                    
                    pr_url = arguments.get("pr_url")
                    if not pr_url:
                        return [types.TextContent(type="text", text="Error: pr_url is required")]
                    
                    agent = PRReviewAgent()
                    pr_data = agent.pr_client.get_pr_for_review(pr_url)
                    tech_stack = agent.stack_detector.detect(pr_data.files, pr_data.diffs)
                    agent.close()
                    
                    return [types.TextContent(type="text", text=json.dumps(tech_stack.to_dict(), indent=2))]
                except Exception as pr_error:
                    return [types.TextContent(type="text", text=f"Tech Stack Detection Error: {str(pr_error)}")]

            # Technical Debt Agent Tools
            elif name == "tech_debt_analyze":
                import json
                try:
                    from agents.technical_debt_agent import TechnicalDebtAgent
                    
                    repo_path = arguments.get("repo_path") or os.getcwd()
                    include_sonarcloud = arguments.get("include_sonarcloud", True)
                    sonar_project_key = arguments.get("sonar_project_key")
                    sonar_branch = arguments.get("sonar_branch", "main")
                    output_format = arguments.get("output_format", "both")
                    
                    agent = TechnicalDebtAgent()
                    report = agent.analyze(
                        repo_path=repo_path,
                        include_sonarcloud=include_sonarcloud,
                        sonar_project_key=sonar_project_key,
                        sonar_branch=sonar_branch,
                        output_format=output_format
                    )
                    
                    if output_format == "json":
                        return [types.TextContent(type="text", text=json.dumps(report.to_dict(), indent=2))]
                    elif output_format == "markdown":
                        return [types.TextContent(type="text", text=report.to_markdown())]
                    else:  # both
                        result = {
                            "json": report.to_dict(),
                            "markdown": report.to_markdown()
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                except Exception as td_error:
                    return [types.TextContent(type="text", text=f"Technical Debt Analysis Error: {str(td_error)}")]

            elif name == "tech_debt_summary":
                try:
                    from agents.technical_debt_agent import TechnicalDebtAgent
                    
                    repo_path = arguments.get("repo_path") or os.getcwd()
                    include_sonarcloud = arguments.get("include_sonarcloud", True)
                    
                    agent = TechnicalDebtAgent()
                    summary = agent.generate_summary(repo_path, include_sonarcloud=include_sonarcloud)
                    
                    return [types.TextContent(type="text", text=summary)]
                except Exception as td_error:
                    return [types.TextContent(type="text", text=f"Technical Debt Summary Error: {str(td_error)}")]

            elif name == "tech_debt_register":
                try:
                    from agents.technical_debt_agent import TechnicalDebtAgent
                    
                    repo_path = arguments.get("repo_path") or os.getcwd()
                    include_sonarcloud = arguments.get("include_sonarcloud", True)
                    
                    agent = TechnicalDebtAgent()
                    register = agent.generate_register(repo_path, include_sonarcloud=include_sonarcloud)
                    
                    return [types.TextContent(type="text", text=register)]
                except Exception as td_error:
                    return [types.TextContent(type="text", text=f"Technical Debt Register Error: {str(td_error)}")]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error executing tool '{name}': {str(e)}"
            )]
