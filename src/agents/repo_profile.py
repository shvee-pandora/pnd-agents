"""
Repo Profile Module

Defines dataclasses and loader for repository profiles that enable
pnd-agents to operate on any target repository with repo-native commands.

A repo profile is a machine-readable configuration file (.claude/repo-profile.json)
that describes:
- Repository identity and metadata
- Runtime environment (Node version, package manager)
- Commands for common operations (install, validate, test, etc.)
- Key paths in the repository
- Coding constraints and conventions
- Quality gate configuration

NOTE: This module has been moved to src/agents/core/repo_profile.py
This file re-exports for backward compatibility.
"""

# Re-export from new location for backward compatibility
from .core.repo_profile import (
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

__all__ = [
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
]
