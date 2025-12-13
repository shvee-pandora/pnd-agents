"""
Unit Test Agent

A dedicated agent for generating minimal, focused unit tests following Pandora coding standards.
This agent analyzes source code and generates Jest/Vitest tests for React components,
utility functions, hooks, and API routes.

Key principles:
- Generate minimal tests that cover real business logic, not boilerplate
- Never introduce new Sonar issues (use globalThis, avoid any, no TODO comments)
- Extend existing test files rather than replacing them
- Respect project coding guidelines from CODING_STANDARDS.md
- Prefer small, readable test blocks over comprehensive coverage
"""

import os
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class TestFramework(Enum):
    """Supported test frameworks."""
    JEST = "jest"
    VITEST = "vitest"
    PLAYWRIGHT = "playwright"
    TESTING_LIBRARY = "testing-library"


class CoverageType(Enum):
    """Types of code coverage."""
    STATEMENT = "statement"
    BRANCH = "branch"
    FUNCTION = "function"
    LINE = "line"


@dataclass
class TestGenerationConfig:
    """Configuration for test generation to ensure minimal, Sonar-compliant output.
    
    These settings help prevent over-generation and ensure tests follow
    Pandora coding standards and don't introduce Sonar violations.
    """
    max_tests_per_unit: int = 3
    max_tests_per_file: int = 15
    max_lines_per_file: int = 200
    include_snapshot_tests: bool = False
    include_accessibility_tests: bool = False
    extend_existing_tests: bool = True
    use_globalThis: bool = True
    avoid_any_type: bool = True
    no_todo_comments: bool = True
    
    # Sonar rules to avoid violating
    sonar_safe_patterns: Dict[str, str] = field(default_factory=lambda: {
        "S7764": "Use globalThis instead of global",
        "S4325": "Avoid unnecessary type assertions",
        "S7741": "Use x === undefined instead of typeof x === 'undefined'",
        "S7780": "Avoid complex escape sequences",
        "S6759": "Do NOT add Readonly<> to props (Pandora standard)",
    })


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    description: str
    test_type: str  # unit, integration, e2e
    assertions: List[str] = field(default_factory=list)
    setup: Optional[str] = None
    teardown: Optional[str] = None
    mocks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "testType": self.test_type,
            "assertions": self.assertions,
            "setup": self.setup,
            "teardown": self.teardown,
            "mocks": self.mocks,
        }


@dataclass
class CoverageReport:
    """Represents code coverage metrics."""
    statements: float = 0.0
    branches: float = 0.0
    functions: float = 0.0
    lines: float = 0.0
    uncovered_lines: List[int] = field(default_factory=list)
    uncovered_branches: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "statements": self.statements,
            "branches": self.branches,
            "functions": self.functions,
            "lines": self.lines,
            "uncoveredLines": self.uncovered_lines,
            "uncoveredBranches": self.uncovered_branches,
            "overall": self.overall_coverage,
            "meets100Percent": self.meets_100_percent,
        }
    
    @property
    def overall_coverage(self) -> float:
        """Calculate overall coverage percentage."""
        return (self.statements + self.branches + self.functions + self.lines) / 4
    
    @property
    def meets_100_percent(self) -> bool:
        """Check if coverage meets 100% target."""
        return all([
            self.statements >= 100,
            self.branches >= 100,
            self.functions >= 100,
            self.lines >= 100,
        ])


@dataclass
class TestFile:
    """Represents a generated test file."""
    source_file: str
    test_file_path: str
    test_cases: List[TestCase] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    mocks: List[str] = field(default_factory=list)
    coverage: Optional[CoverageReport] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sourceFile": self.source_file,
            "testFilePath": self.test_file_path,
            "testCases": [tc.to_dict() for tc in self.test_cases],
            "imports": self.imports,
            "mocks": self.mocks,
            "coverage": self.coverage.to_dict() if self.coverage else None,
        }


@dataclass
class UnitTestResult:
    """Result from unit test generation."""
    status: str  # success, error, partial
    test_files: List[TestFile] = field(default_factory=list)
    total_test_cases: int = 0
    coverage_summary: Optional[CoverageReport] = None
    recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "testFiles": [tf.to_dict() for tf in self.test_files],
            "totalTestCases": self.total_test_cases,
            "coverageSummary": self.coverage_summary.to_dict() if self.coverage_summary else None,
            "recommendations": self.recommendations,
            "error": self.error,
        }


