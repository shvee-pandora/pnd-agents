# Setup Guide

This guide provides detailed instructions for setting up the PG AI Squad agent system.

## Prerequisites

### Required Software

- **Python 3.10+** - For running agent tools and the setup CLI
- **Claude Desktop or Claude Code** - For MCP integration

### Recommended Tools

- **VS Code** - With Python and TypeScript extensions
- **Git** - For version control

## Quick Installation (Recommended)

The fastest way to get started is using the setup CLI:

```bash
# Clone the repository
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents

# Install the package
pip install -e .

# Run the setup wizard
pnd-agents setup
```

The setup wizard will guide you through:
1. Selecting which agents to enable
2. Configuring environment variables (Figma token, Amplience settings)
3. Updating your Claude configuration automatically

---

## Three Ways to Set Up PND Agents

### 1. Claude Code Setup

Claude Code uses `~/.claude.json` for MCP server configuration.

**Automatic Setup:**
```bash
pnd-agents setup
```

**Manual Setup:**

Add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "pnd-agents": {
      "command": "python3",
      "args": ["/path/to/pnd-agents/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/pnd-agents",
        "FIGMA_ACCESS_TOKEN": "your-figma-token",
        "SONAR_TOKEN": "your-sonarcloud-token"
      }
    }
  }
}
```

**Verification:**
```bash
# Check status
pnd-agents status

# In Claude Code, ask:
"What pnd-agents tools do you have access to?"
```

### 2. Claude Desktop Setup

Claude Desktop uses a platform-specific config file.

**Config File Locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.claude.json`

**Automatic Setup:**
```bash
pnd-agents setup
```

**Manual Setup:**

Add to your Claude Desktop config file:
```json
{
  "mcpServers": {
    "pnd-agents": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/pnd-agents/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/pnd-agents",
        "FIGMA_ACCESS_TOKEN": "your-figma-token",
        "SONAR_TOKEN": "your-sonarcloud-token"
      }
    }
  }
}
```

**Important:** Restart Claude Desktop after configuration changes.

### 3. Slash Commands Setup

Slash commands work automatically once pnd-agents is installed. They are defined in `.claude/commands/` and available in any repository.

**Available Slash Commands:**

| Command | Description |
|---------|-------------|
| `/tech-debt` | Analyze technical debt in current repository |
| `/tech-debt summary` | Executive summary for leadership |
| `/tech-debt register` | Detailed debt inventory for sprint planning |
| `/figma` | Parse Figma designs and extract component specs |
| `/frontend` | Generate React/Next.js components |
| `/performance` | Analyze HAR files for performance issues |
| `/exec-summary` | Generate executive summaries from sprint data |

**Using Slash Commands:**

In Claude Desktop or Claude Code, simply type the command:
```
/tech-debt
```

Claude will execute the corresponding agent and return results.

---

## Cross-Repository Usage

**Once pnd-agents is installed, it works across ALL repositories on your machine.** You don't need to install it separately for each project.

### How It Works

1. **Install once**: Clone and install pnd-agents in any location
2. **Configure once**: Run `pnd-agents setup` to configure Claude
3. **Use everywhere**: Open any repository in Claude and use pnd-agents tools

### Using Agents in Any Repository

**Via Natural Language:**
```
"Analyze technical debt in this repository"
"Generate unit tests for src/components/Button.tsx"
"Review this code against Pandora standards"
```

**Via Slash Commands:**
```
/tech-debt              # Works in any repo
/tech-debt summary      # Works in any repo
```

**Via Python API (from any directory):**
```python
from agents.technical_debt_agent import analyze_technical_debt

# Analyze the current repository
report = analyze_technical_debt(".")

# Analyze a different repository
report = analyze_technical_debt("/path/to/other/repo")
```

### Repository-Specific Configuration

For repository-specific settings, create `.claude/repo-profile.json` in your project:

