# Test Case Writing Agent - Stakeholder Overview

**Document Version:** 2.0
**Date:** January 2026
**Prepared for:** Senior Stakeholders

---

## Executive Summary

The **Test Case Writing Agent** (qAIn - Quality AI Agent) is an AI-powered automation tool that generates comprehensive test cases from requirements, user stories, and acceptance criteria. It integrates with JIRA to streamline test management, reducing manual effort and ensuring consistent test coverage across projects.

**Key Value Proposition:**
- Reduces test case writing time by up to 70%
- Ensures consistent test coverage across all acceptance criteria
- Provides traceability from requirements to test cases
- Integrates seamlessly with existing JIRA workflows
- **NEW:** Enriches context from Parent tickets and EPICs
- **NEW:** Discovers and reuses existing test cases
- **NEW:** Merges similar scenarios to reduce redundancy
- **NEW:** Processes external documentation (Figma, Confluence)

---

## What Happens When the Agent is Called

### High-Level Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TEST CASE WRITING AGENT WORKFLOW                      │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │   INPUT      │     │  ENRICHMENT  │     │  PROCESSING  │     │   OUTPUT     │
     │              │     │              │     │              │     │              │
     │ • JIRA Story │────▶│ • Parent/EPIC│────▶│ • Parse      │────▶│ • Test Cases │
     │ • User Story │     │   Context    │     │   Requirements│     │ • Coverage   │
     │ • Acceptance │     │ • Existing   │     │ • Generate   │     │   Matrix     │
     │   Criteria   │     │   Test Cases │     │   Test Cases │     │ • JIRA       │
     │ • Test Types │     │ • Figma/     │     │ • Merge      │     │   Comments   │
     │ • Doc Links  │     │   Confluence │     │   Similar    │     │ • Traceability│
     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
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
| **External Doc Links** | Figma/Confluence URLs (auto-detected or provided) | `https://figma.com/file/...` |

### Step 1.5: Context Enrichment (NEW)

Before generating test cases, the agent enriches the requirements with additional context:

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONTEXT ENRICHMENT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  JIRA CONTEXT   │  │ EXTERNAL DOCS   │  │ EXISTING TESTS  │ │
│  │                 │  │                 │  │                 │ │
│  │ • Parent Ticket │  │ • Figma Designs │  │ • Linked Tests  │ │
│  │ • EPIC Details  │  │ • Confluence    │  │ • Related Tests │ │
│  │ • Story Desc.   │  │   Pages         │  │ • Reusable      │ │
│  │                 │  │                 │  │   Scenarios     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                   │                    │            │
│           └───────────────────┼────────────────────┘            │
│                               ▼                                 │
│                 ┌─────────────────────────┐                     │
│                 │  ENRICHED REQUIREMENTS  │                     │
│                 │  + JIRA Context         │                     │
│                 │  + Design Context       │                     │
│                 │  + Reusable Scenarios   │                     │
│                 └─────────────────────────┘                     │
│                               │                                 │
│                               ▼                                 │
│                 ┌─────────────────────────┐                     │
│                 │   SCENARIO MERGING      │                     │
│                 │   (Jaccard Similarity)  │                     │
│                 │   Threshold: 0.6        │                     │
│                 └─────────────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### A. JIRA Context Enrichment

The agent automatically fetches:

| Context | Source | Purpose |
|---------|--------|---------|
| **Parent Ticket** | JIRA parent field | Broader feature context |
| **EPIC Details** | JIRA epic link | Strategic objectives |
| **Linked Test Cases** | JIRA issue links | Avoid duplication |
| **Related Test Cases** | JQL search by keywords | Identify reusable scenarios |

#### B. External Documentation Processing

URLs are auto-detected from requirements text:

| Doc Type | URL Pattern | Extracted Context |
|----------|-------------|-------------------|
| **Figma** | `figma.com/file/*`, `figma.com/design/*` | UI components, states, breakpoints, accessibility |
| **Confluence** | `*.atlassian.net/wiki/*` | Requirements, API specs, business rules |

#### C. Scenario Merging

Similar scenarios are merged using Jaccard similarity algorithm:
- **Threshold:** 0.6 (60% keyword overlap)
- **Benefit:** Reduces redundant test cases
- **Output:** Combined scenarios with unified steps

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

### Step 3.5: Enhanced API Test Scenarios (NEW)

When generating API tests, the agent includes 34 comprehensive test scenarios:

