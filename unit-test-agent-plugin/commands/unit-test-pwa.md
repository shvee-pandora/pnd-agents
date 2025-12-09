---
description: Generate unit tests for pandora-ecom-web (PWA Kit) components using Jest and React Testing Library.
---

# /unit-test-pwa

Generate comprehensive unit tests for React components in the pandora-ecom-web repository.

## Usage

```
/unit-test-pwa [file-path-or-pattern]
```

## Examples

```
/unit-test-pwa apps/content/overrides/app/components/entry-points-tile/index.jsx
/unit-test-pwa apps/product-list/overrides/app/components/**/*.jsx
/unit-test-pwa --coverage apps/product-details
```

## Options

- `--coverage` - Analyze existing coverage and generate tests for uncovered code
- `--watch` - Generate tests and run in watch mode
- `--dry-run` - Show what tests would be generated without creating files

## What This Command Does

1. **Analyzes** the specified React component(s)
2. **Identifies** props, state, hooks, and dependencies
3. **Generates** comprehensive test files with:
   - Component rendering tests
   - Props variation tests
   - User interaction tests
   - Async operation tests
   - Edge case tests
4. **Creates** test files in the appropriate `__tests__/` directory
5. **Suggests** the command to run the tests

## Test File Location

Tests are created following the pattern:
```
apps/{app}/overrides/app/components/{component}/__tests__/{file}.test.js
```

## Framework Details

- **Test Runner**: Jest (via Nx)
- **Testing Library**: React Testing Library
- **Assertions**: Jest matchers + @testing-library/jest-dom
- **Mocking**: jest.mock() for dependencies

## Run Tests After Generation

```bash
nx test {app-name}
nx test {app-name} --coverage
```

Where `{app-name}` is one of: `content`, `product-list`, `product-details`, `pandora-shared-app`
