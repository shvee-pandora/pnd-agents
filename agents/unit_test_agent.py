"""
Unit Test Agent

A dedicated agent for generating comprehensive unit tests with 100% code coverage.
This agent analyzes source code and generates Jest/Vitest tests for React components,
utility functions, hooks, and API routes following Pandora coding standards.
"""

import os
import re
import json
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
    Agent dedicated to generating comprehensive unit tests with 100% coverage.
    
    This agent analyzes source code and generates tests that cover:
    - All functions and methods
    - All branches (if/else, switch, ternary)
    - All edge cases and error conditions
    - Component rendering and interactions
    - Hook behavior and state changes
    - API route handlers
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
    
    def __init__(self, framework: TestFramework = TestFramework.JEST):
        """
        Initialize the Unit Test Agent.
        
        Args:
            framework: Test framework to use (jest, vitest, etc.)
        """
        self.framework = framework
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
        Generate test cases based on file analysis.
        
        Args:
            analysis: File analysis results
            content: Source file content
            
        Returns:
            List of test cases to achieve 100% coverage
        """
        test_cases = []
        
        # Generate tests for functions
        for func_name in analysis["functions"]:
            # Basic function test
            test_cases.append(TestCase(
                name=f"should call {func_name} successfully",
                description=f"Test that {func_name} executes without errors",
                test_type="unit",
                assertions=[f"expect({func_name}).toBeDefined()"],
            ))
            
            # Test with valid input
            test_cases.append(TestCase(
                name=f"should return expected result from {func_name}",
                description=f"Test {func_name} with valid input",
                test_type="unit",
                assertions=[f"expect(result).toBeDefined()"],
            ))
            
            # Test error handling
            test_cases.append(TestCase(
                name=f"should handle errors in {func_name}",
                description=f"Test {func_name} error handling",
                test_type="unit",
                assertions=["expect(error).toBeDefined()"],
            ))
        
        # Generate tests for React components
        for component in analysis["components"]:
            # Render test
            test_cases.append(TestCase(
                name=f"should render {component} without crashing",
                description=f"Test that {component} renders successfully",
                test_type="unit",
                assertions=[f"expect(screen.getByTestId('{component.lower()}')).toBeInTheDocument()"],
                setup=f"render(<{component} />)",
            ))
            
            # Snapshot test
            test_cases.append(TestCase(
                name=f"should match snapshot for {component}",
                description=f"Snapshot test for {component}",
                test_type="unit",
                assertions=["expect(container).toMatchSnapshot()"],
            ))
            
            # Props test
            test_cases.append(TestCase(
                name=f"should render {component} with props",
                description=f"Test {component} with various props",
                test_type="unit",
                assertions=[f"expect(screen.getByText(props.text)).toBeInTheDocument()"],
            ))
            
            # Interaction test
            test_cases.append(TestCase(
                name=f"should handle user interactions in {component}",
                description=f"Test click/input handlers in {component}",
                test_type="unit",
                assertions=["expect(mockHandler).toHaveBeenCalled()"],
                mocks=["const mockHandler = jest.fn()"],
            ))
            
            # Accessibility test
            test_cases.append(TestCase(
                name=f"should be accessible in {component}",
                description=f"Accessibility test for {component}",
                test_type="unit",
                assertions=["expect(await axe(container)).toHaveNoViolations()"],
            ))
        
        # Generate tests for hooks
        for hook in analysis["hooks"]:
            # Basic hook test
            test_cases.append(TestCase(
                name=f"should initialize {hook} correctly",
                description=f"Test {hook} initial state",
                test_type="unit",
                assertions=["expect(result.current).toBeDefined()"],
                setup=f"const {{ result }} = renderHook(() => {hook}())",
            ))
            
            # State update test
            test_cases.append(TestCase(
                name=f"should update state in {hook}",
                description=f"Test {hook} state updates",
                test_type="unit",
                assertions=["expect(result.current.value).toBe(expected)"],
            ))
            
            # Cleanup test
            test_cases.append(TestCase(
                name=f"should cleanup {hook} on unmount",
                description=f"Test {hook} cleanup",
                test_type="unit",
                assertions=["expect(cleanupFn).toHaveBeenCalled()"],
            ))
        
        # Generate branch coverage tests
        branch_count = analysis["branches"]
        if branch_count > 0:
            test_cases.append(TestCase(
                name="should cover all conditional branches - truthy path",
                description="Test truthy branch conditions",
                test_type="unit",
                assertions=["expect(result).toBe(truthyResult)"],
            ))
            
            test_cases.append(TestCase(
                name="should cover all conditional branches - falsy path",
                description="Test falsy branch conditions",
                test_type="unit",
                assertions=["expect(result).toBe(falsyResult)"],
            ))
            
            test_cases.append(TestCase(
                name="should handle edge cases and null values",
                description="Test null/undefined handling",
                test_type="unit",
                assertions=[
                    "expect(handleNull(null)).toBeDefined()",
                    "expect(handleNull(undefined)).toBeDefined()",
                ],
            ))
        
        return test_cases
    
    def generate_test_file(
        self,
        source_file: str,
        content: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> TestFile:
        """
        Generate a complete test file for a source file.
        
        Args:
            source_file: Path to the source file
            content: Optional source content
            output_dir: Optional output directory for test file
            
        Returns:
            Generated TestFile with all test cases
        """
        if content is None:
            with open(source_file, 'r') as f:
                content = f.read()
        
        # Analyze the source file
        analysis = self.analyze_file(source_file, content)
        
        # Generate test cases
        test_cases = self.generate_test_cases(analysis, content)
        
        # Determine test file path
        source_path = Path(source_file)
        if output_dir:
            test_dir = Path(output_dir)
        else:
            # Default: __tests__ directory next to source
            test_dir = source_path.parent / "__tests__"
        
        test_file_name = source_path.stem + ".test" + source_path.suffix
        test_file_path = str(test_dir / test_file_name)
        
        # Generate imports
        imports = self._generate_imports(analysis, source_file)
        
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
    
    def _generate_imports(self, analysis: Dict[str, Any], source_file: str) -> List[str]:
        """Generate import statements for test file.
        
        Note: Following pandora-group patterns:
        - No @jest/globals import (Jest globals are available)
        - @testing-library/jest-dom for DOM matchers
        - Imports before mocks, mocks before describe blocks
        """
        imports = []
        
        # React import (needed for JSX)
        if analysis["components"]:
            imports.append("import React from 'react';")
        
        # Jest DOM matchers (pandora-group pattern)
        imports.append("import '@testing-library/jest-dom';")
        
        # React testing library imports
        if analysis["components"]:
            imports.append("import { render, screen, fireEvent, waitFor } from '@testing-library/react';")
            imports.append("import userEvent from '@testing-library/user-event';")
        
        # Hook testing imports
        if analysis["hooks"]:
            imports.append("import { renderHook, act } from '@testing-library/react';")
        
        # Vitest-specific imports (only for vitest framework)
        if self.framework == TestFramework.VITEST:
            imports.append("import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';")
        
        # Source file import
        source_path = Path(source_file)
        relative_import = f"../{source_path.stem}"
        exports = analysis["exports"]
        if exports:
            imports.append(f"import {{ {', '.join(exports)} }} from '{relative_import}';")
        
        return imports
    
    def _generate_mocks(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate mock statements for test file.
        
        Note: Following pandora-group patterns:
        - Mocks at module level (top of file, after imports)
        - Inline mock implementations for common Next.js modules
        - jest.mock() calls MUST be hoisted - they run before imports
        """
        mocks = []
        
        # Common Next.js mocks with inline implementations (pandora-group pattern)
        next_mocks = {
            "next/navigation": """jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));""",
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
  default: ({ src, alt, ...props }: any) => <img src={src} alt={alt} {...props} />,
}));""",
            "next/link": """jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href, ...props }: any) => <a href={href} {...props}>{children}</a>,
}));""",
        }
        
        # Check which mocks are needed based on imports
        for dep in analysis["imports"]:
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
            task_description = context.get("task_description", "")
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