```json
{
  "identity": {
    "name": "my-project",
    "type": "next-js-app"
  },
  "commands": {
    "test": "pnpm test",
    "lint": "pnpm lint"
  },
  "paths": {
    "components": "src/components",
    "tests": "src/__tests__"
  }
}
```

Agents will automatically use these settings when analyzing your repository.

---

## Installing New Agents (For Team Members)

When new agents are added to pnd-agents, team members need to update their installation.

### Updating to Get New Agents

```bash
# Navigate to your pnd-agents installation
cd /path/to/pnd-agents

# Pull the latest changes
git pull origin main

# Reinstall the package
pip install -e .

# Re-run setup to configure new agents
pnd-agents setup
```

### Quick Update (If No New Configuration Needed)

```bash
cd /path/to/pnd-agents
git pull origin main
pip install -e .

# Restart Claude Desktop/Code
```

### Verifying New Agents Are Available

```bash
# Check installation status
pnd-agents status

# In Claude, ask:
"What pnd-agents tools do you have access to?"
```

### Team Notification Process

When a new agent is added:
1. The PR description will list new capabilities
2. Team members should run `git pull && pip install -e .`
3. Run `pnd-agents setup` if the agent requires new environment variables
4. Restart Claude Desktop/Code

---

## Installation Options

### Interactive Setup (Default)

```bash
pnd-agents setup
```

This launches an interactive wizard that lets you:
- Choose agents individually with Y/n prompts
- Enter environment variables securely
- Review and confirm the Claude config update

### Preset Configurations

For faster setup, use presets:

```bash
# Default - Recommended agents for most workflows
pnd-agents setup --preset default

# Full - Enable all agents
pnd-agents setup --preset full

# Minimal - Only essential agents (Task Manager, Frontend, Code Review)
pnd-agents setup --preset minimal
```

### Non-Interactive Setup

For CI/CD or scripted installations:

```bash
# Auto-write config without prompts
pnd-agents setup --auto --preset default

# Skip environment variable prompts
pnd-agents setup --skip-env --preset default
```

## Agent Selection

The setup wizard lets you choose which agents to enable:

| Agent | Default | Description |
|-------|---------|-------------|
| Task Manager | Yes | Orchestrates tasks, routes to other agents |
| Frontend Engineer | Yes | React/Next.js components, Storybook |
| Figma Reader | Yes | Extracts design metadata from Figma API |
| Code Review | Yes | Validates code against standards |
| QA | Yes | Generates E2E and integration tests |
| **Unit Test** | Yes | Generates unit tests with **100% coverage** target |
| **Sonar Validation** | Yes | Validates against SonarCloud quality gates |
| **Technical Debt** | Yes | Analyzes repositories for technical debt (READ-ONLY) |
| Amplience CMS | No | Content types, JSON schemas |
| Amplience Placement | No | Maps Figma designs to Amplience CMS modules (HITL) |
| Performance | No | HAR analysis, Core Web Vitals |
| Backend | No | API routes, Server Components |
| Commerce | No | Product search, cart operations via SFCC |
| PRD to Jira | No | Converts PRDs to Jira epics and stories |
| Exec Summary | No | Generates executive summaries from sprint data |
| Roadmap Review | No | Reviews roadmaps and OKRs for risks |
| PR Review | No | Reviews Azure DevOps PRs |
| Sprint AI Report | No | Generates AI contribution reports |

### Changing Agent Selection Later

```bash
# Reconfigure which agents are enabled
pnd-agents config --agents

# View current configuration
pnd-agents config --show
```

## Environment Variables

### Required for Figma Integration

```bash
FIGMA_ACCESS_TOKEN=your-figma-personal-access-token
```

To get a Figma token:
1. Go to Figma Settings > Account
2. Scroll to "Personal access tokens"
3. Generate a new token with read access

### Required for Amplience Integration

```bash
AMPLIENCE_HUB_NAME=pandoragroup
AMPLIENCE_BASE_URL=https://cdn.content.amplience.net
```

### Optional for SonarCloud Integration

```bash
SONAR_TOKEN=your-sonarcloud-token
```

