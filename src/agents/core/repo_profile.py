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
"""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pnd_agents.repo_profile")


@dataclass
class RepoIdentity:
    """Repository identity information."""
    name: str
    description: str = ""
    default_branch: str = "main"
    provider: str = "unknown"  # github, azure_devops, gitlab, unknown
    url: str = ""


@dataclass
class RuntimeConfig:
    """Runtime environment configuration."""
    node_version: str = "20"
    package_manager: str = "pnpm"  # npm, pnpm, yarn, bun
    env_bootstrap: List[str] = field(default_factory=list)


@dataclass
class RepoCommands:
    """Commands for common repository operations."""
    install: str = ""
    validate: str = ""
    lint: str = ""
    lint_fix: str = ""
    typecheck: str = ""
    format: str = ""
    test: str = ""
    test_watch: str = ""
    build: str = ""
    dev: str = ""
    storybook: str = ""
    
    def get_command(self, name: str) -> Optional[str]:
        """Get a command by name."""
        return getattr(self, name, None)
    
    def has_command(self, name: str) -> bool:
        """Check if a command is defined."""
        cmd = self.get_command(name)
        return cmd is not None and cmd != ""


@dataclass
class RepoPaths:
    """Key paths in the repository."""
    components: str = ""
    atoms: str = ""
    molecules: str = ""
    organisms: str = ""
    services: str = ""
    hooks: str = ""
    types: str = ""
    constants: str = ""
    config: str = ""
    tests: str = ""
    stories: str = ""
    mocks: str = ""
    coding_standards: str = ""
    context: str = ""
    skills: str = ""
    workflows_doc: str = ""
    content_mapping: str = ""
    content_renderer: str = ""
    amplience: str = ""
    
    def get_path(self, name: str) -> Optional[str]:
        """Get a path by name."""
        return getattr(self, name, None)
    
    def resolve_path(self, name: str, repo_root: str) -> Optional[str]:
        """Resolve a path relative to repo root."""
        path = self.get_path(name)
        if path:
            return os.path.join(repo_root, path)
        return None


@dataclass
class TypeScriptConstraints:
    """TypeScript-specific constraints."""
    strict_mode: bool = True
    no_any: bool = True
    use_type_over_interface: bool = True
    props_naming: str = "Props"
    no_readonly_wrapper: bool = True


@dataclass
class ReactConstraints:
    """React-specific constraints."""
    server_components_default: bool = True
    client_directive: str = "use client"
    props_destructure_in_body: bool = True
    no_jsx_comments: bool = True
    early_returns: bool = True


@dataclass
class CodeStyleConstraints:
    """Code style constraints."""
    no_todo_comments: bool = True
    no_unused_variables: bool = True
    prefer_for_of: bool = True
    use_at_for_negative_index: bool = True
    avoid_negated_conditions: bool = True


@dataclass
class NamingConstraints:
    """Naming convention constraints."""
    components: str = "PascalCase"
    utilities: str = "camelCase"
    types: str = "PascalCase"
    folders: str = "kebab-case"
    tests: str = "*.spec.tsx or *.test.tsx"


@dataclass
class AtomicDesignConstraints:
    """Atomic design constraints."""
    levels: List[str] = field(default_factory=lambda: ["atoms", "molecules", "organisms"])
    component_structure: List[str] = field(default_factory=list)


@dataclass
class RepoConstraints:
    """All repository constraints."""
    typescript: TypeScriptConstraints = field(default_factory=TypeScriptConstraints)
    react: ReactConstraints = field(default_factory=ReactConstraints)
    code_style: CodeStyleConstraints = field(default_factory=CodeStyleConstraints)
    naming: NamingConstraints = field(default_factory=NamingConstraints)
    atomic_design: AtomicDesignConstraints = field(default_factory=AtomicDesignConstraints)


@dataclass
class SonarConfig:
    """SonarCloud/SonarQube configuration."""
    project_key: str = ""
    lcov_path: str = ""


@dataclass
class QualityConfig:
    """Quality gate configuration."""
    sonar: SonarConfig = field(default_factory=SonarConfig)
    required_checks: List[str] = field(default_factory=list)
    pre_commit_hooks: bool = True


@dataclass
class RepoProfile:
    """
    Complete repository profile.
    
    This is the main dataclass that represents a repo-profile.json file.
    It contains all the information needed for pnd-agents to operate
    on a target repository.
    """
    schema_version: str = "1.0.0"
    repo: RepoIdentity = field(default_factory=lambda: RepoIdentity(name="unknown"))
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    commands: RepoCommands = field(default_factory=RepoCommands)
    paths: RepoPaths = field(default_factory=RepoPaths)
    constraints: RepoConstraints = field(default_factory=RepoConstraints)
    quality: QualityConfig = field(default_factory=QualityConfig)
    workflows: List[str] = field(default_factory=list)
    import_aliases: Dict[str, str] = field(default_factory=dict)
    environment_variables: Dict[str, List[str]] = field(default_factory=dict)
    
    @property
    def name(self) -> str:
        """Get the repository name."""
        return self.repo.name
    
    @property
    def package_manager(self) -> str:
        """Get the package manager."""
        return self.runtime.package_manager
    
    def get_install_command(self) -> str:
        """Get the install command."""
        if self.commands.install:
            return self.commands.install
        # Fallback based on package manager
        pm = self.runtime.package_manager
        return f"{pm} install"
    
    def get_validate_command(self) -> str:
        """Get the validate command."""
        if self.commands.validate:
            return self.commands.validate
        # Fallback
        return f"{self.runtime.package_manager} run validate"
    
    def get_test_command(self) -> str:
        """Get the test command."""
        if self.commands.test:
            return self.commands.test
        return f"{self.runtime.package_manager} test"


def _parse_nested_dataclass(data: Dict[str, Any], cls: type) -> Any:
    """Parse a nested dataclass from a dictionary."""
    if data is None:
        return cls()
    
    # Get field names and types from the dataclass
    field_values = {}
    for field_name in cls.__dataclass_fields__:
        if field_name in data:
            field_values[field_name] = data[field_name]
    
    return cls(**field_values)


def load_repo_profile(profile_path: str) -> RepoProfile:
    """
    Load a repository profile from a JSON file.
    
    Args:
        profile_path: Path to the repo-profile.json file.
        
    Returns:
        RepoProfile instance.
        
    Raises:
        FileNotFoundError: If the profile file doesn't exist.
        json.JSONDecodeError: If the file is not valid JSON.
        ValueError: If the profile is invalid.
    """
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Repo profile not found: {profile_path}")
    
    with open(profile_path, "r") as f:
        data = json.load(f)
    
    return parse_repo_profile(data)


def parse_repo_profile(data: Dict[str, Any]) -> RepoProfile:
    """
    Parse a repository profile from a dictionary.
    
    Args:
        data: Dictionary containing profile data.
        
    Returns:
        RepoProfile instance.
    """
    # Parse repo identity
    repo_data = data.get("repo", {})
    repo = RepoIdentity(
        name=repo_data.get("name", "unknown"),
        description=repo_data.get("description", ""),
        default_branch=repo_data.get("default_branch", "main"),
        provider=repo_data.get("provider", "unknown"),
        url=repo_data.get("url", "")
    )
    
    # Parse runtime config
    runtime_data = data.get("runtime", {})
    runtime = RuntimeConfig(
        node_version=runtime_data.get("node_version", "20"),
        package_manager=runtime_data.get("package_manager", "pnpm"),
        env_bootstrap=runtime_data.get("env_bootstrap", [])
    )
    
    # Parse commands
    commands_data = data.get("commands", {})
    commands = RepoCommands(
        install=commands_data.get("install", ""),
        validate=commands_data.get("validate", ""),
        lint=commands_data.get("lint", ""),
        lint_fix=commands_data.get("lint_fix", ""),
        typecheck=commands_data.get("typecheck", ""),
        format=commands_data.get("format", ""),
        test=commands_data.get("test", ""),
        test_watch=commands_data.get("test_watch", ""),
        build=commands_data.get("build", ""),
        dev=commands_data.get("dev", ""),
        storybook=commands_data.get("storybook", "")
    )
    
    # Parse paths
    paths_data = data.get("paths", {})
    paths = RepoPaths(
        components=paths_data.get("components", ""),
        atoms=paths_data.get("atoms", ""),
        molecules=paths_data.get("molecules", ""),
        organisms=paths_data.get("organisms", ""),
        services=paths_data.get("services", ""),
        hooks=paths_data.get("hooks", ""),
        types=paths_data.get("types", ""),
        constants=paths_data.get("constants", ""),
        config=paths_data.get("config", ""),
        tests=paths_data.get("tests", ""),
        stories=paths_data.get("stories", ""),
        mocks=paths_data.get("mocks", ""),
        coding_standards=paths_data.get("coding_standards", ""),
        context=paths_data.get("context", ""),
        skills=paths_data.get("skills", ""),
        workflows_doc=paths_data.get("workflows_doc", ""),
        content_mapping=paths_data.get("content_mapping", ""),
        content_renderer=paths_data.get("content_renderer", ""),
        amplience=paths_data.get("amplience", "")
    )
    
    # Parse constraints
    constraints_data = data.get("constraints", {})
    
    ts_data = constraints_data.get("typescript", {})
    typescript = TypeScriptConstraints(
        strict_mode=ts_data.get("strict_mode", True),
        no_any=ts_data.get("no_any", True),
        use_type_over_interface=ts_data.get("use_type_over_interface", True),
        props_naming=ts_data.get("props_naming", "Props"),
        no_readonly_wrapper=ts_data.get("no_readonly_wrapper", True)
    )
    
    react_data = constraints_data.get("react", {})
    react = ReactConstraints(
        server_components_default=react_data.get("server_components_default", True),
        client_directive=react_data.get("client_directive", "use client"),
        props_destructure_in_body=react_data.get("props_destructure_in_body", True),
        no_jsx_comments=react_data.get("no_jsx_comments", True),
        early_returns=react_data.get("early_returns", True)
    )
    
    style_data = constraints_data.get("code_style", {})
    code_style = CodeStyleConstraints(
        no_todo_comments=style_data.get("no_todo_comments", True),
        no_unused_variables=style_data.get("no_unused_variables", True),
        prefer_for_of=style_data.get("prefer_for_of", True),
        use_at_for_negative_index=style_data.get("use_at_for_negative_index", True),
        avoid_negated_conditions=style_data.get("avoid_negated_conditions", True)
    )
    
    naming_data = constraints_data.get("naming", {})
    naming = NamingConstraints(
        components=naming_data.get("components", "PascalCase"),
        utilities=naming_data.get("utilities", "camelCase"),
        types=naming_data.get("types", "PascalCase"),
        folders=naming_data.get("folders", "kebab-case"),
        tests=naming_data.get("tests", "*.spec.tsx or *.test.tsx")
    )
    
    atomic_data = constraints_data.get("atomic_design", {})
    atomic_design = AtomicDesignConstraints(
        levels=atomic_data.get("levels", ["atoms", "molecules", "organisms"]),
        component_structure=atomic_data.get("component_structure", [])
    )
    
    constraints = RepoConstraints(
        typescript=typescript,
        react=react,
        code_style=code_style,
        naming=naming,
        atomic_design=atomic_design
    )
    
    # Parse quality config
    quality_data = data.get("quality", {})
    sonar_data = quality_data.get("sonar", {})
    sonar = SonarConfig(
        project_key=sonar_data.get("project_key", ""),
        lcov_path=sonar_data.get("lcov_path", "")
    )
    quality = QualityConfig(
        sonar=sonar,
        required_checks=quality_data.get("required_checks", []),
        pre_commit_hooks=quality_data.get("pre_commit_hooks", True)
    )
    
    return RepoProfile(
        schema_version=data.get("schema_version", "1.0.0"),
        repo=repo,
        runtime=runtime,
        commands=commands,
        paths=paths,
        constraints=constraints,
        quality=quality,
        workflows=data.get("workflows", []),
        import_aliases=data.get("import_aliases", {}),
        environment_variables=data.get("environment_variables", {})
    )


def discover_repo_profile(repo_root: str) -> Optional[str]:
    """
    Discover the repo profile path in a repository.
    
    Looks for repo-profile.json in common locations:
    - .claude/repo-profile.json
    - .ai/repo-profile.json
    - repo-profile.json
    
    Args:
        repo_root: Root directory of the repository.
        
    Returns:
        Path to the profile file, or None if not found.
    """
    search_paths = [
        ".claude/repo-profile.json",
        ".ai/repo-profile.json",
        "repo-profile.json"
    ]
    
    for rel_path in search_paths:
        full_path = os.path.join(repo_root, rel_path)
        if os.path.exists(full_path):
            return full_path
    
    return None


def load_repo_profile_from_root(repo_root: str) -> Optional[RepoProfile]:
    """
    Load a repository profile by discovering it in the repo root.
    
    Args:
        repo_root: Root directory of the repository.
        
    Returns:
        RepoProfile instance, or None if no profile found.
    """
    profile_path = discover_repo_profile(repo_root)
    if profile_path:
        try:
            return load_repo_profile(profile_path)
        except Exception as e:
            logger.warning(f"Failed to load repo profile from {profile_path}: {e}")
    return None
