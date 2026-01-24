# Frequently Asked Questions (FAQ)

This document answers common questions about installing and using the Pandora AI Squad agent system.

## Table of Contents

1. [Configuration File Locations](#configuration-file-locations)
2. [Using Agents in Other Repositories](#using-agents-in-other-repositories)
3. [Global Token Configuration](#global-token-configuration)
4. [Using Agents Without MCP](#using-agents-without-mcp)
5. [Troubleshooting](#troubleshooting)

---

## Configuration File Locations

### Where is the Claude configuration file?

The location depends on which Claude product you're using and your operating system:

#### Claude Code (Terminal/IDE)

| OS | Config File Location |
|----|---------------------|
| macOS | `~/.claude.json` |
| Linux | `~/.claude.json` |
| Windows | `%USERPROFILE%\.claude.json` |

#### Claude Desktop (GUI Application)

| OS | Config File Location |
|----|---------------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` or `~/.claude.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

### How do I find the config file?

**macOS (Claude Desktop):**
```bash
# Open in Finder
open ~/Library/Application\ Support/Claude/

# Or view the file directly
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**macOS (Claude Code):**
```bash
cat ~/.claude.json
```

**Windows (Claude Desktop):**
```powershell
# Open in Explorer
explorer %APPDATA%\Claude

# Or view the file
type %APPDATA%\Claude\claude_desktop_config.json
```

**Windows (Claude Code):**
```powershell
type %USERPROFILE%\.claude.json
```

**Linux:**
```bash
# Claude Code
cat ~/.claude.json

# Claude Desktop (if using XDG config)
cat ~/.config/Claude/claude_desktop_config.json
```

### What should the config file look like?

A properly configured file should look like this:

```json
{
  "mcpServers": {
    "pnd-agents": {
      "command": "python3",
      "args": ["/path/to/pnd-agents/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/pnd-agents",
        "FIGMA_ACCESS_TOKEN": "your-figma-token",
        "SONAR_TOKEN": "your-sonarcloud-token",
        "JIRA_BASE_URL": "https://your-org.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-jira-api-token"
      }
    }
  }
}
```

**Important Notes:**
- Use **absolute paths** (not relative paths like `./main.py`)
- On Windows, use forward slashes or escaped backslashes: `C:/Users/name/pnd-agents/main.py`
- Restart Claude after making changes to the config file

---

## Using Agents in Other Repositories

### Do I need to install pnd-agents in every repository?

**No!** Once pnd-agents is installed and configured, it works across ALL repositories on your machine. You install it once and use it everywhere.

### How does cross-repository usage work?

1. **Install once**: Clone pnd-agents to any location on your machine
2. **Configure once**: Run `pnd-agents setup` to configure Claude
3. **Use everywhere**: Open any repository in Claude and the agents are available

The agents work by analyzing whatever repository you have open in Claude, not the pnd-agents repository itself.

### Example: Using agents in a different project

```
# You have pnd-agents installed at /home/user/tools/pnd-agents
# You're working on a project at /home/user/projects/my-app

# In Claude, open /home/user/projects/my-app
# Then ask:
"Analyze technical debt in this repository"
"Generate unit tests for src/components/Button.tsx"
"Review this code against Pandora standards"
```

The agents will analyze `my-app`, not `pnd-agents`.

### Can I use slash commands in any repository?

Yes! Slash commands work in any repository once pnd-agents is installed:

```
/tech-debt              # Analyzes the current repository
/tech-debt summary      # Executive summary for current repo
/frontend               # Generate components in current repo
/performance            # Analyze HAR files in current repo
```

### Repository-specific configuration

For repository-specific settings, create a `.claude/repo-profile.json` file in your project:

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

## Global Token Configuration

### How do I set tokens globally so I don't have to enter them every time?

There are three ways to configure tokens globally:

### Method 1: Environment Variables (Recommended)

Add tokens to your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.profile`):

```bash
# Add to ~/.bashrc or ~/.zshrc
export FIGMA_ACCESS_TOKEN="your-figma-token"
export SONAR_TOKEN="your-sonarcloud-token"
export JIRA_BASE_URL="https://your-org.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-jira-api-token"
export JIRA_CLOUD_ID="your-jira-cloud-id"
export AZURE_DEVOPS_PAT="your-azure-devops-pat"
export AZURE_DEVOPS_ORG="your-organization"
export AZURE_DEVOPS_PROJECT="your-project"
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Method 2: Claude Config File

Add tokens directly to your Claude configuration file:

```json
{
  "mcpServers": {
    "pnd-agents": {
      "command": "python3",
      "args": ["/path/to/pnd-agents/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/pnd-agents",
        "FIGMA_ACCESS_TOKEN": "your-figma-token",
        "SONAR_TOKEN": "your-sonarcloud-token",
        "JIRA_BASE_URL": "https://your-org.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-jira-api-token",
        "JIRA_CLOUD_ID": "your-jira-cloud-id",
        "AZURE_DEVOPS_PAT": "your-azure-devops-pat",
        "AZURE_DEVOPS_ORG": "your-organization",
        "AZURE_DEVOPS_PROJECT": "your-project"
      }
    }
  }
}
```

### Method 3: .env File in pnd-agents Directory

Create a `.env` file in your pnd-agents installation:

```bash
cd /path/to/pnd-agents
cat > .env << EOF
FIGMA_ACCESS_TOKEN=your-figma-token
SONAR_TOKEN=your-sonarcloud-token
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_CLOUD_ID=your-jira-cloud-id
AZURE_DEVOPS_PAT=your-azure-devops-pat
AZURE_DEVOPS_ORG=your-organization
AZURE_DEVOPS_PROJECT=your-project
EOF
```

### Which tokens are needed for which agents?

| Token | Required For | How to Get |
|-------|--------------|------------|
| `FIGMA_ACCESS_TOKEN` | Figma Reader Agent | Figma Settings > Account > Personal access tokens |
| `SONAR_TOKEN` | Sonar Validation Agent | https://sonarcloud.io/account/security |
| `JIRA_*` tokens | PRD to Jira, Analytics | https://id.atlassian.com/manage-profile/security/api-tokens |
| `AZURE_DEVOPS_*` | PR Review Agent | Azure DevOps > User Settings > Personal Access Tokens |
| `AMPLIENCE_*` | Amplience CMS Agent | Provided by Pandora Amplience admin |

### Verifying tokens are configured

```bash
# Check if environment variables are set
echo $FIGMA_ACCESS_TOKEN
echo $SONAR_TOKEN
echo $JIRA_API_TOKEN

# Or use the CLI
pnd-agents config --show
```

---

## Using Agents Without MCP

### Can I use pnd-agents without Claude Desktop or MCP?

**Yes!** There are several ways to use the agents without MCP:

### Method 1: Python API (Direct Import)

You can import and use agents directly in Python scripts:

```python
# Technical Debt Analysis
from agents.technical_debt_agent import analyze_technical_debt

report = analyze_technical_debt("/path/to/your/repo")
print(report)

# Unit Test Generation
from agents.unit_test_agent import generate_tests

tests = generate_tests("/path/to/your/repo/src/components/Button.tsx")
print(tests)

# Analytics
from agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent()
agent.on_task_started("task-123", "frontend", {"description": "Create component"})
# ... later
agent.on_task_completed("task-123", {"files_created": 3})
```

### Method 2: CLI Commands

Some agents have CLI interfaces:

```bash
# Check installation status
pnd-agents status

# Run setup wizard
pnd-agents setup

# View configuration
pnd-agents config --show

# Run a task (if supported)
pnd-agents run-task "Analyze technical debt"
```

### Method 3: Direct Script Execution

Run agent scripts directly:

```bash
# Run the MCP server (for debugging)
python main.py

# Run specific agent modules
python -m agents.technical_debt_agent analyze /path/to/repo
python -m agents.analytics_agent report
```

### Method 4: HTTP API (Advanced)

For integration with other tools, you can wrap agents in a simple HTTP server:

```python
from flask import Flask, request, jsonify
from agents.technical_debt_agent import analyze_technical_debt

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    repo_path = request.json.get('repo_path', '.')
    report = analyze_technical_debt(repo_path)
    return jsonify(report)

if __name__ == '__main__':
    app.run(port=5000)
```

### Limitations Without MCP

When using agents without MCP, you lose:
- Natural language interaction with Claude
- Automatic context from your current working directory
- Slash command support
- Multi-agent orchestration via Task Manager

However, you gain:
- Programmatic access for automation
- Integration with CI/CD pipelines
- Custom workflows and scripting
- Batch processing capabilities

---

## Troubleshooting

### "pnd-agents: command not found"

**Solution 1: Install the package**
```bash
cd /path/to/pnd-agents
pip install -e .
```

**Solution 2: Use Python module syntax**
```bash
python -m pnd_agents setup
python -m pnd_agents status
```

**Solution 3: Check PATH**
```bash
# Find where pip installs scripts
python -m site --user-base
# Add to PATH
export PATH="$(python -m site --user-base)/bin:$PATH"
```

### Claude doesn't see the agents after setup

1. **Restart Claude** - Always restart after config changes
2. **Check config file location** - Make sure you edited the correct file
3. **Verify paths are absolute** - Use full paths, not relative
4. **Check for JSON syntax errors** - Use a JSON validator

```bash
# Validate JSON syntax
python -c "import json; json.load(open('~/.claude.json'))"
```

### Tokens not working

1. **Verify token is set**:
   ```bash
   echo $FIGMA_ACCESS_TOKEN
   ```

2. **Check token in Claude config**:
   ```bash
   cat ~/.claude.json | grep FIGMA
   ```

3. **Test token directly**:
   ```bash
   # Test Figma token
   curl -H "X-Figma-Token: $FIGMA_ACCESS_TOKEN" \
     "https://api.figma.com/v1/me"
   ```

### Agents work in one repo but not another

1. **Check repo-profile.json** - Repository-specific settings might override defaults
2. **Verify file permissions** - Ensure Claude can read the repository files
3. **Check for .gitignore** - Some files might be ignored

### Getting more help

```bash
# View CLI help
pnd-agents --help
pnd-agents setup --help

# Check installation status
pnd-agents status

# View current configuration
pnd-agents config --show
```

---

## Quick Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `pnd-agents setup` | Run the setup wizard |
| `pnd-agents status` | Check installation status |
| `pnd-agents config --show` | View current configuration |
| `pnd-agents config --env` | Reconfigure environment variables |

### Config File Locations

| Product | OS | Location |
|---------|-----|----------|
| Claude Code | All | `~/.claude.json` |
| Claude Desktop | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Desktop | Linux | `~/.config/Claude/claude_desktop_config.json` |

### Required Tokens by Agent

| Agent | Required Tokens |
|-------|-----------------|
| Figma Reader | `FIGMA_ACCESS_TOKEN` |
| Sonar Validation | `SONAR_TOKEN` |
| PRD to Jira | `JIRA_*` tokens |
| PR Review | `AZURE_DEVOPS_*` tokens |
| Amplience CMS | `AMPLIENCE_*` tokens |

---

**Last Updated**: January 2026  
**Version**: 2.0.0  
**Maintained by**: Pandora Group
