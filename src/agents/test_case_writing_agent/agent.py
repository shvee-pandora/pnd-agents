"""
Test Case Writing Agent

A dedicated agent for generating comprehensive test cases from requirements,
user stories, acceptance criteria, or code analysis. This agent creates
structured test cases that can be used by QA teams or automated testing.

Key principles:
- Generate test cases from requirements, user stories, or code
- Cover positive, negative, edge cases, and boundary conditions
- Follow BDD/Gherkin style when appropriate
- Produce actionable, clear test cases
- Consider accessibility and security testing scenarios
"""

import re
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TestCaseType(Enum):
    """Types of test cases."""
    FUNCTIONAL = "functional"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    BOUNDARY = "boundary"
    INTEGRATION = "integration"
    ACCESSIBILITY = "accessibility"
    SECURITY = "security"
    PERFORMANCE = "performance"


class TestCasePriority(Enum):
    """Priority levels for test cases."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestCaseFormat(Enum):
    """Output formats for test cases."""
    STRUCTURED = "structured"
    GHERKIN = "gherkin"
    MARKDOWN = "markdown"


@dataclass
class TestStep:
    """Represents a single step in a test case."""
    step_number: int
    action: str
    expected_result: str
    test_data: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stepNumber": self.step_number,
            "action": self.action,
            "expectedResult": self.expected_result,
            "testData": self.test_data,
        }

    def to_gherkin(self) -> str:
        """Convert step to Gherkin format."""
        if self.step_number == 1:
            keyword = "Given"
        elif "click" in self.action.lower() or "enter" in self.action.lower():
            keyword = "When"
        else:
            keyword = "Then"
        return f"  {keyword} {self.action}"


@dataclass
class TestCase:
    """Represents a complete test case."""
    id: str
    title: str
    description: str
    test_type: TestCaseType
    priority: TestCasePriority
    preconditions: List[str] = field(default_factory=list)
    steps: List[TestStep] = field(default_factory=list)
    expected_result: str = ""
    tags: List[str] = field(default_factory=list)
    related_requirement: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "testType": self.test_type.value,
            "priority": self.priority.value,
            "preconditions": self.preconditions,
            "steps": [step.to_dict() for step in self.steps],
            "expectedResult": self.expected_result,
            "tags": self.tags,
            "relatedRequirement": self.related_requirement,
        }

    def to_gherkin(self) -> str:
        """Convert test case to Gherkin format."""
        lines = [
            f"@{self.test_type.value} @{self.priority.value}",
            f"Scenario: {self.title}",
        ]

        # Add preconditions as Given steps
        for precondition in self.preconditions:
            lines.append(f"  Given {precondition}")

        # Add test steps
        for step in self.steps:
            lines.append(step.to_gherkin())

        # Add expected result as final Then
        if self.expected_result:
            lines.append(f"  Then {self.expected_result}")

        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Convert test case to Markdown format."""
        lines = [
            f"### {self.id}: {self.title}",
            "",
            f"**Priority:** {self.priority.value}",
            f"**Type:** {self.test_type.value}",
            "",
            f"**Description:** {self.description}",
            "",
        ]

        if self.preconditions:
            lines.append("**Preconditions:**")
            for pre in self.preconditions:
                lines.append(f"- {pre}")
            lines.append("")

        lines.append("**Steps:**")
        for step in self.steps:
            lines.append(f"{step.step_number}. {step.action}")
            lines.append(f"   - Expected: {step.expected_result}")
        lines.append("")

        if self.expected_result:
            lines.append(f"**Expected Result:** {self.expected_result}")
            lines.append("")

        if self.tags:
            lines.append(f"**Tags:** {', '.join(self.tags)}")

        return "\n".join(lines)


@dataclass
class TestSuite:
    """Represents a collection of related test cases."""
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    coverage_areas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "testCases": [tc.to_dict() for tc in self.test_cases],
            "coverageAreas": self.coverage_areas,
            "summary": {
                "totalTestCases": len(self.test_cases),
                "byType": self._count_by_type(),
                "byPriority": self._count_by_priority(),
            }
        }

    def _count_by_type(self) -> Dict[str, int]:
        counts = {}
        for tc in self.test_cases:
            type_name = tc.test_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def _count_by_priority(self) -> Dict[str, int]:
        counts = {}
        for tc in self.test_cases:
            priority_name = tc.priority.value
            counts[priority_name] = counts.get(priority_name, 0) + 1
        return counts