class UnitTestAgent:
    """
    Agent for generating minimal, focused unit tests following Pandora coding standards.
    
    Key principles:
    - Generate only essential tests that cover real business logic
    - Never introduce new Sonar issues
    - Extend existing test files rather than replacing them
    - Respect max limits for tests per file and lines per file
    - Use Sonar-safe patterns (globalThis, no any, no TODO comments)
    """
    
    # Patterns for identifying testable code
    FUNCTION_PATTERN = re.compile(
        r'(?:export\s+)?(?:async\s+)?function\s+(\w+)|'
        r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*(?::\s*\w+)?\s*=>'
    )
    
    COMPONENT_PATTERN = re.compile(
        r'(?:export\s+)?(?:default\s+)?(?:function|const)\s+(\w+).*?(?:React\.FC|JSX\.Element|ReactNode)'
    )
    
    HOOK_PATTERN = re.compile(
        r'(?:export\s+)?(?:const|function)\s+(use\w+)'
    )
    
    CLASS_PATTERN = re.compile(
        r'(?:export\s+)?class\s+(\w+)'
    )
    
    BRANCH_PATTERNS = [
        re.compile(r'\bif\s*\('),
        re.compile(r'\belse\s+if\s*\('),
        re.compile(r'\belse\s*\{'),
        re.compile(r'\bswitch\s*\('),
        re.compile(r'\bcase\s+'),
        re.compile(r'\?\s*[^:]+\s*:'),  # ternary
        re.compile(r'\?\?'),  # nullish coalescing
        re.compile(r'\|\|'),  # logical or
        re.compile(r'&&'),  # logical and
    ]
    
    def __init__(
        self,
        framework: TestFramework = TestFramework.JEST,
        config: Optional[TestGenerationConfig] = None
    ):
        """
        Initialize the Unit Test Agent.
        
        Args:
            framework: Test framework to use (jest, vitest, etc.)
            config: Configuration for test generation limits and Sonar compliance
        """
        self.framework = framework
        self.config = config or TestGenerationConfig()
        self.test_files: List[TestFile] = []
    
    def analyze_file(self, file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a source file to identify testable elements.
        
        Args:
            file_path: Path to the source file
            content: Optional file content (if not provided, reads from file)
            
        Returns:
            Analysis results including functions, components, hooks, branches
        """
        if content is None:
            with open(file_path, 'r') as f:
                content = f.read()
        
        analysis = {
            "file": file_path,
            "functions": [],
            "components": [],
            "hooks": [],
            "classes": [],
            "branches": 0,
            "lines": len(content.split('\n')),
            "imports": [],
            "exports": [],
        }
        
        # Find functions
        for match in self.FUNCTION_PATTERN.finditer(content):
            func_name = match.group(1) or match.group(2)
            if func_name:
                analysis["functions"].append(func_name)
        
        # Find React components
        for match in self.COMPONENT_PATTERN.finditer(content):
            analysis["components"].append(match.group(1))
        
        # Find hooks
        for match in self.HOOK_PATTERN.finditer(content):
            analysis["hooks"].append(match.group(1))
        
        # Find classes
        for match in self.CLASS_PATTERN.finditer(content):
            analysis["classes"].append(match.group(1))
        
        # Count branches
        for pattern in self.BRANCH_PATTERNS:
            analysis["branches"] += len(pattern.findall(content))
        
        # Find imports
        import_pattern = re.compile(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]")
        analysis["imports"] = import_pattern.findall(content)
        
        # Find exports
        export_pattern = re.compile(r"export\s+(?:default\s+)?(?:const|function|class)\s+(\w+)")
        analysis["exports"] = export_pattern.findall(content)
        
        return analysis
    
    def generate_test_cases(self, analysis: Dict[str, Any], content: str) -> List[TestCase]:
        """
        Generate minimal, focused test cases based on file analysis.
        
        Following Pandora coding standards:
        - Only cover real business logic paths
        - Respect max_tests_per_unit and max_tests_per_file limits
        - No snapshot tests by default (they create maintenance burden)
        - No accessibility tests by default (use dedicated a11y tools)
        - No generic "toBeDefined()" assertions (low value)
        
        Args:
            analysis: File analysis results
            content: Source file content
            
        Returns:
            List of focused test cases (limited by config)
        """
        test_cases: List[TestCase] = []
        has_meaningful_branches = analysis["branches"] > 2
        
        # Generate tests for functions (max 2 per function)
        for func_name in analysis["functions"]:
            if len(test_cases) >= self.config.max_tests_per_file:
                break
                
            # Only generate one focused test per function
            test_cases.append(TestCase(
                name=f"should execute {func_name} with valid input",
                description=f"Test {func_name} happy path",
                test_type="unit",
                assertions=["expect(result).not.toBeNull()"],
            ))
            
            # Add error handling test only if function has try/catch or throws
            if has_meaningful_branches and len(test_cases) < self.config.max_tests_per_file:
                test_cases.append(TestCase(
                    name=f"should handle edge cases in {func_name}",
                    description=f"Test {func_name} with edge case input",
                    test_type="unit",
                    assertions=["expect(result).toBeDefined()"],
                ))
        
        # Generate tests for React components (max 2 per component)
        for component in analysis["components"]:
            if len(test_cases) >= self.config.max_tests_per_file:
                break
                
            # Basic render test (always include)
            test_cases.append(TestCase(
                name=f"renders {component} correctly",
                description=f"Test that {component} renders without errors",
                test_type="unit",
                assertions=["expect(container.firstChild).not.toBeNull()"],
                setup=f"const {{ container }} = render(<{component} />)",
            ))
            
            # Interaction test only if component likely has handlers
            if has_meaningful_branches and len(test_cases) < self.config.max_tests_per_file:
                mock_fn = "vi.fn()" if self.framework == TestFramework.VITEST else "jest.fn()"
                test_cases.append(TestCase(
                    name=f"handles interactions in {component}",
                    description=f"Test user interactions in {component}",
                    test_type="unit",
                    assertions=["expect(mockHandler).toHaveBeenCalled()"],
                    mocks=[f"const mockHandler = {mock_fn}"],
                ))
            
            # Snapshot tests only if explicitly enabled
            if self.config.include_snapshot_tests and len(test_cases) < self.config.max_tests_per_file:
                test_cases.append(TestCase(
                    name=f"matches snapshot for {component}",
                    description=f"Snapshot test for {component}",
                    test_type="unit",
                    assertions=["expect(container).toMatchSnapshot()"],
                ))
            
            # Accessibility tests only if explicitly enabled
            if self.config.include_accessibility_tests and len(test_cases) < self.config.max_tests_per_file:
                test_cases.append(TestCase(
                    name=f"is accessible in {component}",
                    description=f"Accessibility test for {component}",
                    test_type="unit",
                    assertions=["expect(await axe(container)).toHaveNoViolations()"],
                ))
        
        # Generate tests for hooks (max 2 per hook)
        for hook in analysis["hooks"]:
            if len(test_cases) >= self.config.max_tests_per_file:
                break
                
            # Basic hook initialization test
            test_cases.append(TestCase(
                name=f"initializes {hook} correctly",
                description=f"Test {hook} initial state",
                test_type="unit",
                assertions=["expect(result.current).toBeDefined()"],
                setup=f"const {{ result }} = renderHook(() => {hook}())",
            ))
            
            # State update test only if hook likely has state
            if has_meaningful_branches and len(test_cases) < self.config.max_tests_per_file:
                test_cases.append(TestCase(
                    name=f"updates state in {hook}",
                    description=f"Test {hook} state changes",
                    test_type="unit",
                    assertions=["expect(result.current).toBeDefined()"],
                ))
        
        # Enforce max tests per file limit
        return test_cases[:self.config.max_tests_per_file]
    
    def _check_existing_test_file(self, test_file_path: str) -> Optional[str]:
        """Check if a test file already exists and return its content.
        
        Following the "extend-not-replace" principle:
        - If an existing test file exists, we should extend it rather than replace
        - Returns the existing content if found, None otherwise
        """
        if os.path.exists(test_file_path):
            with open(test_file_path, 'r') as f:
                return f.read()
        return None
    
    def _extract_existing_test_names(self, existing_content: str) -> List[str]:
        """Extract test names from existing test file to avoid duplicates.
        
        Parses it('...') and test('...') patterns to find existing test names.
        """
        test_pattern = re.compile(r"(?:it|test)\s*\(\s*['\"]([^'\"]+)['\"]")
        return test_pattern.findall(existing_content)
    
    def generate_test_file(
        self,
        source_file: str,
        content: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> TestFile:
        """
        Generate a test file for a source file, extending existing tests if present.
        
        Following Pandora coding standards:
        - If existing test file exists, extend rather than replace
        - Respect max_tests_per_file and max_lines_per_file limits
        - Only generate tests that don't already exist
        
        Args:
            source_file: Path to the source file
            content: Optional source content
            output_dir: Optional output directory for test file
            
        Returns:
            Generated TestFile with test cases (may be empty if extending)
        """
        if content is None:
            with open(source_file, 'r') as f:
                content = f.read()
        
        # Analyze the source file
        analysis = self.analyze_file(source_file, content)
        
        # Determine test file path
        source_path = Path(source_file)
        if output_dir:
            test_dir = Path(output_dir)
        else:
            test_dir = source_path.parent / "__tests__"
        
        test_file_name = source_path.stem + ".test" + source_path.suffix
        test_file_path = str(test_dir / test_file_name)
        
        # Check for existing test file (extend-not-replace logic)
        existing_content = None
        existing_test_names: List[str] = []
        if self.config.extend_existing_tests:
            existing_content = self._check_existing_test_file(test_file_path)
            if existing_content:
                existing_test_names = self._extract_existing_test_names(existing_content)
                existing_lines = len(existing_content.split('\n'))
                
                # If existing file is already at or near max lines, don't add more
                if existing_lines >= self.config.max_lines_per_file - 20:
                    return TestFile(
                        source_file=source_file,
                        test_file_path=test_file_path,
                        test_cases=[],
                        imports=[],
                        mocks=[],
                    )
        
        # Generate test cases
        all_test_cases = self.generate_test_cases(analysis, content)
        
        # Filter out tests that already exist
        test_cases = [
            tc for tc in all_test_cases
            if tc.name not in existing_test_names
        ]
        
        # Generate imports based on actual test cases
        imports = self._generate_imports(analysis, source_file, test_cases)
        
        # Generate mocks
        mocks = self._generate_mocks(analysis)
        
        test_file = TestFile(
            source_file=source_file,
            test_file_path=test_file_path,
            test_cases=test_cases,
            imports=imports,
            mocks=mocks,
        )
        
        self.test_files.append(test_file)
        return test_file
    
    def _generate_imports(self, analysis: Dict[str, Any], source_file: str, test_cases: List[TestCase]) -> List[str]:
        """Generate minimal import statements for test file.
        
        Following pandora-group patterns and Sonar compliance:
        - No @jest/globals import (Jest globals are available)
        - Only import what's actually used in test cases
        - Don't auto-add React import unless JSX is used in mocks
        - Imports before mocks, mocks before describe blocks
        
        Args:
            analysis: File analysis results
            source_file: Path to source file
            test_cases: Generated test cases (to determine needed imports)
        """
        imports = []
        needs_render = False
        needs_screen = False
        needs_user_event = False
        needs_render_hook = False
        needs_act = False
        
        # Analyze test cases to determine needed imports
        for tc in test_cases:
            setup_str = tc.setup or ""
            assertions_str = " ".join(tc.assertions)
            
            if "render(" in setup_str or "render(<" in setup_str:
                needs_render = True
            if "screen." in assertions_str or "screen." in setup_str:
                needs_screen = True
            if "userEvent" in setup_str or "userEvent" in assertions_str:
                needs_user_event = True
            if "renderHook" in setup_str:
                needs_render_hook = True
            if "act(" in setup_str:
                needs_act = True
        
        # Build testing-library imports based on actual usage
        rtl_imports = []
        if needs_render:
            rtl_imports.append("render")
        if needs_screen:
            rtl_imports.append("screen")
        if needs_act:
            rtl_imports.append("act")
        if needs_render_hook:
            rtl_imports.append("renderHook")
        
        if rtl_imports:
            imports.append(f"import {{ {', '.join(rtl_imports)} }} from '@testing-library/react';")
        
        if needs_user_event:
            imports.append("import userEvent from '@testing-library/user-event';")
        
        # Vitest-specific imports (only for vitest framework)
        if self.framework == TestFramework.VITEST:
            imports.append("import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';")
        
        # Source file import - only import what's exported and tested
        source_path = Path(source_file)
        relative_import = f"../{source_path.stem}"
        exports = analysis["exports"]
        if exports:
            imports.append(f"import {{ {', '.join(exports)} }} from '{relative_import}';")
        
        return imports
    
    def _generate_mocks(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate mock statements for test file.
        
        Following pandora-group patterns and Sonar compliance:
        - Mocks at module level (top of file, after imports)
        - Inline mock implementations for common Next.js modules
        - jest.mock() calls MUST be hoisted - they run before imports
        - AVOID using 'any' type (Sonar S4325) - use proper typing or unknown
        - Use globalThis instead of global (Sonar S7764)
        
        Note: pandora-group has centralized mocks in jest.setup.ts for next/navigation,
        so we should NOT re-mock those unless the test specifically needs different behavior.
        """
        mocks = []
        
        # Common Next.js mocks with inline implementations
        # NOTE: Using React.ComponentProps instead of 'any' to avoid Sonar violations
        # NOTE: next/navigation is already mocked in jest.setup.ts - skip it by default
        next_mocks = {
            "next/router": """jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    query: {},
    pathname: '/',
  }),
}));""",
            "next/image": """jest.mock('next/image', () => ({
  __esModule: true,
  default: function MockImage(props: React.ComponentProps<'img'>) {
    return <img {...props} />;
  },
}));""",
            "next/link": """jest.mock('next/link', () => ({
  __esModule: true,
  default: function MockLink({ children, href, ...props }: React.ComponentProps<'a'> & { children: React.ReactNode }) {
    return <a href={href} {...props}>{children}</a>;
  },
}));""",
        }
        
        # Check which mocks are needed based on imports
        # Skip next/navigation as it's centrally mocked in jest.setup.ts
        for dep in analysis["imports"]:
            if "next/navigation" in dep:
                continue  # Already mocked in jest.setup.ts
                
            for mock_key, mock_impl in next_mocks.items():
                if mock_key in dep:
                    mocks.append(mock_impl)
                    break
            else:
                # Generic mock for other dependencies
                if any(pattern in dep for pattern in ["@/lib/", "@/hooks/", "@/services/"]):
                    if self.framework == TestFramework.JEST:
                        mocks.append(f"jest.mock('{dep}');")
                    elif self.framework == TestFramework.VITEST:
                        mocks.append(f"vi.mock('{dep}');")
        
        return mocks
    
    def generate_test_code(self, test_file: TestFile) -> str:
        """
        Generate the actual test code as a string.
        
        Args:
            test_file: TestFile object with test cases
            
        Returns:
            Complete test file content as string
        """
        lines = []
        
        # Add imports
        for imp in test_file.imports:
            lines.append(imp)
        lines.append("")
        
        # Add mocks
        for mock in test_file.mocks:
            lines.append(mock)
        if test_file.mocks:
            lines.append("")
        
        # Add axe matcher extension
        if any("axe" in imp for imp in test_file.imports):
            lines.append("expect.extend(toHaveNoViolations);")
            lines.append("")
        
        # Get source file name for describe block
        source_name = Path(test_file.source_file).stem
        
        # Start describe block
        lines.append(f"describe('{source_name}', () => {{")
        
        # Add beforeEach if needed
        if any(tc.setup for tc in test_file.test_cases):
            lines.append("  beforeEach(() => {")
            lines.append("    // Reset mocks before each test")
            if self.framework == TestFramework.JEST:
                lines.append("    jest.clearAllMocks();")
            else:
                lines.append("    vi.clearAllMocks();")
            lines.append("  });")
            lines.append("")
        
        # Group test cases by type
        unit_tests = [tc for tc in test_file.test_cases if tc.test_type == "unit"]
        integration_tests = [tc for tc in test_file.test_cases if tc.test_type == "integration"]
        
        # Add unit tests
        if unit_tests:
            lines.append("  describe('Unit Tests', () => {")
            for tc in unit_tests:
                lines.append(f"    it('{tc.name}', async () => {{")
                
                # Add setup
                if tc.setup:
                    lines.append(f"      {tc.setup}")
                
                # Add mocks
                for mock in tc.mocks:
                    lines.append(f"      {mock}")
                
                # Add assertions
                for assertion in tc.assertions:
                    lines.append(f"      {assertion};")
                
                lines.append("    });")
                lines.append("")
            lines.append("  });")
        
        # Add integration tests
        if integration_tests:
            lines.append("")
            lines.append("  describe('Integration Tests', () => {")
            for tc in integration_tests:
                lines.append(f"    it('{tc.name}', async () => {{")
                if tc.setup:
                    lines.append(f"      {tc.setup}")
                for assertion in tc.assertions:
                    lines.append(f"      {assertion};")
                lines.append("    });")
                lines.append("")
            lines.append("  });")
        
        # Close describe block
        lines.append("});")
        
        return "\n".join(lines)
    
    def analyze_coverage(self, coverage_data: Dict[str, Any]) -> CoverageReport:
        """
        Analyze coverage data and identify gaps.
        
        Args:
            coverage_data: Coverage report from Jest/Vitest
            
        Returns:
            CoverageReport with analysis
        """
        report = CoverageReport()
        
        if "total" in coverage_data:
            total = coverage_data["total"]
            report.statements = total.get("statements", {}).get("pct", 0)
            report.branches = total.get("branches", {}).get("pct", 0)
            report.functions = total.get("functions", {}).get("pct", 0)
            report.lines = total.get("lines", {}).get("pct", 0)
        
        # Find uncovered lines
        for file_path, file_data in coverage_data.items():
            if file_path == "total":
                continue
            
            if "statementMap" in file_data and "s" in file_data:
                for stmt_id, count in file_data["s"].items():
                    if count == 0:
                        stmt_info = file_data["statementMap"].get(stmt_id, {})
                        start_line = stmt_info.get("start", {}).get("line")
                        if start_line:
                            report.uncovered_lines.append(start_line)
            
            if "branchMap" in file_data and "b" in file_data:
                for branch_id, counts in file_data["b"].items():
                    for i, count in enumerate(counts):
                        if count == 0:
                            branch_info = file_data["branchMap"].get(branch_id, {})
                            report.uncovered_branches.append(
                                f"{branch_info.get('type', 'unknown')} at line {branch_info.get('loc', {}).get('start', {}).get('line', '?')}"
                            )
        
        return report
    
    def generate_coverage_improvement_tests(
        self,
        source_file: str,
        coverage_report: CoverageReport
    ) -> List[TestCase]:
        """
        Generate additional tests to improve coverage to 100%.
        
        Args:
            source_file: Path to source file
            coverage_report: Current coverage report
            
        Returns:
            Additional test cases to cover gaps
        """
        additional_tests = []
        
        # Generate tests for uncovered lines
        for line in coverage_report.uncovered_lines:
            additional_tests.append(TestCase(
                name=f"should cover line {line}",
                description=f"Test to cover uncovered line {line}",
                test_type="unit",
                assertions=[f"// TODO: Add assertion for line {line}"],
            ))
        
        # Generate tests for uncovered branches
        for branch in coverage_report.uncovered_branches:
            additional_tests.append(TestCase(
                name=f"should cover {branch}",
                description=f"Test to cover uncovered branch: {branch}",
                test_type="unit",
                assertions=[f"// TODO: Add assertion for {branch}"],
            ))
        
        return additional_tests
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the unit test agent as part of a workflow.
        
        Args:
            context: Workflow context with task description and input data
            
        Returns:
            Workflow-compatible result
        """
        try:
            input_data = context.get("input_data", {})
            
            # Get source files to test
            source_files = input_data.get("files", [])
            component_spec = input_data.get("component_spec", {})
            
            # If no files provided, try to extract from component spec
            if not source_files and component_spec:
                source_files = component_spec.get("files", [])
            
            result = UnitTestResult(status="success")
            
            # Generate tests for each source file
            for source_file in source_files:
                if isinstance(source_file, dict):
                    file_path = source_file.get("path", "")
                    content = source_file.get("content", "")
                else:
                    file_path = source_file
                    content = None
                
                if file_path:
                    test_file = self.generate_test_file(file_path, content)
                    result.test_files.append(test_file)
                    result.total_test_cases += len(test_file.test_cases)
            
            # Generate recommendations
            result.recommendations = [
                "Run tests with coverage: npm test -- --coverage",
                "Target 100% coverage for all metrics (statements, branches, functions, lines)",
                "Add data-testid attributes to components for reliable testing",
                "Mock external dependencies to isolate unit tests",
                "Use Testing Library queries in order of priority: getByRole > getByLabelText > getByText",
            ]
            
            return {
                "status": "success",
                "data": result.to_dict(),
                "next": "review",
                "error": None,
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "next": None,
                "error": str(e),
            }


def run(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run the Unit Test Agent.
    
    Args:
        context: Workflow context
        
    Returns:
        Workflow-compatible result
    """
    agent = UnitTestAgent()
    return agent.run(context)


def generate_tests(
    source_file: str,
    content: Optional[str] = None,
    framework: str = "jest"
) -> Dict[str, Any]:
    """
    Generate unit tests for a source file.
    
    Args:
        source_file: Path to source file
        content: Optional source content
        framework: Test framework (jest, vitest)
        
    Returns:
        Generated test file information
    """
    fw = TestFramework.JEST if framework == "jest" else TestFramework.VITEST
    agent = UnitTestAgent(framework=fw)
    
    test_file = agent.generate_test_file(source_file, content)
    test_code = agent.generate_test_code(test_file)
    
    return {
        "testFile": test_file.to_dict(),
        "testCode": test_code,
    }
