# Functional Test Automation Agent - Overview

**Document Version:** 1.1
**Date:** January 2026
**Prepared for:** Senior Stakeholders

---

## Executive Summary

The **Functional Test Automation Agent** (func_test_auto) is an AI-powered tool that generates Cypress automation tests from manual test cases, requirements, or JIRA tickets. It always references the `pandora_cypress` repository to ensure generated code follows Pandora's established patterns and conventions, and **REUSES EXISTING STEP DEFINITIONS**.

**Key Value Proposition:**
- Accelerates automation test creation by 60-70%
- **Maximizes reuse of existing step definitions** (reduces duplication)
- Ensures consistency with pandora_cypress repository standards
- Generates Page Object Model (POM) based test structures
- Creates Gherkin feature files with step definition mapping
- Creates complete test suites including fixtures and custom commands
- Integrates with existing QA workflows and JIRA
- **NEW:** Step definition discovery and reuse from existing automation

---

## Reference Repository

**CRITICAL:** This agent ALWAYS references the pandora_cypress repository before generating tests.

```
Repository:      https://pandora-jewelry.visualstudio.com/Pandora%20DDRT%20QA/_git/pandora_cypress
Context:         /.claude/context.md
Step Defs:       /cypress/support/step_definitions/**/*.ts
Common Steps:    /cypress/support/step_definitions/common/**/*.ts
Features:        /cypress/e2e/features/**/*.feature
```

The context.md file contains:
- Project structure and file organization
- Coding conventions and naming standards
- Page Object Model patterns
- Custom Cypress commands available
- Fixture patterns and test data organization
- Best practices for test implementation

---

## Step Definition Reuse (CRITICAL)

**The agent MUST read and reuse existing step definitions before creating new ones.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     STEP DEFINITION REUSE WORKFLOW                           │
└─────────────────────────────────────────────────────────────────────────────┘

  MANUAL TEST STEP
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  STEP 1: SEARCH EXISTING STEP DEFINITIONS                               │
  │                                                                         │
  │  Read all files from:                                                   │
  │  • /cypress/support/step_definitions/**/*.ts                           │
  │  • /cypress/support/step_definitions/common/**/*.ts                    │
  │                                                                         │
  │  Extract patterns like:                                                 │
  │  • Given('user is on {string} page', ...)                              │
  │  • When('user clicks on {string}', ...)                                │
  │  • Then('user should see {string}', ...)                               │
  └─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  STEP 2: MATCH PRIORITY                                                 │
  │                                                                         │
  │  1. EXACT MATCH     → Reuse existing step definition                   │
  │  2. SIMILAR MATCH   → Adapt with parameters                            │
  │  3. COMMON STEP     → Reuse from shared steps                          │
  │  4. NO MATCH        → Create new step (LAST RESORT)                    │
  └─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  STEP 3: OUTPUT                                                         │
  │                                                                         │
  │  Feature file with annotations:                                         │
  │  • Steps using existing definitions → marked with source file          │
  │  • Steps needing new definitions → marked "NEW STEP NEEDED"            │
  │                                                                         │
  │  Step definition file (only for NEW steps)                             │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Step Definition Matching Example

**Manual Test Step:** "Click the Add to Cart button"

**Search Results:**
```typescript
// Found in /cypress/support/step_definitions/common/clicks.ts
When('user clicks on {string}', (element: string) => {
  cy.get(`[data-testid="${element}"]`).click();
});
```

**Result:** REUSE existing step → `When user clicks on "Add to Cart"`

---

## Test Data / Fixtures Reuse (CRITICAL)

