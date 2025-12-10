# Using PG AI Squad Agents with Claude (Without Cloning)

This guide explains how to use the PG AI Squad agents directly with Claude Desktop or Claude Code without cloning the repository to your local machine.

## Overview

PG AI Squad provides production-ready AI agents for Pandora Group website development through the Model Context Protocol (MCP). You can access these agents directly through Claude by configuring your Claude client to connect to the MCP server.

## Available Agents

| Agent | Purpose | Key Capabilities |
|-------|---------|-----------------|
| **Task Manager** | Orchestration | Decomposes tasks, routes to specialists, merges outputs |
| **Frontend Engineer** | React/Next.js Development | Component generation, Storybook stories, accessibility validation |
| **Figma Reader** | Design Integration | Extracts metadata, design tokens, variants from Figma API |
| **Amplience CMS** | Content Management | Content types, JSON schemas, payload examples |
| **Code Review** | Quality Assurance | Validates against Pandora coding standards |
| **Unit Test** | Test Generation | Generates comprehensive tests targeting 100% coverage |
| **Sonar Validation** | Quality Gates | Validates against SonarCloud (0 errors, 0 duplication, 100% coverage) |
| **Performance** | Optimization | HAR file analysis, Core Web Vitals optimization |
| **QA** | Test Automation | E2E tests, integration tests, acceptance criteria validation |
| **Backend** | API Development | API routes, Server Components, mock services |
| **Commerce** | Product Discovery | AI-powered product search and cart preparation |

## Quick Start (Remote Access)

### Option 1: Direct GitHub Integration

You can configure Claude to use the agents directly from GitHub without cloning:

1. **Configure Claude Desktop/Code**

   Add this to your Claude configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.claude.json`
   - **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "pnd-agents": {
         "command": "npx",
         "args": [
           "-y",
           "github:shvee-pandora/pnd-agents"
         ],
         "env": {
           "FIGMA_ACCESS_TOKEN": "your-figma-token-here",
           "AMPLIENCE_HUB_NAME": "pandoragroup",
           "AMPLIENCE_BASE_URL": "https://cdn.content.amplience.net",
           "SONAR_TOKEN": "your-sonarcloud-token-here"
         }
       }
     }
   }
   ```

2. **Set Environment Variables** (Optional but recommended)

   For better security, set environment variables instead of hardcoding tokens:

   ```bash
   # macOS/Linux
   export FIGMA_ACCESS_TOKEN="your-figma-token"
   export SONAR_TOKEN="your-sonarcloud-token"
   ```

   Then reference them in the config:

   ```json
   {
     "mcpServers": {
       "pnd-agents": {
         "command": "npx",
         "args": ["-y", "github:shvee-pandora/pnd-agents"],
         "env": {
           "FIGMA_ACCESS_TOKEN": "${FIGMA_ACCESS_TOKEN}",
           "SONAR_TOKEN": "${SONAR_TOKEN}"
         }
       }
     }
   }
   ```

3. **Restart Claude**

   After updating the configuration, restart Claude Desktop or Claude Code.

4. **Verify Installation**

   In a new Claude conversation, ask:
   ```
   What pnd-agents tools do you have access to?
   ```

### Option 2: Using Python Package (Recommended)

If you have Python installed, you can install the package directly:

```bash
# Install from GitHub
pip install git+https://github.com/shvee-pandora/pnd-agents.git

# Run setup wizard
pnd-agents setup
```

The setup wizard will:
- Let you choose which agents to enable
- Configure environment variables
- Automatically update your Claude configuration

## Getting API Tokens

### Figma Access Token (Required for Figma Integration)

