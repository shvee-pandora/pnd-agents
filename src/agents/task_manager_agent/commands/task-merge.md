# Task Merge

Collect and merge outputs from multiple agents into a final deliverable.

## Context

This command collects the outputs from all assigned agents, validates completeness, resolves conflicts, and produces a unified PR-ready deliverable.

## Requirements

- Completed agent assignments
- All deliverable files
- Validation results from Code Review agent

## Workflow

### 1. Collect Outputs

Gather all deliverables from completed assignments:

```markdown
## Collected Outputs

### From: amplience-cms-agent (ASN-000)
**Status**: Complete
**Files**:
- `contents/content-type-schema/schemas/content/group-header-schema.json`
- `contents/content-type/group-header.json`

### From: frontend-engineer-agent (ASN-001)
**Status**: Complete
**Files**:
- `lib/components/organisms/GroupHeader/GroupHeader.tsx`
- `lib/components/organisms/GroupHeader/types.ts`
- `lib/components/organisms/GroupHeader/index.ts`

### From: frontend-engineer-agent (ASN-002)
**Status**: Complete
**Files**:
- `lib/components/organisms/GroupHeader/GroupHeader.stories.tsx`

### From: qa-agent (ASN-003)
**Status**: Complete
**Files**:
- `lib/components/organisms/GroupHeader/GroupHeader.test.tsx`

### From: code-review-agent (ASN-004)
**Status**: Complete
**Result**: Approved with suggestions
```

### 2. Validate Completeness

Check all expected deliverables are present:

```typescript
interface DeliverableCheck {
  expected: string[];
  received: string[];
  missing: string[];
  extra: string[];
}

function validateDeliverables(task: Task): DeliverableCheck {
  const expected = task.subtasks.flatMap(s => s.deliverables);
  const received = collectReceivedFiles();
  
  return {
    expected,
    received,
    missing: expected.filter(f => !received.includes(f)),
    extra: received.filter(f => !expected.includes(f))
  };
}
```

### 3. Resolve Conflicts

Handle any conflicts between agent outputs:

```markdown
## Conflict Resolution

### Conflict: Type Definition Mismatch
**Files**: 
- `types.ts` (Frontend)
- `group-header-schema.json` (Amplience)

**Issue**: Frontend types don't match Amplience schema properties

**Resolution**: 
- Updated `types.ts` to match schema
- Added missing optional properties
- Aligned naming conventions
```

### 4. Integration Validation

Run integration checks:

```bash
# TypeScript compilation
pnpm typecheck

# ESLint validation
pnpm lint

# Unit tests
pnpm test

# Build verification
pnpm build
```

### 5. Generate PR Package

Create the final PR-ready package:

```markdown
## PR Package

### Title
feat(organisms): Add GroupHeader component with Amplience integration

### Description
Implements the Group Header component for the Pandora Group site.

#### Changes
- Add GroupHeader organism component
- Create Amplience content type schema
- Add Storybook documentation
- Add unit tests with 85% coverage

#### Checklist
- [x] TypeScript strict mode compliant
- [x] ESLint passing
- [x] Unit tests passing
- [x] Storybook story created
- [x] Accessibility validated
- [x] Code review approved

### Files Changed
```
contents/content-type-schema/schemas/content/group-header-schema.json (new)
contents/content-type/group-header.json (new)
lib/components/organisms/GroupHeader/GroupHeader.tsx (new)
lib/components/organisms/GroupHeader/GroupHeader.stories.tsx (new)
lib/components/organisms/GroupHeader/GroupHeader.test.tsx (new)
lib/components/organisms/GroupHeader/types.ts (new)
lib/components/organisms/GroupHeader/index.ts (new)
lib/components/organisms/index.ts (modified)
```

### Testing Instructions
1. Run `pnpm install`
2. Run `pnpm test` to verify tests pass
3. Run `pnpm storybook` to view component
4. Navigate to Organisms > GroupHeader
```

## Merge Report Template

```markdown
# Task Completion Report

## Task: {Task Name}
**ID**: {Task ID}
**Status**: Complete
**Duration**: {Time taken}

## Summary
{Brief description of what was accomplished}

## Deliverables

### Files Created
| File | Agent | Status |
|------|-------|--------|
| {path} | {agent} | {status} |

### Files Modified
| File | Agent | Changes |
|------|-------|---------|
| {path} | {agent} | {description} |

## Quality Metrics

### Code Quality
- TypeScript Errors: 0
- ESLint Errors: 0
- ESLint Warnings: {count}

### Test Coverage
- Statements: {%}
- Branches: {%}
- Functions: {%}
- Lines: {%}

### Accessibility
- Critical Issues: 0
- Warnings: {count}

## Agent Contributions

| Agent | Subtasks | Time | Status |
|-------|----------|------|--------|
| amplience-cms-agent | 1 | {time} | Complete |
| frontend-engineer-agent | 2 | {time} | Complete |
| qa-agent | 1 | {time} | Complete |
| code-review-agent | 1 | {time} | Approved |

## Review Comments
{Summary of code review feedback and resolutions}

## Next Steps
- [ ] Create PR
- [ ] Request human review
- [ ] Deploy to staging
- [ ] Verify in staging environment
```

## Example

### Input
```
Merge outputs for: Group Header Component Task
Assignments: ASN-000, ASN-001, ASN-002, ASN-003, ASN-004
```

### Output
```markdown
# Task Completion Report

## Task: Group Header Component
**ID**: TASK-001
**Status**: Complete
**Duration**: 45 minutes

## Summary
Successfully created the GroupHeader organism component with full Amplience CMS integration, Storybook documentation, and comprehensive test coverage.

## Deliverables

### Files Created
| File | Agent | Status |
|------|-------|--------|
| group-header-schema.json | amplience-cms-agent | Created |
| group-header.json | amplience-cms-agent | Created |
| GroupHeader.tsx | frontend-engineer-agent | Created |
| types.ts | frontend-engineer-agent | Created |
| index.ts | frontend-engineer-agent | Created |
| GroupHeader.stories.tsx | frontend-engineer-agent | Created |
| GroupHeader.test.tsx | qa-agent | Created |

### Files Modified
| File | Agent | Changes |
|------|-------|---------|
| organisms/index.ts | frontend-engineer-agent | Added GroupHeader export |

## Quality Metrics

### Code Quality
- TypeScript Errors: 0
- ESLint Errors: 0
- ESLint Warnings: 2 (non-blocking)

### Test Coverage
- Statements: 87%
- Branches: 82%
- Functions: 90%
- Lines: 85%

### Accessibility
- Critical Issues: 0
- Warnings: 1 (color contrast on hover state)

## PR Ready
All checks passed. Ready to create PR.
```

## Summary

The task-merge command collects outputs from all agents, validates completeness, resolves conflicts, and produces a comprehensive PR-ready package with full documentation and quality metrics.