**The agent MUST read and reuse existing test data fixtures before creating new ones.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TEST DATA / FIXTURES REUSE WORKFLOW                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Read existing fixtures from:                                            │
│     • /cypress/fixtures/**/*.json                                           │
│     • /cypress/fixtures/testData/**/*.json                                  │
│                                                                             │
│  2. For each test data need:                                                │
│     • Identify category (user, product, cart, etc.)                         │
│     • Search existing fixtures by category                                  │
│     • REUSE if found, CREATE only if not found                              │
│                                                                             │
│  3. Output:                                                                 │
│     • Tests reference existing fixtures                                     │
│     • New fixtures only when necessary                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Example - Reusing User Data:**
```typescript
// GOOD: Reference existing fixture
cy.fixture('users/validUser.json').then((user) => {
  cy.get('[data-testid="email"]').type(user.email);
});

// BAD: Hardcode test data
cy.get('[data-testid="email"]').type('test@example.com');
```

---

## Page Object Model (POM) Reuse (CRITICAL)

**The agent MUST read and reuse existing Page Objects before creating new ones.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PAGE OBJECT MODEL REUSE WORKFLOW                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Read existing Page Objects from:                                        │
│     • /cypress/support/page-objects/**/*.ts                                 │
│     • /cypress/support/components/**/*.ts                                   │
│     • /cypress/support/pages/**/*.ts                                        │
│                                                                             │
│  2. For each page interaction:                                              │
│     • Search by page name (e.g., "ProductPage")                             │
│     • Search by URL pattern (e.g., "/product/:id")                          │
│     • IMPORT and REUSE if found                                             │
│     • CREATE new POM only if not found                                      │
│                                                                             │
│  3. Extract from existing POMs:                                             │
│     • Available selectors                                                   │
│     • Available methods                                                     │
│     • URL patterns                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Example - Reusing Page Object:**
```typescript
// GOOD: Import and use existing page object
import { ProductPage } from '@support/page-objects/product-page';
const productPage = new ProductPage();
productPage.visit();
productPage.clickAddToCart();

// BAD: Write selectors inline
cy.visit('/product/123');
cy.get('[data-testid="add-to-cart"]').click();
```

---

## Environment Configuration Reference (CRITICAL)

**Tests MUST use environment configuration, never hardcode URLs or credentials.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENVIRONMENT CONFIGURATION REFERENCE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Read environment config from:                                           │
│     • /cypress.config.ts                                                    │
│     • /cypress.env.json                                                     │
│     • /cypress/config/**/*.json                                             │
│                                                                             │
│  2. Extract:                                                                │
│     • Base URLs for each environment                                        │
│     • API endpoints                                                         │
│     • Environment-specific variables                                        │
│                                                                             │
│  3. Reference in tests:                                                     │
│     • Use Cypress.env() for environment variables                           │
│     • Use environment-specific fixtures                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Example - Using Environment Config:**
```typescript
// GOOD: Use environment variables
cy.visit(Cypress.env('baseUrl') + '/products');
cy.request(Cypress.env('apiUrl') + '/api/users');

// BAD: Hardcode URLs
cy.visit('https://staging.example.com/products');
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FUNC TEST AUTO AGENT WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │   INPUT      │     │   CONTEXT    │     │  PROCESSING  │     │   OUTPUT     │
     │              │     │   FETCH      │     │              │     │              │
     │ • Manual TC  │────▶│ • pandora_   │────▶│ • Parse TC   │────▶│ • Spec Files │
     │ • JIRA Ticket│     │   cypress    │     │ • Map Actions│     │ • Page Objects│
     │ • Requirements│    │   context.md │     │ • Generate   │     │ • Fixtures   │
     │ • User Story │     │ • Patterns   │     │   Code       │     │ • Commands   │
     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## Supported Test Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **FT-UI** | Functional Test - UI Component | Single component validation |
| **FT-API** | Functional Test - API | API endpoint testing |
| **E2E** | End-to-End Test | Complete user journeys |
| **SIT** | System Integration Test | Cross-system flows |
| **REGRESSION** | Regression Test | Existing functionality |
| **SMOKE** | Smoke Test | Critical path validation |

---

## What Happens When the Agent is Called

### Step 1: Context Fetch

Before generating any code, the agent fetches patterns from:
```
https://pandora-jewelry.visualstudio.com/Pandora%20DDRT%20QA/_git/pandora_cypress?path=/.claude/context.md
```

### Step 2: Input Processing

The agent accepts various input formats:

| Input Type | Description |
|------------|-------------|
| **Manual Test Cases** | Text-based test case descriptions |
| **JIRA Tickets** | Ticket content with acceptance criteria |
| **Requirements** | Feature requirements documentation |
| **Gherkin Scenarios** | BDD format test scenarios |

### Step 3: Action Mapping

Manual test steps are mapped to Cypress commands:

| Manual Action | Cypress Command |
|---------------|-----------------|
| Click / Tap | `cy.get(selector).click()` |
| Type / Enter | `cy.get(selector).type(value)` |
| Select / Choose | `cy.get(selector).select(value)` |
| Navigate / Go to | `cy.visit(url)` |
| Verify / See | `cy.get(selector).should('be.visible')` |
| Contains | `cy.get(selector).should('contain', text)` |

### Step 4: Code Generation

The agent generates:

```
Generated Files:
├── cypress/e2e/
│   └── feature-name.cy.ts          # Spec file
├── cypress/support/page-objects/
│   └── feature-name-page.ts        # Page Object
├── cypress/fixtures/
│   └── feature-name.json           # Test data
└── cypress/support/commands.ts     # Custom command additions
```

---

## Output Structure

### Spec File Example

```typescript
/**
 * Cart Functionality
 * Verify add to cart flow
 *
 * Test Level: E2E
 * Tags: ['@smoke', '@cart']
 *
 * Generated by Func Test Auto Agent
 * Reference: https://pandora-jewelry.visualstudio.com/Pandora%20DDRT%20QA/_git/pandora_cypress
 */

