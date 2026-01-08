#!/usr/bin/env python3
"""
Code Singularity End-to-End Demo

This script demonstrates the full Code Singularity pattern where agents
use repo_context from repo-profile.json to operate deterministically.

The demo shows:
1. Loading a repo profile (pandora-group)
2. Creating a TaskManagerAgent with repo context
3. Running the frontend_agent which uses repo_context for:
   - Determining correct file paths (lib/components/atoms vs src/components)
   - Applying coding constraints (Props naming, server components, etc.)
   - Providing validation commands (pnpm validate vs npm run lint)
4. Running the code_review_agent which uses repo_context for:
   - Building repo-specific review suggestions
   - Providing correct validation commands

Usage:
    python examples/code_singularity_e2e_demo.py --repo-root ~/repos/pandora-group
    python examples/code_singularity_e2e_demo.py --repo-root ~/repos/pandora-group --task "Create a Badge atom component"
"""

import argparse
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.repo_profile import load_repo_profile, discover_repo_profile
from src.agents.repo_adapter import RepoAdapter
from workflows.workflow_engine import WorkflowEngine
from workflows.agent_dispatcher import AgentDispatcher


def print_section(title: str, char: str = "="):
    """Print a section header."""
    print(f"\n{char * 60}")
    print(f"  {title}")
    print(f"{char * 60}\n")


