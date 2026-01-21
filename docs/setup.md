# Setup Guide

This guide provides detailed instructions for setting up the **Pandora AI Squad** agent system.

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

## Three Usage Modes

Pandora AI Squad agents can be used in three different ways, each with different capabilities and requirements. This section provides detailed information about each mode to help you choose the right approach.

### Usage Mode Comparison

| Feature | MCP Mode (Claude) | Python API Mode | CLI Mode |
|---------|-------------------|-----------------|----------|
| **Natural language interaction** | Yes | No | No |
| **Slash commands** | Yes | No | No |
| **Multi-agent orchestration** | Yes | Manual | No |
| **CI/CD integration** | No | Yes | Yes |
| **Batch processing** | No | Yes | Limited |
| **Requires Claude Desktop/Code** | Yes | No | No |
| **Programmatic access** | No | Yes | Limited |

### Agent Availability by Mode

Not all agents support all usage modes. The table below shows which agents can be used in each mode:

| Agent | MCP Mode | Python API | CLI | Implementation Type |
|-------|----------|------------|-----|---------------------|
| **Task Manager** | Yes | Yes | No | Python module |
| **Frontend Engineer** | Yes | No | No | Markdown (slash commands) |
| **Backend** | Yes | No | No | Markdown (slash commands) |
| **Figma Reader** | Yes | Yes | No | Python module |
| **Code Review** | Yes | No | No | Markdown (slash commands) |
| **Unit Test** | Yes | Yes | No | Python module |
| **Sonar Validation** | Yes | Yes | No | Python module |
| **QA** | Yes | Yes | No | Python module |
| **PR Review** | Yes | Yes | No | Python module |
| **Technical Debt** | Yes | Yes | Yes | Python module |
| **Performance** | Yes | No | No | Markdown (slash commands) |
| **Broken Experience Detector** | Yes | Yes | No | Python module |
| **PRD to Jira** | Yes | Yes | No | Python module |
| **Exec Summary** | Yes | Yes | No | Python module |
| **Roadmap Review** | Yes | Yes | No | Python module |
| **Analytics** | Yes | Yes | Yes | Python module |
| **Commerce** | Yes | Yes | No | Python module |
| **Amplience CMS** | Yes | No | No | Markdown (slash commands) |
| **Amplience Placement** | Yes | Yes | No | Python module |

**Legend:**
- **Python module**: Has `agent.py` with classes and functions that can be imported directly
- **Markdown (slash commands)**: Defined as markdown files in `agents/` and `commands/` directories, only works through MCP

---

### Mode 1: MCP Mode (Claude Desktop/Code)

This is the **recommended mode** for interactive use. Agents run as MCP (Model Context Protocol) servers that Claude Desktop or Claude Code connects to.

**How it works:**
1. The `main.py` file starts an MCP server that exposes agent tools
2. Claude Desktop/Code connects to this server via the configuration in `claude_desktop_config.json` or `~/.claude.json`
3. When you ask Claude to perform a task, it calls the appropriate MCP tool
4. The tool executes the agent logic and returns results to Claude
5. Claude presents the results in natural language

**Technical details:**
- MCP uses JSON-RPC 2.0 over stdio for communication
- Tools are registered in `src/tools/registry.py`
- Each tool maps to an agent function or workflow
- Environment variables are passed from the Claude config to the MCP server process

**Capabilities:**
- All 20 agents available
- Natural language interaction ("Analyze technical debt in this repo")
- Slash commands (`/tech-debt`, `/frontend`, `/figma`)
- Multi-agent workflows via Task Manager
- Context-aware (knows your current working directory)
- Follow-up questions and iterative refinement

**Limitations:**
- Requires Claude Desktop or Claude Code
- Cannot be automated in CI/CD pipelines
- No batch processing
- Single-threaded interaction

**Best for:**
- Interactive development workflows
- Ad-hoc analysis and code generation
- Learning and exploring agent capabilities
- Tasks requiring human judgment and iteration

---

### Mode 2: Python API Mode

For programmatic access, you can import agent classes directly into your Python code. This mode is ideal for automation, CI/CD integration, and custom tooling.

**How it works:**
1. Import the agent class from the appropriate module
2. Instantiate the agent with any required configuration (tokens, paths)
3. Call agent methods to perform analysis or generation
4. Process the returned results (dict, dataclass, or markdown)

