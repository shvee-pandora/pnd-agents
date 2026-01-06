#!/usr/bin/env python3
"""
Code Singularity Demo
=====================

This script demonstrates how pnd-agents uses the Code Singularity pattern
to operate repositories deterministically via repo-profile.json.

Usage:
    # Dry run (default) - just shows what's available
    python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group

    # Run a specific command
    python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group --run-command validate

    # Show workflow definitions
    python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group --show-workflows

Requirements:
    - pnd-agents installed (pip install -e .)
    - A repository with .claude/repo-profile.json (e.g., pandora-group)
"""

import argparse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.repo_profile import load_repo_profile, discover_repo_profile
from src.agents.repo_adapter import RepoAdapter
from workflows.workflow_engine import WorkflowEngine


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    """Print a section header."""
    print(f"\n--- {title} ---")


def demo_load_profile(repo_root: str) -> RepoAdapter:
    """Step 1: Load the repo profile and create adapter."""
    print_header("STEP 1: Load Repo Profile")
    
    # Discover profile path
    profile_path = discover_repo_profile(repo_root)
    if not profile_path:
        print(f"ERROR: No repo-profile.json found in {repo_root}")
        print("Expected locations: .claude/repo-profile.json, .ai/repo-profile.json, or repo-profile.json")
        sys.exit(1)
    
    print(f"Profile found: {profile_path}")
    
    # Load profile
    profile = load_repo_profile(profile_path)
    print(f"\nRepo: {profile.name}")
    print(f"Description: {profile.repo.description}")
    print(f"Provider: {profile.repo.provider}")
    print(f"Default branch: {profile.repo.default_branch}")
    
    # Create adapter
    adapter = RepoAdapter(profile=profile, repo_root=repo_root)
    return adapter


def demo_show_commands(adapter: RepoAdapter):
    """Step 2: Show available commands."""
    print_header("STEP 2: Available Commands")
    
    print(f"\nPackage manager: {adapter.package_manager}")
    print(f"Node version: {adapter.profile.runtime.node_version}")
    
    print_section("Commands from repo-profile.json")
    commands = ['install', 'validate', 'lint', 'lint_fix', 'typecheck', 'format', 'test', 'build', 'dev', 'storybook']
    for cmd in commands:
        value = adapter.get_command(cmd)
        if value:
            print(f"  {cmd:12} -> {value}")


def demo_show_paths(adapter: RepoAdapter):
    """Step 3: Show resolved paths."""
    print_header("STEP 3: Resolved Paths")
    
    print_section("Key paths (resolved to absolute)")
    paths = ['components', 'atoms', 'molecules', 'organisms', 'services', 
             'content_mapping', 'coding_standards', 'tests', 'hooks', 'types']
    for path_name in paths:
        resolved = adapter.resolve_path(path_name)
        if resolved:
            # Show relative path for readability
            rel_path = os.path.relpath(resolved, adapter.repo_root)
            print(f"  {path_name:18} -> {rel_path}")


def demo_show_constraints(adapter: RepoAdapter):
    """Step 4: Show coding constraints."""
    print_header("STEP 4: Coding Constraints")
    
    print_section("TypeScript")
    print(f"  Use type over interface: {adapter.should_use_type_over_interface()}")
    print(f"  Props naming convention: {adapter.get_props_naming()}")
    
    print_section("React")
    print(f"  Server components default: {adapter.is_server_components_default()}")
    print(f"  Client directive: '{adapter.get_client_directive()}'")
    print(f"  Destructure props in body: {adapter.should_destructure_props_in_body()}")
    
    print_section("Atomic Design")
    print(f"  Levels: {adapter.get_atomic_levels()}")
    structure = adapter.get_component_structure()
    if structure:
        print(f"  Component structure:")
        for item in structure:
            print(f"    - {item}")


def demo_show_quality(adapter: RepoAdapter):
    """Step 5: Show quality gates."""
    print_header("STEP 5: Quality Gates")
    
    print_section("SonarCloud")
    print(f"  Project key: {adapter.get_sonar_project_key()}")
    
    print_section("Required checks")
    for check in adapter.get_required_checks():
        print(f"  - {check}")


