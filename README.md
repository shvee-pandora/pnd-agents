# PG AI Squad

A production-grade agentic system for Pandora Group, featuring MCP-compatible agents that can be loaded as Claude Desktop plugins.

## Overview

PG AI Squad is a comprehensive agent ecosystem designed to assist with building the Pandora Group website. The system includes specialized agents for task management, frontend development, Amplience CMS integration, code review, performance optimization, QA testing, and backend development.

## Features

- **Task Orchestration**: Scrum Master Agent that decomposes tasks and coordinates other agents
- **Frontend Development**: React/Next.js component generation following Pandora UI Toolkit patterns
- **Figma Integration**: Extract component metadata directly from Figma designs via API
- **Amplience CMS**: Content type creation, JSON schema generation, and payload examples
- **Code Review**: Automated validation against Pandora coding standards
- **Performance Analysis**: HAR file analysis and Core Web Vitals optimization
- **QA Testing**: Unit test, integration test, and E2E test generation
- **Backend Development**: API routes, Server Components, and mock API services

## Agents

| Agent | Role | Description |
|-------|------|-------------|
| Task Manager | Orchestrator | Decomposes tasks, assigns to agents, merges outputs |
| Frontend Engineer | Specialist | Generates React components, Storybook stories, validates accessibility |
| Figma Reader | Specialist | Extracts component metadata, design tokens, variants from Figma |
| Amplience CMS | Specialist | Creates content types, schemas, and example payloads |
| Code Review | Validator | Validates code against Pandora standards |
| Performance | Specialist | Analyzes HAR files, suggests optimizations |
| QA | Validator | Generates tests, validates acceptance criteria |
| Backend | Specialist | Creates API routes, Server Components, mock APIs |
| Commerce | Specialist | Agentic commerce - finds products, filters by criteria, prepares cart metadata |

## Quick Start

### Prerequisites

- Python 3.10+
- Claude Desktop or Claude Code (for MCP integration)

### One-Command Installation

```bash
# Clone and install
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents
pip install -e .

# Run the setup wizard
pnd-agents setup
```

The setup wizard will:
1. Let you choose which agents to enable
2. Configure environment variables (Figma token, Amplience settings)
3. Automatically update your Claude configuration

### Installation Options

```bash
# Interactive setup (recommended)
pnd-agents setup

# Use preset configurations
pnd-agents setup --preset default    # Recommended agents
pnd-agents setup --preset full       # All agents enabled
pnd-agents setup --preset minimal    # Only essential agents

# Skip environment variable prompts
pnd-agents setup --skip-env

# Auto-write config without prompts
pnd-agents setup --auto --preset default
```

### Reconfigure Anytime

```bash
# Change which agents are enabled
pnd-agents config --agents

# Update environment variables
pnd-agents config --env

# View current configuration
pnd-agents config --show

# Check installation status
pnd-agents status

# Remove from Claude config
pnd-agents uninstall
```

### Manual Configuration (Alternative)

If you prefer manual setup, set these environment variables:

```bash
export FIGMA_ACCESS_TOKEN="your-figma-token"
export AMPLIENCE_HUB_NAME="pandoragroup"
export AMPLIENCE_BASE_URL="https://cdn.content.amplience.net"
```

Then add to your Claude config (`~/.claude.json`):

```json
{
  "mcpServers": {
    "pnd-agents": {
      "command": "python",
      "args": ["/path/to/pnd-agents/main.py"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "${env:FIGMA_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Usage

#### With Claude Desktop / Claude Code

1. Run `pnd-agents setup` to configure
2. Restart Claude Desktop/Code
3. Start a conversation and the agents will be available
4. Try: "Use the Task Manager to help me create a component from Figma"

#### Figma Workflow (Design-First)

For best results when creating components from Figma:

1. Provide a Figma URL in your task
2. The Task Manager will automatically:
   - Call the Figma Reader Agent first
   - Extract component metadata, design tokens, variants
   - Pass the data to the Frontend Engineer Agent
   - Generate React components matching the design
   - Run Code Review and QA agents

Example prompt:
```
Create a Stories carousel component from this Figma design:
https://www.figma.com/design/ABC123/My-Design?node-id=123-456
```

#### Programmatic Usage

```python
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

