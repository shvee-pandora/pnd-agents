#!/usr/bin/env python3
"""
PND Agents CLI

One-command setup and configuration for PG AI Squad agents.
"""

import argparse
import json
import os
import platform
import sys
from pathlib import Path
from typing import Optional


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def color(text: str, color_code: str) -> str:
    """Apply color to text if terminal supports it."""
    if sys.stdout.isatty():
        return f"{color_code}{text}{Colors.ENDC}"
    return text


# Agent definitions
AGENTS = {
    "task-manager": {
        "name": "Task Manager Agent",
        "description": "Orchestrates tasks, decomposes work, routes to other agents",
        "role": "orchestrator",
        "default": True,
    },
    "frontend-engineer": {
        "name": "Frontend Engineer Agent",
        "description": "React/Next.js components, Storybook, accessibility",
        "role": "specialist",
        "default": True,
    },
    "amplience-cms": {
        "name": "Amplience CMS Agent",
        "description": "Content types, JSON schemas, CMS integration",
        "role": "specialist",
        "default": False,
    },
    "code-review": {
        "name": "Code Review Agent",
        "description": "Code standards validation, PR reviews",
        "role": "validator",
        "default": True,
    },
    "performance": {
        "name": "Performance Agent",
        "description": "HAR analysis, Core Web Vitals, optimization",
        "role": "specialist",
        "default": False,
    },
    "qa": {
        "name": "QA Agent",
        "description": "Unit tests, integration tests, Playwright E2E",
        "role": "validator",
        "default": True,
    },
    "backend": {
        "name": "Backend Agent",
        "description": "API routes, Server Components, mock APIs",
        "role": "specialist",
        "default": False,
    },
    "figma-reader": {
        "name": "Figma Reader Agent",
        "description": "Extract component metadata from Figma designs",
        "role": "specialist",
        "default": True,
    },
    "broken-experience-detector": {
        "name": "Broken Experience Detector Agent",
        "description": "Scan URLs for performance, accessibility, SEO, and UX issues",
        "role": "specialist",
        "default": True,
    },
}

# Environment variables
ENV_VARS = {
    "FIGMA_ACCESS_TOKEN": {
        "description": "Figma API token for reading designs",
        "required_for": ["figma-reader", "frontend-engineer"],
        "sensitive": True,
    },
    "AMPLIENCE_HUB_NAME": {
        "description": "Amplience hub name",
        "required_for": ["amplience-cms"],
        "sensitive": False,
    },
    "AMPLIENCE_BASE_URL": {
        "description": "Amplience base URL",
        "required_for": ["amplience-cms"],
        "sensitive": False,
    },
}


def get_claude_config_path() -> Path:
    """Get the Claude Desktop/Code config file path based on OS."""
    system = platform.system()
    home = Path.home()
    
    if system == "Darwin":  # macOS
        # Check for Claude Code first, then Claude Desktop
        claude_code_path = home / ".claude.json"
        claude_desktop_path = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        
        if claude_code_path.exists():
            return claude_code_path
        elif claude_desktop_path.exists():
            return claude_desktop_path
        else:
            # Default to Claude Code config
            return claude_code_path
    elif system == "Windows":
        return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return home / ".claude.json"


def get_pnd_agents_path() -> Path:
    """Get the path to the pnd-agents installation."""
    # Try to find the package location
    current_file = Path(__file__).resolve()
    # Go up from pnd_agents/cli.py to the repo root
    return current_file.parent.parent


def print_banner():
    """Print the PND Agents banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ██████╗ ███╗   ██╗██████╗      █████╗  ██████╗ ███████╗ ║
    ║   ██╔══██╗████╗  ██║██╔══██╗    ██╔══██╗██╔════╝ ██╔════╝ ║
    ║   ██████╔╝██╔██╗ ██║██║  ██║    ███████║██║  ███╗█████╗   ║
    ║   ██╔═══╝ ██║╚██╗██║██║  ██║    ██╔══██║██║   ██║██╔══╝   ║
    ║   ██║     ██║ ╚████║██████╔╝    ██║  ██║╚██████╔╝███████╗ ║
    ║   ╚═╝     ╚═╝  ╚═══╝╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ║
    ║                                                           ║
    ║              PG AI Squad - Setup Wizard                   ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(color(banner, Colors.CYAN))


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt user for yes/no answer."""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{question} [{default_str}]: ").strip().lower()
        if response == "":
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'")


