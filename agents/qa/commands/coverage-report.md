# Coverage Report

Generate and analyze test coverage reports.

## Context

This command generates test coverage reports, analyzes coverage gaps, and provides recommendations for improving test coverage.

## Requirements

- Test suite execution results
- Coverage thresholds
- Source code to analyze

## Workflow

### 1. Run Coverage Analysis

```bash
# Run tests with coverage
pnpm test --coverage

# Generate detailed report
pnpm test --coverage --coverageReporters=text,lcov,cobertura
```

### 2. Parse Coverage Data

```typescript
interface CoverageReport {
  summary: {
    statements: CoverageMetric;
    branches: CoverageMetric;
    functions: CoverageMetric;
    lines: CoverageMetric;
  };
  files: FileCoverage[];
  uncoveredLines: UncoveredLine[];
}

interface CoverageMetric {
  total: number;
  covered: number;
  skipped: number;
  pct: number;
}
```

### 3. Analyze Coverage Gaps

```markdown
## Coverage Gap Analysis

### Uncovered Files
Files with 0% coverage that need tests.

### Low Coverage Files
Files below threshold that need more tests.

### Uncovered Branches
Conditional logic not tested.

### Uncovered Functions
Functions without test coverage.
```

### 4. Generate Report

```markdown
# Test Coverage Report

## Summary

| Metric | Coverage | Threshold | Status |
|--------|----------|-----------|--------|
| Statements | {pct}% | 75% | {status} |
| Branches | {pct}% | 75% | {status} |
| Functions | {pct}% | 75% | {status} |
| Lines | {pct}% | 75% | {status} |

**Overall Status**: {Pass/Fail}

## Coverage by Directory

| Directory | Statements | Branches | Functions | Lines |
|-----------|------------|----------|-----------|-------|
| lib/components/atoms | {%} | {%} | {%} | {%} |
| lib/components/molecules | {%} | {%} | {%} | {%} |
| lib/components/organisms | {%} | {%} | {%} | {%} |
| lib/services | {%} | {%} | {%} | {%} |
| lib/hooks | {%} | {%} | {%} | {%} |
| lib/utils | {%} | {%} | {%} | {%} |

## Files Below Threshold

| File | Statements | Branches | Functions | Lines |
|------|------------|----------|-----------|-------|
| {file} | {%} | {%} | {%} | {%} |

## Uncovered Code

### {File Path}

**Lines**: {line numbers}
**Type**: {Statement/Branch/Function}

```{language}
{uncovered code snippet}
```

**Recommendation**: {How to test this code}

## Coverage Trends

| Date | Statements | Branches | Functions | Lines |
|------|------------|----------|-----------|-------|
| {date} | {%} | {%} | {%} | {%} |

## Recommendations

### High Priority
1. {Recommendation for critical uncovered code}
2. {Recommendation for critical uncovered code}

### Medium Priority
1. {Recommendation for important uncovered code}

### Low Priority
1. {Recommendation for nice-to-have coverage}
```

## Coverage Thresholds

```javascript
// jest.config.cjs
module.exports = {
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 75,
      lines: 75,
      statements: 75
    },
    // Per-file thresholds
    './lib/components/**/*.tsx': {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './lib/services/**/*.ts': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  }
};
```

## Coverage Exclusions

```javascript
// jest.config.cjs
module.exports = {
  collectCoverageFrom: [
    'lib/**/*.{ts,tsx}',
    '!lib/**/*.stories.tsx',
    '!lib/**/*.d.ts',
    '!lib/**/index.ts',
    '!lib/**/types.ts',
    '!lib/**/__mocks__/**'
  ],
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/.next/',
    '/coverage/'
  ]
};
```

## Example

### Input
```
Run coverage for: lib/components/organisms/
Threshold: 75%
```

### Output
```markdown
# Test Coverage Report

## Summary

| Metric | Coverage | Threshold | Status |
|--------|----------|-----------|--------|
| Statements | 82.5% | 75% | Pass |
| Branches | 71.2% | 75% | Fail |
| Functions | 85.0% | 75% | Pass |
| Lines | 81.8% | 75% | Pass |

**Overall Status**: Fail (Branch coverage below threshold)

## Coverage by Directory

| Directory | Statements | Branches | Functions | Lines |
|-----------|------------|----------|-----------|-------|
| lib/components/organisms/PageCover | 95% | 90% | 100% | 94% |
| lib/components/organisms/Contacts | 88% | 82% | 90% | 87% |
| lib/components/organisms/Drawer | 75% | 60% | 80% | 74% |
| lib/components/organisms/BreadcrumbExpanded | 70% | 55% | 75% | 68% |

## Files Below Threshold

| File | Statements | Branches | Functions | Lines |
|------|------------|----------|-----------|-------|
| Drawer/Drawer.tsx | 75% | 60% | 80% | 74% |
| BreadcrumbExpanded/BreadcrumbExpanded.tsx | 70% | 55% | 75% | 68% |

## Uncovered Code

### lib/components/organisms/Drawer/Drawer.tsx

**Lines**: 45-52
**Type**: Branch

```typescript
// Uncovered: slideDirection === 'auto' branch
if (slideDirection === 'auto') {
  return isMobile ? 'bottom' : 'right';
}
```

**Recommendation**: Add test for auto slide direction with mobile viewport.

### lib/components/organisms/BreadcrumbExpanded/BreadcrumbExpanded.tsx

**Lines**: 28-35
**Type**: Branch

```typescript
// Uncovered: empty breadcrumbs case
if (breadcrumbs.length === 0) {
  return null;
}
```

**Recommendation**: Add test for empty breadcrumbs array.

## Recommendations

### High Priority
1. Add tests for Drawer auto slide direction (affects branch coverage)
2. Add tests for BreadcrumbExpanded empty state

### Medium Priority
1. Increase Drawer test coverage for edge cases
2. Add more interaction tests for Contacts component

### Low Priority
1. Add snapshot tests for visual regression
```

## Summary

The coverage-report command generates comprehensive test coverage reports, identifies gaps, and provides actionable recommendations for improving coverage.