1. Go to [Figma Settings > Account](https://www.figma.com/settings)
2. Scroll to "Personal access tokens"
3. Click "Generate new token"
4. Give it a descriptive name (e.g., "PG AI Squad")
5. Copy the token immediately (you won't see it again)

### SonarCloud Token (Optional)

1. Go to [SonarCloud Security Settings](https://sonarcloud.io/account/security)
2. Generate a new token with "Analyze Projects" permission
3. Copy the token

**Note**: The Sonar Validation Agent can work without a token for basic validation, but API access enables real-time data from SonarCloud.

## Usage Examples

Once configured, you can use the agents directly in Claude conversations:

### 1. Create Component from Figma

```
Create a Stories carousel component from this Figma design:
https://www.figma.com/design/ABC123/My-Design?node-id=123-456
```

**What happens:**
- Task Manager detects "Figma" workflow
- Figma Reader extracts design metadata
- Frontend Engineer generates React component
- Code Review validates against standards
- Unit Test generates comprehensive tests
- Sonar Validation checks quality gates

### 2. Generate Unit Tests with 100% Coverage

```
Write unit tests for the Button component in src/components/Button/Button.tsx
with 100% coverage
```

**What happens:**
- Unit Test Agent analyzes the source file
- Generates test cases for all functions, branches, and edge cases
- Creates accessibility tests using jest-axe
- Sonar Validation verifies coverage meets quality gates

### 3. Validate Code Before PR

```
Validate my code in the feature/new-header branch against SonarCloud
quality gates before I create a PR
```

**What happens:**
- Sonar Validation Agent fetches issues, duplications, and coverage
- Analyzes pipeline configuration
- Generates fix plans for each issue
- Creates PR checklist for quality gate compliance

### 4. Create Amplience Content Type

```
Create an Amplience content type for a homepage hero section with:
- Title (text)
- Description (text)
- Background image (image)
- CTA button (link)
```

**What happens:**
- Amplience Agent generates JSON schema
- Creates example payload
- Provides content type registration instructions

### 5. Performance Optimization

```
Analyze this HAR file and suggest performance optimizations:
[attach HAR file]
```

**What happens:**
- Performance Agent parses HAR file
- Identifies slow endpoints
- Suggests caching/CDN improvements
- Provides Core Web Vitals metrics

### 6. AI-Powered Commerce

```
Find a silver bracelet under 700 DKK
```

**What happens:**
- Commerce Agent searches product catalog
- Filters by criteria (material, price, currency)
- Returns product recommendations with cart metadata

## Workflow Pipelines

The Task Manager automatically orchestrates agents based on task type:

| Task Type | Detection Keywords | Pipeline |
|-----------|-------------------|----------|
| **Figma** | figma, design, frame, component | Figma Reader → Frontend → Code Review → Unit Test → Sonar → Performance |
| **Frontend** | react, component, tsx, ui | Frontend → Code Review → Unit Test → Sonar → Performance |
| **Backend** | api, endpoint, server, route | Backend → Code Review → Unit Test → Sonar |
| **Amplience** | content type, cms, schema | Amplience → Frontend → Code Review → Unit Test → Sonar |
| **Unit Test** | unit tests, coverage, jest | Unit Test → Sonar |
| **Sonar** | sonar, quality gate, duplication | Sonar → Code Review |
| **QA** | tests, automation, playwright, e2e | QA → Unit Test → Sonar |
| **Performance** | performance, har, metrics | Performance |

## Advanced Usage

### Multi-Agent Workflows

You can request complex workflows that involve multiple agents:

```
Create a Stories carousel from Figma, write unit tests with 100% coverage,
validate against SonarCloud, and generate Playwright E2E tests
```

### Specific Agent Requests

You can also request specific agents directly:

```
Use the Figma Reader to extract design tokens from:
https://www.figma.com/design/ABC123/Design-System
```

```
Use the Code Review Agent to validate src/components/Header
against Pandora coding standards
```

### Task Decomposition

For complex tasks, the Task Manager will decompose them:

```
Build a complete product card component with:
- Figma design extraction
- React component implementation
- Storybook stories
- Unit tests with 100% coverage
- E2E tests
- SonarCloud validation
```

## Pandora Coding Standards

All agents follow Pandora's coding standards:

- **Next.js App Router** - Server Components, streaming, caching
- **Atomic Design** - atoms, molecules, organisms, templates
- **Design Tokens** - colors, typography, spacing, motion
- **TypeScript Strict Mode** - no `any`, proper typing
- **ESLint Rules** - security, accessibility, SonarJS
- **Accessibility** - WCAG 2.1 AA compliance
- **Amplience Patterns** - global partials, content hierarchies

## Quality Gates (Sonar Validation)

The Sonar Validation Agent enforces:

- **0 errors** - No bugs or vulnerabilities
- **0 duplication** - No duplicated code blocks
- **100% coverage** - All code paths tested

When issues are found, the agent generates fix plans with step-by-step instructions.

## Troubleshooting

### Agents Not Available in Claude

1. **Check Configuration File**
   - Verify the config file exists at the correct location
   - Ensure JSON syntax is valid
   - Confirm paths are absolute (not relative)

2. **Restart Claude**
   - Configuration changes require a restart
   - Close and reopen Claude Desktop/Code completely

3. **Check Logs**
   - Claude Desktop logs: `~/Library/Logs/Claude/`
   - Look for MCP connection errors

### Figma API Errors

1. **Verify Token**
   - Ensure `FIGMA_ACCESS_TOKEN` is set correctly
   - Check token hasn't expired
   - Verify token has read access to the file

2. **Check URL Format**
   - Use the full Figma URL including node-id
   - Example: `https://www.figma.com/design/ABC123/My-Design?node-id=123-456`

### SonarCloud API Errors

1. **Verify Token** (if using API access)
   - Ensure `SONAR_TOKEN` is set correctly
   - Check token has "Analyze Projects" permission

2. **Fallback Mode**
   - The agent works without a token for basic validation
   - API access enables real-time data fetching

### Python Installation Issues

If using the Python package method:

```bash
# Verify Python version (3.10+ required)
python --version

# Reinstall package
pip uninstall pnd-agents
pip install git+https://github.com/shvee-pandora/pnd-agents.git

# Run setup again
pnd-agents setup
```

## Environment Variables Reference

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| `FIGMA_ACCESS_TOKEN` | For Figma integration | Figma API authentication | `figd_...` |
| `AMPLIENCE_HUB_NAME` | For Amplience integration | Amplience hub identifier | `pandoragroup` |
| `AMPLIENCE_BASE_URL` | For Amplience integration | Amplience CDN base URL | `https://cdn.content.amplience.net` |
| `SONAR_TOKEN` | Optional | SonarCloud API access | `sqp_...` |
| `SFCC_OCAPI_INSTANCE` | For Commerce (live) | Salesforce Commerce Cloud instance | `production-emea-pandora.demandware.net` |
| `SFCC_CLIENT_ID` | For Commerce (live) | SFCC client ID | Your client ID |
| `SFCC_SITE_ID` | For Commerce (live) | SFCC site identifier | `en-GB` |

## Security Best Practices

1. **Never Commit Tokens**
   - Add `.env` to `.gitignore`
   - Use environment variables instead of hardcoding

2. **Use Minimal Permissions**
   - Figma: Read-only access
   - SonarCloud: "Analyze Projects" only

3. **Rotate Tokens Regularly**
   - Generate new tokens periodically
   - Revoke old tokens after rotation

4. **Use Separate Tokens per Environment**
   - Development tokens for local work
   - Production tokens for CI/CD only

## Support and Resources

- **Repository**: [github.com/shvee-pandora/pnd-agents](https://github.com/shvee-pandora/pnd-agents)
- **Documentation**: 
  - [Setup Guide](https://github.com/shvee-pandora/pnd-agents/blob/main/docs/setup.md)
  - [Architecture](https://github.com/shvee-pandora/pnd-agents/blob/main/docs/architecture.md)
  - [Publishing Guide](https://github.com/shvee-pandora/pnd-agents/blob/main/docs/publishing.md)
- **Examples**: [github.com/shvee-pandora/pnd-agents/tree/main/examples](https://github.com/shvee-pandora/pnd-agents/tree/main/examples)

## Next Steps

1. **Configure Claude** with the MCP server settings above
2. **Get API Tokens** for Figma and optionally SonarCloud
3. **Start a Conversation** in Claude and try the example prompts
4. **Explore Workflows** by requesting different types of tasks
5. **Review Documentation** for advanced features and customization

## Example Conversation Starters

Here are some ready-to-use prompts to get started:

```
List all available pnd-agents tools and their capabilities
```

```
Create a React component for a product card with image, title, price, and CTA button
```

```
Extract design tokens from this Figma file: [URL]
```

```
Review the code in src/components/Header for Pandora coding standards
```

```
Generate unit tests with 100% coverage for src/utils/formatPrice.ts
```

```
Validate my feature branch against SonarCloud quality gates
```

```
Find gold earrings under 1000 EUR
```

---

**Note**: This guide assumes you're using Claude Desktop or Claude Code with MCP support. For programmatic usage or custom integrations, see the [main README](https://github.com/shvee-pandora/pnd-agents).