def prompt_input(prompt: str, default: str = "", sensitive: bool = False) -> str:
    """Prompt user for input."""
    if default:
        display_default = "***" if sensitive and default else default
        full_prompt = f"{prompt} [{display_default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    if sensitive:
        import getpass
        try:
            response = getpass.getpass(full_prompt)
        except Exception:
            response = input(full_prompt)
    else:
        response = input(full_prompt)
    
    return response.strip() if response.strip() else default


def select_agents(preset: Optional[str] = None) -> dict[str, bool]:
    """Interactive agent selection."""
    selected = {}
    
    if preset == "minimal":
        # Only essential agents
        for agent_id in AGENTS:
            selected[agent_id] = agent_id in ["task-manager", "frontend-engineer", "code-review"]
    elif preset == "full":
        # All agents
        for agent_id in AGENTS:
            selected[agent_id] = True
    elif preset == "default":
        # Default selection
        for agent_id, info in AGENTS.items():
            selected[agent_id] = info["default"]
    else:
        # Interactive selection
        print(color("\nSelect agents to enable:", Colors.BOLD))
        print(color("(Press Enter to accept default, 'y' to enable, 'n' to disable)\n", Colors.CYAN))
        
        for agent_id, info in AGENTS.items():
            role_color = {
                "orchestrator": Colors.YELLOW,
                "specialist": Colors.BLUE,
                "validator": Colors.GREEN,
            }.get(info["role"], Colors.ENDC)
            
            role_badge = color(f"[{info['role']}]", role_color)
            name = color(info["name"], Colors.BOLD)
            desc = info["description"]
            default = info["default"]
            
            print(f"  {role_badge} {name}")
            print(f"      {desc}")
            selected[agent_id] = prompt_yes_no(f"      Enable {agent_id}?", default)
            print()
    
    return selected


def configure_env_vars(selected_agents: dict[str, bool]) -> dict[str, str]:
    """Configure environment variables based on selected agents."""
    env_config = {}
    
    # Determine which env vars are needed
    needed_vars = set()
    for var_name, var_info in ENV_VARS.items():
        for agent_id in var_info["required_for"]:
            if selected_agents.get(agent_id, False):
                needed_vars.add(var_name)
                break
    
    if not needed_vars:
        return env_config
    
    print(color("\nConfigure environment variables:", Colors.BOLD))
    print(color("(Press Enter to skip, values will be read from environment if not set)\n", Colors.CYAN))
    
    for var_name in sorted(needed_vars):
        var_info = ENV_VARS[var_name]
        current_value = os.environ.get(var_name, "")
        
        print(f"  {color(var_name, Colors.YELLOW)}")
        print(f"      {var_info['description']}")
        
        value = prompt_input(
            "      Value",
            default=current_value,
            sensitive=var_info["sensitive"]
        )
        
        if value:
            env_config[var_name] = value
        print()
    
    return env_config


def generate_claude_config(
    selected_agents: dict[str, bool],
    env_config: dict[str, str],
    pnd_agents_path: Path
) -> dict:
    """Generate Claude MCP server configuration."""
    main_py_path = pnd_agents_path / "main.py"
    
    # Build environment variables
    env = {
        "PYTHONPATH": str(pnd_agents_path),
    }
    
    # Add configured env vars
    for var_name, value in env_config.items():
        env[var_name] = value
    
    # Add placeholders for unconfigured but needed vars
    for var_name in ENV_VARS:
        if var_name not in env:
            env[var_name] = f"${{env:{var_name}}}"
    
    # Build enabled agents list for reference
    enabled_agents = [aid for aid, enabled in selected_agents.items() if enabled]
    
    config = {
        "pnd-agents": {
            "command": sys.executable,  # Use current Python interpreter
            "args": [str(main_py_path)],
            "env": env,
            "_enabled_agents": enabled_agents,  # Metadata for reference
        }
    }
    
    return config


def write_agent_config(selected_agents: dict[str, bool], pnd_agents_path: Path):
    """Write agent configuration to agents.config.json."""
    config_path = pnd_agents_path / "mcp-config" / "agents.config.json"
    
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {"agents": []}
    
    # Update enabled status for each agent
    for agent in config.get("agents", []):
        agent_id = agent.get("id")
        if agent_id in selected_agents:
            agent["enabled"] = selected_agents[agent_id]
    
    # Write back
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    return config_path


