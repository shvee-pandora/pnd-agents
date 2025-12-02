# Setup Guide

This guide provides detailed instructions for setting up the PG AI Squad agent system.

## Prerequisites

### Required Software

- **Python 3.10+** - For running agent tools
- **Node.js 20+** - For running development commands
- **pnpm** - Package manager for Node.js projects
- **Claude Desktop** - For MCP integration (optional)

### Recommended Tools

- **VS Code** - With Python and TypeScript extensions
- **Git** - For version control

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Amplience Configuration
AMPLIENCE_HUB_NAME=pandoragroup
AMPLIENCE_BASE_URL=https://cdn.content.amplience.net
AMPLIENCE_LOCALE=en
AMPLIENCE_CACHE_TTL=300000

# Figma Configuration (optional)
FIGMA_ACCESS_TOKEN=your-figma-personal-access-token

# Development
NODE_ENV=development
```

### 4. Configure Claude Desktop (Optional)

To use the agents as Claude Desktop plugins:

```bash
# Copy MCP configuration
mkdir -p ~/.config/claude
cp mcp-config/claude.config.json ~/.config/claude/mcp.json

# Edit the configuration to set your workspace folder
# Replace ${workspaceFolder} with the actual path
```

Example `~/.config/claude/mcp.json`:

```json
{
  "mcpServers": {
    "pg-ai-squad": {
      "command": "python",
      "args": ["-m", "pnd_agents.server"],
      "cwd": "/path/to/pnd-agents",
      "env": {
        "PYTHONPATH": "/path/to/pnd-agents",
        "AMPLIENCE_HUB_NAME": "pandoragroup"
      }
    }
  }
}
```

## Configuration

### Agent Configuration

The `mcp-config/agents.config.json` file defines all agents and their capabilities:

```json
{
  "agents": [
    {
      "id": "task-manager",
      "name": "Task Manager Agent",
      "role": "orchestrator",
      "capabilities": ["task-decomposition", "agent-routing"],
      "commands": ["task-decompose", "task-assign", "task-merge"]
    }
  ]
}
```

### Tool Configuration

Each tool can be configured independently:

#### Filesystem Tool

```python
from tools import FilesystemTool

# Restrict operations to a specific directory
fs = FilesystemTool(base_path='/path/to/project')
```

#### Command Runner

```python
from tools import CommandRunner

# Configure working directory and timeout
runner = CommandRunner(
    working_dir='/path/to/project',
    timeout=300,  # 5 minutes
    env={'NODE_ENV': 'development'}
)
```

#### Amplience API

```python
from tools import AmplienceAPI, AmplienceConfig

# Custom configuration
config = AmplienceConfig(
    hub_name='pandoragroup',
    base_url='https://cdn.content.amplience.net',
    locale='en',
    cache_ttl=300000
)
api = AmplienceAPI(config)
```

## Verification

### Test the Installation

```bash
# Test Python tools
python -c "from tools import FilesystemTool; print('Tools loaded successfully')"

# Test command runner
python -c "from tools import CommandRunner; r = CommandRunner(); print(r.run('echo Hello').stdout)"
```

### Test Agent Commands

```bash
# List available agents
cat mcp-config/agents.config.json | jq '.agents[].name'

# View agent commands
cat agents/task_manager/commands/task-decompose.md
```

## Troubleshooting

### Common Issues

#### Python Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/pnd-agents:$PYTHONPATH
```

#### Claude Desktop Not Finding Agents

1. Check that `~/.config/claude/mcp.json` exists
2. Verify the paths in the configuration are absolute
3. Restart Claude Desktop after configuration changes

#### Amplience API Errors

1. Verify `AMPLIENCE_HUB_NAME` is correct
2. Check network connectivity to Amplience CDN
3. For preview mode, ensure VSE parameter is set

### Getting Help

- Check the [Architecture](ARCHITECTURE.md) document for system design
- Review [Examples](examples/) for usage patterns
- Open an issue on GitHub for bugs or feature requests

## Next Steps

1. Read the [Architecture](ARCHITECTURE.md) document
2. Try the [Examples](examples/)
3. Start using agents with Claude Desktop or programmatically
