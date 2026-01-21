# Validate Standards

Validate code against the latest JavaScript/TypeScript coding standards using Context7.

## Context

This command performs automated validation of code against the latest framework-specific coding standards (fetched from Context7), running linters, type checkers, and custom validation rules. Works with any JS/TS framework: React, Vue, Angular, Svelte, Node.js, Next.js, and more.

## Requirements

- Code files to validate
- Access to ESLint, TypeScript, and Prettier configurations
- Access to Context7 MCP for fetching latest coding standards

## Workflow

### 0. Detect Framework & Fetch Standards from Context7

**IMPORTANT**: Before validating, identify the framework and fetch latest standards:

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

### 1. Run Automated Checks

Execute validation tools (adapt based on project's package manager):

```bash
# TypeScript type checking
npm run typecheck  # or pnpm/yarn typecheck

# ESLint validation
npm run lint  # or pnpm/yarn lint

# Prettier format check
npm run format:check  # or pnpm/yarn format:check

# Run all validations (if available)
npm run validate  # or pnpm/yarn validate
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

Run framework-agnostic and framework-specific checks (from Context7):

```markdown
## Custom Validations

### File Naming (Universal)
- [ ] Components/Classes use PascalCase
- [ ] Hooks/Composables use use{Name} pattern
- [ ] Utils use camelCase
- [ ] Test files use .test.ts/.spec.ts

### Directory Structure (Universal)
- [ ] Components/modules at correct abstraction level
- [ ] Index exports present where appropriate
- [ ] Types in separate files or co-located

### Import Organization (Universal)
- [ ] External imports first
- [ ] Internal imports second
- [ ] Relative imports last
- [ ] No circular dependencies

### Framework-Specific Patterns (from Context7)
- [ ] Following framework's recommended patterns
- [ ] Using framework's latest features appropriately
- [ ] Proper component/module organization
- [ ] Correct lifecycle/reactivity usage
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

## Universal Standards Reference

### TypeScript Configuration (Recommended)
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

### ESLint Rules (Universal)
```javascript
{
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-unused-vars": "error",
    "no-console": "warn",
    "prefer-const": "error",
    "eqeqeq": "error",
    "import/order": "error"
  }
}
// Note: Add framework-specific rules based on detected framework
// React: react-hooks/rules-of-hooks, react-hooks/exhaustive-deps
// Vue: vue/*, @vue/eslint-config-*
// Angular: @angular-eslint/*
```

### File Naming Patterns (Universal)
```
Components/Classes: PascalCase.tsx/vue/svelte
  ✓ UserProfile.tsx
  ✗ user-profile.tsx
  ✗ userProfile.tsx

Hooks/Composables: use{Name}.ts
  ✓ useAuth.ts
  ✗ UseAuth.ts
  ✗ auth-hook.ts

Utils: camelCase.ts
  ✓ formatDate.ts
  ✗ FormatDate.ts
  ✗ format-date.ts

Types: types.ts or {name}.types.ts
  ✓ types.ts
  ✓ UserProfile.types.ts
  ✗ Types.ts

Tests: {name}.test.ts or {name}.spec.ts
  ✓ UserProfile.test.tsx
  ✓ UserProfile.spec.ts
  ✗ UserProfileTest.tsx
```

### Directory Structure (Universal Principles)
```
src/
├── components/      # UI components (any framework)
│   └── {Component}/
│       ├── {Component}.tsx/vue/svelte
│       ├── types.ts
│       ├── index.ts
│       └── {Component}.test.ts
├── hooks/           # React hooks / Vue composables
├── utils/           # Utility functions
├── services/        # API/business logic
├── types/           # Shared type definitions
└── constants/       # Application constants

Note: Adapt structure based on framework conventions
(e.g., Angular modules, Vue stores, etc.)
```

## Example

### Input
```
Validate: src/components/UserProfile/
Framework detected: React (from package.json)
```

### Output
```markdown
# Standards Validation Report

## Framework Detected
React (from package.json dependencies)

## Context7 Standards Applied
- React best practices (hooks, component patterns)
- TypeScript strict mode
- Universal JS/TS standards

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
src/components/UserProfile/UserProfile.tsx
  12:5  error  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
  25:9  warning  React Hook useEffect has a missing dependency  react-hooks/exhaustive-deps

✖ 2 problems (1 error, 1 warning)
```

### Prettier (Fail)
```
src/components/UserProfile/UserProfile.tsx
src/components/UserProfile/types.ts
```

## Custom Validations

### File Naming (Pass)
All files follow naming conventions.

### Directory Structure (Fail)
| Check | Status |
|-------|--------|
| Components at correct level | Pass |
| Index exports present | Pass |
| Types separated | Fail - types inline in component |

### Import Organization (Fail)
| File | Issue |
|------|-------|
| UserProfile.tsx | Relative imports before internal imports |

## Remediation Steps

1. Run `npm run lint:fix` to fix the ESLint warning
2. Run `npm run format` to fix formatting in 2 files
3. Fix the `any` type on line 12
4. Move types to separate types.ts file
5. Reorder imports: external → internal → relative
```

## Summary

The validate-standards command performs comprehensive automated validation against the latest coding standards (fetched from Context7), providing detailed reports and remediation guidance. Works with any JavaScript/TypeScript framework.