def write_env_file(env_config: dict[str, str], pnd_agents_path: Path):
    """Write environment variables to .env file."""
    env_path = pnd_agents_path / ".env"
    
    # Read existing .env if present
    existing = {}
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing[key.strip()] = value.strip()
    
    # Merge with new config
    existing.update(env_config)
    
    # Write back
    with open(env_path, "w") as f:
        f.write("# PND Agents Environment Configuration\n")
        f.write("# Generated by pnd-agents setup\n\n")
        for key, value in sorted(existing.items()):
            f.write(f"{key}={value}\n")
    
    return env_path


def update_claude_config(mcp_config: dict, config_path: Path, auto_write: bool = False) -> bool:
    """Update Claude config file with MCP server entry."""
    # Read existing config
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            existing_config = {}
    
    # Ensure mcpServers key exists
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Check if pnd-agents already configured
    if "pnd-agents" in existing_config["mcpServers"]:
        print(color("\nExisting pnd-agents configuration found.", Colors.YELLOW))
        if not auto_write:
            if not prompt_yes_no("Overwrite existing configuration?", default=True):
                return False
    
    # Update config
    existing_config["mcpServers"].update(mcp_config)
    
    if auto_write:
        write_config = True
    else:
        print(color("\nClaude config will be updated at:", Colors.CYAN))
        print(f"  {config_path}")
        write_config = prompt_yes_no("\nWrite configuration to file?", default=True)
    
    if write_config:
        # Create parent directories if needed
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(existing_config, f, indent=2)
        
        print(color(f"\nConfiguration written to {config_path}", Colors.GREEN))
        return True
    else:
        # Print config for manual copy
        print(color("\nAdd this to your Claude config file:", Colors.YELLOW))
        print(color("─" * 60, Colors.CYAN))
        print(json.dumps({"mcpServers": mcp_config}, indent=2))
        print(color("─" * 60, Colors.CYAN))
        return False


def cmd_setup(args):
    """Run the setup wizard."""
    print_banner()
    
    pnd_agents_path = get_pnd_agents_path()
    print(f"PND Agents path: {color(str(pnd_agents_path), Colors.CYAN)}")
    
    # Check if main.py exists
    main_py = pnd_agents_path / "main.py"
    if not main_py.exists():
        print(color(f"\nError: main.py not found at {main_py}", Colors.RED))
        print("Make sure you're running setup from the pnd-agents directory.")
        return 1
    
    # Select agents
    if args.preset:
        selected_agents = select_agents(preset=args.preset)
        print(color(f"\nUsing '{args.preset}' preset:", Colors.CYAN))
        for agent_id, enabled in selected_agents.items():
            status = color("[x]", Colors.GREEN) if enabled else "[ ]"
            print(f"  {status} {AGENTS[agent_id]['name']}")
    else:
        selected_agents = select_agents()
    
    # Configure environment variables
    if args.skip_env:
        env_config = {}
    else:
        env_config = configure_env_vars(selected_agents)
    
    # Generate Claude config
    mcp_config = generate_claude_config(selected_agents, env_config, pnd_agents_path)
    
    # Write agent config
    agent_config_path = write_agent_config(selected_agents, pnd_agents_path)
    print(color(f"\nAgent config written to {agent_config_path}", Colors.GREEN))
    
    # Write .env file if we have env vars
    if env_config:
        env_path = write_env_file(env_config, pnd_agents_path)
        print(color(f"Environment config written to {env_path}", Colors.GREEN))
    
    # Update Claude config
    claude_config_path = get_claude_config_path()
    update_claude_config(mcp_config, claude_config_path, auto_write=args.auto)
    
    # Print summary
    print(color("\n" + "═" * 60, Colors.CYAN))
    print(color("Setup Complete!", Colors.GREEN + Colors.BOLD))
    print(color("═" * 60, Colors.CYAN))
    
    enabled_count = sum(1 for v in selected_agents.values() if v)
    print(f"\nEnabled agents: {color(str(enabled_count), Colors.GREEN)} / {len(AGENTS)}")
    
    print(color("\nNext steps:", Colors.YELLOW))
    print("  1. Restart Claude Desktop/Code to load the new configuration")
    print("  2. Start a new conversation and the pnd-agents tools will be available")
    print("  3. Try: 'Use the Task Manager to help me create a component'")
    
    return 0


