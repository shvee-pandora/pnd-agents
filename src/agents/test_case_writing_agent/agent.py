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
- Integrate with JIRA for test case management
"""

import re
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

# JIRA Integration signature comment
QAIN_SIGNATURE = "I'm your Junior Quality Engineer - qAIn"


# =============================================================================
# External Documentation Link Processing
# =============================================================================

def extract_links_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extract Figma and Confluence links from text.

    Args:
        text: Text that may contain documentation links

    Returns:
        Dictionary with 'figma' and 'confluence' link lists
    """
    links = {
        "figma": [],
        "confluence": [],
        "other": []
    }

    # Figma URL patterns
    figma_patterns = [
        r'https?://(?:www\.)?figma\.com/(?:file|design|proto)/[^\s\)>\]]+',
        r'https?://(?:www\.)?figma\.com/board/[^\s\)>\]]+',
    ]

    # Confluence URL patterns
    confluence_patterns = [
        r'https?://[^\s/]+\.atlassian\.net/wiki/[^\s\)>\]]+',
        r'https?://[^\s/]+/confluence/[^\s\)>\]]+',
        r'https?://confluence\.[^\s/]+/[^\s\)>\]]+',
    ]

    for pattern in figma_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        links["figma"].extend(matches)

    for pattern in confluence_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        links["confluence"].extend(matches)

    # Remove duplicates while preserving order
    links["figma"] = list(dict.fromkeys(links["figma"]))
    links["confluence"] = list(dict.fromkeys(links["confluence"]))

    return links


