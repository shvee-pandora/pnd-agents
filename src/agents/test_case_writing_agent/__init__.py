"""
Test Case Writing Agent Package

Re-exports the main agent class, enums, dataclasses, and convenience functions.
Includes JIRA integration for test case management.

Supports Pandora JIRA Workflow Hierarchy: Initiative -> Epic -> Story -> Task
"""

from .agent import (
    # Main agent class
    TestCaseWritingAgent,
    # Enums
    TestCaseType,
    TestCasePriority,
    TestCaseFormat,
    TestLevel,
    TestingCycle,
    ComponentType,
    TestingTechnique,
    # Dataclasses
    TestStep,
    TestCase,
    TestSuite,
    TestCaseWritingResult,
    JiraWorkflowConfig,
    JiraTestCaseCreationResult,
    JiraContext,
    # Convenience functions
    run,
    generate_test_cases,
    generate_comprehensive_test_suite,
    # JIRA integration functions
    get_workflow_questions,
    generate_coverage_comment,
    generate_traceability_matrix_comment,
    generate_coverage_matrix_comment,
    create_jira_test_cases,
    run_jira_workflow,
    fetch_jira_context,
    # Constants
    QAIN_SIGNATURE,
    PANDORA_JIRA_HIERARCHY,
)

__all__ = [
    # Main agent class
    "TestCaseWritingAgent",
    # Enums
    "TestCaseType",
    "TestCasePriority",
    "TestCaseFormat",
    "TestLevel",
    "TestingCycle",
    "ComponentType",
    "TestingTechnique",
    # Dataclasses
    "TestStep",
    "TestCase",
    "TestSuite",
    "TestCaseWritingResult",
    "JiraWorkflowConfig",
    "JiraTestCaseCreationResult",
    "JiraContext",
    # Convenience functions
    "run",
    "generate_test_cases",
    "generate_comprehensive_test_suite",
    # JIRA integration functions
    "get_workflow_questions",
    "generate_coverage_comment",
    "generate_traceability_matrix_comment",
    "generate_coverage_matrix_comment",
    "create_jira_test_cases",
    "run_jira_workflow",
    "fetch_jira_context",
    # Constants
    "QAIN_SIGNATURE",
    "PANDORA_JIRA_HIERARCHY",
]
