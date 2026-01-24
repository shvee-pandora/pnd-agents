"""
Technical Debt Agent

A dedicated agent for identifying, classifying, prioritizing, and explaining
technical debt across a repository using static analysis, repository context,
and optional SonarCloud data.

Key capabilities:
1. REPOSITORY ANALYSIS: Scan workspace for debt indicators
2. CLASSIFICATION: Categorize debt by type (Code, Test, Architecture, Dependency, Process)
3. SEVERITY SCORING: Rate impact and effort for each debt item
4. CONTEXT-AWARE: Use repo profile and conventions for targeted analysis

This agent is READ-ONLY and produces actionable reports for engineers,
tech leads, and leadership without modifying any code.
"""

import os
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import httpx


class DebtCategory(Enum):
    """Categories of technical debt."""
    CODE = "Code Debt"
    TEST = "Test Debt"
    ARCHITECTURE = "Architecture Debt"
    DEPENDENCY = "Dependency Debt"
    PROCESS = "Process/Documentation Debt"


class Severity(Enum):
    """Severity levels for technical debt."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ImpactType(Enum):
    """Types of impact from technical debt."""
    DELIVERY_RISK = "Delivery Risk"
    MAINTENANCE_COST = "Maintenance Cost"
    STABILITY_RISK = "Stability Risk"


class EffortSize(Enum):
    """Estimated effort to fix debt."""
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"


@dataclass
class DebtItem:
    """Represents a single technical debt item."""
    id: str
    title: str
    description: str
    category: DebtCategory
    severity: Severity
    impact: List[ImpactType]
    effort: EffortSize
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None
    source: str = "static_analysis"  # static_analysis, sonarcloud, manual
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "severity": self.severity.value,
            "impact": [i.value for i in self.impact],
            "effort": self.effort.value,
            "filePath": self.file_path,
            "lineNumber": self.line_number,
            "codeSnippet": self.code_snippet,
            "recommendation": self.recommendation,
            "source": self.source,
        }


@dataclass
class DebtSummary:
    """Summary statistics for technical debt."""
    total_items: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_effort: Dict[str, int] = field(default_factory=dict)
    high_risk_files: List[str] = field(default_factory=list)
    estimated_total_effort: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "totalItems": self.total_items,
            "byCategory": self.by_category,
            "bySeverity": self.by_severity,
            "byEffort": self.by_effort,
            "highRiskFiles": self.high_risk_files,
            "estimatedTotalEffort": self.estimated_total_effort,
        }


@dataclass
class TechnicalDebtReport:
    """Complete technical debt analysis report."""
    status: str  # success, error, partial
    repo_name: Optional[str] = None
    repo_path: Optional[str] = None
    summary: Optional[DebtSummary] = None
    items: List[DebtItem] = field(default_factory=list)
    hotspots: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    sonarcloud_integrated: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "repoName": self.repo_name,
            "repoPath": self.repo_path,
            "summary": self.summary.to_dict() if self.summary else None,
            "items": [item.to_dict() for item in self.items],
            "hotspots": self.hotspots,
            "recommendations": self.recommendations,
            "nextActions": self.next_actions,
            "sonarcloudIntegrated": self.sonarcloud_integrated,
            "error": self.error,
        }
    
    def to_markdown(self) -> str:
        """Generate markdown report suitable for engineers and leadership."""
        lines = []
        
        # Executive Summary
        lines.append("# Technical Debt Analysis Report")
        lines.append("")
        
        if self.repo_name:
            lines.append(f"**Repository:** {self.repo_name}")
        if self.repo_path:
            lines.append(f"**Path:** {self.repo_path}")
        lines.append(f"**SonarCloud Integration:** {'Yes' if self.sonarcloud_integrated else 'No'}")
        lines.append("")
        
        # Summary Section
        lines.append("## Executive Summary")
        lines.append("")
        if self.summary:
            lines.append(f"**Total Debt Items:** {self.summary.total_items}")
            lines.append(f"**Estimated Total Effort:** {self.summary.estimated_total_effort}")
            lines.append("")
            
            # Severity breakdown
            if self.summary.by_severity:
                lines.append("### Severity Distribution")
                lines.append("")
                lines.append("| Severity | Count |")
                lines.append("|----------|-------|")
                for severity, count in self.summary.by_severity.items():
                    lines.append(f"| {severity} | {count} |")
                lines.append("")
            
            # Category breakdown
            if self.summary.by_category:
                lines.append("### Category Distribution")
                lines.append("")
                lines.append("| Category | Count |")
                lines.append("|----------|-------|")
                for category, count in self.summary.by_category.items():
                    lines.append(f"| {category} | {count} |")
                lines.append("")
        
        # High-Risk Hotspots
        if self.hotspots:
            lines.append("## High-Risk Hotspots")
            lines.append("")
            lines.append("Files with the highest concentration of technical debt:")
            lines.append("")
            for i, hotspot in enumerate(self.hotspots[:10], 1):
                file_path = hotspot.get("file", "Unknown")
                debt_count = hotspot.get("debtCount", 0)
                risk_score = hotspot.get("riskScore", 0)
                lines.append(f"{i}. **{file_path}** - {debt_count} issues (Risk Score: {risk_score})")
            lines.append("")
        
        # Technical Debt Breakdown
        lines.append("## Technical Debt Breakdown")
        lines.append("")
        
        # Group items by category
        items_by_category: Dict[str, List[DebtItem]] = {}
        for item in self.items:
            cat = item.category.value
            if cat not in items_by_category:
                items_by_category[cat] = []
            items_by_category[cat].append(item)
        
        for category, items in items_by_category.items():
            lines.append(f"### {category}")
            lines.append("")
            for item in items[:10]:  # Limit to 10 per category
                severity_emoji = {"High": "!!!", "Medium": "!!", "Low": "!"}
                severity_marker = severity_emoji.get(item.severity.value, "")
                lines.append(f"#### {severity_marker} {item.title}")
                lines.append("")
                lines.append(f"**Severity:** {item.severity.value} | **Effort:** {item.effort.value}")
                if item.file_path:
                    location = f"{item.file_path}"
                    if item.line_number:
                        location += f":{item.line_number}"
                    lines.append(f"**Location:** `{location}`")
                lines.append("")
                lines.append(item.description)
                lines.append("")
                if item.recommendation:
                    lines.append(f"**Recommendation:** {item.recommendation}")
                    lines.append("")
            
            if len(items) > 10:
                lines.append(f"*... and {len(items) - 10} more items in this category*")
                lines.append("")
        
        # Recommendations
        if self.recommendations:
            lines.append("## Recommendations (Prioritized)")
            lines.append("")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # Next Actions
        if self.next_actions:
            lines.append("## Suggested Next Actions")
            lines.append("")
            for i, action in enumerate(self.next_actions, 1):
                lines.append(f"{i}. {action}")
            lines.append("")
        
        return "\n".join(lines)


class TechnicalDebtAgent:
    """
    Agent for identifying, classifying, and reporting technical debt.
    
    This agent performs READ-ONLY analysis and produces actionable reports
    suitable for engineers, tech leads, and leadership.
    
    Key capabilities:
    - Static code analysis for debt indicators
    - Optional SonarCloud integration for enhanced analysis
    - Context-aware recommendations using repo profile
    - Structured output in JSON and Markdown formats
    """
    
    SONARCLOUD_API_BASE = "https://sonarcloud.io/api"
    
    # Patterns for detecting technical debt indicators
    TODO_PATTERN = re.compile(r"(?://|#|/\*)\s*(TODO|FIXME|HACK|XXX|BUG|OPTIMIZE)[\s:]+(.+?)(?:\*/)?$", re.MULTILINE | re.IGNORECASE)
    DEPRECATED_PATTERN = re.compile(r"@deprecated|\.deprecated\(|DEPRECATED", re.IGNORECASE)
    LARGE_FUNCTION_PATTERN = re.compile(r"(?:function|const|async function)\s+(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{", re.MULTILINE)
    COMPLEXITY_INDICATORS = [
        re.compile(r"\bif\s*\("),
        re.compile(r"\belse\s+if\s*\("),
        re.compile(r"\bswitch\s*\("),
        re.compile(r"\bfor\s*\("),
        re.compile(r"\bwhile\s*\("),
        re.compile(r"\bcatch\s*\("),
        re.compile(r"\?\s*[^:]+\s*:"),  # ternary
    ]
    
    # File size thresholds
    LARGE_FILE_LINES = 500
    LARGE_FUNCTION_LINES = 100
    HIGH_COMPLEXITY_THRESHOLD = 15
    
    # File extensions to analyze
    ANALYZABLE_EXTENSIONS = {
        ".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".go", ".rs",
        ".css", ".scss", ".less", ".json", ".yaml", ".yml"
    }
    
    # Directories to skip
    SKIP_DIRECTORIES = {
        "node_modules", ".git", "dist", "build", ".next", "__pycache__",
        "coverage", ".nyc_output", "vendor", "target", ".cache"
    }
    
    def __init__(
        self,
        token: Optional[str] = None,
        organization: str = "pandora-jewelry",
        project_key: Optional[str] = None
    ):
        """
        Initialize the Technical Debt Agent.
        
        Args:
            token: SonarCloud API token (reads from SONAR_TOKEN env var if not provided)
            organization: SonarCloud organization
            project_key: SonarCloud project key (optional)
        """
        self.token = token or os.environ.get("SONAR_TOKEN")
        self.organization = organization
        self.project_key = project_key
        
        # HTTP client for SonarCloud API calls
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        self.client = httpx.Client(
            headers=headers,
            timeout=30.0,
        )
        
        self._debt_items: List[DebtItem] = []
        self._item_counter = 0
    
    def _generate_item_id(self) -> str:
        """Generate a unique ID for a debt item."""
        self._item_counter += 1
        return f"TD-{self._item_counter:04d}"
    
    def _load_repo_profile(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """Load repo profile if it exists."""
        profile_paths = [
            Path(repo_path) / ".claude" / "repo-profile.json",
            Path(repo_path) / ".ai" / "repo-profile.json",
            Path(repo_path) / "repo-profile.json",
        ]
        
        for profile_path in profile_paths:
            if profile_path.exists():
                try:
                    import json
                    with open(profile_path, 'r') as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
        
        return None
    
    def _should_skip_path(self, path: Path) -> bool:
        """Check if a path should be skipped during analysis."""
        for part in path.parts:
            if part in self.SKIP_DIRECTORIES:
                return True
        return False
    
    def _estimate_cyclomatic_complexity(self, content: str) -> int:
        """Estimate cyclomatic complexity from code content."""
        complexity = 1  # Base complexity
        for pattern in self.COMPLEXITY_INDICATORS:
            complexity += len(pattern.findall(content))
        return complexity
    
    def _count_function_lines(self, content: str, start_pos: int) -> int:
        """Count lines in a function starting from a position."""
        brace_count = 0
        started = False
        lines = 0
        
        for i, char in enumerate(content[start_pos:]):
            if char == '{':
                brace_count += 1
                started = True
            elif char == '}':
                brace_count -= 1
                if started and brace_count == 0:
                    break
            elif char == '\n' and started:
                lines += 1
        
        return lines
    
    def analyze_file(self, file_path: str, content: Optional[str] = None) -> List[DebtItem]:
        """
        Analyze a single file for technical debt indicators.
        
        Args:
            file_path: Path to the file
            content: Optional file content (reads from file if not provided)
            
        Returns:
            List of DebtItem objects found in the file
        """
        items: List[DebtItem] = []
        
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except (IOError, OSError):
                return items
        
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Check for large file
        if total_lines > self.LARGE_FILE_LINES:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title=f"Large file: {Path(file_path).name}",
                description=f"File has {total_lines} lines, exceeding the recommended {self.LARGE_FILE_LINES} lines. Large files are harder to maintain and understand.",
                category=DebtCategory.CODE,
                severity=Severity.MEDIUM if total_lines < 1000 else Severity.HIGH,
                impact=[ImpactType.MAINTENANCE_COST],
                effort=EffortSize.LARGE,
                file_path=file_path,
                recommendation="Consider splitting this file into smaller, focused modules with single responsibilities.",
            ))
        
        # Find TODO/FIXME comments
        for match in self.TODO_PATTERN.finditer(content):
            tag = match.group(1).upper()
            message = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            severity = Severity.HIGH if tag in ["FIXME", "BUG", "HACK"] else Severity.LOW
            
            items.append(DebtItem(
                id=self._generate_item_id(),
                title=f"{tag} comment found",
                description=message,
                category=DebtCategory.CODE,
                severity=severity,
                impact=[ImpactType.MAINTENANCE_COST],
                effort=EffortSize.SMALL if tag == "TODO" else EffortSize.MEDIUM,
                file_path=file_path,
                line_number=line_num,
                code_snippet=match.group(0),
                recommendation=f"Address this {tag} comment or create a tracked issue for it.",
            ))
        
        # Find deprecated patterns
        for match in self.DEPRECATED_PATTERN.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            items.append(DebtItem(
                id=self._generate_item_id(),
                title="Deprecated code usage",
                description="Code marked as deprecated or using deprecated APIs should be updated.",
                category=DebtCategory.CODE,
                severity=Severity.MEDIUM,
                impact=[ImpactType.STABILITY_RISK, ImpactType.MAINTENANCE_COST],
                effort=EffortSize.MEDIUM,
                file_path=file_path,
                line_number=line_num,
                recommendation="Update to use the recommended replacement API or pattern.",
            ))
        
        # Check for high complexity
        complexity = self._estimate_cyclomatic_complexity(content)
        if complexity > self.HIGH_COMPLEXITY_THRESHOLD:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title=f"High cyclomatic complexity: {complexity}",
                description=f"File has estimated cyclomatic complexity of {complexity}, exceeding threshold of {self.HIGH_COMPLEXITY_THRESHOLD}. High complexity makes code harder to test and maintain.",
                category=DebtCategory.CODE,
                severity=Severity.HIGH if complexity > 30 else Severity.MEDIUM,
                impact=[ImpactType.MAINTENANCE_COST, ImpactType.STABILITY_RISK],
                effort=EffortSize.LARGE,
                file_path=file_path,
                recommendation="Refactor complex logic into smaller, focused functions. Use early returns and extract conditional logic.",
            ))
        
        # Find large functions
        for match in self.LARGE_FUNCTION_PATTERN.finditer(content):
            func_name = match.group(1)
            func_lines = self._count_function_lines(content, match.start())
            
            if func_lines > self.LARGE_FUNCTION_LINES:
                line_num = content[:match.start()].count('\n') + 1
                items.append(DebtItem(
                    id=self._generate_item_id(),
                    title=f"Large function: {func_name}",
                    description=f"Function '{func_name}' has approximately {func_lines} lines, exceeding the recommended {self.LARGE_FUNCTION_LINES} lines.",
                    category=DebtCategory.CODE,
                    severity=Severity.MEDIUM,
                    impact=[ImpactType.MAINTENANCE_COST],
                    effort=EffortSize.MEDIUM,
                    file_path=file_path,
                    line_number=line_num,
                    recommendation=f"Break down '{func_name}' into smaller, single-purpose functions.",
                ))
        
        return items
    
    def analyze_directory(
        self,
        directory_path: str,
        max_files: int = 500
    ) -> List[DebtItem]:
        """
        Analyze all files in a directory for technical debt.
        
        Args:
            directory_path: Path to the directory
            max_files: Maximum number of files to analyze
            
        Returns:
            List of DebtItem objects found
        """
        items: List[DebtItem] = []
        files_analyzed = 0
        
        dir_path = Path(directory_path)
        if not dir_path.exists():
            return items
        
        for file_path in dir_path.rglob("*"):
            if files_analyzed >= max_files:
                break
            
            if not file_path.is_file():
                continue
            
            if self._should_skip_path(file_path):
                continue
            
            if file_path.suffix not in self.ANALYZABLE_EXTENSIONS:
                continue
            
            file_items = self.analyze_file(str(file_path))
            items.extend(file_items)
            files_analyzed += 1
        
        return items
    
    def analyze_test_coverage(self, repo_path: str) -> List[DebtItem]:
        """
        Analyze test coverage and identify test debt.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            List of test-related DebtItem objects
        """
        items: List[DebtItem] = []
        repo = Path(repo_path)
        
        # Check for test directories
        test_dirs = ["__tests__", "tests", "test", "spec"]
        has_tests = any((repo / d).exists() for d in test_dirs)
        
        if not has_tests:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title="No test directory found",
                description="Repository does not appear to have a dedicated test directory. This indicates potential lack of test coverage.",
                category=DebtCategory.TEST,
                severity=Severity.HIGH,
                impact=[ImpactType.STABILITY_RISK, ImpactType.DELIVERY_RISK],
                effort=EffortSize.LARGE,
                recommendation="Create a test directory and add unit tests for critical business logic.",
            ))
        
        # Check for test configuration files
        test_configs = [
            "jest.config.js", "jest.config.ts", "vitest.config.ts",
            "pytest.ini", "setup.cfg", "pyproject.toml"
        ]
        has_test_config = any((repo / c).exists() for c in test_configs)
        
        if has_tests and not has_test_config:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title="Missing test configuration",
                description="Test directory exists but no test framework configuration file was found.",
                category=DebtCategory.TEST,
                severity=Severity.MEDIUM,
                impact=[ImpactType.MAINTENANCE_COST],
                effort=EffortSize.SMALL,
                recommendation="Add a test configuration file (e.g., jest.config.js, vitest.config.ts) for consistent test execution.",
            ))
        
        # Check for coverage configuration
        coverage_configs = [
            "coverage", ".nyc_output", "htmlcov", ".coverage"
        ]
        has_coverage = any((repo / c).exists() for c in coverage_configs)
        
        if has_tests and not has_coverage:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title="No coverage reports found",
                description="Tests exist but no coverage reports were found. Code coverage tracking helps identify untested code.",
                category=DebtCategory.TEST,
                severity=Severity.LOW,
                impact=[ImpactType.MAINTENANCE_COST],
                effort=EffortSize.SMALL,
                recommendation="Configure coverage reporting in your test framework and CI pipeline.",
            ))
        
        return items
    
    def analyze_dependencies(self, repo_path: str) -> List[DebtItem]:
        """
        Analyze dependencies for potential debt.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            List of dependency-related DebtItem objects
        """
        items: List[DebtItem] = []
        repo = Path(repo_path)
        
        # Check package.json for Node.js projects
        package_json = repo / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    pkg = json.load(f)
                
                deps = pkg.get("dependencies", {})
                dev_deps = pkg.get("devDependencies", {})
                
                # Check for outdated patterns
                if "react" in deps:
                    react_version = deps["react"]
                    if react_version.startswith("^16") or react_version.startswith("16"):
                        items.append(DebtItem(
                            id=self._generate_item_id(),
                            title="Outdated React version",
                            description=f"React version {react_version} is outdated. Consider upgrading to React 18+ for improved performance and features.",
                            category=DebtCategory.DEPENDENCY,
                            severity=Severity.MEDIUM,
                            impact=[ImpactType.MAINTENANCE_COST, ImpactType.STABILITY_RISK],
                            effort=EffortSize.LARGE,
                            file_path=str(package_json),
                            recommendation="Plan a React upgrade to version 18+ to benefit from concurrent features and improved performance.",
                        ))
                
                # Check for deprecated packages
                deprecated_packages = ["request", "node-sass", "tslint", "enzyme"]
                for pkg_name in deprecated_packages:
                    if pkg_name in deps or pkg_name in dev_deps:
                        items.append(DebtItem(
                            id=self._generate_item_id(),
                            title=f"Deprecated package: {pkg_name}",
                            description=f"Package '{pkg_name}' is deprecated and should be replaced with a maintained alternative.",
                            category=DebtCategory.DEPENDENCY,
                            severity=Severity.MEDIUM,
                            impact=[ImpactType.STABILITY_RISK, ImpactType.MAINTENANCE_COST],
                            effort=EffortSize.MEDIUM,
                            file_path=str(package_json),
                            recommendation=f"Replace '{pkg_name}' with its recommended successor.",
                        ))
                
                # Check for too many dependencies
                total_deps = len(deps) + len(dev_deps)
                if total_deps > 100:
                    items.append(DebtItem(
                        id=self._generate_item_id(),
                        title=f"High dependency count: {total_deps}",
                        description=f"Project has {total_deps} dependencies. Large dependency trees increase security risk and maintenance burden.",
                        category=DebtCategory.DEPENDENCY,
                        severity=Severity.LOW,
                        impact=[ImpactType.MAINTENANCE_COST, ImpactType.STABILITY_RISK],
                        effort=EffortSize.MEDIUM,
                        file_path=str(package_json),
                        recommendation="Audit dependencies and remove unused packages. Consider consolidating similar functionality.",
                    ))
                
            except (json.JSONDecodeError, IOError):
                pass
        
        # Check for lock file consistency
        lock_files = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
        lock_count = sum(1 for lf in lock_files if (repo / lf).exists())
        
        if lock_count > 1:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title="Multiple lock files detected",
                description="Multiple package manager lock files exist. This can cause inconsistent installations.",
                category=DebtCategory.DEPENDENCY,
                severity=Severity.MEDIUM,
                impact=[ImpactType.STABILITY_RISK],
                effort=EffortSize.SMALL,
                recommendation="Standardize on a single package manager and remove other lock files.",
            ))
        
        return items
    
    def analyze_architecture(self, repo_path: str) -> List[DebtItem]:
        """
        Analyze architecture patterns for potential debt.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            List of architecture-related DebtItem objects
        """
        items: List[DebtItem] = []
        repo = Path(repo_path)
        
        # Check for mixed patterns (e.g., both pages and app router in Next.js)
        has_pages = (repo / "pages").exists() or (repo / "src" / "pages").exists()
        has_app = (repo / "app").exists() or (repo / "src" / "app").exists()
        
        if has_pages and has_app:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title="Mixed Next.js routing patterns",
                description="Both 'pages' and 'app' directories exist. This indicates a partial migration to App Router.",
                category=DebtCategory.ARCHITECTURE,
                severity=Severity.MEDIUM,
                impact=[ImpactType.MAINTENANCE_COST, ImpactType.DELIVERY_RISK],
                effort=EffortSize.LARGE,
                recommendation="Complete the migration to App Router or document the hybrid approach and migration plan.",
            ))
        
        # Check for deeply nested directories
        max_depth = 0
        for path in repo.rglob("*"):
            if self._should_skip_path(path):
                continue
            depth = len(path.relative_to(repo).parts)
            max_depth = max(max_depth, depth)
        
        if max_depth > 10:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title=f"Deep directory nesting: {max_depth} levels",
                description=f"Directory structure has {max_depth} levels of nesting. Deep nesting makes navigation and imports difficult.",
                category=DebtCategory.ARCHITECTURE,
                severity=Severity.LOW,
                impact=[ImpactType.MAINTENANCE_COST],
                effort=EffortSize.MEDIUM,
                recommendation="Consider flattening the directory structure or using path aliases for deep imports.",
            ))
        
        # Check for missing documentation
        doc_files = ["README.md", "CONTRIBUTING.md", "ARCHITECTURE.md"]
        missing_docs = [d for d in doc_files if not (repo / d).exists()]
        
        if "README.md" in missing_docs:
            items.append(DebtItem(
                id=self._generate_item_id(),
                title="Missing README.md",
                description="Repository lacks a README file. This makes onboarding and understanding the project difficult.",
                category=DebtCategory.PROCESS,
                severity=Severity.MEDIUM,
                impact=[ImpactType.MAINTENANCE_COST],
                effort=EffortSize.SMALL,
                recommendation="Create a README.md with project overview, setup instructions, and contribution guidelines.",
            ))
        
        return items
    
    def fetch_sonarcloud_issues(
        self,
        project_key: Optional[str] = None,
        branch: str = "main"
    ) -> List[DebtItem]:
        """
        Fetch issues from SonarCloud and convert to DebtItems.
        
        Args:
            project_key: SonarCloud project key
            branch: Branch to analyze
            
        Returns:
            List of DebtItem objects from SonarCloud
        """
        items: List[DebtItem] = []
        
        if not self.token:
            return items
        
        key = project_key or self.project_key
        if not key:
            return items
        
        try:
            # Fetch issues from SonarCloud
            response = self.client.get(
                f"{self.SONARCLOUD_API_BASE}/issues/search",
                params={
                    "componentKeys": key,
                    "branch": branch,
                    "ps": 100,  # Page size
                    "statuses": "OPEN,CONFIRMED,REOPENED",
                }
            )
            
            if response.status_code != 200:
                return items
            
            data = response.json()
            issues = data.get("issues", [])
            
            for issue in issues:
                # Map SonarCloud severity to our severity
                sonar_severity = issue.get("severity", "MINOR")
                severity_map = {
                    "BLOCKER": Severity.HIGH,
                    "CRITICAL": Severity.HIGH,
                    "MAJOR": Severity.MEDIUM,
                    "MINOR": Severity.LOW,
                    "INFO": Severity.LOW,
                }
                severity = severity_map.get(sonar_severity, Severity.LOW)
                
                # Map SonarCloud type to our category
                sonar_type = issue.get("type", "CODE_SMELL")
                category_map = {
                    "BUG": DebtCategory.CODE,
                    "VULNERABILITY": DebtCategory.CODE,
                    "CODE_SMELL": DebtCategory.CODE,
                    "SECURITY_HOTSPOT": DebtCategory.CODE,
                }
                category = category_map.get(sonar_type, DebtCategory.CODE)
                
                # Map effort
                effort_str = issue.get("effort", "30min")
                if "h" in effort_str or "d" in effort_str:
                    effort = EffortSize.LARGE
                elif "30min" in effort_str or "1h" in effort_str:
                    effort = EffortSize.MEDIUM
                else:
                    effort = EffortSize.SMALL
                
                items.append(DebtItem(
                    id=self._generate_item_id(),
                    title=issue.get("message", "SonarCloud Issue"),
                    description=f"SonarCloud {sonar_type}: {issue.get('message', '')}",
                    category=category,
                    severity=severity,
                    impact=[ImpactType.MAINTENANCE_COST],
                    effort=effort,
                    file_path=issue.get("component", "").split(":")[-1],
                    line_number=issue.get("line"),
                    source="sonarcloud",
                    recommendation=f"Fix SonarCloud rule {issue.get('rule', 'unknown')}",
                ))
            
        except Exception:
            pass  # SonarCloud integration is optional
        
        return items
    
    def _calculate_summary(self, items: List[DebtItem]) -> DebtSummary:
        """Calculate summary statistics from debt items."""
        summary = DebtSummary(total_items=len(items))
        
        # Count by category
        for item in items:
            cat = item.category.value
            summary.by_category[cat] = summary.by_category.get(cat, 0) + 1
        
        # Count by severity
        for item in items:
            sev = item.severity.value
            summary.by_severity[sev] = summary.by_severity.get(sev, 0) + 1
        
        # Count by effort
        for item in items:
            eff = item.effort.value
            summary.by_effort[eff] = summary.by_effort.get(eff, 0) + 1
        
        # Calculate high-risk files
        file_debt_count: Dict[str, int] = {}
        for item in items:
            if item.file_path:
                file_debt_count[item.file_path] = file_debt_count.get(item.file_path, 0) + 1
        
        sorted_files = sorted(file_debt_count.items(), key=lambda x: x[1], reverse=True)
        summary.high_risk_files = [f[0] for f in sorted_files[:10]]
        
        # Estimate total effort
        effort_hours = {
            EffortSize.SMALL: 2,
            EffortSize.MEDIUM: 8,
            EffortSize.LARGE: 24,
        }
        total_hours = sum(effort_hours.get(item.effort, 4) for item in items)
        
        if total_hours < 8:
            summary.estimated_total_effort = f"{total_hours} hours"
        elif total_hours < 40:
            summary.estimated_total_effort = f"{total_hours // 8} days"
        else:
            summary.estimated_total_effort = f"{total_hours // 40} weeks"
        
        return summary
    
    def _calculate_hotspots(self, items: List[DebtItem]) -> List[Dict[str, Any]]:
        """Calculate high-risk hotspots from debt items."""
        file_data: Dict[str, Dict[str, Any]] = {}
        
        for item in items:
            if not item.file_path:
                continue
            
            if item.file_path not in file_data:
                file_data[item.file_path] = {
                    "file": item.file_path,
                    "debtCount": 0,
                    "highSeverityCount": 0,
                    "categories": set(),
                }
            
            file_data[item.file_path]["debtCount"] += 1
            file_data[item.file_path]["categories"].add(item.category.value)
            
            if item.severity == Severity.HIGH:
                file_data[item.file_path]["highSeverityCount"] += 1
        
        # Calculate risk score
        for data in file_data.values():
            data["riskScore"] = (
                data["debtCount"] * 1 +
                data["highSeverityCount"] * 3 +
                len(data["categories"]) * 2
            )
            data["categories"] = list(data["categories"])
        
        # Sort by risk score
        hotspots = sorted(file_data.values(), key=lambda x: x["riskScore"], reverse=True)
        return hotspots[:20]
    
    def _generate_recommendations(self, items: List[DebtItem], summary: DebtSummary) -> List[str]:
        """Generate prioritized recommendations based on analysis."""
        recommendations = []
        
        # High severity items first
        high_count = summary.by_severity.get("High", 0)
        if high_count > 0:
            recommendations.append(
                f"Address {high_count} high-severity items first, focusing on FIXME/BUG comments and high-complexity code."
            )
        
        # Category-specific recommendations
        if summary.by_category.get("Test Debt", 0) > 0:
            recommendations.append(
                "Improve test coverage by adding unit tests for critical business logic and edge cases."
            )
        
        if summary.by_category.get("Dependency Debt", 0) > 0:
            recommendations.append(
                "Audit and update dependencies, removing deprecated packages and consolidating similar functionality."
            )
        
        if summary.by_category.get("Architecture Debt", 0) > 0:
            recommendations.append(
                "Document architectural decisions and create a migration plan for legacy patterns."
            )
        
        # File-specific recommendations
        if summary.high_risk_files:
            recommendations.append(
                f"Prioritize refactoring high-risk files: {', '.join(summary.high_risk_files[:3])}"
            )
        
        # Effort-based recommendations
        large_count = summary.by_effort.get("L", 0)
        if large_count > 3:
            recommendations.append(
                f"Break down {large_count} large-effort items into smaller, incremental improvements."
            )
        
        return recommendations
    
    def _generate_next_actions(self, items: List[DebtItem], summary: DebtSummary) -> List[str]:
        """Generate suggested next actions."""
        actions = []
        
        # Quick wins
        small_count = summary.by_effort.get("S", 0)
        if small_count > 0:
            actions.append(
                f"Start with {small_count} small-effort items for quick wins and momentum."
            )
        
        # TODO cleanup
        todo_items = [i for i in items if "TODO" in i.title or "FIXME" in i.title]
        if todo_items:
            actions.append(
                f"Create tracked issues for {len(todo_items)} TODO/FIXME comments and remove resolved ones."
            )
        
        # Test coverage
        test_items = [i for i in items if i.category == DebtCategory.TEST]
        if test_items:
            actions.append(
                "Set up code coverage reporting in CI pipeline to track test debt reduction."
            )
        
        # Documentation
        doc_items = [i for i in items if i.category == DebtCategory.PROCESS]
        if doc_items:
            actions.append(
                "Schedule a documentation sprint to address process and documentation debt."
            )
        
        # Regular review
        actions.append(
            "Schedule monthly technical debt review sessions to track progress and identify new debt."
        )
        
        return actions
    
    def analyze(
        self,
        repo_path: str,
        include_sonarcloud: bool = True,
        sonar_project_key: Optional[str] = None,
        sonar_branch: str = "main",
        output_format: str = "both"
    ) -> TechnicalDebtReport:
        """
        Perform comprehensive technical debt analysis on a repository.
        
        Args:
            repo_path: Path to the repository
            include_sonarcloud: Whether to include SonarCloud data
            sonar_project_key: SonarCloud project key (optional)
            sonar_branch: Branch to analyze in SonarCloud
            output_format: Output format (json, markdown, both)
            
        Returns:
            TechnicalDebtReport with complete analysis
        """
        self._debt_items = []
        self._item_counter = 0
        
        repo = Path(repo_path)
        if not repo.exists():
            return TechnicalDebtReport(
                status="error",
                error=f"Repository path does not exist: {repo_path}"
            )
        
        # Load repo profile for context-aware analysis
        repo_profile = self._load_repo_profile(repo_path)
        repo_name = repo_profile.get("identity", {}).get("name") if repo_profile else repo.name
        
        # Perform static analysis
        code_items = self.analyze_directory(repo_path)
        test_items = self.analyze_test_coverage(repo_path)
        dep_items = self.analyze_dependencies(repo_path)
        arch_items = self.analyze_architecture(repo_path)
        
        all_items = code_items + test_items + dep_items + arch_items
        
        # Optionally include SonarCloud data
        sonarcloud_integrated = False
        if include_sonarcloud and self.token:
            sonar_items = self.fetch_sonarcloud_issues(
                project_key=sonar_project_key,
                branch=sonar_branch
            )
            if sonar_items:
                all_items.extend(sonar_items)
                sonarcloud_integrated = True
        
        # Calculate summary and hotspots
        summary = self._calculate_summary(all_items)
        hotspots = self._calculate_hotspots(all_items)
        recommendations = self._generate_recommendations(all_items, summary)
        next_actions = self._generate_next_actions(all_items, summary)
        
        return TechnicalDebtReport(
            status="success",
            repo_name=repo_name,
            repo_path=repo_path,
            summary=summary,
            items=all_items,
            hotspots=hotspots,
            recommendations=recommendations,
            next_actions=next_actions,
            sonarcloud_integrated=sonarcloud_integrated,
        )
    
    def generate_register(
        self,
        repo_path: str,
        include_sonarcloud: bool = True
    ) -> str:
        """
        Generate a technical debt register (detailed inventory).
        
        Args:
            repo_path: Path to the repository
            include_sonarcloud: Whether to include SonarCloud data
            
        Returns:
            Markdown-formatted debt register
        """
        report = self.analyze(repo_path, include_sonarcloud=include_sonarcloud)
        
        lines = ["# Technical Debt Register", ""]
        lines.append(f"**Generated for:** {report.repo_name}")
        lines.append(f"**Total Items:** {report.summary.total_items if report.summary else 0}")
        lines.append("")
        
        lines.append("## Debt Inventory")
        lines.append("")
        lines.append("| ID | Title | Category | Severity | Effort | Location |")
        lines.append("|-----|-------|----------|----------|--------|----------|")
        
        for item in report.items:
            location = item.file_path or "N/A"
            if item.line_number:
                location += f":{item.line_number}"
            lines.append(
                f"| {item.id} | {item.title[:50]} | {item.category.value} | "
                f"{item.severity.value} | {item.effort.value} | {location[:30]} |"
            )
        
        return "\n".join(lines)
    
    def generate_summary(
        self,
        repo_path: str,
        include_sonarcloud: bool = True
    ) -> str:
        """
        Generate an executive summary of technical debt.
        
        Args:
            repo_path: Path to the repository
            include_sonarcloud: Whether to include SonarCloud data
            
        Returns:
            Markdown-formatted executive summary
        """
        report = self.analyze(repo_path, include_sonarcloud=include_sonarcloud)
        
        if report.status == "error":
            return f"Error: {report.error}"
        
        lines = ["# Technical Debt Executive Summary", ""]
        
        if report.summary:
            lines.append(f"**Repository:** {report.repo_name}")
            lines.append(f"**Total Debt Items:** {report.summary.total_items}")
            lines.append(f"**Estimated Effort:** {report.summary.estimated_total_effort}")
            lines.append("")
            
            # Risk assessment
            high_count = report.summary.by_severity.get("High", 0)
            medium_count = report.summary.by_severity.get("Medium", 0)
            
            if high_count > 10:
                risk_level = "HIGH"
            elif high_count > 5 or medium_count > 20:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            lines.append(f"**Overall Risk Level:** {risk_level}")
            lines.append("")
            
            # Key findings
            lines.append("## Key Findings")
            lines.append("")
            for rec in report.recommendations[:5]:
                lines.append(f"- {rec}")
            lines.append("")
            
            # Immediate actions
            lines.append("## Recommended Actions")
            lines.append("")
            for action in report.next_actions[:3]:
                lines.append(f"1. {action}")
        
        return "\n".join(lines)
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the technical debt agent with the given context.
        
        This method is called by the Task Manager or workflow engine.
        
        Args:
            context: Context dictionary with task, input, metadata
            
        Returns:
            Result dictionary with status, data, and optional next agent
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        metadata = context.get("metadata", {})
        
        # Get repo path from context
        repo_path = input_data.get("repo_path") or metadata.get("repo_path") or os.getcwd()
        
        # Determine output type from task
        task_lower = task.lower()
        
        if "register" in task_lower:
            result = self.generate_register(repo_path)
            return {
                "status": "success",
                "data": {"register": result, "format": "markdown"},
            }
        elif "summary" in task_lower or "leadership" in task_lower or "executive" in task_lower:
            result = self.generate_summary(repo_path)
            return {
                "status": "success",
                "data": {"summary": result, "format": "markdown"},
            }
        else:
            # Full analysis
            report = self.analyze(repo_path)
            return {
                "status": report.status,
                "data": {
                    "report": report.to_dict(),
                    "markdown": report.to_markdown(),
                },
                "error": report.error,
            }


def run(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function to run the Technical Debt Agent.
    
    Args:
        context: Context dictionary with task, input, metadata
        
    Returns:
        Result dictionary
    """
    agent = TechnicalDebtAgent()
    return agent.run(context)


def analyze_technical_debt(
    repo_path: str,
    include_sonarcloud: bool = True,
    output_format: str = "both"
) -> TechnicalDebtReport:
    """
    Convenience function to analyze technical debt in a repository.
    
    Args:
        repo_path: Path to the repository
        include_sonarcloud: Whether to include SonarCloud data
        output_format: Output format (json, markdown, both)
        
    Returns:
        TechnicalDebtReport with complete analysis
    """
    agent = TechnicalDebtAgent()
    return agent.analyze(repo_path, include_sonarcloud=include_sonarcloud, output_format=output_format)