def fetch_external_doc_content(url: str, auth_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch content from external documentation URL (Figma or Confluence).

    Args:
        url: The documentation URL
        auth_token: Optional authentication token

    Returns:
        Dictionary with extracted content and metadata
    """
    result = {
        "url": url,
        "type": "unknown",
        "title": "",
        "content": "",
        "components": [],
        "requirements": [],
        "error": None
    }

    try:
        # Determine URL type
        if "figma.com" in url.lower():
            result["type"] = "figma"
            result["content"] = _extract_figma_context(url)
        elif "atlassian.net/wiki" in url.lower() or "confluence" in url.lower():
            result["type"] = "confluence"
            result["content"] = _extract_confluence_context(url, auth_token)
        else:
            result["type"] = "other"
            result["content"] = f"External documentation link: {url}"

    except Exception as e:
        logger.warning(f"Failed to fetch external doc from {url}: {e}")
        result["error"] = str(e)
        result["content"] = f"[Unable to fetch content from {url}. Manual review required.]"

    return result


def _extract_figma_context(url: str) -> str:
    """
    Extract context from Figma URL for test case generation.

    Note: Full Figma API integration requires authentication.
    This provides structured guidance for manual review.

    Args:
        url: Figma file/design URL

    Returns:
        Context string for test case generation
    """
    # Extract file key from URL
    file_key_match = re.search(r'figma\.com/(?:file|design|proto)/([^/]+)', url)
    file_key = file_key_match.group(1) if file_key_match else "unknown"

    context = f"""
## Figma Design Reference
**URL:** {url}
**File Key:** {file_key}

### Design Review Checklist for Test Cases:
1. **Visual Elements:**
   - Verify all UI components match the design
   - Check color schemes, typography, and spacing
   - Validate responsive breakpoints if specified

2. **Interactive Elements:**
   - Identify all clickable/tappable elements
   - Note hover states and transitions
   - Document form fields and validation requirements

3. **User Flows:**
   - Map out primary user journey from design
   - Identify entry and exit points
   - Note conditional paths and error states

4. **Accessibility Considerations:**
   - Check color contrast ratios
   - Verify touch target sizes
   - Note any animation/motion requirements

5. **Edge Cases from Design:**
   - Empty states
   - Loading states
   - Error states
   - Maximum content scenarios

### Recommended Test Scenarios:
- Validate UI matches Figma design specifications
- Test all interactive elements identified in design
- Verify responsive behavior across breakpoints
- Test accessibility compliance per design annotations
"""
    return context


def _extract_confluence_context(url: str, auth_token: Optional[str] = None) -> str:
    """
    Extract context from Confluence URL for test case generation.

    Args:
        url: Confluence page URL
        auth_token: Optional Confluence API token

    Returns:
        Context string for test case generation
    """
    # Try to extract page info from URL
    page_match = re.search(r'/pages/(\d+)', url)
    page_id = page_match.group(1) if page_match else None

    space_match = re.search(r'/spaces/([^/]+)', url)
    space_key = space_match.group(1) if space_match else None

    context = f"""
## Confluence Documentation Reference
**URL:** {url}
**Page ID:** {page_id or 'Not extracted'}
**Space:** {space_key or 'Not extracted'}

### Documentation Review for Test Cases:
1. **Requirements Extraction:**
   - Identify functional requirements
   - Note acceptance criteria
   - Extract business rules

2. **Technical Specifications:**
   - API endpoints and contracts
   - Data models and schemas
   - Integration points

3. **User Stories:**
   - Parse user story format (As a... I want... So that...)
   - Extract acceptance criteria
   - Identify personas and use cases

4. **Test Considerations:**
   - Documented test scenarios
   - Known edge cases
   - Performance requirements

### Recommended Actions:
- Review linked Confluence page for detailed requirements
- Extract acceptance criteria for test case generation
- Identify any referenced API specifications or schemas
- Note any cross-references to other documentation
"""

    # If we have auth token, we could make API call
    if auth_token and page_id:
        context += """
### API Integration Available:
- Confluence API token provided
- Can fetch page content programmatically
- Contact administrator for API access if needed
"""

    return context


def enrich_requirements_with_external_docs(
    requirements: str,
    external_links: List[str],
    auth_tokens: Optional[Dict[str, str]] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Enrich requirements text with content from external documentation links.

    Args:
        requirements: Original requirements text
        external_links: List of external documentation URLs
        auth_tokens: Optional dict with 'figma' and 'confluence' tokens

    Returns:
        Tuple of (enriched requirements string, list of fetched doc metadata)
    """
    if not external_links:
        # Try to extract links from requirements text
        extracted = extract_links_from_text(requirements)
        external_links = extracted["figma"] + extracted["confluence"]

    if not external_links:
        return requirements, []

    auth_tokens = auth_tokens or {}
    fetched_docs = []
    enriched_content = [requirements, "\n\n---\n## External Documentation Context\n"]

    for url in external_links:
        token = None
        if "figma.com" in url.lower():
            token = auth_tokens.get("figma")
        elif "confluence" in url.lower() or "atlassian.net" in url.lower():
            token = auth_tokens.get("confluence")

        doc_content = fetch_external_doc_content(url, token)
        fetched_docs.append(doc_content)

        if doc_content["content"]:
            enriched_content.append(f"\n### Source: {doc_content['type'].title()}\n")
            enriched_content.append(doc_content["content"])

    enriched_requirements = "\n".join(enriched_content)

    logger.info(f"Enriched requirements with {len(fetched_docs)} external document(s)")

    return enriched_requirements, fetched_docs


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


class TestLevel(Enum):
    """Test levels for categorization."""
    FT_UI = "FT-UI"
    FT_API = "FT-API"
    SIT = "SIT"
    E2E = "E2E"
    UAT = "UAT"
    A11Y = "A11Y"
    PERFORMANCE = "Performance"
    SECURITY = "Security"


class TestingCycle(Enum):
    """Testing cycle categorization."""
    SMOKE = "Smoke"
    SANITY = "Sanity"
    REGRESSION = "Regression"
    EXPLORATORY = "Exploratory"


class ComponentType(Enum):
    """Component types for test cases."""
    UI = "UI"
    API = "API"
    E2E = "E2E"
    DATABASE = "Database"
    INTEGRATION = "Integration"


class TestingTechnique(Enum):
    """Testing techniques used for test case design."""
    BOUNDARY_VALUE_ANALYSIS = "Boundary Value Analysis (BVA)"
    EQUIVALENCE_PARTITIONING = "Equivalence Partitioning (EP)"
    DECISION_TABLE = "Decision Table Testing"
    STATE_TRANSITION = "State Transition Testing"
    USE_CASE = "Use Case Testing"
    ERROR_GUESSING = "Error Guessing"
    PAIRWISE = "Pairwise (All-Pairs) Testing"
    CAUSE_EFFECT = "Cause-Effect Graphing"
    EXPLORATORY = "Exploratory Testing"
    DECISION_COVERAGE = "Decision Coverage / Branch Testing"
    PERFORMANCE = "Performance Testing"
    SECURITY = "Security Testing"
    USABILITY = "Usability Testing"


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
    # New fields for enhanced test case management
    is_regression: bool = False
    is_smoke: bool = False
    test_level: Optional[TestLevel] = None
    testing_cycle: Optional[TestingCycle] = None
    component: Optional[ComponentType] = None
    testing_technique: Optional[TestingTechnique] = None
    technique_rationale: Optional[str] = None
    test_data: List[Dict[str, Any]] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)

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
            "isRegression": self.is_regression,
            "isSmoke": self.is_smoke,
            "testLevel": self.test_level.value if self.test_level else None,
            "testingCycle": self.testing_cycle.value if self.testing_cycle else None,
            "component": self.component.value if self.component else None,
            "testingTechnique": self.testing_technique.value if self.testing_technique else None,
            "techniqueRationale": self.technique_rationale,
            "testData": self.test_data,
            "labels": self.labels,
        }

    def to_gherkin(self) -> str:
        """Convert test case to Gherkin format with full metadata."""
        # Build metadata tags
        metadata_lines = []
        if self.labels:
            metadata_lines.append(f"@Label: {', '.join(self.labels)}")
        if self.component:
            metadata_lines.append(f"@Component: {self.component.value}")
        metadata_lines.append(f"@Priority: {self.priority.value.capitalize()}")
        metadata_lines.append(f"@TestType: {'Functional' if self.test_type in [TestCaseType.FUNCTIONAL, TestCaseType.NEGATIVE, TestCaseType.EDGE_CASE, TestCaseType.BOUNDARY, TestCaseType.INTEGRATION] else 'Non-Functional'}")
        if self.test_level:
            metadata_lines.append(f"@TestLevel: {self.test_level.value}")
        if self.testing_cycle:
            metadata_lines.append(f"@TestingCycle: {self.testing_cycle.value}")
        if self.testing_technique:
            metadata_lines.append(f"@TestingTechnique: {self.testing_technique.value}")
        if self.technique_rationale:
            metadata_lines.append(f"@TechniqueRationale: {self.technique_rationale}")

        lines = metadata_lines + [
            "",
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
        """Convert test case to Markdown format with full metadata."""
        lines = [
            f"### {self.id}: {self.title}",
            "",
        ]

        # Metadata table
        lines.append("| Attribute | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| **Priority** | {self.priority.value.capitalize()} |")
        lines.append(f"| **Type** | {self.test_type.value} |")
        if self.test_level:
            lines.append(f"| **Test Level** | {self.test_level.value} |")
        if self.testing_cycle:
            lines.append(f"| **Testing Cycle** | {self.testing_cycle.value} |")
        if self.component:
            lines.append(f"| **Component** | {self.component.value} |")
        if self.testing_technique:
            lines.append(f"| **Technique** | {self.testing_technique.value} |")
        if self.is_smoke:
            lines.append("| **Smoke Test** | Yes |")
        if self.is_regression:
            lines.append("| **Regression** | Yes |")
        lines.append("")

        lines.append(f"**Description:** {self.description}")
        lines.append("")

        if self.technique_rationale:
            lines.append(f"**Technique Rationale:** {self.technique_rationale}")
            lines.append("")

        if self.preconditions:
            lines.append("**Preconditions:**")
            for pre in self.preconditions:
                lines.append(f"- {pre}")
            lines.append("")

        lines.append("**Steps:**")
        for step in self.steps:
            lines.append(f"{step.step_number}. {step.action}")
            lines.append(f"   - Expected: {step.expected_result}")
            if step.test_data:
                lines.append(f"   - Test Data: {step.test_data}")
        lines.append("")

        if self.expected_result:
            lines.append(f"**Expected Result:** {self.expected_result}")
            lines.append("")

        if self.test_data:
            lines.append("**Test Data:**")
            for data in self.test_data:
                lines.append(f"- {data}")
            lines.append("")

        if self.tags:
            lines.append(f"**Tags:** {', '.join(self.tags)}")

        if self.labels:
            lines.append(f"**Labels:** {', '.join(self.labels)}")

        return "\n".join(lines)


@dataclass
class TestSuite:
    """Represents a collection of related test cases."""
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    coverage_areas: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    coverage_gaps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "testCases": [tc.to_dict() for tc in self.test_cases],
            "coverageAreas": self.coverage_areas,
            "requirements": self.requirements,
            "coverageGaps": self.coverage_gaps,
            "summary": {
                "totalTestCases": len(self.test_cases),
                "byType": self._count_by_type(),
                "byPriority": self._count_by_priority(),
                "byTestLevel": self._count_by_test_level(),
                "byTestingCycle": self._count_by_testing_cycle(),
                "byComponent": self._count_by_component(),
                "byTechnique": self._count_by_technique(),
                "smokeTests": sum(1 for tc in self.test_cases if tc.is_smoke),
                "regressionTests": sum(1 for tc in self.test_cases if tc.is_regression),
            },
            "traceabilityMatrix": self._build_traceability_matrix(),
            "coverageMatrix": self._build_coverage_matrix(),
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

    def _count_by_test_level(self) -> Dict[str, int]:
        counts = {}
        for tc in self.test_cases:
            if tc.test_level:
                level_name = tc.test_level.value
                counts[level_name] = counts.get(level_name, 0) + 1
        return counts

    def _count_by_testing_cycle(self) -> Dict[str, int]:
        counts = {}
        for tc in self.test_cases:
            if tc.testing_cycle:
                cycle_name = tc.testing_cycle.value
                counts[cycle_name] = counts.get(cycle_name, 0) + 1
        return counts

    def _count_by_component(self) -> Dict[str, int]:
        counts = {}
        for tc in self.test_cases:
            if tc.component:
                comp_name = tc.component.value
                counts[comp_name] = counts.get(comp_name, 0) + 1
        return counts

    def _count_by_technique(self) -> Dict[str, int]:
        counts = {}
        for tc in self.test_cases:
            if tc.testing_technique:
                tech_name = tc.testing_technique.value
                counts[tech_name] = counts.get(tech_name, 0) + 1
        return counts

    def _build_traceability_matrix(self) -> List[Dict[str, Any]]:
        """Build traceability matrix linking requirements to test cases."""
        matrix = []
        for tc in self.test_cases:
            matrix.append({
                "testCaseId": tc.id,
                "testCaseTitle": tc.title,
                "requirement": tc.related_requirement,
                "testType": tc.test_type.value,
                "priority": tc.priority.value,
                "testLevel": tc.test_level.value if tc.test_level else None,
            })
        return matrix

    def _build_coverage_matrix(self) -> Dict[str, Any]:
        """Build coverage matrix showing Priority x Test Level distribution."""
        # Initialize matrix
        priorities = [p.value for p in TestCasePriority]
        levels = [l.value for l in TestLevel]

        matrix = {p: {l: 0 for l in levels} for p in priorities}

        for tc in self.test_cases:
            if tc.test_level:
                matrix[tc.priority.value][tc.test_level.value] += 1

        return {
            "priorityByLevel": matrix,
            "testTypeSummary": self._count_by_type(),
            "testingCycleSummary": self._count_by_testing_cycle(),
        }

    def get_priority_level_table(self) -> str:
        """Generate Priority x Test Level table as markdown."""
        levels = [l.value for l in TestLevel]
        priorities = [p.value for p in TestCasePriority]

        # Build count matrix
        matrix = {p: {l: 0 for l in levels} for p in priorities}
        for tc in self.test_cases:
            if tc.test_level:
                matrix[tc.priority.value][tc.test_level.value] += 1

        # Generate markdown table
        header = "| Priority | " + " | ".join(levels) + " | Total |"
        separator = "|" + "|".join(["---"] * (len(levels) + 2)) + "|"

        rows = [header, separator]
        for priority in priorities:
            row_counts = [str(matrix[priority][level]) for level in levels]
            total = sum(matrix[priority].values())
            rows.append(f"| {priority.capitalize()} | " + " | ".join(row_counts) + f" | {total} |")

        # Add totals row
        col_totals = [str(sum(matrix[p][l] for p in priorities)) for l in levels]
        grand_total = sum(int(t) for t in col_totals)
        rows.append(f"| **Total** | " + " | ".join(col_totals) + f" | **{grand_total}** |")

        return "\n".join(rows)


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


@dataclass
class JiraWorkflowConfig:
    """Configuration for JIRA test case workflow."""
    project_key: str
    story_key: str
    test_types: List[str] = field(default_factory=list)
    include_functional: bool = True
    include_api: bool = False
    include_sit: bool = False
    include_e2e: bool = False
    include_uat: bool = False
    include_a11y: bool = False
    include_performance: bool = False
    include_security: bool = False
    feature_label: str = ""
    create_in_jira: bool = True
    link_to_story: bool = True
    # External documentation links
    external_doc_links: List[str] = field(default_factory=list)
    external_doc_content: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_answers(cls, answers: Dict[str, Any]) -> "JiraWorkflowConfig":
        """Create config from user answers."""
        test_types = answers.get("test_types", [])
        if isinstance(test_types, str):
            test_types = [t.strip() for t in test_types.split(",")]

        # Parse external doc links
        external_links = answers.get("external_doc_links", [])
        if isinstance(external_links, str):
            external_links = [l.strip() for l in external_links.split(",") if l.strip()]

        return cls(
            project_key=answers.get("project_key", ""),
            story_key=answers.get("story_key", ""),
            test_types=test_types,
            include_functional="FT-UI" in test_types or "Functional" in test_types,
            include_api="FT-API" in test_types or "API" in test_types,
            include_sit="SIT" in test_types,
            include_e2e="E2E" in test_types,
            include_uat="UAT" in test_types,
            include_a11y="A11Y" in test_types or "Accessibility" in test_types,
            include_performance="Performance" in test_types,
            include_security="Security" in test_types,
            feature_label=answers.get("feature_label", ""),
            create_in_jira=answers.get("create_in_jira", True),
            link_to_story=answers.get("link_to_story", True),
            external_doc_links=external_links,
        )


@dataclass
class JiraTestCaseCreationResult:
    """Result from JIRA test case creation."""
    created_count: int = 0
    linked_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    created_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


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

    # Patterns for extracting testable requirements (enhanced)
    REQUIREMENT_PATTERNS = [
        # Basic requirement patterns
        re.compile(r"(?:should|must|shall)\s+(.+?)(?:\.|$)", re.IGNORECASE),
        re.compile(r"(?:user\s+)?(?:can|is able to)\s+(.+?)(?:\.|$)", re.IGNORECASE),
        re.compile(r"(?:when|if)\s+(.+?),?\s*(?:then|should)\s+(.+?)(?:\.|$)", re.IGNORECASE),
        re.compile(r"given\s+(.+?),?\s*when\s+(.+?),?\s*then\s+(.+?)(?:\.|$)", re.IGNORECASE),
        # User story format: As a [role], I want [feature], so that [benefit]
        re.compile(r"as\s+(?:a|an)\s+(.+?),?\s*i\s+want\s+(.+?),?\s*so\s+that\s+(.+?)(?:\.|$)", re.IGNORECASE),
        # Verification statements
        re.compile(r"(?:verify|ensure|confirm|validate)\s+(?:that\s+)?(.+?)(?:\.|$)", re.IGNORECASE),
        # Explicit acceptance criteria format
        re.compile(r"(?:AC\d*|acceptance\s+criteria?)[\s:]+(.+?)(?:\.|$)", re.IGNORECASE),
        # Feature description
        re.compile(r"(?:feature|functionality)[\s:]+(.+?)(?:\.|$)", re.IGNORECASE),
        # Expects/returns patterns (for API)
        re.compile(r"(?:expects?|returns?|responds?\s+with)\s+(.+?)(?:\.|$)", re.IGNORECASE),
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

    # Field-specific edge cases for context-aware testing
    FIELD_SPECIFIC_EDGE_CASES: Dict[str, List[str]] = {
        "email": [
            "missing @ symbol",
            "multiple @ symbols",
            "invalid domain",
            "case sensitivity",
            "special characters in local part",
            "very long email address",
            "spaces in email",
            "unicode characters",
        ],
        "password": [
            "common/weak passwords",
            "dictionary words",
            "no complexity (all lowercase)",
            "minimum length boundary",
            "maximum length boundary",
            "spaces only",
            "SQL injection attempt",
            "unicode characters",
        ],
        "phone": [
            "invalid country code",
            "too few digits",
            "too many digits",
            "letters mixed with numbers",
            "special characters",
            "international format",
            "extension format",
        ],
        "date": [
            "leap year (Feb 29)",
            "invalid month (13)",
            "invalid day (32)",
            "timezone boundaries",
            "future dates when not allowed",
            "past dates when not allowed",
            "date format variations",
            "year 2038 problem",
        ],
        "numeric": [
            "floating point precision",
            "integer overflow",
            "NaN value",
            "Infinity value",
            "negative zero",
            "scientific notation",
            "leading zeros",
            "currency format",
        ],
        "url": [
            "missing protocol",
            "invalid protocol",
            "localhost URLs",
            "IP addresses",
            "port numbers",
            "query parameters",
            "fragments/anchors",
            "encoded characters",
        ],
        "file_upload": [
            "empty file",
            "file too large",
            "wrong file type",
            "malicious file extension",
            "file with spaces in name",
            "unicode filename",
            "multiple file upload",
            "corrupted file",
        ],
        "text": [
            "empty input",
            "whitespace only",
            "leading/trailing spaces",
            "minimum length boundary",
            "maximum length boundary",
            "special characters (!@#$%^&*)",
            "HTML tags injection",
            "script tags (XSS attempt)",
            "SQL injection patterns",
            "unicode characters",
            "emoji characters",
            "newline characters",
            "tab characters",
            "null byte injection",
            "very long string (10000+ chars)",
            "RTL (right-to-left) text",
            "mixed case sensitivity",
        ],
        "textarea": [
            "empty input",
            "whitespace only",
            "single character",
            "maximum character limit",
            "exceeding character limit",
            "multiple paragraphs",
            "line breaks (\\n, \\r\\n)",
            "tab characters",
            "HTML tags injection",
            "script tags (XSS attempt)",
            "markdown syntax",
            "code blocks",
            "unicode characters",
            "emoji characters",
            "copy-paste from Word (hidden formatting)",
            "very long text without spaces",
            "mixed languages",
            "URL auto-linking",
        ],
        "dropdown": [
            "no selection (default state)",
            "first option selection",
            "last option selection",
            "middle option selection",
            "rapid selection changes",
            "selecting disabled option",
            "option with very long text",
            "option with special characters",
            "option with HTML entities",
            "selecting same option twice",
            "programmatic value change",
            "invalid value injection via DOM",
            "empty options list",
            "single option only",
            "option groups navigation",
            "keyboard navigation (arrow keys)",
            "search/filter functionality",
            "multi-select behavior (if applicable)",
        ],
        "radio": [
            "no selection (default state)",
            "single option selection",
            "changing selection between options",
            "selecting already selected option",
            "rapid selection changes",
            "disabled option interaction",
            "option with very long label",
            "option with special characters",
            "keyboard navigation (Tab, Space)",
            "programmatic value change",
            "invalid value injection via DOM",
            "single radio button only",
            "large number of options (20+)",
            "horizontal vs vertical layout",
            "hidden radio buttons",
            "required validation when none selected",
        ],
        "checkbox": [
            "unchecked state (default)",
            "checked state",
            "toggle on/off",
            "rapid toggle multiple times",
            "indeterminate state",
            "disabled checkbox interaction",
            "required checkbox not checked",
            "checkbox with very long label",
            "checkbox with special characters",
            "keyboard interaction (Space key)",
            "multiple checkboxes - select all",
            "multiple checkboxes - deselect all",
            "multiple checkboxes - partial selection",
            "checkbox group minimum selection",
            "checkbox group maximum selection",
            "programmatic value change",
            "hidden checkbox submission",
            "checkbox in disabled fieldset",
        ],
    }

    # API test scenarios
    API_TEST_SCENARIOS = [
        # Basic validation
        ("valid request with all required fields", TestCasePriority.CRITICAL, True),
        ("missing required fields", TestCasePriority.HIGH, False),
        ("invalid field types", TestCasePriority.HIGH, False),
        ("empty request body", TestCasePriority.MEDIUM, False),
        ("malformed JSON", TestCasePriority.MEDIUM, False),
        # Status codes for invalid input
        ("proper 400 status code for invalid input", TestCasePriority.HIGH, False),
        ("proper 404 status code for non-existent resource", TestCasePriority.HIGH, False),
        ("proper 422 status code for unprocessable entity", TestCasePriority.MEDIUM, False),
        ("proper 409 status code for conflict/duplicate", TestCasePriority.MEDIUM, False),
        # Authentication & Authorization
        ("invalid authentication token", TestCasePriority.CRITICAL, False),
        ("expired authentication token", TestCasePriority.HIGH, False),
        ("missing authentication header", TestCasePriority.CRITICAL, False),
        # Security - Role-based access control (RBAC)
        ("role-based access - admin user access", TestCasePriority.CRITICAL, True),
        ("role-based access - regular user restricted access", TestCasePriority.CRITICAL, False),
        ("role-based access - unauthorized role rejection", TestCasePriority.CRITICAL, False),
        ("role-based access - permission escalation prevention", TestCasePriority.HIGH, False),
        # Contract validation (OpenAPI/Swagger)
        ("contract - response JSON matches OpenAPI spec", TestCasePriority.CRITICAL, True),
        ("contract - all required fields exist in response", TestCasePriority.CRITICAL, True),
        ("contract - response data types match spec", TestCasePriority.HIGH, True),
        ("contract - response schema validation", TestCasePriority.HIGH, True),
        ("contract - request body schema validation", TestCasePriority.HIGH, False),
        # Idempotency
        ("idempotency - repeated POST with same key returns same result", TestCasePriority.HIGH, True),
        ("idempotency - duplicate request does not create duplicate resource", TestCasePriority.HIGH, True),
        ("idempotency - PUT request is idempotent", TestCasePriority.MEDIUM, True),
        ("idempotency - DELETE request is idempotent", TestCasePriority.MEDIUM, True),
        # Versioning & Backward compatibility
        ("versioning - v1 API backward compatibility", TestCasePriority.HIGH, True),
        ("versioning - v2 API new features work correctly", TestCasePriority.HIGH, True),
        ("versioning - deprecated endpoint warning in response", TestCasePriority.MEDIUM, True),
        ("versioning - version header handling", TestCasePriority.MEDIUM, True),
        # Data persistence & Database integrity
        ("db persistence - correct data persisted after API call", TestCasePriority.CRITICAL, True),
        ("db persistence - no duplicate records created", TestCasePriority.CRITICAL, True),
        ("db persistence - transactional consistency on success", TestCasePriority.HIGH, True),
        ("db persistence - rollback on partial failure", TestCasePriority.HIGH, False),
        ("db persistence - referential integrity maintained", TestCasePriority.HIGH, True),
        # Rate limiting & Performance
        ("rate limiting behavior", TestCasePriority.MEDIUM, False),
        ("timeout handling", TestCasePriority.MEDIUM, False),
        ("pagination with valid parameters", TestCasePriority.HIGH, True),
        ("pagination with invalid parameters", TestCasePriority.MEDIUM, False),
        ("concurrent requests", TestCasePriority.MEDIUM, False),
        ("large payload handling", TestCasePriority.LOW, False),
        # Protocol & Format
        ("content-type validation", TestCasePriority.MEDIUM, False),
        ("HTTP method validation", TestCasePriority.HIGH, False),
        ("CORS preflight request", TestCasePriority.MEDIUM, True),
        ("response format validation", TestCasePriority.HIGH, True),
    ]

    # Boundary value scenarios
    BOUNDARY_SCENARIOS = [
        ("minimum value minus one", "min-1", TestCasePriority.HIGH),
        ("minimum value", "min", TestCasePriority.CRITICAL),
        ("minimum value plus one", "min+1", TestCasePriority.HIGH),
        ("typical/nominal value", "nominal", TestCasePriority.MEDIUM),
        ("maximum value minus one", "max-1", TestCasePriority.HIGH),
        ("maximum value", "max", TestCasePriority.CRITICAL),
        ("maximum value plus one", "max+1", TestCasePriority.HIGH),
    ]

    # Integration test scenarios
    INTEGRATION_SCENARIOS = [
        "data flow between components",
        "API contract validation",
        "database transaction integrity",
        "message queue processing",
        "cache synchronization",
        "external service integration",
        "authentication flow across services",
        "error propagation between layers",
        "configuration consistency",
        "logging and monitoring integration",
    ]

    # Performance test scenarios
    PERFORMANCE_SCENARIOS = [
        ("response time under normal load", "< 2 seconds", TestCasePriority.HIGH),
        ("response time under peak load", "< 5 seconds", TestCasePriority.HIGH),
        ("throughput test (requests/second)", "> 100 req/s", TestCasePriority.MEDIUM),
        ("memory usage under load", "< 80% capacity", TestCasePriority.MEDIUM),
        ("CPU usage under load", "< 70% capacity", TestCasePriority.MEDIUM),
        ("database query performance", "< 100ms", TestCasePriority.HIGH),
        ("concurrent user handling", "> 1000 users", TestCasePriority.MEDIUM),
        ("resource cleanup after load", "no memory leaks", TestCasePriority.HIGH),
        ("graceful degradation", "maintains core functionality", TestCasePriority.MEDIUM),
        ("recovery time after failure", "< 30 seconds", TestCasePriority.HIGH),
    ]

    # Cross-browser/device test scenarios
    CROSS_BROWSER_SCENARIOS = [
        ("Chrome latest", "desktop", TestCasePriority.CRITICAL),
        ("Firefox latest", "desktop", TestCasePriority.HIGH),
        ("Safari latest", "desktop", TestCasePriority.HIGH),
        ("Edge latest", "desktop", TestCasePriority.MEDIUM),
        ("Chrome Android", "mobile", TestCasePriority.HIGH),
        ("Safari iOS", "mobile", TestCasePriority.HIGH),
        ("Samsung Internet", "mobile", TestCasePriority.LOW),
        ("Tablet landscape", "tablet", TestCasePriority.MEDIUM),
        ("Tablet portrait", "tablet", TestCasePriority.MEDIUM),
    ]

    # State transition definitions for common scenarios
    COMMON_STATE_TRANSITIONS: Dict[str, Dict[str, List[str]]] = {
        "user_session": {
            "logged_out": ["logging_in"],
            "logging_in": ["logged_in", "login_failed"],
            "logged_in": ["logged_out", "session_expired"],
            "login_failed": ["logging_in", "account_locked"],
            "session_expired": ["logged_out", "logging_in"],
            "account_locked": ["logged_out"],
        },
        "order_status": {
            "draft": ["submitted", "cancelled"],
            "submitted": ["processing", "cancelled"],
            "processing": ["shipped", "cancelled", "on_hold"],
            "on_hold": ["processing", "cancelled"],
            "shipped": ["delivered", "returned"],
            "delivered": ["returned", "completed"],
            "returned": ["refunded"],
            "refunded": ["completed"],
            "cancelled": ["completed"],
            "completed": [],
        },
        "payment_status": {
            "pending": ["processing", "failed", "cancelled"],
            "processing": ["completed", "failed"],
            "completed": ["refunded"],
            "failed": ["pending", "cancelled"],
            "refunded": [],
            "cancelled": [],
        },
    }

    def __init__(
        self,
        output_format: TestCaseFormat = TestCaseFormat.STRUCTURED,
        include_edge_cases: bool = True,
        include_security: bool = False,
        include_accessibility: bool = False,
        include_boundary: bool = True,
        include_integration: bool = False,
        include_performance: bool = False,
        include_api: bool = False,
        include_cross_browser: bool = False,
        default_label: str = "qAIn",
    ):
        """
        Initialize the Test Case Writing Agent.

        Args:
            output_format: Format for test case output
            include_edge_cases: Whether to include edge case test scenarios
            include_security: Whether to include security test scenarios
            include_accessibility: Whether to include accessibility test scenarios
            include_boundary: Whether to include boundary value test scenarios
            include_integration: Whether to include integration test scenarios
            include_performance: Whether to include performance test scenarios
            include_api: Whether to include API-specific test scenarios
            include_cross_browser: Whether to include cross-browser test scenarios
            default_label: Default label to add to all test cases
        """
        self.output_format = output_format
        self.include_edge_cases = include_edge_cases
        self.include_security = include_security
        self.include_accessibility = include_accessibility
        self.include_boundary = include_boundary
        self.include_integration = include_integration
        self.include_performance = include_performance
        self.include_api = include_api
        self.include_cross_browser = include_cross_browser
        self.default_label = default_label
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

    def generate_boundary_tests(
        self,
        feature_name: str,
        field_name: str = "input",
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
    ) -> List[TestCase]:
        """
        Generate boundary value test cases.

        Args:
            feature_name: Name of the feature being tested
            field_name: Name of the field being tested
            min_value: Minimum valid value (if known)
            max_value: Maximum valid value (if known)

        Returns:
            List of boundary test cases
        """
        test_cases = []

        for scenario_name, boundary_type, priority in self.BOUNDARY_SCENARIOS:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Validate that {field_name} handles {scenario_name}",
                description=f"Boundary Value Analysis: Test {field_name} at {boundary_type}",
                test_type=TestCaseType.BOUNDARY,
                priority=priority,
                preconditions=[f"User is on the {feature_name} page"],
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Enter {boundary_type} value for {field_name}",
                        expected_result="Value is accepted for processing",
                        test_data=f"Boundary: {boundary_type}" + (f" (min={min_value}, max={max_value})" if min_value or max_value else ""),
                    ),
                    TestStep(
                        step_number=2,
                        action="Submit the form or trigger validation",
                        expected_result="System validates boundary correctly",
                    ),
                    TestStep(
                        step_number=3,
                        action="Verify system behavior",
                        expected_result="Valid boundaries accepted, invalid boundaries rejected with clear message",
                    ),
                ],
                expected_result=f"System correctly handles {scenario_name} for {field_name}",
                tags=["boundary", "bva", field_name.lower().replace(" ", "-")],
                test_level=TestLevel.FT_UI,
                testing_cycle=TestingCycle.REGRESSION,
                component=ComponentType.UI,
                testing_technique=TestingTechnique.BOUNDARY_VALUE_ANALYSIS,
                technique_rationale="BVA is ideal for testing input validation at value boundaries",
                labels=[self.default_label, feature_name.lower().replace(" ", "-")],
                is_regression=True,
            )
            test_cases.append(test_case)

        return test_cases

    def generate_integration_tests(
        self,
        feature_name: str,
        dependencies: Optional[List[str]] = None,
    ) -> List[TestCase]:
        """
        Generate integration test cases.

        Args:
            feature_name: Name of the feature being tested
            dependencies: List of dependent components/services

        Returns:
            List of integration test cases
        """
        test_cases = []

        for scenario in self.INTEGRATION_SCENARIOS:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Validate that {feature_name} {scenario}",
                description=f"Integration test: Verify {scenario} for {feature_name}",
                test_type=TestCaseType.INTEGRATION,
                priority=TestCasePriority.HIGH,
                preconditions=[
                    f"All dependent services are running",
                    f"Test environment is configured for integration testing",
                ] + ([f"Dependencies: {', '.join(dependencies)}"] if dependencies else []),
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Set up integration test scenario for {scenario}",
                        expected_result="Test environment ready",
                    ),
                    TestStep(
                        step_number=2,
                        action=f"Execute {feature_name} functionality",
                        expected_result="Feature executes and interacts with dependencies",
                    ),
                    TestStep(
                        step_number=3,
                        action="Verify integration points",
                        expected_result=f"{scenario} works correctly",
                    ),
                    TestStep(
                        step_number=4,
                        action="Validate data consistency across components",
                        expected_result="Data is consistent across all integrated components",
                    ),
                ],
                expected_result=f"{feature_name} correctly handles {scenario}",
                tags=["integration", "sit", scenario.replace(" ", "-")],
                test_level=TestLevel.SIT,
                testing_cycle=TestingCycle.REGRESSION,
                component=ComponentType.INTEGRATION,
                testing_technique=TestingTechnique.USE_CASE,
                technique_rationale="Use Case Testing validates real-world integration scenarios",
                labels=[self.default_label, feature_name.lower().replace(" ", "-")],
                is_regression=True,
            )
            test_cases.append(test_case)

        return test_cases

    def generate_performance_tests(self, feature_name: str) -> List[TestCase]:
        """
        Generate performance test cases.

        Args:
            feature_name: Name of the feature being tested

        Returns:
            List of performance test cases
        """
        test_cases = []

        for scenario_name, threshold, priority in self.PERFORMANCE_SCENARIOS:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Validate that {feature_name} meets {scenario_name}",
                description=f"Performance test: {scenario_name} with threshold {threshold}",
                test_type=TestCaseType.PERFORMANCE,
                priority=priority,
                preconditions=[
                    f"Performance testing environment is configured",
                    "Baseline metrics are established",
                    "Load testing tools are available",
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Configure test for {scenario_name}",
                        expected_result="Test configuration complete",
                    ),
                    TestStep(
                        step_number=2,
                        action="Execute performance test",
                        expected_result="Test completes without errors",
                    ),
                    TestStep(
                        step_number=3,
                        action=f"Measure against threshold: {threshold}",
                        expected_result=f"Results meet or exceed threshold: {threshold}",
                    ),
                    TestStep(
                        step_number=4,
                        action="Analyze results and identify bottlenecks",
                        expected_result="Performance report generated",
                    ),
                ],
                expected_result=f"{feature_name} meets performance criteria: {threshold}",
                tags=["performance", "load-testing", scenario_name.replace(" ", "-").replace("/", "-")],
                test_level=TestLevel.PERFORMANCE,
                testing_cycle=TestingCycle.REGRESSION,
                component=ComponentType.E2E,
                testing_technique=TestingTechnique.PERFORMANCE,
                technique_rationale="Performance testing ensures system meets non-functional requirements",
                labels=[self.default_label, feature_name.lower().replace(" ", "-"), "performance"],
            )
            test_cases.append(test_case)

        return test_cases

    def generate_api_tests(
        self,
        feature_name: str,
        endpoint: str = "/api/endpoint",
        http_method: str = "POST",
    ) -> List[TestCase]:
        """
        Generate API-specific test cases.

        Args:
            feature_name: Name of the feature/API being tested
            endpoint: API endpoint path
            http_method: HTTP method (GET, POST, PUT, DELETE, etc.)

        Returns:
            List of API test cases
        """
        test_cases = []

        for scenario_name, priority, is_positive in self.API_TEST_SCENARIOS:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Validate that {endpoint} handles {scenario_name}",
                description=f"API test: {http_method} {endpoint} - {scenario_name}",
                test_type=TestCaseType.FUNCTIONAL if is_positive else TestCaseType.NEGATIVE,
                priority=priority,
                preconditions=[
                    f"API server is running",
                    f"Valid authentication credentials are available",
                    f"Test data is prepared",
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Prepare {http_method} request for {scenario_name}",
                        expected_result="Request payload constructed",
                    ),
                    TestStep(
                        step_number=2,
                        action=f"Send {http_method} request to {endpoint}",
                        expected_result="Response received from server",
                    ),
                    TestStep(
                        step_number=3,
                        action="Validate response status code",
                        expected_result=f"{'2xx success' if is_positive else '4xx/5xx error'} status code returned",
                    ),
                    TestStep(
                        step_number=4,
                        action="Validate response body structure and content",
                        expected_result="Response matches expected schema",
                    ),
                ],
                expected_result=f"API correctly handles {scenario_name}",
                tags=["api", http_method.lower(), "positive" if is_positive else "negative"],
                test_level=TestLevel.FT_API,
                testing_cycle=TestingCycle.SMOKE if priority == TestCasePriority.CRITICAL else TestingCycle.REGRESSION,
                component=ComponentType.API,
                testing_technique=TestingTechnique.EQUIVALENCE_PARTITIONING if not is_positive else TestingTechnique.USE_CASE,
                technique_rationale="EP partitions inputs into valid/invalid classes for comprehensive API testing" if not is_positive else "Use Case validates expected API behavior",
                labels=[self.default_label, feature_name.lower().replace(" ", "-"), "api"],
                is_smoke=priority == TestCasePriority.CRITICAL,
                is_regression=True,
            )
            test_cases.append(test_case)

        return test_cases

    def generate_state_transition_tests(
        self,
        feature_name: str,
        states: Optional[List[str]] = None,
        valid_transitions: Optional[Dict[str, List[str]]] = None,
        state_type: str = "user_session",
    ) -> List[TestCase]:
        """
        Generate state transition test cases.

        Args:
            feature_name: Name of the feature being tested
            states: List of possible states (optional, uses predefined if not provided)
            valid_transitions: Dict mapping state to valid next states
            state_type: Type of state machine to use from COMMON_STATE_TRANSITIONS

        Returns:
            List of state transition test cases
        """
        test_cases = []

        # Use provided transitions or default to common transitions
        if valid_transitions is None:
            if state_type in self.COMMON_STATE_TRANSITIONS:
                valid_transitions = self.COMMON_STATE_TRANSITIONS[state_type]
            else:
                return test_cases

        if states is None:
            states = list(valid_transitions.keys())

        # Generate valid transition tests
        for from_state, to_states in valid_transitions.items():
            for to_state in to_states:
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Validate that transition from {from_state} to {to_state} works",
                    description=f"State transition test: {from_state} → {to_state}",
                    test_type=TestCaseType.FUNCTIONAL,
                    priority=TestCasePriority.HIGH,
                    preconditions=[
                        f"System is in '{from_state}' state",
                        f"All prerequisites for transition are met",
                    ],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=f"Verify current state is '{from_state}'",
                            expected_result=f"System confirms state is '{from_state}'",
                        ),
                        TestStep(
                            step_number=2,
                            action=f"Trigger transition to '{to_state}'",
                            expected_result="Transition initiated",
                        ),
                        TestStep(
                            step_number=3,
                            action="Verify state change completed",
                            expected_result=f"System is now in '{to_state}' state",
                        ),
                    ],
                    expected_result=f"Valid transition from {from_state} to {to_state} succeeds",
                    tags=["state-transition", from_state, to_state],
                    test_level=TestLevel.FT_UI,
                    testing_cycle=TestingCycle.REGRESSION,
                    component=ComponentType.UI,
                    testing_technique=TestingTechnique.STATE_TRANSITION,
                    technique_rationale="State Transition Testing validates system behavior across different states",
                    labels=[self.default_label, feature_name.lower().replace(" ", "-")],
                    is_regression=True,
                )
                test_cases.append(test_case)

        # Generate invalid transition tests
        for from_state in states:
            valid_to_states = valid_transitions.get(from_state, [])
            invalid_to_states = [s for s in states if s not in valid_to_states and s != from_state]

            for to_state in invalid_to_states[:2]:  # Limit to 2 invalid transitions per state
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Validate that invalid transition from {from_state} to {to_state} is blocked",
                    description=f"Invalid state transition test: {from_state} → {to_state} (should fail)",
                    test_type=TestCaseType.NEGATIVE,
                    priority=TestCasePriority.MEDIUM,
                    preconditions=[
                        f"System is in '{from_state}' state",
                    ],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=f"Verify current state is '{from_state}'",
                            expected_result=f"System confirms state is '{from_state}'",
                        ),
                        TestStep(
                            step_number=2,
                            action=f"Attempt invalid transition to '{to_state}'",
                            expected_result="System rejects invalid transition",
                        ),
                        TestStep(
                            step_number=3,
                            action="Verify state unchanged",
                            expected_result=f"System remains in '{from_state}' state",
                        ),
                    ],
                    expected_result=f"Invalid transition from {from_state} to {to_state} is properly blocked",
                    tags=["state-transition", "negative", from_state, to_state],
                    test_level=TestLevel.FT_UI,
                    testing_cycle=TestingCycle.REGRESSION,
                    component=ComponentType.UI,
                    testing_technique=TestingTechnique.STATE_TRANSITION,
                    technique_rationale="State Transition Testing validates invalid transitions are blocked",
                    labels=[self.default_label, feature_name.lower().replace(" ", "-")],
                )
                test_cases.append(test_case)

        return test_cases

    def generate_field_specific_edge_cases(
        self,
        feature_name: str,
        field_type: str,
        field_name: str = "field",
    ) -> List[TestCase]:
        """
        Generate edge case tests specific to a field type.

        Args:
            feature_name: Name of the feature being tested
            field_type: Type of field (email, password, phone, date, numeric, url, file_upload)
            field_name: Name of the specific field

        Returns:
            List of field-specific edge case test cases
        """
        test_cases = []

        if field_type not in self.FIELD_SPECIFIC_EDGE_CASES:
            return test_cases

        scenarios = self.FIELD_SPECIFIC_EDGE_CASES[field_type]

        for scenario in scenarios:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Validate that {field_name} handles {scenario}",
                description=f"Field-specific edge case: {field_type} - {scenario}",
                test_type=TestCaseType.EDGE_CASE,
                priority=TestCasePriority.MEDIUM,
                preconditions=[f"User is on the {feature_name} page"],
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Enter {scenario} in {field_name} field",
                        expected_result="Input is accepted for validation",
                    ),
                    TestStep(
                        step_number=2,
                        action="Submit or validate the field",
                        expected_result="Validation executes",
                    ),
                    TestStep(
                        step_number=3,
                        action="Verify validation result",
                        expected_result="Appropriate validation message displayed",
                    ),
                ],
                expected_result=f"{field_name} correctly handles {scenario}",
                tags=["edge-case", field_type, scenario.replace(" ", "-").replace("/", "-")],
                test_level=TestLevel.FT_UI,
                testing_cycle=TestingCycle.REGRESSION,
                component=ComponentType.UI,
                testing_technique=TestingTechnique.ERROR_GUESSING,
                technique_rationale=f"Error Guessing predicts common {field_type} validation issues",
                labels=[self.default_label, feature_name.lower().replace(" ", "-")],
            )
            test_cases.append(test_case)

        return test_cases

    def generate_cross_browser_tests(self, feature_name: str) -> List[TestCase]:
        """
        Generate cross-browser/device test cases.

        Args:
            feature_name: Name of the feature being tested

        Returns:
            List of cross-browser test cases
        """
        test_cases = []

        for browser, device_type, priority in self.CROSS_BROWSER_SCENARIOS:
            test_case = TestCase(
                id=self._generate_test_id(),
                title=f"Validate that {feature_name} works on {browser} ({device_type})",
                description=f"Cross-browser test: {feature_name} on {browser}",
                test_type=TestCaseType.FUNCTIONAL,
                priority=priority,
                preconditions=[
                    f"{browser} browser is installed and configured",
                    f"Test device ({device_type}) is available",
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        action=f"Open {feature_name} in {browser} on {device_type}",
                        expected_result="Page loads correctly",
                    ),
                    TestStep(
                        step_number=2,
                        action="Verify layout and styling",
                        expected_result="UI renders correctly for this browser/device",
                    ),
                    TestStep(
                        step_number=3,
                        action="Test all interactive elements",
                        expected_result="All interactions work as expected",
                    ),
                    TestStep(
                        step_number=4,
                        action="Verify responsive behavior",
                        expected_result="Layout adapts correctly to screen size",
                    ),
                ],
                expected_result=f"{feature_name} works correctly on {browser} ({device_type})",
                tags=["cross-browser", browser.lower().replace(" ", "-"), device_type],
                test_level=TestLevel.E2E,
                testing_cycle=TestingCycle.REGRESSION,
                component=ComponentType.UI,
                testing_technique=TestingTechnique.PAIRWISE,
                technique_rationale="Pairwise testing covers browser/device combinations efficiently",
                labels=[self.default_label, feature_name.lower().replace(" ", "-"), "cross-browser"],
            )
            test_cases.append(test_case)

        return test_cases

    def generate_data_driven_tests(
        self,
        feature_name: str,
        input_fields: List[Dict[str, Any]],
    ) -> List[TestCase]:
        """
        Generate data-driven test cases based on input field specifications.

        Args:
            feature_name: Name of the feature being tested
            input_fields: List of field specifications with structure:
                {
                    "name": "field_name",
                    "type": "text|number|email|date|etc",
                    "required": True|False,
                    "min_length": int (optional),
                    "max_length": int (optional),
                    "min_value": number (optional),
                    "max_value": number (optional),
                    "pattern": "regex" (optional),
                    "valid_values": ["list", "of", "values"] (optional),
                }

        Returns:
            List of data-driven test cases
        """
        test_cases = []

        for field in input_fields:
            field_name = field.get("name", "field")
            field_type = field.get("type", "text")
            is_required = field.get("required", False)

            # Required field test
            if is_required:
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Validate that {field_name} is required",
                    description=f"Verify {field_name} cannot be empty when required",
                    test_type=TestCaseType.NEGATIVE,
                    priority=TestCasePriority.HIGH,
                    preconditions=[f"User is on the {feature_name} page"],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=f"Leave {field_name} empty",
                            expected_result="Field is empty",
                        ),
                        TestStep(
                            step_number=2,
                            action="Submit the form",
                            expected_result="Validation error displayed",
                        ),
                    ],
                    expected_result=f"Required field validation for {field_name} works correctly",
                    tags=["data-driven", "required", field_name.lower()],
                    test_level=TestLevel.FT_UI,
                    testing_cycle=TestingCycle.SMOKE,
                    component=ComponentType.UI,
                    testing_technique=TestingTechnique.EQUIVALENCE_PARTITIONING,
                    technique_rationale="EP validates required vs optional field behavior",
                    labels=[self.default_label, feature_name.lower().replace(" ", "-")],
                    test_data=[{"field": field_name, "value": "", "expected": "error"}],
                    is_smoke=True,
                )
                test_cases.append(test_case)

            # Length validation tests
            if "min_length" in field:
                min_len = field["min_length"]
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Validate that {field_name} minimum length is {min_len}",
                    description=f"Verify {field_name} rejects values shorter than {min_len} characters",
                    test_type=TestCaseType.BOUNDARY,
                    priority=TestCasePriority.HIGH,
                    preconditions=[f"User is on the {feature_name} page"],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=f"Enter {min_len - 1} characters in {field_name}",
                            expected_result="Input accepted",
                        ),
                        TestStep(
                            step_number=2,
                            action="Submit the form",
                            expected_result="Minimum length validation error",
                        ),
                    ],
                    expected_result=f"Minimum length validation for {field_name} works correctly",
                    tags=["data-driven", "min-length", field_name.lower()],
                    test_level=TestLevel.FT_UI,
                    testing_cycle=TestingCycle.REGRESSION,
                    component=ComponentType.UI,
                    testing_technique=TestingTechnique.BOUNDARY_VALUE_ANALYSIS,
                    technique_rationale="BVA tests minimum length boundary",
                    labels=[self.default_label, feature_name.lower().replace(" ", "-")],
                    test_data=[{"field": field_name, "value": "x" * (min_len - 1), "expected": "error"}],
                )
                test_cases.append(test_case)

            if "max_length" in field:
                max_len = field["max_length"]
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Validate that {field_name} maximum length is {max_len}",
                    description=f"Verify {field_name} rejects values longer than {max_len} characters",
                    test_type=TestCaseType.BOUNDARY,
                    priority=TestCasePriority.HIGH,
                    preconditions=[f"User is on the {feature_name} page"],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=f"Enter {max_len + 1} characters in {field_name}",
                            expected_result="Input accepted or truncated",
                        ),
                        TestStep(
                            step_number=2,
                            action="Submit the form",
                            expected_result="Maximum length validation triggers",
                        ),
                    ],
                    expected_result=f"Maximum length validation for {field_name} works correctly",
                    tags=["data-driven", "max-length", field_name.lower()],
                    test_level=TestLevel.FT_UI,
                    testing_cycle=TestingCycle.REGRESSION,
                    component=ComponentType.UI,
                    testing_technique=TestingTechnique.BOUNDARY_VALUE_ANALYSIS,
                    technique_rationale="BVA tests maximum length boundary",
                    labels=[self.default_label, feature_name.lower().replace(" ", "-")],
                    test_data=[{"field": field_name, "value": "x" * (max_len + 1), "expected": "error"}],
                )
                test_cases.append(test_case)

            # Valid values test (equivalence partitioning)
            if "valid_values" in field:
                valid_values = field["valid_values"]
                test_case = TestCase(
                    id=self._generate_test_id(),
                    title=f"Validate that {field_name} accepts valid values",
                    description=f"Verify {field_name} accepts: {', '.join(str(v) for v in valid_values[:3])}...",
                    test_type=TestCaseType.FUNCTIONAL,
                    priority=TestCasePriority.HIGH,
                    preconditions=[f"User is on the {feature_name} page"],
                    steps=[
                        TestStep(
                            step_number=1,
                            action=f"Enter a valid value from: {valid_values}",
                            expected_result="Value is accepted",
                        ),
                        TestStep(
                            step_number=2,
                            action="Submit the form",
                            expected_result="Form submits successfully",
                        ),
                    ],
                    expected_result=f"Valid values accepted for {field_name}",
                    tags=["data-driven", "valid-values", field_name.lower()],
                    test_level=TestLevel.FT_UI,
                    testing_cycle=TestingCycle.SMOKE,
                    component=ComponentType.UI,
                    testing_technique=TestingTechnique.EQUIVALENCE_PARTITIONING,
                    technique_rationale="EP tests valid value partitions",
                    labels=[self.default_label, feature_name.lower().replace(" ", "-")],
                    test_data=[{"field": field_name, "valid_values": valid_values}],
                    is_smoke=True,
                )
                test_cases.append(test_case)

            # Field type specific edge cases
            type_specific_tests = self.generate_field_specific_edge_cases(
                feature_name, field_type, field_name
            )
            test_cases.extend(type_specific_tests[:3])  # Limit to top 3 edge cases per field

        return test_cases

    def calculate_coverage_gaps(
        self,
        requirements: List[str],
        test_cases: List[TestCase],
    ) -> Dict[str, Any]:
        """
        Identify requirements without adequate test coverage.

        Args:
            requirements: List of requirement strings
            test_cases: List of generated test cases

        Returns:
            Coverage gap analysis
        """
        covered_requirements = set()
        for tc in test_cases:
            if tc.related_requirement:
                covered_requirements.add(tc.related_requirement)

        uncovered = [req for req in requirements if req not in covered_requirements]

        # Analyze coverage by test type
        type_coverage = {}
        for tc in test_cases:
            type_name = tc.test_type.value
            type_coverage[type_name] = type_coverage.get(type_name, 0) + 1

        # Identify missing test types
        all_types = {t.value for t in TestCaseType}
        covered_types = set(type_coverage.keys())
        missing_types = all_types - covered_types

        return {
            "totalRequirements": len(requirements),
            "coveredRequirements": len(covered_requirements),
            "uncoveredRequirements": uncovered,
            "coveragePercentage": (len(covered_requirements) / len(requirements) * 100) if requirements else 100,
            "testTypesCovered": list(covered_types),
            "testTypesMissing": list(missing_types),
            "recommendations": self._generate_coverage_recommendations(uncovered, missing_types),
        }

    def _generate_coverage_recommendations(
        self,
        uncovered: List[str],
        missing_types: set,
    ) -> List[str]:
        """Generate recommendations based on coverage gaps."""
        recommendations = []

        if uncovered:
            recommendations.append(f"Add test cases for {len(uncovered)} uncovered requirements")

        if "security" in missing_types:
            recommendations.append("Consider adding security test cases (SQL injection, XSS, etc.)")

        if "performance" in missing_types:
            recommendations.append("Consider adding performance test cases for critical features")

        if "accessibility" in missing_types:
            recommendations.append("Consider adding accessibility test cases (WCAG compliance)")

        if "boundary" in missing_types:
            recommendations.append("Add boundary value tests for numeric and text inputs")

        if "integration" in missing_types:
            recommendations.append("Add integration tests for component interactions")

        return recommendations

    def generate_test_suite(
        self,
        text: str,
        feature_name: str,
        include_all_types: bool = False,
        external_doc_links: Optional[List[str]] = None,
    ) -> TestSuite:
        """
        Generate a complete test suite from requirements text.

        Args:
            text: Text containing requirements or user stories
            feature_name: Name of the feature being tested
            include_all_types: Override settings to include all test types
            external_doc_links: Optional list of Figma/Confluence URLs to enrich requirements

        Returns:
            Complete test suite with all applicable test cases
        """
        # Enrich requirements with external documentation (Figma, Confluence)
        enriched_text, external_docs = enrich_requirements_with_external_docs(
            text,
            external_doc_links or []
        )

        # Log if external docs were found
        if external_docs:
            doc_types = [d["type"] for d in external_docs]
            logger.info(f"Enriched requirements with external docs: {doc_types}")

        # Extract requirements from enriched text
        requirements = self.extract_requirements(enriched_text)

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

        # Boundary tests
        if self.include_boundary or include_all_types:
            boundary_tests = self.generate_boundary_tests(feature_name)
            test_cases.extend(boundary_tests)
            coverage_areas.append("Boundary Value Analysis")

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

        # Integration tests
        if self.include_integration or include_all_types:
            integration_tests = self.generate_integration_tests(feature_name)
            test_cases.extend(integration_tests)
            coverage_areas.append("Integration (SIT)")

        # Performance tests
        if self.include_performance or include_all_types:
            performance_tests = self.generate_performance_tests(feature_name)
            test_cases.extend(performance_tests)
            coverage_areas.append("Performance")

        # API tests
        if self.include_api or include_all_types:
            api_tests = self.generate_api_tests(feature_name)
            test_cases.extend(api_tests)
            coverage_areas.append("API")

        # Cross-browser tests
        if self.include_cross_browser or include_all_types:
            browser_tests = self.generate_cross_browser_tests(feature_name)
            test_cases.extend(browser_tests)
            coverage_areas.append("Cross-Browser/Device")

        # Add default labels to all test cases
        for tc in test_cases:
            if self.default_label and self.default_label not in tc.labels:
                tc.labels.append(self.default_label)

        # Calculate coverage gaps
        requirement_texts = [req.get("context", "") for req in requirements]
        coverage_gaps = self.calculate_coverage_gaps(requirement_texts, test_cases)

        return TestSuite(
            name=f"{feature_name} Test Suite",
            description=f"Comprehensive test suite for {feature_name}",
            test_cases=test_cases,
            coverage_areas=coverage_areas,
            requirements=requirement_texts,
            coverage_gaps=coverage_gaps.get("uncoveredRequirements", []),
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
                    - include_performance: Whether to include performance tests
                    - include_integration: Whether to include integration tests
                    - include_api: Whether to include API tests
                    - include_cross_browser: Whether to include cross-browser tests
                    - include_all: Whether to include all test types
                    - input_fields: List of field specs for data-driven tests
                    - state_type: Type of state machine for state transition tests

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
            if input_data.get("include_performance"):
                self.include_performance = True
            if input_data.get("include_integration"):
                self.include_integration = True
            if input_data.get("include_api"):
                self.include_api = True
            if input_data.get("include_cross_browser"):
                self.include_cross_browser = True

            include_all = input_data.get("include_all", False)

            # Add acceptance criteria to requirements
            if acceptance_criteria:
                requirements_text += "\n" + "\n".join(
                    f"The system should {ac}" for ac in acceptance_criteria
                )

            # Generate test suite
            test_suite = self.generate_test_suite(requirements_text, feature_name, include_all)

            # Generate additional test types if requested
            additional_tests = []

            # Data-driven tests from field specifications
            input_fields = input_data.get("input_fields", [])
            if input_fields:
                data_driven = self.generate_data_driven_tests(feature_name, input_fields)
                additional_tests.extend(data_driven)

            # State transition tests
            state_type = input_data.get("state_type")
            if state_type:
                state_tests = self.generate_state_transition_tests(feature_name, state_type=state_type)
                additional_tests.extend(state_tests)

            # Add additional tests to suite
            if additional_tests:
                test_suite.test_cases.extend(additional_tests)

            # Build result
            result = TestCaseWritingResult(
                status="success",
                test_suites=[test_suite],
                total_test_cases=len(test_suite.test_cases),
                coverage_summary={
                    "areas": test_suite.coverage_areas,
                    "byType": test_suite._count_by_type(),
                    "byPriority": test_suite._count_by_priority(),
                    "byTestLevel": test_suite._count_by_test_level(),
                    "byTestingCycle": test_suite._count_by_testing_cycle(),
                    "byComponent": test_suite._count_by_component(),
                    "byTechnique": test_suite._count_by_technique(),
                    "priorityByLevelTable": test_suite.get_priority_level_table(),
                },
                recommendations=self._generate_coverage_recommendations(
                    test_suite.coverage_gaps,
                    set(TestCaseType.__members__.keys()) - {tc.test_type.name for tc in test_suite.test_cases}
                ),
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
    include_boundary: bool = True,
    include_integration: bool = False,
    include_performance: bool = False,
    include_api: bool = False,
    include_cross_browser: bool = False,
    include_all: bool = False,
    output_format: str = "structured",
    default_label: str = "qAIn",
    external_doc_links: Optional[List[str]] = None,
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
        include_boundary: Whether to include boundary value tests
        include_integration: Whether to include integration tests
        include_performance: Whether to include performance tests
        include_api: Whether to include API tests
        include_cross_browser: Whether to include cross-browser tests
        include_all: Whether to include all test types
        output_format: Output format (structured, gherkin, markdown)
        default_label: Default label to add to all test cases
        external_doc_links: Optional list of Figma/Confluence URLs for additional context

    Returns:
        Generated test cases with coverage summary
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
        include_boundary=include_boundary,
        include_integration=include_integration,
        include_performance=include_performance,
        include_api=include_api,
        include_cross_browser=include_cross_browser,
        default_label=default_label,
    )

    test_suite = agent.generate_test_suite(
        requirements,
        feature_name,
        include_all,
        external_doc_links=external_doc_links
    )

    return {
        "testSuite": test_suite.to_dict(),
        "formatted": agent.format_output(test_suite),
        "priorityLevelTable": test_suite.get_priority_level_table(),
        "traceabilityMatrix": test_suite._build_traceability_matrix(),
        "coverageMatrix": test_suite._build_coverage_matrix(),
    }


def generate_comprehensive_test_suite(
    requirements: str,
    feature_name: str,
    input_fields: Optional[List[Dict[str, Any]]] = None,
    state_type: Optional[str] = None,
    output_format: str = "gherkin",
) -> Dict[str, Any]:
    """
    Generate a comprehensive test suite with all test types.

    This function generates:
    - Functional tests from requirements
    - Negative/error handling tests
    - Boundary value tests
    - Edge case tests
    - Field-specific tests (if input_fields provided)
    - State transition tests (if state_type provided)
    - Accessibility tests
    - Security tests
    - Performance tests
    - API tests
    - Cross-browser tests

    Args:
        requirements: Text containing requirements or user stories
        feature_name: Name of the feature being tested
        input_fields: Optional list of field specifications for data-driven tests
        state_type: Optional state machine type (user_session, order_status, payment_status)
        output_format: Output format (structured, gherkin, markdown)

    Returns:
        Comprehensive test suite with all matrices and summaries
    """
    format_map = {
        "structured": TestCaseFormat.STRUCTURED,
        "gherkin": TestCaseFormat.GHERKIN,
        "markdown": TestCaseFormat.MARKDOWN,
    }

    agent = TestCaseWritingAgent(
        output_format=format_map.get(output_format, TestCaseFormat.GHERKIN),
        include_edge_cases=True,
        include_security=True,
        include_accessibility=True,
        include_boundary=True,
        include_integration=True,
        include_performance=True,
        include_api=True,
        include_cross_browser=True,
    )

    # Generate main test suite with all types
    test_suite = agent.generate_test_suite(requirements, feature_name, include_all_types=True)

    # Add data-driven tests if field specs provided
    if input_fields:
        data_driven_tests = agent.generate_data_driven_tests(feature_name, input_fields)
        test_suite.test_cases.extend(data_driven_tests)
        test_suite.coverage_areas.append("Data-Driven")

    # Add state transition tests if state type provided
    if state_type:
        state_tests = agent.generate_state_transition_tests(feature_name, state_type=state_type)
        test_suite.test_cases.extend(state_tests)
        test_suite.coverage_areas.append("State Transition")

    return {
        "testSuite": test_suite.to_dict(),
        "formatted": agent.format_output(test_suite),
        "priorityLevelTable": test_suite.get_priority_level_table(),
        "traceabilityMatrix": test_suite._build_traceability_matrix(),
        "coverageMatrix": test_suite._build_coverage_matrix(),
        "summary": {
            "totalTestCases": len(test_suite.test_cases),
            "coverageAreas": test_suite.coverage_areas,
            "byType": test_suite._count_by_type(),
            "byPriority": test_suite._count_by_priority(),
            "byTestLevel": test_suite._count_by_test_level(),
            "byTestingCycle": test_suite._count_by_testing_cycle(),
        },
    }


# ==================== JIRA Integration Functions ====================

def get_workflow_questions() -> List[Dict[str, Any]]:
    """
    Get questions to ask the user before generating test cases.

    Returns:
        List of questions in AskUserQuestion format
    """
    return [
        {
            "question": "What is the JIRA ticket ID for the story? (e.g., PANDORA-123)",
            "header": "Story ID",
            "options": [
                {"label": "Enter ticket ID", "description": "I'll type the JIRA ticket ID"},
            ],
            "multiSelect": False,
        },
        {
            "question": "Which types of testing do you need?",
            "header": "Test Types",
            "options": [
                {"label": "FT-UI", "description": "Functional Testing - UI"},
                {"label": "FT-API", "description": "Functional Testing - API"},
                {"label": "SIT", "description": "System Integration Testing"},
                {"label": "E2E", "description": "End-to-End Testing"},
                {"label": "UAT", "description": "User Acceptance Testing"},
                {"label": "A11Y", "description": "Accessibility Testing"},
                {"label": "Performance", "description": "Performance Testing"},
                {"label": "Security", "description": "Security Testing"},
            ],
            "multiSelect": True,
        },
        {
            "question": "What label should be used for the feature/module?",
            "header": "Feature Label",
            "options": [
                {"label": "Enter label", "description": "I'll type the feature/module name"},
            ],
            "multiSelect": False,
        },
    ]


def generate_coverage_comment(
    test_suite: TestSuite,
    story_key: str,
    created_keys: List[str],
) -> str:
    """
    Generate a detailed coverage comment for JIRA.

    Args:
        test_suite: Generated test suite
        story_key: JIRA story key
        created_keys: List of created test case keys

    Returns:
        Formatted comment string for JIRA
    """
    # Build priority x level table
    priority_table = test_suite.get_priority_level_table()

    # Build test type summary
    type_counts = test_suite._count_by_type()
    type_summary = "\n".join([f"- {t}: {c}" for t, c in type_counts.items()])

    # Build testing cycle summary
    cycle_counts = test_suite._count_by_testing_cycle()
    cycle_summary = "\n".join([f"- {c}: {n}" for c, n in cycle_counts.items()]) if cycle_counts else "- N/A"

    # Build traceability matrix
    traceability = test_suite._build_traceability_matrix()
    trace_rows = []
    for item in traceability[:10]:  # Limit to first 10 for readability
        trace_rows.append(f"| {item['testCaseId']} | {item['testCaseTitle'][:40]}... | {item['testLevel'] or 'N/A'} | {item['priority']} |")

    trace_table = """| Test Case ID | Title | Test Level | Priority |
|--------------|-------|------------|----------|
""" + "\n".join(trace_rows)

    if len(traceability) > 10:
        trace_table += f"\n\n*... and {len(traceability) - 10} more test cases*"

    # Build coverage matrix summary
    coverage = test_suite._build_coverage_matrix()

    comment = f"""{QAIN_SIGNATURE}

**Test Designing and Test Management Completed**

---

**Story:** {story_key}
**Total Test Cases Created:** {len(test_suite.test_cases)}
**Test Cases Linked:** {len(created_keys)}

---

## Test Case Summary by Priority x Test Level

{priority_table}

---

## Test Type Summary

{type_summary}

---

## Testing Cycle Summary

{cycle_summary}

---

## Traceability Matrix

{trace_table}

---

## Coverage Areas

{', '.join(test_suite.coverage_areas)}

---

## Created Test Cases

{', '.join(created_keys) if created_keys else 'Test cases generated but not created in JIRA'}

---

*Generated by qAIn - Your Junior Quality Engineer*
"""
    return comment


def generate_traceability_matrix_comment(test_suite: TestSuite, story_key: str) -> str:
    """
    Generate a traceability matrix comment for JIRA.

    Args:
        test_suite: Generated test suite
        story_key: JIRA story key

    Returns:
        Formatted traceability matrix comment
    """
    traceability = test_suite._build_traceability_matrix()

    rows = []
    for item in traceability:
        rows.append(
            f"| {item['testCaseId']} | {item['testCaseTitle'][:50]} | {item['requirement'] or story_key} | "
            f"{item['testType']} | {item['testLevel'] or 'N/A'} | {item['priority']} |"
        )

    table = """| Test Case ID | Title | Linked Requirement | Type | Level | Priority |
|--------------|-------|-------------------|------|-------|----------|
""" + "\n".join(rows)

    return f"""{QAIN_SIGNATURE}

**Traceability Matrix for {story_key}**

{table}

---

**Total Test Cases:** {len(traceability)}
"""


def generate_coverage_matrix_comment(test_suite: TestSuite, story_key: str) -> str:
    """
    Generate a coverage matrix comment for JIRA.

    Args:
        test_suite: Generated test suite
        story_key: JIRA story key

    Returns:
        Formatted coverage matrix comment
    """
    coverage = test_suite._build_coverage_matrix()
    priority_table = test_suite.get_priority_level_table()

    type_summary = coverage.get("testTypeSummary", {})
    cycle_summary = coverage.get("testingCycleSummary", {})

    type_rows = "\n".join([f"| {t} | {c} |" for t, c in type_summary.items()])
    cycle_rows = "\n".join([f"| {c} | {n} |" for c, n in cycle_summary.items()])

    return f"""{QAIN_SIGNATURE}

**Coverage Matrix for {story_key}**

## Priority x Test Level Distribution

{priority_table}

## Test Type Distribution

| Test Type | Count |
|-----------|-------|
{type_rows}

## Testing Cycle Distribution

| Cycle | Count |
|-------|-------|
{cycle_rows}

---

**Coverage Areas:** {', '.join(test_suite.coverage_areas)}
"""


async def create_jira_test_cases(
    test_suite: TestSuite,
    config: JiraWorkflowConfig,
    jira_client: Any,
) -> JiraTestCaseCreationResult:
    """
    Create test cases in JIRA and link them to the story.

    Args:
        test_suite: Generated test suite
        config: JIRA workflow configuration
        jira_client: JIRA client instance

    Returns:
        Result of test case creation
    """
    result = JiraTestCaseCreationResult()

    # Get existing test cases to avoid duplicates
    existing_tests = jira_client.search_test_cases(
        project_key=config.project_key,
        labels=[config.feature_label] if config.feature_label else None,
    )
    existing_summaries = {tc.summary for tc in existing_tests}

    for test_case in test_suite.test_cases:
        try:
            # Check for duplicate
            if test_case.title in existing_summaries:
                result.skipped_count += 1
                result.skipped_keys.append(test_case.title[:50])
                logger.info(f"Skipping duplicate test case: {test_case.title[:50]}")
                continue

            # Build labels
            labels = list(test_case.labels) if test_case.labels else []
            if config.feature_label and config.feature_label not in labels:
                labels.append(config.feature_label)
            if "qAIn" not in labels:
                labels.append("qAIn")

            # Build component list
            components = []
            if test_case.component:
                components.append(test_case.component.value)

            # Map priority
            priority_map = {
                "critical": "Highest",
                "high": "High",
                "medium": "Medium",
                "low": "Low",
            }
            priority = priority_map.get(test_case.priority.value, "Medium")

            # Create test case in JIRA
            if config.create_in_jira:
                jira_issue = jira_client.create_test_case(
                    project_key=config.project_key,
                    summary=test_case.title,
                    description=test_case.to_gherkin(),
                    labels=labels,
                    priority=priority,
                    components=components if components else None,
                    test_type="Functional" if test_case.test_type in [
                        TestCaseType.FUNCTIONAL, TestCaseType.NEGATIVE,
                        TestCaseType.EDGE_CASE, TestCaseType.BOUNDARY,
                        TestCaseType.INTEGRATION
                    ] else "Non-Functional",
                    test_level=test_case.test_level.value if test_case.test_level else None,
                    testing_cycle=test_case.testing_cycle.value if test_case.testing_cycle else None,
                )

                if jira_issue:
                    result.created_count += 1
                    result.created_keys.append(jira_issue.key)

                    # Link to story
                    if config.link_to_story:
                        linked = jira_client.link_issues(
                            inward_issue=jira_issue.key,
                            outward_issue=config.story_key,
                            link_type="Tests",
                        )
                        if linked:
                            result.linked_count += 1
                else:
                    result.failed_count += 1
                    result.errors.append(f"Failed to create: {test_case.title[:50]}")
            else:
                # Dry run - just count
                result.created_count += 1
                result.created_keys.append(test_case.id)

        except Exception as e:
            result.failed_count += 1
            result.errors.append(f"Error creating {test_case.title[:30]}: {str(e)}")
            logger.error(f"Failed to create test case: {e}")

    return result


def run_jira_workflow(
    story_key: str,
    requirements: str,
    feature_name: str,
    test_types: List[str],
    jira_client: Optional[Any] = None,
    create_in_jira: bool = False,
    external_doc_links: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Run the complete JIRA test case workflow.

    Args:
        story_key: JIRA story key (e.g., "PANDORA-123")
        requirements: Requirements text or acceptance criteria
        feature_name: Name of the feature being tested
        test_types: List of test types to generate (FT-UI, FT-API, SIT, E2E, etc.)
        jira_client: Optional JIRA client instance
        create_in_jira: Whether to actually create test cases in JIRA
        external_doc_links: Optional list of Figma/Confluence URLs for additional context

    Returns:
        Workflow result with test suite and JIRA comments
    """
    # Parse project key from story key
    project_key = story_key.split("-")[0] if "-" in story_key else "PANDORA"

    # Create workflow config
    config = JiraWorkflowConfig(
        project_key=project_key,
        story_key=story_key,
        test_types=test_types,
        include_functional="FT-UI" in test_types or "Functional" in test_types,
        include_api="FT-API" in test_types or "API" in test_types,
        include_sit="SIT" in test_types,
        include_e2e="E2E" in test_types,
        include_uat="UAT" in test_types,
        include_a11y="A11Y" in test_types or "Accessibility" in test_types,
        include_performance="Performance" in test_types,
        include_security="Security" in test_types,
        feature_label=feature_name.lower().replace(" ", "-"),
        create_in_jira=create_in_jira and jira_client is not None,
        link_to_story=create_in_jira and jira_client is not None,
    )

    # Create agent with appropriate settings
    agent = TestCaseWritingAgent(
        output_format=TestCaseFormat.GHERKIN,
        include_edge_cases=True,
        include_security=config.include_security,
        include_accessibility=config.include_a11y,
        include_boundary=True,
        include_integration=config.include_sit,
        include_performance=config.include_performance,
        include_api=config.include_api,
        include_cross_browser=config.include_e2e,
        default_label="qAIn",
    )

    # Generate test suite (enriched with external documentation if provided)
    test_suite = agent.generate_test_suite(
        requirements,
        feature_name,
        include_all_types=False,
        external_doc_links=external_doc_links
    )

    # Generate JIRA comments
    coverage_comment = generate_coverage_comment(test_suite, story_key, [])
    traceability_comment = generate_traceability_matrix_comment(test_suite, story_key)
    coverage_matrix_comment = generate_coverage_matrix_comment(test_suite, story_key)

    result = {
        "status": "success",
        "story_key": story_key,
        "test_suite": test_suite.to_dict(),
        "formatted_test_cases": agent.format_output(test_suite),
        "total_test_cases": len(test_suite.test_cases),
        "coverage_areas": test_suite.coverage_areas,
        "jira_comments": {
            "coverage": coverage_comment,
            "traceability_matrix": traceability_comment,
            "coverage_matrix": coverage_matrix_comment,
        },
        "summary": {
            "byType": test_suite._count_by_type(),
            "byPriority": test_suite._count_by_priority(),
            "byTestLevel": test_suite._count_by_test_level(),
            "byTestingCycle": test_suite._count_by_testing_cycle(),
        },
        "priority_level_table": test_suite.get_priority_level_table(),
    }

    # Create in JIRA if configured
    if config.create_in_jira and jira_client:
        import asyncio
        creation_result = asyncio.run(create_jira_test_cases(test_suite, config, jira_client))
        result["jira_creation"] = {
            "created": creation_result.created_count,
            "linked": creation_result.linked_count,
            "skipped": creation_result.skipped_count,
            "failed": creation_result.failed_count,
            "created_keys": creation_result.created_keys,
            "errors": creation_result.errors,
        }

        # Update coverage comment with actual keys
        result["jira_comments"]["coverage"] = generate_coverage_comment(
            test_suite, story_key, creation_result.created_keys
        )

    return result
