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
"""

import logging
import os
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .repo_profile import (
    RepoProfile,
    load_repo_profile,
    load_repo_profile_from_root,
)

logger = logging.getLogger("pnd_agents.repo_adapter")


@dataclass
class CommandResult:
    """Result of running a command."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    command: str
    duration_ms: float = 0


@dataclass
class RepoAdapter:
    """
    Adapter for operating on a target repository.
    
    The adapter provides a normalized interface for:
    - Running repository commands (install, validate, test, etc.)
    - Resolving paths relative to repo root
    - Checking coding constraints
    - Getting quality gate configuration
    """
    
    profile: RepoProfile
    repo_root: str
    _env_initialized: bool = field(default=False, repr=False)
    
    @classmethod
    def from_repo_root(cls, repo_root: str) -> Optional["RepoAdapter"]:
        """
        Create a RepoAdapter from a repository root directory.
        
        Args:
            repo_root: Path to the repository root.
            
        Returns:
            RepoAdapter instance, or None if no profile found.
        """
        profile = load_repo_profile_from_root(repo_root)
        if profile:
            return cls(profile=profile, repo_root=repo_root)
        return None
    
    @classmethod
    def from_profile_path(cls, profile_path: str, repo_root: Optional[str] = None) -> "RepoAdapter":
        """
        Create a RepoAdapter from a profile file path.
        
        Args:
            profile_path: Path to the repo-profile.json file.
            repo_root: Optional repo root (defaults to parent of .claude folder).
            
        Returns:
            RepoAdapter instance.
        """
        profile = load_repo_profile(profile_path)
        
        if repo_root is None:
            # Infer repo root from profile path
            # e.g., /path/to/repo/.claude/repo-profile.json -> /path/to/repo
            repo_root = os.path.dirname(os.path.dirname(profile_path))
        
        return cls(profile=profile, repo_root=repo_root)
    
    @property
    def name(self) -> str:
        """Get the repository name."""
        return self.profile.name
    
    @property
    def package_manager(self) -> str:
        """Get the package manager."""
        return self.profile.package_manager
    
    def get_command(self, name: str) -> Optional[str]:
        """
        Get a command by name.
        
        Args:
            name: Command name (install, validate, lint, test, etc.)
            
        Returns:
            The command string, or None if not defined.
        """
        cmd = self.profile.commands.get_command(name)
        if cmd:
            return cmd
        
        # Fallback commands based on package manager
        pm = self.package_manager
        fallbacks = {
            "install": f"{pm} install",
            "validate": f"{pm} run validate",
            "lint": f"{pm} run lint",
            "lint_fix": f"{pm} run lint:fix",
            "typecheck": f"{pm} run typecheck",
            "format": f"{pm} run format",
            "test": f"{pm} test",
            "build": f"{pm} run build",
            "dev": f"{pm} run dev",
        }
        
        return fallbacks.get(name)
    
    def has_command(self, name: str) -> bool:
        """Check if a command is available."""
        return self.get_command(name) is not None
    
    def resolve_path(self, name: str) -> Optional[str]:
        """
        Resolve a path by name relative to repo root.
        
        Args:
            name: Path name (components, atoms, tests, etc.)
            
        Returns:
            Absolute path, or None if not defined.
        """
        return self.profile.paths.resolve_path(name, self.repo_root)
    
    def get_relative_path(self, name: str) -> Optional[str]:
        """
        Get a relative path by name.
        
        Args:
            name: Path name.
            
        Returns:
            Relative path from repo root, or None if not defined.
        """
        return self.profile.paths.get_path(name)
    
    def run_command(
        self,
        name: str,
        extra_args: Optional[List[str]] = None,
        timeout: int = 300,
        capture_output: bool = True
    ) -> CommandResult:
        """
        Run a repository command.
        
        Args:
            name: Command name (install, validate, test, etc.)
            extra_args: Additional arguments to append.
            timeout: Command timeout in seconds.
            capture_output: Whether to capture stdout/stderr.
            
        Returns:
            CommandResult with execution details.
        """
        import time
        
        cmd = self.get_command(name)
        if not cmd:
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Command '{name}' not found in repo profile",
                command=""
            )
        
        # Append extra args
        if extra_args:
            cmd = f"{cmd} {' '.join(extra_args)}"
        
        # Initialize environment if needed
        env_cmds = []
        if not self._env_initialized and self.profile.runtime.env_bootstrap:
            env_cmds = self.profile.runtime.env_bootstrap
        
        # Build full command
        full_cmd = " && ".join(env_cmds + [cmd]) if env_cmds else cmd
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                cwd=self.repo_root,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            self._env_initialized = True
            
            return CommandResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                command=full_cmd,
                duration_ms=duration_ms
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                command=full_cmd,
                duration_ms=timeout * 1000
            )
        except Exception as e:
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                command=full_cmd
            )
    
    def should_use_type_over_interface(self) -> bool:
        """Check if types should be used over interfaces."""
        return self.profile.constraints.typescript.use_type_over_interface
    
    def should_destructure_props_in_body(self) -> bool:
        """Check if props should be destructured in function body."""
        return self.profile.constraints.react.props_destructure_in_body
    
    def is_server_components_default(self) -> bool:
        """Check if server components are the default."""
        return self.profile.constraints.react.server_components_default
    
    def get_client_directive(self) -> str:
        """Get the client component directive."""
        return self.profile.constraints.react.client_directive
    
    def get_props_naming(self) -> str:
        """Get the props type naming convention."""
        return self.profile.constraints.typescript.props_naming
    
    def get_atomic_levels(self) -> List[str]:
        """Get the atomic design levels."""
        return self.profile.constraints.atomic_design.levels
    
    def get_component_structure(self) -> List[str]:
        """Get the expected component file structure."""
        return self.profile.constraints.atomic_design.component_structure
    
    def get_sonar_project_key(self) -> str:
        """Get the SonarCloud/SonarQube project key."""
        return self.profile.quality.sonar.project_key
    
    def get_required_checks(self) -> List[str]:
        """Get the required quality checks."""
        return self.profile.quality.required_checks
    
    def get_workflows(self) -> List[str]:
        """Get the list of workflow file paths."""
        return self.profile.workflows
    
    def get_workflow_path(self, workflow_name: str) -> Optional[str]:
        """
        Get the path to a workflow file by name.
        
        Args:
            workflow_name: Name of the workflow (e.g., "fix-ci").
            
        Returns:
            Absolute path to the workflow file, or None if not found.
        """
        for workflow_path in self.profile.workflows:
            if workflow_name in workflow_path:
                return os.path.join(self.repo_root, workflow_path)
        return None
    
    def get_context_for_agent(self) -> Dict[str, Any]:
        """
        Get context information for agents.
        
        Returns a dictionary with all relevant information that agents
        need to operate on this repository.
        """
        return {
            "repo_name": self.name,
            "repo_root": self.repo_root,
            "package_manager": self.package_manager,
            "commands": {
                "install": self.get_command("install"),
                "validate": self.get_command("validate"),
                "lint": self.get_command("lint"),
                "lint_fix": self.get_command("lint_fix"),
                "typecheck": self.get_command("typecheck"),
                "test": self.get_command("test"),
                "build": self.get_command("build"),
            },
            "paths": {
                "components": self.resolve_path("components"),
                "atoms": self.resolve_path("atoms"),
                "molecules": self.resolve_path("molecules"),
                "organisms": self.resolve_path("organisms"),
                "tests": self.resolve_path("tests"),
                "coding_standards": self.resolve_path("coding_standards"),
            },
            "constraints": {
                "use_type_over_interface": self.should_use_type_over_interface(),
                "props_destructure_in_body": self.should_destructure_props_in_body(),
                "server_components_default": self.is_server_components_default(),
                "client_directive": self.get_client_directive(),
                "props_naming": self.get_props_naming(),
                "atomic_levels": self.get_atomic_levels(),
            },
            "quality": {
                "sonar_project_key": self.get_sonar_project_key(),
                "required_checks": self.get_required_checks(),
            }
        }
    
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """
        Validate that the repository environment is properly set up.
        
        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues = []
        
        # Check repo root exists
        if not os.path.isdir(self.repo_root):
            issues.append(f"Repository root does not exist: {self.repo_root}")
            return False, issues
        
        # Check package.json exists (for Node.js projects)
        package_json = os.path.join(self.repo_root, "package.json")
        if not os.path.exists(package_json):
            issues.append("package.json not found in repo root")
        
        # Check node_modules exists
        node_modules = os.path.join(self.repo_root, "node_modules")
        if not os.path.isdir(node_modules):
            issues.append("node_modules not found - run install command first")
        
        # Check coding standards file exists
        coding_standards = self.resolve_path("coding_standards")
        if coding_standards and not os.path.exists(coding_standards):
            issues.append(f"Coding standards file not found: {coding_standards}")
        
        return len(issues) == 0, issues


# Registry of known repo profiles for quick lookup
KNOWN_REPOS: Dict[str, str] = {
    "pandora-group": "~/repos/pandora-group/.claude/repo-profile.json",
}


def get_adapter_for_repo(repo_name: str) -> Optional[RepoAdapter]:
    """
    Get a RepoAdapter for a known repository by name.
    
    Args:
        repo_name: Name of the repository.
        
    Returns:
        RepoAdapter instance, or None if not found.
    """
    if repo_name in KNOWN_REPOS:
        profile_path = os.path.expanduser(KNOWN_REPOS[repo_name])
        if os.path.exists(profile_path):
            return RepoAdapter.from_profile_path(profile_path)
    
    # Try to find in common locations
    common_roots = [
        os.path.expanduser(f"~/repos/{repo_name}"),
        os.path.expanduser(f"~/{repo_name}"),
        f"/home/ubuntu/repos/{repo_name}",
    ]
    
    for root in common_roots:
        if os.path.isdir(root):
            adapter = RepoAdapter.from_repo_root(root)
            if adapter:
                return adapter
    
    return None
