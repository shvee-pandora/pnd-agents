# Code Singularity Demo

This demo shows how pnd-agents uses the **Code Singularity** pattern to operate repositories deterministically via `repo-profile.json`.

## What is Code Singularity?

Code Singularity is the moment when AI agents can run your codebase better than you can. It's achieved by creating an "agent interface layer" - machine-readable configuration that tells agents exactly how to operate a repository without guessing.

The key components are:

1. **repo-profile.json** - Machine-readable contract defining commands, paths, constraints, and quality gates
2. **Workflow YAMLs** - Declarative playbooks for common engineering tasks
3. **Agent Memory** - Durable storage for patterns, troubleshooting notes, and playbooks

## Quick Start

```bash
# From the pnd-agents directory
cd ~/repos/pnd-agents

# Run the demo against pandora-group (dry run - shows all info)
python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group

# Run a specific command
python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group --run-command validate

# Show available workflows
python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group --show-workflows
```

## What the Demo Shows

### Step 1: Load Repo Profile
Discovers and loads `.claude/repo-profile.json` from the target repository.

### Step 2: Available Commands
Shows all commands defined in the profile (install, validate, lint, test, build, etc.) with their actual values.

### Step 3: Resolved Paths
Shows key paths (components, atoms, content-mapping, etc.) resolved to absolute paths.

### Step 4: Coding Constraints
Shows TypeScript, React, and atomic design constraints that agents should follow.

### Step 5: Quality Gates
Shows SonarCloud configuration and required checks.

### Step 6: WorkflowEngine Integration
Demonstrates how `WorkflowEngine` injects repo context into workflow metadata, making it available to all agents.

## Example Output

```
============================================================
  STEP 1: Load Repo Profile
============================================================
Profile found: /home/ubuntu/repos/pandora-group/.claude/repo-profile.json

Repo: pandora-group
Description: Pandora Group corporate website built with Next.js 15, React 19, and TypeScript
Provider: azure_devops
Default branch: main

============================================================
  STEP 2: Available Commands
============================================================

Package manager: pnpm
Node version: 20

--- Commands from repo-profile.json ---
  install      -> pnpm install
  validate     -> pnpm validate
  lint         -> pnpm lint
  lint_fix     -> pnpm lint:fix
  typecheck    -> pnpm check-types
  test         -> pnpm test
  build        -> pnpm build

============================================================
  STEP 6: WorkflowEngine Integration
============================================================

Workflow ID: 9e6d022b
Task type detected: default
Pipeline: frontend -> review -> qa

--- Injected repo context (available to all agents) ---
  metadata['repo_name']: pandora-group
  metadata['repo_context']['commands']: ['install', 'validate', 'lint', ...]
  metadata['repo_context']['constraints']:
    - use_type_over_interface: True
    - server_components_default: True
    - atomic_levels: ['atoms', 'molecules', 'organisms']
```

## How It Works

```python
from src.agents.repo_profile import load_repo_profile
from src.agents.repo_adapter import RepoAdapter
from workflows.workflow_engine import WorkflowEngine

# 1. Load the repo profile
profile = load_repo_profile('/path/to/repo/.claude/repo-profile.json')

# 2. Create adapter (normalizes commands/paths)
adapter = RepoAdapter(profile=profile, repo_root='/path/to/repo')

# 3. Use adapter to get commands and paths
adapter.get_command('validate')      # Returns: "pnpm validate"
adapter.resolve_path('components')   # Returns: "/path/to/repo/lib/components"

# 4. Create WorkflowEngine with adapter
engine = WorkflowEngine(repo_adapter=adapter)
context = engine.create_workflow("Fix validate failures")

# 5. Agents can now access repo context via metadata
context.metadata['repo_context']['commands']['validate']  # "pnpm validate"
context.metadata['repo_context']['constraints']['use_type_over_interface']  # True

# 6. Run commands via adapter
result = adapter.run_command('validate')
print(f"Success: {result.success}")
```

## Benefits

1. **No more guessing** - Agents read the profile and know exactly what commands to run
2. **Consistent paths** - `resolve_path('atoms')` always returns the correct location
3. **Constraint awareness** - Agents know coding conventions (TypeScript strictness, naming rules, etc.)
4. **Deterministic workflows** - Same input = same behavior across different agents/sessions
5. **Multi-repo support** - Any repo with a `repo-profile.json` can be operated the same way

## Adding Code Singularity to Your Repo

To enable Code Singularity for a new repository:

1. Create `.claude/repo-profile.json` with your repo's commands, paths, and constraints
2. Optionally add `.claude/workflows/*.yaml` for common engineering tasks
3. Optionally create `.claude/memory/` for storing patterns and troubleshooting notes

See `pandora-group/.claude/repo-profile.json` for a complete example.

## Next Steps

1. **Wire agent handlers** - Update existing pnd-agents handlers to read `metadata['repo_context']`
2. **Add workflow executor** - Build a runner that parses `.claude/workflows/*.yaml`
3. **Expand memory** - Document patterns/troubleshooting in `.claude/memory/`
