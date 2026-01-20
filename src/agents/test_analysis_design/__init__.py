"""
Test Analysis Design Agent Package (qAIn) - v2.2

Re-exports the main agent class, enums, dataclasses, and convenience functions.
Includes JIRA integration for test case management.

Supports Pandora JIRA Workflow Hierarchy: Initiative -> Epic -> Story -> Task

v2.2 Features:
- Mandatory interactive workflow (QAIN_WORKFLOW_MANDATORY=True)
- Mandatory JIRA connection verification (verify_jira_connection)
- Workflow state tracking constants
"""

from .agent import (
    # Main agent class
    TestAnalysisDesignAgent,
    # Enums
    TestCaseType,
    TestCasePriority,
    TestCaseFormat,
    TestLevel,
    TestingCycle,
    ComponentType,
    TestingTechnique,
    QAInWorkflowMode,
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
    verify_jira_connection,
    # qAIn Interactive Workflow functions
    get_qain_initial_questions,
    get_qain_action_questions,
    get_qain_full_workflow_questions,
    analyze_ticket_for_testing_types,
    generate_testing_type_comment,
    run_qain_workflow,
    # Constants
    QAIN_SIGNATURE,
    PANDORA_JIRA_HIERARCHY,
    # v2.2 Workflow state constants
    QAIN_WORKFLOW_MANDATORY,
    WORKFLOW_STATE_KEY,
    WORKFLOW_HIERARCHY_ANSWERED,
    WORKFLOW_ACTION_ANSWERED,
    WORKFLOW_HIERARCHY_CHOICE,
    WORKFLOW_ACTION_CHOICE,
)

__all__ = [
    # Main agent class
    "TestAnalysisDesignAgent",
    # Enums
    "TestCaseType",
    "TestCasePriority",
    "TestCaseFormat",
    "TestLevel",
    "TestingCycle",
    "ComponentType",
    "TestingTechnique",
    "QAInWorkflowMode",
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
    "verify_jira_connection",
    # qAIn Interactive Workflow functions
    "get_qain_initial_questions",
    "get_qain_action_questions",
    "get_qain_full_workflow_questions",
    "analyze_ticket_for_testing_types",
    "generate_testing_type_comment",
    "run_qain_workflow",
    # Constants
    "QAIN_SIGNATURE",
    "PANDORA_JIRA_HIERARCHY",
    # v2.2 Workflow state constants
    "QAIN_WORKFLOW_MANDATORY",
    "WORKFLOW_STATE_KEY",
    "WORKFLOW_HIERARCHY_ANSWERED",
    "WORKFLOW_ACTION_ANSWERED",
    "WORKFLOW_HIERARCHY_CHOICE",
    "WORKFLOW_ACTION_CHOICE",
]
