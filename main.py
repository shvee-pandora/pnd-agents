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
