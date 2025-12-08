# Publishing pnd-agents to Azure Artifacts

This document describes how to publish and install pnd-agents from the internal Azure Artifacts PyPI feed.

## For Maintainers: Publishing a New Version

### 1. Update the Version

Edit `pyproject.toml` and update the version number:

```toml
[project]
name = "pnd-agents"
version = "1.1.0"  # Increment this
```

### 2. Commit and Tag

```bash
git add pyproject.toml
git commit -m "chore: bump version to 1.1.0"
git push origin main

# Create and push a version tag
git tag v1.1.0
git push origin v1.1.0
```

### 3. Pipeline Execution

The Azure Pipeline will automatically:
1. Build the wheel and sdist packages
2. Publish to the `BI-Databases` Azure Artifacts feed

Monitor the pipeline at: https://dev.azure.com/pandora-jewelry/Spark/_build

## For Developers: Installing pnd-agents

### Option 1: One-time Installation

```bash
# Install from Azure Artifacts (requires authentication)
pip install pnd-agents \
  --index-url "https://pkgs.dev.azure.com/pandora-jewelry/_packaging/BI-Databases/pypi/simple/" \
  --extra-index-url "https://pypi.org/simple"
```

### Option 2: Configure pip Globally (Recommended)

Create or edit `~/.config/pip/pip.conf` (Linux/macOS) or `%APPDATA%\pip\pip.ini` (Windows):

```ini
[global]
index-url = https://pkgs.dev.azure.com/pandora-jewelry/_packaging/BI-Databases/pypi/simple/
extra-index-url = https://pypi.org/simple
trusted-host = pkgs.dev.azure.com
```

Then simply run:

```bash
pip install pnd-agents
```

### Authentication

Azure Artifacts requires authentication. You have several options:

#### Option A: Azure CLI (Recommended)

```bash
# Install Azure CLI if not already installed
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Install the artifacts-keyring helper
pip install artifacts-keyring

# Now pip install will automatically authenticate
pip install pnd-agents
```

#### Option B: Personal Access Token (PAT)

1. Create a PAT at https://dev.azure.com/pandora-jewelry/_usersSettings/tokens
2. Select "Packaging (Read)" scope
3. Use the PAT in the URL:

```bash
pip install pnd-agents \
  --index-url "https://YOUR_USERNAME:YOUR_PAT@pkgs.dev.azure.com/pandora-jewelry/_packaging/BI-Databases/pypi/simple/"
```

## Post-Installation Setup

After installing pnd-agents, run the setup wizard:

```bash
# Interactive setup
pnd-agents setup

# Or use a preset
pnd-agents setup --preset default --auto
```

This will:
1. Configure which agents to enable
2. Set up environment variables (FIGMA_ACCESS_TOKEN, etc.)
3. Register pnd-agents as an MCP server in Claude Desktop/Code

### Required Environment Variables

Set these in your shell profile or `.env` file:

| Variable | Required For | Description |
|----------|--------------|-------------|
| `FIGMA_ACCESS_TOKEN` | Figma Reader Agent | Figma API token |
| `AMPLIENCE_HUB_NAME` | Amplience CMS Agent | Amplience hub name |
| `AMPLIENCE_BASE_URL` | Amplience CMS Agent | Amplience base URL |

### Install Playwright (for BX Detector)

```bash
playwright install chromium
```

## Verify Installation

```bash
# Check installation status
pnd-agents status

# Test with a simple task analysis
pnd-agents analyze-task "Create a React component"
```

## Troubleshooting

### "Package not found" Error

Ensure you're authenticated with Azure Artifacts:
```bash
pip install artifacts-keyring
az login
```

### "Permission denied" Error

Your PAT may have expired or lack the "Packaging (Read)" scope. Create a new PAT.

### Claude Not Detecting pnd-agents

1. Restart Claude Desktop/Code after running `pnd-agents setup`
2. Check the config file exists:
   - macOS: `~/.claude.json` or `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.claude.json`