## Project Structure

```
pnd-agents/
├── agents/                    # Agent definitions
│   ├── task_manager/          # Task Manager Agent
│   ├── frontend/              # Frontend Engineer Agent
│   ├── amplience/             # Amplience CMS Agent
│   ├── code_review/           # Code Review Agent
│   ├── performance/           # Performance Agent
│   ├── qa/                    # QA Agent
│   └── backend/               # Backend Agent
├── tools/                     # Core tools
│   ├── filesystem.py          # File system operations
│   ├── command_runner.py      # Command execution
│   ├── figma_parser.py        # Figma design parsing
│   ├── amplience_api.py       # Amplience CMS integration
│   └── har_analyzer.py        # HAR file analysis
├── mcp-config/                # MCP configuration
│   ├── claude.config.json     # Claude Desktop config
│   └── agents.config.json     # Agent configuration
├── examples/                  # Example tasks
│   ├── create-component-from-figma.md
│   ├── create-amplience-content-type.md
│   └── performance-optimization.md
└── .claude-plugin/            # Plugin marketplace config
    └── marketplace.json
```

## Agentic Commerce POC

The Commerce Agent enables AI-powered product discovery and cart preparation. It understands natural language shopping goals and returns product recommendations ready for cart addition.

### Usage

```python
from agents.commerce_agent import find_product_and_prepare_cart

# Find a product matching a shopping goal
result = find_product_and_prepare_cart("silver bracelet under 700 DKK")
print(result)
# {
#   "productId": "599114C00",
#   "name": "Pandora Moments Silver Heart Clasp Snake Chain Bracelet",
#   "price": 599,
#   "currency": "DKK",
#   "imageUrl": "https://...",
#   "message": "Found Pandora Moments Silver Heart Clasp Snake Chain Bracelet (599 DKK) - Ready to add to cart."
# }
```

### MCP Tool

The commerce agent is registered as an MCP tool: `commerce_find_product_and_prepare_cart`

Example prompts:
- "Find a silver bracelet under 700 DKK"
- "Heart charms under 400 DKK"
- "Gold ring under 2000 EUR"

### Environment Variables

For live API access, set these environment variables:

```bash
export SFCC_OCAPI_INSTANCE="production-emea-pandora.demandware.net"
export SFCC_CLIENT_ID="your-client-id"
export SFCC_SITE_ID="en-GB"
```

The agent includes mock product data for POC testing when API access is unavailable.

### Integration with pandora-ecom-web

The Commerce Agent integrates with pandora-ecom-web via the `/api/agentic-commerce` endpoint and the `/ai-demo` page. See the pandora-ecom-web repository for frontend integration details.

## Documentation

- [Setup Guide](SETUP.md) - Detailed installation and configuration
- [Architecture](ARCHITECTURE.md) - System architecture and design decisions
- [Examples](examples/) - Example tasks demonstrating agent collaboration

## Pandora Coding Standards

All agents follow Pandora's coding standards from Epic INS-2509:

- **Next.js App Router** - Server Components, streaming, caching
- **Atomic Design** - atoms, molecules, organisms, templates
- **Design Tokens** - colors, typography, spacing, motion
- **TypeScript Strict Mode** - no `any`, proper typing
- **ESLint Rules** - security, accessibility, SonarJS
- **Accessibility** - WCAG 2.1 AA compliance
- **Amplience Patterns** - global partials, content hierarchies

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/INS-XXXX-description`
3. Make your changes
4. Run validation: `pnpm validate`
5. Create a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Pandora Group Website](https://www.pandoragroup.com)
- [Amplience CMS](https://amplience.com)
- [Claude Desktop](https://claude.ai/desktop)
- [MCP Specification](https://modelcontextprotocol.io)
