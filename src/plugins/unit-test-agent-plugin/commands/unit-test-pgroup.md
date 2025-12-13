---
description: Generate unit tests for pandora-group (Next.js 15) components using Jest and React Testing Library with TypeScript.
---

# /unit-test-pgroup

Generate comprehensive unit tests for React components in the pandora-group repository.

## Usage

```
/unit-test-pgroup [file-path-or-pattern]
```

## Examples

```
/unit-test-pgroup app/components/ui/button.tsx
/unit-test-pgroup app/components/**/*.tsx
/unit-test-pgroup --coverage app/hooks
```

## Options

- `--coverage` - Analyze existing coverage and generate tests for uncovered code
- `--watch` - Generate tests and run in watch mode
- `--dry-run` - Show what tests would be generated without creating files

## What This Command Does

1. **Analyzes** the specified TypeScript component(s)
2. **Identifies** props types, state, hooks, and dependencies
3. **Generates** comprehensive test files with:
   - Component rendering tests
   - Props variation tests
   - User interaction tests (using userEvent)
   - Async operation tests
   - Edge case tests
   - TypeScript type safety
4. **Creates** test files co-located with source or in `__tests__/`
5. **Suggests** the command to run the tests

## Test File Location

Tests are created following one of these patterns:
```
app/components/{component}/{file}.test.tsx
app/components/{component}/__tests__/{file}.test.tsx
```

## Framework Details

- **Test Runner**: Jest
- **Testing Library**: React Testing Library
- **User Events**: @testing-library/user-event
- **Assertions**: Jest matchers + @testing-library/jest-dom
- **Environment**: happy-dom
- **Language**: TypeScript

## Next.js Specific Mocking

The agent automatically handles mocking for:
- `next/navigation` (useRouter, usePathname, useSearchParams)
- `next/image` (Image component)
- `next-intl` (useTranslations, useLocale)
- `next-themes` (useTheme)

## Run Tests After Generation

```bash
npm test
npm run test:watch
npm run testcoverage
npm run test:ci
```
