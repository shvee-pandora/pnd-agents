#!/usr/bin/env python3
"""
Code Singularity Agent Demo
============================

This demo shows an AI agent using the Code Singularity pattern to scaffold
a new component in pandora-group. The agent reads the repo contract and
creates files in exactly the right place with the correct structure.

Usage:
    # Dry run (default) - shows what would be created
    python examples/agent_demo.py --repo-root ~/repos/pandora-group --component Badge --level atoms

    # Execute - actually creates the files
    python examples/agent_demo.py --repo-root ~/repos/pandora-group --component Badge --level atoms --execute

    # Run validation after creating
    python examples/agent_demo.py --repo-root ~/repos/pandora-group --component Badge --level atoms --execute --validate
"""

import argparse
import os
import sys
import time
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.repo_profile import load_repo_profile, discover_repo_profile
from src.agents.repo_adapter import RepoAdapter
from workflows.workflow_engine import WorkflowEngine


# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_agent(message: str, delay: float = 0.03):
    """Print message with typing effect to simulate agent thinking."""
    prefix = f"{Colors.CYAN}[Agent]{Colors.END} "
    print(prefix, end='', flush=True)
    for char in message:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def print_step(step_num: int, title: str):
    """Print a step header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  Step {step_num}: {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {message}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.YELLOW}[INFO]{Colors.END} {message}")


def print_file_content(filename: str, content: str):
    """Print file content with syntax highlighting effect."""
    print(f"\n{Colors.CYAN}--- {filename} ---{Colors.END}")
    print(content)
    print(f"{Colors.CYAN}--- end ---{Colors.END}\n")


def generate_component_file(component_name: str, is_server: bool) -> str:
    """Generate the main component file content."""
    directive = "" if is_server else "'use client';\n\n"
    return f'''{directive}import {{ {component_name}Props }} from './types';

function {component_name}(props: {component_name}Props) {{
  const {{ children, variant = 'default', className }} = props;

  return (
    <span
      className={{`{component_name.lower()} {component_name.lower()}--${{variant}} ${{className || ''}}`}}
      data-testid="{component_name.lower()}"
    >
      {{children}}
    </span>
  );
}}

export default {component_name};
'''


def generate_types_file(component_name: str, props_naming: str) -> str:
    """Generate the types file content."""
    return f'''export type {component_name}{props_naming} = {{
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'secondary';
  className?: string;
}};
'''


def generate_test_file(component_name: str) -> str:
    """Generate the test file content."""
    return f'''import {{ render, screen }} from '@testing-library/react';
import {component_name} from '../{component_name}';

describe('{component_name}', () => {{
  it('renders children correctly', () => {{
    render(<{component_name}>Test Content</{component_name}>);
    expect(screen.getByTestId('{component_name.lower()}')).toHaveTextContent('Test Content');
  }});

  it('applies variant class', () => {{
    render(<{component_name} variant="primary">Content</{component_name}>);
    expect(screen.getByTestId('{component_name.lower()}')).toHaveClass('{component_name.lower()}--primary');
  }});

  it('applies custom className', () => {{
    render(<{component_name} className="custom-class">Content</{component_name}>);
    expect(screen.getByTestId('{component_name.lower()}')).toHaveClass('custom-class');
  }});
}});
'''


def generate_story_file(component_name: str) -> str:
    """Generate the Storybook story file content."""
    return f'''import type {{ Meta, StoryObj }} from '@storybook/react';
import {component_name} from '../{component_name}';

const meta: Meta<typeof {component_name}> = {{
  title: 'Atoms/{component_name}',
  component: {component_name},
  tags: ['autodocs'],
  argTypes: {{
    variant: {{
      control: 'select',
      options: ['default', 'primary', 'secondary'],
    }},
  }},
}};

export default meta;
type Story = StoryObj<typeof {component_name}>;

export const Default: Story = {{
  args: {{
    children: '{component_name} Text',
    variant: 'default',
  }},
}};

export const Primary: Story = {{
  args: {{
    children: '{component_name} Text',
    variant: 'primary',
  }},
}};

export const Secondary: Story = {{
  args: {{
    children: '{component_name} Text',
    variant: 'secondary',
  }},
}};
'''


def generate_mock_file(component_name: str) -> str:
    """Generate the mock file content."""
    return f'''import {{ {component_name}Props }} from '../types';

export const mock{component_name}Props: {component_name}Props = {{
  children: 'Mock {component_name}',
  variant: 'default',
}};

export const mock{component_name}Variants = {{
  default: {{ ...mock{component_name}Props, variant: 'default' as const }},
  primary: {{ ...mock{component_name}Props, variant: 'primary' as const }},
  secondary: {{ ...mock{component_name}Props, variant: 'secondary' as const }},
}};
'''


def run_demo(
    repo_root: str,
    component_name: str,
    level: str,
    execute: bool = False,
    validate: bool = False
):
    """Run the Code Singularity agent demo."""
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}  CODE SINGULARITY AGENT DEMO{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}  Task: Create '{component_name}' component in {level}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    
    time.sleep(1)
    
    # Step 1: Load repo profile
    print_step(1, "Loading Repo Contract")
    print_agent("I need to understand this repository before making changes...")
    time.sleep(0.5)
    
    profile_path = discover_repo_profile(repo_root)
    if not profile_path:
        print(f"{Colors.RED}ERROR: No repo-profile.json found{Colors.END}")
        sys.exit(1)
    
    print_agent(f"Found repo contract at: {os.path.relpath(profile_path, repo_root)}")
    profile = load_repo_profile(profile_path)
    adapter = RepoAdapter(profile=profile, repo_root=repo_root)
    
    print_info(f"Repo: {profile.name}")
    print_info(f"Package manager: {adapter.package_manager}")
    print_info(f"Node version: {profile.runtime.node_version}")
    
    # Step 2: Read constraints
    print_step(2, "Reading Coding Constraints")
    print_agent("Let me check the coding standards defined in the repo contract...")
    time.sleep(0.5)
    
    is_server = adapter.is_server_components_default()
    props_naming = adapter.get_props_naming()
    atomic_levels = adapter.get_atomic_levels()
    component_structure = adapter.get_component_structure()
    
    print_info(f"Server components by default: {is_server}")
    print_info(f"Props naming convention: {props_naming}")
    print_info(f"Atomic design levels: {atomic_levels}")
    print_info(f"Required files per component: {component_structure}")
    
    if level not in atomic_levels:
        print(f"{Colors.RED}ERROR: '{level}' is not a valid atomic level. Must be one of: {atomic_levels}{Colors.END}")
        sys.exit(1)
    
    # Step 3: Determine target path
    print_step(3, "Determining Target Location")
    print_agent(f"Looking up the canonical path for '{level}' components...")
    time.sleep(0.5)
    
    base_path = adapter.resolve_path(level)
    component_folder = component_name.lower()
    target_path = os.path.join(base_path, component_folder)
    rel_target = os.path.relpath(target_path, repo_root)
    
    print_info(f"Base path for {level}: {os.path.relpath(base_path, repo_root)}")
    print_info(f"Component folder: {rel_target}")
    
    # Step 4: Generate files
    print_step(4, "Generating Component Files")
    print_agent(f"Creating {component_name} component following the repo contract...")
    time.sleep(0.5)
    
    files_to_create = {
        f"{component_name}.tsx": generate_component_file(component_name, is_server),
        "types.ts": generate_types_file(component_name, props_naming),
        f"__tests__/{component_name}.spec.tsx": generate_test_file(component_name),
        f"__stories__/{component_name}.stories.tsx": generate_story_file(component_name),
        "__mocks__/index.ts": generate_mock_file(component_name),
    }
    
    for filename, content in files_to_create.items():
        print_info(f"Generated: {filename}")
        if not execute:
            print_file_content(filename, content[:500] + "..." if len(content) > 500 else content)
    
    # Step 5: Execute (if requested)
    if execute:
        print_step(5, "Creating Files")
        print_agent("Writing files to disk...")
        
        # Create directories
        os.makedirs(target_path, exist_ok=True)
        os.makedirs(os.path.join(target_path, "__tests__"), exist_ok=True)
        os.makedirs(os.path.join(target_path, "__stories__"), exist_ok=True)
        os.makedirs(os.path.join(target_path, "__mocks__"), exist_ok=True)
        
        for filename, content in files_to_create.items():
            filepath = os.path.join(target_path, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            print_success(f"Created: {os.path.relpath(filepath, repo_root)}")
        
        # Create index.ts for exports
        index_content = f"export {{ default as {component_name} }} from './{component_name}';\nexport type {{ {component_name}Props }} from './types';\n"
        index_path = os.path.join(target_path, "index.ts")
        with open(index_path, 'w') as f:
            f.write(index_content)
        print_success(f"Created: {os.path.relpath(index_path, repo_root)}")
    else:
        print_step(5, "Dry Run Complete")
        print_agent("This was a dry run. Use --execute to create the files.")
        print_info(f"Would create {len(files_to_create) + 1} files in: {rel_target}")
    
    # Step 6: Validate (if requested)
    if execute and validate:
        print_step(6, "Running Validation")
        print_agent(f"Running '{adapter.get_command('validate')}' to verify the changes...")
        
        result = adapter.run_command('validate', timeout=120)
        
        if result.success:
            print_success("Validation passed!")
        else:
            print(f"{Colors.RED}Validation failed (exit code: {result.exit_code}){Colors.END}")
            if result.stderr:
                print(f"Stderr: {result.stderr[:500]}")
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}  DEMO COMPLETE{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}")
    
    print_agent("The Code Singularity pattern enabled me to:")
    print(f"  1. Read the repo contract ({Colors.CYAN}repo-profile.json{Colors.END})")
    print(f"  2. Understand coding constraints ({Colors.CYAN}TypeScript, React, Atomic Design{Colors.END})")
    print(f"  3. Find the correct location ({Colors.CYAN}{rel_target}{Colors.END})")
    print(f"  4. Generate files following conventions ({Colors.CYAN}{len(files_to_create) + 1} files{Colors.END})")
    if execute and validate:
        print(f"  5. Validate the changes ({Colors.CYAN}{adapter.get_command('validate')}{Colors.END})")
    
    print(f"\n{Colors.YELLOW}No guessing. No hardcoding. Just deterministic, contract-driven behavior.{Colors.END}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Code Singularity Agent Demo - Watch an agent scaffold a component",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--repo-root', '-r',
        required=True,
        help='Path to the repository root'
    )
    parser.add_argument(
        '--component', '-c',
        required=True,
        help='Name of the component to create (PascalCase)'
    )
    parser.add_argument(
        '--level', '-l',
        default='atoms',
        choices=['atoms', 'molecules', 'organisms'],
        help='Atomic design level (default: atoms)'
    )
    parser.add_argument(
        '--execute', '-e',
        action='store_true',
        help='Actually create the files (default: dry run)'
    )
    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Run validation after creating files (requires --execute)'
    )
    
    args = parser.parse_args()
    
    repo_root = os.path.expanduser(args.repo_root)
    
    if not os.path.isdir(repo_root):
        print(f"ERROR: Repository root not found: {repo_root}")
        sys.exit(1)
    
    run_demo(
        repo_root=repo_root,
        component_name=args.component,
        level=args.level,
        execute=args.execute,
        validate=args.validate
    )


if __name__ == '__main__':
    main()
