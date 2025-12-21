"""
Test Case Writing Agent Package

Re-exports the main agent class, enums, dataclasses, and convenience functions.
Includes JIRA integration for test case management.
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
    # Constants
    QAIN_SIGNATURE,
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
    # Constants
    "QAIN_SIGNATURE",
]
