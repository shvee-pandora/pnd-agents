"""
Repo Adapter Module

Provides an adapter layer between pnd-agents and target repositories.
The adapter normalizes commands, paths, and constraints from a RepoProfile
so that the WorkflowEngine can operate on any repository deterministically.

Usage:
    adapter = RepoAdapter.from_repo_root("/path/to/repo")
    
    # Get normalized commands
    install_cmd = adapter.get_command("install")
    validate_cmd = adapter.get_command("validate")
    
    # Get resolved paths
    components_path = adapter.resolve_path("components")
    
    # Check constraints
    if adapter.should_use_type_over_interface():
        # Generate type instead of interface
        pass

NOTE: This module has been moved to src/agents/core/repo_adapter.py
This file re-exports for backward compatibility.
"""

# Re-export from new location for backward compatibility
from .core.repo_adapter import (
    CommandResult,
    RepoAdapter,
    KNOWN_REPOS,
    get_adapter_for_repo,
)

__all__ = [
    "CommandResult",
    "RepoAdapter",
    "KNOWN_REPOS",
    "get_adapter_for_repo",
]
