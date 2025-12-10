#!/usr/bin/env python3
"""
MCP Usage Example for Analytics Agent

This example demonstrates how to use the Analytics Agent via MCP
(Model Context Protocol) for Claude Desktop/Code integration.
"""

import asyncio
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.analytics_mcp_server import (
    get_analytics_tools,
    handle_analytics_tool,
)


async def example_list_tools():
    """Example: List available analytics MCP tools."""
    print("=" * 60)
    print("Example: List Available MCP Tools")
    print("=" * 60)
    
    tools = get_analytics_tools()
    
    print(f"\nFound {len(tools)} analytics tools:\n")
    for tool in tools:
        print(f"  - {tool.name}")
        print(f"    Description: {tool.description[:60]}...")
        print()


async def example_track_task_start():
    """Example: Track task start via MCP."""
    print("=" * 60)
    print("Example: Track Task Start via MCP")
    print("=" * 60)
    
    result = await handle_analytics_tool(
        "analytics_track_task_start",
        {
            "agent_name": "Frontend Engineer Agent",
            "task_description": "Create ProductCard component from Figma",
            "jira_task_id": "EPA-100",
        }
    )
    
    print("\nMCP Response:")
    print(result[0].text)


async def example_track_task_end():
    """Example: Track task completion via MCP."""
    print("\n" + "=" * 60)
    print("Example: Track Task End via MCP")
    print("=" * 60)
    
    result = await handle_analytics_tool(
        "analytics_track_task_end",
        {
            "agent_name": "Frontend Engineer Agent",
            "jira_task_id": "EPA-100",
            "duration": 180000,
            "iterations": 3,
            "errors": [],
            "effectiveness_score": 95.0,
            "requires_human_review": False,
        }
    )
    
    print("\nMCP Response:")
    print(result[0].text)


async def example_track_failure():
    """Example: Track task failure via MCP."""
    print("\n" + "=" * 60)
    print("Example: Track Task Failure via MCP")
    print("=" * 60)
    
    # First start the task
    await handle_analytics_tool(
        "analytics_track_task_start",
        {
            "agent_name": "Unit Test Agent",
            "task_description": "Generate tests for complex module",
            "jira_task_id": "EPA-101",
        }
    )
    
    # Then track failure
    result = await handle_analytics_tool(
        "analytics_track_task_failure",
        {
            "agent_name": "Unit Test Agent",
            "jira_task_id": "EPA-101",
            "errors": [
                "Unable to parse module structure",
                "Missing type definitions",
            ],
        }
    )
    
    print("\nMCP Response:")
    print(result[0].text)


async def example_generate_report():
    """Example: Generate report via MCP."""
    print("\n" + "=" * 60)
    print("Example: Generate Report via MCP")
    print("=" * 60)
    
    # JSON report
    print("\n1. JSON Report:")
    result = await handle_analytics_tool(
        "analytics_generate_report",
        {
            "days": 7,
            "format": "json",
        }
    )
    
    data = json.loads(result[0].text)
    print(f"   Report type: {data.get('reportType', 'N/A')}")
    print(f"   Generated at: {data.get('generatedAt', 'N/A')}")
    
    # Markdown report
    print("\n2. Markdown Report:")
    result = await handle_analytics_tool(
        "analytics_generate_report",
        {
            "days": 7,
            "format": "markdown",
        }
    )
    
    md_preview = result[0].text[:200]
    print(f"   Preview: {md_preview}...")


async def example_list_analytics():
    """Example: List analytics via MCP."""
    print("\n" + "=" * 60)
    print("Example: List Analytics via MCP")
    print("=" * 60)
    
    result = await handle_analytics_tool(
        "analytics_list",
        {
            "days": 7,
        }
    )
    
    data = json.loads(result[0].text)
    print(f"\nFound {data.get('count', 0)} tasks")
    
    if data.get("tasks"):
        print("\nRecent tasks:")
        for task in data["tasks"][:3]:
            print(f"  - {task.get('agentName', 'Unknown')}: {task.get('taskName', 'N/A')[:40]}...")


async def example_get_config():
    """Example: Get configuration via MCP."""
    print("\n" + "=" * 60)
    print("Example: Get Configuration via MCP")
    print("=" * 60)
    
    result = await handle_analytics_tool(
        "analytics_get_config",
        {}
    )
    
    data = json.loads(result[0].text)
    print("\nCurrent configuration:")
    for key, value in data.get("config", {}).items():
        print(f"  {key}: {value}")


async def example_update_config():
    """Example: Update configuration via MCP."""
    print("\n" + "=" * 60)
    print("Example: Update Configuration via MCP")
    print("=" * 60)
    
    result = await handle_analytics_tool(
        "analytics_update_config",
        {
            "estimated_time_saved_per_task": 2.5,
            "jira_comment_enabled": True,
        }
    )
    
    data = json.loads(result[0].text)
    print(f"\nStatus: {data.get('status')}")
    print(f"Message: {data.get('message')}")


async def main():
    """Run all MCP examples."""
    print("\n" + "#" * 60)
    print("# Analytics Agent - MCP Usage Examples")
    print("#" * 60)
    
    await example_list_tools()
    await example_track_task_start()
    await example_track_task_end()
    await example_track_failure()
    await example_generate_report()
    await example_list_analytics()
    await example_get_config()
    await example_update_config()
    
    print("\n" + "#" * 60)
    print("# MCP Examples Complete!")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
