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
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "har_get_performance_metrics":
                result = har_analyzer.get_performance_metrics(arguments["file_path"])
                import json
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

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
                import asyncio
                try:
                    bx_agent = BrokenExperienceDetectorAgent(headless=True)
                    report = asyncio.get_event_loop().run_until_complete(
                        bx_agent.scan_site(arguments["url"])
                    )
                    
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

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error executing tool '{name}': {str(e)}"
            )]