To get a SonarCloud token:
1. Go to https://sonarcloud.io/account/security
2. Generate a new token with "Analyze Projects" permission
3. The Sonar Validation Agent will use this to fetch issues, coverage, and quality gate status

Note: The Sonar Validation Agent can work without a token for basic validation, but API access enables fetching real-time data from https://sonarcloud.io/summary/new_code?id=pandora-jewelry_spark_pandora-group&branch=master

### Configuring Environment Variables

The setup wizard will prompt for these values. You can also:

```bash
# Update environment variables later
pnd-agents config --env

# Or create a .env file manually
cat > .env << EOF
FIGMA_ACCESS_TOKEN=your-token
AMPLIENCE_HUB_NAME=pandoragroup
AMPLIENCE_BASE_URL=https://cdn.content.amplience.net
EOF
```

## Manual Configuration (Alternative)

If you prefer manual setup instead of the CLI:

### 1. Clone and Install

```bash
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents
pip install -e .
```

### 2. Create .env File

```bash
cat > .env << EOF
FIGMA_ACCESS_TOKEN=your-figma-token
AMPLIENCE_HUB_NAME=pandoragroup
AMPLIENCE_BASE_URL=https://cdn.content.amplience.net
EOF
```

### 3. Update Claude Config

Add to `~/.claude.json` (Claude Code) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Claude Desktop on macOS):

```json
{
  "mcpServers": {
    "pnd-agents": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/pnd-agents/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/pnd-agents",
        "FIGMA_ACCESS_TOKEN": "your-figma-token",
        "AMPLIENCE_HUB_NAME": "pandoragroup",
        "AMPLIENCE_BASE_URL": "https://cdn.content.amplience.net"
      }
    }
  }
}
```

## Verification

### Check Installation Status

```bash
pnd-agents status
```

This shows:
- Installation path
- Whether main.py exists
- Agent configuration status
- Claude config status

### Test the MCP Server

```bash
# Start the server manually to check for errors
python main.py
```

The server should start without errors and wait for MCP client connections.

### Test in Claude

1. Restart Claude Desktop/Code after setup
2. Start a new conversation
3. The pnd-agents tools should be available
4. Try: "List the available pnd-agents tools"

## CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `pnd-agents setup` | Run the setup wizard |
| `pnd-agents config --agents` | Reconfigure agent selection |
| `pnd-agents config --env` | Reconfigure environment variables |
| `pnd-agents config --show` | Show current configuration |
| `pnd-agents status` | Show installation status |
| `pnd-agents uninstall` | Remove from Claude config |

### Setup Options

| Option | Description |
|--------|-------------|
| `--preset default` | Use default agent selection |
| `--preset full` | Enable all agents |
| `--preset minimal` | Enable only essential agents |
| `--skip-env` | Skip environment variable prompts |
| `--auto` | Auto-write config without prompts |

## Troubleshooting

### Common Issues

#### "pnd-agents: command not found"

This usually means the CLI wasn't installed in the Python environment you're using. Here are several solutions:

**Solution 1: Install the package properly**
```bash
cd /path/to/pnd-agents
pip install -e .
```

**Solution 2: Use the module fallback**
```bash
# Instead of: pnd-agents setup
# Use: python -m pnd_agents setup
python -m pnd_agents setup
python -m pnd_agents status
python -m pnd_agents config --show
```

**Solution 3: Check Python environment (for Claude Code users)**

Claude Code may use a different Python than your terminal. Check your Claude config to see which Python it uses, then install with that specific Python:
```bash
# Example: if Claude uses /usr/local/bin/python3
/usr/local/bin/python3 -m pip install -e /path/to/pnd-agents
```

**Solution 4: Verify PATH includes pip scripts directory**
```bash
# Find where pip installs scripts
python -m site --user-base
# Add the bin directory to your PATH if needed
export PATH="$(python -m site --user-base)/bin:$PATH"
```

**Verification:**
```bash
# Check if package is installed
pip show pnd-agents

# Test the CLI
pnd-agents --help
# Or fallback:
python -m pnd_agents --help
```

