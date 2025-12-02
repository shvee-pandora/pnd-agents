"""
Command Runner Tool

Provides command execution capabilities for agents including
running ESLint, Prettier, TypeScript, Jest, and Playwright.
"""

import subprocess
import os
import shlex
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class CommandStatus(Enum):
    """Status of command execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class CommandResult:
    """Result of a command execution."""
    command: str
    status: CommandStatus
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float


class CommandRunner:
    """
    Command execution tool for agents.
    
    Provides safe command execution with timeout handling,
    output capture, and common development tool integrations.
    """
    
    # Allowed commands for security
    ALLOWED_COMMANDS = {
        'npm', 'npx', 'pnpm', 'yarn',
        'node', 'tsc', 'eslint', 'prettier',
        'jest', 'playwright', 'vitest',
        'git', 'cat', 'ls', 'pwd', 'echo',
        'mkdir', 'rm', 'cp', 'mv', 'touch',
    }
    
    def __init__(
        self,
        working_dir: Optional[str] = None,
        timeout: int = 300,
        env: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the command runner.
        
        Args:
            working_dir: Working directory for commands.
            timeout: Default timeout in seconds.
            env: Additional environment variables.
        """
        self.working_dir = working_dir or os.getcwd()
        self.timeout = timeout
        self.env = {**os.environ, **(env or {})}
    
    def _validate_command(self, command: str) -> bool:
        """
        Validate that a command is allowed.
        
        Args:
            command: Command string to validate.
            
        Returns:
            True if command is allowed.
        """
        # Extract the base command
        parts = shlex.split(command)
        if not parts:
            return False
        
        base_cmd = os.path.basename(parts[0])
        return base_cmd in self.ALLOWED_COMMANDS
    
    def run(
        self,
        command: str,
        timeout: Optional[int] = None,
        capture_output: bool = True,
        check: bool = False
    ) -> CommandResult:
        """
        Run a command and return the result.
        
        Args:
            command: Command string to execute.
            timeout: Timeout in seconds (overrides default).
            capture_output: Whether to capture stdout/stderr.
            check: Raise exception on non-zero exit code.
            
        Returns:
            CommandResult with execution details.
            
        Raises:
            ValueError: If command is not allowed.
            subprocess.TimeoutExpired: If command times out.
        """
        if not self._validate_command(command):
            raise ValueError(f"Command not allowed: {command}")
        
        import time
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                env=self.env,
                capture_output=capture_output,
                text=True,
                timeout=timeout or self.timeout
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            status = CommandStatus.SUCCESS if result.returncode == 0 else CommandStatus.FAILURE
            
            cmd_result = CommandResult(
                command=command,
                status=status,
                exit_code=result.returncode,
                stdout=result.stdout or '',
                stderr=result.stderr or '',
                duration_ms=duration_ms
            )
            
            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode,
                    command,
                    result.stdout,
                    result.stderr
                )
            
            return cmd_result
            
        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000
            return CommandResult(
                command=command,
                status=CommandStatus.TIMEOUT,
                exit_code=-1,
                stdout=e.stdout or '' if hasattr(e, 'stdout') else '',
                stderr=e.stderr or '' if hasattr(e, 'stderr') else '',
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CommandResult(
                command=command,
                status=CommandStatus.ERROR,
                exit_code=-1,
                stdout='',
                stderr=str(e),
                duration_ms=duration_ms
            )
    
    # Convenience methods for common tools
    
    def run_eslint(
        self,
        paths: List[str],
        fix: bool = False,
        config: Optional[str] = None
    ) -> CommandResult:
        """
        Run ESLint on specified paths.
        
        Args:
            paths: List of file/directory paths to lint.
            fix: Whether to auto-fix issues.
            config: Optional config file path.
            
        Returns:
            CommandResult with lint output.
        """
        cmd_parts = ['npx', 'eslint']
        
        if fix:
            cmd_parts.append('--fix')
        
        if config:
            cmd_parts.extend(['--config', config])
        
        cmd_parts.extend(paths)
        
        return self.run(' '.join(cmd_parts))
    
    def run_prettier(
        self,
        paths: List[str],
        write: bool = False,
        check: bool = False
    ) -> CommandResult:
        """
        Run Prettier on specified paths.
        
        Args:
            paths: List of file/directory paths to format.
            write: Whether to write changes.
            check: Whether to check formatting only.
            
        Returns:
            CommandResult with format output.
        """
        cmd_parts = ['npx', 'prettier']
        
        if write:
            cmd_parts.append('--write')
        elif check:
            cmd_parts.append('--check')
        
        cmd_parts.extend(paths)
        
        return self.run(' '.join(cmd_parts))
    
    def run_typescript(
        self,
        project: Optional[str] = None,
        no_emit: bool = True
    ) -> CommandResult:
        """
        Run TypeScript compiler.
        
        Args:
            project: Path to tsconfig.json.
            no_emit: Whether to skip emitting files.
            
        Returns:
            CommandResult with type check output.
        """
        cmd_parts = ['npx', 'tsc']
        
        if project:
            cmd_parts.extend(['--project', project])
        
        if no_emit:
            cmd_parts.append('--noEmit')
        
        return self.run(' '.join(cmd_parts))
    
    def run_jest(
        self,
        paths: Optional[List[str]] = None,
        coverage: bool = False,
        watch: bool = False,
        config: Optional[str] = None
    ) -> CommandResult:
        """
        Run Jest tests.
        
        Args:
            paths: Optional test file paths.
            coverage: Whether to collect coverage.
            watch: Whether to run in watch mode.
            config: Optional config file path.
            
        Returns:
            CommandResult with test output.
        """
        cmd_parts = ['npx', 'jest']
        
        if coverage:
            cmd_parts.append('--coverage')
        
        if watch:
            cmd_parts.append('--watch')
        
        if config:
            cmd_parts.extend(['--config', config])
        
        if paths:
            cmd_parts.extend(paths)
        
        return self.run(' '.join(cmd_parts))
    
    def run_playwright(
        self,
        paths: Optional[List[str]] = None,
        project: Optional[str] = None,
        headed: bool = False
    ) -> CommandResult:
        """
        Run Playwright tests.
        
        Args:
            paths: Optional test file paths.
            project: Browser project to run.
            headed: Whether to run in headed mode.
            
        Returns:
            CommandResult with test output.
        """
        cmd_parts = ['npx', 'playwright', 'test']
        
        if project:
            cmd_parts.extend(['--project', project])
        
        if headed:
            cmd_parts.append('--headed')
        
        if paths:
            cmd_parts.extend(paths)
        
        return self.run(' '.join(cmd_parts))
    
    def run_npm_script(self, script: str) -> CommandResult:
        """
        Run an npm script.
        
        Args:
            script: Script name to run.
            
        Returns:
            CommandResult with script output.
        """
        return self.run(f'npm run {script}')
    
    def run_pnpm_script(self, script: str) -> CommandResult:
        """
        Run a pnpm script.
        
        Args:
            script: Script name to run.
            
        Returns:
            CommandResult with script output.
        """
        return self.run(f'pnpm {script}')
    
    def validate(self) -> CommandResult:
        """
        Run full validation (lint + typecheck + format check).
        
        Returns:
            CommandResult with validation output.
        """
        return self.run('pnpm validate')
    
    def build(self) -> CommandResult:
        """
        Run build command.
        
        Returns:
            CommandResult with build output.
        """
        return self.run('pnpm build')
    
    def test(self, coverage: bool = False) -> CommandResult:
        """
        Run tests.
        
        Args:
            coverage: Whether to collect coverage.
            
        Returns:
            CommandResult with test output.
        """
        cmd = 'pnpm test'
        if coverage:
            cmd = 'pnpm testcoverage'
        return self.run(cmd)


# Convenience functions
def run_command(command: str, working_dir: Optional[str] = None) -> CommandResult:
    """Quick command execution."""
    return CommandRunner(working_dir=working_dir).run(command)


def run_eslint(paths: List[str], fix: bool = False) -> CommandResult:
    """Quick ESLint execution."""
    return CommandRunner().run_eslint(paths, fix=fix)


def run_typescript() -> CommandResult:
    """Quick TypeScript check."""
    return CommandRunner().run_typescript()


def run_tests(coverage: bool = False) -> CommandResult:
    """Quick test execution."""
    return CommandRunner().test(coverage=coverage)
