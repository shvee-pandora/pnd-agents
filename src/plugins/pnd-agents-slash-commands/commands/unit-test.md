---
description: Generate comprehensive unit tests for React components and TypeScript code.
---

# /unit-test

Generate comprehensive unit tests using Jest and React Testing Library with full TypeScript support.

## Usage

```
/unit-test [paste component code or describe what to test]
```

## Examples

```
/unit-test [paste your React component here]
/unit-test Generate tests for a useCart hook with add/remove/update functions
/unit-test Create tests for the ProductCard component covering all props
```

## What This Command Does

1. **Analyzes** the component or function structure
2. **Identifies** props, state, hooks, and side effects
3. **Generates** comprehensive test cases
4. **Includes** edge cases and error scenarios
5. **Mocks** external dependencies appropriately
6. **Creates** readable, maintainable test code

## Output Format

The agent provides:
- Complete test file with imports
- Describe blocks organized by functionality
- Individual test cases with clear names
- Mock setup for dependencies
- Cleanup and teardown where needed
- Coverage suggestions

## Test Categories Generated

- **Rendering**: Component mounts without errors
- **Props**: All prop variations tested
- **Interactions**: Click, input, form submission
- **State**: State changes and updates
- **Async**: API calls, loading states, errors
- **Edge Cases**: Empty data, null values, boundaries

## Framework Support

- **Jest** with TypeScript
- **React Testing Library**
- **@testing-library/user-event**
- **MSW** for API mocking
- **jest-dom** matchers

## Pandora Testing Standards

- Minimum 80% coverage target
- Descriptive test names
- AAA pattern (Arrange, Act, Assert)
- No implementation details testing
- Accessibility queries preferred
