---
description: Validate test coverage, identify gaps, and generate QA test scenarios.
---

# /qa

Analyze test coverage, identify testing gaps, and generate comprehensive QA test scenarios for your application.

## Usage

```
/qa [describe feature or paste code to analyze for test coverage]
```

## Examples

```
/qa Analyze test coverage for the checkout flow
/qa Generate test scenarios for the product search feature
/qa Review this component and identify missing test cases
```

## What This Command Does

1. **Analyzes** existing test coverage
2. **Identifies** untested code paths and edge cases
3. **Generates** comprehensive test scenarios
4. **Creates** test case documentation
5. **Suggests** automation opportunities
6. **Prioritizes** tests by risk and impact

## Output Format

The agent provides:
- Coverage analysis summary
- Gap identification report
- Test scenario matrix
- Priority-ranked test cases
- Automation recommendations
- Regression test suggestions

## Test Scenario Categories

- **Functional**: Core feature behavior
- **Edge Cases**: Boundary conditions, empty states
- **Error Handling**: Invalid inputs, API failures
- **Integration**: Component interactions
- **Regression**: Previously fixed bugs
- **Accessibility**: Screen reader, keyboard navigation

## QA Deliverables

- Test case specifications
- Acceptance criteria validation
- Bug risk assessment
- Test data requirements
- Environment considerations

## Pandora QA Standards

- Gherkin format for acceptance tests
- Risk-based test prioritization
- Cross-browser testing requirements
- Mobile responsiveness validation
- Performance threshold verification