@dataclass
class TestCaseWritingResult:
    """Result from test case generation."""
    status: str
    test_suites: List[TestSuite] = field(default_factory=list)
    total_test_cases: int = 0
    coverage_summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "testSuites": [ts.to_dict() for ts in self.test_suites],
            "totalTestCases": self.total_test_cases,
            "coverageSummary": self.coverage_summary,
            "recommendations": self.recommendations,
            "error": self.error,
        }


class TestCaseWritingAgent:
    """
    Agent for generating comprehensive test cases from requirements,
    user stories, acceptance criteria, or code analysis.

    Key capabilities:
    - Parse requirements and user stories to extract testable conditions
    - Generate positive, negative, and edge case scenarios
    - Create structured test cases with clear steps and expected results
    - Support multiple output formats (structured, Gherkin, Markdown)
    - Consider accessibility and security testing scenarios
    """

    # Patterns for extracting testable requirements
    REQUIREMENT_PATTERNS = [
        re.compile(r"(?:should|must|shall)\s+(.+?)(?:\.|$)", re.IGNORECASE),
        re.compile(r"(?:user\s+)?(?:can|is able to)\s+(.+?)(?:\.|$)", re.IGNORECASE),
        re.compile(r"(?:when|if)\s+(.+?),?\s+(?:then|should)\s+(.+?)(?:\.|$)", re.IGNORECASE),
        re.compile(r"(?:given)\s+(.+?),?\s+(?:when)\s+(.+?),?\s+(?:then)\s+(.+?)(?:\.|$)", re.IGNORECASE),
    ]

    # Common edge cases to consider
    EDGE_CASE_SCENARIOS = [
        "empty input",
        "null/undefined values",
        "maximum length input",
        "minimum length input",
        "special characters",
        "unicode characters",
        "whitespace only",
        "very long strings",
        "negative numbers",
        "zero values",
        "boundary values",
        "concurrent operations",
    ]

    # Security test scenarios
    SECURITY_SCENARIOS = [
        "SQL injection attempts",
        "XSS attack vectors",
        "CSRF token validation",
        "authentication bypass",
        "authorization checks",
        "input sanitization",
        "sensitive data exposure",
        "session management",
    ]

    # Accessibility test scenarios
    ACCESSIBILITY_SCENARIOS = [
        "keyboard navigation",
        "screen reader compatibility",
        "color contrast",
        "focus indicators",
        "alt text for images",
        "form labels",
        "error announcements",
        "skip navigation links",
    ]

    def __init__(
        self,
        output_format: TestCaseFormat = TestCaseFormat.STRUCTURED,
        include_edge_cases: bool = True,
        include_security: bool = False,
        include_accessibility: bool = False,
    ):
        """
        Initialize the Test Case Writing Agent.

        Args:
            output_format: Format for test case output
            include_edge_cases: Whether to include edge case test scenarios
            include_security: Whether to include security test scenarios
            include_accessibility: Whether to include accessibility test scenarios
        """
        self.output_format = output_format
        self.include_edge_cases = include_edge_cases
        self.include_security = include_security
        self.include_accessibility = include_accessibility
        self._test_case_counter = 0

    def _generate_test_id(self, prefix: str = "TC") -> str:
        """Generate a unique test case ID."""
        self._test_case_counter += 1
        return f"{prefix}-{self._test_case_counter:04d}"

    def extract_requirements(self, text: str) -> List[Dict[str, str]]:
        """
        Extract testable requirements from text.

        Args:
            text: Text containing requirements or user stories

        Returns:
            List of extracted requirements with their context
        """
        requirements = []

        for pattern in self.REQUIREMENT_PATTERNS:
            for match in pattern.finditer(text):
                groups = match.groups()
                if len(groups) == 1:
                    requirements.append({
                        "type": "simple",
                        "condition": groups[0].strip(),
                        "context": match.group(0),
                    })
                elif len(groups) == 2:
                    requirements.append({
                        "type": "conditional",
                        "when": groups[0].strip(),
                        "then": groups[1].strip(),
                        "context": match.group(0),
                    })
                elif len(groups) == 3:
                    requirements.append({
                        "type": "gherkin",
                        "given": groups[0].strip(),
                        "when": groups[1].strip(),
                        "then": groups[2].strip(),
                        "context": match.group(0),
                    })

        return requirements

    def generate_functional_test_cases(
        self,
        requirements: List[Dict[str, str]],
        feature_name: str,
    ) -> List[TestCase]:
        """
        Generate functional test cases from requirements.

        Args:
            requirements: List of extracted requirements
            feature_name: Name of the feature being tested

        Returns:
            List of functional test cases
        """
        test_cases = []

        for req in requirements:
            # Positive test case
            if req["type"] == "simple":
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Verify {req['condition']}",
                    description=f"Validate that the system {req['condition']}",
                    test_type=TestCaseType.FUNCTIONAL,
                    priority=TestCasePriority.HIGH,
                    preconditions=[f"User is on the {feature_name} page"],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=f"Perform action to trigger: {req['condition']}",
                            expected_result="Action is performed successfully",
                        ),
                        TestStep(
                            step_number=2,
                            action="Verify the expected behavior",
                            expected_result=req['condition'],
                        ),
                    ],
                    expected_result=f"System {req['condition']}",
                    tags=["functional", feature_name.lower().replace(" ", "-")],
                    related_requirement=req["context"],
                )
                test_cases.append(test_case)

            elif req["type"] == "conditional":
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Verify when {req['when'][:50]}...",
                    description=f"Validate conditional behavior: {req['context']}",
                    test_type=TestCaseType.FUNCTIONAL,
                    priority=TestCasePriority.HIGH,
                    preconditions=[f"User is on the {feature_name} page"],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=f"Set up condition: {req['when']}",
                            expected_result="Condition is set up correctly",
                        ),
                        TestStep(
                            step_number=2,
                            action="Trigger the action",
                            expected_result=req['then'],
                        ),
                    ],
                    expected_result=req['then'],
                    tags=["functional", "conditional", feature_name.lower().replace(" ", "-")],
                    related_requirement=req["context"],
                )
                test_cases.append(test_case)

            elif req["type"] == "gherkin":
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Verify {req['then'][:50]}...",
                    description=f"BDD scenario: {req['context']}",
                    test_type=TestCaseType.FUNCTIONAL,
                    priority=TestCasePriority.HIGH,
                    preconditions=[req['given']],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=req['when'],
                            expected_result="Action is performed",
                        ),
                        TestStep(
                            step_number=2,
                            action="Verify outcome",
                            expected_result=req['then'],
                        ),
                    ],
                    expected_result=req['then'],
                    tags=["functional", "bdd", feature_name.lower().replace(" ", "-")],
                    related_requirement=req["context"],
                )
                test_cases.append(test_case)

        return test_cases

    def generate_negative_test_cases(
        self,
        requirements: List[Dict[str, str]],
        feature_name: str,
    ) -> List[TestCase]:
        """
        Generate negative test cases (testing what should NOT happen).

        Args:
            requirements: List of extracted requirements
            feature_name: Name of the feature being tested

        Returns:
            List of negative test cases
        """
        test_cases = []

        for req in requirements:
            condition = req.get("condition") or req.get("then", "")
            if not condition:
                continue

            # Create negative test case
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Verify system handles invalid input for {condition[:30]}...",
                description=f"Validate error handling when requirement cannot be met",
                test_type=TestCaseType.NEGATIVE,
                priority=TestCasePriority.MEDIUM,
                preconditions=[f"User is on the {feature_name} page"],
                steps=[
                    TestStep(
                        step_number=1,
                        action="Provide invalid or missing input",
                        expected_result="System accepts input for validation",
                    ),
                    TestStep(
                        step_number=2,
                        action="Attempt to complete the action",
                        expected_result="System displays appropriate error message",
                    ),
                    TestStep(
                        step_number=3,
                        action="Verify system state remains consistent",
                        expected_result="No data corruption or unintended changes",
                    ),
                ],
                expected_result="System gracefully handles invalid input with clear error message",
                tags=["negative", "error-handling", feature_name.lower().replace(" ", "-")],
                related_requirement=req.get("context"),
            )
            test_cases.append(test_case)

        return test_cases

    def generate_edge_case_tests(self, feature_name: str) -> List[TestCase]:
        """
        Generate edge case test scenarios.

        Args:
            feature_name: Name of the feature being tested

        Returns:
            List of edge case test cases
        """
        test_cases = []

        for scenario in self.EDGE_CASE_SCENARIOS:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Handle {scenario} in {feature_name}",
                description=f"Verify system handles {scenario} correctly",
                test_type=TestCaseType.EDGE_CASE,
                priority=TestCasePriority.MEDIUM,
                preconditions=[f"User is on the {feature_name} page"],
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Provide {scenario} as input",
                        expected_result="System accepts input",
                    ),
                    TestStep(
                        step_number=2,
                        action="Submit or process the input",
                        expected_result="System handles edge case appropriately",
                    ),
                ],
                expected_result=f"System handles {scenario} without errors or crashes",
                tags=["edge-case", scenario.replace(" ", "-").replace("/", "-")],
            )
            test_cases.append(test_case)

        return test_cases

    def generate_accessibility_tests(self, feature_name: str) -> List[TestCase]:
        """
        Generate accessibility test scenarios.

        Args:
            feature_name: Name of the feature being tested

        Returns:
            List of accessibility test cases
        """
        test_cases = []

        for scenario in self.ACCESSIBILITY_SCENARIOS:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Verify {scenario} for {feature_name}",
                description=f"Accessibility test: {scenario}",
                test_type=TestCaseType.ACCESSIBILITY,
                priority=TestCasePriority.HIGH,
                preconditions=[
                    f"User is on the {feature_name} page",
                    "Accessibility testing tools are available",
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Test {scenario}",
                        expected_result=f"{scenario.capitalize()} works correctly",
                    ),
                    TestStep(
                        step_number=2,
                        action="Verify WCAG 2.1 AA compliance",
                        expected_result="No accessibility violations",
                    ),
                ],
                expected_result=f"Feature passes {scenario} accessibility check",
                tags=["accessibility", "a11y", scenario.replace(" ", "-")],
            )
            test_cases.append(test_case)

        return test_cases

    def generate_security_tests(self, feature_name: str) -> List[TestCase]:
        """
        Generate security test scenarios.

        Args:
            feature_name: Name of the feature being tested

        Returns:
            List of security test cases
        """
        test_cases = []

        for scenario in self.SECURITY_SCENARIOS:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Verify protection against {scenario}",
                description=f"Security test: {scenario}",
                test_type=TestCaseType.SECURITY,
                priority=TestCasePriority.CRITICAL,
                preconditions=[
                    f"User is on the {feature_name} page",
                    "Security testing tools are available",
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Attempt {scenario}",
                        expected_result="Attack vector is blocked",
                    ),
                    TestStep(
                        step_number=2,
                        action="Verify system remains secure",
                        expected_result="No security breach or data exposure",
                    ),
                    TestStep(
                        step_number=3,
                        action="Check security logs",
                        expected_result="Attempt is logged appropriately",
                    ),
                ],
                expected_result=f"System is protected against {scenario}",
                tags=["security", scenario.replace(" ", "-")],
            )
            test_cases.append(test_case)

        return test_cases

    def generate_test_suite(
        self,
        text: str,
        feature_name: str,
        include_all_types: bool = False,
    ) -> TestSuite:
        """
        Generate a complete test suite from requirements text.

        Args:
            text: Text containing requirements or user stories
            feature_name: Name of the feature being tested
            include_all_types: Override settings to include all test types

        Returns:
            Complete test suite with all applicable test cases
        """
        # Extract requirements
        requirements = self.extract_requirements(text)

        # Generate test cases
        test_cases = []
        coverage_areas = []

        # Functional tests (always included)
        functional_tests = self.generate_functional_test_cases(requirements, feature_name)
        test_cases.extend(functional_tests)
        coverage_areas.append("Functional")

        # Negative tests (always included)
        negative_tests = self.generate_negative_test_cases(requirements, feature_name)
        test_cases.extend(negative_tests)
        coverage_areas.append("Negative/Error Handling")

        # Edge case tests
        if self.include_edge_cases or include_all_types:
            edge_tests = self.generate_edge_case_tests(feature_name)
            test_cases.extend(edge_tests)
            coverage_areas.append("Edge Cases")

        # Accessibility tests
        if self.include_accessibility or include_all_types:
            a11y_tests = self.generate_accessibility_tests(feature_name)
            test_cases.extend(a11y_tests)
            coverage_areas.append("Accessibility")

        # Security tests
        if self.include_security or include_all_types:
            security_tests = self.generate_security_tests(feature_name)
            test_cases.extend(security_tests)
            coverage_areas.append("Security")

        return TestSuite(
            name=f"{feature_name} Test Suite",
            description=f"Comprehensive test suite for {feature_name}",
            test_cases=test_cases,
            coverage_areas=coverage_areas,
        )

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the test case writing agent as part of a workflow.

        Args:
            context: Workflow context with:
                - task_description: Description of what to generate tests for
                - input_data: Dictionary with:
                    - requirements: Text with requirements/user stories
                    - feature_name: Name of the feature
                    - acceptance_criteria: List of acceptance criteria
                    - include_security: Whether to include security tests
                    - include_accessibility: Whether to include a11y tests

        Returns:
            Workflow-compatible result with generated test cases
        """
        logger.info("TestCaseWritingAgent.run called")

        try:
            task_description = context.get("task_description", "")
            input_data = context.get("input_data", {})

            # Extract parameters
            requirements_text = input_data.get("requirements", task_description)
            feature_name = input_data.get("feature_name", self._extract_feature_name(task_description))
            acceptance_criteria = input_data.get("acceptance_criteria", [])

            # Update settings based on input
            if input_data.get("include_security"):
                self.include_security = True
            if input_data.get("include_accessibility"):
                self.include_accessibility = True

            # Add acceptance criteria to requirements
            if acceptance_criteria:
                requirements_text += "\n" + "\n".join(
                    f"The system should {ac}" for ac in acceptance_criteria
                )

            # Generate test suite
            test_suite = self.generate_test_suite(requirements_text, feature_name)

            # Build result
            result = TestCaseWritingResult(
                status="success",
                test_suites=[test_suite],
                total_test_cases=len(test_suite.test_cases),
                coverage_summary={
                    "areas": test_suite.coverage_areas,
                    "byType": test_suite._count_by_type(),
                    "byPriority": test_suite._count_by_priority(),
                },
                recommendations=[
                    "Review generated test cases for completeness",
                    "Add specific test data for each scenario",
                    "Prioritize critical path test cases for automation",
                    "Consider adding performance test cases for critical features",
                    "Update test cases as requirements evolve",
                ],
            )

            return {
                "status": "success",
                "data": result.to_dict(),
                "next": "qa",
                "error": None,
            }

        except Exception as e:
            logger.error(f"TestCaseWritingAgent.run failed: {e}")
            return {
                "status": "error",
                "data": None,
                "next": None,
                "error": str(e),
            }

    def _extract_feature_name(self, text: str) -> str:
        """Extract feature name from task description."""
        # Look for common patterns
        patterns = [
            r"test\s+cases?\s+for\s+(?:the\s+)?(.+?)(?:\.|$)",
            r"tests?\s+for\s+(?:the\s+)?(.+?)(?:\.|$)",
            r"(?:test|validate)\s+(?:the\s+)?(.+?)(?:feature|functionality|component)?(?:\.|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r"\s+", " ", name)
                return name[:50]  # Limit length

        return "Feature"

    def format_output(self, test_suite: TestSuite) -> str:
        """
        Format test suite output based on configured format.

        Args:
            test_suite: Test suite to format

        Returns:
            Formatted string output
        """
        if self.output_format == TestCaseFormat.GHERKIN:
            lines = [f"Feature: {test_suite.name}", "", test_suite.description, ""]
            for tc in test_suite.test_cases:
                lines.append(tc.to_gherkin())
                lines.append("")
            return "\n".join(lines)

        elif self.output_format == TestCaseFormat.MARKDOWN:
            lines = [f"# {test_suite.name}", "", test_suite.description, ""]
            for tc in test_suite.test_cases:
                lines.append(tc.to_markdown())
                lines.append("")
            return "\n".join(lines)

        else:  # STRUCTURED
            import json
            return json.dumps(test_suite.to_dict(), indent=2)


def run(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run the Test Case Writing Agent.

    Args:
        context: Workflow context

    Returns:
        Workflow-compatible result
    """
    agent = TestCaseWritingAgent()
    return agent.run(context)


def generate_test_cases(
    requirements: str,
    feature_name: str = "Feature",
    include_edge_cases: bool = True,
    include_security: bool = False,
    include_accessibility: bool = False,
    output_format: str = "structured",
) -> Dict[str, Any]:
    """
    Generate test cases from requirements.

    Convenience function for independent usage.

    Args:
        requirements: Text containing requirements or user stories
        feature_name: Name of the feature being tested
        include_edge_cases: Whether to include edge case tests
        include_security: Whether to include security tests
        include_accessibility: Whether to include accessibility tests
        output_format: Output format (structured, gherkin, markdown)

    Returns:
        Generated test cases
    """
    format_map = {
        "structured": TestCaseFormat.STRUCTURED,
        "gherkin": TestCaseFormat.GHERKIN,
        "markdown": TestCaseFormat.MARKDOWN,
    }

    agent = TestCaseWritingAgent(
        output_format=format_map.get(output_format, TestCaseFormat.STRUCTURED),
        include_edge_cases=include_edge_cases,
        include_security=include_security,
        include_accessibility=include_accessibility,
    )

    test_suite = agent.generate_test_suite(requirements, feature_name)

    return {
        "testSuite": test_suite.to_dict(),
        "formatted": agent.format_output(test_suite),
    }
