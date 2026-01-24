# How Agents Work

This document provides a low-level explanation of how agents work in the Pandora AI Squad system, including their internal architecture, execution flow, standards workflow, and integration with external services.

## Agent Architecture Overview

Each agent in the Pandora AI Squad follows a consistent architecture pattern that enables modularity, testability, and extensibility.

### Agent Types

The system has two types of agents based on their implementation:

**1. Markdown-Based Agents (Slash Command Agents)**
These agents are defined entirely in markdown files and provide instructions to Claude. They don't execute code directly but guide Claude's behavior.

```
src/agents/{agent_name}/
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

Examples: frontend, backend, code_review, performance, amplience

**2. Python Module Agents**
These agents are implemented as Python modules with executable code that can be called programmatically or via MCP tools.

```
src/agents/{agent_name}/
├── __init__.py
├── agent.py                     # Main agent implementation
├── models.py                    # Data models (optional)
└── utils.py                     # Utility functions (optional)
```

Examples: task_manager_agent, unit_test_agent, sonar_validation_agent, commerce_agent

## Agent Definition Structure

### Markdown Agent Definition

Agent definitions use markdown with YAML frontmatter:

```markdown
---
name: code-review-agent
description: Universal Code Review Agent that validates JavaScript/TypeScript code
model: sonnet
---

# Code Review Agent

## Core Principles
1. Review Budget: Maximum 10 findings per review
2. Only Flag What Matters: Issues that will fail CI or break functionality
...

## Standards Workflow
### Step 1: Apply Pandora Standards (ALWAYS - Primary Source)
### Step 2: Detect Framework/Library
### Step 3: Fetch Latest Standards from Context7 (OPTIONAL)
### Step 4: Apply Framework-Specific Standards
...
```

### Python Agent Definition

Python agents implement a consistent interface:

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from agents.core.base_agent import BaseAgent, AgentResult, AgentContext

class UnitTestAgent(BaseAgent):
    """Agent for generating unit tests with 100% coverage target."""
    
    def __init__(self):
        super().__init__(
            name="unit-test",
            description="Generates comprehensive unit tests"
        )
    
    def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's main functionality."""
        # Implementation here
        pass
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze a source file for testable elements."""
        pass
    
    def generate_test_cases(self, analysis: AnalysisResult) -> List[TestCase]:
        """Generate test cases from analysis."""
        pass
```

## Execution Flow

### 1. Task Reception

When a user sends a request to Claude, the flow begins:

```
User Request
    │
    ▼
Claude Desktop/Code (MCP Client)
    │
    │ MCP Protocol
    ▼
Pandora AI Squad Server (MCP Server)
    │
    ▼
Task Manager Agent (Orchestrator)
```

### 2. Task Analysis and Routing

The Task Manager Agent analyzes the request and determines the appropriate workflow:

```python
def analyze_task(self, task_description: str) -> TaskPlan:
    """Analyze a task and create an execution plan."""
    
    # 1. Detect task type from keywords
    task_type = self._detect_task_type(task_description)
    
    # 2. Get the appropriate pipeline
    pipeline = WORKFLOW_PIPELINES.get(task_type, DEFAULT_PIPELINE)
    
    # 3. Create subtasks for each agent in the pipeline
    subtasks = self._create_subtasks(task_description, pipeline)
    
    return TaskPlan(
        task_type=task_type,
        pipeline=pipeline,
        subtasks=subtasks
    )
```

### 3. Pipeline Execution

Tasks flow through agent pipelines based on their type:

| Task Type | Pipeline |
|-----------|----------|
| Figma | Figma Reader -> Frontend -> Code Review -> Unit Test -> Sonar -> Performance |
| Frontend | Frontend -> Code Review -> Unit Test -> Sonar -> Performance |
| Backend | Backend -> Code Review -> Unit Test -> Sonar |
| Unit Test | Unit Test -> Sonar |
| Sonar | Sonar -> Code Review |

### 4. Agent Execution

Each agent in the pipeline executes its specific task:

```python
def execute_pipeline(self, plan: TaskPlan) -> PipelineResult:
    """Execute all agents in the pipeline sequentially."""
    
    context = AgentContext(task=plan.task_description)
    
    for agent_name in plan.pipeline:
        agent = self._get_agent(agent_name)
        
        # Execute the agent
        result = agent.execute(context)
        
        # Update context with agent output
        context.add_stage_result(agent_name, result)
        
        # Check for failures
        if result.status == 'failure':
            return PipelineResult(status='failure', context=context)
    
    return PipelineResult(status='success', context=context)
```

## Standards Workflow (Code Review Agent)

The Code Review Agent uses a hierarchical standards workflow:

### Standards Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  1. Pandora Standards (coding_standards.py)                 │
│     - ALWAYS enforced                                       │
│     - Highest priority                                      │
│     - Source: src/agents/core/coding_standards.py           │
├─────────────────────────────────────────────────────────────┤
│  2. Context7 Framework Standards                            │
│     - OPTIONAL enhancement                                  │
│     - Fetched dynamically via MCP                           │
│     - Framework-specific best practices                     │
├─────────────────────────────────────────────────────────────┤
│  3. Universal JS/TS Standards                               │
│     - Built-in knowledge fallback                           │
│     - General best practices                                │
└─────────────────────────────────────────────────────────────┘
```

### Pandora Standards (Primary Source)

The `coding_standards.py` file contains Pandora-specific rules that MUST always be enforced:

```python
CODING_STANDARDS = {
    "use-type-over-interface": {
        "description": "Use `type` over `interface` for object types",
        "good": "type UserData = { id: string; };",
        "bad": "interface UserData { id: string; }"
    },
    "no-todo-comments": {
        "description": "No TODO comments in production code",
        "pattern": r"//\s*TODO"
    },
    "prefer-for-of": {
        "description": "Prefer `for...of` over forEach",
        "good": "for (const item of items) { }",
        "bad": "items.forEach(item => { });"
    },
    "use-at-negative-index": {
        "description": "Use `.at(-n)` for negative indexing",
        "good": "const last = arr.at(-1);",
        "bad": "const last = arr[arr.length-1];"
    },
    "avoid-negated-conditions": {
        "description": "Avoid negated conditions with else blocks",
        "good": "if (condition) { B } else { A }",
        "bad": "if (!condition) { A } else { B }"
    },
    "use-globalthis": {
        "description": "Use globalThis instead of global",
        "good": "globalThis.window",
        "bad": "global.window"
    },
    "direct-undefined-comparison": {
        "description": "Compare with undefined directly",
        "good": "if (value === undefined) { }",
        "bad": "if (typeof value === 'undefined') { }"
    },
    "use-nullish-coalescing": {
        "description": "Use nullish coalescing (??) over logical OR (||)",
        "good": "const value = input ?? 'default';",
        "bad": "const value = input || 'default';"
    },
    "use-optional-chaining": {
        "description": "Use optional chaining (?.)",
        "good": "const name = user?.profile?.name;",
        "bad": "const name = user && user.profile && user.profile.name;"
    }
}
```

### Context7 Integration (Optional Enhancement)

When Context7 MCP is available, the agent fetches framework-specific standards:

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Detect Framework                                   │
│  - Check package.json for dependencies                      │
│  - Identify: react, vue, angular, svelte, next, etc.        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Resolve Library ID (Context7 MCP)                  │
│  - Tool: resolve-library-id                                 │
│  - Input: libraryName="react"                               │
│  - Output: libraryId="/facebook/react"                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Query Documentation (Context7 MCP)                 │
│  - Tool: query-docs                                         │
│  - Input: libraryId="/facebook/react",                      │
│           query="coding standards and best practices"       │
│  - Output: Latest React best practices                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Apply Standards                                    │
│  - Pandora standards (always)                               │
│  - Context7 standards (if available)                        │
│  - Universal standards (fallback)                           │
└─────────────────────────────────────────────────────────────┘
```

### Fallback Behavior

If Context7 is NOT available, the agent falls back to:
1. Pandora standards from `coding_standards.py` (always enforced)
2. Built-in framework knowledge from Claude's training data
3. Universal JS/TS best practices

## MCP Integration

### MCP Server Architecture

The Pandora AI Squad runs as an MCP (Model Context Protocol) server:

```python
# main.py
from mcp.server import Server
from tools.registry import register_all_tools

server = Server("pnd-agents")

# Register all tools
register_all_tools(server)

# Start the server
server.run()
```

### Tool Registration

Tools are registered in the MCP server to expose agent functionality:

```python
# tools/registry.py
def register_all_tools(server: Server):
    """Register all MCP tools."""
    
    # Filesystem tools
    server.register_tool("fs_read_file", fs_read_file)
    server.register_tool("fs_write_file", fs_write_file)
    
    # Agent tools
    server.register_tool("unit_test_generate", unit_test_generate)
    server.register_tool("sonar_validate", sonar_validate)
    server.register_tool("code_review", code_review)
    
    # Analytics tools
    server.register_tool("track_task_start", track_task_start)
    server.register_tool("track_task_end", track_task_end)
```

### MCP Communication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Desktop                           │
│                   (MCP Client Interface)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ JSON-RPC over stdio
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Pandora AI Squad Server                     │
│                   (MCP Server Interface)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Tool Registry                      │   │
│  │  - fs_read_file, fs_write_file                       │   │
│  │  - unit_test_generate, sonar_validate                │   │
│  │  - code_review, commerce_find_product                │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Agent Layer                        │   │
│  │  - Task Manager, Frontend, Backend                   │   │
│  │  - Code Review, Unit Test, Sonar                     │   │
│  │  - Commerce, Amplience, Performance                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