```
┌─────────────────────────────────────────────────────────────────┐
│                    API TEST SCENARIOS (34 Total)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │  BASIC VALIDATION   │  │  AUTHENTICATION     │              │
│  │                     │  │                     │              │
│  │ • Valid request     │  │ • Invalid token     │              │
│  │ • Missing fields    │  │ • Expired token     │              │
│  │ • Invalid format    │  │ • Missing header    │              │
│  │ • Malformed JSON    │  │ • Unauthorized user │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │  RBAC SECURITY      │  │  HTTP STATUS CODES  │              │
│  │                     │  │                     │              │
│  │ • Admin access      │  │ • 400 Bad Request   │              │
│  │ • Regular user      │  │ • 404 Not Found     │              │
│  │ • Role rejection    │  │ • 409 Conflict      │              │
│  │ • Permission denied │  │ • 422 Unprocessable │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │  CONTRACT TESTING   │  │  IDEMPOTENCY        │              │
│  │                     │  │                     │              │
│  │ • OpenAPI/Swagger   │  │ • Repeated POST     │              │
│  │ • Response schema   │  │ • Duplicate check   │              │
│  │ • Request schema    │  │ • PUT idempotent    │              │
│  │ • Content-Type      │  │ • DELETE idempotent │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │  API VERSIONING     │  │  DATABASE           │              │
│  │                     │  │                     │              │
│  │ • v1 compatibility  │  │ • Persistence check │              │
│  │ • v2 new features   │  │ • Transactional     │              │
│  │ • Deprecation       │  │ • Rollback on error │              │
│  │ • Header version    │  │ • Consistency       │              │
│  └─────────────────────┘  └─────────────────────┘              │
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

### JIRA Context Structure (NEW)
```
JiraContext
├── story_key: "OG-7381"
├── story_summary: "Product Set Engraving"
├── story_description: "As a customer..."
├── parent_key: "OG-7380"
├── parent_summary: "Engraving Feature"
├── parent_description: "Parent feature details..."
├── epic_key: "OG-7000"
├── epic_summary: "Q1 2026 Enhancements"
├── epic_description: "Epic level objectives..."
├── linked_test_cases: [
│   ├── key: "OG-7382"
│   ├── summary: "Test engraving flow"
│   └── status: "Ready"
│   ]
├── related_test_cases: [...]
└── reusable_scenarios: ["Engraving validation", "CTA visibility"]
```

---

## Integration Points

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| **JIRA** | REST API v3 | Create test cases, link issues, add comments, fetch parent/epic context |
| **Figma** | URL parsing + API | Extract design context, UI components, states |
| **Confluence** | URL parsing + API | Extract requirements, API specs, business rules |
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
    include_api=True,  # NEW: Generates 34 API test scenarios
    external_doc_links=[  # NEW: External documentation
        "https://figma.com/file/ABC123/Login-Design",
        "https://company.atlassian.net/wiki/spaces/PROJ/pages/123"
    ],
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
        "external_doc_links": [],  # NEW: Auto-detected from requirements
    }
})
```

### 3. JIRA Workflow (with Context Enrichment)
```python
from src.agents.test_case_writing_agent import run_jira_workflow

result = run_jira_workflow(
    story_key="OG-7381",
    requirements="...",
    feature_name="Product Set Engraving",
    test_types=["FT-UI", "E2E"],
    create_in_jira=True,
    # NEW: Context enrichment options
    include_parent_context=True,   # Fetch parent ticket
    include_epic_context=True,     # Fetch EPIC details
    include_existing_tests=True,   # Find existing test cases
    external_doc_links=[],         # Figma/Confluence URLs
)

# NEW: Result includes JIRA context info
print(f"Parent: {result['jira_context']['parent_key']}")
print(f"Epic: {result['jira_context']['epic_key']}")
print(f"Linked tests found: {result['jira_context']['linked_test_count']}")
print(f"Related tests found: {result['jira_context']['related_test_count']}")
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
| **Context Awareness** | Parent/EPIC context enrichment for better test design |
| **Reusability** | Discovers and leverages existing test cases |
| **Redundancy Reduction** | Merges similar scenarios using AI similarity matching |
| **Design Integration** | Figma/Confluence content informs test scenarios |
| **API Coverage** | 34 comprehensive API test scenarios out-of-the-box |

---

## Signature

All outputs from the Test Case Writing Agent include the signature:

> **"I'm your Junior Quality Engineer - qAIn"**

This identifies AI-generated test artifacts for governance and audit purposes.

---

## Contact & Support

For questions about the Test Case Writing Agent, contact the **PG AI Squad**.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | January 2026 | Added JIRA context enrichment (parent/EPIC), external doc processing (Figma/Confluence), scenario merging, 34 API test scenarios |
| 1.0 | January 2026 | Initial release with core test case generation and JIRA integration |

---

*Document generated by AI Documentation Agent*
