# Review Code

Perform comprehensive code review against the latest JavaScript/TypeScript coding standards using Context7.

## Context

This command performs a thorough code review of submitted code changes, validating against the latest framework-specific coding standards (fetched from Context7), architectural patterns, and best practices. Works with any JS/TS framework: React, Vue, Angular, Svelte, Node.js, Next.js, and more.

## Requirements

- Code files to review
- Context about the feature/change
- Access to Context7 MCP for fetching latest coding standards

## Workflow

### 0. Detect Framework & Fetch Standards from Context7

**IMPORTANT**: Before reviewing, identify the framework and fetch latest standards:

```markdown
## Framework Detection
1. Check package.json for primary framework:
   - react, react-dom → React
   - vue → Vue
   - @angular/core → Angular
   - svelte → Svelte
   - next → Next.js
   - nuxt → Nuxt
   - express → Express/Node.js

2. Use Context7 to fetch latest standards:
   - resolve-library-id: Get the Context7 library ID
   - query-docs: Fetch "coding standards and best practices"
```

### 1. Initial Scan

Perform quick scan for critical issues:
- Security vulnerabilities
- Runtime errors
- Breaking changes
- Missing dependencies

### 2. Architecture Review

Validate architectural patterns based on detected framework:

```markdown
## Architecture Checklist (Universal)

### Component/Module Structure
- [ ] Components/modules at correct abstraction level
- [ ] No circular dependencies
- [ ] Proper composition patterns
- [ ] Reusable abstractions

### Framework-Specific (from Context7)
- [ ] Following framework's recommended patterns
- [ ] Using framework's latest features appropriately
- [ ] Proper data fetching patterns for the framework
- [ ] Correct lifecycle/reactivity usage

### State Management
- [ ] Appropriate state location
- [ ] No prop drilling (or using framework's solution)
- [ ] State management follows framework conventions
- [ ] No unnecessary re-renders/reactivity triggers
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

Check code quality standards (universal + framework-specific from Context7):

```markdown
## Code Quality Checklist

### Naming (Universal)
- [ ] Components/Classes: PascalCase
- [ ] Functions/Hooks/Composables: camelCase (use{Name} for hooks)
- [ ] Utils: camelCase
- [ ] Constants: UPPER_SNAKE_CASE or camelCase

### Structure (Universal)
- [ ] Imports organized (external → internal → relative)
- [ ] State/reactive declarations at top
- [ ] Event handlers before render/return
- [ ] Early returns for edge cases

### Framework-Specific (from Context7)
- [ ] Following framework's naming conventions
- [ ] Using framework's recommended patterns
- [ ] Proper component/module organization

### Documentation
- [ ] JSDoc/TSDoc for public APIs
- [ ] Complex logic commented
- [ ] Props/parameters documented
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
// UserProfile.tsx (React component)
const UserProfile = (props: any) => {
  const [isLoading, setIsLoading] = useState(false)
  
  return (
    <div onClick={() => console.log('clicked')}>
      <img src={props.avatar} />
      <h1>{props.name}</h1>
    </div>
  )
}
```

### Output
```markdown
# Code Review Summary

## Framework Detected
React (from package.json dependencies)

## Context7 Standards Applied
- React best practices (hooks, component patterns)
- TypeScript strict mode
- Accessibility (WCAG 2.1)

## Files Reviewed
- UserProfile.tsx

## Overall Assessment
**Status**: Changes Requested

## Statistics
- Critical Issues: 2
- Warnings: 2
- Suggestions: 1

## Critical Issues

### 1. CRITICAL | UserProfile.tsx:1

**Issue**: Using `any` type for props
**Rule**: TypeScript strict mode - no implicit any

**Current**:
```typescript
const UserProfile = (props: any) => {
```

**Suggested**:
```typescript
type UserProfileProps = {
  avatar: string;
  name: string;
};

const UserProfile = ({ avatar, name }: UserProfileProps) => {
```

**Why**: Type safety prevents runtime errors and improves IDE support.

### 2. CRITICAL | UserProfile.tsx:5

**Issue**: Image missing alt attribute
**Rule**: WCAG 2.1 - Images must have alt text

**Current**:
```tsx
<img src={props.avatar} />
```

**Suggested**:
```tsx
<img src={avatar} alt={`${name}'s avatar`} />
```

**Why**: Screen readers need alt text to describe images.

## Warnings

### 1. WARNING | UserProfile.tsx:4

**Issue**: Console.log in production code

**Suggestion**: Remove console.log or use proper logging utility.

### 2. WARNING | UserProfile.tsx:2

**Issue**: Unused state variable `isLoading`

**Suggestion**: Remove unused state or implement loading logic.

## Suggestions

### 1. SUGGESTION | UserProfile.tsx:1

Consider using React.memo for performance if this component re-renders frequently:
```typescript
export const UserProfile = React.memo(({ avatar, name }: UserProfileProps) => {
  // ...
});
```

## Recommendation
Please address the 2 critical issues before approval. The accessibility and type safety issues must be fixed.
```

## Summary

The review-code command performs comprehensive code review against the latest coding standards (fetched from Context7), providing actionable feedback organized by severity. Works with any JavaScript/TypeScript framework.
