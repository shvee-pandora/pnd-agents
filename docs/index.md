# Documentation Index

Welcome to the **Pandora AI Squad** documentation. This index provides an overview of all available documentation and guides you to the right resource based on your needs.

## Quick Navigation

| Document | Description | Best For |
|----------|-------------|----------|
| [Setup Guide](./setup.md) | Complete installation and configuration | First-time setup |
| [FAQ](./faq.md) | Common questions and troubleshooting | Installation issues |
| [Using Agents Without MCP](./using-agents-without-mcp.md) | Python API, CLI, automation | CI/CD, scripting |
| [Quick Reference](./quick-reference.md) | One-page quick reference card | Quick lookup, sharing |
| [Architecture](./architecture.md) | System architecture and design | Understanding the system |
| [How Agents Work](./how-agents-work.md) | Low-level agent internals | Developers, contributors |
| [Agents Overview](./agents-overview.md) | All agents and their capabilities | Agent reference |
| [Publishing](./publishing.md) | Publishing to Azure Artifacts | Maintainers |
| [Delivery Reports](./delivery-reports-guide.md) | Sprint and delivery reporting tools | Project managers |

## Getting Started

### New Users
1. Start with the [Quick Reference](./quick-reference.md) for a 4-step setup
2. Follow the [Setup Guide](./setup.md) for detailed installation
3. Review the [Architecture](./architecture.md) to understand the system
4. Read [How Agents Work](./how-agents-work.md) for low-level details

### For Developers & Contributors
If you want to understand how agents work internally or contribute to the project:
1. Read [How Agents Work](./how-agents-work.md) for agent internals
2. Review [Architecture](./architecture.md) for system design
3. Check [Agents Overview](./agents-overview.md) for all available agents

## Documentation by Topic

### Setup & Configuration
- [Setup Guide](./setup.md) - Complete installation with prerequisites, options, and troubleshooting
- [FAQ](./faq.md) - Common questions about config locations, cross-repo usage, tokens
- [Quick Reference](./quick-reference.md) - Condensed setup steps and common commands

### Programmatic Usage
- [Using Agents Without MCP](./using-agents-without-mcp.md) - Python API, CLI commands, CI/CD integration

### Architecture & Design
- [Architecture](./architecture.md) - System architecture, agent design, tools, and MCP integration
- [How Agents Work](./how-agents-work.md) - Low-level agent internals, standards workflow, Context7 integration

### Agents
- [Agents Overview](./agents-overview.md) - Complete list of all agents with capabilities and documentation links

### Publishing & Distribution
- [Publishing](./publishing.md) - Guide for publishing to Azure Artifacts

### Reporting
- [Delivery Reports Guide](./delivery-reports-guide.md) - Sprint and delivery reporting tools

## Configuration Files

The project uses two configuration directories:

### `/config/` - Runtime Configuration
- `analytics.config.json` - Analytics agent settings
- `jira.config.json` - JIRA integration credentials
- `agent-workflow.json` - Workflow engine configuration

### `/mcp-config/` - MCP Client Configuration
- `agents.config.json` - Agent definitions for MCP
- `claude.config.json` - Claude Desktop/Code configuration template

## Examples

Working examples are available in the `/examples/` directory:

- [Analytics Examples](../examples/analytics/README.md) - Analytics agent usage examples
- [Create Component from Figma](../examples/create-component-from-figma.md) - Figma to React workflow
- [Create Amplience Content Type](../examples/create-amplience-content-type.md) - CMS content type creation
- [Performance Optimization](../examples/performance-optimization.md) - HAR analysis and optimization

## Usage Scenarios

### Scenario 1: New Team Member Onboarding
1. Share [Quick Reference](./quick-reference.md) for immediate setup
2. Point to [FAQ](./faq.md) for common questions
3. Use [Setup Guide](./setup.md) for detailed installation

### Scenario 2: Quick Setup for Existing Claude Users
1. Use [Quick Reference](./quick-reference.md) for 4-step setup
2. Refer to [FAQ](./faq.md) only if issues arise

### Scenario 3: Team Training Session
1. Present [Architecture](./architecture.md) diagrams on screen
2. Walk through [Quick Reference](./quick-reference.md) steps
3. Distribute [FAQ](./faq.md) for troubleshooting reference

## Quality Standards

All agents enforce these quality standards:

- **Pandora Coding Standards** (from `coding_standards.py`) - Primary source of truth
- **Context7 Framework Standards** - Latest best practices for any JS/TS framework
- **Universal JS/TS Standards** - General best practices
- Next.js App Router patterns
- Atomic Design methodology
- TypeScript Strict Mode
- Accessibility (WCAG 2.1 AA)
- SonarCloud (0 errors, 0 duplication, 100% coverage)
- ESLint Rules
- Design Tokens

## Directory Structure

The agent system uses a categorized directory structure:

```
src/agents/
├── core/                    # Shared infrastructure
│   ├── coding_standards.py  # Pandora coding standards
│   ├── repo_adapter.py      # Cross-repo utilities
│   ├── clients/             # External service clients
│   └── analyzers/           # Shared analysis utilities
├── universal/               # Framework-agnostic agents
│   ├── orchestration/       # Task Manager
│   ├── development/         # Frontend, Backend, Figma
│   ├── quality/             # Code Review, Unit Test, QA, Sonar
│   ├── performance/         # Performance, Broken Experience
│   ├── product_management/  # PRD to Jira, Exec Summary, Roadmap
│   └── analytics/           # Analytics, Technical Debt
└── platform/                # Platform-specific agents
    ├── commerce/            # Pandora Commerce
    └── cms/                 # Amplience CMS
```

## Links

- **Repository**: [github.com/shvee-pandora/pnd-agents](https://github.com/shvee-pandora/pnd-agents)
- **Main README**: [README.md](../README.md)

---

**Last Updated**: January 2026  
**Version**: 2.0.0  
**Maintained by**: Pandora Group