**Technical details:**
- Agent classes are located in `src/agents/<agent_name>/agent.py`
- Most agents follow a similar pattern: `__init__()`, `analyze()`, `run()`
- Results are typically returned as dataclasses with `to_dict()` and `to_markdown()` methods
- Environment variables are read automatically if not passed explicitly

**Available agents with Python API:**

```python
# Technical Debt Agent
from agents.technical_debt_agent.agent import TechnicalDebtAgent, analyze_technical_debt

agent = TechnicalDebtAgent(token="optional-sonar-token")
report = agent.analyze("/path/to/repo")
print(report.to_markdown())

# Or use the convenience function
report = analyze_technical_debt("/path/to/repo")
```

```python
# Analytics Agent
from agents.analytics_agent.agent import AnalyticsAgent

agent = AnalyticsAgent(log_dir="/path/to/logs")
agent.on_task_started("frontend-engineer", "Create Button component", jira_task_id="PROJ-123")
# ... task executes ...
agent.on_task_completed("frontend-engineer", jira_task_id="PROJ-123", metrics={"duration": 5000})
report = agent.generate_sprint_report("Sprint 42", "2026-01-01", "2026-01-14")
```

```python
# Sonar Validation Agent
from agents.sonar_validation_agent.agent import SonarValidationAgent

agent = SonarValidationAgent(token="your-token", project_key="your-project")
status = agent.fetch_quality_gate_status()
issues = agent.fetch_issues(severities=["BLOCKER", "CRITICAL"])
result = agent.validate()
```

```python
# Unit Test Agent
from agents.unit_test_agent.agent import UnitTestAgent

agent = UnitTestAgent()
analysis = agent.analyze_file("/path/to/component.tsx")
tests = agent.generate_tests("/path/to/component.tsx", framework="jest", coverage_target=100)
```

```python
# QA Agent
from agents.qa_agent.agent import QAAgent

agent = QAAgent()
result = agent.validate(
    implementation_path="/path/to/component.tsx",
    acceptance_criteria="Given... When... Then..."
)
```

```python
# Figma Reader Agent
from agents.figma_reader_agent.agent import FigmaReaderAgent

agent = FigmaReaderAgent(token="your-figma-token")
metadata = agent.extract_component("https://www.figma.com/design/ABC123/Design?node-id=123-456")
```

```python
# PR Review Agent
from agents.pr_review_agent.agent import PRReviewAgent

agent = PRReviewAgent(pat="your-azure-devops-pat", organization="your-org", project="your-project")
review = agent.review_pr(pr_id=12345)
```

```python
# PM Agents (PRD to Jira, Exec Summary, Roadmap Review)
from agents.pm_agent_pack.prd_to_jira_agent import PRDToJiraAgent
from agents.pm_agent_pack.exec_summary_agent import ExecSummaryAgent
from agents.pm_agent_pack.roadmap_review_agent import RoadmapReviewAgent

prd_agent = PRDToJiraAgent()
summary_agent = ExecSummaryAgent()
roadmap_agent = RoadmapReviewAgent()
```

```python
# Broken Experience Detector Agent
from agents.broken_experience_detector_agent.agent import BrokenExperienceDetectorAgent

agent = BrokenExperienceDetectorAgent()
results = agent.scan_urls(["https://example.com/page1", "https://example.com/page2"])
```

```python
# Commerce Agent (Pandora-specific)
from agents.commerce_agent.agent import CommerceAgent

agent = CommerceAgent()
# Pandora e-commerce operations
```

```python
# Amplience Placement Agent (Pandora-specific)
from agents.amplience_placement_agent.agent import AmpliencePlacementAgent

agent = AmpliencePlacementAgent()
# Amplience module mapping operations
```

**Capabilities:**
- 14 agents with full Python API support
- Programmatic access for automation
- CI/CD pipeline integration
- Batch processing multiple files/repos
- Custom error handling and retry logic
- Integration with other Python tools

**Limitations:**
- No natural language interaction
- No slash commands
- Manual orchestration required for multi-agent workflows
- Must handle environment setup manually

**Best for:**
- CI/CD pipelines (GitHub Actions, Azure Pipelines)
- Automated code quality checks
- Batch analysis of multiple repositories
- Custom tooling and integrations
- Scheduled reports and monitoring

---

### Mode 3: CLI Mode

Some agents provide command-line interfaces for quick operations without writing Python code.

