# Pandora AI Squad

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

> **💡 Want to use these agents without cloning?** See the [Claude Usage Guide](docs/claude-usage.md) for instructions on using these agents directly in Claude Desktop/Code without local installation.

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

**Important:** The `pip install -e .` step is required to make the `pnd-agents` CLI command available. If you skip this step, the MCP tools will work but the CLI commands won't be available in your terminal.

The setup wizard will:
1. Let you choose which agents to enable
2. Configure environment variables (Figma token, Amplience settings)
3. Automatically update your Claude configuration

### Troubleshooting: CLI Not Found

If you see `pnd-agents: command not found`, try these solutions:

1. **Verify installation:** Run `pip show pnd-agents` to check if the package is installed
2. **Use module fallback:** Run `python -m pnd_agents` instead of `pnd-agents`
3. **Check Python environment:** Make sure you're using the same Python that Claude uses:
   ```bash
   # Find which Python Claude is using (check your Claude config)
   # Then install with that specific Python:
   /usr/local/bin/python3 -m pip install -e .
   ```
4. **Check PATH:** The CLI script is installed in your Python's `bin` directory. Ensure it's in your PATH:
   ```bash
   # Find where pip installs scripts
   python -m site --user-base
   # Add the bin directory to your PATH if needed
   ```

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

### Using Slash Commands (No MCP Setup Required)

PND Agents are also available as **slash commands** in both Claude Desktop and Claude Code. This is the easiest way to use the agents - no MCP server configuration needed.

#### Option A: Claude Code (CLI/IDE)

The `.claude/commands/` directory in this repository contains all 17 agent commands. When you open Claude Code in this repo, type `/` to see available commands:

```bash
# Clone the repo
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents

# Open in Claude Code and use slash commands
/frontend Create a product card component
/prd-to-jira [paste your PRD content]
/code-review [paste code to review]
```

To use these commands in your own project, copy the `.claude/commands/` folder:

```bash
cp -r .claude/commands/ /path/to/your/project/.claude/commands/
```

#### Option B: Claude Desktop Plugin

Install the plugin from `src/plugins/pnd-agents-slash-commands/`:

**macOS:**
```bash
cp -r src/plugins/pnd-agents-slash-commands ~/Library/Application\ Support/Claude/plugins/
```

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse src\plugins\pnd-agents-slash-commands $env:APPDATA\Claude\plugins\
```

Then restart Claude Desktop and type `/` to see all available commands.

#### Available Slash Commands

**Development Agents:**

| Command | Description | Example |
|---------|-------------|---------|
| `/task-manager` | Orchestrate complex tasks across specialized agents | `/task-manager Create a product detail page with cart functionality` |
| `/frontend` | Generate React/Next.js components | `/frontend Create a product card with image, title, price` |
| `/backend` | Create API routes and serverless functions | `/backend Create a REST API for user profiles` |
| `/unit-test` | Generate comprehensive unit tests | `/unit-test [paste component code]` |
| `/code-review` | Review code for quality and security | `/code-review [paste code to review]` |

**CMS Agents:**

| Command | Description | Example |
|---------|-------------|---------|
| `/amplience` | Create Amplience CMS content types | `/amplience Create a hero banner content type` |
| `/amplience-placement` | Configure content placements and slots | `/amplience-placement Configure hero slot for homepage` |

**Quality & Performance Agents:**

| Command | Description | Example |
|---------|-------------|---------|
| `/qa` | Analyze test coverage and generate scenarios | `/qa Analyze test coverage for checkout flow` |
| `/performance` | Analyze HAR files and Core Web Vitals | `/performance Our LCP is 4.2s, help identify causes` |
| `/sonar` | Validate SonarCloud compliance | `/sonar [paste code for analysis]` |
| `/bx-scan` | Detect broken experiences and dead links | `/bx-scan https://www.pandora.net/en-us` |

**Commerce Agents:**

| Command | Description | Example |
|---------|-------------|---------|
| `/commerce` | SFCC product search and integration | `/commerce Find rings under $500` |
| `/figma` | Extract design tokens from Figma | `/figma Extract color tokens from brand guidelines` |

**Product Management Agents:**

| Command | Description | Example |
|---------|-------------|---------|
| `/prd-to-jira` | Convert PRDs to Jira epics and stories | `/prd-to-jira [paste PRD content]` |
| `/exec-summary` | Generate executive summaries | `/exec-summary [paste sprint data]` |
| `/roadmap-review` | Critique roadmaps and OKRs | `/roadmap-review [paste roadmap]` |
| `/analytics` | Generate sprint reports and metrics | `/analytics Generate velocity report for last 6 sprints` |

