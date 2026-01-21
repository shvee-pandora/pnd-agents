# Architecture

This document describes the architecture and design decisions of the Pandora AI Squad agent system.

## Overview

Pandora AI Squad follows a plugin-based architecture inspired by the [wshobson/agents](https://github.com/wshobson/agents) framework. The system is designed to be:

- **Modular**: Each agent is a self-contained unit with specific capabilities
- **Extensible**: New agents and tools can be added without modifying existing code
- **MCP-Compatible**: Agents can be loaded as Claude Desktop plugins via MCP
- **Standards-Compliant**: All generated code follows Pandora coding standards
- **Universal**: Most agents work with any JavaScript/TypeScript framework via Context7 integration

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
│                   Pandora AI Squad Server                        │
│                    (MCP Server Interface)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Universal Agents                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │  Task    │ │ Frontend │ │  Code    │ │   Unit   │     │  │
│  │  │ Manager  │ │ Engineer │ │  Review  │ │   Test   │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │ Backend  │ │  Sonar   │ │   QA     │ │ PR Review│     │  │
│  │  │ Engineer │ │Validation│ │  Agent   │ │  Agent   │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │Performance│ │  Figma  │ │ PRD to   │ │Analytics │     │  │
│  │  │ Analyzer │ │  Reader │ │  Jira    │ │  Agent   │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Platform Agents                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │  │
│  │  │ Commerce │ │Amplience │ │Amplience │                   │  │
│  │  │  Agent   │ │   CMS    │ │Placement │                   │  │
│  │  └──────────┘ └──────────┘ └──────────┘                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      Tools Layer                           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │Filesystem│ │ Command  │ │  Figma   │ │Amplience │     │  │
│  │  │   Tool   │ │  Runner  │ │  Parser  │ │   API    │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │   HAR    │ │  Sonar   │ │   JIRA   │ │  Azure   │     │  │
│  │  │ Analyzer │ │  Client  │ │  Client  │ │  DevOps  │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

The agent system uses a categorized directory structure that separates universal agents from platform-specific ones:

```
src/agents/
├── core/                              # Shared infrastructure
│   ├── __init__.py
│   ├── base_agent.py                  # Abstract base class
│   ├── coding_standards.py            # Pandora coding standards
│   ├── repo_adapter.py                # Cross-repo utilities
│   ├── repo_profile.py                # Repository detection
│   ├── clients/                       # External service clients
│   │   ├── sonar_client.py            # SonarCloud API client
│   │   ├── azure_devops_client.py     # Azure DevOps client
│   │   ├── jira_client.py             # JIRA API client
│   │   └── figma_client.py            # Figma API client
│   └── analyzers/                     # Shared analysis utilities
│       ├── coverage_analyzer.py       # Code coverage analysis
│       ├── tech_stack_detector.py     # Technology detection
│       └── pattern_matcher.py         # Regex pattern matching
│
├── universal/                         # Framework-agnostic agents
│   ├── orchestration/
│   │   └── task_manager/              # Task orchestration
│   ├── development/
│   │   ├── frontend/                  # React/Next.js components
│   │   ├── backend/                   # API routes, Server Components
│   │   └── figma_reader/              # Figma design extraction
│   ├── quality/
│   │   ├── code_review/               # Code standards validation
│   │   ├── unit_test/                 # Test generation
│   │   ├── qa/                        # E2E and integration tests
│   │   ├── sonar_validation/          # SonarCloud quality gates
│   │   ├── pr_review/                 # PR review automation
│   │   └── technical_debt/            # Tech debt analysis
│   ├── performance/
│   │   ├── performance_analyzer/      # HAR analysis, Core Web Vitals
│   │   └── broken_experience_detector/ # UX issue detection
│   ├── product_management/
│   │   ├── prd_to_jira/               # PRD to JIRA conversion
│   │   ├── exec_summary/              # Executive summaries
│   │   └── roadmap_review/            # Roadmap analysis
│   └── analytics/
│       └── analytics/                 # Task tracking and metrics
│
└── platform/                          # Platform-specific agents
    ├── commerce/                      # Pandora Commerce (SFCC)
    ├── amplience_cms/                 # Amplience CMS
    └── amplience_placement/           # Amplience module mapping
```

## Agent Architecture

Each agent follows a consistent structure based on its type:

### Markdown-Based Agents (Slash Command Agents)

```
{agent_name}/
├── agents/
│   └── {agent-name}-agent.md    # Agent definition with capabilities
├── commands/
│   ├── command-1.md             # Command definitions
│   └── command-2.md
└── skills/                      # Optional skills directory
    └── skill-name/
        ├── metadata.md
        └── instructions.md
```

### Python Module Agents

```
{agent_name}/
├── __init__.py
├── agent.py                     # Main agent implementation
├── models.py                    # Data models (optional)
└── utils.py                     # Utility functions (optional)
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
    "pnd-agents": {
      "command": "pnd-agents",
      "args": ["serve"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "your-figma-token",
        "JIRA_BASE_URL": "https://your-org.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-jira-token"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### Context7 Integration (Optional)

The Code Review Agent can optionally use Context7 MCP to fetch the latest coding standards for any JavaScript/TypeScript framework. When Context7 is configured, the agent uses a standards hierarchy:

1. **Pandora Standards** (from `coding_standards.py`) - ALWAYS enforced, highest priority
2. **Context7 Framework Standards** - Latest best practices for detected framework
3. **Universal JS/TS Standards** - General best practices (fallback)

If Context7 is not available, the agent falls back to Pandora standards and built-in framework knowledge.

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