def print_json(data: dict, indent: int = 2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


def run_demo(repo_root: str, task: str = None):
    """
    Run the end-to-end Code Singularity demo.
    
    Args:
        repo_root: Path to the target repository (e.g., pandora-group)
        task: Optional task description for the frontend agent
    """
    print_section("CODE SINGULARITY END-TO-END DEMO")
    print(f"Target Repository: {repo_root}")
    
    # Step 1: Discover and load repo profile
    print_section("STEP 1: Discover Repo Profile", "-")
    
    profile_path = discover_repo_profile(repo_root)
    if not profile_path:
        print(f"ERROR: No repo-profile.json found in {repo_root}")
        print("The Code Singularity pattern requires a .claude/repo-profile.json file.")
        return False
    
    print(f"Found profile: {profile_path}")
    profile = load_repo_profile(profile_path)
    print(f"Loaded profile for: {profile.name}")
    print(f"Package manager: {profile.package_manager}")
    print(f"Node version: {profile.runtime.node_version}")
    
    # Step 2: Create RepoAdapter
    print_section("STEP 2: Create RepoAdapter", "-")
    
    adapter = RepoAdapter(profile=profile, repo_root=repo_root)
    print(f"RepoAdapter created for: {adapter.name}")
    print(f"Repo root: {adapter.repo_root}")
    
    # Show available commands
    print("\nAvailable commands from repo profile:")
    for cmd_name in ["install", "validate", "lint", "test", "build"]:
        cmd = adapter.get_command(cmd_name)
        if cmd:
            print(f"  {cmd_name}: {cmd}")
    
    # Show resolved paths
    print("\nResolved paths from repo profile:")
    for path_name in ["components", "atoms", "molecules", "organisms", "content_mapping"]:
        try:
            resolved = adapter.resolve_path(path_name)
            if resolved:
                # Show relative path for readability
                rel_path = os.path.relpath(resolved, repo_root)
                print(f"  {path_name}: {rel_path}")
        except Exception:
            pass
    
    # Step 3: Create WorkflowEngine with RepoAdapter
    print_section("STEP 3: Create WorkflowEngine with RepoAdapter", "-")
    
    engine = WorkflowEngine()
    engine.set_repo_adapter(adapter)
    print("WorkflowEngine created with RepoAdapter attached")
    
    # Create a workflow context - this injects repo_context into metadata
    default_task = task or "Create a Badge atom component"
    workflow_context = engine.create_workflow(default_task)
    
    print(f"\nWorkflow created: {workflow_context.workflow_id}")
    print(f"Task: {default_task}")
    
    # Show the injected repo_context
    repo_context = workflow_context.metadata.get("repo_context", {})
    print("\nRepo context injected into workflow metadata:")
    print(f"  repo_name: {workflow_context.metadata.get('repo_name')}")
    print(f"  commands available: {list(repo_context.get('commands', {}).keys())}")
    print(f"  paths available: {list(repo_context.get('paths', {}).keys())}")
    print(f"  constraints available: {list(repo_context.get('constraints', {}).keys())}")
    
    # Step 4: Run frontend_agent with repo_context
    print_section("STEP 4: Run frontend_agent with repo_context", "-")
    
    dispatcher = AgentDispatcher()
    
    # Build context for frontend agent (simulating workflow execution)
    frontend_context = {
        "task": default_task,
        "input": {
            "previous_output": {}
        },
        "metadata": workflow_context.metadata
    }
    
    print("Executing frontend_agent handler...")
    print(f"Task: {default_task}")
    
    frontend_result = dispatcher.execute("frontend", frontend_context)
    
    print("\nFrontend Agent Result:")
    print(f"  Status: {frontend_result.status}")
    print(f"  Next agent: {frontend_result.next}")
    
    if frontend_result.data:
        print("\n  Component Spec:")
        spec = frontend_result.data.get("component_spec", {})
        print(f"    Name: {spec.get('name')}")
        print(f"    Props type name: {spec.get('props_type_name')}")
        print(f"    Use type keyword: {spec.get('use_type_keyword')}")
        print(f"    Is server component: {spec.get('is_server_component')}")
        
        print("\n  Files to generate (using repo_context paths):")
        for f in frontend_result.data.get("files_to_generate", []):
            print(f"    - {f}")
        
        print(f"\n  Atomic level detected: {frontend_result.data.get('atomic_level')}")
        
        if frontend_result.data.get("repo_context_used"):
            print("\n  CODE SINGULARITY METADATA:")
            print("    repo_context_used: True")
            print(f"    repo_name: {frontend_result.data.get('repo_name')}")
            print(f"    constraints_applied: {frontend_result.data.get('constraints_applied')}")
            print(f"    commands: {frontend_result.data.get('commands')}")
    
    # Step 5: Run code_review_agent with repo_context
    print_section("STEP 5: Run code_review_agent with repo_context", "-")
    
    # Build context for review agent (simulating workflow execution)
    review_context = {
        "task": f"Review component: {default_task}",
        "input": {
            "previous_output": frontend_result.data
        },
        "metadata": workflow_context.metadata
    }
    
    print("Executing code_review_agent handler...")
    
    review_result = dispatcher.execute("review", review_context)
    
    print("\nCode Review Agent Result:")
    print(f"  Status: {review_result.status}")
    print(f"  Next agent: {review_result.next}")
    
    if review_result.data:
        print("\n  Files reviewed:")
        for f in review_result.data.get("files_reviewed", []):
            print(f"    - {f}")
        
        print("\n  Suggestions (from repo_context constraints):")
        for s in review_result.data.get("suggestions", []):
            print(f"    - {s}")
        
        print("\n  Validation commands (from repo_context):")
        for cmd in review_result.data.get("validation_commands", []):
            print(f"    - {cmd}")
        
        if review_result.data.get("repo_context_used"):
            print("\n  CODE SINGULARITY METADATA:")
            print("    repo_context_used: True")
            print(f"    repo_name: {review_result.data.get('repo_name')}")
    
    # Summary
    print_section("DEMO SUMMARY")
    
    print("The Code Singularity pattern enables agents to:")
    print("  1. Read repo-profile.json to understand repo conventions")
    print("  2. Use correct paths (lib/components/atoms vs src/components)")
    print("  3. Apply coding constraints (Props naming, server components)")
    print("  4. Provide correct validation commands (pnpm validate)")
    print()
    print("Key benefits:")
    print("  - Deterministic behavior: Same input = same output across sessions")
    print("  - Multi-repo support: Same agent code works with different repos")
    print("  - No guessing: Agents read the contract, not hardcoded values")
    print()
    print("Files generated follow pandora-group conventions:")
    for f in frontend_result.data.get("files_to_generate", []):
        print(f"  - {f}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Code Singularity End-to-End Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run with pandora-group repo
    python examples/code_singularity_e2e_demo.py --repo-root ~/repos/pandora-group
    
    # Run with custom task
    python examples/code_singularity_e2e_demo.py --repo-root ~/repos/pandora-group --task "Create a Card molecule component"
    
    # Run with different atomic level
    python examples/code_singularity_e2e_demo.py --repo-root ~/repos/pandora-group --task "Create a Header organism component"
        """
    )
    
    parser.add_argument(
        "--repo-root",
        required=True,
        help="Path to the target repository (must have .claude/repo-profile.json)"
    )
    
    parser.add_argument(
        "--task",
        default=None,
        help="Task description for the frontend agent (default: 'Create a Badge atom component')"
    )
    
    args = parser.parse_args()
    
    # Expand user path
    repo_root = os.path.expanduser(args.repo_root)
    
    if not os.path.isdir(repo_root):
        print(f"ERROR: Repository not found: {repo_root}")
        sys.exit(1)
    
    success = run_demo(repo_root, args.task)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
