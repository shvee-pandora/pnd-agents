"""
PND Agents Core Module

Cross-cutting utilities and base classes for all agents.
This module provides:
- coding_standards: Centralized coding standards and Sonar rules
- repo_adapter: Repository adapter for Code Singularity pattern
- repo_profile: Repository profile schema and loader
- base_agent: Base class interface for all agents
"""

from .coding_standards import (
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

from .repo_profile import (
    RepoIdentity,
    RuntimeConfig,
    RepoCommands,
    RepoPaths,
    TypeScriptConstraints,
    ReactConstraints,
    CodeStyleConstraints,
    NamingConstraints,
    AtomicDesignConstraints,
    RepoConstraints,
    SonarConfig,
    QualityConfig,
    RepoProfile,
    load_repo_profile,
    parse_repo_profile,
    discover_repo_profile,
    load_repo_profile_from_root,
)

from .repo_adapter import (
    CommandResult,
    RepoAdapter,
    KNOWN_REPOS,
    get_adapter_for_repo,
)

from .base_agent import (
    AgentResult,
    AgentContext,
    BaseAgent,
)

__all__ = [
    # coding_standards
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
    # repo_profile
    "RepoIdentity",
    "RuntimeConfig",
    "RepoCommands",
    "RepoPaths",
    "TypeScriptConstraints",
    "ReactConstraints",
    "CodeStyleConstraints",
    "NamingConstraints",
    "AtomicDesignConstraints",
    "RepoConstraints",
    "SonarConfig",
    "QualityConfig",
    "RepoProfile",
    "load_repo_profile",
    "parse_repo_profile",
    "discover_repo_profile",
    "load_repo_profile_from_root",
    # repo_adapter
    "CommandResult",
    "RepoAdapter",
    "KNOWN_REPOS",
    "get_adapter_for_repo",
    # base_agent
    "AgentResult",
    "AgentContext",
    "BaseAgent",
]