**How it works:**
1. Run the pnd-agents CLI command with appropriate arguments
2. The CLI parses arguments and calls the underlying agent
3. Results are printed to stdout or saved to files

**Available CLI commands:**

```bash
# Installation and configuration
pnd-agents setup              # Run setup wizard
pnd-agents status             # Check installation status
pnd-agents config --show      # View current configuration
pnd-agents config --agents    # Reconfigure agents
pnd-agents config --env       # Reconfigure environment variables
pnd-agents uninstall          # Remove from Claude config

# Analysis commands
pnd-agents scan               # Scan current directory for issues
pnd-agents scan --path /repo  # Scan specific directory

# Task execution (experimental)
pnd-agents run-task "description"    # Run a task
pnd-agents analyze-task "description" # Analyze without executing

# Reporting
pnd-agents sprint-report --sprint "Sprint 42" --start "2026-01-01" --end "2026-01-14"
```

**Direct module execution:**

```bash
# Technical Debt Agent
python -m agents.technical_debt_agent.agent analyze /path/to/repo
python -m agents.technical_debt_agent.agent summary /path/to/repo
python -m agents.technical_debt_agent.agent register /path/to/repo

# Analytics Agent
python -m agents.analytics_agent.agent track-start frontend-engineer "Create component"
python -m agents.analytics_agent.agent track-end frontend-engineer
python -m agents.analytics_agent.agent report --days 7
python -m agents.analytics_agent.agent list
```

**Capabilities:**
- Quick operations without writing code
- Scriptable for shell automation
- Works in any terminal

**Limitations:**
- Limited to 2-3 agents with CLI support
- Less flexible than Python API
- No interactive features
- Limited output formatting options

**Best for:**
- Quick one-off analysis
- Shell scripts and automation
- Developers who prefer CLI over Python
- Simple CI/CD integration

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

The setup wizard uses **pack-based selection** for easier configuration. Instead of selecting individual agents, you choose from 5 agent packs:

### Agent Packs

| Pack | Agents Included | Description |
|------|-----------------|-------------|
| **Core Pack** | Task Manager | Essential orchestration (1 agent) |
| **Developer Pack** | Frontend, Backend, Figma Reader, Unit Test, Code Review, QA, PR Review | Development workflow (7 agents) |
| **Quality & Security Pack** | Sonar Validation, Technical Debt, Snyk, Performance, Broken Experience Detector | Quality assurance (5 agents) |
| **Product Management Pack** | PRD to Jira, Exec Summary, Roadmap Review, Analytics | PM tools (4 agents) |
| **Pandora Platform Pack** | Commerce, Amplience CMS, Amplience Placement | Pandora-specific integrations (3 agents) |

### Preset Configurations

```bash
# Minimal - Core Pack only (1 agent)
pnd-agents setup --preset minimal

# Default - Core + Developer Packs (8 agents)
pnd-agents setup --preset default

# Full - All 20 agents
pnd-agents setup --preset full
```

### Changing Agent Selection Later

```bash
# Reconfigure which agents are enabled
pnd-agents config --agents

# View current configuration
pnd-agents config --show
```

## Environment Variables

### Figma Integration

```bash
FIGMA_ACCESS_TOKEN=your-figma-personal-access-token
```

To get a Figma token:
1. Go to Figma Settings > Account
2. Scroll to "Personal access tokens"
3. Generate a new token with read access

### Amplience Integration

```bash
AMPLIENCE_HUB_NAME=pandoragroup
AMPLIENCE_BASE_URL=https://cdn.content.amplience.net
```

### SonarCloud Integration

```bash
SONAR_TOKEN=your-sonarcloud-token
```

To get a SonarCloud token:
1. Go to https://sonarcloud.io/account/security
2. Generate a new token with "Analyze Projects" permission
3. The Sonar Validation Agent will use this to fetch issues, coverage, and quality gate status

### JIRA Integration

```bash
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_CLOUD_ID=your-jira-cloud-id
```

To get a JIRA API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create a new API token
3. Use your Atlassian email and the token for authentication

### Azure DevOps Integration

```bash
AZURE_DEVOPS_PAT=your-azure-devops-pat
AZURE_DEVOPS_ORG=your-organization
AZURE_DEVOPS_PROJECT=your-project
```

To get an Azure DevOps PAT:
1. Go to Azure DevOps > User Settings > Personal Access Tokens
2. Create a new token with appropriate scopes (Code Read, Work Items Read/Write)

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
