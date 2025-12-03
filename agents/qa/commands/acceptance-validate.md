# Acceptance Validate

Validate features against acceptance criteria.

## Context

This command validates implemented features against their acceptance criteria, ensuring all requirements are met before deployment.

## Requirements

- Feature implementation
- Acceptance criteria from user story
- Test results

## Workflow

### 1. Parse Acceptance Criteria

Extract testable criteria from user story:

```markdown
## User Story
As a {user type}
I want to {action}
So that {benefit}

## Acceptance Criteria

### AC1: {Criterion Title}
**Given** {precondition}
**When** {action}
**Then** {expected result}

### AC2: {Criterion Title}
**Given** {precondition}
**When** {action}
**Then** {expected result}
```

### 2. Map to Test Cases

```markdown
## Test Case Mapping

| AC | Test Type | Test File | Status |
|----|-----------|-----------|--------|
| AC1 | Unit | Component.test.tsx | Pass |
| AC1 | E2E | feature.spec.ts | Pass |
| AC2 | Unit | Component.test.tsx | Fail |
| AC2 | Integration | service.test.ts | Pass |
```

### 3. Execute Validation

```markdown
## Validation Results

### AC1: {Criterion Title}
**Status**: Pass

**Evidence**:
- Unit test: `it('renders correctly')` - Pass
- E2E test: `test('displays on page')` - Pass
- Manual verification: Confirmed

### AC2: {Criterion Title}
**Status**: Fail

**Evidence**:
- Unit test: `it('handles error state')` - Fail
- Error: Expected error message not displayed

**Gap**:
- Error state not implemented
- Missing error boundary
```

### 4. Generate Report

```markdown
# Acceptance Validation Report

## Feature: {Feature Name}
**Story**: {Story ID}
**Date**: {Date}

## Summary

| Status | Count |
|--------|-------|
| Pass | {n} |
| Fail | {n} |
| Blocked | {n} |
| Not Tested | {n} |

**Overall**: {Ready for Release / Needs Work}

## Acceptance Criteria Validation

### AC1: {Title}
**Status**: Pass

**Criteria**:
> Given {precondition}
> When {action}
> Then {expected result}

**Validation**:
- [x] Unit tests pass
- [x] Integration tests pass
- [x] E2E tests pass
- [x] Manual verification complete

**Evidence**:
{Screenshot or test output}

---

### AC2: {Title}
**Status**: Fail

**Criteria**:
> Given {precondition}
> When {action}
> Then {expected result}

**Validation**:
- [x] Unit tests pass
- [ ] Integration tests fail
- [ ] E2E tests not run
- [ ] Manual verification incomplete

**Issues**:
1. {Issue description}
2. {Issue description}

**Required Actions**:
1. {Action to fix}
2. {Action to fix}

---

## Non-Functional Requirements

### Performance
- [ ] Page load < 3s
- [ ] LCP < 2.5s
- [ ] No memory leaks

### Accessibility
- [ ] WCAG 2.1 AA compliant
- [ ] Keyboard navigable
- [ ] Screen reader compatible

### Security
- [ ] No XSS vulnerabilities
- [ ] Input validation
- [ ] Secure data handling

## Recommendations

### Must Fix Before Release
1. {Critical issue}

### Should Fix
1. {Important issue}

### Nice to Have
1. {Enhancement}

## Sign-off

| Role | Name | Status | Date |
|------|------|--------|------|
| QA | {name} | {Approved/Rejected} | {date} |
| Dev | {name} | {Approved/Rejected} | {date} |
| PO | {name} | {Approved/Rejected} | {date} |
```

## Validation Checklist Template

```markdown
## Feature Validation Checklist

### Functional Requirements
- [ ] All acceptance criteria met
- [ ] Happy path works correctly
- [ ] Error handling works correctly
- [ ] Edge cases handled
- [ ] Data validation works

### UI/UX Requirements
- [ ] Matches design specifications
- [ ] Responsive across breakpoints
- [ ] Animations work correctly
- [ ] Loading states displayed
- [ ] Error states displayed

### Technical Requirements
- [ ] TypeScript strict mode compliant
- [ ] ESLint passing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Coverage threshold met

### Accessibility Requirements
- [ ] Semantic HTML used
- [ ] ARIA attributes correct
- [ ] Keyboard navigation works
- [ ] Focus management correct
- [ ] Color contrast sufficient
- [ ] Screen reader compatible

### Performance Requirements
- [ ] Page load time acceptable
- [ ] No unnecessary re-renders
- [ ] Images optimized
- [ ] Bundle size acceptable

### Security Requirements
- [ ] Input sanitized
- [ ] No XSS vulnerabilities
- [ ] Secure external links
- [ ] No sensitive data exposed
```

## Example

### Input
```
Feature: Contact Form
Story: INS-1234

Acceptance Criteria:
AC1: User can submit contact form with valid data
AC2: Form shows validation errors for invalid input
AC3: User sees success message after submission
AC4: Form is accessible via keyboard
```

### Output
```markdown
# Acceptance Validation Report

## Feature: Contact Form
**Story**: INS-1234
**Date**: March 15, 2024

## Summary

| Status | Count |
|--------|-------|
| Pass | 3 |
| Fail | 1 |
| Blocked | 0 |
| Not Tested | 0 |

**Overall**: Needs Work

## Acceptance Criteria Validation

### AC1: User can submit contact form with valid data
**Status**: Pass

**Criteria**:
> Given I am on the contact page
> When I fill in all required fields with valid data and click Submit
> Then the form is submitted successfully

**Validation**:
- [x] Unit tests pass (ContactForm.test.tsx:45)
- [x] Integration tests pass (contact-api.test.ts:23)
- [x] E2E tests pass (contact.spec.ts:12)
- [x] Manual verification complete

---

### AC2: Form shows validation errors for invalid input
**Status**: Pass

**Criteria**:
> Given I am on the contact page
> When I submit the form with invalid data
> Then I see appropriate error messages

**Validation**:
- [x] Unit tests pass (ContactForm.test.tsx:78)
- [x] E2E tests pass (contact.spec.ts:34)
- [x] Manual verification complete

---

### AC3: User sees success message after submission
**Status**: Pass

**Criteria**:
> Given I have submitted the form successfully
> When the submission completes
> Then I see a success message

**Validation**:
- [x] Unit tests pass (ContactForm.test.tsx:112)
- [x] E2E tests pass (contact.spec.ts:56)
- [x] Manual verification complete

---

### AC4: Form is accessible via keyboard
**Status**: Fail

**Criteria**:
> Given I am using keyboard navigation
> When I tab through the form
> Then I can access all fields and submit

**Validation**:
- [x] Unit tests pass
- [ ] E2E tests fail (contact.spec.ts:78)
- [ ] Manual verification failed

**Issues**:
1. Submit button not focusable after form validation error
2. Focus not returned to first error field

**Required Actions**:
1. Fix focus management after validation
2. Add focus trap within form

---

## Recommendations

### Must Fix Before Release
1. Fix keyboard accessibility issues (AC4)

### Should Fix
1. Add loading state during submission

### Nice to Have
1. Add form auto-save functionality
```

## Summary

The acceptance-validate command validates features against acceptance criteria, providing detailed evidence and recommendations for release readiness.
