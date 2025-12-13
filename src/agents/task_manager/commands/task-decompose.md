# Task Decompose

Decompose a complex task into actionable subtasks for the PG AI Squad agents.

## Context

This command takes a natural language task description and breaks it down into structured subtasks that can be assigned to specialized agents (Frontend, Amplience, Code Review, Performance, QA, Backend).

## Requirements

- Natural language task description
- Understanding of Pandora coding standards
- Knowledge of agent capabilities

## Workflow

### 1. Parse Task Description

Extract key information from the task:
- Feature name and purpose
- Components involved
- Data/content requirements
- Quality requirements
- Dependencies

### 2. Identify Work Streams

Categorize work into agent domains:

```markdown
## Work Streams

### Frontend Work
- Component creation
- Styling implementation
- Accessibility compliance
- Storybook documentation

### Amplience Work
- Content type design
- Schema creation
- Payload examples
- Preview integration

### Backend Work
- API routes
- Data fetching
- Server components
- Integrations

### QA Work
- Unit tests
- Integration tests
- E2E tests
- Coverage reports

### Code Review
- Standards validation
- Architecture review
- Accessibility audit
- Performance review
```

### 3. Create Subtask Structure

For each subtask, define:

```markdown
### Subtask: {Name}

**Agent**: {Frontend/Amplience/Code Review/Performance/QA/Backend}
**Priority**: {High/Medium/Low}
**Estimated Effort**: {Small/Medium/Large}

**Description**:
{What needs to be done}

**Acceptance Criteria**:
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Criterion 3}

**Dependencies**:
- {Blocking subtask, if any}

**Deliverables**:
- {File or artifact 1}
- {File or artifact 2}
```

### 4. Define Execution Order

Create a dependency graph:

```markdown
## Execution Plan

### Phase 1: Foundation (Parallel)
1. Amplience: Create content type schema
2. Frontend: Set up component structure

### Phase 2: Implementation (Sequential)
3. Frontend: Implement component (depends on 1, 2)
4. Backend: Create API route (depends on 1)

### Phase 3: Quality (Parallel)
5. QA: Write unit tests (depends on 3)
6. QA: Write E2E tests (depends on 3, 4)

### Phase 4: Review (Sequential)
7. Code Review: Validate all deliverables (depends on 3, 4, 5, 6)
```

## Example

### Input
```
Create a Group Header component from Figma with Schema, Story, and Tests
```

### Output
```markdown
## Task: Group Header Component

### Requirements
- Create responsive header component from Figma design
- Implement Amplience content type for header content
- Create Storybook story with all variants
- Write comprehensive tests
- Ensure accessibility compliance

### Subtasks

#### 1. Create Header Content Type [Agent: Amplience]
**Priority**: High
**Effort**: Medium

**Description**: Design and create the Amplience content type schema for the Group Header, including logo, navigation links, and CTA button.

**Acceptance Criteria**:
- [ ] JSON Schema follows Pandora patterns
- [ ] Uses global partials for common elements
- [ ] Includes example payload
- [ ] UI configuration created

**Deliverables**:
- `contents/content-type-schema/schemas/content/group-header-schema.json`
- `contents/content-type/group-header.json`

#### 2. Implement Header Component [Agent: Frontend]
**Priority**: High
**Effort**: Large
**Dependencies**: Subtask 1

**Description**: Build the GroupHeader React component following atomic design patterns, implementing responsive behavior and accessibility.

**Acceptance Criteria**:
- [ ] Matches Figma design
- [ ] Responsive across breakpoints
- [ ] Keyboard navigable
- [ ] TypeScript strict compliant

**Deliverables**:
- `lib/components/organisms/GroupHeader/GroupHeader.tsx`
- `lib/components/organisms/GroupHeader/types.ts`
- `lib/components/organisms/GroupHeader/index.ts`

#### 3. Create Storybook Story [Agent: Frontend]
**Priority**: Medium
**Effort**: Small
**Dependencies**: Subtask 2

**Description**: Create comprehensive Storybook documentation with all variants and controls.

**Acceptance Criteria**:
- [ ] Default story present
- [ ] All variants documented
- [ ] Controls for all props
- [ ] Accessibility addon passing

**Deliverables**:
- `lib/components/organisms/GroupHeader/GroupHeader.stories.tsx`

#### 4. Write Unit Tests [Agent: QA]
**Priority**: High
**Effort**: Medium
**Dependencies**: Subtask 2

**Description**: Write Jest unit tests covering all component behavior and edge cases.

**Acceptance Criteria**:
- [ ] 80%+ coverage
- [ ] Edge cases covered
- [ ] Accessibility tests included

**Deliverables**:
- `lib/components/organisms/GroupHeader/GroupHeader.test.tsx`

#### 5. Code Review [Agent: Code Review]
**Priority**: High
**Effort**: Small
**Dependencies**: Subtasks 1-4

**Description**: Validate all deliverables against Pandora coding standards.

**Acceptance Criteria**:
- [ ] TypeScript strict compliant
- [ ] ESLint passing
- [ ] Atomic design followed
- [ ] Accessibility requirements met

### Execution Plan

1. **Phase 1** (Parallel): Subtasks 1, 2
2. **Phase 2** (Sequential): Subtask 3 (after 2)
3. **Phase 3** (Parallel): Subtask 4 (after 2)
4. **Phase 4** (Sequential): Subtask 5 (after all)
```

## Summary

The task-decompose command transforms complex feature requests into structured, actionable subtasks with clear ownership, dependencies, and acceptance criteria. This enables efficient parallel execution and ensures comprehensive coverage of all aspects of the feature.
