# PG AI Squad

A production-grade agentic system for Pandora Group, featuring MCP-compatible agents that can be loaded as Claude Desktop plugins.

## Overview

PG AI Squad is a comprehensive agent ecosystem designed to assist with building the Pandora Group website. The system includes specialized agents for task management, frontend development, Amplience CMS integration, code review, performance optimization, QA testing, and backend development.

## Features

- **Workflow Engine**: Automatic task type detection and multi-agent pipeline orchestration
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
| QA | Validator | Generates E2E and integration tests, validates acceptance criteria |
| **Unit Test** | Specialist | Generates comprehensive unit tests with **100% coverage** target |
| **Sonar Validation** | Validator | Validates against SonarCloud quality gates (0 errors, 0 duplication, 100% coverage) |
| Backend | Specialist | Creates API routes, Server Components, mock APIs |
| Commerce | Specialist | Agentic commerce - finds products, filters by criteria, prepares cart metadata |

## Quick Start

> **💡 Want to use these agents without cloning?** See the [Claude Usage Guide](CLAUDE_USAGE.md) for instructions on using these agents directly in Claude Desktop/Code without local installation.

### Prerequisites

- Python 3.10+
- Claude Desktop or Claude Code (for MCP integration)

### One-Command Installation

```bash
# Clone and install
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents
pip install -e .

# Install Playwright browser binaries (required for Broken Experience Detector)
playwright install

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

## Workflow Engine

The workflow engine automatically detects task types and orchestrates agents in a pipeline. When you give a task to the Task Manager, it analyzes the description, selects the appropriate workflow, and runs agents sequentially until completion.

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        TASK INPUT                               │
│  "Create Stories carousel from Figma: https://figma.com/..."   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TASK TYPE DETECTION                          │
│  Keywords: "figma", "carousel" → Detected: FIGMA workflow       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW PIPELINE                            │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Figma   │──▶│ Frontend │──▶│  Review  │──▶│    QA    │    │
│  │  Reader  │   │ Engineer │   │  Agent   │   │  Agent   │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│       │              │              │              │           │
│       ▼              ▼              ▼              ▼           │
│   Design         Component      Standards      Tests          │
│   Tokens         Code           Report         Generated      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FINAL OUTPUT                                 │
│  Complete component with tests, following Pandora standards     │
└─────────────────────────────────────────────────────────────────┘
```

### Task Type Detection

The engine detects task types using keyword matching:

| Task Type | Keywords |
|-----------|----------|
| Figma | figma, design, frame, component, ui spec |
| Frontend | react, component, tsx, ui, frontend |
| Backend | api, endpoint, server, route, integration |
| Amplience | content type, cms, schema, amplience |
| Unit Test | unit tests, coverage, jest, vitest, 100% coverage |
| Sonar | sonar, sonarcloud, quality gate, duplication, code smells |
| QA | tests, automation, playwright, e2e, integration tests |
| Code Review | review, lint, standards, refactor |
| Performance | performance, har, metrics, optimization |

### Workflow Pipelines

Different task types trigger different agent sequences (now includes Unit Test and Sonar Validation):

| Workflow | Pipeline |
|----------|----------|
| Figma | Figma Reader → Frontend → Code Review → **Unit Test → Sonar** → Performance |
| Frontend | Frontend → Code Review → **Unit Test → Sonar** → Performance |
| Backend | Backend → Code Review → **Unit Test → Sonar** |
| Amplience | Amplience → Frontend → Code Review → **Unit Test → Sonar** |
| Unit Test | **Unit Test → Sonar** |
| Sonar | **Sonar** → Code Review |
| Default | Frontend → Code Review → **Unit Test → Sonar** |

### CLI Commands

```bash
# Run a task through the workflow engine
pnd-agents run-task "Create Stories carousel from Figma: https://figma.com/..."

# Run with ticket ID and branch
pnd-agents run-task "Build product card component" --ticket INS-2509 --branch feature/product-card

# Show workflow plan without executing
pnd-agents run-task "Create API endpoint for products" --plan-only

# Analyze a task to see which workflow would be used
pnd-agents analyze-task "Create content type for homepage hero"

# Save workflow output to file
pnd-agents run-task "Build header component" --output /tmp/workflow-result.json
```

### Programmatic Usage

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
for stage in context.stages:
    print(f"  {stage.agent_name}: {stage.status}")
```

### State Management

The workflow engine persists state to `/tmp/pnd_agent_context.json`, enabling:

- Resume interrupted workflows
- Pass data between agents
- Track progress and timing
- Debug failed stages

```python
# Resume an interrupted task
agent = TaskManagerAgent()
context = agent.resume_task(verbose=True)

# Clear saved state
agent.clear_task()
```

## Unit Test Agent

The Unit Test Agent is dedicated to generating comprehensive unit tests with a **100% coverage** target. It analyzes source code and generates tests that cover all functions, branches, and edge cases.

### Features

- Analyzes source files to identify testable elements (functions, components, hooks, classes)
- Generates test cases for all code paths including branches
- Supports Jest and Vitest frameworks
- Generates accessibility tests using jest-axe
- Provides coverage improvement recommendations

### Usage

```python
from agents.unit_test_agent import UnitTestAgent, generate_tests

# Generate tests for a source file
result = generate_tests("src/components/Button/Button.tsx", framework="jest")
print(result["testCode"])

# Or use the agent directly
agent = UnitTestAgent()
test_file = agent.generate_test_file("src/components/Button/Button.tsx")
print(f"Generated {len(test_file.test_cases)} test cases")
```

### CLI Usage

```bash
# Run unit test generation as part of workflow
pnd-agents run-task "Write unit tests for the Button component with 100% coverage"
```

## Sonar Validation Agent

The Sonar Validation Agent validates code against SonarCloud quality gates before PR creation. It ensures **0 errors, 0 duplication, and 100% coverage**.

### Features

- Fetches issues, duplications, and coverage from SonarCloud API
- Analyzes pipeline configuration files (azure-pipelines.yml, sonar-project.properties)
- Generates fix plans for each issue with step-by-step instructions
- Creates PR checklists to ensure quality gate compliance
- Targets: https://sonarcloud.io/summary/new_code?id=pandora-jewelry_spark_pandora-group&branch=master

### Usage

```python
from agents.sonar_validation_agent import SonarValidationAgent, validate_for_pr

# Validate code for PR readiness
result = validate_for_pr(branch="feature/my-branch", project_key="pandora-jewelry_spark_pandora-group")
print(f"Ready for PR: {result['readyForPR']}")
print(result['checklist'])

# Or use the agent directly
agent = SonarValidationAgent()
validation = agent.validate(branch="master")
print(f"Quality Gate: {validation.quality_gate_status}")
print(f"Issues: {len(validation.issues)}")
```

### Environment Variables

```bash
export SONAR_TOKEN="your-sonarcloud-token"  # Optional, for API access
```

### CLI Usage

```bash
# Run Sonar validation as part of workflow
pnd-agents run-task "Validate code against SonarCloud quality gates"
```

## Documentation

- [Claude Usage Guide](CLAUDE_USAGE.md) - Using agents with Claude without cloning the repo
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
