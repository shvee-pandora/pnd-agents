#!/usr/bin/env python3
"""
PG AI Squad MCP Server

Main entry point for the MCP server. This script handles the case where
Claude Desktop may not respect the cwd setting by using __file__ to
determine the project root and set up sys.path accordingly.
"""

import os
import sys

# Ensure this directory is on sys.path so imports work even if cwd is /
# This is critical because Claude Desktop may ignore the cwd setting
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import asyncio
from mcp.server.stdio import stdio_server
from mcp.server import Server
from tools import register_tools


async def main():
    """Main entry point for the MCP server."""
    # Create a new MCP server
    server = Server(name="pnd-agents")

    # Register all tools
    register_tools(server)

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
