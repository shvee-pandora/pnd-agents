# Unit Test Generation Skill

This skill provides the core capability to analyze source code and generate comprehensive unit tests with full coverage.

## Allowed Tools

- Read
- Grep
- Glob
- Bash
- Edit

## Skill Description

When generating unit tests, follow this systematic approach:

### 1. Source Code Analysis

First, thoroughly analyze the source file to understand:

**For Functions/Utilities:**
- Function signature (parameters, return type)
- Input validation logic
- Business logic branches
- Error handling paths
- Side effects (API calls, state mutations)
- Dependencies (imports, injected services)

**For React Components:**
- Props interface and required/optional props
- Internal state (useState, useReducer)
- Effects (useEffect, useLayoutEffect)
- Custom hooks used
- Event handlers
- Conditional rendering logic
- Child components rendered

**For Hooks:**
- Input parameters
- Return value structure
- Internal state management
- Side effects
- Cleanup logic

### 2. Test Case Identification

Generate test cases for:

**Happy Path:**
- Default/typical usage
- All valid input combinations
- Expected output verification

**Edge Cases:**
- Empty inputs (null, undefined, empty string, empty array)
- Boundary values (min, max, zero)
- Special characters
- Large inputs

**Error Handling:**
- Invalid inputs
- API failures
- Network errors
- Timeout scenarios

**State Transitions:**
- Initial state
- State after actions
- State after async operations

### 3. Mock Strategy

Determine what needs mocking:

**External Dependencies:**
- API clients
- Database connections
- File system operations
- Third-party libraries

**Framework Features:**
- Router (navigation, params)
- Context providers
- Global state

**Browser APIs:**
- localStorage/sessionStorage
- fetch/XMLHttpRequest
- window/document methods

### 4. Test Structure

Organize tests following best practices:

```
describe('ModuleName', () => {
    // Setup and teardown
    beforeEach(() => { /* reset mocks */ })
    afterEach(() => { /* cleanup */ })

    describe('functionName', () => {
        it('should [expected behavior] when [condition]', () => {
            // Arrange
            // Act
            // Assert
        })
    })
})
```

### 5. Assertion Strategy

Use appropriate assertions:

**Value Assertions:**
- Equality checks
- Type checks
- Truthiness checks

**Function Assertions:**
- Called/not called
- Called with specific arguments
- Call count

**DOM Assertions:**
- Element presence
- Text content
- Attributes
- Accessibility

### 6. Coverage Goals

Target 100% coverage across:

- **Statements**: Every line of code executed
- **Branches**: Every if/else, switch case, ternary
- **Functions**: Every function called
- **Lines**: Every logical line covered

### 7. Output Format

Generate test files that:

- Follow the project's existing test patterns
- Include all necessary imports
- Have clear, descriptive test names
- Are properly formatted
- Can run immediately without modification

## Framework-Specific Guidelines

### Jest (PWA, Pandora Group)

```javascript
// Mocking
jest.mock('module', () => ({ fn: jest.fn() }))

// Assertions
expect(value).toBe(expected)
expect(fn).toHaveBeenCalledWith(args)
expect(element).toBeInTheDocument()

// Async
await waitFor(() => expect(...))
```

### Mocha/Chai (SFRA)

```javascript
// Mocking
const stub = sinon.stub(obj, 'method')
proxyquire('module', { dep: mock })

// Assertions
assert.equal(actual, expected)
assert.isTrue(condition)
assert.throws(() => fn())

// Async
return promise.then(result => assert.equal(...))
```

## Quality Checklist

Before outputting tests, verify:

- [ ] All exports are tested
- [ ] All branches are covered
- [ ] Error cases are handled
- [ ] Mocks are properly set up and cleaned up
- [ ] Test descriptions are clear and specific
- [ ] No hardcoded values that should be variables
- [ ] Tests are independent (no shared state)
- [ ] Async operations are properly awaited
