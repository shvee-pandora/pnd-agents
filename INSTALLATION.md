# PND Agents Installation Guide

This guide provides clear, step-by-step instructions for installing and using pnd-agents. Choose the installation method that best fits your needs.

## Prerequisites

Before installing pnd-agents, ensure you have the following:

### Required Software

| Software | Version | Download Link | Purpose |
|----------|---------|---------------|---------|
| **Python** | 3.10 or higher | [python.org/downloads](https://www.python.org/downloads/) | Required runtime |
| **pip** | Latest | Included with Python | Package installer |
| **Git** | Any recent version | [git-scm.com/downloads](https://git-scm.com/downloads) | Clone repository |

### Optional Software (for specific features)

| Software | Download Link | Purpose |
|----------|---------------|---------|
| **Claude Desktop** | [claude.ai/download](https://claude.ai/download) | MCP integration (recommended) |
| **Claude Code** | [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=Anthropic.claude-code) | VS Code integration |
| **Node.js** | [nodejs.org](https://nodejs.org/) | Only if using npx method |

### Verify Prerequisites

Run these commands to verify your setup:

```bash
# Check Python version (must be 3.10+)
python3 --version

# Check pip is available
pip3 --version

# Check Git is available
git --version
```

**macOS Note:** Use `python3` and `pip3` instead of `python` and `pip`.

## Installation Methods

Choose ONE of the following methods:

### Method 1: pip install from GitHub (Recommended for most users)

This is the simplest method - no cloning required:

```bash
# Install directly from GitHub
pip3 install git+https://github.com/shvee-pandora/pnd-agents.git

# Install Playwright browsers (required for Broken Experience Detector)
playwright install

# Verify installation
python3 -m pnd_agents status
```

### Method 2: Clone and Install (Recommended for contributors)

Use this method if you want to modify the code or contribute:

```bash
# Clone the repository
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents

# Install in editable mode
pip3 install -e .

# Install Playwright browsers
playwright install

# Verify installation
python3 -m pnd_agents status
```

### Method 3: requirements.txt (Alternative)

If you prefer using requirements.txt:

```bash
# Clone the repository
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents

# Install dependencies
pip3 install -r requirements.txt

# Install Playwright browsers
playwright install
```

**Note:** This method doesn't install the CLI command. Use `python3 -m pnd_agents` instead of `pnd-agents`.

## Three Ways to Use Agents

### Way 1: With Claude Desktop/Claude Code (Full MCP Integration)

This gives you the full agent experience with Claude as the AI backbone.

**Setup:**
```bash
# After installing pnd-agents, run the setup wizard
pnd-agents setup

# Or use module fallback if CLI not found
python3 -m pnd_agents setup
```

The setup wizard will:
1. Let you choose which agents to enable
2. Configure environment variables (Figma token, etc.)
3. Automatically update your Claude configuration

**After setup:**
1. Restart Claude Desktop/Code
2. Start a conversation
3. Use prompts like: "Using pnd-agents, analyze this task: Create a React component"

**Example prompts:**
```
Using pnd-agents Task Manager, create a React component from this Figma:
https://www.figma.com/design/ABC123/My-Design?node-id=123-456
```

```
Using pnd-agents, write unit tests for src/components/Button.tsx with 100% coverage
```

### Way 2: Command Line Interface (CLI)

Use agents directly from your terminal without Claude:

```bash
# Check installation status
pnd-agents status
# Or: python3 -m pnd_agents status

# Analyze a task (shows plan without executing)
pnd-agents analyze-task "Create a React component for product cards"
# Or: python3 -m pnd_agents analyze-task "Create a React component"

# Run a task through the workflow engine
pnd-agents run-task "Create a React component for product cards"
# Or: python3 -m pnd_agents run-task "Create a React component"

# Run with ticket ID and branch
pnd-agents run-task "Build header component" --ticket INS-2509 --branch feature/header

# Show workflow plan without executing
pnd-agents run-task "Create API endpoint" --plan-only

# View configuration
pnd-agents config --show
```

**Available CLI Commands:**

| Command | Description |
|---------|-------------|
| `pnd-agents status` | Check installation and configuration status |
| `pnd-agents setup` | Run the interactive setup wizard |
| `pnd-agents analyze-task "..."` | Analyze a task and show the workflow plan |
| `pnd-agents run-task "..."` | Execute a task through the workflow engine |
| `pnd-agents config --show` | View current configuration |
| `pnd-agents config --agents` | Reconfigure which agents are enabled |
| `pnd-agents config --env` | Reconfigure environment variables |
| `pnd-agents uninstall` | Remove from Claude config |

### Way 3: Python API (Programmatic Usage)

Import and use agents directly in your Python code:

```python
# Import tools
from tools import FilesystemTool, CommandRunner, FigmaParser, AmplienceAPI, HARAnalyzer

# Use filesystem tool
fs = FilesystemTool()
content = fs.read_file('path/to/file.tsx')

# Run commands
runner = CommandRunner()
result = runner.run_eslint(['src/'])

# Parse Figma designs
parser = FigmaParser()
components = parser.parse_file('design.json')

# Interact with Amplience
api = AmplienceAPI()
content = api.fetch_by_key('homepage-hero')

# Analyze HAR files
analyzer = HARAnalyzer()
report = analyzer.parse_file('performance.har')
```

**Using the Task Manager programmatically:**

```python
from agents.task_manager_agent import TaskManagerAgent

# Create the agent
agent = TaskManagerAgent()

# Analyze a task (without executing)
plan = agent.analyze_task("Create Stories carousel from Figma: https://figma.com/...")
print(f"Detected type: {plan['detected_type']}")
print(f"Pipeline: {plan['pipeline']}")

# Run a task
context = agent.run_task(
    "Create Stories carousel from Figma: https://figma.com/...",
    metadata={"ticket_id": "INS-2509"},
    verbose=True
)

# Check status
print(f"Status: {context.status}")
```

## Environment Variables

### Required for Figma Integration

```bash
export FIGMA_ACCESS_TOKEN="your-figma-token"
```

**How to get a Figma token:**
1. Go to [Figma Settings > Account](https://www.figma.com/settings)
2. Scroll to "Personal access tokens"
3. Click "Generate new token"
4. Copy the token (you won't see it again)

### Optional for Amplience Integration

```bash
export AMPLIENCE_HUB_NAME="pandoragroup"
export AMPLIENCE_BASE_URL="https://cdn.content.amplience.net"
```

### Optional for SonarCloud Integration

```bash
export SONAR_TOKEN="your-sonarcloud-token"
```

**How to get a SonarCloud token:**
1. Go to [SonarCloud Security Settings](https://sonarcloud.io/account/security)
2. Generate a new token with "Analyze Projects" permission

### Setting Environment Variables

**Option A: Using .env file (recommended)**
```bash
# Create .env file in the pnd-agents directory
cat > .env << EOF
FIGMA_ACCESS_TOKEN=your-figma-token
AMPLIENCE_HUB_NAME=pandoragroup
AMPLIENCE_BASE_URL=https://cdn.content.amplience.net
SONAR_TOKEN=your-sonarcloud-token
EOF
```

**Option B: Export in shell**
```bash
# Add to ~/.zshrc or ~/.bashrc
export FIGMA_ACCESS_TOKEN="your-figma-token"
```

**Option C: Using the setup wizard**
```bash
pnd-agents setup
# The wizard will prompt for environment variables
```

## Troubleshooting

### "pnd-agents: command not found"

This is the most common issue. Try these solutions in order:

**Solution 1: Use the module fallback**
```bash
# Instead of: pnd-agents status
python3 -m pnd_agents status
```

**Solution 2: Add Python bin to PATH (macOS)**
```bash
# Add to ~/.zshrc
echo 'export PATH="$HOME/Library/Python/3.12/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Solution 3: Reinstall the package**
```bash
pip3 uninstall pnd-agents -y
pip3 install git+https://github.com/shvee-pandora/pnd-agents.git
```

**Solution 4: Verify installation**
```bash
pip3 show pnd-agents
```

### "ModuleNotFoundError: No module named 'workflow'"

You have an old version. Update:
```bash
pip3 uninstall pnd-agents -y
pip3 install git+https://github.com/shvee-pandora/pnd-agents.git
```

### "ModuleNotFoundError: No module named 'mcp'"

The mcp package is missing. Install it:
```bash
pip3 install mcp>=1.0.0
```

Or reinstall pnd-agents:
```bash
pip3 install git+https://github.com/shvee-pandora/pnd-agents.git
```

### Claude Desktop Not Finding Agents

1. **Check config file location:**
   - macOS: `~/.claude.json` or `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.claude.json`

2. **Verify paths are absolute** (not relative)

3. **Restart Claude Desktop** after configuration changes

4. **Run setup again:**
   ```bash
   pnd-agents setup
   ```

### Figma API Errors

1. Verify your `FIGMA_ACCESS_TOKEN` is valid
2. Check the token has read access to the file
3. Ensure the Figma URL format is correct:
   ```
   https://www.figma.com/design/ABC123/My-Design?node-id=123-456
   ```

## Updating pnd-agents

```bash
# If installed via pip from GitHub
pip3 install --upgrade git+https://github.com/shvee-pandora/pnd-agents.git

# If cloned locally
cd pnd-agents
git pull origin main
pip3 install -e .
```

## Uninstalling

```bash
# Remove from Claude config
pnd-agents uninstall

# Uninstall the package
pip3 uninstall pnd-agents

# Optionally remove the cloned directory
rm -rf /path/to/pnd-agents
```

## Quick Reference

| Task | Command |
|------|---------|
| Install from GitHub | `pip3 install git+https://github.com/shvee-pandora/pnd-agents.git` |
| Check status | `python3 -m pnd_agents status` |
| Setup Claude integration | `python3 -m pnd_agents setup` |
| Analyze a task | `python3 -m pnd_agents analyze-task "your task"` |
| Run a task | `python3 -m pnd_agents run-task "your task"` |
| View config | `python3 -m pnd_agents config --show` |

## Next Steps

1. Run `pnd-agents status` to verify installation
2. Run `pnd-agents setup` to configure Claude integration (optional)
3. Try `pnd-agents analyze-task "Create a React component"` to test
4. Read the [README](README.md) for detailed agent documentation
5. Check [docs/claude-usage.md](docs/claude-usage.md) for Claude-specific usage

## Support

- **Repository:** [github.com/shvee-pandora/pnd-agents](https://github.com/shvee-pandora/pnd-agents)
- **Issues:** [github.com/shvee-pandora/pnd-agents/issues](https://github.com/shvee-pandora/pnd-agents/issues)
