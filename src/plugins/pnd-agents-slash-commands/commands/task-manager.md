---
description: Orchestrate complex tasks by breaking them into subtasks and routing to specialized agents.
---

# /task-manager

Break down complex development tasks into manageable subtasks and coordinate their execution across specialized agents.

## Usage

```
/task-manager [task description]
```

## Examples

```
/task-manager Create a new product detail page with Figma design integration
/task-manager Refactor the checkout flow to improve performance
/task-manager Add unit tests for all components in the cart module
```

## What This Command Does

1. **Analyzes** your task description to understand requirements
2. **Decomposes** the task into logical subtasks with dependencies
3. **Identifies** which specialized agents should handle each subtask
4. **Creates** a structured execution plan with priorities
5. **Produces** a comprehensive task breakdown ready for implementation

## Output Format

The agent provides:
- Task breakdown with numbered subtasks
- Agent assignments for each subtask
- Dependency mapping between tasks
- Estimated complexity for each item
- Suggested execution order

## Best For

- Complex features requiring multiple skills
- Cross-functional development work
- Sprint planning and task estimation
- Coordinating frontend, backend, and testing work

## Pandora Standards

This agent enforces Pandora coding standards including:
- TypeScript strict mode
- Component naming conventions
- Test coverage requirements
- Documentation standards
