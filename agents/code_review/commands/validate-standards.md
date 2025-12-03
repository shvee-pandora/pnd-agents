# Validate Standards

Validate code against Pandora coding standards and architectural guidelines.

## Context

This command performs automated validation of code against Pandora's coding standards, running linters, type checkers, and custom validation rules.

## Requirements

- Code files to validate
- Access to ESLint, TypeScript, and Prettier configurations
- Pandora coding standards reference

## Workflow

### 1. Run Automated Checks

Execute validation tools:

```bash
# TypeScript type checking
pnpm typecheck

# ESLint validation
pnpm lint

# Prettier format check
pnpm format:check

# Run all validations
pnpm validate
```

### 2. Parse Results

Collect and categorize results:

```markdown
## Validation Results

### TypeScript
- Errors: {count}
- Files checked: {count}

### ESLint
- Errors: {count}
- Warnings: {count}
- Files checked: {count}

### Prettier
- Files needing formatting: {count}
```

### 3. Custom Validations

Run Pandora-specific checks:

```markdown
## Custom Validations

### File Naming
- [ ] Components use PascalCase
- [ ] Hooks use use{Name} pattern
- [ ] Utils use camelCase
- [ ] Test files use .test.tsx/.spec.tsx

### Directory Structure
- [ ] Components in correct atomic level
- [ ] Index exports present
- [ ] Types in separate files

### Import Organization
- [ ] External imports first
- [ ] Internal imports second
- [ ] Relative imports last
- [ ] No circular dependencies

### Component Patterns
- [ ] 'use client' only when needed
- [ ] displayName set
- [ ] Props destructured
- [ ] Proper typing
```

### 4. Generate Report

```markdown
# Standards Validation Report

## Summary
**Status**: {Pass / Fail}
**Total Issues**: {count}

## Automated Checks

### TypeScript ({status})
```
{TypeScript output}
```

### ESLint ({status})
```
{ESLint output}
```

### Prettier ({status})
```
{Prettier output}
```

## Custom Validations

### File Naming ({status})
| File | Expected | Actual | Status |
|------|----------|--------|--------|
| {file} | {expected} | {actual} | {pass/fail} |

### Directory Structure ({status})
| Check | Status |
|-------|--------|
| Components in atomic levels | {pass/fail} |
| Index exports present | {pass/fail} |
| Types separated | {pass/fail} |

### Import Organization ({status})
| File | Issue |
|------|-------|
| {file} | {issue description} |

## Issues by Severity

### Critical (Must Fix)
1. {Issue description}
2. {Issue description}

### Warnings (Should Fix)
1. {Warning description}
2. {Warning description}

### Info (Consider)
1. {Suggestion}
2. {Suggestion}

## Remediation Steps

1. Run `pnpm lint:fix` to auto-fix ESLint issues
2. Run `pnpm format` to fix formatting
3. Manually fix TypeScript errors
4. Address custom validation failures
```

## Pandora Standards Reference

### TypeScript Configuration
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### ESLint Rules
```javascript
{
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "jsx-a11y/alt-text": "error",
    "import/order": "error"
  }
}
```

### File Naming Patterns
```
Components: PascalCase.tsx
  ✓ PageCover.tsx
  ✗ page-cover.tsx
  ✗ pageCover.tsx

Hooks: use{Name}.ts
  ✓ useField.ts
  ✗ UseField.ts
  ✗ field-hook.ts

Utils: camelCase.ts
  ✓ buildImageUrl.ts
  ✗ BuildImageUrl.ts
  ✗ build-image-url.ts

Types: types.ts or {name}.types.ts
  ✓ types.ts
  ✓ PageCover.types.ts
  ✗ Types.ts

Tests: {name}.test.tsx or {name}.spec.tsx
  ✓ PageCover.test.tsx
  ✓ PageCover.spec.tsx
  ✗ PageCoverTest.tsx
```

### Directory Structure
```
lib/components/
├── atoms/           # Base components
│   └── {Component}/
│       ├── {Component}.tsx
│       ├── types.ts
│       ├── index.ts
│       ├── {Component}.test.tsx
│       └── {Component}.stories.tsx
├── molecules/       # Composite components
├── organisms/       # Complex components
└── templates/       # Page layouts
```

## Example

### Input
```
Validate: lib/components/organisms/PageCover/
```

### Output
```markdown
# Standards Validation Report

## Summary
**Status**: Fail
**Total Issues**: 5

## Automated Checks

### TypeScript (Pass)
```
No errors found
```

### ESLint (Fail)
```
lib/components/organisms/PageCover/PageCover.tsx
  12:5  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  25:9  warning  React Hook useEffect has a missing dependency  react-hooks/exhaustive-deps

✖ 2 problems (1 error, 1 warning)
```

### Prettier (Fail)
```
lib/components/organisms/PageCover/PageCover.tsx
lib/components/organisms/PageCover/types.ts
```

## Custom Validations

### File Naming (Pass)
All files follow naming conventions.

### Directory Structure (Fail)
| Check | Status |
|-------|--------|
| Components in atomic levels | Pass |
| Index exports present | Pass |
| Types separated | Fail - types inline in component |

### Import Organization (Fail)
| File | Issue |
|------|-------|
| PageCover.tsx | Relative imports before internal imports |

## Remediation Steps

1. Run `pnpm lint:fix` to fix the ESLint warning
2. Run `pnpm format` to fix formatting in 2 files
3. Fix the `any` type on line 12
4. Move types to separate types.ts file
5. Reorder imports: external → internal → relative
```

## Summary

The validate-standards command performs comprehensive automated validation against Pandora coding standards, providing detailed reports and remediation guidance.
