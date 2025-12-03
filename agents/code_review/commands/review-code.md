# Review Code

Perform comprehensive code review against Pandora coding standards.

## Context

This command performs a thorough code review of submitted code changes, validating against Pandora's coding standards, architectural patterns, and best practices.

## Requirements

- Code files to review
- Context about the feature/change
- Pandora coding standards reference

## Workflow

### 1. Initial Scan

Perform quick scan for critical issues:
- Security vulnerabilities
- Runtime errors
- Breaking changes
- Missing dependencies

### 2. Architecture Review

Validate architectural patterns:

```markdown
## Architecture Checklist

### Atomic Design
- [ ] Components at correct level (atom/molecule/organism)
- [ ] No circular dependencies
- [ ] Proper composition patterns
- [ ] Reusable abstractions

### Next.js App Router
- [ ] Correct use of 'use client' directive
- [ ] Server components for data fetching
- [ ] Proper loading/error states
- [ ] Metadata generation implemented

### State Management
- [ ] Appropriate state location
- [ ] No prop drilling
- [ ] Context used correctly
- [ ] No unnecessary re-renders
```

### 3. TypeScript Review

Validate TypeScript usage:

```markdown
## TypeScript Checklist

### Type Safety
- [ ] No `any` types without justification
- [ ] Proper interface definitions
- [ ] Generic types where appropriate
- [ ] Type guards for runtime checks

### Strict Mode
- [ ] strictNullChecks compliant
- [ ] noImplicitAny compliant
- [ ] No unused variables/parameters
- [ ] Explicit return types on functions
```

### 4. Code Quality Review

Check code quality standards:

```markdown
## Code Quality Checklist

### Naming
- [ ] Components: PascalCase
- [ ] Hooks: use{Name}
- [ ] Utils: camelCase
- [ ] Constants: UPPER_SNAKE_CASE

### Structure
- [ ] Imports organized (external → internal → relative)
- [ ] Hooks at top of component
- [ ] Event handlers before render
- [ ] Early returns for edge cases

### Documentation
- [ ] JSDoc for public APIs
- [ ] Complex logic commented
- [ ] Props documented
```

### 5. Accessibility Review

Validate accessibility compliance:

```markdown
## Accessibility Checklist

- [ ] Semantic HTML elements
- [ ] ARIA attributes where needed
- [ ] Keyboard navigation works
- [ ] Focus management correct
- [ ] Alt text for images
- [ ] Color contrast sufficient
```

### 6. Performance Review

Check for performance issues:

```markdown
## Performance Checklist

- [ ] Memoization where needed
- [ ] No unnecessary re-renders
- [ ] Lazy loading for heavy components
- [ ] Image optimization
- [ ] Bundle size impact acceptable
```

### 7. Security Review

Validate security practices:

```markdown
## Security Checklist

- [ ] No XSS vulnerabilities
- [ ] Input sanitization
- [ ] No hardcoded secrets
- [ ] Secure external links (rel="noopener")
- [ ] No sensitive data exposure
```

### 8. Testing Review

Check test coverage:

```markdown
## Testing Checklist

- [ ] Unit tests present
- [ ] Edge cases covered
- [ ] Mocks appropriate
- [ ] Coverage threshold met
- [ ] Tests are meaningful
```

## Review Comment Format

### Critical Issue
```markdown
**CRITICAL** | {File}:{Line}

**Issue**: {Description}
**Rule**: {Standard violated}

**Current**:
```{lang}
{problematic code}
```

**Suggested**:
```{lang}
{fixed code}
```

**Why**: {Explanation}
```

### Warning
```markdown
**WARNING** | {File}:{Line}

**Issue**: {Description}

**Suggestion**: {Recommended change}
```

### Suggestion
```markdown
**SUGGESTION** | {File}:{Line}

Consider {improvement}. This would {benefit}.
```

### Positive Feedback
```markdown
**GOOD** | {File}:{Line}

{Positive observation about the code}
```

## Review Summary Template

```markdown
# Code Review Summary

## Files Reviewed
- {file1.tsx}
- {file2.ts}

## Overall Assessment
**Status**: {Approved / Changes Requested / Rejected}

## Statistics
- Critical Issues: {count}
- Warnings: {count}
- Suggestions: {count}

## Critical Issues
1. {Issue summary with file:line}
2. {Issue summary with file:line}

## Warnings
1. {Warning summary}
2. {Warning summary}

## Suggestions
1. {Suggestion summary}
2. {Suggestion summary}

## Positive Observations
- {Good practice observed}
- {Good practice observed}

## Recommendation
{Final recommendation and next steps}
```

## Example

### Input
```typescript
// PageCover.tsx
const PageCover = (props: any) => {
  const [isLoading, setIsLoading] = useState(false)
  
  return (
    <div onClick={() => console.log('clicked')}>
      <img src={props.image} />
      <h1>{props.title}</h1>
    </div>
  )
}
```

### Output
```markdown
# Code Review Summary

## Files Reviewed
- PageCover.tsx

## Overall Assessment
**Status**: Changes Requested

## Statistics
- Critical Issues: 2
- Warnings: 2
- Suggestions: 1

## Critical Issues

### 1. CRITICAL | PageCover.tsx:1

**Issue**: Using `any` type for props
**Rule**: TypeScript strict mode - no implicit any

**Current**:
```typescript
const PageCover = (props: any) => {
```

**Suggested**:
```typescript
interface PageCoverProps {
  image: string;
  title: string;
}

const PageCover: React.FC<PageCoverProps> = ({ image, title }) => {
```

**Why**: Type safety prevents runtime errors and improves IDE support.

### 2. CRITICAL | PageCover.tsx:5

**Issue**: Image missing alt attribute
**Rule**: WCAG 2.1 - Images must have alt text

**Current**:
```tsx
<img src={props.image} />
```

**Suggested**:
```tsx
<img src={image} alt={title} />
```

**Why**: Screen readers need alt text to describe images.

## Warnings

### 1. WARNING | PageCover.tsx:4

**Issue**: Console.log in production code

**Suggestion**: Remove console.log or use proper logging utility.

### 2. WARNING | PageCover.tsx:2

**Issue**: Unused state variable `isLoading`

**Suggestion**: Remove unused state or implement loading logic.

## Suggestions

### 1. SUGGESTION | PageCover.tsx:1

Consider adding displayName for better debugging:
```typescript
PageCover.displayName = 'PageCover';
```

## Recommendation
Please address the 2 critical issues before approval. The accessibility and type safety issues must be fixed.
```

## Summary

The review-code command performs comprehensive code review against Pandora coding standards, providing actionable feedback organized by severity.
