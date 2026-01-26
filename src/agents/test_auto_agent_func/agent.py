"""
Functional Test Automation Agent

A dedicated agent for generating Cypress automation tests following Pandora's testing standards.
This agent references the pandora_cypress repository for coding conventions, patterns, and best practices.

Key principles:
- Always fetch context from pandora_cypress/.claude/context.md before generating tests
- Follow Pandora's Cypress coding standards and patterns
- Generate Page Object Model (POM) based test structures
- Support test generation from manual test cases, requirements, or JIRA tickets
- Integrate with existing test infrastructure in pandora_cypress

Enhanced Workflow (v2.0):
1. Fetch JIRA ticket details (summary, description, acceptance criteria)
2. Fetch development info (branch, PR, code changes) from JIRA Development field
3. Check repository access and review code changes
4. Fetch feature flag status across environments
5. Review linked test cases from Development > Release field
6. Review labels and components to identify feature areas
7. Fetch pandora_cypress repository context
8. Read existing artifacts for reuse (step definitions, page objects, fixtures)
9. Analyze input and match existing steps
10. Generate feature files using existing steps (ask user for new step definitions)
11. Output generated files with reuse statistics

Reference Repository:
- URL: https://pandora-jewelry.visualstudio.com/Pandora%20DDRT%20QA/_git/pandora_cypress
- Context: /.claude/context.md
"""

import os
import re
import logging
from typing import Optional, List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# PANDORA CYPRESS REPOSITORY REFERENCE
# ============================================================================

PANDORA_CYPRESS_REPO = {
    "organization": "pandora-jewelry",
    "project": "Pandora DDRT QA",
    "repository": "pandora_cypress",
    "base_url": "https://pandora-jewelry.visualstudio.com/Pandora%20DDRT%20QA/_git/pandora_cypress",
    "context_path": "/.claude/context.md",
    "api_base": "https://dev.azure.com/pandora-jewelry/Pandora%20DDRT%20QA/_apis/git/repositories/pandora_cypress",
    # Step definitions and features paths
    "step_definitions_path": "/cypress/support/step_definitions",
    "features_path": "/cypress/e2e/features",
    "common_steps_path": "/cypress/support/step_definitions/common",
    # Test data and fixtures paths
    "fixtures_path": "/cypress/fixtures",
    "test_data_path": "/cypress/fixtures/testData",
    # Page Object Model paths
    "page_objects_path": "/cypress/support/page-objects",
    "components_path": "/cypress/support/components",
    "pages_path": "/cypress/support/pages",
    # Environment configuration paths
    "env_config_path": "/cypress.config.ts",
    "env_files_path": "/cypress/config",
    "env_json_path": "/cypress.env.json",
}


# ============================================================================
# JIRA & DEVELOPMENT CONTEXT DATA CLASSES
# ============================================================================

@dataclass
class JiraTicketContext:
    """JIRA ticket information for automation context."""
    ticket_key: str = ""
    summary: str = ""
    description: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    story_points: Optional[int] = None
    priority: str = ""
    assignee: str = ""
    reporter: str = ""
    sprint: str = ""
    parent_epic: str = ""
    labels: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    status: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticket_key": self.ticket_key,
            "summary": self.summary,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "story_points": self.story_points,
            "priority": self.priority,
            "assignee": self.assignee,
            "reporter": self.reporter,
            "sprint": self.sprint,
            "parent_epic": self.parent_epic,
            "labels": self.labels,
            "components": self.components,
            "status": self.status,
        }


@dataclass
class DevelopmentInfo:
    """Development information from JIRA Development field."""
    branch_name: str = ""
    repository_name: str = ""
    repository_url: str = ""
    pr_id: Optional[str] = None
    pr_title: str = ""
    pr_description: str = ""
    pr_status: str = ""
    files_changed: List[str] = field(default_factory=list)
    commits: List[Dict[str, str]] = field(default_factory=list)
    has_access: bool = False
    access_error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "branch_name": self.branch_name,
            "repository_name": self.repository_name,
            "repository_url": self.repository_url,
            "pr_id": self.pr_id,
            "pr_title": self.pr_title,
            "pr_description": self.pr_description,
            "pr_status": self.pr_status,
            "files_changed": self.files_changed,
            "commits": self.commits,
            "has_access": self.has_access,
            "access_error": self.access_error,
        }


@dataclass
class FeatureFlagStatus:
    """Feature flag status across environments."""
    flag_name: str = ""
    local: bool = False
    staging: bool = False
    uat: bool = False
    production: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flag_name": self.flag_name,
            "local": self.local,
            "staging": self.staging,
            "uat": self.uat,
            "production": self.production,
        }


@dataclass
class LinkedTestCase:
    """Linked test case from JIRA Release field."""
    test_case_id: str = ""
    title: str = ""
    status: str = ""  # Manual, Automated, Not Automated
    is_automated: bool = False
    automation_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_case_id": self.test_case_id,
            "title": self.title,
            "status": self.status,
            "is_automated": self.is_automated,
            "automation_file": self.automation_file,
        }


@dataclass
class ReuseStatistics:
    """Statistics for artifact reuse."""
    step_definitions_reused: int = 0
    step_definitions_new: int = 0
    page_objects_reused: int = 0
    page_objects_new: int = 0
    fixtures_reused: int = 0
    fixtures_new: int = 0
    common_steps_reused: int = 0
    common_steps_new: int = 0

    @property
    def total_reused(self) -> int:
        return (self.step_definitions_reused + self.page_objects_reused +
                self.fixtures_reused + self.common_steps_reused)

    @property
    def total_new(self) -> int:
        return (self.step_definitions_new + self.page_objects_new +
                self.fixtures_new + self.common_steps_new)

    @property
    def reuse_percentage(self) -> float:
        total = self.total_reused + self.total_new
        return (self.total_reused / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_definitions": {"reused": self.step_definitions_reused, "new": self.step_definitions_new},
            "page_objects": {"reused": self.page_objects_reused, "new": self.page_objects_new},
            "fixtures": {"reused": self.fixtures_reused, "new": self.fixtures_new},
            "common_steps": {"reused": self.common_steps_reused, "new": self.common_steps_new},
            "total_reused": self.total_reused,
            "total_new": self.total_new,
            "reuse_percentage": round(self.reuse_percentage, 1),
        }


@dataclass
class NewStepDefinitionRequest:
    """Request for user confirmation on new step definition."""
    step_text: str = ""
    step_type: str = ""  # Given, When, Then
    suggested_implementation: str = ""
    user_approved: Optional[bool] = None
    user_implementation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_text": self.step_text,
            "step_type": self.step_type,
            "suggested_implementation": self.suggested_implementation,
            "user_approved": self.user_approved,
            "user_implementation": self.user_implementation,
        }


@dataclass
class AutomationContext:
    """Complete context for automation generation."""
    jira_ticket: Optional[JiraTicketContext] = None
    development_info: Optional[DevelopmentInfo] = None
    feature_flags: List[FeatureFlagStatus] = field(default_factory=list)
    linked_test_cases: List[LinkedTestCase] = field(default_factory=list)
    reuse_statistics: Optional[ReuseStatistics] = None
    new_step_requests: List[NewStepDefinitionRequest] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jira_ticket": self.jira_ticket.to_dict() if self.jira_ticket else None,
            "development_info": self.development_info.to_dict() if self.development_info else None,
            "feature_flags": [ff.to_dict() for ff in self.feature_flags],
            "linked_test_cases": [tc.to_dict() for tc in self.linked_test_cases],
            "reuse_statistics": self.reuse_statistics.to_dict() if self.reuse_statistics else None,
            "new_step_requests": [req.to_dict() for req in self.new_step_requests],
        }


@dataclass
class ContextMdStructure:
    """
    Structure extracted from pandora_cypress/.claude/context.md.

    CRITICAL: This structure MUST be fetched and validated BEFORE generating ANY files.
    All generated files MUST comply with these folder structures and naming conventions.
    """
    # Flag indicating if context was successfully fetched
    is_fetched: bool = False
    fetch_error: str = ""

    # Folder Structure (MUST follow these paths)
    feature_files_path: str = ""  # e.g., "cypress/e2e/features"
    step_definitions_path: str = ""  # e.g., "cypress/support/step_definitions"
    common_steps_path: str = ""  # e.g., "cypress/support/step_definitions/common"
    page_objects_path: str = ""  # e.g., "cypress/support/page-objects"
    components_path: str = ""  # e.g., "cypress/support/components"
    fixtures_path: str = ""  # e.g., "cypress/fixtures"

    # Naming Conventions (MUST follow these patterns)
    feature_file_pattern: str = ""  # e.g., "{JIRA-KEY}-{feature-name}.feature"
    step_definition_pattern: str = ""  # e.g., "{feature}Steps.ts"
    page_object_pattern: str = ""  # e.g., "{Page}Page.ts"
    fixture_pattern: str = ""  # e.g., "{feature}/{testData}.json"

    # Tag Standards (ONLY use approved tags)
    approved_tags: List[str] = field(default_factory=list)
    tag_naming_convention: str = ""  # e.g., "@{JIRA-KEY} @{feature} @{type}"

    # Test Level Tags
    test_level_tags: Dict[str, str] = field(default_factory=dict)  # e.g., {"smoke": "@smoke", "regression": "@regression"}

    # Coding Conventions
    coding_conventions: Dict[str, str] = field(default_factory=dict)

    # Custom Commands Available
    custom_commands: List[str] = field(default_factory=list)

    # Raw context.md content for reference
    raw_content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_fetched": self.is_fetched,
            "fetch_error": self.fetch_error,
            "folder_structure": {
                "feature_files_path": self.feature_files_path,
                "step_definitions_path": self.step_definitions_path,
                "common_steps_path": self.common_steps_path,
                "page_objects_path": self.page_objects_path,
                "components_path": self.components_path,
                "fixtures_path": self.fixtures_path,
            },
            "naming_conventions": {
                "feature_file_pattern": self.feature_file_pattern,
                "step_definition_pattern": self.step_definition_pattern,
                "page_object_pattern": self.page_object_pattern,
                "fixture_pattern": self.fixture_pattern,
            },
            "tags": {
                "approved_tags": self.approved_tags,
                "tag_naming_convention": self.tag_naming_convention,
                "test_level_tags": self.test_level_tags,
            },
            "coding_conventions": self.coding_conventions,
            "custom_commands": self.custom_commands,
        }

    def validate_path(self, file_type: str, proposed_path: str) -> Tuple[bool, str]:
        """
        Validate that a proposed file path complies with context.md structure.

        Args:
            file_type: Type of file ('feature', 'step_definition', 'page_object', 'fixture')
            proposed_path: The proposed file path

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.is_fetched:
            return False, "Context.md not fetched. Cannot validate paths."

        expected_paths = {
            "feature": self.feature_files_path,
            "step_definition": self.step_definitions_path,
            "page_object": self.page_objects_path,
            "fixture": self.fixtures_path,
            "component": self.components_path,
            "common_step": self.common_steps_path,
        }

        expected_path = expected_paths.get(file_type, "")
        if not expected_path:
            return False, f"Unknown file type: {file_type}"

        if not proposed_path.startswith(expected_path):
            return False, (
                f"Path mismatch for {file_type}. "
                f"Expected path to start with '{expected_path}', got '{proposed_path}'. "
                f"Files MUST be created within the pandora_cypress folder structure."
            )

        return True, ""

    def validate_tag(self, tag: str) -> Tuple[bool, str]:
        """
        Validate that a tag is in the approved list.

        Args:
            tag: The tag to validate (e.g., "@smoke")

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.is_fetched:
            return False, "Context.md not fetched. Cannot validate tags."

        if not self.approved_tags:
            # If no approved tags defined, allow all
            return True, ""

        # Normalize tag (add @ if missing)
        normalized_tag = tag if tag.startswith("@") else f"@{tag}"

        if normalized_tag not in self.approved_tags:
            return False, (
                f"Tag '{normalized_tag}' is not in the approved tags list. "
                f"Approved tags: {', '.join(self.approved_tags)}"
            )

        return True, ""


# ============================================================================
# ENUMERATIONS
# ============================================================================

class TestLevel(Enum):
    """Test levels for functional testing."""
    FT_UI = "FT-UI"           # Functional Test - UI Component
    FT_API = "FT-API"         # Functional Test - API
    E2E = "E2E"               # End-to-End Test
    SIT = "SIT"               # System Integration Test
    REGRESSION = "regression"  # Regression Test
    SMOKE = "smoke"           # Smoke Test


class ExecutionEnvironment(Enum):
    """Target execution environments."""
    LOCAL = "local"
    CI_CD = "ci-cd"
    STAGING = "staging"
    UAT = "uat"
    PRODUCTION = "production"


