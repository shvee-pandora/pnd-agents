# PND Meta-Agent

A Mastra-based Agent Factory that generates pnd-agents compatible agent packages through a guided CLI interview process.

## Overview

The Meta-Agent solves a common problem: creating new agents is manual and error-prone. Everyone hand-rolls structure, metadata, permissions, and docs differently, leading to inconsistent implementations and review friction.

This tool provides a guided interview that produces a complete, pluggable agent package with explicit manifests and enforceable permissions.

## Features

- **Guided CLI Interview**: Collects agent specifications through interactive prompts
- **Complete Package Generation**: Creates 6 files per agent
- **Safety Constraints**: Read-only agents cannot use write tools (enforced at generation and runtime)
- **9 Available Tools**: filesystem_read/write, test_runner, coverage_analyzer, code_parser, git_operations, http_client, database_query, command_runner

## Installation

```bash
cd meta-agent
npm install
```

## Quick Start

### Generate Demo Agent (Recommended First Step)

```bash
npm run generate-demo
```

This generates a **Read-Only Unit Test Advisor Agent** in `generated-agents/unit_test_advisor/`.

### Create Custom Agent via Interview

```bash
npm run interview
```

The CLI will guide you through:

1. **Agent name** (snake_case, e.g., `code_analyzer`)
2. **Display name** (e.g., "Code Analyzer")
3. **Brief description**
4. **Single responsibility** (what the agent does)
5. **Permission level**: `read_only` or `read_write`
6. **Tools to use** (select from available tools)
7. **Memory enabled** (yes/no)
8. **Execution environment** (local/ci/both)
9. **Output format** (report/suggestions/structured_data/markdown)

## Generated Files

Each agent package includes:

| File | Description |
|------|-------------|
| `agent.py` | Python agent with `run(context)` method |
| `manifest.json` | Agent metadata and capabilities |
| `permissions.json` | Enforced safety constraints |
| `tools.json` | Tool definitions and schemas |
| `README.md` | Auto-generated documentation |
| `__init__.py` | Package initialization |

## Available Tools

### Read-Only Tools
- `filesystem_read` - Read files from the filesystem
- `test_runner` - Run test suites (Jest, Vitest, Playwright)
- `coverage_analyzer` - Analyze test coverage reports
- `code_parser` - Parse and analyze source code
- `http_client` - Make HTTP requests to external APIs
- `database_query` - Query databases (SELECT only)

### Read-Write Tools
- `filesystem_write` - Write files to the filesystem
- `git_operations` - Perform git operations (commit, push, branch)
- `command_runner` - Run shell commands

**Note**: Read-only agents can only select read-only tools. This is enforced during the interview and at runtime.

## Using Generated Agents

### As a Standalone Agent

```python
from unit_test_advisor import UnitTestAdvisorAgent

agent = UnitTestAdvisorAgent()
result = agent.run({
    "task_description": "Analyze test coverage for src/components",
    "input_data": {
        "path": "./src/components",
        "run_tests": True,
        "coverage_path": "coverage/coverage-summary.json"
    }
})

print(result.to_dict())
```

### Integrating with pnd-agents

1. Copy the generated agent folder to `src/agents/`
2. Register the agent in `workflows/agent_dispatcher.py`
3. Add to workflow rules if needed

```python
# In agent_dispatcher.py
from src.agents.unit_test_advisor import UnitTestAdvisorAgent

dispatcher.register("unit_test_advisor", unit_test_advisor_handler)
```

## Demo Script for Team Presentations

### Opening Story (60 seconds)

> "Today I'm showing you an Agent Factory. In pnd-agents, we have a runtime and orchestration layer, but creating a new agent is still manual and error-prone. Everyone hand-rolls structure, metadata, permissions, and docs differently. This leads to inconsistent implementations, unclear capabilities, and review friction—especially around safety constraints.
>
> The Meta-Agent solves this: a guided interview produces a complete, pluggable agent package with explicit manifests and enforceable permissions. Our demo use case is a Unit Test Advisor that can analyze tests and coverage but is guaranteed not to modify code."

### Live Demo Steps

**Step 1: Show what you're producing (30s)**

> "An agent package isn't just code. It's 6 files: agent.py, manifest.json, permissions.json, tools.json, README.md, and __init__.py"

**Step 2: Quick win - one command (2 min)**

```bash
cd pnd-agents/meta-agent
npm install
npm run generate-demo
```

> "This generates a read-only Unit Test Advisor agent in generated-agents/unit_test_advisor/"

**Step 3: Review the generated files (3-4 min)**

Open and highlight:

- `manifest.json`: "Agent identity + capabilities: name, permission level, allowed tools, inputs/outputs"
- `permissions.json`: "The safety contract: canModifyFiles: false, canExecuteCommands: false. Explicit allowed vs denied operations"
- `agent.py`: "The implementation with run(context) method and runtime permission validation"

**Step 4: Verify it works (1 min)**

```bash
python3 -m py_compile generated-agents/unit_test_advisor/agent.py
```

> "Valid Python, ready to integrate"

**Step 5: Show the interview (3-4 min)**

```bash
npm run interview
```

Walk through creating a custom agent, narrating each question.

**Step 6: Close (1 min)**

> "Benefits: Faster creation (minutes not hours), consistent structure, safer by default, easier onboarding"

## Safety Model

### Permission Levels

| Level | Can Modify Files | Can Execute Commands | Can Modify Git |
|-------|------------------|---------------------|----------------|
| `read_only` | No | No | No |
| `read_write` | Yes | Yes | Yes |

### Runtime Enforcement

Generated agents include runtime validation:

```python
def _validate_permissions(self):
    """Validate that the agent's permissions are correctly configured."""
    if self.IS_READ_ONLY:
        write_tools = ["filesystem_write", "git_operations", "command_runner"]
        for tool in self.ALLOWED_TOOLS:
            if tool in write_tools:
                raise ValueError(f"Read-only agent cannot use write tool: {tool}")
```

## Project Structure

```
meta-agent/
├── src/
│   ├── agents/
│   │   └── meta-agent.ts      # Mastra agent definition
│   ├── cli.ts                 # CLI interview interface
│   ├── index.ts               # Main exports
│   ├── templates/             # Code generation templates
│   │   ├── agent-py.ts        # Python agent template
│   │   ├── manifest-json.ts   # Manifest template
│   │   ├── permissions-json.ts # Permissions template
│   │   ├── tools-json.ts      # Tools template
│   │   └── readme-md.ts       # README template
│   ├── tools/                 # Mastra tools
│   │   ├── validate-config.ts # Config validation
│   │   └── generate-agent.ts  # Agent generation
│   └── types/                 # TypeScript types
│       └── agent-config.ts    # Agent config schema
├── package.json
├── tsconfig.json
└── README.md
```

## Development

### Run Lint Checks

```bash
npm run lint
```

### Build

```bash
npm run build
```

## Troubleshooting

### "Invalid name" error during interview

Agent names must be in snake_case format (lowercase letters, numbers, and underscores only). Example: `unit_test_advisor`, `code_analyzer_v2`

### Generated Python has syntax errors

Run `npm run lint` to ensure the TypeScript compiles correctly, then regenerate the agent.

### Read-only agent shows write tools

This shouldn't happen - the CLI filters tools based on permission level. If you see this, please report it as a bug.

## License

MIT