For detailed documentation, see the [Slash Commands Runbook](https://pandoradigital.atlassian.net/wiki/spaces/~712020a796c84908ee48a8bc04950e7f6fb704/pages/5165351194/PND+Agents+Slash+Commands+-+Runbook).

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
├── src/                           # Source code (Python packages)
│   ├── pnd_agents/                # Main CLI package
│   │   ├── cli.py                 # Command-line interface
│   │   └── tools/                 # Compatibility shim for tools
│   ├── agents/                    # Agent implementations
│   │   ├── task_manager_agent/    # Task Manager (orchestrator)
│   │   ├── frontend/              # Frontend Engineer Agent
│   │   ├── figma_reader_agent/    # Figma Reader Agent
│   │   ├── amplience/             # Amplience CMS Agent
│   │   ├── code_review/           # Code Review Agent
│   │   ├── unit_test_agent/       # Unit Test Agent
│   │   ├── sonar_validation_agent/# Sonar Validation Agent
│   │   ├── qa_agent/              # QA Agent
│   │   ├── performance/           # Performance Agent
│   │   ├── backend/               # Backend Agent
│   │   ├── commerce_agent/        # Commerce Agent
│   │   ├── broken_experience_detector_agent/  # Broken Experience Detector
│   │   ├── analytics_agent/       # Analytics Agent
│   │   └── coding_standards.py    # Shared coding standards
│   ├── tools/                     # Core tools
│   │   ├── filesystem.py          # File system operations
│   │   ├── command_runner.py      # Command execution
│   │   ├── figma_parser.py        # Figma design parsing
│   │   ├── amplience_api.py       # Amplience CMS integration
│   │   ├── har_analyzer.py        # HAR file analysis
│   │   ├── jira_client.py         # Jira integration
│   │   ├── analytics_store.py     # Analytics storage
│   │   └── registry.py            # MCP tool registration
│   ├── config/                    # Configuration files
│   ├── mcp/                       # MCP server modules
│   └── plugins/                   # Claude plugins
│       └── unit-test-agent-plugin/# Unit test plugin for Claude Code
├── workflows/                     # Workflow definitions
│   ├── workflow_engine.py         # Workflow orchestration
│   ├── agent_dispatcher.py        # Agent dispatch logic
│   └── workflow_rules.json        # Workflow configuration
├── docs/                          # Documentation
│   ├── setup.md                   # Setup guide
│   ├── architecture.md            # Architecture overview
│   ├── claude-usage.md            # Claude usage guide
│   └── agents-overview.md         # Agent documentation
├── examples/                      # Example tasks
│   ├── create-component-from-figma.md
│   ├── create-amplience-content-type.md
│   └── performance-optimization.md
├── tests/                         # Test files
├── mcp-config/                    # MCP configuration templates
├── main.py                        # MCP server entry point
├── pyproject.toml                 # Python package configuration
├── requirements.txt               # Python dependencies
├── INSTALLATION.md                # Installation guide
└── .claude-plugin/                # Plugin marketplace config
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

The workflow engine automatically detects task types and orchestrates agents in a pipeline. When you give a task to the Task Manager, it analyzes the description, selects the appropriate workflow, and runs agents either sequentially or in parallel until completion.

### Execution Modes

The workflow engine supports two execution modes:

1. **Sequential Execution** (default): Agents run one after another, passing outputs between stages
2. **Parallel Execution**: Independent agents run simultaneously, improving performance for complex workflows

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
│                 PARALLEL WORKFLOW PIPELINE                      │
│                                                                 │
│  Group 1:  ┌──────────┐                                        │
│            │  Figma   │  (sequential)                          │
│            │  Reader  │                                        │
│            └──────────┘                                        │
│                 │                                               │
│  Group 2:  ┌──────────┐                                        │
│            │ Frontend │  (sequential)                          │
│            │ Engineer │                                        │
│            └──────────┘                                        │
│                 │                                               │
│  Group 3:  ┌──────────┐                                        │
│            │  Review  │  (sequential)                          │
│            │  Agent   │                                        │
│            └──────────┘                                        │
│                 │                                               │
│  Group 4:  ┌──────────┐   ┌──────────┐                        │
│            │Unit Test │ + │ Perform. │  (parallel)             │
│            │  Agent   │   │  Agent   │                        │
│            └──────────┘   └──────────┘                        │
│                 │                                               │
│  Group 5:  ┌──────────┐                                        │
│            │  Sonar   │  (sequential)                          │
│            │  Agent   │                                        │
│            └──────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 COMPREHENSIVE SUMMARY                           │
│  - Agents used, tasks executed, files changed                   │
│  - Errors encountered, recommendations                          │
│  - Execution trace with timestamps                              │
└─────────────────────────────────────────────────────────────────┘
```

### Cross-Agent Communication

Agents can communicate with each other during execution using the `call_agent` hook:

```python
def my_handler(context):
    call_agent = context.get("call_agent")
    if call_agent:
        sonar_result = call_agent("sonar", {"branch": "main"})
    return AgentResult(status="success", data={...})
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

# Run a task (sequential execution)
context = agent.run_task(
    "Create Stories carousel from Figma: https://figma.com/...",
    metadata={"ticket_id": "INS-2509"},
    verbose=True
)

# Run a task with parallel execution
context = agent.run_task_parallel(
    "Create Stories carousel from Figma: https://figma.com/...",
    metadata={"ticket_id": "INS-2509"},
    verbose=True,
    max_workers=4  # Maximum parallel agents
)

# Check status
print(f"Status: {context.status}")
for agent_name, stage in context.stages.items():
    print(f"  {agent_name}: {stage.status}")

# Get comprehensive summary
summary = context.get_summary()
print(f"Agents used: {summary['agents_used']}")
print(f"Files changed: {summary['files_changed']}")
print(f"Errors: {summary['errors']}")
print(f"Recommendations: {summary['recommendations']}")
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

## Analytics & Reporting Agent

The Analytics & Reporting Agent tracks metrics about agent performance, persists structured logs, updates JIRA issues, and generates reports. It provides MCP endpoints for Claude Desktop/Code integration.

### Features

- Tracks task events from all agents in the squad
- Persists structured metrics to JSON files in `/logs/agent-analytics/`
- Updates JIRA issues with AI agent metrics via Atlassian REST API v3
- Provides MCP commands for Claude integration
- Generates weekly/per-task dashboards and reports (JSON, Markdown, JIRA)

### Metrics Tracked

For each agent task:
- `aiUsed`: Always true
- `agentName`: Name of agent who completed task
- `taskName`: Summary of the task
- `startTime` / `endTime`: Timestamps
- `duration`: Calculated time difference
- `iterations`: How many attempts the agent made
- `errors`: Errors encountered
- `effectivenessScore`: Derived score based on retries & quality
- `requiresHumanReview`: True if code review agent flagged issues
- `confidenceScore`: Model confidence

### Usage

```python
from agents.analytics_agent import AnalyticsAgent, record_event

# Initialize the agent
agent = AnalyticsAgent()

# Track task start
agent.on_task_started(
    agent_name="Frontend Engineer Agent",
    task_description="Create Header Component",
    jira_task_id="EPA-123",
)

# Track task completion
agent.on_task_completed(
    agent_name="Frontend Engineer Agent",
    jira_task_id="EPA-123",
    metrics={
        "duration": 208000,
        "iterations": 4,
        "errors": [],
        "effectivenessScore": 92.0,
    },
)

# Generate reports
json_report = agent.generate_json_report(days=14)
md_report = agent.generate_markdown_report(days=14)
```

### Using the Convenience Function

Other agents can use the `record_event` function for lightweight tracking:

```python
from tools.analytics_store import record_event

record_event(
    event_type="task_started",
    agent_name="Code Review Agent",
    task_description="Review PR #42",
    jira_task_id="EPA-456",
)
```

### MCP Commands

The following MCP commands are available for Claude Desktop/Code:

| Command | Description |
|---------|-------------|
| `analytics_track_task_start` | Record the start of a task |
| `analytics_track_task_end` | Record task completion |
| `analytics_track_task_failure` | Record task failure |
| `analytics_update_jira_task` | Update JIRA with AI metrics |
| `analytics_generate_report` | Generate performance report |
| `analytics_list` | List stored analytics |
| `analytics_get_config` | Get current configuration |
| `analytics_update_config` | Update configuration |

### JIRA Integration

Each task completion can result in a JIRA comment:

```
🤖 AI Agent Update – PG AI Squad

Agent: Frontend Engineer Agent
Task: Implement Header Component from Figma
Status: Completed

Metrics:
- Duration: 3m 28s
- Iterations: 4
- Errors: 1 (auto-fixed)
- Effectiveness Score: 92%
- Human Review Required: No

AI Productivity Tracker Agent v1.0
```

### Environment Variables

```bash
export JIRA_BASE_URL="https://your-instance.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

### Configuration

Analytics configuration is stored in `config/analytics.config.json` and JIRA configuration in `config/jira.config.json`. See [examples/analytics/README.md](examples/analytics/README.md) for detailed configuration options.

### CLI Usage

```bash
# Generate analytics reports
python scripts/generate_report.py --format all --days 14 --output-dir ./reports
```

## Documentation

All documentation has been consolidated into the `/docs` folder for better organization:

- [Documentation Index](docs/index.md) - Complete documentation overview and navigation
- [Claude Usage Guide](docs/claude-usage.md) - Using agents with Claude without cloning the repo
- [Setup Guide](docs/setup.md) - Detailed installation and configuration
- [Architecture](docs/architecture.md) - System architecture and design decisions
- [Agents Overview](docs/agents-overview.md) - Complete list of all agents with capabilities
- [Quick Reference](docs/quick-reference.md) - One-page quick reference card
- [Publishing Guide](docs/publishing.md) - Publishing to Azure Artifacts
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