def demo_workflow_context(adapter: RepoAdapter):
    """Step 6: Show workflow context injection."""
    print_header("STEP 6: WorkflowEngine Integration")
    
    # Create engine with adapter
    engine = WorkflowEngine(repo_adapter=adapter)
    
    # Create a sample workflow
    context = engine.create_workflow("Fix validate failures in the repository")
    
    print(f"\nWorkflow ID: {context.workflow_id}")
    print(f"Task type detected: {context.task_type.value}")
    print(f"Pipeline: {' -> '.join(context.pipeline)}")
    
    print_section("Injected repo context (available to all agents)")
    print(f"  metadata['repo_name']: {context.metadata.get('repo_name')}")
    print(f"  metadata['repo_root']: {context.metadata.get('repo_root')}")
    
    repo_ctx = context.metadata.get('repo_context', {})
    print(f"  metadata['repo_context']['commands']: {list(repo_ctx.get('commands', {}).keys())}")
    
    constraints = repo_ctx.get('constraints', {})
    print(f"  metadata['repo_context']['constraints']:")
    print(f"    - use_type_over_interface: {constraints.get('use_type_over_interface')}")
    print(f"    - server_components_default: {constraints.get('server_components_default')}")
    print(f"    - atomic_levels: {constraints.get('atomic_levels')}")


def demo_show_workflows(adapter: RepoAdapter):
    """Show available workflow definitions."""
    print_header("Available Workflow Definitions")
    
    workflows = adapter.get_workflows()
    if not workflows:
        print("\nNo workflows defined in repo-profile.json")
        return
    
    print(f"\nFound {len(workflows)} workflow(s):")
    for workflow_path in workflows:
        workflow_name = os.path.basename(workflow_path).replace('.yaml', '')
        full_path = os.path.join(adapter.repo_root, workflow_path)
        exists = os.path.exists(full_path)
        status = "OK" if exists else "NOT FOUND"
        print(f"  [{status}] {workflow_name}: {workflow_path}")
    
    print("\nNote: These are automation-ready playbooks. An executor needs to be")
    print("wired to parse and run these YAML workflows for full automation.")


def demo_run_command(adapter: RepoAdapter, command_name: str):
    """Run a command via the adapter."""
    print_header(f"Running Command: {command_name}")
    
    cmd = adapter.get_command(command_name)
    if not cmd:
        print(f"ERROR: Command '{command_name}' not found in repo profile")
        return
    
    print(f"\nCommand: {cmd}")
    print(f"Working directory: {adapter.repo_root}")
    print("\nExecuting... (this may take a moment)")
    print("-" * 40)
    
    result = adapter.run_command(command_name, timeout=300)
    
    print("-" * 40)
    print(f"\nResult: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"Exit code: {result.exit_code}")
    print(f"Duration: {result.duration_ms:.0f}ms")
    
    if result.stdout:
        print(f"\nStdout (last 1000 chars):\n{result.stdout[-1000:]}")
    
    if not result.success and result.stderr:
        print(f"\nStderr (last 500 chars):\n{result.stderr[-500:]}")


def main():
    parser = argparse.ArgumentParser(
        description="Code Singularity Demo - Demonstrate repo-profile.json usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show all repo information (dry run)
  python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group

  # Run the validate command
  python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group --run-command validate

  # Show available workflows
  python examples/code_singularity_demo.py --repo-root ~/repos/pandora-group --show-workflows
        """
    )
    parser.add_argument(
        '--repo-root', '-r',
        required=True,
        help='Path to the repository root (must contain .claude/repo-profile.json)'
    )
    parser.add_argument(
        '--run-command', '-c',
        help='Run a specific command (e.g., validate, lint, test)'
    )
    parser.add_argument(
        '--show-workflows', '-w',
        action='store_true',
        help='Show available workflow definitions'
    )
    
    args = parser.parse_args()
    
    # Expand user path
    repo_root = os.path.expanduser(args.repo_root)
    
    if not os.path.isdir(repo_root):
        print(f"ERROR: Repository root not found: {repo_root}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("  CODE SINGULARITY DEMO")
    print("  Demonstrating deterministic repo operations via repo-profile.json")
    print("=" * 60)
    
    # Load profile and create adapter
    adapter = demo_load_profile(repo_root)
    
    if args.show_workflows:
        demo_show_workflows(adapter)
    elif args.run_command:
        demo_run_command(adapter, args.run_command)
    else:
        # Full demo
        demo_show_commands(adapter)
        demo_show_paths(adapter)
        demo_show_constraints(adapter)
        demo_show_quality(adapter)
        demo_workflow_context(adapter)
        demo_show_workflows(adapter)
    
    print("\n" + "=" * 60)
    print("  DEMO COMPLETE")
    print("=" * 60)
    print("\nThe Code Singularity pattern enables AI agents to operate any")
    print("repository with a repo-profile.json deterministically, without")
    print("hardcoding commands, paths, or conventions.")
    print()


if __name__ == '__main__':
    main()