def cmd_config(args):
    """Reconfigure specific settings."""
    pnd_agents_path = get_pnd_agents_path()
    
    if args.agents:
        print(color("\nReconfigure agents:", Colors.BOLD))
        selected_agents = select_agents()
        write_agent_config(selected_agents, pnd_agents_path)
        print(color("\nAgent configuration updated.", Colors.GREEN))
    
    if args.env:
        print(color("\nReconfigure environment variables:", Colors.BOLD))
        # Load current agent config to determine needed vars
        config_path = pnd_agents_path / "mcp-config" / "agents.config.json"
        selected_agents = {}
        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)
                for agent in config.get("agents", []):
                    selected_agents[agent["id"]] = agent.get("enabled", True)
        else:
            for agent_id, info in AGENTS.items():
                selected_agents[agent_id] = info["default"]
        
        env_config = configure_env_vars(selected_agents)
        if env_config:
            write_env_file(env_config, pnd_agents_path)
            print(color("\nEnvironment configuration updated.", Colors.GREEN))
    
    if args.show:
        print(color("\nCurrent configuration:", Colors.BOLD))
        
        # Show agent config
        config_path = pnd_agents_path / "mcp-config" / "agents.config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)
            
            print(color("\nAgents:", Colors.CYAN))
            for agent in config.get("agents", []):
                enabled = agent.get("enabled", True)
                status = color("[x]", Colors.GREEN) if enabled else "[ ]"
                print(f"  {status} {agent['name']}")
        
        # Show env config
        env_path = pnd_agents_path / ".env"
        if env_path.exists():
            print(color("\nEnvironment (.env):", Colors.CYAN))
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "TOKEN" in line or "SECRET" in line or "KEY" in line:
                            key = line.split("=")[0]
                            print(f"  {key}=***")
                        else:
                            print(f"  {line}")
    
    return 0


def cmd_status(args):
    """Show current status and configuration."""
    pnd_agents_path = get_pnd_agents_path()
    
    print(color("\nPND Agents Status", Colors.BOLD))
    print(color("═" * 40, Colors.CYAN))
    
    # Check installation
    print(f"\nInstallation path: {pnd_agents_path}")
    
    main_py = pnd_agents_path / "main.py"
    if main_py.exists():
        print(color("  main.py: Found", Colors.GREEN))
    else:
        print(color("  main.py: Not found", Colors.RED))
    
    # Check agent config
    config_path = pnd_agents_path / "mcp-config" / "agents.config.json"
    if config_path.exists():
        print(color("  agents.config.json: Found", Colors.GREEN))
        with open(config_path, "r") as f:
            config = json.load(f)
        enabled = sum(1 for a in config.get("agents", []) if a.get("enabled", True))
        print(f"    Enabled agents: {enabled}")
    else:
        print(color("  agents.config.json: Not found", Colors.YELLOW))
    
    # Check .env
    env_path = pnd_agents_path / ".env"
    if env_path.exists():
        print(color("  .env: Found", Colors.GREEN))
    else:
        print(color("  .env: Not found (optional)", Colors.YELLOW))
    
    # Check Claude config
    claude_config_path = get_claude_config_path()
    print(f"\nClaude config: {claude_config_path}")
    if claude_config_path.exists():
        print(color("  Config file: Found", Colors.GREEN))
        with open(claude_config_path, "r") as f:
            try:
                config = json.load(f)
                if "pnd-agents" in config.get("mcpServers", {}):
                    print(color("  pnd-agents: Configured", Colors.GREEN))
                else:
                    print(color("  pnd-agents: Not configured", Colors.YELLOW))
            except json.JSONDecodeError:
                print(color("  Config file: Invalid JSON", Colors.RED))
    else:
        print(color("  Config file: Not found", Colors.YELLOW))
    
    return 0


def cmd_scan(args):
    """Scan a URL for broken experiences."""
    import asyncio
    import sys
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(get_pnd_agents_path()))
    
    from agents.broken_experience_detector_agent import BrokenExperienceDetectorAgent
    
    url = args.url
    output_format = args.format
    
    print(color(f"\nScanning: {url}", Colors.CYAN))
    print(color("This may take 30-60 seconds...\n", Colors.YELLOW))
    
    try:
        agent = BrokenExperienceDetectorAgent(headless=True)
        report = asyncio.run(agent.scan_site(url))
        
        if output_format == "json":
            import json
            print(json.dumps(report.to_dict(), indent=2))
        elif output_format == "markdown":
            print(report.to_markdown())
        else:  # both
            print(color("=" * 60, Colors.CYAN))
            print(color("MARKDOWN REPORT", Colors.BOLD))
            print(color("=" * 60, Colors.CYAN))
            print(report.to_markdown())
            print(color("\n" + "=" * 60, Colors.CYAN))
            print(color("JSON REPORT", Colors.BOLD))
            print(color("=" * 60, Colors.CYAN))
            import json
            print(json.dumps(report.to_dict(), indent=2))
        
        # Print summary
        print(color(f"\n{'=' * 60}", Colors.CYAN))
        print(color(f"Scan Complete! Score: {report.score}/100", Colors.GREEN if report.score >= 70 else Colors.YELLOW if report.score >= 50 else Colors.RED))
        print(color(f"{'=' * 60}", Colors.CYAN))
        
        return 0
    except Exception as e:
        print(color(f"\nError scanning URL: {e}", Colors.RED))
        if os.environ.get("DEBUG"):
            import traceback
            traceback.print_exc()
        return 1


