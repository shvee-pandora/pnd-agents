# Test Case Writing Agent - Stakeholder Overview

**Document Version:** 1.0
**Date:** January 2026
**Prepared for:** Senior Stakeholders

---

## Executive Summary

The **Test Case Writing Agent** is an AI-powered automation tool that generates comprehensive test cases from requirements, user stories, and acceptance criteria. It integrates with JIRA to streamline test management, reducing manual effort and ensuring consistent test coverage across projects.

**Key Value Proposition:**
- Reduces test case writing time by up to 70%
- Ensures consistent test coverage across all acceptance criteria
- Provides traceability from requirements to test cases
- Integrates seamlessly with existing JIRA workflows

---

## What Happens When the Agent is Called

### High-Level Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TEST CASE WRITING AGENT WORKFLOW                      │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │   INPUT      │     │  PROCESSING  │     │   OUTPUT     │
     │              │     │              │     │              │
     │ • JIRA Story │────▶│ • Parse      │────▶│ • Test Cases │
     │ • User Story │     │   Requirements│     │ • Coverage   │
     │ • Acceptance │     │ • Generate   │     │   Matrix     │
     │   Criteria   │     │   Test Cases │     │ • JIRA       │
     │ • Test Types │     │ • Classify   │     │   Comments   │
     │   Required   │     │   & Organize │     │ • Traceability│
     └──────────────┘     └──────────────┘     └──────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   JIRA INTEGRATION   │
                    │                      │
                    │ • Create Test Cases  │
                    │ • Link to Story      │
                    │ • Add Coverage       │
                    │   Comments           │
                    └──────────────────────┘
```

---

## Detailed Process Steps

### Step 1: Input Processing

When the agent is invoked, it receives:

| Input | Description | Example |
|-------|-------------|---------|
| **Requirements/User Story** | Text describing the feature | "As a customer, I want to add engraving to products..." |
| **Acceptance Criteria** | List of conditions to be met | "Engrave CTA visible when set has 1 engravable product" |
| **Feature Name** | Name of the feature being tested | "Product Set Engraving" |
| **Test Types** | Types of testing required | FT-UI, E2E, Integration |
| **JIRA Story Key** | Reference ticket | OG-7381 |

### Step 2: Requirements Extraction

The agent parses input text using pattern recognition to identify testable conditions:

- **User Story Format:** "As a [role], I want [feature], so that [benefit]"
- **Conditional Statements:** "When [condition], then [outcome]"
- **BDD/Gherkin:** "Given [context], When [action], Then [result]"
- **Acceptance Criteria:** Numbered or bulleted requirements

### Step 3: Test Case Generation

The agent generates multiple categories of test cases:

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEST CASE GENERATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  FUNCTIONAL │  │  NEGATIVE   │  │  EDGE CASE  │             │
│  │    Tests    │  │    Tests    │  │    Tests    │             │
│  │             │  │             │  │             │             │
│  │ • Happy path│  │ • Invalid   │  │ • Empty     │             │
│  │ • Positive  │  │   input     │  │   input     │             │
│  │   scenarios │  │ • Error     │  │ • Max/Min   │             │
│  │             │  │   handling  │  │   values    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  BOUNDARY   │  │ INTEGRATION │  │    API      │             │
│  │    Tests    │  │    Tests    │  │   Tests     │             │
│  │             │  │             │  │             │             │
│  │ • Min-1     │  │ • Data flow │  │ • Valid     │             │
│  │ • Min       │  │ • Service   │  │   request   │             │
│  │ • Max       │  │   contracts │  │ • Auth      │             │
│  │ • Max+1     │  │ • DB        │  │ • Errors    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ SECURITY    │  │ACCESSIBILITY│  │ PERFORMANCE │             │
│  │   Tests     │  │   Tests     │  │    Tests    │             │
│  │             │  │             │  │             │             │
│  │ • XSS       │  │ • Keyboard  │  │ • Load time │             │
│  │ • SQL Inj.  │  │ • Screen    │  │ • Throughput│             │
│  │ • CSRF      │  │   reader    │  │ • Concurrent│             │
│  │ • Auth      │  │ • Contrast  │  │   users     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 4: Test Case Classification

Each generated test case is automatically classified with:

| Attribute | Values | Purpose |
|-----------|--------|---------|
| **Priority** | Critical, High, Medium, Low | Execution prioritization |
| **Test Level** | FT-UI, FT-API, SIT, E2E, UAT, A11Y, Performance, Security | Test categorization |
| **Testing Cycle** | Smoke, Sanity, Regression, Exploratory | When to execute |
| **Component** | UI, API, E2E, Database, Integration | System area |
| **Testing Technique** | BVA, Equivalence Partitioning, Decision Table, etc. | Design method used |

### Step 5: Output Generation

The agent produces multiple outputs:

#### A. Test Cases (Gherkin Format)
```gherkin
@Label: qAIn, ProductSetEngraving
@Component: UI
@Priority: High
@TestType: Functional
@TestLevel: FT-UI
@TestingCycle: Regression

