# PR Comment

Generate and post code review comments on pull requests.

## Context

This command generates structured code review comments for pull requests, providing actionable feedback in a consistent format.

## Requirements

- Review findings from code review
- PR context (files changed, description)
- Severity classification

## Workflow

### 1. Classify Findings

Categorize review findings:

```markdown
## Finding Categories

### Critical (Blocking)
- Security vulnerabilities
- Runtime errors
- Breaking changes
- Data loss risks
- Accessibility violations (critical)

### Warning (Should Fix)
- Code quality issues
- Performance concerns
- Minor accessibility issues
- Missing tests
- Documentation gaps

### Suggestion (Nice to Have)
- Style improvements
- Refactoring opportunities
- Alternative approaches
- Best practice recommendations
```

### 2. Generate Inline Comments

For specific line issues:

```markdown
### Inline Comment Format

**File**: `{file_path}`
**Line**: {line_number}
**Severity**: {Critical/Warning/Suggestion}

{Comment body with context and suggestion}

```{language}
// Suggested fix
{code example}
```
```

### 3. Generate Summary Comment

For overall PR feedback:

```markdown
## Code Review Summary

### Overview
{Brief description of the changes reviewed}

### Status: {Approved / Changes Requested / Needs Discussion}

### Statistics
| Category | Count |
|----------|-------|
| Critical | {n} |
| Warnings | {n} |
| Suggestions | {n} |

### Critical Issues (Must Fix)
{List of critical issues with file:line references}

### Warnings (Should Fix)
{List of warnings}

### Suggestions (Consider)
{List of suggestions}

### What's Good
{Positive observations about the code}

### Next Steps
{Clear action items for the author}
```

### 4. Format for GitHub

Use GitHub-flavored markdown:

```markdown
## 🔍 Code Review

### Status: ⚠️ Changes Requested

<details>
<summary>📊 Review Statistics</summary>

| Category | Count |
|----------|-------|
| 🔴 Critical | 2 |
| 🟡 Warnings | 3 |
| 🔵 Suggestions | 1 |

</details>

### 🔴 Critical Issues

#### 1. Type Safety Violation
📍 `lib/components/PageCover.tsx:12`

Using `any` type bypasses TypeScript's type checking:

```typescript
// Current
const handleClick = (event: any) => { ... }

// Suggested
const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => { ... }
```

#### 2. Missing Alt Text
📍 `lib/components/PageCover.tsx:25`

Images must have alt text for accessibility:

```tsx
// Current
<img src={imageUrl} />

// Suggested
<img src={imageUrl} alt={title} />
```

### 🟡 Warnings

1. **Unused Import** - `PageCover.tsx:3` - Remove unused `useState` import
2. **Missing Test** - No unit tests for new component
3. **Console Log** - `PageCover.tsx:18` - Remove console.log

### 🔵 Suggestions

1. Consider adding `displayName` for better debugging

### ✅ What's Good

- Clean component structure
- Good use of TypeScript generics
- Proper error handling

### 📋 Next Steps

1. Fix the 2 critical issues
2. Address warnings before merge
3. Consider suggestions for future improvements

---
*Automated review by PG AI Squad Code Review Agent*
```

## Comment Templates

### Approval
```markdown
## ✅ Code Review: Approved

Great work on this PR! The code follows Pandora standards and is ready to merge.

### Highlights
- {Positive observation 1}
- {Positive observation 2}

### Minor Suggestions (Optional)
- {Optional improvement 1}

LGTM! 🎉
```

### Changes Requested
```markdown
## ⚠️ Code Review: Changes Requested

Good progress, but there are some issues that need to be addressed before merging.

### Must Fix ({count})
1. {Critical issue 1}
2. {Critical issue 2}

### Should Fix ({count})
1. {Warning 1}
2. {Warning 2}

Please address the critical issues and re-request review.
```

### Needs Discussion
```markdown
## 💬 Code Review: Needs Discussion

I have some questions about the approach taken in this PR.

### Questions
1. {Question about design decision}
2. {Question about implementation choice}

### Concerns
1. {Concern about approach}

Let's discuss before proceeding.
```

## Example

### Input
```
PR: Add PageCover component
Files: PageCover.tsx, types.ts, index.ts
Findings:
- Critical: any type on line 12
- Critical: missing alt text on line 25
- Warning: unused import on line 3
- Suggestion: add displayName
```

### Output

```markdown
## 🔍 Code Review: PageCover Component

### Status: ⚠️ Changes Requested

This PR adds the PageCover organism component. The implementation looks good overall, but there are a couple of critical issues that need to be addressed.

<details>
<summary>📊 Review Statistics</summary>

| Category | Count |
|----------|-------|
| 🔴 Critical | 2 |
| 🟡 Warnings | 1 |
| 🔵 Suggestions | 1 |

</details>

### 🔴 Critical Issues

#### 1. Type Safety Violation
📍 `lib/components/organisms/PageCover/PageCover.tsx:12`

The `any` type bypasses TypeScript's type checking, which can lead to runtime errors.

```typescript
// Current
const handleClick = (event: any) => {

// Suggested
const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
```

#### 2. Accessibility: Missing Alt Text
📍 `lib/components/organisms/PageCover/PageCover.tsx:25`

Images must have descriptive alt text for screen reader users (WCAG 1.1.1).

```tsx
// Current
<img src={imageUrl} />

// Suggested
<img src={imageUrl} alt={altText || title} />
```

### 🟡 Warnings

1. **Unused Import** - `PageCover.tsx:3`
   - The `useState` import is not used. Remove it to keep the code clean.

### 🔵 Suggestions

1. **Add displayName** - Consider adding `PageCover.displayName = 'PageCover'` for better debugging in React DevTools.

### ✅ What's Good

- Clean component structure following atomic design
- Good TypeScript interface definitions in types.ts
- Proper index.ts exports

### 📋 Next Steps

1. Fix the 2 critical issues (type safety and accessibility)
2. Remove the unused import
3. Re-request review once changes are made

---
*Automated review by PG AI Squad Code Review Agent*
```

## Summary

The pr-comment command generates structured, actionable code review comments for pull requests, following a consistent format with clear severity classification and remediation guidance.
