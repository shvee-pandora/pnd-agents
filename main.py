from mcp.server import Server
from tools import register_tools

# Create a new MCP server
server = Server(name="pnd-agents")

# Register all tools that Devin created
register_tools(server)

if __name__ == "__main__":
    server.run()
