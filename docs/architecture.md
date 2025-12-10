# Architecture

This document describes the architecture and design decisions of the PG AI Squad agent system.

## Overview

PG AI Squad follows a plugin-based architecture inspired by the [wshobson/agents](https://github.com/wshobson/agents) framework. The system is designed to be:

- **Modular**: Each agent is a self-contained unit with specific capabilities
- **Extensible**: New agents and tools can be added without modifying existing code
- **MCP-Compatible**: Agents can be loaded as Claude Desktop plugins via MCP
- **Standards-Compliant**: All generated code follows Pandora coding standards

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Desktop                            │
│                     (MCP Client Interface)                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ MCP Protocol
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PG AI Squad Server                          │
│                    (MCP Server Interface)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │    Task     │  │  Frontend   │  │  Amplience  │              │
│  │   Manager   │  │  Engineer   │  │    CMS      │              │
│  │    Agent    │  │    Agent    │  │    Agent    │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐              │
│  │    Code     │  │ Performance │  │     QA      │              │
│  │   Review    │  │    Agent    │  │    Agent    │              │
│  │    Agent    │  │             │  │             │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      Tools Layer                             ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       ││
│  │  │Filesystem│ │ Command  │ │  Figma   │ │Amplience │       ││
│  │  │   Tool   │ │  Runner  │ │  Parser  │ │   API    │       ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       ││
│  │                    ┌──────────┐                              ││
│  │                    │   HAR    │                              ││
│  │                    │ Analyzer │                              ││
│  │                    └──────────┘                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Architecture

Each agent follows a consistent structure:

```
agents/{agent_name}/
├── agents/
│   └── {agent-name}-agent.md    # Agent definition with capabilities
├── commands/
│   ├── command-1.md             # Command definitions
│   ├── command-2.md
│   └── command-3.md
└── skills/                      # Optional skills directory
    └── skill-name/
        ├── metadata.md
        ├── instructions.md
        └── resources/
```

### Agent Definition

Agent definitions use markdown with YAML frontmatter:

```markdown
---
name: frontend-engineer-agent
description: Specialized in React/Next.js component development
model: sonnet
---

# Frontend Engineer Agent

## Capabilities
- Figma design parsing
- React component generation
- Storybook story creation
- Accessibility validation

## Commands
- component-generate
- story-create
- accessibility-validate
```

### Command Definition

Commands define specific actions an agent can perform:

```markdown
---
name: component-generate
description: Generate React components from Figma designs
---

# Component Generate

## Context
This command generates React/Next.js components following Pandora UI Toolkit patterns.

## Requirements
- Figma design or component specification
- Target atomic design level

## Workflow
1. Analyze design
2. Determine component structure
3. Generate TypeScript code
4. Create types and exports

## Example
...
```

## Tools Architecture

Tools provide the "Effects" system for agents to interact with external systems:

### Filesystem Tool

```python
class FilesystemTool:
    """File system operations with path validation."""
    
    def read_file(self, path: str) -> str
    def write_file(self, path: str, content: str) -> str
    def list_directory(self, path: str) -> List[FileInfo]
    def exists(self, path: str) -> bool
```

### Command Runner

```python
class CommandRunner:
    """Safe command execution with timeout handling."""
    
    def run(self, command: str) -> CommandResult
    def run_eslint(self, paths: List[str]) -> CommandResult
    def run_typescript(self) -> CommandResult
    def run_jest(self, paths: List[str]) -> CommandResult
```

### Figma Parser

```python
class FigmaParser:
    """Parse Figma designs to extract component information."""
    
    def parse_file(self, path: str) -> List[FigmaComponent]
    def extract_colors(self) -> Dict[str, Color]
    def extract_typography(self) -> Dict[str, Typography]
    def get_design_tokens(self) -> DesignTokens
```

### Amplience API

```python
class AmplienceAPI:
    """Amplience CMS integration."""
    
    def fetch_by_id(self, content_id: str) -> ContentItem
    def fetch_by_key(self, delivery_key: str) -> ContentItem
    def fetch_by_filter(self, filters: List[FilterCriteria]) -> List[ContentItem]
    def build_image_url(self, image: Dict, width: int) -> str
```

### HAR Analyzer

```python
class HARAnalyzer:
    """HTTP Archive file analysis for performance optimization."""
    
    def parse_file(self, path: str) -> HARAnalysisReport
    def to_markdown_report(self, report: HARAnalysisReport) -> str
```

## MCP Integration

The system integrates with Claude Desktop via the Model Context Protocol (MCP):

### Configuration

```json
{
  "mcpServers": {
    "pg-ai-squad": {
      "command": "python",
      "args": ["-m", "pnd_agents.server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

### Agent Registration

Agents are registered in the marketplace configuration:

```json
{
  "plugins": [
    {
      "name": "task-manager",
      "source": "./agents/task_manager",
      "commands": ["./commands/task-decompose.md"],
      "agents": ["./agents/task-manager-agent.md"]
    }
  ]
}
```

## Workflow Patterns

### Task Decomposition

```
User Request
    │
    ▼
Task Manager Agent
    │
    ├── Analyze request
    ├── Identify required agents
    ├── Create subtasks
    │
    ▼
Subtask Distribution
    │
    ├── Frontend Engineer → Component generation
    ├── Amplience CMS → Schema creation
    ├── QA Agent → Test generation
    │
    ▼
Output Collection
    │
    ▼
Task Manager Agent
    │
    ├── Merge outputs
    ├── Validate completeness
    │
    ▼
Final Deliverable
```

### Agent Communication

Agents communicate through structured outputs:

```typescript
interface AgentOutput {
  agent: string;
  command: string;
  status: 'success' | 'failure';
  output: {
    files?: FileOutput[];
    report?: string;
    errors?: string[];
  };
}
```

## Design Decisions

### Why Markdown-Based Definitions?

1. **Human Readable**: Easy to understand and modify
2. **Version Control Friendly**: Clear diffs in git
3. **Documentation as Code**: Definitions serve as documentation
4. **Flexible**: YAML frontmatter for structured data, markdown for content

### Why Python Tools?

1. **Rich Ecosystem**: Extensive libraries for file handling, HTTP, parsing
2. **Type Safety**: Type hints with dataclasses
3. **Cross-Platform**: Works on all major operating systems
4. **MCP Compatibility**: Easy to expose as MCP tools

### Why Separate Agents?

1. **Single Responsibility**: Each agent has a focused purpose
2. **Parallel Execution**: Independent agents can run concurrently
3. **Maintainability**: Changes to one agent don't affect others
4. **Testability**: Agents can be tested in isolation

## Pandora Standards Integration

All agents enforce Pandora coding standards:

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

### ESLint Rules

- `@typescript-eslint/strict-type-checked`
- `eslint-plugin-jsx-a11y`
- `eslint-plugin-security`
- `eslint-plugin-sonarjs`

### Atomic Design

```
lib/components/
├── atoms/       # Basic building blocks
├── molecules/   # Simple composites
├── organisms/   # Complex components
└── templates/   # Page layouts
```

### Amplience Patterns

- Global partials for reusable schemas
- Content hierarchies for navigation
- VSE support for preview mode
- Dynamic Media for image optimization

## Future Enhancements

1. **Agent Memory**: Persistent context across sessions
2. **Learning**: Improve from feedback and corrections
3. **Parallel Execution**: Run multiple agents simultaneously
4. **Custom Tools**: Plugin system for additional tools
5. **Metrics**: Track agent performance and usage
