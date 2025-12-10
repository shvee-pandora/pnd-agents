# Documentation Index

Welcome to the PG AI Squad documentation. This index provides an overview of all available documentation and guides you to the right resource based on your needs.

## Quick Navigation

| Document | Description | Best For |
|----------|-------------|----------|
| [Setup Guide](./setup.md) | Complete installation and configuration | First-time setup |
| [Claude Usage](./claude-usage.md) | Using agents with Claude without cloning | Remote usage via Claude |
| [Quick Reference](./quick-reference.md) | One-page quick reference card | Quick lookup, sharing |
| [Architecture](./architecture.md) | System architecture and design | Understanding the system |
| [Publishing](./publishing.md) | Publishing to Azure Artifacts | Maintainers |
| [Setup Diagram](./setup-diagram.md) | Visual ASCII setup flow | Visual learners |
| [Agents Overview](./agents-overview.md) | All agents and their capabilities | Agent reference |

## Getting Started

### New Users
1. Start with the [Quick Reference](./quick-reference.md) for a 4-step setup
2. Follow the [Setup Guide](./setup.md) for detailed installation
3. Review the [Architecture](./architecture.md) to understand the system

### Using Claude Without Cloning
If you want to use the agents directly in Claude Desktop/Code without cloning the repository:
1. Follow the [Claude Usage Guide](./claude-usage.md)
2. Use the [Quick Reference](./quick-reference.md) for a condensed version

### Visual Learners
Check out the [Setup Diagram](./setup-diagram.md) for ASCII diagrams of the setup flow and agent capabilities.

## Documentation by Topic

### Setup & Configuration
- [Setup Guide](./setup.md) - Complete installation with prerequisites, options, and troubleshooting
- [Claude Usage](./claude-usage.md) - Remote usage via Claude Desktop/Code
- [Quick Reference](./quick-reference.md) - Condensed setup steps and common commands
- [Setup Diagram](./setup-diagram.md) - Visual representation of setup flow

### Architecture & Design
- [Architecture](./architecture.md) - System architecture, agent design, tools, and MCP integration

### Agents
- [Agents Overview](./agents-overview.md) - Complete list of all agents with capabilities and documentation links

### Publishing & Distribution
- [Publishing](./publishing.md) - Guide for publishing to Azure Artifacts

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
2. Point to [Claude Usage](./claude-usage.md) for detailed information
3. Use [Setup Diagram](./setup-diagram.md) for visual learners

### Scenario 2: Quick Setup for Existing Claude Users
1. Use [Quick Reference](./quick-reference.md) for 4-step setup
2. Refer to [Claude Usage](./claude-usage.md) only if issues arise

### Scenario 3: Team Training Session
1. Present [Setup Diagram](./setup-diagram.md) on screen
2. Walk through [Quick Reference](./quick-reference.md) steps
3. Distribute [Claude Usage](./claude-usage.md) for reference

## Quality Standards

All agents enforce these quality standards:

- Next.js App Router patterns
- Atomic Design methodology
- TypeScript Strict Mode
- Accessibility (WCAG 2.1 AA)
- SonarCloud (0 errors, 0 duplication, 100% coverage)
- ESLint Rules
- Design Tokens

## Links

- **Repository**: [github.com/shvee-pandora/pnd-agents](https://github.com/shvee-pandora/pnd-agents)
- **Main README**: [README.md](../README.md)

---

**Last Updated**: December 2025  
**Version**: 1.0.0  
**Maintained by**: Pandora Group