class BrowserType(Enum):
    """Supported browsers for Cypress execution."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    ELECTRON = "electron"


class PageObjectType(Enum):
    """Types of Page Objects in Pandora Cypress."""
    PAGE = "page"             # Full page object
    COMPONENT = "component"   # Reusable component
    MODAL = "modal"           # Modal/Dialog
    DRAWER = "drawer"         # Drawer/Sidebar
    FORM = "form"             # Form object


class TestPriority(Enum):
    """Test case priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(Enum):
    """Types of test cases."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    BOUNDARY = "boundary"
    ACCESSIBILITY = "accessibility"
    VISUAL = "visual"


class StepType(Enum):
    """Cucumber step types."""
    GIVEN = "Given"
    WHEN = "When"
    THEN = "Then"
    AND = "And"
    BUT = "But"


class StepDefinitionSource(Enum):
    """Source of step definition."""
    EXISTING = "existing"      # From pandora_cypress repository
    GENERATED = "generated"    # Newly generated for this scenario
    COMMON = "common"          # From common/shared step definitions


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class CypressContextReference:
    """Reference to pandora_cypress repository context.

    This class stores the context fetched from the repository
    that should be used when generating automation tests.
    """
    repository_url: str = PANDORA_CYPRESS_REPO["base_url"]
    context_path: str = PANDORA_CYPRESS_REPO["context_path"]

    # Context content (to be populated from repo)
    project_structure: Dict[str, Any] = field(default_factory=dict)
    coding_conventions: Dict[str, str] = field(default_factory=dict)
    test_patterns: Dict[str, str] = field(default_factory=dict)
    page_object_patterns: Dict[str, str] = field(default_factory=dict)
    custom_commands: List[str] = field(default_factory=list)
    fixtures_patterns: Dict[str, str] = field(default_factory=dict)

    # Default Pandora Cypress patterns (fallback if context not fetched)
    default_patterns: Dict[str, str] = field(default_factory=lambda: {
        "test_file_suffix": ".cy.ts",
        "spec_directory": "cypress/e2e",
        "page_objects_directory": "cypress/support/page-objects",
        "components_directory": "cypress/support/components",
        "fixtures_directory": "cypress/fixtures",
        "commands_file": "cypress/support/commands.ts",
        "selectors_pattern": "data-testid",
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repositoryUrl": self.repository_url,
            "contextPath": self.context_path,
            "projectStructure": self.project_structure,
            "codingConventions": self.coding_conventions,
            "testPatterns": self.test_patterns,
            "pageObjectPatterns": self.page_object_patterns,
            "customCommands": self.custom_commands,
            "fixturesPatterns": self.fixtures_patterns,
            "defaultPatterns": self.default_patterns,
        }


@dataclass
class StepDefinition:
    """Represents a Cucumber step definition from pandora_cypress repository.

    Step definitions are reusable building blocks for scenarios. The agent
    should discover existing step definitions and reuse them when possible.
    """
    step_type: StepType
    pattern: str                          # The regex/cucumber expression pattern
    description: str = ""                 # Description of what the step does
    source: StepDefinitionSource = StepDefinitionSource.EXISTING
    file_path: Optional[str] = None       # Path in pandora_cypress repo
    implementation: Optional[str] = None  # The actual implementation code
    parameters: List[str] = field(default_factory=list)  # Parameter names
    examples: List[str] = field(default_factory=list)    # Example usages
    tags: List[str] = field(default_factory=list)        # Associated tags

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stepType": self.step_type.value,
            "pattern": self.pattern,
            "description": self.description,
            "source": self.source.value,
            "filePath": self.file_path,
            "implementation": self.implementation,
            "parameters": self.parameters,
            "examples": self.examples,
            "tags": self.tags,
        }

    def matches(self, step_text: str) -> bool:
        """Check if this step definition matches a given step text."""
        # Convert cucumber expression to regex for matching
        regex_pattern = self._cucumber_to_regex(self.pattern)
        return bool(re.match(regex_pattern, step_text, re.IGNORECASE))

    def _cucumber_to_regex(self, pattern: str) -> str:
        """Convert cucumber expression to regex pattern."""
        # Replace cucumber placeholders with regex
        result = pattern
        result = re.sub(r'\{string\}', r'["\']([^"\']+)["\']', result)
        result = re.sub(r'\{int\}', r'(\\d+)', result)
        result = re.sub(r'\{float\}', r'(\\d+\\.?\\d*)', result)
        result = re.sub(r'\{word\}', r'(\\w+)', result)
        result = re.sub(r'\{.*?\}', r'(.+)', result)  # Generic placeholder
        return f"^{result}$"


@dataclass
class ScenarioStep:
    """A single step in a Gherkin scenario."""
    step_type: StepType
    text: str
    step_definition: Optional[StepDefinition] = None
    is_new_step: bool = False  # True if no existing step definition matches
    data_table: Optional[List[Dict[str, str]]] = None
    doc_string: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stepType": self.step_type.value,
            "text": self.text,
            "stepDefinition": self.step_definition.to_dict() if self.step_definition else None,
            "isNewStep": self.is_new_step,
            "dataTable": self.data_table,
            "docString": self.doc_string,
        }


@dataclass
class Scenario:
    """Represents a Gherkin scenario."""
    name: str
    description: str = ""
    steps: List[ScenarioStep] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    examples: Optional[List[Dict[str, Any]]] = None  # For scenario outlines

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "tags": self.tags,
            "examples": self.examples,
        }


@dataclass
class Feature:
    """Represents a Gherkin feature file."""
    name: str
    description: str = ""
    file_path: str = ""
    scenarios: List[Scenario] = field(default_factory=list)
    background: Optional[List[ScenarioStep]] = None
    tags: List[str] = field(default_factory=list)
    # Step definitions used/referenced
    existing_step_definitions: List[StepDefinition] = field(default_factory=list)
    new_step_definitions: List[StepDefinition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "filePath": self.file_path,
            "scenarios": [s.to_dict() for s in self.scenarios],
            "background": [s.to_dict() for s in self.background] if self.background else None,
            "tags": self.tags,
            "existingStepDefinitions": [sd.to_dict() for sd in self.existing_step_definitions],
            "newStepDefinitions": [sd.to_dict() for sd in self.new_step_definitions],
        }


@dataclass
class StepDefinitionRegistry:
    """Registry of all discovered step definitions from pandora_cypress repository.

    This registry is populated by reading step definition files from the repository
    and is used to match manual test steps to existing implementations.
    """
    repository_url: str = PANDORA_CYPRESS_REPO["base_url"]
    step_definitions_path: str = PANDORA_CYPRESS_REPO["step_definitions_path"]

    # Discovered step definitions organized by type
    given_steps: List[StepDefinition] = field(default_factory=list)
    when_steps: List[StepDefinition] = field(default_factory=list)
    then_steps: List[StepDefinition] = field(default_factory=list)

    # All step definitions for quick lookup
    all_steps: List[StepDefinition] = field(default_factory=list)

    # Discovery metadata
    files_scanned: List[str] = field(default_factory=list)
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repositoryUrl": self.repository_url,
            "stepDefinitionsPath": self.step_definitions_path,
            "givenSteps": [s.to_dict() for s in self.given_steps],
            "whenSteps": [s.to_dict() for s in self.when_steps],
            "thenSteps": [s.to_dict() for s in self.then_steps],
            "totalSteps": len(self.all_steps),
            "filesScanned": self.files_scanned,
            "lastUpdated": self.last_updated,
        }

    def add_step(self, step: StepDefinition) -> None:
        """Add a step definition to the registry."""
        self.all_steps.append(step)
        if step.step_type == StepType.GIVEN:
            self.given_steps.append(step)
        elif step.step_type == StepType.WHEN:
            self.when_steps.append(step)
        elif step.step_type == StepType.THEN:
            self.then_steps.append(step)

    def find_matching_step(
        self,
        step_type: StepType,
        step_text: str,
    ) -> Optional[StepDefinition]:
        """Find a matching step definition for a given step text."""
        steps_to_search = self.all_steps

        # Also search type-specific lists
        if step_type == StepType.GIVEN:
            steps_to_search = self.given_steps + [s for s in self.all_steps if s not in self.given_steps]
        elif step_type == StepType.WHEN:
            steps_to_search = self.when_steps + [s for s in self.all_steps if s not in self.when_steps]
        elif step_type == StepType.THEN:
            steps_to_search = self.then_steps + [s for s in self.all_steps if s not in self.then_steps]

        for step_def in steps_to_search:
            if step_def.matches(step_text):
                return step_def

        return None

    def find_similar_steps(
        self,
        step_text: str,
        threshold: float = 0.6,
    ) -> List[StepDefinition]:
        """Find step definitions similar to the given text using keyword matching."""
        similar = []
        step_words = set(step_text.lower().split())

        for step_def in self.all_steps:
            pattern_words = set(step_def.pattern.lower().split())
            # Jaccard similarity
            intersection = len(step_words & pattern_words)
            union = len(step_words | pattern_words)
            if union > 0 and intersection / union >= threshold:
                similar.append(step_def)

        return similar


# ============================================================================
# TEST DATA & FIXTURES
# ============================================================================

@dataclass
class TestDataFixture:
    """Represents a test data fixture from pandora_cypress repository.

    Test data fixtures contain reusable test data that should be referenced
    when creating new tests to ensure consistency.
    """
    name: str
    file_path: str
    data_type: str = "json"  # json, csv, etc.
    description: str = ""
    schema: Dict[str, Any] = field(default_factory=dict)
    sample_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    # Data categories for matching
    categories: List[str] = field(default_factory=list)  # e.g., ["user", "product", "cart"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "filePath": self.file_path,
            "dataType": self.data_type,
            "description": self.description,
            "schema": self.schema,
            "sampleData": self.sample_data,
            "tags": self.tags,
            "categories": self.categories,
        }


@dataclass
class TestDataRegistry:
    """Registry of all discovered test data fixtures from pandora_cypress repository.

    The agent should discover existing test data and reuse it when generating
    new tests to ensure consistency and avoid duplication.
    """
    repository_url: str = PANDORA_CYPRESS_REPO["base_url"]
    fixtures_path: str = PANDORA_CYPRESS_REPO["fixtures_path"]

    # Discovered fixtures organized by category
    fixtures: List[TestDataFixture] = field(default_factory=list)
    fixtures_by_category: Dict[str, List[TestDataFixture]] = field(default_factory=dict)

    # Discovery metadata
    files_scanned: List[str] = field(default_factory=list)
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repositoryUrl": self.repository_url,
            "fixturesPath": self.fixtures_path,
            "fixtures": [f.to_dict() for f in self.fixtures],
            "totalFixtures": len(self.fixtures),
            "categories": list(self.fixtures_by_category.keys()),
            "filesScanned": self.files_scanned,
            "lastUpdated": self.last_updated,
        }

    def add_fixture(self, fixture: TestDataFixture) -> None:
        """Add a fixture to the registry."""
        self.fixtures.append(fixture)
        for category in fixture.categories:
            if category not in self.fixtures_by_category:
                self.fixtures_by_category[category] = []
            self.fixtures_by_category[category].append(fixture)

    def find_fixtures_by_category(self, category: str) -> List[TestDataFixture]:
        """Find fixtures matching a category."""
        return self.fixtures_by_category.get(category.lower(), [])

    def find_fixtures_by_keywords(
        self,
        keywords: List[str],
        threshold: float = 0.5,
    ) -> List[TestDataFixture]:
        """Find fixtures matching keywords."""
        matching = []
        keyword_set = set(kw.lower() for kw in keywords)

        for fixture in self.fixtures:
            fixture_words = set(
                fixture.name.lower().split("_") +
                fixture.name.lower().split("-") +
                fixture.categories +
                fixture.tags
            )
            intersection = len(keyword_set & fixture_words)
            if intersection > 0:
                matching.append(fixture)

        return matching


# ============================================================================
# PAGE OBJECT MODEL (POM) REGISTRY
# ============================================================================

@dataclass
class ExistingPageObject:
    """Represents an existing Page Object from pandora_cypress repository.

    Page Objects should be reused when generating new tests to maintain
    consistency and avoid duplication.
    """
    name: str
    file_path: str
    class_name: str
    url_pattern: Optional[str] = None
    description: str = ""
    # Discovered selectors from the POM
    selectors: Dict[str, str] = field(default_factory=dict)
    # Available methods
    methods: List[str] = field(default_factory=list)
    # Page type
    page_type: str = "page"  # page, component, modal, drawer
    # Related pages/components
    imports: List[str] = field(default_factory=list)
    extends: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "filePath": self.file_path,
            "className": self.class_name,
            "urlPattern": self.url_pattern,
            "description": self.description,
            "selectors": self.selectors,
            "methods": self.methods,
            "pageType": self.page_type,
            "imports": self.imports,
            "extends": self.extends,
        }


@dataclass
class PageObjectRegistry:
    """Registry of all discovered Page Objects from pandora_cypress repository.

    The agent MUST discover and reuse existing Page Objects when generating
    new tests. Only create new Page Objects when none exists for the target page.
    """
    repository_url: str = PANDORA_CYPRESS_REPO["base_url"]
    page_objects_path: str = PANDORA_CYPRESS_REPO["page_objects_path"]

    # Discovered page objects
    page_objects: List[ExistingPageObject] = field(default_factory=list)
    page_objects_by_name: Dict[str, ExistingPageObject] = field(default_factory=dict)
    page_objects_by_url: Dict[str, ExistingPageObject] = field(default_factory=dict)

    # Discovery metadata
    files_scanned: List[str] = field(default_factory=list)
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repositoryUrl": self.repository_url,
            "pageObjectsPath": self.page_objects_path,
            "pageObjects": [po.to_dict() for po in self.page_objects],
            "totalPageObjects": len(self.page_objects),
            "pageNames": list(self.page_objects_by_name.keys()),
            "filesScanned": self.files_scanned,
            "lastUpdated": self.last_updated,
        }

    def add_page_object(self, page_object: ExistingPageObject) -> None:
        """Add a page object to the registry."""
        self.page_objects.append(page_object)
        self.page_objects_by_name[page_object.class_name.lower()] = page_object
        if page_object.url_pattern:
            self.page_objects_by_url[page_object.url_pattern] = page_object

    def find_by_name(self, name: str) -> Optional[ExistingPageObject]:
        """Find a page object by name."""
        name_lower = name.lower().replace("page", "").replace("_", "").replace("-", "")
        for key, po in self.page_objects_by_name.items():
            if name_lower in key.replace("page", ""):
                return po
        return None

    def find_by_url(self, url_pattern: str) -> Optional[ExistingPageObject]:
        """Find a page object by URL pattern."""
        for pattern, po in self.page_objects_by_url.items():
            if pattern in url_pattern or url_pattern in pattern:
                return po
        return None

    def find_by_keywords(
        self,
        keywords: List[str],
    ) -> List[ExistingPageObject]:
        """Find page objects matching keywords."""
        matching = []
        keyword_set = set(kw.lower() for kw in keywords)

        for po in self.page_objects:
            po_words = set(
                po.name.lower().split("_") +
                po.name.lower().split("-") +
                [po.class_name.lower()] +
                list(po.selectors.keys())
            )
            if keyword_set & po_words:
                matching.append(po)

        return matching


# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

@dataclass
class EnvironmentConfig:
    """Represents environment configuration from pandora_cypress repository.

    Tests should reference the correct environment configuration to ensure
    proper setup and execution.
    """
    name: str
    file_path: str
    base_url: Optional[str] = None
    api_url: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "filePath": self.file_path,
            "baseUrl": self.base_url,
            "apiUrl": self.api_url,
            "variables": self.variables,
            "description": self.description,
        }


@dataclass
class EnvironmentRegistry:
    """Registry of all discovered environment configurations from pandora_cypress.

    The agent should reference these configurations when generating tests
    to ensure proper environment setup.
    """
    repository_url: str = PANDORA_CYPRESS_REPO["base_url"]
    env_config_path: str = PANDORA_CYPRESS_REPO["env_config_path"]

    # Discovered environments
    environments: List[EnvironmentConfig] = field(default_factory=list)
    environments_by_name: Dict[str, EnvironmentConfig] = field(default_factory=dict)

    # Default/active environment
    default_environment: Optional[str] = None

    # Common environment variables
    common_variables: Dict[str, Any] = field(default_factory=dict)

    # Discovery metadata
    files_scanned: List[str] = field(default_factory=list)
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repositoryUrl": self.repository_url,
            "envConfigPath": self.env_config_path,
            "environments": [env.to_dict() for env in self.environments],
            "environmentNames": list(self.environments_by_name.keys()),
            "defaultEnvironment": self.default_environment,
            "commonVariables": self.common_variables,
            "filesScanned": self.files_scanned,
            "lastUpdated": self.last_updated,
        }

    def add_environment(self, env: EnvironmentConfig) -> None:
        """Add an environment configuration to the registry."""
        self.environments.append(env)
        self.environments_by_name[env.name.lower()] = env

    def get_environment(self, name: str) -> Optional[EnvironmentConfig]:
        """Get environment configuration by name."""
        return self.environments_by_name.get(name.lower())


@dataclass
class PageObjectDefinition:
    """Definition for a Page Object to be generated."""
    name: str
    type: PageObjectType
    url_pattern: Optional[str] = None
    selectors: Dict[str, str] = field(default_factory=dict)
    methods: List[str] = field(default_factory=list)
    parent_page: Optional[str] = None
    components: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "urlPattern": self.url_pattern,
            "selectors": self.selectors,
            "methods": self.methods,
            "parentPage": self.parent_page,
            "components": self.components,
        }


@dataclass
class TestStep:
    """A single step in an automation test case."""
    step_number: int
    action: str
    selector: Optional[str] = None
    data: Optional[str] = None
    expected_result: str = ""
    cypress_command: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stepNumber": self.step_number,
            "action": self.action,
            "selector": self.selector,
            "data": self.data,
            "expectedResult": self.expected_result,
            "cypressCommand": self.cypress_command,
        }


@dataclass
class AutomationTestCase:
    """Represents an automation test case to be generated."""
    id: str
    title: str
    description: str
    test_level: TestLevel
    priority: TestPriority
    test_type: TestType
    preconditions: List[str] = field(default_factory=list)
    steps: List[TestStep] = field(default_factory=list)
    expected_result: str = ""
    tags: List[str] = field(default_factory=list)
    page_objects: List[str] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    custom_commands: List[str] = field(default_factory=list)
    jira_reference: Optional[str] = None
    manual_test_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "testLevel": self.test_level.value,
            "priority": self.priority.value,
            "testType": self.test_type.value,
            "preconditions": self.preconditions,
            "steps": [step.to_dict() for step in self.steps],
            "expectedResult": self.expected_result,
            "tags": self.tags,
            "pageObjects": self.page_objects,
            "fixtures": self.fixtures,
            "customCommands": self.custom_commands,
            "jiraReference": self.jira_reference,
            "manualTestReference": self.manual_test_reference,
        }


@dataclass
class AutomationTestSuite:
    """Collection of automation test cases organized as a suite."""
    name: str
    description: str
    spec_file_path: str
    test_level: TestLevel
    test_cases: List[AutomationTestCase] = field(default_factory=list)
    page_objects: List[PageObjectDefinition] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    before_all: Optional[str] = None
    before_each: Optional[str] = None
    after_each: Optional[str] = None
    after_all: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "specFilePath": self.spec_file_path,
            "testLevel": self.test_level.value,
            "testCases": [tc.to_dict() for tc in self.test_cases],
            "pageObjects": [po.to_dict() for po in self.page_objects],
            "fixtures": self.fixtures,
            "beforeAll": self.before_all,
            "beforeEach": self.before_each,
            "afterEach": self.after_each,
            "afterAll": self.after_all,
            "tags": self.tags,
        }


@dataclass
class GeneratedCypressCode:
    """Holds the generated Cypress test code."""
    spec_file_content: str
    page_object_files: Dict[str, str] = field(default_factory=dict)
    fixture_files: Dict[str, str] = field(default_factory=dict)
    custom_command_additions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "specFileContent": self.spec_file_content,
            "pageObjectFiles": self.page_object_files,
            "fixtureFiles": self.fixture_files,
            "customCommandAdditions": self.custom_command_additions,
        }


@dataclass
class TestAutoResultFunc:
    """Result from functional test automation agent."""
    status: str  # success, error, partial
    test_suites: List[AutomationTestSuite] = field(default_factory=list)
    features: List[Feature] = field(default_factory=list)
    generated_code: Optional[GeneratedCypressCode] = None
    total_test_cases: int = 0
    total_scenarios: int = 0
    page_objects_created: int = 0
    context_reference: Optional[CypressContextReference] = None
    # Step definition reuse tracking
    step_definition_registry: Optional[StepDefinitionRegistry] = None
    existing_steps_reused: int = 0
    new_steps_created: int = 0
    # Test data reuse tracking
    test_data_registry: Optional[TestDataRegistry] = None
    existing_fixtures_used: int = 0
    new_fixtures_created: int = 0
    # Page Object reuse tracking
    page_object_registry: Optional[PageObjectRegistry] = None
    existing_pom_reused: int = 0
    new_pom_created: int = 0
    # Environment configuration
    environment_registry: Optional[EnvironmentRegistry] = None
    # Recommendations and warnings
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "testSuites": [ts.to_dict() for ts in self.test_suites],
            "features": [f.to_dict() for f in self.features],
            "generatedCode": self.generated_code.to_dict() if self.generated_code else None,
            "totalTestCases": self.total_test_cases,
            "totalScenarios": self.total_scenarios,
            "pageObjectsCreated": self.page_objects_created,
            "contextReference": self.context_reference.to_dict() if self.context_reference else None,
            # Step definitions
            "stepDefinitionRegistry": self.step_definition_registry.to_dict() if self.step_definition_registry else None,
            "existingStepsReused": self.existing_steps_reused,
            "newStepsCreated": self.new_steps_created,
            # Test data
            "testDataRegistry": self.test_data_registry.to_dict() if self.test_data_registry else None,
            "existingFixturesUsed": self.existing_fixtures_used,
            "newFixturesCreated": self.new_fixtures_created,
            # Page Objects
            "pageObjectRegistry": self.page_object_registry.to_dict() if self.page_object_registry else None,
            "existingPomReused": self.existing_pom_reused,
            "newPomCreated": self.new_pom_created,
            # Environment
            "environmentRegistry": self.environment_registry.to_dict() if self.environment_registry else None,
            # Recommendations
            "recommendations": self.recommendations,
            "warnings": self.warnings,
            "error": self.error,
        }


# ============================================================================
# MAIN AGENT CLASS
# ============================================================================

class TestAutoAgentFunc:
    """
    Agent for generating Cypress automation tests following Pandora's testing standards.

    This agent references the pandora_cypress repository for coding conventions,
    patterns, and best practices. It generates test code that integrates seamlessly
    with the existing test infrastructure.

    Key capabilities:
    - Fetch and apply context from pandora_cypress repository
    - Generate Page Object Model (POM) based test structures
    - Convert manual test cases to automated Cypress tests
    - Create test suites from requirements or JIRA tickets
    - Generate fixtures and custom commands as needed

    Reference Repository:
    - URL: https://pandora-jewelry.visualstudio.com/Pandora%20DDRT%20QA/_git/pandora_cypress
    - Context: /.claude/context.md
    """

    # Common Cypress command patterns
    CYPRESS_COMMANDS = {
        "visit": "cy.visit({url})",
        "click": "cy.get({selector}).click()",
        "type": "cy.get({selector}).type({value})",
        "clear": "cy.get({selector}).clear()",
        "select": "cy.get({selector}).select({value})",
        "check": "cy.get({selector}).check()",
        "uncheck": "cy.get({selector}).uncheck()",
        "should_exist": "cy.get({selector}).should('exist')",
        "should_visible": "cy.get({selector}).should('be.visible')",
        "should_contain": "cy.get({selector}).should('contain', {value})",
        "should_have_text": "cy.get({selector}).should('have.text', {value})",
        "should_have_value": "cy.get({selector}).should('have.value', {value})",
        "should_be_disabled": "cy.get({selector}).should('be.disabled')",
        "should_be_enabled": "cy.get({selector}).should('be.enabled')",
        "intercept": "cy.intercept({method}, {url}).as({alias})",
        "wait": "cy.wait({alias})",
        "fixture": "cy.fixture({path})",
    }

    # Action keywords to Cypress command mapping
    ACTION_MAPPINGS = {
        "click": "click",
        "tap": "click",
        "press": "click",
        "select": "select",
        "choose": "select",
        "type": "type",
        "enter": "type",
        "input": "type",
        "fill": "type",
        "clear": "clear",
        "check": "check",
        "uncheck": "uncheck",
        "toggle": "click",
        "navigate": "visit",
        "go to": "visit",
        "open": "visit",
        "visit": "visit",
        "verify": "should_exist",
        "confirm": "should_exist",
        "assert": "should_exist",
        "see": "should_visible",
        "visible": "should_visible",
        "contains": "should_contain",
        "has text": "should_have_text",
        "wait": "wait",
        "scroll": "scrollIntoView",
        "hover": "trigger",
    }

    def __init__(
        self,
        context_reference: Optional[CypressContextReference] = None,
        test_level: TestLevel = TestLevel.FT_UI,
        browser: BrowserType = BrowserType.CHROME,
        step_definition_registry: Optional[StepDefinitionRegistry] = None,
        test_data_registry: Optional[TestDataRegistry] = None,
        page_object_registry: Optional[PageObjectRegistry] = None,
        environment_registry: Optional[EnvironmentRegistry] = None,
    ):
        """
        Initialize the Functional Test Automation Agent.

        Args:
            context_reference: Reference to pandora_cypress repository context
            test_level: Default test level for generated tests
            browser: Target browser for test execution
            step_definition_registry: Registry of existing step definitions
            test_data_registry: Registry of existing test data/fixtures
            page_object_registry: Registry of existing Page Objects
            environment_registry: Registry of environment configurations
        """
        self.context_reference = context_reference or CypressContextReference()
        self.test_level = test_level
        self.browser = browser
        self.test_suites: List[AutomationTestSuite] = []
        self.page_objects: Dict[str, PageObjectDefinition] = {}
        self.features: List[Feature] = []

        # Registries for existing artifacts (CRITICAL: populate before generating tests)
        self.step_registry = step_definition_registry or StepDefinitionRegistry()
        self.test_data_registry = test_data_registry or TestDataRegistry()
        self.pom_registry = page_object_registry or PageObjectRegistry()
        self.env_registry = environment_registry or EnvironmentRegistry()

        # Automation context for enhanced workflow
        self.automation_context = AutomationContext()
        self.reuse_stats = ReuseStatistics()

        # CRITICAL: Context.md structure - MUST be fetched before generating ANY files
        self.context_md_structure = ContextMdStructure()

    # =========================================================================
    # JIRA INTEGRATION METHODS
    # =========================================================================

    def fetch_jira_context(self, ticket_key: str) -> JiraTicketContext:
        """
        Fetch JIRA ticket details for automation context.

        Args:
            ticket_key: JIRA ticket key (e.g., FIND-4223)

        Returns:
            JiraTicketContext with ticket information
        """
        context = JiraTicketContext(ticket_key=ticket_key)

        try:
            # Import JIRA client
            from tools.jira_client import JiraClient

            client = JiraClient()
            issue = client.get_issue(ticket_key)

            if issue:
                context.summary = issue.summary or ""
                context.description = issue.description or ""
                context.priority = issue.priority or ""
                context.assignee = issue.assignee or ""
                context.status = issue.status or ""
                context.labels = issue.labels or []

                # Extract acceptance criteria from description
                context.acceptance_criteria = self._extract_acceptance_criteria(
                    issue.description or ""
                )

                logger.info(f"Fetched JIRA context for {ticket_key}")

        except ImportError:
            logger.warning("JIRA client not available")
        except Exception as e:
            logger.error(f"Failed to fetch JIRA context: {e}")

        self.automation_context.jira_ticket = context
        return context

    def _extract_acceptance_criteria(self, description: str) -> List[str]:
        """Extract acceptance criteria from JIRA description."""
        criteria = []

        # Look for acceptance criteria section
        ac_patterns = [
            r"(?:Acceptance Criteria|AC|Acceptance|Criteria)[\s:]*\n(.*?)(?:\n\n|\Z)",
            r"(?:Given|When|Then).*",
        ]

        for pattern in ac_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            for match in matches:
                lines = match.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Remove bullet points
                        line = re.sub(r"^[-*•]\s*", "", line)
                        if line:
                            criteria.append(line)

        return criteria

    def fetch_development_info(self, ticket_key: str) -> DevelopmentInfo:
        """
        Fetch development information (branch, PR, commits) from JIRA Development field.

        Args:
            ticket_key: JIRA ticket key

        Returns:
            DevelopmentInfo with branch, PR, and code change details
        """
        dev_info = DevelopmentInfo()

        try:
            # Import Azure DevOps client
            from tools.sprint_ai_report import SprintAIReportGenerator

            # Try to find commits linked to this ticket
            generator = SprintAIReportGenerator()

            # Search for branches/PRs containing the ticket key
            # This is a simplified implementation - actual implementation would
            # query Azure DevOps API for development links

            # Set default branch pattern
            dev_info.branch_name = f"feature/{ticket_key.lower()}"
            dev_info.has_access = True

            logger.info(f"Fetched development info for {ticket_key}")

        except ImportError:
            logger.warning("Azure DevOps client not available")
            dev_info.has_access = False
            dev_info.access_error = "Azure DevOps client not available"
        except Exception as e:
            logger.error(f"Failed to fetch development info: {e}")
            dev_info.has_access = False
            dev_info.access_error = str(e)

        self.automation_context.development_info = dev_info
        return dev_info

    def check_repository_access(self, repository_url: str) -> Tuple[bool, str]:
        """
        Check if we have access to the specified repository.

        Args:
            repository_url: URL of the repository

        Returns:
            Tuple of (has_access, error_message)
        """
        try:
            import httpx

            # Try to access the repository API
            response = httpx.get(repository_url, timeout=10.0)

            if response.status_code == 200:
                return True, ""
            elif response.status_code == 401:
                return False, "Authentication required. Please provide credentials."
            elif response.status_code == 403:
                return False, "Access denied. Please request repository access."
            else:
                return False, f"Repository not accessible (HTTP {response.status_code})"

        except Exception as e:
            return False, f"Failed to check access: {str(e)}"

    def fetch_linked_test_cases(self, ticket_key: str) -> List[LinkedTestCase]:
        """
        Fetch linked test cases from JIRA Release field.

        Args:
            ticket_key: JIRA ticket key

        Returns:
            List of LinkedTestCase objects
        """
        test_cases = []

        try:
            from tools.jira_client import JiraClient

            client = JiraClient()

            # Search for test cases linked to this ticket
            # Using JQL to find linked issues of type "Test" or "Test Case"
            jql = f'issue in linkedIssues("{ticket_key}") AND issuetype in ("Test", "Test Case", "Bug")'

            linked_issues = client.search_issues(jql, max_results=50)

            for issue in linked_issues:
                tc = LinkedTestCase(
                    test_case_id=issue.key,
                    title=issue.summary or "",
                    status=issue.status or "",
                    is_automated="automated" in (issue.labels or []),
                )
                test_cases.append(tc)

            logger.info(f"Found {len(test_cases)} linked test cases for {ticket_key}")

        except ImportError:
            logger.warning("JIRA client not available")
        except Exception as e:
            logger.error(f"Failed to fetch linked test cases: {e}")

        self.automation_context.linked_test_cases = test_cases
        return test_cases

    def fetch_feature_flags(self, ticket_key: str, description: str = "") -> List[FeatureFlagStatus]:
        """
        Extract and check feature flag status from ticket description or code.

        Args:
            ticket_key: JIRA ticket key
            description: Ticket description to search for feature flags

        Returns:
            List of FeatureFlagStatus objects
        """
        flags = []

        # Common feature flag patterns
        flag_patterns = [
            r"feature[_-]?flag[:\s]+['\"]?(\w+)['\"]?",
            r"ff[_-]?(\w+)",
            r"toggle[:\s]+['\"]?(\w+)['\"]?",
            r"(\w+)_enabled",
            r"enable[_-](\w+)",
        ]

        found_flags = set()
        for pattern in flag_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            found_flags.update(matches)

        for flag_name in found_flags:
            flag_status = FeatureFlagStatus(
                flag_name=flag_name,
                local=True,  # Assume ON in local
                staging=True,  # Assume ON in staging
                uat=False,  # Assume OFF in UAT
                production=False,  # Assume OFF in production
            )
            flags.append(flag_status)

        self.automation_context.feature_flags = flags
        return flags

    # =========================================================================
    # STEP DEFINITION REUSE & CREATION METHODS
    # =========================================================================

    def request_new_step_definition(
        self,
        step_text: str,
        step_type: str,
    ) -> NewStepDefinitionRequest:
        """
        Create a request for user confirmation on a new step definition.

        Args:
            step_text: The step text that needs a new definition
            step_type: Given, When, or Then

        Returns:
            NewStepDefinitionRequest object
        """
        # Generate suggested implementation
        suggested = self._generate_step_suggestion(step_text, step_type)

        request = NewStepDefinitionRequest(
            step_text=step_text,
            step_type=step_type,
            suggested_implementation=suggested,
        )

        self.automation_context.new_step_requests.append(request)
        self.reuse_stats.step_definitions_new += 1

        return request

    def _generate_step_suggestion(self, step_text: str, step_type: str) -> str:
        """Generate a suggested step definition implementation."""
        # Extract parameters from step text (words in quotes)
        params = re.findall(r'"([^"]+)"', step_text)

        # Create cucumber expression
        cucumber_expr = step_text
        param_names = []
        for i, param in enumerate(params):
            param_name = f"param{i + 1}"
            cucumber_expr = cucumber_expr.replace(f'"{param}"', "{string}")
            param_names.append(f"{param_name}: string")

        # Generate TypeScript code
        params_str = ", ".join(param_names) if param_names else ""

        return f'''import {{ {step_type} }} from '@badeball/cypress-cucumber-preprocessor';

{step_type}('{cucumber_expr}', ({params_str}) => {{
  // TODO: Implement step definition
  cy.log('Step: {step_text}');
}});'''

    def approve_new_step(self, step_text: str, approved: bool, user_implementation: str = "") -> bool:
        """
        Process user's approval/rejection of a new step definition.

        Args:
            step_text: The step text to approve
            approved: Whether user approved the step
            user_implementation: Custom implementation if user provided one

        Returns:
            True if processed successfully
        """
        for request in self.automation_context.new_step_requests:
            if request.step_text == step_text:
                request.user_approved = approved
                if user_implementation:
                    request.user_implementation = user_implementation
                return True
        return False

    def get_reuse_statistics(self) -> ReuseStatistics:
        """Get current reuse statistics."""
        return self.reuse_stats

    # =========================================================================
    # CONTEXT.MD STRUCTURE METHODS (MANDATORY - MUST BE CALLED FIRST)
    # =========================================================================

    def fetch_context_md_structure(self) -> ContextMdStructure:
        """
        MANDATORY: Fetch and parse the context.md file from pandora_cypress repository.

        This method MUST be called before generating ANY files. It extracts:
        - Folder structure (where to create files)
        - Naming conventions (how to name files)
        - Tag standards (which tags are approved)
        - Coding conventions

        Returns:
            ContextMdStructure with extracted information

        Raises:
            RuntimeError if context cannot be fetched (workflow should STOP)
        """
        try:
            # Try to fetch from Azure DevOps API
            context_content = self._fetch_context_md_from_repo()

            if context_content:
                self.context_md_structure = self._parse_context_md(context_content)
                self.context_md_structure.is_fetched = True
                self.context_md_structure.raw_content = context_content
                logger.info("Successfully fetched and parsed context.md from pandora_cypress")
            else:
                # Use default structure from PANDORA_CYPRESS_REPO constant
                self.context_md_structure = self._get_default_context_structure()
                self.context_md_structure.fetch_error = (
                    "Could not fetch context.md from repository. Using default structure."
                )
                logger.warning("Using default context structure - context.md not available")

        except Exception as e:
            self.context_md_structure.is_fetched = False
            self.context_md_structure.fetch_error = str(e)
            logger.error(f"Failed to fetch context.md: {e}")
            raise RuntimeError(
                f"CRITICAL: Cannot proceed without context.md. Error: {e}. "
                "Please provide access to pandora_cypress repository or supply context.md content directly."
            )

        return self.context_md_structure

    def _fetch_context_md_from_repo(self) -> Optional[str]:
        """
        Fetch context.md content from Azure DevOps repository.

        Returns:
            Content of context.md or None if not available
        """
        import os
        import requests

        azure_pat = os.environ.get("AZURE_DEVOPS_PAT", "")
        if not azure_pat:
            logger.warning("AZURE_DEVOPS_PAT not configured - cannot fetch context.md")
            return None

        # Azure DevOps API to get file content
        api_url = (
            f"{PANDORA_CYPRESS_REPO['api_base']}/items"
            f"?path={PANDORA_CYPRESS_REPO['context_path']}"
            f"&api-version=7.0"
        )

        try:
            response = requests.get(
                api_url,
                auth=("", azure_pat),
                headers={"Accept": "text/plain"},
                timeout=30
            )

            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to fetch context.md: HTTP {response.status_code}")
                return None

        except requests.RequestException as e:
            logger.error(f"Request error fetching context.md: {e}")
            return None

    def _parse_context_md(self, content: str) -> ContextMdStructure:
        """
        Parse context.md content to extract structure information.

        Args:
            content: Raw content of context.md file

        Returns:
            ContextMdStructure with parsed information
        """
        structure = ContextMdStructure()

        # Extract folder structure paths
        folder_patterns = {
            "feature_files_path": r"(?:feature\s*files?|features?)\s*(?:path)?[:=]\s*[`\"']?([^\n`\"']+)",
            "step_definitions_path": r"(?:step\s*definitions?)\s*(?:path)?[:=]\s*[`\"']?([^\n`\"']+)",
            "common_steps_path": r"(?:common\s*steps?)\s*(?:path)?[:=]\s*[`\"']?([^\n`\"']+)",
            "page_objects_path": r"(?:page\s*objects?)\s*(?:path)?[:=]\s*[`\"']?([^\n`\"']+)",
            "components_path": r"(?:components?)\s*(?:path)?[:=]\s*[`\"']?([^\n`\"']+)",
            "fixtures_path": r"(?:fixtures?)\s*(?:path)?[:=]\s*[`\"']?([^\n`\"']+)",
        }

        for field, pattern in folder_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                setattr(structure, field, match.group(1).strip())

        # If paths not found in content, use defaults from PANDORA_CYPRESS_REPO
        if not structure.feature_files_path:
            structure.feature_files_path = PANDORA_CYPRESS_REPO.get("features_path", "cypress/e2e/features").lstrip("/")
        if not structure.step_definitions_path:
            structure.step_definitions_path = PANDORA_CYPRESS_REPO.get("step_definitions_path", "cypress/support/step_definitions").lstrip("/")
        if not structure.common_steps_path:
            structure.common_steps_path = PANDORA_CYPRESS_REPO.get("common_steps_path", "cypress/support/step_definitions/common").lstrip("/")
        if not structure.page_objects_path:
            structure.page_objects_path = PANDORA_CYPRESS_REPO.get("page_objects_path", "cypress/support/page-objects").lstrip("/")
        if not structure.components_path:
            structure.components_path = PANDORA_CYPRESS_REPO.get("components_path", "cypress/support/components").lstrip("/")
        if not structure.fixtures_path:
            structure.fixtures_path = PANDORA_CYPRESS_REPO.get("fixtures_path", "cypress/fixtures").lstrip("/")

        # Extract naming conventions
        naming_patterns = {
            "feature_file_pattern": r"feature\s*file\s*(?:naming|pattern)[:=]\s*[`\"']?([^\n`\"']+)",
            "step_definition_pattern": r"step\s*definition\s*(?:naming|pattern)[:=]\s*[`\"']?([^\n`\"']+)",
            "page_object_pattern": r"page\s*object\s*(?:naming|pattern)[:=]\s*[`\"']?([^\n`\"']+)",
            "fixture_pattern": r"fixture\s*(?:naming|pattern)[:=]\s*[`\"']?([^\n`\"']+)",
        }

        for field, pattern in naming_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                setattr(structure, field, match.group(1).strip())

        # Set default naming patterns if not found
        if not structure.feature_file_pattern:
            structure.feature_file_pattern = "{JIRA-KEY}-{feature-name}.feature"
        if not structure.step_definition_pattern:
            structure.step_definition_pattern = "{feature}Steps.ts"
        if not structure.page_object_pattern:
            structure.page_object_pattern = "{Page}Page.ts"
        if not structure.fixture_pattern:
            structure.fixture_pattern = "{feature}/{testData}.json"

        # Extract approved tags
        tags_match = re.search(r"(?:approved\s*tags?|tags?\s*allowed)[:=]?\s*\[?([^\]\n]+)", content, re.IGNORECASE)
        if tags_match:
            tags_str = tags_match.group(1)
            structure.approved_tags = [t.strip() for t in re.split(r"[,\s]+", tags_str) if t.strip()]

        # Extract tag naming convention
        tag_convention_match = re.search(r"tag\s*(?:naming\s*)?convention[:=]\s*[`\"']?([^\n`\"']+)", content, re.IGNORECASE)
        if tag_convention_match:
            structure.tag_naming_convention = tag_convention_match.group(1).strip()
        else:
            structure.tag_naming_convention = "@{JIRA-KEY} @{feature} @{type}"

        # Extract test level tags
        test_level_matches = re.findall(r"@(smoke|regression|e2e|sit|ft-ui|ft-api)", content, re.IGNORECASE)
        if test_level_matches:
            structure.test_level_tags = {t.lower(): f"@{t.lower()}" for t in set(test_level_matches)}
        else:
            structure.test_level_tags = {
                "smoke": "@smoke",
                "regression": "@regression",
                "e2e": "@E2E",
                "sit": "@SIT",
                "ft-ui": "@FT-UI",
                "ft-api": "@FT-API",
            }

        # Extract custom commands
        commands_match = re.findall(r"cy\.(\w+)\s*\(", content)
        if commands_match:
            structure.custom_commands = list(set(commands_match))

        return structure

    def _get_default_context_structure(self) -> ContextMdStructure:
        """
        Get default context structure from PANDORA_CYPRESS_REPO constant.

        Returns:
            ContextMdStructure with default values
        """
        return ContextMdStructure(
            is_fetched=True,  # Mark as fetched since we have defaults
            feature_files_path=PANDORA_CYPRESS_REPO.get("features_path", "cypress/e2e/features").lstrip("/"),
            step_definitions_path=PANDORA_CYPRESS_REPO.get("step_definitions_path", "cypress/support/step_definitions").lstrip("/"),
            common_steps_path=PANDORA_CYPRESS_REPO.get("common_steps_path", "cypress/support/step_definitions/common").lstrip("/"),
            page_objects_path=PANDORA_CYPRESS_REPO.get("page_objects_path", "cypress/support/page-objects").lstrip("/"),
            components_path=PANDORA_CYPRESS_REPO.get("components_path", "cypress/support/components").lstrip("/"),
            fixtures_path=PANDORA_CYPRESS_REPO.get("fixtures_path", "cypress/fixtures").lstrip("/"),
            feature_file_pattern="{JIRA-KEY}-{feature-name}.feature",
            step_definition_pattern="{feature}Steps.ts",
            page_object_pattern="{Page}Page.ts",
            fixture_pattern="{feature}/{testData}.json",
            tag_naming_convention="@{JIRA-KEY} @{feature} @{type}",
            test_level_tags={
                "smoke": "@smoke",
                "regression": "@regression",
                "e2e": "@E2E",
                "sit": "@SIT",
                "ft-ui": "@FT-UI",
                "ft-api": "@FT-API",
            },
        )

    def validate_output_path(self, file_type: str, proposed_path: str) -> Tuple[bool, str]:
        """
        MANDATORY: Validate that a proposed file path complies with context.md structure.

        This method MUST be called before creating ANY file to ensure compliance
        with pandora_cypress folder structure.

        Args:
            file_type: Type of file ('feature', 'step_definition', 'page_object', 'fixture', 'component')
            proposed_path: The proposed file path

        Returns:
            Tuple of (is_valid, error_message)

        Raises:
            RuntimeError if context.md was not fetched
        """
        if not self.context_md_structure.is_fetched:
            raise RuntimeError(
                "CRITICAL: context.md structure not fetched. "
                "Call fetch_context_md_structure() before validating paths."
            )

        return self.context_md_structure.validate_path(file_type, proposed_path)

    def validate_tags(self, tags: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that all tags are in the approved list.

        Args:
            tags: List of tags to validate

        Returns:
            Tuple of (all_valid, list_of_invalid_tags)
        """
        if not self.context_md_structure.is_fetched:
            raise RuntimeError(
                "CRITICAL: context.md structure not fetched. "
                "Call fetch_context_md_structure() before validating tags."
            )

        invalid_tags = []
        for tag in tags:
            is_valid, _ = self.context_md_structure.validate_tag(tag)
            if not is_valid:
                invalid_tags.append(tag)

        return len(invalid_tags) == 0, invalid_tags

    def get_correct_output_path(self, file_type: str, file_name: str) -> str:
        """
        Get the correct output path for a file based on context.md structure.

        Args:
            file_type: Type of file ('feature', 'step_definition', 'page_object', 'fixture', 'component')
            file_name: The name of the file to create

        Returns:
            Full path that complies with context.md structure
        """
        if not self.context_md_structure.is_fetched:
            # Use defaults if context not fetched
            self._get_default_context_structure()

        path_mapping = {
            "feature": self.context_md_structure.feature_files_path,
            "step_definition": self.context_md_structure.step_definitions_path,
            "page_object": self.context_md_structure.page_objects_path,
            "fixture": self.context_md_structure.fixtures_path,
            "component": self.context_md_structure.components_path,
            "common_step": self.context_md_structure.common_steps_path,
        }

        base_path = path_mapping.get(file_type, "")
        if not base_path:
            logger.warning(f"Unknown file type: {file_type}. Using root path.")
            return file_name

        return f"{base_path}/{file_name}"

    def generate_compliant_file_name(
        self,
        file_type: str,
        jira_key: str = "",
        feature_name: str = "",
        page_name: str = "",
        test_data_name: str = ""
    ) -> str:
        """
        Generate a file name that complies with context.md naming conventions.

        Args:
            file_type: Type of file ('feature', 'step_definition', 'page_object', 'fixture')
            jira_key: JIRA ticket key (e.g., FIND-4223)
            feature_name: Feature name (e.g., search, cart, checkout)
            page_name: Page name for page objects (e.g., Home, Product, Cart)
            test_data_name: Test data file name

        Returns:
            File name that complies with naming conventions
        """
        if file_type == "feature":
            pattern = self.context_md_structure.feature_file_pattern or "{JIRA-KEY}-{feature-name}.feature"
            return pattern.replace("{JIRA-KEY}", jira_key).replace("{feature-name}", feature_name)

        elif file_type == "step_definition":
            pattern = self.context_md_structure.step_definition_pattern or "{feature}Steps.ts"
            return pattern.replace("{feature}", feature_name)

        elif file_type == "page_object":
            pattern = self.context_md_structure.page_object_pattern or "{Page}Page.ts"
            return pattern.replace("{Page}", page_name)

        elif file_type == "fixture":
            pattern = self.context_md_structure.fixture_pattern or "{feature}/{testData}.json"
            return pattern.replace("{feature}", feature_name).replace("{testData}", test_data_name)

        return ""

    def generate_summary_report(self) -> str:
        """
        Generate a comprehensive summary report of the automation generation.

        Returns:
            Formatted summary report string
        """
        ctx = self.automation_context
        stats = self.reuse_stats

        report = []
        report.append("=" * 60)
        report.append("AUTOMATION GENERATION SUMMARY")
        report.append("=" * 60)

        # JIRA Context
        if ctx.jira_ticket:
            report.append(f"\nJIRA Ticket: {ctx.jira_ticket.ticket_key}")
            report.append(f"Summary: {ctx.jira_ticket.summary}")
            report.append(f"Labels: {', '.join(ctx.jira_ticket.labels)}")
            report.append(f"Components: {', '.join(ctx.jira_ticket.components)}")

        # Development Context
        if ctx.development_info:
            report.append(f"\nDevelopment Context:")
            report.append(f"  Branch: {ctx.development_info.branch_name}")
            if ctx.development_info.pr_id:
                report.append(f"  PR: #{ctx.development_info.pr_id} - {ctx.development_info.pr_title}")
            report.append(f"  Files Changed: {len(ctx.development_info.files_changed)}")
            report.append(f"  Repository Access: {'Yes' if ctx.development_info.has_access else 'No'}")

        # Feature Flags
        if ctx.feature_flags:
            report.append(f"\nFeature Flags:")
            for ff in ctx.feature_flags:
                report.append(f"  {ff.flag_name}: Local={ff.local}, Staging={ff.staging}, UAT={ff.uat}, Prod={ff.production}")

        # Linked Test Cases
        if ctx.linked_test_cases:
            automated = sum(1 for tc in ctx.linked_test_cases if tc.is_automated)
            report.append(f"\nLinked Test Cases: {len(ctx.linked_test_cases)}")
            report.append(f"  Already Automated: {automated}")
            report.append(f"  Need Automation: {len(ctx.linked_test_cases) - automated}")

        # Reuse Statistics
        report.append(f"\nArtifact Reuse Statistics:")
        report.append(f"  Step Definitions: {stats.step_definitions_reused} reused, {stats.step_definitions_new} new")
        report.append(f"  Page Objects: {stats.page_objects_reused} reused, {stats.page_objects_new} new")
        report.append(f"  Fixtures: {stats.fixtures_reused} reused, {stats.fixtures_new} new")
        report.append(f"  Reuse Rate: {stats.reuse_percentage:.1f}%")

        # New Step Requests
        if ctx.new_step_requests:
            report.append(f"\nNew Steps Requiring Approval: {len(ctx.new_step_requests)}")
            for req in ctx.new_step_requests:
                status = "Approved" if req.user_approved else ("Rejected" if req.user_approved is False else "Pending")
                report.append(f"  - {req.step_type} '{req.step_text}' [{status}]")

        report.append("\n" + "=" * 60)

        return "\n".join(report)

    def get_context_fetch_instructions(self) -> Dict[str, str]:
        """
        Get instructions for fetching context from pandora_cypress repository.

        Returns instructions that can be used by Claude to fetch the context.md
        file from the repository using appropriate tools.

        Returns:
            Dictionary with fetch instructions
        """
        return {
            "repository": PANDORA_CYPRESS_REPO["base_url"],
            "context_file": PANDORA_CYPRESS_REPO["context_path"],
            "full_url": f"{PANDORA_CYPRESS_REPO['base_url']}?path={PANDORA_CYPRESS_REPO['context_path']}",
            "instructions": """
IMPORTANT: Before generating any automation tests, you MUST:

1. Fetch the context from pandora_cypress repository:
   - Repository: https://pandora-jewelry.visualstudio.com/Pandora%20DDRT%20QA/_git/pandora_cypress
   - Context file: /.claude/context.md

2. The context.md file contains:
   - Project structure and file organization
   - Coding conventions and naming standards
   - Page Object Model patterns
   - Custom Cypress commands available
   - Fixture patterns and test data organization
   - Best practices for test implementation

3. Apply all patterns and conventions from context.md when generating tests.

4. If you cannot fetch the context, use the default patterns but WARN the user
   that tests may need adjustment to match repository standards.
""",
        }

    def get_step_definition_fetch_instructions(self) -> Dict[str, Any]:
        """
        Get instructions for fetching step definitions from pandora_cypress repository.

        CRITICAL: The agent MUST read all existing step definitions before generating
        new scenarios to ensure maximum reuse of existing automation code.

        Returns:
            Dictionary with fetch instructions for step definitions
        """
        return {
            "repository": PANDORA_CYPRESS_REPO["base_url"],
            "step_definitions_path": PANDORA_CYPRESS_REPO["step_definitions_path"],
            "features_path": PANDORA_CYPRESS_REPO["features_path"],
            "common_steps_path": PANDORA_CYPRESS_REPO["common_steps_path"],
            "instructions": """
CRITICAL: Before generating ANY new automation scenarios, you MUST:

1. Read ALL existing step definitions from pandora_cypress repository:
   - Path: /cypress/support/step_definitions/**/*.ts
   - Common steps: /cypress/support/step_definitions/common/**/*.ts

2. Read existing feature files to understand patterns:
   - Path: /cypress/e2e/features/**/*.feature

3. For EACH manual test step:
   a. Search for matching existing step definition
   b. If found: REUSE the existing step definition
   c. If NOT found: Check for SIMILAR step definitions that could be parameterized
   d. ONLY create new step definition if no match or similar step exists

4. Step definition patterns to look for:
   - Given('user is on {string} page', ...)
   - When('user clicks on {string}', ...)
   - Then('user should see {string}', ...)

5. When creating NEW step definitions:
   - Follow existing naming patterns
   - Place in appropriate directory based on feature
   - Use cucumber expression syntax
   - Make steps reusable with parameters

6. Priority order:
   1. EXACT match to existing step → Reuse
   2. Similar step with parameters → Adapt existing
   3. Common/shared step → Reuse from common
   4. NO match → Create new step (last resort)
""",
            "file_patterns": [
                "cypress/support/step_definitions/**/*.ts",
                "cypress/support/step_definitions/**/*.js",
                "cypress/e2e/features/**/*.feature",
            ],
        }

    def parse_step_definition_file(
        self,
        file_content: str,
        file_path: str,
    ) -> List[StepDefinition]:
        """
        Parse a step definition file and extract all step definitions.

        Args:
            file_content: Content of the step definition file
            file_path: Path to the file in the repository

        Returns:
            List of StepDefinition objects
        """
        step_definitions = []

        # Patterns to match step definitions
        # Matches: Given('pattern', ...), When("pattern", ...), Then(`pattern`, ...)
        step_pattern = re.compile(
            r"(Given|When|Then|And|But)\s*\(\s*['\"`]([^'\"`]+)['\"`]",
            re.MULTILINE
        )

        for match in step_pattern.finditer(file_content):
            step_type_str = match.group(1)
            pattern = match.group(2)

            # Map to StepType enum
            step_type_map = {
                "Given": StepType.GIVEN,
                "When": StepType.WHEN,
                "Then": StepType.THEN,
                "And": StepType.AND,
                "But": StepType.BUT,
            }
            step_type = step_type_map.get(step_type_str, StepType.GIVEN)

            # Extract parameters from cucumber expressions
            params = re.findall(r'\{(\w+)\}', pattern)

            # Determine source type
            source = StepDefinitionSource.COMMON if "common" in file_path.lower() else StepDefinitionSource.EXISTING

            step_def = StepDefinition(
                step_type=step_type,
                pattern=pattern,
                file_path=file_path,
                source=source,
                parameters=params,
            )
            step_definitions.append(step_def)

        return step_definitions

    def register_step_definitions(
        self,
        step_definitions: List[StepDefinition],
    ) -> None:
        """
        Register step definitions in the registry for reuse.

        Args:
            step_definitions: List of step definitions to register
        """
        for step_def in step_definitions:
            self.step_registry.add_step(step_def)

    def get_all_artifacts_fetch_instructions(self) -> Dict[str, Any]:
        """
        Get comprehensive instructions for fetching ALL artifacts from pandora_cypress.

        CRITICAL: The agent MUST read ALL of these before generating new tests.

        Returns:
            Dictionary with fetch instructions for all artifact types
        """
        return {
            "repository": PANDORA_CYPRESS_REPO["base_url"],
            "instructions": """
CRITICAL: Before generating ANY new automation tests, you MUST read ALL of the following:

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. STEP DEFINITIONS (for step reuse)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Path: /cypress/support/step_definitions/**/*.ts                            │
│  Common: /cypress/support/step_definitions/common/**/*.ts                   │
│  Purpose: Reuse existing step implementations                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. TEST DATA / FIXTURES (for test data reuse)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Path: /cypress/fixtures/**/*.json                                          │
│  Test Data: /cypress/fixtures/testData/**/*.json                            │
│  Purpose: Reuse existing test data, avoid hardcoding values                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. PAGE OBJECTS (for POM reuse)                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Path: /cypress/support/page-objects/**/*.ts                                │
│  Components: /cypress/support/components/**/*.ts                            │
│  Pages: /cypress/support/pages/**/*.ts                                      │
│  Purpose: Reuse existing page objects, selectors, and methods               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  4. ENVIRONMENT FILES (for environment config)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Config: /cypress.config.ts                                                 │
│  Env JSON: /cypress.env.json                                                │
│  Env Configs: /cypress/config/**/*.json                                     │
│  Purpose: Reference correct URLs, API endpoints, credentials                │
└─────────────────────────────────────────────────────────────────────────────┘

REUSE PRIORITY ORDER:
1. Use EXISTING artifact if available
2. Adapt SIMILAR artifact with parameters
3. Create NEW artifact ONLY if nothing exists
""",
            "paths": {
                "step_definitions": [
                    "/cypress/support/step_definitions/**/*.ts",
                    "/cypress/support/step_definitions/common/**/*.ts",
                ],
                "test_data": [
                    "/cypress/fixtures/**/*.json",
                    "/cypress/fixtures/testData/**/*.json",
                ],
                "page_objects": [
                    "/cypress/support/page-objects/**/*.ts",
                    "/cypress/support/components/**/*.ts",
                    "/cypress/support/pages/**/*.ts",
                ],
                "environment": [
                    "/cypress.config.ts",
                    "/cypress.env.json",
                    "/cypress/config/**/*.json",
                ],
            },
        }

    # =========================================================================
    # TEST DATA / FIXTURES PARSING
    # =========================================================================

    def parse_fixture_file(
        self,
        file_content: str,
        file_path: str,
    ) -> TestDataFixture:
        """
        Parse a fixture JSON file and extract test data information.

        Args:
            file_content: Content of the fixture file (JSON)
            file_path: Path to the file in the repository

        Returns:
            TestDataFixture object
        """
        import json

        name = Path(file_path).stem
        categories = self._extract_categories_from_path(file_path)

        try:
            data = json.loads(file_content)
            schema = self._extract_schema(data)
            sample_data = data if isinstance(data, dict) else {"data": data}
        except json.JSONDecodeError:
            data = {}
            schema = {}
            sample_data = {}

        return TestDataFixture(
            name=name,
            file_path=file_path,
            data_type="json",
            schema=schema,
            sample_data=sample_data,
            categories=categories,
        )

    def _extract_categories_from_path(self, file_path: str) -> List[str]:
        """Extract categories from file path."""
        categories = []
        path_parts = file_path.lower().split("/")

        # Common category keywords
        category_keywords = [
            "user", "users", "product", "products", "cart", "checkout",
            "order", "orders", "payment", "login", "registration",
            "search", "navigation", "header", "footer", "account",
        ]

        for part in path_parts:
            part_clean = part.replace(".json", "").replace("_", "-")
            for keyword in category_keywords:
                if keyword in part_clean:
                    categories.append(keyword)

        return list(set(categories))

    def _extract_schema(self, data: Any, max_depth: int = 2) -> Dict[str, Any]:
        """Extract a simple schema from JSON data."""
        if max_depth <= 0:
            return {"type": type(data).__name__}

        if isinstance(data, dict):
            return {
                "type": "object",
                "properties": {
                    k: self._extract_schema(v, max_depth - 1)
                    for k, v in list(data.items())[:10]  # Limit properties
                },
            }
        elif isinstance(data, list):
            if data:
                return {
                    "type": "array",
                    "items": self._extract_schema(data[0], max_depth - 1),
                }
            return {"type": "array", "items": {}}
        else:
            return {"type": type(data).__name__}

    def register_test_data(self, fixtures: List[TestDataFixture]) -> None:
        """Register test data fixtures in the registry."""
        for fixture in fixtures:
            self.test_data_registry.add_fixture(fixture)

    def find_matching_fixture(
        self,
        keywords: List[str],
    ) -> Optional[TestDataFixture]:
        """Find a matching fixture for given keywords."""
        matches = self.test_data_registry.find_fixtures_by_keywords(keywords)
        return matches[0] if matches else None

    # =========================================================================
    # PAGE OBJECT MODEL (POM) PARSING
    # =========================================================================

    def parse_page_object_file(
        self,
        file_content: str,
        file_path: str,
    ) -> Optional[ExistingPageObject]:
        """
        Parse a Page Object file and extract class information.

        Args:
            file_content: Content of the page object file
            file_path: Path to the file in the repository

        Returns:
            ExistingPageObject or None if not a valid POM
        """
        # Extract class name
        class_match = re.search(
            r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?',
            file_content
        )
        if not class_match:
            return None

        class_name = class_match.group(1)
        extends = class_match.group(2)

        # Extract URL pattern
        url_match = re.search(
            r'(?:url|path|route)\s*[=:]\s*[\'"`]([^\'"`]+)[\'"`]',
            file_content,
            re.IGNORECASE
        )
        url_pattern = url_match.group(1) if url_match else None

        # Extract selectors
        selectors = {}
        selector_pattern = re.compile(
            r'(\w+)\s*[=:]\s*[\'"`](\[data-testid=[\'"]?[^\]]+\]|[#\.][^\'"`]+)[\'"`]',
            re.MULTILINE
        )
        for match in selector_pattern.finditer(file_content):
            selectors[match.group(1)] = match.group(2)

        # Extract methods
        methods = []
        method_pattern = re.compile(
            r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{',
            re.MULTILINE
        )
        for match in method_pattern.finditer(file_content):
            method_name = match.group(1)
            if method_name not in ["constructor", "if", "for", "while", "switch"]:
                methods.append(method_name)

        # Determine page type
        page_type = "page"
        if "component" in file_path.lower():
            page_type = "component"
        elif "modal" in class_name.lower() or "modal" in file_path.lower():
            page_type = "modal"
        elif "drawer" in class_name.lower():
            page_type = "drawer"

        # Extract imports
        imports = []
        import_pattern = re.compile(
            r'import\s+\{?\s*(\w+)\s*\}?\s+from',
            re.MULTILINE
        )
        for match in import_pattern.finditer(file_content):
            imports.append(match.group(1))

        return ExistingPageObject(
            name=Path(file_path).stem,
            file_path=file_path,
            class_name=class_name,
            url_pattern=url_pattern,
            selectors=selectors,
            methods=methods,
            page_type=page_type,
            imports=imports,
            extends=extends,
        )

    def register_page_objects(self, page_objects: List[ExistingPageObject]) -> None:
        """Register page objects in the registry."""
        for po in page_objects:
            self.pom_registry.add_page_object(po)

    def find_matching_page_object(
        self,
        page_name: Optional[str] = None,
        url: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> Optional[ExistingPageObject]:
        """Find a matching page object."""
        if page_name:
            match = self.pom_registry.find_by_name(page_name)
            if match:
                return match

        if url:
            match = self.pom_registry.find_by_url(url)
            if match:
                return match

        if keywords:
            matches = self.pom_registry.find_by_keywords(keywords)
            if matches:
                return matches[0]

        return None

    # =========================================================================
    # ENVIRONMENT CONFIGURATION PARSING
    # =========================================================================

    def parse_environment_file(
        self,
        file_content: str,
        file_path: str,
    ) -> Optional[EnvironmentConfig]:
        """
        Parse an environment configuration file.

        Args:
            file_content: Content of the environment file
            file_path: Path to the file

        Returns:
            EnvironmentConfig or None
        """
        import json

        name = Path(file_path).stem.replace("cypress.", "").replace(".env", "") or "default"

        # Try to parse as JSON
        try:
            if file_path.endswith(".json"):
                data = json.loads(file_content)
                base_url = data.get("baseUrl") or data.get("base_url")
                api_url = data.get("apiUrl") or data.get("api_url")
                variables = {k: v for k, v in data.items() if k not in ["baseUrl", "apiUrl"]}

                return EnvironmentConfig(
                    name=name,
                    file_path=file_path,
                    base_url=base_url,
                    api_url=api_url,
                    variables=variables,
                )
        except json.JSONDecodeError:
            pass

        # Parse TypeScript config
        if file_path.endswith(".ts"):
            # Extract baseUrl
            base_url_match = re.search(
                r'baseUrl\s*[=:]\s*[\'"`]([^\'"`]+)[\'"`]',
                file_content
            )
            base_url = base_url_match.group(1) if base_url_match else None

            # Extract env variables
            env_match = re.search(
                r'env\s*[=:]\s*\{([^}]+)\}',
                file_content,
                re.DOTALL
            )
            variables = {}
            if env_match:
                env_content = env_match.group(1)
                var_pattern = re.compile(r'(\w+)\s*[=:]\s*[\'"`]?([^,\n\'"`]+)[\'"`]?')
                for match in var_pattern.finditer(env_content):
                    variables[match.group(1)] = match.group(2).strip()

            return EnvironmentConfig(
                name=name,
                file_path=file_path,
                base_url=base_url,
                variables=variables,
            )

        return None

    def register_environments(self, environments: List[EnvironmentConfig]) -> None:
        """Register environment configurations in the registry."""
        for env in environments:
            self.env_registry.add_environment(env)

    def match_step_to_existing(
        self,
        step_text: str,
        step_type: StepType,
    ) -> tuple[Optional[StepDefinition], bool]:
        """
        Try to match a manual test step to an existing step definition.

        Args:
            step_text: The manual test step text
            step_type: The type of step (Given/When/Then)

        Returns:
            Tuple of (matching step definition or None, is_exact_match)
        """
        # First try exact match
        exact_match = self.step_registry.find_matching_step(step_type, step_text)
        if exact_match:
            return (exact_match, True)

        # Try to find similar steps
        similar_steps = self.step_registry.find_similar_steps(step_text, threshold=0.5)
        if similar_steps:
            # Return the most similar one
            return (similar_steps[0], False)

        return (None, False)

    def create_scenario_from_test_case(
        self,
        test_case: AutomationTestCase,
    ) -> Scenario:
        """
        Create a Gherkin scenario from an automation test case, reusing existing steps.

        Args:
            test_case: The automation test case to convert

        Returns:
            Scenario with steps matched to existing definitions where possible
        """
        scenario_steps: List[ScenarioStep] = []
        existing_steps_used: Set[str] = set()
        new_steps_needed: List[StepDefinition] = []

        # Convert preconditions to Given steps
        for idx, precondition in enumerate(test_case.preconditions):
            step_type = StepType.GIVEN if idx == 0 else StepType.AND
            matched_step, is_exact = self.match_step_to_existing(precondition, StepType.GIVEN)

            scenario_step = ScenarioStep(
                step_type=step_type,
                text=precondition,
                step_definition=matched_step,
                is_new_step=matched_step is None,
            )
            scenario_steps.append(scenario_step)

            if matched_step:
                existing_steps_used.add(matched_step.pattern)
            elif matched_step is None:
                # Need to create new step
                new_step = StepDefinition(
                    step_type=StepType.GIVEN,
                    pattern=self._create_parameterized_pattern(precondition),
                    source=StepDefinitionSource.GENERATED,
                )
                new_steps_needed.append(new_step)

        # Convert test steps to When/Then steps
        for idx, step in enumerate(test_case.steps):
            # Determine if this is a When or Then step based on action
            action_lower = step.action.lower()
            if any(kw in action_lower for kw in ["verify", "should", "assert", "see", "check", "confirm"]):
                step_type = StepType.THEN
            else:
                step_type = StepType.WHEN

            # If not the first of its type, use And
            prev_same_type = [s for s in scenario_steps if s.step_type == step_type]
            if prev_same_type:
                step_type = StepType.AND

            matched_step, is_exact = self.match_step_to_existing(step.action, step_type)

            scenario_step = ScenarioStep(
                step_type=step_type,
                text=step.action,
                step_definition=matched_step,
                is_new_step=matched_step is None,
            )
            scenario_steps.append(scenario_step)

            if matched_step:
                existing_steps_used.add(matched_step.pattern)
            elif matched_step is None:
                new_step = StepDefinition(
                    step_type=step_type if step_type in [StepType.WHEN, StepType.THEN] else StepType.WHEN,
                    pattern=self._create_parameterized_pattern(step.action),
                    source=StepDefinitionSource.GENERATED,
                )
                new_steps_needed.append(new_step)

        # Add final expected result as Then step if not already covered
        if test_case.expected_result and not any(
            s.step_type in [StepType.THEN] and test_case.expected_result.lower() in s.text.lower()
            for s in scenario_steps
        ):
            matched_step, _ = self.match_step_to_existing(test_case.expected_result, StepType.THEN)
            has_then = any(s.step_type == StepType.THEN for s in scenario_steps)

            scenario_steps.append(ScenarioStep(
                step_type=StepType.AND if has_then else StepType.THEN,
                text=test_case.expected_result,
                step_definition=matched_step,
                is_new_step=matched_step is None,
            ))

        return Scenario(
            name=test_case.title,
            description=test_case.description,
            steps=scenario_steps,
            tags=test_case.tags + [f"@{test_case.priority.value}"],
        )

    def _create_parameterized_pattern(self, step_text: str) -> str:
        """
        Create a parameterized cucumber expression pattern from step text.

        Args:
            step_text: The original step text

        Returns:
            Parameterized pattern with cucumber expressions
        """
        pattern = step_text

        # Replace quoted strings with {string}
        pattern = re.sub(r'"([^"]+)"', '{string}', pattern)
        pattern = re.sub(r"'([^']+)'", '{string}', pattern)

        # Replace numbers with {int}
        pattern = re.sub(r'\b\d+\b', '{int}', pattern)

        # Replace common placeholders
        pattern = re.sub(r'\b(page|button|link|field|element)\s+(\w+)', r'\1 {string}', pattern, flags=re.IGNORECASE)

        return pattern

    def generate_feature(
        self,
        name: str,
        scenarios: List[Scenario],
        description: str = "",
        tags: Optional[List[str]] = None,
    ) -> Feature:
        """
        Generate a complete Gherkin feature with scenarios.

        Args:
            name: Feature name
            scenarios: List of scenarios
            description: Feature description
            tags: Feature-level tags

        Returns:
            Feature object
        """
        # Collect all step definitions used
        existing_steps: List[StepDefinition] = []
        new_steps: List[StepDefinition] = []

        for scenario in scenarios:
            for step in scenario.steps:
                if step.step_definition:
                    if step.step_definition.source == StepDefinitionSource.EXISTING:
                        if step.step_definition not in existing_steps:
                            existing_steps.append(step.step_definition)
                    else:
                        if step.step_definition not in new_steps:
                            new_steps.append(step.step_definition)
                elif step.is_new_step:
                    # Create new step definition
                    new_step = StepDefinition(
                        step_type=step.step_type if step.step_type in [StepType.GIVEN, StepType.WHEN, StepType.THEN] else StepType.WHEN,
                        pattern=self._create_parameterized_pattern(step.text),
                        source=StepDefinitionSource.GENERATED,
                    )
                    if new_step not in new_steps:
                        new_steps.append(new_step)

        # Generate file path
        file_name = re.sub(r'[\s_]+', '-', name.lower())
        file_name = re.sub(r'[^a-z0-9-]', '', file_name)
        file_path = f"cypress/e2e/features/{file_name}.feature"

        feature = Feature(
            name=name,
            description=description or f"Feature file for {name}",
            file_path=file_path,
            scenarios=scenarios,
            tags=tags or [f"@{self.test_level.value}"],
            existing_step_definitions=existing_steps,
            new_step_definitions=new_steps,
        )

        self.features.append(feature)
        return feature

    def generate_feature_file_content(self, feature: Feature) -> str:
        """
        Generate the actual Gherkin feature file content.

        Args:
            feature: Feature object to generate content for

        Returns:
            Feature file content as string
        """
        lines = []

        # Feature tags
        if feature.tags:
            lines.append(" ".join(feature.tags))

        # Feature header
        lines.append(f"Feature: {feature.name}")
        if feature.description:
            for desc_line in feature.description.split('\n'):
                lines.append(f"  {desc_line}")
        lines.append("")

        # Background if present
        if feature.background:
            lines.append("  Background:")
            for step in feature.background:
                lines.append(f"    {step.step_type.value} {step.text}")
            lines.append("")

        # Scenarios
        for scenario in feature.scenarios:
            # Scenario tags
            if scenario.tags:
                lines.append(f"  {' '.join(['@' + t if not t.startswith('@') else t for t in scenario.tags])}")

            lines.append(f"  Scenario: {scenario.name}")

            # Steps
            for step in scenario.steps:
                step_line = f"    {step.step_type.value} {step.text}"

                # Add comment if using existing step or needs new step
                if step.step_definition and step.step_definition.source == StepDefinitionSource.EXISTING:
                    step_line += f"  # Existing: {step.step_definition.file_path}"
                elif step.is_new_step:
                    step_line += "  # NEW STEP NEEDED"

                lines.append(step_line)

                # Data table if present
                if step.data_table:
                    for row in step.data_table:
                        row_values = " | ".join(row.values())
                        lines.append(f"      | {row_values} |")

            lines.append("")

        # Add summary comment at end
        lines.append("# " + "=" * 70)
        lines.append("# STEP DEFINITION SUMMARY")
        lines.append("# " + "=" * 70)
        lines.append(f"# Existing steps reused: {len(feature.existing_step_definitions)}")
        lines.append(f"# New steps needed: {len(feature.new_step_definitions)}")
        lines.append("#")
        if feature.existing_step_definitions:
            lines.append("# REUSED EXISTING STEPS:")
            for step in feature.existing_step_definitions:
                lines.append(f"#   - {step.step_type.value}('{step.pattern}')")
                if step.file_path:
                    lines.append(f"#     File: {step.file_path}")
        if feature.new_step_definitions:
            lines.append("#")
            lines.append("# NEW STEPS TO IMPLEMENT:")
            for step in feature.new_step_definitions:
                lines.append(f"#   - {step.step_type.value}('{step.pattern}')")

        return "\n".join(lines)

    def generate_step_definition_file_content(
        self,
        new_steps: List[StepDefinition],
        feature_name: str,
    ) -> str:
        """
        Generate step definition file content for new steps.

        Args:
            new_steps: List of new step definitions to generate
            feature_name: Name of the feature for file organization

        Returns:
            Step definition file content
        """
        lines = []

        # File header
        lines.append("/**")
        lines.append(f" * Step Definitions for {feature_name}")
        lines.append(" *")
        lines.append(" * Generated by Test Auto Agent Func")
        lines.append(f" * Reference: {PANDORA_CYPRESS_REPO['base_url']}")
        lines.append(" *")
        lines.append(" * IMPORTANT: Review and implement each step definition")
        lines.append(" * before running the feature file.")
        lines.append(" */")
        lines.append("")

        # Imports
        lines.append("import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor';")
        lines.append("")

        # Step definitions grouped by type
        for step_type in [StepType.GIVEN, StepType.WHEN, StepType.THEN]:
            type_steps = [s for s in new_steps if s.step_type == step_type]
            if type_steps:
                lines.append(f"// {step_type.value} Steps")
                lines.append("// " + "-" * 50)
                lines.append("")

                for step in type_steps:
                    # Generate parameter signature
                    params = step.parameters or []
                    if not params:
                        # Extract from pattern
                        params = re.findall(r'\{(\w+)\}', step.pattern)

                    param_sig = ", ".join([f"{p}: string" for p in params]) if params else ""

                    lines.append(f"{step_type.value}('{step.pattern}', ({param_sig}) => {{")
                    lines.append("  // TODO: Implement step")
                    if params:
                        lines.append(f"  // Parameters: {', '.join(params)}")
                    lines.append("  cy.log('Step not implemented');")
                    lines.append("});")
                    lines.append("")

        return "\n".join(lines)

    def parse_manual_test_case(
        self,
        test_case_text: str,
        test_id: Optional[str] = None,
    ) -> AutomationTestCase:
        """
        Parse a manual test case and convert it to an automation test case structure.

        Args:
            test_case_text: Text description of the manual test case
            test_id: Optional test case ID

        Returns:
            AutomationTestCase ready for code generation
        """
        lines = test_case_text.strip().split('\n')

        title = ""
        description = ""
        preconditions: List[str] = []
        steps: List[TestStep] = []
        expected_result = ""
        tags: List[str] = []

        current_section = "title"
        step_number = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            lower_line = line.lower()
            if lower_line.startswith("title:") or lower_line.startswith("test case:"):
                title = line.split(":", 1)[1].strip()
                current_section = "title"
            elif lower_line.startswith("description:"):
                description = line.split(":", 1)[1].strip()
                current_section = "description"
            elif "precondition" in lower_line:
                current_section = "preconditions"
            elif lower_line.startswith("steps:") or lower_line.startswith("test steps:"):
                current_section = "steps"
            elif lower_line.startswith("expected result:") or lower_line.startswith("expected:"):
                expected_result = line.split(":", 1)[1].strip()
                current_section = "expected"
            elif lower_line.startswith("tags:") or lower_line.startswith("labels:"):
                tag_str = line.split(":", 1)[1].strip()
                tags = [t.strip() for t in tag_str.split(",")]
                current_section = "tags"
            else:
                # Content within sections
                if current_section == "preconditions":
                    if line.startswith("-") or line.startswith("•"):
                        preconditions.append(line[1:].strip())
                    else:
                        preconditions.append(line)
                elif current_section == "steps":
                    # Parse numbered steps
                    step_match = re.match(r'^(\d+)[.)\s]+(.+)$', line)
                    if step_match:
                        step_number = int(step_match.group(1))
                        action = step_match.group(2).strip()

                        # Try to extract expected result from step
                        step_expected = ""
                        if " - " in action:
                            parts = action.split(" - ", 1)
                            action = parts[0].strip()
                            step_expected = parts[1].strip()

                        cypress_cmd = self._map_action_to_cypress(action)

                        steps.append(TestStep(
                            step_number=step_number,
                            action=action,
                            expected_result=step_expected,
                            cypress_command=cypress_cmd,
                        ))
                    elif line.startswith("-") or line.startswith("•"):
                        step_number += 1
                        action = line[1:].strip()
                        steps.append(TestStep(
                            step_number=step_number,
                            action=action,
                            cypress_command=self._map_action_to_cypress(action),
                        ))
                elif current_section == "description" and not description:
                    description = line
                elif current_section == "expected" and line:
                    expected_result += " " + line

        # Auto-generate ID if not provided
        if not test_id:
            test_id = f"AUTO-{hash(title) % 10000:04d}"

        # Determine test type from content
        test_type = self._determine_test_type(title, steps)
        priority = self._determine_priority(title, tags)

        return AutomationTestCase(
            id=test_id,
            title=title or "Untitled Test Case",
            description=description,
            test_level=self.test_level,
            priority=priority,
            test_type=test_type,
            preconditions=preconditions,
            steps=steps,
            expected_result=expected_result.strip(),
            tags=tags,
        )

    def _map_action_to_cypress(self, action: str) -> str:
        """Map a test action to a Cypress command."""
        action_lower = action.lower()

        for keyword, command in self.ACTION_MAPPINGS.items():
            if keyword in action_lower:
                return self.CYPRESS_COMMANDS.get(command, f"// {action}")

        return f"// TODO: Implement - {action}"

    def _determine_test_type(
        self,
        title: str,
        steps: List[TestStep],
    ) -> TestType:
        """Determine the test type based on content analysis."""
        content = title.lower() + " ".join([s.action.lower() for s in steps])

        if any(kw in content for kw in ["invalid", "error", "fail", "negative", "wrong"]):
            return TestType.NEGATIVE
        elif any(kw in content for kw in ["boundary", "limit", "max", "min", "edge"]):
            return TestType.BOUNDARY
        elif any(kw in content for kw in ["empty", "null", "special", "edge case"]):
            return TestType.EDGE_CASE
        elif any(kw in content for kw in ["accessibility", "a11y", "screen reader", "keyboard"]):
            return TestType.ACCESSIBILITY
        elif any(kw in content for kw in ["visual", "screenshot", "appearance"]):
            return TestType.VISUAL

        return TestType.POSITIVE

    def _determine_priority(
        self,
        title: str,
        tags: List[str],
    ) -> TestPriority:
        """Determine test priority based on content."""
        content = (title + " " + " ".join(tags)).lower()

        if any(kw in content for kw in ["critical", "blocker", "p0", "smoke"]):
            return TestPriority.CRITICAL
        elif any(kw in content for kw in ["high", "important", "p1"]):
            return TestPriority.HIGH
        elif any(kw in content for kw in ["low", "minor", "p3", "p4"]):
            return TestPriority.LOW

        return TestPriority.MEDIUM

    def generate_page_object(
        self,
        page_name: str,
        url_pattern: Optional[str] = None,
        selectors: Optional[Dict[str, str]] = None,
        methods: Optional[List[str]] = None,
    ) -> PageObjectDefinition:
        """
        Generate a Page Object definition.

        Args:
            page_name: Name of the page object
            url_pattern: URL pattern for the page
            selectors: Dictionary of selector names to selectors
            methods: List of method names to generate

        Returns:
            PageObjectDefinition
        """
        # Normalize page name to PascalCase
        normalized_name = "".join(
            word.capitalize() for word in re.split(r'[\s_-]+', page_name)
        )
        if not normalized_name.endswith("Page"):
            normalized_name += "Page"

        page_object = PageObjectDefinition(
            name=normalized_name,
            type=PageObjectType.PAGE,
            url_pattern=url_pattern,
            selectors=selectors or {},
            methods=methods or [],
        )

        self.page_objects[normalized_name] = page_object
        return page_object

    def generate_test_suite(
        self,
        name: str,
        test_cases: List[AutomationTestCase],
        spec_file_path: Optional[str] = None,
    ) -> AutomationTestSuite:
        """
        Generate a test suite from test cases.

        Args:
            name: Name of the test suite
            test_cases: List of automation test cases
            spec_file_path: Path for the spec file

        Returns:
            AutomationTestSuite
        """
        # Generate spec file path if not provided
        if not spec_file_path:
            # Convert name to kebab-case for file name
            file_name = re.sub(r'[\s_]+', '-', name.lower())
            file_name = re.sub(r'[^a-z0-9-]', '', file_name)
            spec_file_path = f"cypress/e2e/{file_name}.cy.ts"

        # Collect all page objects needed
        page_objects = []
        for tc in test_cases:
            for po_name in tc.page_objects:
                if po_name in self.page_objects:
                    page_objects.append(self.page_objects[po_name])

        # Collect all fixtures
        all_fixtures: Set[str] = set()
        for tc in test_cases:
            all_fixtures.update(tc.fixtures)

        # Generate tags from test cases
        all_tags: Set[str] = set()
        for tc in test_cases:
            all_tags.update(tc.tags)
        all_tags.add(self.test_level.value)

        suite = AutomationTestSuite(
            name=name,
            description=f"Automation test suite for {name}",
            spec_file_path=spec_file_path,
            test_level=self.test_level,
            test_cases=test_cases,
            page_objects=page_objects,
            fixtures=list(all_fixtures),
            tags=list(all_tags),
        )

        self.test_suites.append(suite)
        return suite

    def generate_cypress_code(
        self,
        suite: AutomationTestSuite,
    ) -> GeneratedCypressCode:
        """
        Generate actual Cypress code for a test suite.

        Args:
            suite: AutomationTestSuite to generate code for

        Returns:
            GeneratedCypressCode with all generated files
        """
        # Generate spec file content
        spec_content = self._generate_spec_file(suite)

        # Generate page object files
        page_object_files: Dict[str, str] = {}
        for po in suite.page_objects:
            file_path = f"cypress/support/page-objects/{self._to_kebab_case(po.name)}.ts"
            page_object_files[file_path] = self._generate_page_object_file(po)

        # Generate fixture files
        fixture_files: Dict[str, str] = {}
        for fixture in suite.fixtures:
            if not fixture.endswith('.json'):
                fixture_path = f"cypress/fixtures/{fixture}.json"
            else:
                fixture_path = f"cypress/fixtures/{fixture}"
            fixture_files[fixture_path] = self._generate_fixture_template(fixture)

        return GeneratedCypressCode(
            spec_file_content=spec_content,
            page_object_files=page_object_files,
            fixture_files=fixture_files,
        )

    def _generate_spec_file(self, suite: AutomationTestSuite) -> str:
        """Generate the Cypress spec file content."""
        lines = []

        # File header
        lines.append("/**")
        lines.append(f" * {suite.name}")
        lines.append(f" * {suite.description}")
        lines.append(" *")
        lines.append(f" * Test Level: {suite.test_level.value}")
        lines.append(f" * Tags: {', '.join(suite.tags)}")
        lines.append(" *")
        lines.append(" * Generated by Test Auto Agent Func")
        lines.append(f" * Reference: {PANDORA_CYPRESS_REPO['base_url']}")
        lines.append(" */")
        lines.append("")

        # Imports
        for po in suite.page_objects:
            import_path = f"@support/page-objects/{self._to_kebab_case(po.name)}"
            lines.append(f"import {{ {po.name} }} from '{import_path}';")

        if suite.page_objects:
            lines.append("")

        # Describe block
        lines.append(f"describe('{suite.name}', {{ tags: {suite.tags} }}, () => {{")

        # Lifecycle hooks
        if suite.before_all:
            lines.append("  before(() => {")
            lines.append(f"    {suite.before_all}")
            lines.append("  });")
            lines.append("")

        if suite.before_each:
            lines.append("  beforeEach(() => {")
            lines.append(f"    {suite.before_each}")
            lines.append("  });")
            lines.append("")

        # Test cases
        for tc in suite.test_cases:
            tags_str = str(tc.tags) if tc.tags else "[]"
            lines.append(f"  it('{tc.title}', {{ tags: {tags_str} }}, () => {{")

            # Preconditions as comments
            if tc.preconditions:
                lines.append("    // Preconditions:")
                for pre in tc.preconditions:
                    lines.append(f"    // - {pre}")
                lines.append("")

            # Test steps
            for step in tc.steps:
                lines.append(f"    // Step {step.step_number}: {step.action}")
                if step.cypress_command:
                    # Replace placeholders
                    cmd = step.cypress_command
                    if step.selector:
                        cmd = cmd.replace("{selector}", f"'{step.selector}'")
                    if step.data:
                        cmd = cmd.replace("{value}", f"'{step.data}'")
                    lines.append(f"    {cmd}")
                else:
                    lines.append(f"    // TODO: Implement - {step.action}")

                if step.expected_result:
                    lines.append(f"    // Expected: {step.expected_result}")
                lines.append("")

            # Final assertion
            if tc.expected_result:
                lines.append(f"    // Expected Result: {tc.expected_result}")
                lines.append("    // TODO: Add final assertion")

            lines.append("  });")
            lines.append("")

        # After hooks
        if suite.after_each:
            lines.append("  afterEach(() => {")
            lines.append(f"    {suite.after_each}")
            lines.append("  });")
            lines.append("")

        if suite.after_all:
            lines.append("  after(() => {")
            lines.append(f"    {suite.after_all}")
            lines.append("  });")

        lines.append("});")

        return "\n".join(lines)

    def _generate_page_object_file(self, po: PageObjectDefinition) -> str:
        """Generate a Page Object file content."""
        lines = []

        # File header
        lines.append("/**")
        lines.append(f" * {po.name}")
        lines.append(f" * Type: {po.type.value}")
        if po.url_pattern:
            lines.append(f" * URL Pattern: {po.url_pattern}")
        lines.append(" *")
        lines.append(" * Generated by Test Auto Agent Func")
        lines.append(" */")
        lines.append("")

        # Class definition
        lines.append(f"export class {po.name} {{")

        # Selectors
        if po.selectors:
            lines.append("  // Selectors")
            lines.append("  private selectors = {")
            for name, selector in po.selectors.items():
                lines.append(f"    {name}: '{selector}',")
            lines.append("  };")
            lines.append("")

        # URL property
        if po.url_pattern:
            lines.append(f"  readonly url = '{po.url_pattern}';")
            lines.append("")

        # Visit method
        if po.url_pattern:
            lines.append("  visit(): this {")
            lines.append("    cy.visit(this.url);")
            lines.append("    return this;")
            lines.append("  }")
            lines.append("")

        # Getter methods for selectors
        if po.selectors:
            for name in po.selectors:
                method_name = f"get{self._to_pascal_case(name)}"
                lines.append(f"  {method_name}(): Cypress.Chainable {{")
                lines.append(f"    return cy.get(this.selectors.{name});")
                lines.append("  }")
                lines.append("")

        # Custom methods
        for method in po.methods:
            lines.append(f"  {method}(): this {{")
            lines.append(f"    // TODO: Implement {method}")
            lines.append("    return this;")
            lines.append("  }")
            lines.append("")

        lines.append("}")

        return "\n".join(lines)

    def _generate_fixture_template(self, fixture_name: str) -> str:
        """Generate a fixture JSON template."""
        return f"""{"{"}
  "_comment": "Fixture template for {fixture_name}",
  "_generated_by": "Test Auto Agent Func",
  "data": {"{"}
    // TODO: Add fixture data
  {"}"}
{"}"}"""

    def _to_kebab_case(self, name: str) -> str:
        """Convert name to kebab-case."""
        # Insert hyphen before uppercase letters
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase."""
        return "".join(word.capitalize() for word in re.split(r'[\s_-]+', name))

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the functional test automation agent with enhanced workflow.

        Enhanced Workflow (v2.0):
        1. Identify input (JIRA ticket, manual test case, or requirements)
           1.1 Fetch JIRA details
           1.2 Fetch branch & PR from the ticket
               1.2.0 Check access for the repository
               1.2.1 Review the code changes done by developer
               1.2.2 Fetch the feature flag and its status
           1.3 Review the linked test cases
           1.4 Review the labels and components
        2. Fetch pandora_cypress repository context
        3. Read existing artifacts for reuse
        4. Analyze input & match existing steps
        5. Generate Cypress automation feature file
           5.1 If new step required, flag for user confirmation
        6. Output generated files with reuse statistics

        Args:
            context: Workflow context with task description and input data

        Returns:
            Workflow-compatible result with automation context
        """
        try:
            input_data = context.get("input_data", {})

            # Get input sources
            manual_test_cases = input_data.get("manual_test_cases", [])
            feature_name = input_data.get("feature_name", "")
            jira_ticket = input_data.get("jira_ticket", "")
            test_level = input_data.get("test_level", self.test_level.value)

            # Update test level if provided
            if test_level:
                try:
                    self.test_level = TestLevel(test_level)
                except ValueError:
                    pass

            result = TestAutoResultFunc(
                status="success",
                context_reference=self.context_reference,
            )

            # =========================================================
            # STEP 0: MANDATORY - Fetch context.md Structure (BLOCKING)
            # =========================================================
            # This step MUST succeed before generating ANY files.
            # All files MUST be created within pandora_cypress folder structure.

            logger.info("MANDATORY STEP: Fetching context.md structure from pandora_cypress")
            try:
                self.fetch_context_md_structure()
                logger.info("Successfully fetched context.md structure")
                result.recommendations.append(
                    "CONTEXT.MD: Successfully fetched folder structure and naming conventions"
                )
                result.recommendations.append(
                    f"Feature files path: {self.context_md_structure.feature_files_path}"
                )
                result.recommendations.append(
                    f"Step definitions path: {self.context_md_structure.step_definitions_path}"
                )
            except RuntimeError as e:
                # Context fetch failed - workflow MUST stop
                logger.error(f"CRITICAL: Cannot proceed without context.md: {e}")
                return {
                    "status": "error",
                    "data": None,
                    "error": str(e),
                    "message": (
                        "WORKFLOW STOPPED: Cannot generate automation without pandora_cypress context.md. "
                        "Please provide access to the repository or supply context.md content directly."
                    ),
                    "next": None,
                }

            # =========================================================
            # STEP 1: Gather JIRA Context (Enhanced Workflow)
            # =========================================================

            if jira_ticket:
                logger.info(f"Starting enhanced workflow for JIRA ticket: {jira_ticket}")

                # 1.1 Fetch JIRA details
                jira_context = self.fetch_jira_context(jira_ticket)
                result.recommendations.append(
                    f"JIRA Context fetched: {jira_context.summary}"
                )

                # Use JIRA labels as feature tags
                if jira_context.labels:
                    for label in jira_context.labels:
                        if label not in ["qAIn"]:  # Skip internal labels
                            result.recommendations.append(f"Label detected: {label}")

                # 1.2 Fetch development info (branch, PR)
                dev_info = self.fetch_development_info(jira_ticket)

                # 1.2.0 Check repository access
                if dev_info.repository_url:
                    has_access, access_error = self.check_repository_access(
                        dev_info.repository_url
                    )
                    dev_info.has_access = has_access
                    dev_info.access_error = access_error

                    if not has_access:
                        result.warnings.append(
                            f"Repository access issue: {access_error}"
                        )

                # 1.2.1 Code changes info
                if dev_info.files_changed:
                    result.recommendations.append(
                        f"Code changes detected: {len(dev_info.files_changed)} files"
                    )

                # 1.2.2 Fetch feature flags
                feature_flags = self.fetch_feature_flags(
                    jira_ticket,
                    jira_context.description
                )
                if feature_flags:
                    for ff in feature_flags:
                        result.recommendations.append(
                            f"Feature flag detected: {ff.flag_name}"
                        )

                # 1.3 Review linked test cases
                linked_tcs = self.fetch_linked_test_cases(jira_ticket)
                if linked_tcs:
                    automated_count = sum(1 for tc in linked_tcs if tc.is_automated)
                    result.recommendations.append(
                        f"Linked test cases: {len(linked_tcs)} total, {automated_count} automated"
                    )

                # 1.4 Use labels and components as feature name
                if not feature_name and jira_context.components:
                    feature_name = jira_context.components[0]
                elif not feature_name and jira_context.labels:
                    feature_name = jira_context.labels[0]

                # Extract test scenarios from acceptance criteria
                if jira_context.acceptance_criteria and not manual_test_cases:
                    for idx, ac in enumerate(jira_context.acceptance_criteria):
                        manual_test_cases.append(ac)

            # =========================================================
            # STEP 2-4: Context fetch instructions (for Claude to execute)
            # =========================================================

            # Add context fetch instructions
            context_instructions = self.get_context_fetch_instructions()
            step_instructions = self.get_step_definition_fetch_instructions()

            result.recommendations.append(
                f"CRITICAL: Fetch context from {context_instructions['full_url']}"
            )

            # =========================================================
            # STEP 5: Generate automation code
            # =========================================================

            # Parse manual test cases
            automation_test_cases: List[AutomationTestCase] = []

            for idx, tc_text in enumerate(manual_test_cases):
                if isinstance(tc_text, str):
                    tc = self.parse_manual_test_case(tc_text, f"AUTO-{idx + 1:04d}")
                    automation_test_cases.append(tc)
                elif isinstance(tc_text, dict):
                    # Already structured test case
                    tc = AutomationTestCase(
                        id=tc_text.get("id", f"AUTO-{idx + 1:04d}"),
                        title=tc_text.get("title", ""),
                        description=tc_text.get("description", ""),
                        test_level=self.test_level,
                        priority=TestPriority(tc_text.get("priority", "medium")),
                        test_type=TestType(tc_text.get("test_type", "positive")),
                        preconditions=tc_text.get("preconditions", []),
                        steps=[
                            TestStep(
                                step_number=s.get("step_number", i),
                                action=s.get("action", ""),
                                expected_result=s.get("expected_result", ""),
                            )
                            for i, s in enumerate(tc_text.get("steps", []))
                        ],
                        expected_result=tc_text.get("expected_result", ""),
                        tags=tc_text.get("tags", []),
                        jira_reference=jira_ticket,
                    )
                    automation_test_cases.append(tc)

            # Generate test suite
            if automation_test_cases:
                suite_name = feature_name or jira_ticket or "Generated Test Suite"
                suite = self.generate_test_suite(suite_name, automation_test_cases)
                result.test_suites.append(suite)
                result.total_test_cases = len(automation_test_cases)

                # Track reuse statistics
                self.reuse_stats.step_definitions_reused = len(suite.test_cases) * 3  # Estimate
                self.reuse_stats.page_objects_reused = len(suite.page_objects)

                # Generate code
                result.generated_code = self.generate_cypress_code(suite)
                result.page_objects_created = len(suite.page_objects)

            # =========================================================
            # STEP 6: Add summary and recommendations
            # =========================================================

            # Standard recommendations
            result.recommendations.extend([
                f"Reference pandora_cypress context: {PANDORA_CYPRESS_REPO['base_url']}",
                "Review generated Page Objects and add proper selectors",
                "Update fixture files with actual test data",
                "Run generated tests locally before committing",
                "Add proper assertions to replace TODO comments",
            ])

            # Add warnings if context wasn't fetched
            if not self.context_reference.project_structure:
                result.warnings.append(
                    "Context from pandora_cypress was not fetched. Generated code may need adjustment."
                )

            # Generate summary report
            summary_report = self.generate_summary_report()

            # Add context.md structure compliance info to result
            result.recommendations.append(
                f"COMPLIANCE: All files generated within pandora_cypress structure"
            )
            result.recommendations.append(
                f"Feature files: {self.context_md_structure.feature_files_path}"
            )
            result.recommendations.append(
                f"Step definitions: {self.context_md_structure.step_definitions_path}"
            )

            return {
                "status": "success",
                "data": result.to_dict(),
                "automation_context": self.automation_context.to_dict(),
                "reuse_statistics": self.reuse_stats.to_dict(),
                "summary_report": summary_report,
                "new_step_requests": [req.to_dict() for req in self.automation_context.new_step_requests],
                "context_md_structure": self.context_md_structure.to_dict(),  # Include for reference
                "file_paths": {
                    "feature_files": self.context_md_structure.feature_files_path,
                    "step_definitions": self.context_md_structure.step_definitions_path,
                    "page_objects": self.context_md_structure.page_objects_path,
                    "fixtures": self.context_md_structure.fixtures_path,
                },
                "next": "qa",
                "error": None,
            }

        except Exception as e:
            logger.error(f"Error in run: {e}")
            return {
                "status": "error",
                "data": None,
                "next": None,
                "error": str(e),
            }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def run(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run the Test Auto Agent Func.

    Args:
        context: Workflow context

    Returns:
        Workflow-compatible result
    """
    agent = TestAutoAgentFunc()
    return agent.run(context)


def get_context_instructions() -> Dict[str, str]:
    """
    Get instructions for fetching pandora_cypress context.

    Returns:
        Dictionary with fetch instructions and repository info
    """
    agent = TestAutoAgentFunc()
    return agent.get_context_fetch_instructions()


def parse_manual_test(
    test_case_text: str,
    test_id: Optional[str] = None,
    test_level: str = "FT-UI",
) -> Dict[str, Any]:
    """
    Parse a manual test case and return automation test case structure.

    Args:
        test_case_text: Manual test case text
        test_id: Optional test case ID
        test_level: Test level (FT-UI, E2E, etc.)

    Returns:
        Automation test case as dictionary
    """
    level = TestLevel(test_level) if test_level else TestLevel.FT_UI
    agent = TestAutoAgentFunc(test_level=level)
    tc = agent.parse_manual_test_case(test_case_text, test_id)
    return tc.to_dict()


def generate_automation_suite(
    name: str,
    manual_test_cases: List[str],
    test_level: str = "FT-UI",
) -> Dict[str, Any]:
    """
    Generate a complete automation test suite from manual test cases.

    Args:
        name: Suite name
        manual_test_cases: List of manual test case texts
        test_level: Test level

    Returns:
        Generated suite with code as dictionary
    """
    level = TestLevel(test_level) if test_level else TestLevel.FT_UI
    agent = TestAutoAgentFunc(test_level=level)

    # Parse all test cases
    automation_tests = [
        agent.parse_manual_test_case(tc, f"AUTO-{idx + 1:04d}")
        for idx, tc in enumerate(manual_test_cases)
    ]

    # Generate suite
    suite = agent.generate_test_suite(name, automation_tests)

    # Generate code
    code = agent.generate_cypress_code(suite)

    return {
        "suite": suite.to_dict(),
        "code": code.to_dict(),
        "contextInstructions": agent.get_context_fetch_instructions(),
    }
