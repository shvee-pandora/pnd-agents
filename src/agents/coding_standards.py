"""
Centralized Coding Standards and Sonar Rules for PND Agents

This module provides a single source of truth for:
- Sonar rules and their fixes
- Pandora coding standards
- Quality gate requirements
- Coverage targets

All agents (Unit Test, Code Review, Sonar Validation) should import from this module
to ensure consistent enforcement of standards.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SonarRule:
    """Represents a Sonar rule with detection and fix information."""
    rule_id: str
    description: str
    severity: Severity
    detect_pattern: Optional[str] = None
    prevent_message: str = ""
    autofix: Optional[str] = None
    applies_to: List[str] = field(default_factory=lambda: ["*.ts", "*.tsx", "*.js", "*.jsx"])
    
    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "severity": self.severity.value,
            "detect_pattern": self.detect_pattern,
            "prevent_message": self.prevent_message,
            "autofix": self.autofix,
            "applies_to": self.applies_to,
        }


@dataclass
class CodingStandard:
    """Represents a Pandora coding standard rule."""
    name: str
    description: str
    good_example: str
    bad_example: str
    enforce: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "good_example": self.good_example,
            "bad_example": self.bad_example,
            "enforce": self.enforce,
        }


@dataclass
class QualityGates:
    """Quality gate requirements aligned with SonarCloud."""
    min_line_coverage: int = 100
    min_branch_coverage: int = 100
    min_function_coverage: int = 100
    max_bugs: int = 0
    max_vulnerabilities: int = 0
    max_code_smells: int = 0
    max_duplicated_lines_percent: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "min_line_coverage": self.min_line_coverage,
            "min_branch_coverage": self.min_branch_coverage,
            "min_function_coverage": self.min_function_coverage,
            "max_bugs": self.max_bugs,
            "max_vulnerabilities": self.max_vulnerabilities,
            "max_code_smells": self.max_code_smells,
            "max_duplicated_lines_percent": self.max_duplicated_lines_percent,
        }


# =============================================================================
# SONAR RULES - Common rules that agents must enforce/avoid
# =============================================================================

SONAR_RULES: Dict[str, SonarRule] = {
    "S7764": SonarRule(
        rule_id="S7764",
        description="Prefer globalThis over global",
        severity=Severity.HIGH,
        detect_pattern=r"\bglobal\b(?!This)",
        prevent_message="Use `globalThis` instead of `global` for cross-environment compatibility",
        autofix="Replace `global` with `globalThis`",
    ),
    "S4325": SonarRule(
        rule_id="S4325",
        description="Avoid unnecessary type assertions",
        severity=Severity.MEDIUM,
        detect_pattern=r"as\s+\w+(?:\s*\[\s*\])?(?:\s*\|\s*\w+)*\s*[;,)\]]",
        prevent_message="Avoid unnecessary type assertions - let TypeScript infer types",
        autofix=None,
    ),
    "S7741": SonarRule(
        rule_id="S7741",
        description="Compare with undefined directly",
        severity=Severity.MEDIUM,
        detect_pattern=r"typeof\s+\w+\s*===?\s*['\"]undefined['\"]",
        prevent_message="Use `x === undefined` instead of `typeof x === 'undefined'`",
        autofix="Replace `typeof x === 'undefined'` with `x === undefined`",
    ),
    "S7780": SonarRule(
        rule_id="S7780",
        description="Use String.raw for complex escape sequences",
        severity=Severity.LOW,
        detect_pattern=r"['\"].*\\\\.*['\"]",
        prevent_message="Use String.raw`` for strings with complex escape sequences",
        autofix=None,
    ),
    "S6759": SonarRule(
        rule_id="S6759",
        description="Mark props as read-only",
        severity=Severity.LOW,
        detect_pattern=r"type\s+\w*Props\s*=\s*\{",
        prevent_message="SKIP for pandora-group - conflicts with 'Don't wrap Next.js props with Readonly<>'",
        autofix=None,
    ),
    "S1854": SonarRule(
        rule_id="S1854",
        description="Remove unused variable assignments",
        severity=Severity.MEDIUM,
        detect_pattern=r"const\s+\w+\s*=\s*[^;]+;\s*(?://.*)?$",
        prevent_message="Don't declare variables that aren't used",
        autofix="Remove the unused variable declaration",
    ),
    "S1481": SonarRule(
        rule_id="S1481",
        description="Remove unused local variables",
        severity=Severity.MEDIUM,
        detect_pattern=None,
        prevent_message="Remove unused local variables",
        autofix="Delete the unused variable or prefix with underscore",
    ),
    "S6606": SonarRule(
        rule_id="S6606",
        description="Use nullish coalescing operator",
        severity=Severity.LOW,
        detect_pattern=r"\|\|\s*(?:null|undefined|''|0|false)",
        prevent_message="Use `??` instead of `||` for null/undefined checks",
        autofix="Replace `||` with `??`",
    ),
    "S6582": SonarRule(
        rule_id="S6582",
        description="Use optional chaining",
        severity=Severity.LOW,
        detect_pattern=r"\w+\s*&&\s*\w+\.\w+",
        prevent_message="Use optional chaining `?.` instead of `&&` chains",
        autofix="Replace `obj && obj.prop` with `obj?.prop`",
    ),
    "S3776": SonarRule(
        rule_id="S3776",
        description="Reduce cognitive complexity",
        severity=Severity.HIGH,
        detect_pattern=None,
        prevent_message="Keep functions simple - max 15 cognitive complexity",
        autofix=None,
    ),
    "S1128": SonarRule(
        rule_id="S1128",
        description="Remove unused imports",
        severity=Severity.MEDIUM,
        detect_pattern=None,
        prevent_message="Remove unused imports",
        autofix="Run ESLint auto-fix: npx eslint --fix",
    ),
}

# Rules that should NOT be enforced for specific repos
REPO_IGNORED_RULES: Dict[str, List[str]] = {
    "pandora-group": ["S6759"],  # Conflicts with "Don't wrap props with Readonly<>"
    "pandora-ecom-web": [],
    "pandora-sfra": [],
}


# =============================================================================
# PANDORA CODING STANDARDS
# =============================================================================

CODING_STANDARDS: List[CodingStandard] = [
    CodingStandard(
        name="use-type-over-interface",
        description="Use `type` over `interface` for object types",
        good_example="type UserData = { id: string; name: string; };",
        bad_example="interface UserData { id: string; name: string; }",
        enforce=True,
    ),
    CodingStandard(
        name="no-todo-comments",
        description="No TODO comments in production code",
        good_example="// Implement error handling for edge cases",
        bad_example="// TODO: fix this later",
        enforce=True,
    ),
    CodingStandard(
        name="prefer-for-of",
        description="Prefer `for...of` over forEach for arrays",
        good_example="for (const item of items) { process(item); }",
        bad_example="items.forEach(item => { process(item); });",
        enforce=True,
    ),
    CodingStandard(
        name="use-at-for-negative-index",
        description="Use `.at(-n)` for negative indexing",
        good_example="const last = arr.at(-1);",
        bad_example="const last = arr[arr.length - 1];",
        enforce=True,
    ),
    CodingStandard(
        name="avoid-negated-conditions",
        description="Avoid negated conditions with else blocks",
        good_example="if (condition) { B } else { A }",
        bad_example="if (!condition) { A } else { B }",
        enforce=True,
    ),
    CodingStandard(
        name="no-readonly-nextjs-props",
        description="Don't wrap Next.js props with Readonly<>",
        good_example="type Props = { title: string };",
        bad_example="type Props = Readonly<{ title: string }>;",
        enforce=True,
    ),
    CodingStandard(
        name="use-globalThis",
        description="Use globalThis instead of global",
        good_example="globalThis.window",
        bad_example="global.window",
        enforce=True,
    ),
    CodingStandard(
        name="direct-undefined-comparison",
        description="Compare with undefined directly",
        good_example="if (value === undefined) { }",
        bad_example="if (typeof value === 'undefined') { }",
        enforce=True,
    ),
]


# =============================================================================
# QUALITY GATES - Default requirements
# =============================================================================

DEFAULT_QUALITY_GATES = QualityGates(
    min_line_coverage=100,
    min_branch_coverage=100,
    min_function_coverage=100,
    max_bugs=0,
    max_vulnerabilities=0,
    max_code_smells=0,
    max_duplicated_lines_percent=0.0,
)


# =============================================================================
# TEST GENERATION LIMITS
# =============================================================================

TEST_GENERATION_LIMITS = {
    "max_tests_per_unit": 3,
    "max_tests_per_file": 15,
    "max_lines_per_file": 200,
}


# =============================================================================
# CODE REVIEW LIMITS
# =============================================================================

CODE_REVIEW_LIMITS = {
    "max_findings": 10,
    "max_words_per_review": 200,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_enforced_rules(repo_name: str = "default") -> List[SonarRule]:
    """Get list of Sonar rules that should be enforced for a repo."""
    ignored = REPO_IGNORED_RULES.get(repo_name, [])
    return [rule for rule_id, rule in SONAR_RULES.items() if rule_id not in ignored]


def get_rule_by_id(rule_id: str) -> Optional[SonarRule]:
    """Get a specific Sonar rule by ID."""
    return SONAR_RULES.get(rule_id)


def get_coding_standards(enforce_only: bool = True) -> List[CodingStandard]:
    """Get list of coding standards, optionally filtered to enforced only."""
    if enforce_only:
        return [std for std in CODING_STANDARDS if std.enforce]
    return CODING_STANDARDS


def check_quality_gates(
    line_coverage: float,
    branch_coverage: float,
    function_coverage: float,
    bugs: int = 0,
    vulnerabilities: int = 0,
    code_smells: int = 0,
    duplicated_lines_percent: float = 0.0,
    gates: QualityGates = DEFAULT_QUALITY_GATES,
) -> Dict[str, bool]:
    """Check if metrics pass quality gates. Returns dict of gate -> pass/fail."""
    return {
        "line_coverage": line_coverage >= gates.min_line_coverage,
        "branch_coverage": branch_coverage >= gates.min_branch_coverage,
        "function_coverage": function_coverage >= gates.min_function_coverage,
        "bugs": bugs <= gates.max_bugs,
        "vulnerabilities": vulnerabilities <= gates.max_vulnerabilities,
        "code_smells": code_smells <= gates.max_code_smells,
        "duplicated_lines": duplicated_lines_percent <= gates.max_duplicated_lines_percent,
    }


def passes_all_quality_gates(
    line_coverage: float,
    branch_coverage: float,
    function_coverage: float,
    bugs: int = 0,
    vulnerabilities: int = 0,
    code_smells: int = 0,
    duplicated_lines_percent: float = 0.0,
    gates: QualityGates = DEFAULT_QUALITY_GATES,
) -> bool:
    """Check if all quality gates pass."""
    results = check_quality_gates(
        line_coverage, branch_coverage, function_coverage,
        bugs, vulnerabilities, code_smells, duplicated_lines_percent, gates
    )
    return all(results.values())


def get_pre_generation_checklist(repo_name: str = "default") -> str:
    """Generate a pre-generation checklist for agents."""
    rules = get_enforced_rules(repo_name)
    standards = get_coding_standards(enforce_only=True)
    
    lines = [
        "## Pre-Generation Checklist",
        "",
        "### DO:",
    ]
    
    for rule in rules[:5]:
        if rule.autofix:
            lines.append(f"- {rule.autofix}")
    
    for std in standards[:3]:
        lines.append(f"- {std.good_example}")
    
    lines.extend([
        "",
        "### DON'T:",
    ])
    
    for rule in rules[:5]:
        lines.append(f"- {rule.prevent_message}")
    
    lines.extend([
        "",
        "### Coverage Requirements:",
        f"- Line Coverage: {DEFAULT_QUALITY_GATES.min_line_coverage}%",
        f"- Branch Coverage: {DEFAULT_QUALITY_GATES.min_branch_coverage}%",
        f"- Function Coverage: {DEFAULT_QUALITY_GATES.min_function_coverage}%",
    ])
    
    return "\n".join(lines)
