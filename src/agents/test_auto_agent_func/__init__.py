"""
Test Auto Agent Func Package

Generates Cypress automation tests following Pandora's testing standards.
References pandora_cypress repository for coding conventions, patterns, and
EXISTING STEP DEFINITIONS to maximize reuse.

Repository Reference:
- URL: https://pandora-jewelry.visualstudio.com/Pandora%20DDRT%20QA/_git/pandora_cypress
- Context: /.claude/context.md
- Step Definitions: /cypress/support/step_definitions/**/*.ts
- Features: /cypress/e2e/features/**/*.feature

CRITICAL: The agent MUST read all existing step definitions before generating
new scenarios to ensure maximum reuse of existing automation code.
"""

from .agent import (
    # Main Agent Class
    TestAutoAgentFunc,
    # Enums
    TestLevel,
    ExecutionEnvironment,
    BrowserType,
    PageObjectType,
    TestPriority,
    TestType,
    StepType,
    StepDefinitionSource,
    # Data Classes - Context & Config
    CypressContextReference,
    # Data Classes - Step Definitions
    StepDefinition,
    StepDefinitionRegistry,
    ScenarioStep,
    Scenario,
    Feature,
    # Data Classes - Test Data / Fixtures
    TestDataFixture,
    TestDataRegistry,
    # Data Classes - Page Object Model (POM)
    ExistingPageObject,
    PageObjectRegistry,
    # Data Classes - Environment
    EnvironmentConfig,
    EnvironmentRegistry,
    # Data Classes - Page Objects & Tests (Generated)
    PageObjectDefinition,
    TestStep,
    AutomationTestCase,
    AutomationTestSuite,
    GeneratedCypressCode,
    TestAutoResultFunc,
    # Convenience Functions
    run,
    get_context_instructions,
    parse_manual_test,
    generate_automation_suite,
    # Constants
    PANDORA_CYPRESS_REPO,
)

__all__ = [
    # Main Agent Class
    "TestAutoAgentFunc",
    # Enums
    "TestLevel",
    "ExecutionEnvironment",
    "BrowserType",
    "PageObjectType",
    "TestPriority",
    "TestType",
    "StepType",
    "StepDefinitionSource",
    # Data Classes - Context & Config
    "CypressContextReference",
    # Data Classes - Step Definitions
    "StepDefinition",
    "StepDefinitionRegistry",
    "ScenarioStep",
    "Scenario",
    "Feature",
    # Data Classes - Test Data / Fixtures
    "TestDataFixture",
    "TestDataRegistry",
    # Data Classes - Page Object Model (POM)
    "ExistingPageObject",
    "PageObjectRegistry",
    # Data Classes - Environment
    "EnvironmentConfig",
    "EnvironmentRegistry",
    # Data Classes - Page Objects & Tests (Generated)
    "PageObjectDefinition",
    "TestStep",
    "AutomationTestCase",
    "AutomationTestSuite",
    "GeneratedCypressCode",
    "TestAutoResultFunc",
    # Convenience Functions
    "run",
    "get_context_instructions",
    "parse_manual_test",
    "generate_automation_suite",
    # Constants
    "PANDORA_CYPRESS_REPO",
]
