# PND Agents Usage Guide

This comprehensive guide explains all the different ways to use PND Agents (PG AI Squad) for your development workflow. Whether you prefer natural language prompts, slash commands, CLI tools, or programmatic integration, this guide covers each method step by step.

## Table of Contents

1. [Overview of Usage Methods](#overview-of-usage-methods)
2. [Method 1: MCP Integration with Claude Desktop/Code](#method-1-mcp-integration-with-claude-desktopcode)
3. [Method 2: Slash Commands in Claude Code](#method-2-slash-commands-in-claude-code)
4. [Method 3: Command Line Interface (CLI)](#method-3-command-line-interface-cli)
5. [Method 4: Python API (Programmatic Usage)](#method-4-python-api-programmatic-usage)
6. [Method 5: MCP Tools Direct Invocation](#method-5-mcp-tools-direct-invocation)
7. [Workflow Examples](#workflow-examples)
8. [Troubleshooting](#troubleshooting)

## Overview of Usage Methods

PND Agents provides five distinct ways to interact with the AI agents:

| Method | Best For | Prerequisites |
|--------|----------|---------------|
| **MCP Integration** | Natural language conversations with Claude | Claude Desktop/Code + MCP config |
| **Slash Commands** | Quick agent invocation in Claude Code | Claude Code + `.claude/agents/` |
| **CLI** | Terminal-based workflows, CI/CD | Python 3.10+, pip install |
| **Python API** | Custom integrations, scripts | Python 3.10+, pip install |
| **MCP Tools** | Direct tool calls from Claude | MCP server running |

## Method 1: MCP Integration with Claude Desktop/Code

This is the recommended method for most users. It provides a seamless conversational experience where Claude automatically has access to all PND agents.

### Step 1: Install PND Agents

```bash
# Option A: Install directly from GitHub
pip install git+https://github.com/shvee-pandora/pnd-agents.git

# Option B: Clone and install locally
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents
pip install -e .

# Install Playwright browsers (required for Broken Experience Detector)
playwright install
```

### Step 2: Run the Setup Wizard

```bash
pnd-agents setup
```

The setup wizard will:
1. Let you choose which agents to enable
2. Prompt for environment variables (Figma token, etc.)
3. Automatically update your Claude configuration

Alternatively, use preset configurations:
```bash
pnd-agents setup --preset default    # Recommended agents
pnd-agents setup --preset full       # All agents enabled
pnd-agents setup --preset minimal    # Only essential agents
```

### Step 3: Restart Claude Desktop/Code

After setup, restart Claude Desktop or Claude Code to load the new MCP configuration.

### Step 4: Start Using Agents

In a new Claude conversation, you can now use natural language to invoke agents:

**Example prompts:**

```
Create a React component from this Figma design:
https://www.figma.com/design/ABC123/My-Design?node-id=123-456
```

```
Write unit tests for src/components/Button/Button.tsx with 100% coverage
```

```
Validate my code in the feature/new-header branch against SonarCloud quality gates
```

```
Find a silver bracelet under 700 DKK
```

### How It Works

When you send a message to Claude:
1. Claude analyzes your request
2. The Task Manager Agent detects the task type (figma, frontend, backend, etc.)
3. A pipeline of agents is automatically orchestrated
4. Results are returned in a comprehensive summary

## Method 2: Slash Commands in Claude Code

Slash commands provide quick access to specific agents directly in Claude Code.

### Step 1: Ensure PND Agents is Installed

Follow the installation steps from Method 1.

### Step 2: Verify Slash Command Agents

The following agents are available as slash commands (defined in `.claude/agents/`):

| Slash Command | Agent | Description |
|---------------|-------|-------------|
| `/task-manager` | Task Manager | Orchestrates complex tasks, coordinates multiple agents |
| `/unit-test` | Unit Test Agent | Generates comprehensive unit tests with 100% coverage |
| `/qa` | QA Agent | Validates implementation against test cases |

### Step 3: Using Slash Commands

In Claude Code, type `/` followed by the agent name:

**Task Manager Agent:**
```
/task-manager Create a Stories carousel component from Figma: https://figma.com/...
```

**Unit Test Agent:**
```
/unit-test Generate tests for src/components/Header/Header.tsx
```

**QA Agent:**
```
/qa Validate the implementation against these acceptance criteria:
- User can click the button
- Button shows loading state
- Error messages display correctly
```

### Step 4: Using Skills (Auto-Activated)

Skills in `.claude/skills/` activate automatically based on keywords:

**Unit Test Generation Skill** - Activates when you mention:
- "unit tests", "test", "coverage", "jest", "vitest"

**QA Validation Skill** - Activates when you mention:
- "validate", "verify", "check", "QA", "acceptance criteria"

Example (skill auto-activates):
```
Write tests for the formatPrice utility function with 100% branch coverage
```

## Method 3: Command Line Interface (CLI)

The CLI provides direct terminal access to agents without requiring Claude.

### Step 1: Install PND Agents

```bash
pip install git+https://github.com/shvee-pandora/pnd-agents.git
```

### Step 2: Verify Installation

```bash
pnd-agents status
# Or use module fallback:
python -m pnd_agents status
```

### Step 3: Available CLI Commands

**Check Status:**
```bash
pnd-agents status
```

**Analyze a Task (without executing):**
```bash
pnd-agents analyze-task "Create a React component for product cards"
```

This shows:
- Detected task type
- Pipeline that would be used
- Agents that would be involved

**Run a Task:**
```bash
pnd-agents run-task "Create a React component for product cards"
```

**Run with Ticket ID and Branch:**
```bash
pnd-agents run-task "Build header component" --ticket INS-2509 --branch feature/header
```

**Show Plan Only (dry run):**
```bash
pnd-agents run-task "Create API endpoint" --plan-only
```

**Save Output to File:**
```bash
pnd-agents run-task "Build header component" --output /tmp/workflow-result.json
```

### Step 4: Configuration Commands

**View Current Configuration:**
```bash
pnd-agents config --show
```

**Reconfigure Agents:**
```bash
pnd-agents config --agents
```

**Update Environment Variables:**
```bash
pnd-agents config --env
```

**Uninstall from Claude Config:**
```bash
pnd-agents uninstall
```

### CLI Command Reference

| Command | Description |
|---------|-------------|
| `pnd-agents status` | Check installation and configuration status |
| `pnd-agents setup` | Run the interactive setup wizard |
| `pnd-agents analyze-task "..."` | Analyze a task and show the workflow plan |
| `pnd-agents run-task "..."` | Execute a task through the workflow engine |
| `pnd-agents config --show` | View current configuration |
| `pnd-agents config --agents` | Reconfigure which agents are enabled |
| `pnd-agents config --env` | Reconfigure environment variables |
| `pnd-agents uninstall` | Remove from Claude config |

## Method 4: Python API (Programmatic Usage)

For custom integrations, scripts, or CI/CD pipelines, use the Python API directly.

### Step 1: Install PND Agents

```bash
pip install git+https://github.com/shvee-pandora/pnd-agents.git
```

### Step 2: Using Individual Tools

```python
from tools import FilesystemTool, CommandRunner, FigmaParser, AmplienceAPI, HARAnalyzer

# Filesystem operations
fs = FilesystemTool()
content = fs.read_file('path/to/file.tsx')
fs.write_file('path/to/output.tsx', generated_code)

# Run development commands
runner = CommandRunner()
result = runner.run_eslint(['src/'])
test_result = runner.run_tests(coverage=True)

# Parse Figma designs
parser = FigmaParser()
components = parser.parse_file('design.json')
colors = parser.extract_colors('design.json')

# Interact with Amplience CMS
api = AmplienceAPI()
content = api.fetch_by_key('homepage-hero')
content_by_id = api.fetch_by_id('content-id-123')

# Analyze HAR files for performance
analyzer = HARAnalyzer()
report = analyzer.parse_file('performance.har')
metrics = analyzer.get_performance_metrics('performance.har')
```

### Step 3: Using the Task Manager Agent

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

# Resume an interrupted task
context = agent.resume_task(verbose=True)
```

### Step 4: Using Individual Agents

**Unit Test Agent:**
```python
from agents.unit_test_agent import UnitTestAgent

agent = UnitTestAgent()

# Analyze a source file
analysis = agent.analyze_file('src/components/Button.tsx')
print(f"Functions: {analysis.functions}")
print(f"Components: {analysis.components}")
print(f"Branches: {analysis.branches}")

# Generate test cases
test_cases = agent.generate_test_cases(analysis)

# Generate test file
test_file = agent.generate_test_file(test_cases)
print(test_file.content)
```

**Sonar Validation Agent:**
```python
from agents.sonar_validation_agent import SonarValidationAgent

agent = SonarValidationAgent()

# Get pre-generation warnings
warnings = agent.get_pre_generation_warnings('pandora-group')
for warning in warnings:
    print(f"DO: {warning.do_message}")
    print(f"DON'T: {warning.dont_message}")

# Validate generated code
result = agent.validate_generated_code(code, 'pandora-group')
if result.has_issues:
    print(f"Issues found: {result.issues}")

# Fetch project status from SonarCloud
status = agent.fetch_project_status(branch='main')
print(f"Quality Gate: {status.quality_gate}")

# Generate fix plans for issues
issues = agent.fetch_issues(branch='main')
fix_plans = agent.generate_fix_plan(issues)
```

**Figma Reader Agent:**
```python
from agents.figma_reader_agent import FigmaReaderAgent

agent = FigmaReaderAgent()

# Read a Figma design
result = agent.read_figma(
    url_or_file_key='https://www.figma.com/design/ABC123/My-Design?node-id=123-456'
)
print(f"Components: {result['components']}")
print(f"Design Tokens: {result['design_tokens']}")
```

**Commerce Agent:**
```python
from agents.commerce_agent import CommerceAgent

agent = CommerceAgent()

# Find products matching a goal
result = agent.find_product_and_prepare_cart("silver bracelet under 700 DKK")
print(f"Product: {result['name']}")
print(f"Price: {result['price']} {result['currency']}")
```

## Method 5: MCP Tools Direct Invocation

When Claude has access to the MCP server, you can directly invoke specific tools.

### Available MCP Tools

**Filesystem Tools:**
- `fs_read_file` - Read file contents
- `fs_write_file` - Write content to file
- `fs_list_directory` - List directory contents
- `fs_read_json` - Read and parse JSON file
- `fs_write_json` - Write data to JSON file

**Command Runner Tools:**
- `cmd_run` - Run shell command
- `cmd_run_eslint` - Run ESLint
- `cmd_run_prettier` - Run Prettier
- `cmd_run_tests` - Run test suite

**Figma Tools:**
- `figma_parse_file` - Parse Figma JSON export
- `figma_extract_colors` - Extract color palette
- `figma_read` - Read Figma via API (requires token)

**Amplience Tools:**
- `amplience_fetch_by_key` - Fetch content by delivery key
- `amplience_fetch_by_id` - Fetch content by ID

**HAR Analyzer Tools:**
- `har_parse_file` - Parse HAR file
- `har_get_performance_metrics` - Extract performance metrics

**Agent Tools:**
- `unit_test_generate` - Generate unit tests
- `unit_test_analyze` - Analyze source file for testable elements
- `qa_validate` - Validate against test cases
- `sonar_validate` - Validate against SonarCloud quality gates
- `sonar_get_issues` - Fetch SonarCloud issues
- `sonar_get_coverage` - Fetch coverage metrics
- `sonar_get_quality_gate` - Fetch quality gate status
- `sonar_validate_for_pr` - Validate for PR readiness
- `commerce_find_product_and_prepare_cart` - Find products
- `broken_experience_detector_scan_site` - Scan website for issues

### Example: Direct Tool Invocation in Claude

```
Use the unit_test_generate tool to create tests for src/utils/formatPrice.ts
```

```
Use sonar_get_issues to fetch all BLOCKER and CRITICAL issues from the main branch
```

```
Use broken_experience_detector_scan_site to scan https://us.pandora.net
```

## Workflow Examples

### Example 1: Create Component from Figma (Full Workflow)

**Using Natural Language:**
```
Create a Stories carousel component from this Figma design:
https://www.figma.com/design/ABC123/My-Design?node-id=123-456

Include:
- React component with TypeScript
- Storybook story
- Unit tests with 100% coverage
- Accessibility validation
```

**What Happens:**
1. Task Manager detects "figma" workflow
2. Figma Reader extracts design metadata
3. Frontend Engineer generates React component
4. Unit Test Agent generates tests
5. Code Review validates against standards
6. Sonar Validation checks quality gates
7. Performance Agent analyzes for optimizations

### Example 2: Generate Tests for Existing Code

**Using Slash Command:**
```
/unit-test Generate comprehensive tests for src/components/ProductCard/ProductCard.tsx
```

**Using CLI:**
```bash
pnd-agents run-task "Write unit tests for src/components/ProductCard/ProductCard.tsx with 100% coverage"
```

**Using Python API:**
```python
from agents.unit_test_agent import UnitTestAgent

agent = UnitTestAgent()
analysis = agent.analyze_file('src/components/ProductCard/ProductCard.tsx')
test_cases = agent.generate_test_cases(analysis)
test_file = agent.generate_test_file(test_cases)

# Write the test file
with open('src/components/ProductCard/ProductCard.test.tsx', 'w') as f:
    f.write(test_file.content)
```

### Example 3: Pre-PR Quality Validation

**Using Natural Language:**
```
Validate my code in the feature/new-header branch against SonarCloud quality gates
before I create a PR. Generate a checklist of issues to fix.
```

**Using CLI:**
```bash
pnd-agents run-task "Validate feature/new-header branch for PR readiness"
```

**Using Python API:**
```python
from agents.sonar_validation_agent import validate_for_pr

result = validate_for_pr(branch='feature/new-header')
print(result['checklist'])
print(f"Ready for PR: {result['ready']}")
```

### Example 4: Performance Analysis

**Using Natural Language:**
```
Analyze this HAR file and suggest performance optimizations:
/path/to/performance.har
```

**Using Python API:**
```python
from tools import HARAnalyzer

analyzer = HARAnalyzer()
report = analyzer.parse_file('performance.har')
print(report.to_markdown())
```

### Example 5: Agentic Commerce

**Using Natural Language:**
```
Find gold earrings under 1000 EUR and prepare cart metadata
```

**Using MCP Tool:**
```
Use commerce_find_product_and_prepare_cart with goal "gold earrings under 1000 EUR"
```

## Troubleshooting

### "pnd-agents: command not found"

**Solution 1:** Use the module fallback
```bash
python -m pnd_agents status
```

**Solution 2:** Add Python bin to PATH (macOS)
```bash
echo 'export PATH="$HOME/Library/Python/3.12/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Solution 3:** Reinstall the package
```bash
pip uninstall pnd-agents -y
pip install git+https://github.com/shvee-pandora/pnd-agents.git
```

### Agents Not Available in Claude

1. Verify the config file exists at the correct location:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.claude.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Ensure JSON syntax is valid

3. Restart Claude Desktop/Code completely

4. Run setup again: `pnd-agents setup`

### Figma API Errors

1. Verify `FIGMA_ACCESS_TOKEN` is set correctly
2. Check token hasn't expired
3. Verify token has read access to the file
4. Use correct URL format: `https://www.figma.com/design/ABC123/My-Design?node-id=123-456`

### SonarCloud API Errors

1. Verify `SONAR_TOKEN` is set correctly
2. Check token has "Analyze Projects" permission
3. The agent works without a token for basic validation

## Environment Variables Reference

| Variable | Required | Purpose |
|----------|----------|---------|
| `FIGMA_ACCESS_TOKEN` | For Figma integration | Figma API authentication |
| `AMPLIENCE_HUB_NAME` | For Amplience integration | Amplience hub identifier |
| `AMPLIENCE_BASE_URL` | For Amplience integration | Amplience CDN base URL |
| `SONAR_TOKEN` | Optional | SonarCloud API access |
| `SFCC_OCAPI_INSTANCE` | For Commerce (live) | Salesforce Commerce Cloud instance |
| `SFCC_CLIENT_ID` | For Commerce (live) | SFCC client ID |
| `SFCC_SITE_ID` | For Commerce (live) | SFCC site identifier |

## Next Steps

1. Choose the usage method that best fits your workflow
2. Run `pnd-agents setup` to configure your environment
3. Try the example prompts to get familiar with the agents
4. Explore the [Architecture Guide](architecture.md) for deeper understanding
5. Check [Claude Usage Guide](claude-usage.md) for more Claude-specific tips