def cmd_run_task(args):
    """Run a task through the workflow engine."""
    import sys
    import os
    
    # Add parent directory to path for imports
    pnd_agents_path = get_pnd_agents_path()
    sys.path.insert(0, str(pnd_agents_path))
    
    try:
        from agents.task_manager_agent import TaskManagerAgent
    except ImportError as e:
        print(color(f"Error importing TaskManagerAgent: {e}", Colors.RED))
        return 1
    
    task = args.task
    
    print(color("\n" + "=" * 60, Colors.CYAN))
    print(color("PND AGENTS - Workflow Engine", Colors.BOLD))
    print(color("=" * 60, Colors.CYAN))
    
    # Create task manager
    agent = TaskManagerAgent()
    
    if args.plan_only:
        # Just show the plan without executing
        plan = agent.analyze_task(task)
        print(f"\nTask: \"{plan['task'][:80]}{'...' if len(plan['task']) > 80 else ''}\"")
        print(f"Detected Type: {color(plan['detected_type'], Colors.YELLOW)}")
        print(f"\nPipeline ({len(plan['pipeline'])} stages):")
        for stage in plan['stages']:
            print(f"  {stage['step']}. {color(stage['agent'].capitalize() + 'Agent', Colors.CYAN)} -> {stage['description']}")
        return 0
    
    # Build metadata
    metadata = {}
    if args.ticket:
        metadata['ticket_id'] = args.ticket
    if args.branch:
        metadata['branch'] = args.branch
    
    # Run the task
    try:
        context = agent.run_task(task, metadata=metadata, verbose=not args.quiet)
        
        if args.output:
            # Write output to file
            import json
            with open(args.output, 'w') as f:
                json.dump(agent.to_dict(context), f, indent=2)
            print(color(f"\nOutput written to {args.output}", Colors.GREEN))
        
        if context.status == "completed":
            print(color("\nWorkflow completed successfully!", Colors.GREEN))
            return 0
        else:
            print(color(f"\nWorkflow ended with status: {context.status}", Colors.YELLOW))
            return 1
            
    except Exception as e:
        print(color(f"\nError running task: {e}", Colors.RED))
        if os.environ.get("DEBUG"):
            import traceback
            traceback.print_exc()
        return 1


def cmd_analyze_task(args):
    """Analyze a task and show the workflow plan."""
    import sys
    
    # Add parent directory to path for imports
    pnd_agents_path = get_pnd_agents_path()
    sys.path.insert(0, str(pnd_agents_path))
    
    try:
        from workflow.workflow_engine import WorkflowEngine
    except ImportError as e:
        print(color(f"Error importing WorkflowEngine: {e}", Colors.RED))
        return 1
    
    task = args.task
    engine = WorkflowEngine()
    
    plan = engine.get_workflow_plan(task)
    
    print(color("\n" + "=" * 60, Colors.CYAN))
    print(color("TASK ANALYSIS", Colors.BOLD))
    print(color("=" * 60, Colors.CYAN))
    
    print(f"\nTask: \"{plan['task'][:80]}{'...' if len(plan['task']) > 80 else ''}\"")
    print(f"Detected Type: {color(plan['detected_type'], Colors.YELLOW)}")
    print(f"\nWorkflow Pipeline:")
    
    for stage in plan['stages']:
        agent_name = stage['agent'].capitalize() + 'Agent'
        print(f"  {stage['step']}. {color(agent_name, Colors.CYAN)}")
        print(f"     -> {stage['description']}")
    
    print(color("\n" + "=" * 60, Colors.CYAN))
    return 0


