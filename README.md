# PG AI Squad

A production-grade agentic system for Pandora Group, featuring MCP-compatible agents that can be loaded as Claude Desktop plugins.

## Overview

PG AI Squad is a comprehensive agent ecosystem designed to assist with building the Pandora Group website. The system includes specialized agents for task management, frontend development, Amplience CMS integration, code review, performance optimization, QA testing, and backend development.

## Features

- **Task Orchestration**: Scrum Master Agent that decomposes tasks and coordinates other agents
- **Frontend Development**: React/Next.js component generation following Pandora UI Toolkit patterns
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
| Amplience CMS | Specialist | Creates content types, schemas, and example payloads |
| Code Review | Validator | Validates code against Pandora standards |
| Performance | Specialist | Analyzes HAR files, suggests optimizations |
| QA | Validator | Generates tests, validates acceptance criteria |
| Backend | Specialist | Creates API routes, Server Components, mock APIs |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 20+
- Claude Desktop (for MCP integration)

### Installation

```bash
# Clone the repository
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents

# Install Python dependencies
pip install -r requirements.txt

# Configure Claude Desktop
cp mcp-config/claude.config.json ~/.config/claude/mcp.json
```

### Configuration

Set the following environment variables:

```bash
export AMPLIENCE_HUB_NAME="pandoragroup"
export AMPLIENCE_BASE_URL="https://cdn.content.amplience.net"
export FIGMA_ACCESS_TOKEN="your-figma-token"
```

### Usage

#### With Claude Desktop

1. Open Claude Desktop
2. The PG AI Squad agents will be available as MCP plugins
3. Start a conversation and ask for help with development tasks

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
