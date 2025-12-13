"""
Analytics MCP Server Module

Provides MCP (Model Context Protocol) endpoints for Claude Desktop/Code
to interact with the Analytics & Reporting Agent.

Supported MCP Commands:
- track_task_start: Record the start of a task
- track_task_end: Record the completion of a task
- update_jira_task: Update JIRA issue with AI metrics
- generate_agent_report: Generate performance report
- list_analytics: List stored analytics data
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List

from mcp import types
from mcp.server import Server

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analytics_agent import AnalyticsAgent
from tools.jira_client import JiraClient

logger = logging.getLogger("pnd_agents.analytics_mcp")


def get_analytics_tools() -> List[types.Tool]:
    """
    Get the list of analytics MCP tools.
    
    Returns:
        List of MCP Tool definitions
    """
    return [
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
                    },
                    "confidence_score": {
                        "type": "number",
                        "description": "Model confidence score (0-1)",
                        "default": 1.0
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
            name="analytics_update_jira_task",
            description="Update a JIRA issue with AI agent metrics. Adds a formatted comment and updates custom fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "jira_task_id": {
                        "type": "string",
                        "description": "JIRA issue key (e.g., 'EPA-123')"
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent"
                    },
                    "task_name": {
                        "type": "string",
                        "description": "Name/description of the task"
                    },
                    "status": {
                        "type": "string",
                        "description": "Task status (Completed, Failed, In Progress)",
                        "enum": ["Completed", "Failed", "In Progress"]
                    },
                    "duration_ms": {
                        "type": "number",
                        "description": "Duration in milliseconds"
                    },
                    "iterations": {
                        "type": "integer",
                        "description": "Number of iterations"
                    },
                    "errors": {
                        "type": "integer",
                        "description": "Number of errors"
                    },
                    "effectiveness_score": {
                        "type": "number",
                        "description": "Effectiveness score (0-100)"
                    },
                    "requires_human_review": {
                        "type": "boolean",
                        "description": "Whether human review is required"
                    }
                },
                "required": ["jira_task_id", "agent_name", "status"]
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
            description="List stored analytics data with optional filters.",
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
            name="analytics_get_config",
            description="Get current analytics configuration.",
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
                    "jira_comment_enabled": {
                        "type": "boolean",
                        "description": "Enable/disable JIRA comments"
                    },
                    "jira_custom_fields_enabled": {
                        "type": "boolean",
                        "description": "Enable/disable JIRA custom field updates"
                    },
                    "auto_update_jira": {
                        "type": "boolean",
                        "description": "Enable/disable automatic JIRA updates on task completion"
                    },
                    "estimated_time_saved_per_task": {
                        "type": "number",
                        "description": "Estimated hours saved per AI task (for reporting)"
                    }
                }
            }
        ),
    ]


async def handle_analytics_tool(
    name: str,
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handle analytics tool calls.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        List of TextContent with results
    """
    try:
        analytics_agent = AnalyticsAgent()
        
        if name == "analytics_track_task_start":
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
        
        elif name == "analytics_track_task_end":
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
        
        elif name == "analytics_track_task_failure":
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
        
        elif name == "analytics_update_jira_task":
            jira_client = JiraClient()
            
            # Format duration
            duration_ms = arguments.get("duration_ms", 0)
            if duration_ms < 60000:
                duration_str = f"{duration_ms / 1000:.1f}s"
            else:
                minutes = duration_ms / 60000
                seconds = (duration_ms % 60000) / 1000
                duration_str = f"{minutes:.0f}m {seconds:.0f}s"
            
            # Build comment
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
            
            # Add comment to JIRA
            jira_client.add_comment(arguments["jira_task_id"], comment)
            
            # Update custom fields if available
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
        
        elif name == "analytics_generate_report":
            output_format = arguments.get("format", "json")
            days = arguments.get("days", 14)
            
            if output_format == "markdown":
                report = analytics_agent.generate_markdown_report(days=days)
                return [types.TextContent(type="text", text=report)]
            else:
                report = analytics_agent.generate_json_report(days=days)
                return [types.TextContent(type="text", text=json.dumps(report, indent=2))]
        
        elif name == "analytics_list":
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
        
        elif name == "analytics_get_config":
            result = {
                "status": "success",
                "config": analytics_agent.config,
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analytics_update_config":
            # Update config values
            for key, value in arguments.items():
                if key in analytics_agent.config:
                    analytics_agent.config[key] = value
            
            result = {
                "status": "success",
                "message": "Configuration updated",
                "config": analytics_agent.config,
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": f"Unknown tool: {name}"})
            )]
    
    except Exception as e:
        logger.error(f"Error handling analytics tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


def register_analytics_tools(server: Server) -> None:
    """
    Register analytics tools with an MCP server.
    
    This function can be called to add analytics tools to an existing
    MCP server instance.
    
    Args:
        server: The MCP server instance to register tools with
    """
    # Get existing list_tools handler if any
    original_list_tools = None
    original_call_tool = None
    
    # Store references to add to existing handlers
    analytics_tools = get_analytics_tools()
    
    @server.list_tools()
    async def list_tools_with_analytics() -> List[types.Tool]:
        """List all tools including analytics tools."""
        tools = []
        if original_list_tools:
            tools = await original_list_tools()
        tools.extend(analytics_tools)
        return tools
    
    @server.call_tool()
    async def call_tool_with_analytics(
        name: str,
        arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Handle tool calls including analytics tools."""
        # Check if this is an analytics tool
        if name.startswith("analytics_"):
            return await handle_analytics_tool(name, arguments)
        
        # Otherwise, delegate to original handler
        if original_call_tool:
            return await original_call_tool(name, arguments)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": f"Unknown tool: {name}"})
        )]


class AnalyticsMCPServer:
    """
    Standalone MCP server for analytics tools.
    
    Can be run independently or integrated with the main pnd-agents server.
    """
    
    def __init__(self, name: str = "pnd-agents-analytics"):
        """
        Initialize the analytics MCP server.
        
        Args:
            name: Server name for MCP identification
        """
        self.server = Server(name=name)
        self._register_tools()
    
    def _register_tools(self):
        """Register all analytics tools."""
        analytics_tools = get_analytics_tools()
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List all analytics tools."""
            return analytics_tools
        
        @self.server.call_tool()
        async def call_tool(
            name: str,
            arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle analytics tool calls."""
            return await handle_analytics_tool(name, arguments)
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for standalone analytics MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = AnalyticsMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
