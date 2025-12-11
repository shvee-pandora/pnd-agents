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

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error executing tool '{name}': {str(e)}"
            )]