import { ProductPage } from '@support/page-objects/product-page';
import { CartPage } from '@support/page-objects/cart-page';

describe('Cart Functionality', { tags: ['@smoke', '@cart'] }, () => {
  const productPage = new ProductPage();
  const cartPage = new CartPage();

  beforeEach(() => {
    cy.login();
  });

  it('should add product to cart successfully', () => {
    productPage.visit();
    productPage.getAddToCartButton().click();
    productPage.getCartCount().should('contain', '1');
    cartPage.visit();
    cartPage.getCartItems().should('have.length.at.least', 1);
  });
});
```

### Page Object Example

```typescript
/**
 * ProductPage
 * Type: page
 * URL Pattern: /product/:id
 *
 * Generated by Func Test Auto Agent
 */

export class ProductPage {
  private selectors = {
    addToCartButton: '[data-testid="add-to-cart-btn"]',
    cartCount: '[data-testid="cart-count"]',
    cartIcon: '[data-testid="cart-icon"]',
  };

  readonly url = '/product';

  visit(): this {
    cy.visit(this.url);
    return this;
  }

  getAddToCartButton(): Cypress.Chainable {
    return cy.get(this.selectors.addToCartButton);
  }

  getCartCount(): Cypress.Chainable {
    return cy.get(this.selectors.cartCount);
  }