Scenario: Verify Engrave CTA visible when set has 1 engravable product
  Given User is on Product Set PDP with 1 engravable child product
  When User views the product details
  Then Engrave CTA button is visible
  And CTA matches standard product engraving design
```

#### B. Coverage Matrix
| Priority | FT-UI | FT-API | SIT | E2E | Total |
|----------|-------|--------|-----|-----|-------|
| Critical | 2 | 0 | 0 | 1 | 3 |
| High | 5 | 2 | 1 | 2 | 10 |
| Medium | 3 | 1 | 2 | 1 | 7 |
| Low | 1 | 0 | 0 | 0 | 1 |
| **Total** | **11** | **3** | **3** | **4** | **21** |

#### C. Traceability Matrix
| Test Case ID | Title | Linked Requirement | Type | Level |
|--------------|-------|-------------------|------|-------|
| TC-0001 | Verify Engrave CTA visible | AC-1 | functional | FT-UI |
| TC-0002 | Verify CTA hidden for 0 engravable | AC-3 | functional | FT-UI |
| TC-0003 | Verify CTA hidden for multiple | AC-8 | edge_case | FT-UI |

### Step 6: JIRA Integration

When JIRA integration is enabled:

```
┌─────────────────────────────────────────────────────────────────┐
│                      JIRA WORKFLOW                              │
└─────────────────────────────────────────────────────────────────┘

  1. CREATE TEST CASES                2. LINK TO STORY
  ┌──────────────────┐               ┌──────────────────┐
  │ For each TC:     │               │ Create "Tests"   │
  │ • Create issue   │──────────────▶│ link from test   │
  │   type: TestCase │               │ case to story    │
  │ • Set priority   │               └──────────────────┘
  │ • Add labels     │                        │
  │ • Set component  │                        ▼
  └──────────────────┘               3. ADD COMMENT
                                     ┌──────────────────┐
                                     │ Post coverage    │
                                     │ summary comment  │
                                     │ on story         │
                                     └──────────────────┘
```

**JIRA Comment Posted (Example):**
```
I'm your Junior Quality Engineer - qAIn

**Test Designing and Test Management Completed**

---

**Story:** OG-7381
**Total Test Cases Created:** 21
**Test Cases Linked:** 21

---

## Test Case Summary by Priority x Test Level

