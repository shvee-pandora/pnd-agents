"""
Pattern Matcher

Shared regex patterns and matching utilities for code analysis.
Used by code_review, sonar_validation, and other analysis agents.

Usage:
    from src.agents.core.analyzers.pattern_matcher import PatternMatcher, PATTERNS
    
    matcher = PatternMatcher()
    issues = matcher.find_security_issues(code)
    todos = matcher.find_todos(code)
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Pattern

logger = logging.getLogger("pnd_agents.core.analyzers.pattern_matcher")


@dataclass
class PatternMatch:
    """A match found by the pattern matcher."""
    pattern_name: str
    line_number: int
    column: int
    match_text: str
    context: str  # Surrounding line
    severity: str = "info"  # info, warning, error
    message: str = ""


# Common patterns for code analysis
PATTERNS: Dict[str, Dict[str, Any]] = {
    # Security patterns
    "hardcoded_secret": {
        "pattern": r'(?i)(password|secret|api_key|apikey|token|auth)\s*[=:]\s*["\'][^"\']{8,}["\']',
        "severity": "error",
        "message": "Possible hardcoded secret detected",
    },
    "sql_injection": {
        "pattern": r'(?i)(execute|query)\s*\(\s*["\'].*\+.*["\']|f["\'].*\{.*\}.*(?:select|insert|update|delete)',
        "severity": "error",
        "message": "Possible SQL injection vulnerability",
    },
    "eval_usage": {
        "pattern": r'\beval\s*\(',
        "severity": "warning",
        "message": "Use of eval() is discouraged",
    },
    
    # Code quality patterns
    "todo_comment": {
        "pattern": r'(?i)(?://|#|/\*|\*)\s*(TODO|FIXME|HACK|XXX|BUG)[\s:]+(.+)',
        "severity": "info",
        "message": "TODO comment found",
    },
    "console_log": {
        "pattern": r'\bconsole\.(log|debug|info|warn|error)\s*\(',
        "severity": "warning",
        "message": "Console statement should be removed",
    },
    "debugger_statement": {
        "pattern": r'\bdebugger\b',
        "severity": "warning",
        "message": "Debugger statement should be removed",
    },
    
    # TypeScript/JavaScript patterns
    "any_type": {
        "pattern": r':\s*any\b',
        "severity": "warning",
        "message": "Avoid using 'any' type",
    },
    "ts_ignore": {
        "pattern": r'@ts-ignore|@ts-nocheck',
        "severity": "warning",
        "message": "TypeScript ignore directive found",
    },
    
    # React patterns
    "useeffect_missing_deps": {
        "pattern": r'useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]*\}\s*,\s*\[\s*\]\s*\)',
        "severity": "info",
        "message": "useEffect with empty dependency array - verify this is intentional",
    },
    
    # Python patterns
    "bare_except": {
        "pattern": r'\bexcept\s*:',
        "severity": "warning",
        "message": "Bare except clause - specify exception type",
    },
    "print_statement": {
        "pattern": r'\bprint\s*\(',
        "severity": "info",
        "message": "Print statement found - consider using logging",
    },
}


class PatternMatcher:
    """
    Matcher for common code patterns.
    
    Provides utilities for finding security issues, code smells, and TODOs.
    """
    
    def __init__(self, custom_patterns: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize the pattern matcher.
        
        Args:
            custom_patterns: Additional patterns to include
        """
        self.patterns = {**PATTERNS}
        if custom_patterns:
            self.patterns.update(custom_patterns)
        
        # Compile patterns
        self._compiled: Dict[str, Pattern] = {}
        for name, config in self.patterns.items():
            self._compiled[name] = re.compile(config["pattern"])
    
    def find_matches(
        self,
        code: str,
        pattern_names: Optional[List[str]] = None
    ) -> List[PatternMatch]:
        """
        Find all pattern matches in code.
        
        Args:
            code: Source code to analyze
            pattern_names: Specific patterns to check (all if None)
            
        Returns:
            List of PatternMatch objects.
        """
        raise NotImplementedError("PatternMatcher.find_matches() not yet implemented")
    
    def find_security_issues(self, code: str) -> List[PatternMatch]:
        """
        Find security-related issues in code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of security-related PatternMatch objects.
        """
        security_patterns = ["hardcoded_secret", "sql_injection", "eval_usage"]
        return self.find_matches(code, security_patterns)
    
    def find_todos(self, code: str) -> List[PatternMatch]:
        """
        Find TODO comments in code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of TODO PatternMatch objects.
        """
        return self.find_matches(code, ["todo_comment"])
    
    def find_debug_statements(self, code: str) -> List[PatternMatch]:
        """
        Find debug statements that should be removed.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of debug-related PatternMatch objects.
        """
        debug_patterns = ["console_log", "debugger_statement", "print_statement"]
        return self.find_matches(code, debug_patterns)


__all__ = ["PatternMatcher", "PatternMatch", "PATTERNS"]
