---
name: test-analysis
description: Analyze source code, requirements, or JIRA tickets to identify testing needs, coverage gaps, and testing strategies. Use when assessing testability, planning test coverage, or understanding what tests are needed for a feature.
allowed-tools: Read, Grep, Glob, Bash
---

# Test Analysis Skill

Analyze code, requirements, or tickets to identify testing needs and strategies.

## When to Use

This skill activates when:
- User wants to understand what tests are needed for code
- Analyzing testability of a component or module
- Identifying coverage gaps in existing tests
- Planning test strategy for a feature or change
- Reviewing code for testing complexity
- User mentions "analyze tests", "test analysis", "what tests", "testing strategy"

## Analysis Categories

### Code Testability Analysis
- Identify functions, components, and modules
- Assess code complexity and branching
- Detect dependencies that need mocking
- Evaluate separation of concerns
- Identify side effects and async operations

### Coverage Gap Analysis
- Compare source code against existing tests
- Identify untested functions and branches
- Find missing edge case coverage
- Detect untested error paths
- Highlight integration points without tests

### Testing Complexity Assessment
- Evaluate mock requirements
- Assess setup/teardown complexity
- Identify flaky test risks
- Determine test isolation challenges
- Rate overall testing difficulty (Low/Medium/High)

### Testing Strategy Recommendations
- Suggest unit vs integration vs E2E balance
- Recommend mock strategies
- Identify critical paths for testing
- Suggest test data requirements
- Propose testing priorities

## Analysis Process

1. **Gather Context**:
   - Read source code or requirements
   - Find existing tests for the module
   - Understand the feature scope

2. **Analyze Testability**:
   - Identify all testable elements
   - Assess complexity of each element
   - Note dependencies and side effects

3. **Identify Gaps**:
   - Compare against existing tests
   - Find untested paths and branches
   - Note missing edge cases

4. **Generate Recommendations**:
   - Prioritize testing needs
   - Suggest testing approaches
   - Estimate testing effort

## Output Format

```markdown
## Test Analysis Report

### Summary
- **Testability Score**: X/10
- **Current Coverage**: Estimated X%
- **Critical Gaps**: X items

### Testable Elements
| Element | Type | Complexity | Priority |
|---------|------|------------|----------|
| functionName | Function | Low | High |
| ComponentName | React Component | Medium | High |

### Coverage Gaps
1. **[Gap Description]**
   - Location: `file.ts:line`
   - Impact: High/Medium/Low
   - Recommendation: [What tests to add]

### Mock Requirements
- External service X needs mocking
- Database calls need mocking
- Browser APIs: localStorage, fetch

### Testing Strategy
1. **Unit Tests**: [Recommendations]
2. **Integration Tests**: [Recommendations]
3. **E2E Tests**: [Recommendations]

### Priority Test Cases
1. [High Priority] - Test case description
2. [High Priority] - Test case description
3. [Medium Priority] - Test case description

### Estimated Effort
- Unit Tests: X test files, ~Y test cases
- Complexity: Low/Medium/High
```

## Best Practices

- Focus on business-critical paths first
- Consider maintenance cost of tests
- Balance coverage with test quality
- Identify shared test utilities opportunities
- Consider data-driven test approaches
- Flag potential flaky test scenarios
- Note accessibility testing needs