| Priority | FT-UI | FT-API | SIT | E2E | Total |
|----------|-------|--------|-----|-----|-------|
| Critical | 2 | 0 | 0 | 1 | 3 |
| High | 5 | 2 | 1 | 2 | 10 |
...
```

---

## Test Case Types & When Generated

| Test Type | Generated When | Use Case |
|-----------|----------------|----------|
| **Functional** | Always | Core feature validation |
| **Negative** | Always | Error handling verification |
| **Edge Case** | `include_edge_cases=True` | Unusual input scenarios |
| **Boundary** | `include_boundary=True` | Min/max value testing |
| **Integration** | `include_integration=True` | Cross-component testing |
| **API** | `include_api=True` | REST API validation |
| **Security** | `include_security=True` | Vulnerability testing |
| **Accessibility** | `include_accessibility=True` | WCAG compliance |
| **Performance** | `include_performance=True` | Load & response testing |

---

## Testing Techniques Applied

The agent applies industry-standard testing techniques:

| Technique | Application |
|-----------|-------------|
| **Boundary Value Analysis (BVA)** | Input field limits |
| **Equivalence Partitioning** | Input data grouping |
| **Decision Table Testing** | Complex business rules |
| **State Transition Testing** | Workflow states (login, order, payment) |
| **Use Case Testing** | End-to-end scenarios |
| **Error Guessing** | Common failure points |

---

## Data Structures

### Test Case Structure
```
TestCase
├── id: TC-0001
├── title: "Verify Engrave CTA visible..."
├── description: "Validate that the system..."
├── test_type: FUNCTIONAL
├── priority: HIGH
├── preconditions: ["User is on PDP"]
├── steps: [
│   ├── step_number: 1
│   ├── action: "Navigate to Set PDP"
│   └── expected_result: "Page loads"
│   ]
├── expected_result: "CTA is visible"
├── test_level: FT-UI
├── testing_cycle: REGRESSION
├── component: UI
├── testing_technique: USE_CASE
├── labels: ["qAIn", "ProductSetEngraving"]
└── related_requirement: "AC-1"
```

### Test Suite Structure
```
TestSuite
├── name: "Product Set Engraving Test Suite"
├── description: "Comprehensive test suite..."
├── test_cases: [TestCase, TestCase, ...]
├── coverage_areas: ["Functional", "Edge Case", "Boundary"]
├── requirements: ["AC-1", "AC-2", ...]
└── coverage_gaps: ["Security not covered"]
```

---

## Integration Points

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| **JIRA** | REST API v3 | Create test cases, link issues, add comments |
| **Workflow Engine** | Context-based | Part of larger agent workflows |
| **CLI** | Direct invocation | Standalone test generation |

---

## Entry Points

The agent can be invoked through multiple methods:

### 1. Direct Function Call
```python
from src.agents.test_case_writing_agent import generate_test_cases

result = generate_test_cases(
    requirements="User should be able to login...",
    feature_name="User Login",
    include_security=True,
    include_accessibility=True,
)
```

### 2. Workflow Context
```python
from src.agents.test_case_writing_agent import run

result = run({
    "task_description": "Generate tests for login feature",
    "input_data": {
        "requirements": "...",
        "feature_name": "Login",
        "include_all": True,
    }
})
```

### 3. JIRA Workflow
```python
from src.agents.test_case_writing_agent import run_jira_workflow

result = run_jira_workflow(
    story_key="OG-7381",
    requirements="...",
    feature_name="Product Set Engraving",
    test_types=["FT-UI", "E2E"],
    create_in_jira=True,
)
```

---

## Benefits Summary

| Benefit | Impact |
|---------|--------|
| **Time Savings** | 70% reduction in test case writing time |
| **Consistency** | Standardized test case format across teams |
| **Coverage** | Systematic coverage of edge cases often missed manually |
| **Traceability** | Automatic linking of tests to requirements |
| **Quality** | Professional-grade test design techniques applied |
| **Integration** | Seamless JIRA workflow integration |
| **Documentation** | Auto-generated coverage matrices and reports |

---

## Signature

All outputs from the Test Case Writing Agent include the signature:

> **"I'm your Junior Quality Engineer - qAIn"**

This identifies AI-generated test artifacts for governance and audit purposes.

---

## Contact & Support

For questions about the Test Case Writing Agent, contact the **PG AI Squad**.

---

*Document generated by AI Documentation Agent*
