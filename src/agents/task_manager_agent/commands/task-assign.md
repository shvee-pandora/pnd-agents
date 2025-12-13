# Task Assign

Assign decomposed subtasks to the appropriate PG AI Squad agents.

## Context

This command takes decomposed subtasks and routes them to the correct specialized agent based on the task type, required skills, and agent capabilities.

## Requirements

- Decomposed subtasks from task-decompose
- Understanding of agent capabilities
- Dependency information

## Agent Routing Matrix

| Task Type | Primary Agent | Secondary Agent |
|-----------|---------------|-----------------|
| React component | Frontend Engineer | - |
| Storybook story | Frontend Engineer | - |
| Figma parsing | Frontend Engineer | - |
| Accessibility | Frontend Engineer | Code Review |
| Content type | Amplience CMS | - |
| JSON schema | Amplience CMS | - |
| Content payload | Amplience CMS | - |
| API route | Backend | - |
| Server component | Backend | Frontend Engineer |
| Data fetching | Backend | - |
| Unit tests | QA | - |
| Integration tests | QA | - |
| E2E tests | QA | - |
| Code review | Code Review | - |
| Standards validation | Code Review | - |
| HAR analysis | Performance | - |
| Optimization | Performance | Frontend/Backend |

## Workflow

### 1. Analyze Subtask

For each subtask, determine:
- Primary skill required
- Tools needed
- Output format expected
- Quality criteria

### 2. Match to Agent

```typescript
function assignAgent(subtask: Subtask): AgentAssignment {
  const taskType = identifyTaskType(subtask);
  
  const agentMap: Record<TaskType, Agent> = {
    'component': 'frontend-engineer-agent',
    'story': 'frontend-engineer-agent',
    'accessibility': 'frontend-engineer-agent',
    'content-type': 'amplience-cms-agent',
    'schema': 'amplience-cms-agent',
    'api-route': 'backend-agent',
    'server-component': 'backend-agent',
    'unit-test': 'qa-agent',
    'e2e-test': 'qa-agent',
    'review': 'code-review-agent',
    'performance': 'performance-agent'
  };

  return {
    agent: agentMap[taskType],
    subtask,
    priority: calculatePriority(subtask),
    estimatedTime: estimateTime(subtask)
  };
}
```

### 3. Create Assignment

```markdown
## Agent Assignment

### Assignment ID: {UUID}
**Agent**: {Agent Name}
**Subtask**: {Subtask Name}
**Priority**: {1-5}
**Status**: Pending

### Context
{Background information the agent needs}

### Instructions
{Specific instructions for the agent}

### Expected Output
{What the agent should produce}

### Quality Criteria
- {Criterion 1}
- {Criterion 2}

### Dependencies
- Waiting on: {List of blocking assignments}
- Blocks: {List of dependent assignments}
```

### 4. Queue Management

```markdown
## Assignment Queue

### Ready (No Dependencies)
1. [HIGH] amplience-cms-agent: Create Header Content Type
2. [HIGH] frontend-engineer-agent: Set up component structure

### Waiting
3. [HIGH] frontend-engineer-agent: Implement component
   - Waiting on: #1, #2
4. [MEDIUM] qa-agent: Write unit tests
   - Waiting on: #3

### In Progress
(None)

### Completed
(None)
```

## Example

### Input
```markdown
Subtask: Implement Header Component
Agent: Frontend
Dependencies: Content Type Schema
```

### Output
```markdown
## Agent Assignment

### Assignment ID: ASN-001
**Agent**: frontend-engineer-agent
**Subtask**: Implement Header Component
**Priority**: 1 (High)
**Status**: Waiting

### Context
The Group Header is a responsive navigation component that displays the Pandora logo, main navigation links, and a CTA button. The Amplience content type schema (ASN-000) defines the content structure.

### Instructions
1. Create component directory: `lib/components/organisms/GroupHeader/`
2. Implement `GroupHeader.tsx` following Pandora patterns
3. Create `types.ts` with TypeScript interfaces
4. Create `index.ts` for public exports
5. Use Amplience content type for props interface
6. Implement responsive behavior (mobile hamburger menu)
7. Ensure keyboard navigation works
8. Add proper ARIA attributes

### Expected Output
```
lib/components/organisms/GroupHeader/
├── GroupHeader.tsx
├── types.ts
├── index.ts
└── styles.module.css (if needed)
```

### Quality Criteria
- [ ] Matches Figma design specifications
- [ ] TypeScript strict mode compliant
- [ ] No ESLint errors
- [ ] Responsive across all breakpoints
- [ ] Keyboard accessible
- [ ] WCAG 2.1 AA compliant

### Dependencies
- Waiting on: ASN-000 (Content Type Schema)
- Blocks: ASN-002 (Storybook Story), ASN-003 (Unit Tests)
```

## Summary

The task-assign command routes subtasks to the appropriate specialized agents, providing them with the context, instructions, and quality criteria needed to complete their work successfully.
