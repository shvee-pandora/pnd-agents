"""
Centralized Coding Standards and Sonar Rules for PND Agents

This module provides a single source of truth for:
- Sonar rules and their fixes
- Pandora coding standards
- Quality gate requirements
- Coverage targets

All agents (Unit Test, Code Review, Sonar Validation) should import from this module
to ensure consistent enforcement of standards.

NOTE: This module has been moved to src/agents/core/coding_standards.py
This file re-exports for backward compatibility.
"""

# Re-export from new location for backward compatibility
from .core.coding_standards import (
    Severity,
    SonarRule,
    CodingStandard,
    QualityGates,
    SONAR_RULES,
    REPO_IGNORED_RULES,
    CODING_STANDARDS,
    DEFAULT_QUALITY_GATES,
    TEST_GENERATION_LIMITS,
    CODE_REVIEW_LIMITS,
    get_enforced_rules,
    get_rule_by_id,
    get_coding_standards,
    check_quality_gates,
    passes_all_quality_gates,
    get_pre_generation_checklist,
)

__all__ = [
    "Severity",
    "SonarRule",
    "CodingStandard",
    "QualityGates",
    "SONAR_RULES",
    "REPO_IGNORED_RULES",
    "CODING_STANDARDS",
    "DEFAULT_QUALITY_GATES",
    "TEST_GENERATION_LIMITS",
    "CODE_REVIEW_LIMITS",
    "get_enforced_rules",
    "get_rule_by_id",
    "get_coding_standards",
    "check_quality_gates",
    "passes_all_quality_gates",
    "get_pre_generation_checklist",
]