#### Claude Desktop Not Finding Agents

1. Check that the config file exists:
   - macOS: `~/.claude.json` or `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.claude.json`

2. Verify paths are absolute (not relative)

3. Restart Claude Desktop after configuration changes

#### Figma API Errors

1. Verify your `FIGMA_ACCESS_TOKEN` is valid
2. Check the token has read access to the file
3. Ensure the Figma URL format is correct

#### Python Import Errors

```bash
# Ensure PYTHONPATH includes the project
export PYTHONPATH=/path/to/pnd-agents:$PYTHONPATH
```

### Getting Help

```bash
# View CLI help
pnd-agents --help
pnd-agents setup --help

# Check status
pnd-agents status
```

## Updating

To update pnd-agents:

```bash
cd pnd-agents
git pull origin main
pip install -e .

# Re-run setup if there are new agents or config changes
pnd-agents setup
```

## Uninstalling

```bash
# Remove from Claude config
pnd-agents uninstall

# Optionally remove the directory
rm -rf /path/to/pnd-agents
```

## Next Steps

1. Read the [Architecture](ARCHITECTURE.md) document
2. Try the [Examples](examples/)
3. Start using agents with Claude Desktop or Claude Code

### Example Workflows

**Create a component from Figma:**
```
Create a Stories carousel component from this Figma design:
https://www.figma.com/design/ABC123/My-Design?node-id=123-456
```

**Review code against standards:**
```
Review the code in src/components/Header for Pandora coding standards
```

**Generate unit tests with 100% coverage:**
```
Write unit tests for the Button component with 100% coverage
```

**Validate code against SonarCloud before PR:**
```
Validate my code against SonarCloud quality gates before I create a PR
```

**Full workflow with Unit Test and Sonar:**
```
Create a Stories carousel from Figma, write unit tests with 100% coverage, and validate against SonarCloud
```

## Team Setup Guide

This section provides step-by-step instructions for setting up pnd-agents for your team.

### Step 1: Clone the Repository

```bash
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents
```

### Step 2: Install Dependencies

```bash
pip install -e .
```

### Step 3: Run Setup Wizard

```bash
pnd-agents setup
```

The wizard will prompt you to:
1. Select which agents to enable (Unit Test and Sonar Validation are enabled by default)
2. Enter your Figma access token
3. Optionally enter your SonarCloud token for API access

### Step 4: Restart Claude

After setup completes, restart Claude Desktop or Claude Code to load the new configuration.

### Step 5: Verify Installation

```bash
pnd-agents status
```

In Claude, ask: "What pnd-agents tools do you have access to?"

### Team Environment Variables

For team-wide setup, create a shared `.env.example` file:

```bash
# Required for Figma integration
FIGMA_ACCESS_TOKEN=your-figma-token

# Optional for Amplience CMS
AMPLIENCE_HUB_NAME=pandoragroup
AMPLIENCE_BASE_URL=https://cdn.content.amplience.net

# Optional for SonarCloud API access
SONAR_TOKEN=your-sonarcloud-token
```

Each team member should copy this to `.env` and fill in their own tokens.

### Workflow Pipelines

The Task Manager automatically orchestrates agents based on task type:

| Task Type | Pipeline |
|-----------|----------|
| Figma | Figma Reader → Frontend → Code Review → Unit Test → Sonar → Performance |
| Frontend | Frontend → Code Review → Unit Test → Sonar → Performance |
| Backend | Backend → Code Review → Unit Test → Sonar |
| Unit Test | Unit Test → Sonar |
| Sonar | Sonar → Code Review |
| Technical Debt | Technical Debt (standalone, READ-ONLY analysis) |

### Quality Gates

The Sonar Validation Agent enforces these quality gates:
- **0 errors** - No bugs or vulnerabilities
- **0 duplication** - No duplicated code blocks
- **100% coverage** - All code paths tested

When issues are found, the agent generates fix plans with step-by-step instructions.