The agent system uses a categorized directory structure:

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
│   │   │   ├── providers/             # GitHub, Azure DevOps, local
│   │   │   ├── analyzers/             # Security, performance, quality
│   │   │   └── roles/                 # Frontend, backend, QA roles
│   │   ├── unit_test/                 # Test generation
│   │   ├── qa/                        # E2E and integration tests
│   │   ├── sonar_validation/          # SonarCloud quality gates
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

## Agent Communication

### Context Passing

Agents communicate through a shared context object:

```python
@dataclass
class AgentContext:
    """Shared context for agent pipeline execution."""
    
    task: str                          # Original task description
    metadata: Dict[str, Any]           # Task metadata (ticket_id, branch, etc.)
    stages: Dict[str, StageResult]     # Results from each agent
    files: Dict[str, str]              # Generated files
    errors: List[str]                  # Accumulated errors
    
    def add_stage_result(self, agent_name: str, result: AgentResult):
        """Add result from an agent stage."""
        self.stages[agent_name] = StageResult(
            status=result.status,
            output=result.output,
            files=result.files
        )
        
        # Merge generated files
        if result.files:
            self.files.update(result.files)
        
        # Accumulate errors
        if result.errors:
            self.errors.extend(result.errors)
```

### Output Format

Agents produce structured outputs:

```python
@dataclass
class AgentResult:
    """Result from agent execution."""
    
    status: str                        # 'success', 'failure', 'partial'
    output: str                        # Human-readable output
    files: Optional[Dict[str, str]]    # Generated files (path -> content)
    errors: Optional[List[str]]        # Error messages
    metrics: Optional[Dict[str, Any]]  # Performance metrics
```

## Analytics and Tracking

### Task Event Tracking

The Analytics Agent tracks task execution:

```python
def track_task_start(agent_name: str, task_id: str, metadata: Dict):
    """Record task start event."""
    event = TaskEvent(
        event_type='started',
        agent_name=agent_name,
        task_id=task_id,
        timestamp=datetime.utcnow(),
        metadata=metadata
    )
    analytics_store.record_event(event)

def track_task_end(agent_name: str, task_id: str, result: AgentResult):
    """Record task completion event."""
    event = TaskEvent(
        event_type='completed' if result.status == 'success' else 'failed',
        agent_name=agent_name,
        task_id=task_id,
        timestamp=datetime.utcnow(),
        duration=calculate_duration(task_id),
        metrics=result.metrics
    )
    analytics_store.record_event(event)
```

### Metrics Collected

- **Duration**: Time taken for task execution
- **Iterations**: Number of retry attempts
- **Errors**: Error count and types
- **Effectiveness Score**: Success rate over time
- **Confidence Score**: Agent's confidence in output
- **Human Review**: Whether human review was required

## Error Handling

### Retry Logic

Agents implement retry logic for transient failures:

```python
def execute_with_retry(self, context: AgentContext, max_retries: int = 3) -> AgentResult:
    """Execute agent with retry logic."""
    
    for attempt in range(max_retries):
        try:
            result = self.execute(context)
            
            if result.status == 'success':
                return result
            
            # Log retry attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying...")
            
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return AgentResult(status='failure', errors=['Max retries exceeded'])
```

### Error Propagation

Errors are propagated through the pipeline with context:

```python
def handle_agent_error(self, agent_name: str, error: Exception, context: AgentContext):
    """Handle agent execution error."""
    
    error_info = {
        'agent': agent_name,
        'error_type': type(error).__name__,
        'message': str(error),
        'context': context.task
    }
    
    # Log error
    logger.error(f"Agent {agent_name} failed: {error}", extra=error_info)
    
    # Add to context
    context.errors.append(f"{agent_name}: {error}")
    
    # Determine if pipeline should continue
    if isinstance(error, CriticalError):
        raise PipelineAbortError(f"Critical error in {agent_name}")
```

## Testing Agents

### Unit Testing

Agents are tested in isolation:

```python
def test_code_review_agent_detects_interface():
    """Test that code review agent flags interface usage."""
    
    agent = CodeReviewAgent()
    
    code = """
    interface UserData {
        id: string;
    }
    """
    
    result = agent.review(code)
    
    assert 'use-type-over-interface' in result.findings
    assert result.findings['use-type-over-interface'].severity == 'warning'
```

### Integration Testing

Pipeline execution is tested end-to-end:

```python
def test_frontend_pipeline():
    """Test complete frontend pipeline execution."""
    
    task_manager = TaskManagerAgent()
    
    result = task_manager.run_task(
        "Create a Button component with primary and secondary variants"
    )
    
    assert result.status == 'success'
    assert 'Button.tsx' in result.files
    assert 'Button.test.tsx' in result.files
```

## Related Documentation

- [Architecture](./architecture.md) - High-level system architecture
- [Agents Overview](./agents-overview.md) - All available agents
- [Setup Guide](./setup.md) - Installation and configuration

---

**Last Updated**: January 2026  
**Version**: 2.0.0  
**Maintained by**: Pandora Group