  getCartIcon(): Cypress.Chainable {
    return cy.get(this.selectors.cartIcon);
  }
}
```

---

## Data Structures

### AutomationTestCase

```
AutomationTestCase
├── id: AUTO-0001
├── title: "Verify add to cart functionality"
├── description: "Test product can be added to cart"
├── test_level: E2E
├── priority: HIGH
├── test_type: POSITIVE
├── preconditions: ["User is logged in"]
├── steps: [
│   ├── step_number: 1
│   ├── action: "Navigate to product page"
│   ├── cypress_command: "cy.visit('/product')"
│   └── expected_result: "Page loads"
│   ]
├── expected_result: "Product in cart"
├── page_objects: ["ProductPage", "CartPage"]
├── fixtures: ["product-data.json"]
└── jira_reference: "OG-1234"
```

### AutomationTestSuite

```
AutomationTestSuite
├── name: "Cart Functionality"
├── description: "Cart feature test suite"
├── spec_file_path: "cypress/e2e/cart.cy.ts"
├── test_level: E2E
├── test_cases: [AutomationTestCase, ...]
├── page_objects: [PageObjectDefinition, ...]
├── fixtures: ["cart-data.json"]
├── before_all: "cy.clearLocalStorage()"
├── before_each: "cy.login()"
├── after_each: null
├── after_all: null
└── tags: ["@smoke", "@cart"]
```

---

## Integration Points

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| **pandora_cypress** | Repository Reference | Source of patterns and standards |
| **JIRA** | Ticket Reference | Link tests to tickets |
| **Test Case Writing Agent** | Workflow Input | Accept qAIn generated test cases |
| **QA Agent** | Workflow Output | Validate generated tests |

---

## Entry Points

### 1. Direct Function Call

```python
from src.agents.func_test_auto_agent import generate_automation_suite

result = generate_automation_suite(
    name="Cart Functionality",
    manual_test_cases=[
        """
        Title: Verify add to cart
        Steps:
        1. Navigate to product page
        2. Click add to cart
        3. Verify cart count increases
        Expected: Product in cart
        """,
    ],
    test_level="E2E",
)

print(result["code"]["specFileContent"])
```

### 2. Workflow Context

```python
from src.agents.func_test_auto_agent import run

result = run({
    "task_description": "Generate automation tests for cart feature",
    "input_data": {
        "feature_name": "Cart Functionality",
        "manual_test_cases": [...],
        "test_level": "E2E",
        "jira_ticket": "OG-1234",
    }
})
```

### 3. Parse Single Test Case

```python
from src.agents.func_test_auto_agent import parse_manual_test

test_case = parse_manual_test(
    test_case_text="""
    Title: Verify login flow
    Preconditions:
    - User has valid credentials
    Steps:
    1. Navigate to login page
    2. Enter username
    3. Enter password
    4. Click login button
    Expected: User is logged in
    """,
    test_id="TC-001",
    test_level="E2E",
)
```

---

## Recommendations

After test generation:

1. **Fetch context first** - Always reference pandora_cypress before generating
2. **Review selectors** - Update to match actual DOM attributes
3. **Add test data** - Update fixture files with real data
4. **Run locally** - Validate tests execute correctly
5. **Replace TODOs** - Add proper assertions where indicated
6. **CI/CD integration** - Add generated tests to pipelines

---

## Benefits Summary

| Benefit | Impact |
|---------|--------|
| **Time Savings** | 60-70% faster test automation creation |
| **Consistency** | Tests follow pandora_cypress patterns |
| **Quality** | POM-based structure for maintainability |
| **Traceability** | JIRA and manual test references |
| **Integration** | Seamless workflow with other agents |
| **Scalability** | Bulk test case conversion supported |

---

## Workflow Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        QA AUTOMATION WORKFLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

  JIRA Ticket
       │
       ▼
  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │ Test Case       │     │ Func Test Auto  │     │ QA Agent        │
  │ Writing Agent   │────▶│ Agent           │────▶│                 │
  │ (qAIn)          │     │                 │     │ Validation      │
  │                 │     │ Generate        │     │                 │
  │ Generate Manual │     │ Cypress Tests   │     │ Review &        │
  │ Test Cases      │     │                 │     │ Validate        │
  └─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  pandora_cypress    │
                    │  Repository         │
                    │                     │
                    │  Generated tests    │
                    │  committed here     │
                    └─────────────────────┘
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial release with core functionality |

---

## Contact & Support

For questions about the Functional Test Automation Agent, contact the **PG AI Squad**.

---

*Document generated by AI Documentation Agent*