def cmd_uninstall(args):
    """Remove pnd-agents configuration."""
    print(color("\nUninstall PND Agents Configuration", Colors.BOLD))
    
    if not prompt_yes_no("This will remove pnd-agents from your Claude config. Continue?", default=False):
        print("Cancelled.")
        return 0
    
    claude_config_path = get_claude_config_path()
    
    if claude_config_path.exists():
        with open(claude_config_path, "r") as f:
            config = json.load(f)
        
        if "pnd-agents" in config.get("mcpServers", {}):
            del config["mcpServers"]["pnd-agents"]
            
            with open(claude_config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            print(color("\npnd-agents removed from Claude config.", Colors.GREEN))
        else:
            print(color("\npnd-agents not found in Claude config.", Colors.YELLOW))
    else:
        print(color("\nClaude config file not found.", Colors.YELLOW))
    
    print("\nNote: The pnd-agents files are still on disk. To fully remove, delete the directory.")
    
    return 0


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pnd-agents",
        description="PG AI Squad - Setup and configuration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pnd-agents setup              Interactive setup wizard
  pnd-agents setup --preset default   Use default agent selection
  pnd-agents setup --preset full      Enable all agents
  pnd-agents setup --preset minimal   Enable only essential agents
  pnd-agents config --agents    Reconfigure agent selection
  pnd-agents config --env       Reconfigure environment variables
  pnd-agents config --show      Show current configuration
  pnd-agents status             Show installation status
  pnd-agents uninstall          Remove from Claude config
  pnd-agents scan <url>         Scan URL for broken experiences
  pnd-agents run-task "Create Stories carousel from Figma: ..."
  pnd-agents run-task "Build React component" --plan-only
  pnd-agents analyze-task "Create API endpoint for products"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Run the setup wizard")
    setup_parser.add_argument(
        "--preset",
        choices=["default", "full", "minimal"],
        help="Use a preset agent selection instead of interactive"
    )
    setup_parser.add_argument(
        "--skip-env",
        action="store_true",
        help="Skip environment variable configuration"
    )
    setup_parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically write config without prompting"
    )
    setup_parser.set_defaults(func=cmd_setup)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Reconfigure settings")
    config_parser.add_argument(
        "--agents",
        action="store_true",
        help="Reconfigure agent selection"
    )
    config_parser.add_argument(
        "--env",
        action="store_true",
        help="Reconfigure environment variables"
    )
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="Show current configuration"
    )
    config_parser.set_defaults(func=cmd_config)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show installation status")
    status_parser.set_defaults(func=cmd_status)
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove from Claude config")
    uninstall_parser.set_defaults(func=cmd_uninstall)
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a URL for broken experiences")
    scan_parser.add_argument(
        "url",
        help="URL to scan (e.g., 'https://us.pandora.net', 'http://localhost:3000')"
    )
    scan_parser.add_argument(
        "--format",
        choices=["json", "markdown", "both"],
        default="both",
        help="Output format (default: both)"
    )
    scan_parser.set_defaults(func=cmd_scan)
    
    # Run-task command
    run_task_parser = subparsers.add_parser("run-task", help="Run a task through the workflow engine")
    run_task_parser.add_argument(
        "task",
        help="Task description (e.g., 'Create the Stories carousel using Figma link: ...')"
    )
    run_task_parser.add_argument(
        "--ticket",
        help="Ticket ID (e.g., INS-2509)"
    )
    run_task_parser.add_argument(
        "--branch",
        help="Branch name to use"
    )
    run_task_parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Only show the workflow plan without executing"
    )
    run_task_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )
    run_task_parser.add_argument(
        "--output",
        help="Output file path for workflow results (JSON)"
    )
    run_task_parser.set_defaults(func=cmd_run_task)
    
    # Analyze-task command
    analyze_parser = subparsers.add_parser("analyze-task", help="Analyze a task and show the workflow plan")
    analyze_parser.add_argument(
        "task",
        help="Task description to analyze"
    )
    analyze_parser.set_defaults(func=cmd_analyze_task)
    
    args = parser.parse_args()
    
    if args.command is None:
        # Default to setup if no command given
        args.command = "setup"
        args.preset = None
        args.skip_env = False
        args.auto = False
        args.func = cmd_setup
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print(color("\n\nSetup cancelled.", Colors.YELLOW))
        return 1
    except Exception as e:
        print(color(f"\nError: {e}", Colors.RED))
        if os.environ.get("DEBUG"):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
