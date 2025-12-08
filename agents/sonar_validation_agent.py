"""
Sonar Validation Agent

A dedicated agent for validating code against SonarCloud quality gates before PR creation.
This agent reads pipeline files, checks the SonarCloud dashboard, and provides a plan
to fix any issues to maintain 0 errors, 0 duplication, and 100% coverage.
"""

import os
import re
import json
import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SonarSeverity(Enum):
    """SonarCloud issue severity levels."""
    BLOCKER = "BLOCKER"
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"


class SonarIssueType(Enum):
    """SonarCloud issue types."""
    BUG = "BUG"
    VULNERABILITY = "VULNERABILITY"
    CODE_SMELL = "CODE_SMELL"
    SECURITY_HOTSPOT = "SECURITY_HOTSPOT"


class QualityGateStatus(Enum):
    """Quality gate status."""
    OK = "OK"
    WARN = "WARN"
    ERROR = "ERROR"
    NONE = "NONE"


@dataclass
class SonarIssue:
    """Represents a SonarCloud issue."""
    key: str
    rule: str
    severity: str
    component: str
    line: Optional[int]
    message: str
    type: str
    effort: Optional[str] = None
    debt: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "rule": self.rule,
            "severity": self.severity,
            "component": self.component,
            "line": self.line,
            "message": self.message,
            "type": self.type,
            "effort": self.effort,
            "debt": self.debt,
        }


@dataclass
class DuplicationBlock:
    """Represents a code duplication block."""
    file: str
    start_line: int
    end_line: int
    duplicated_lines: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "startLine": self.start_line,
            "endLine": self.end_line,
            "duplicatedLines": self.duplicated_lines,
        }


@dataclass
class CoverageMetrics:
    """Code coverage metrics from SonarCloud."""
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    lines_to_cover: int = 0
    uncovered_lines: int = 0
    conditions_to_cover: int = 0
    uncovered_conditions: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "lineCoverage": self.line_coverage,
            "branchCoverage": self.branch_coverage,
            "linesToCover": self.lines_to_cover,
            "uncoveredLines": self.uncovered_lines,
            "conditionsToCover": self.conditions_to_cover,
            "uncoveredConditions": self.uncovered_conditions,
            "meets100Percent": self.meets_100_percent,
        }
    
    @property
    def meets_100_percent(self) -> bool:
        """Check if coverage meets 100% target."""
        return self.line_coverage >= 100 and self.branch_coverage >= 100


@dataclass
class QualityGateCondition:
    """A quality gate condition."""
    metric: str
    operator: str
    value: str
    status: str
    actual_value: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric,
            "operator": self.operator,
            "threshold": self.value,
            "status": self.status,
            "actualValue": self.actual_value,
        }


@dataclass
class FixPlan:
    """A plan to fix SonarCloud issues."""
    issue: SonarIssue
    fix_description: str
    fix_steps: List[str]
    estimated_effort: str
    priority: int  # 1 = highest
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue": self.issue.to_dict(),
            "fixDescription": self.fix_description,
            "fixSteps": self.fix_steps,
            "estimatedEffort": self.estimated_effort,
            "priority": self.priority,
        }


@dataclass
class SonarValidationResult:
    """Result from Sonar validation."""
    status: str  # success, warning, error
    quality_gate_status: str
    issues: List[SonarIssue] = field(default_factory=list)
    duplications: List[DuplicationBlock] = field(default_factory=list)
    coverage: Optional[CoverageMetrics] = None
    quality_gate_conditions: List[QualityGateCondition] = field(default_factory=list)
    fix_plans: List[FixPlan] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "qualityGateStatus": self.quality_gate_status,
            "issues": [i.to_dict() for i in self.issues],
            "duplications": [d.to_dict() for d in self.duplications],
            "coverage": self.coverage.to_dict() if self.coverage else None,
            "qualityGateConditions": [c.to_dict() for c in self.quality_gate_conditions],
            "fixPlans": [f.to_dict() for f in self.fix_plans],
            "summary": self.summary,
            "error": self.error,
        }


class SonarValidationAgent:
    """
    Agent for validating code against SonarCloud quality gates.
    
    This agent:
    - Reads pipeline configuration files
    - Checks SonarCloud dashboard for issues
    - Analyzes code for potential Sonar violations
    - Provides fix plans to maintain 0 errors, 0 duplication, 100% coverage
    """
    
    SONARCLOUD_API_BASE = "https://sonarcloud.io/api"
    
    # Common Sonar rules and their fixes
    RULE_FIXES = {
        "typescript:S1854": {
            "description": "Remove unused variable assignment",
            "steps": ["Remove the unused variable", "Or use the variable if it was intended"],
        },
        "typescript:S1481": {
            "description": "Remove unused local variable",
            "steps": ["Delete the unused variable declaration", "Or prefix with underscore if intentionally unused"],
        },
        "typescript:S6606": {
            "description": "Use nullish coalescing operator",
            "steps": ["Replace || with ?? for null/undefined checks", "Ensure the fallback is appropriate"],
        },
        "typescript:S6582": {
            "description": "Use optional chaining",
            "steps": ["Replace && chains with ?.", "Example: obj && obj.prop -> obj?.prop"],
        },
        "typescript:S3776": {
            "description": "Reduce cognitive complexity",
            "steps": [
                "Extract complex conditions into named functions",
                "Split large functions into smaller ones",
                "Use early returns to reduce nesting",
            ],
        },
        "typescript:S1128": {
            "description": "Remove unused imports",
            "steps": ["Delete the unused import statement", "Run ESLint auto-fix: npx eslint --fix"],
        },
        "typescript:S6544": {
            "description": "Avoid async functions without await",
            "steps": ["Add await to async operations", "Or remove async keyword if not needed"],
        },
        "typescript:S6747": {
            "description": "Use proper React key prop",
            "steps": ["Add unique key prop to list items", "Use stable IDs, not array indices"],
        },
        "javascript:S3358": {
            "description": "Simplify nested ternary expressions",
            "steps": ["Extract to if/else or switch statement", "Or use a lookup object"],
        },
        "css:S4666": {
            "description": "Remove duplicate CSS properties",
            "steps": ["Remove the duplicate property", "Keep only the intended value"],
        },
    }
    
    def __init__(
        self,
        token: Optional[str] = None,
        organization: str = "pandora-jewelry",
        project_key: str = "pandora-jewelry_spark_pandora-group"
    ):
        """
        Initialize the Sonar Validation Agent.
        
        Args:
            token: SonarCloud API token (reads from SONAR_TOKEN env var if not provided)
            organization: SonarCloud organization
            project_key: SonarCloud project key
        """
        self.token = token or os.environ.get("SONAR_TOKEN")
        self.organization = organization
        self.project_key = project_key
        
        # HTTP client for API calls
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        self.client = httpx.Client(
            headers=headers,
            timeout=30.0,
        )
    
    def fetch_project_status(self, branch: str = "master") -> Dict[str, Any]:
        """
        Fetch project quality gate status from SonarCloud.
        
        Args:
            branch: Branch to check (default: master)
            
        Returns:
            Quality gate status and metrics
        """
        try:
            response = self.client.get(
                f"{self.SONARCLOUD_API_BASE}/qualitygates/project_status",
                params={
                    "projectKey": self.project_key,
                    "branch": branch,
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def fetch_issues(
        self,
        branch: str = "master",
        severities: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        resolved: bool = False
    ) -> List[SonarIssue]:
        """
        Fetch issues from SonarCloud.
        
        Args:
            branch: Branch to check
            severities: Filter by severity levels
            types: Filter by issue types
            resolved: Include resolved issues
            
        Returns:
            List of SonarIssue objects
        """
        issues = []
        
        try:
            params = {
                "componentKeys": self.project_key,
                "branch": branch,
                "resolved": str(resolved).lower(),
                "ps": 500,  # Page size
            }
            
            if severities:
                params["severities"] = ",".join(severities)
            if types:
                params["types"] = ",".join(types)
            
            response = self.client.get(
                f"{self.SONARCLOUD_API_BASE}/issues/search",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            for issue_data in data.get("issues", []):
                issues.append(SonarIssue(
                    key=issue_data.get("key", ""),
                    rule=issue_data.get("rule", ""),
                    severity=issue_data.get("severity", ""),
                    component=issue_data.get("component", ""),
                    line=issue_data.get("line"),
                    message=issue_data.get("message", ""),
                    type=issue_data.get("type", ""),
                    effort=issue_data.get("effort"),
                    debt=issue_data.get("debt"),
                ))
                
        except Exception as e:
            print(f"Error fetching issues: {e}")
        
        return issues
    
    def fetch_duplications(self, branch: str = "master") -> List[DuplicationBlock]:
        """
        Fetch code duplications from SonarCloud.
        
        Args:
            branch: Branch to check
            
        Returns:
            List of DuplicationBlock objects
        """
        duplications = []
        
        try:
            response = self.client.get(
                f"{self.SONARCLOUD_API_BASE}/measures/component",
                params={
                    "component": self.project_key,
                    "branch": branch,
                    "metricKeys": "duplicated_lines,duplicated_blocks,duplicated_files,duplicated_lines_density",
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse duplication metrics
            measures = data.get("component", {}).get("measures", [])
            for measure in measures:
                if measure.get("metric") == "duplicated_blocks" and int(measure.get("value", 0)) > 0:
                    # Fetch detailed duplication info
                    dup_response = self.client.get(
                        f"{self.SONARCLOUD_API_BASE}/duplications/show",
                        params={
                            "key": self.project_key,
                            "branch": branch,
                        }
                    )
                    if dup_response.status_code == 200:
                        dup_data = dup_response.json()
                        for dup in dup_data.get("duplications", []):
                            for block in dup.get("blocks", []):
                                duplications.append(DuplicationBlock(
                                    file=block.get("_ref", ""),
                                    start_line=block.get("from", 0),
                                    end_line=block.get("from", 0) + block.get("size", 0),
                                    duplicated_lines=block.get("size", 0),
                                ))
                    break
                    
        except Exception as e:
            print(f"Error fetching duplications: {e}")
        
        return duplications
    
    def fetch_coverage(self, branch: str = "master") -> CoverageMetrics:
        """
        Fetch coverage metrics from SonarCloud.
        
        Args:
            branch: Branch to check
            
        Returns:
            CoverageMetrics object
        """
        coverage = CoverageMetrics()
        
        try:
            response = self.client.get(
                f"{self.SONARCLOUD_API_BASE}/measures/component",
                params={
                    "component": self.project_key,
                    "branch": branch,
                    "metricKeys": "coverage,line_coverage,branch_coverage,lines_to_cover,uncovered_lines,conditions_to_cover,uncovered_conditions",
                }
            )
            response.raise_for_status()
            data = response.json()
            
            measures = data.get("component", {}).get("measures", [])
            for measure in measures:
                metric = measure.get("metric")
                value = measure.get("value", "0")
                
                if metric == "line_coverage":
                    coverage.line_coverage = float(value)
                elif metric == "branch_coverage":
                    coverage.branch_coverage = float(value)
                elif metric == "lines_to_cover":
                    coverage.lines_to_cover = int(value)
                elif metric == "uncovered_lines":
                    coverage.uncovered_lines = int(value)
                elif metric == "conditions_to_cover":
                    coverage.conditions_to_cover = int(value)
                elif metric == "uncovered_conditions":
                    coverage.uncovered_conditions = int(value)
                    
        except Exception as e:
            print(f"Error fetching coverage: {e}")
        
        return coverage
    
    def analyze_pipeline_files(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze pipeline configuration files for Sonar settings.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Pipeline analysis results
        """
        analysis = {
            "sonarConfigFound": False,
            "sonarProjectKey": None,
            "sonarOrganization": None,
            "qualityGateId": None,
            "exclusions": [],
            "inclusions": [],
            "coverageReportPaths": [],
            "pipelineFiles": [],
        }
        
        repo = Path(repo_path)
        
        # Check for sonar-project.properties
        sonar_props = repo / "sonar-project.properties"
        if sonar_props.exists():
            analysis["sonarConfigFound"] = True
            analysis["pipelineFiles"].append(str(sonar_props))
            
            with open(sonar_props, 'r') as f:
                content = f.read()
                
            # Parse properties
            for line in content.split('\n'):
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "sonar.projectKey":
                        analysis["sonarProjectKey"] = value
                    elif key == "sonar.organization":
                        analysis["sonarOrganization"] = value
                    elif key == "sonar.qualitygate":
                        analysis["qualityGateId"] = value
                    elif key == "sonar.exclusions":
                        analysis["exclusions"] = value.split(',')
                    elif key == "sonar.inclusions":
                        analysis["inclusions"] = value.split(',')
                    elif "coverage" in key.lower() and "path" in key.lower():
                        analysis["coverageReportPaths"].append(value)
        
        # Check for azure-pipelines.yml
        azure_pipeline = repo / "azure-pipelines.yml"
        if azure_pipeline.exists():
            analysis["pipelineFiles"].append(str(azure_pipeline))
            
            with open(azure_pipeline, 'r') as f:
                content = f.read()
            
            # Check for SonarCloud tasks
            if "SonarCloudPrepare" in content or "SonarCloudAnalyze" in content:
                analysis["sonarConfigFound"] = True
        
        # Check for GitHub Actions
        github_workflows = repo / ".github" / "workflows"
        if github_workflows.exists():
            for workflow_file in github_workflows.glob("*.yml"):
                analysis["pipelineFiles"].append(str(workflow_file))
                
                with open(workflow_file, 'r') as f:
                    content = f.read()
                
                if "sonarcloud" in content.lower() or "sonar" in content.lower():
                    analysis["sonarConfigFound"] = True
        
        return analysis
    
    def generate_fix_plan(self, issue: SonarIssue) -> FixPlan:
        """
        Generate a fix plan for a SonarCloud issue.
        
        Args:
            issue: SonarIssue to fix
            
        Returns:
            FixPlan with steps to resolve the issue
        """
        # Get known fix for the rule
        rule_fix = self.RULE_FIXES.get(issue.rule, {})
        
        if rule_fix:
            fix_description = rule_fix.get("description", f"Fix {issue.rule}")
            fix_steps = rule_fix.get("steps", [])
        else:
            # Generate generic fix based on issue type
            fix_description = f"Fix {issue.type.lower()}: {issue.message}"
            fix_steps = self._generate_generic_fix_steps(issue)
        
        # Determine priority based on severity
        priority_map = {
            "BLOCKER": 1,
            "CRITICAL": 2,
            "MAJOR": 3,
            "MINOR": 4,
            "INFO": 5,
        }
        priority = priority_map.get(issue.severity, 5)
        
        return FixPlan(
            issue=issue,
            fix_description=fix_description,
            fix_steps=fix_steps,
            estimated_effort=issue.effort or "5min",
            priority=priority,
        )
    
    def _generate_generic_fix_steps(self, issue: SonarIssue) -> List[str]:
        """Generate generic fix steps based on issue type."""
        steps = []
        
        if issue.type == "BUG":
            steps = [
                f"Review the code at {issue.component}:{issue.line}",
                "Identify the root cause of the bug",
                "Apply the appropriate fix",
                "Add unit tests to prevent regression",
            ]
        elif issue.type == "VULNERABILITY":
            steps = [
                f"Review the security issue at {issue.component}:{issue.line}",
                "Understand the vulnerability and its impact",
                "Apply security best practices to fix",
                "Validate the fix doesn't introduce new vulnerabilities",
            ]
        elif issue.type == "CODE_SMELL":
            steps = [
                f"Review the code smell at {issue.component}:{issue.line}",
                "Refactor the code to improve maintainability",
                "Ensure tests still pass after refactoring",
            ]
        elif issue.type == "SECURITY_HOTSPOT":
            steps = [
                f"Review the security hotspot at {issue.component}:{issue.line}",
                "Determine if the code is actually vulnerable",
                "If vulnerable, apply appropriate security measures",
                "Mark as reviewed in SonarCloud if safe",
            ]
        else:
            steps = [
                f"Review the issue at {issue.component}:{issue.line}",
                f"Address the issue: {issue.message}",
            ]
        
        return steps
    
    def validate(
        self,
        branch: str = "master",
        repo_path: Optional[str] = None
    ) -> SonarValidationResult:
        """
        Perform full Sonar validation.
        
        Args:
            branch: Branch to validate
            repo_path: Optional path to repository for pipeline analysis
            
        Returns:
            SonarValidationResult with all findings and fix plans
        """
        result = SonarValidationResult(
            status="success",
            quality_gate_status="UNKNOWN",
        )
        
        # Fetch quality gate status
        qg_status = self.fetch_project_status(branch)
        if "error" not in qg_status:
            project_status = qg_status.get("projectStatus", {})
            result.quality_gate_status = project_status.get("status", "UNKNOWN")
            
            # Parse quality gate conditions
            for condition in project_status.get("conditions", []):
                result.quality_gate_conditions.append(QualityGateCondition(
                    metric=condition.get("metricKey", ""),
                    operator=condition.get("comparator", ""),
                    value=condition.get("errorThreshold", ""),
                    status=condition.get("status", ""),
                    actual_value=condition.get("actualValue", ""),
                ))
        
        # Fetch issues
        result.issues = self.fetch_issues(branch)
        
        # Fetch duplications
        result.duplications = self.fetch_duplications(branch)
        
        # Fetch coverage
        result.coverage = self.fetch_coverage(branch)
        
        # Generate fix plans for all issues
        for issue in result.issues:
            fix_plan = self.generate_fix_plan(issue)
            result.fix_plans.append(fix_plan)
        
        # Sort fix plans by priority
        result.fix_plans.sort(key=lambda x: x.priority)
        
        # Generate summary
        result.summary = {
            "totalIssues": len(result.issues),
            "blockers": len([i for i in result.issues if i.severity == "BLOCKER"]),
            "criticals": len([i for i in result.issues if i.severity == "CRITICAL"]),
            "majors": len([i for i in result.issues if i.severity == "MAJOR"]),
            "minors": len([i for i in result.issues if i.severity == "MINOR"]),
            "bugs": len([i for i in result.issues if i.type == "BUG"]),
            "vulnerabilities": len([i for i in result.issues if i.type == "VULNERABILITY"]),
            "codeSmells": len([i for i in result.issues if i.type == "CODE_SMELL"]),
            "duplicatedBlocks": len(result.duplications),
            "lineCoverage": result.coverage.line_coverage if result.coverage else 0,
            "branchCoverage": result.coverage.branch_coverage if result.coverage else 0,
            "qualityGatePassed": result.quality_gate_status == "OK",
        }
        
        # Determine overall status
        if result.quality_gate_status == "ERROR":
            result.status = "error"
        elif result.quality_gate_status == "WARN" or len(result.issues) > 0:
            result.status = "warning"
        else:
            result.status = "success"
        
        # Analyze pipeline files if repo path provided
        if repo_path:
            pipeline_analysis = self.analyze_pipeline_files(repo_path)
            result.summary["pipelineAnalysis"] = pipeline_analysis
        
        return result
    
    def generate_pr_checklist(self, result: SonarValidationResult) -> str:
        """
        Generate a PR checklist based on validation results.
        
        Args:
            result: SonarValidationResult
            
        Returns:
            Markdown checklist for PR
        """
        lines = ["## SonarCloud Pre-PR Checklist\n"]
        
        # Quality Gate Status
        status_emoji = {
            "OK": "pass",
            "WARN": "warning",
            "ERROR": "fail",
        }.get(result.quality_gate_status, "unknown")
        
        lines.append(f"### Quality Gate: {result.quality_gate_status}\n")
        
        # Issues to fix
        if result.issues:
            lines.append("### Issues to Fix Before PR\n")
            for i, plan in enumerate(result.fix_plans[:10], 1):  # Top 10 priority
                lines.append(f"- [ ] **{plan.issue.severity}** [{plan.issue.rule}] {plan.issue.message}")
                lines.append(f"  - File: `{plan.issue.component}`:{plan.issue.line}")
                lines.append(f"  - Fix: {plan.fix_description}")
        else:
            lines.append("### No Issues Found\n")
        
        # Coverage
        if result.coverage:
            lines.append("\n### Coverage Targets\n")
            lines.append(f"- [ ] Line Coverage: {result.coverage.line_coverage}% (target: 100%)")
            lines.append(f"- [ ] Branch Coverage: {result.coverage.branch_coverage}% (target: 100%)")
            
            if result.coverage.uncovered_lines > 0:
                lines.append(f"- [ ] Cover {result.coverage.uncovered_lines} uncovered lines")
        
        # Duplications
        if result.duplications:
            lines.append("\n### Duplications to Remove\n")
            for dup in result.duplications[:5]:
                lines.append(f"- [ ] Remove duplication in `{dup.file}` (lines {dup.start_line}-{dup.end_line})")
        
        return "\n".join(lines)
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the Sonar validation agent as part of a workflow.
        
        Args:
            context: Workflow context with task description and input data
            
        Returns:
            Workflow-compatible result
        """
        try:
            task_description = context.get("task_description", "")
            input_data = context.get("input_data", {})
            
            # Get branch to validate
            branch = input_data.get("branch", "master")
            repo_path = input_data.get("repo_path")
            
            # Run validation
            result = self.validate(branch, repo_path)
            
            # Generate PR checklist
            checklist = self.generate_pr_checklist(result)
            
            # Add checklist to result
            result_dict = result.to_dict()
            result_dict["prChecklist"] = checklist
            
            return {
                "status": result.status,
                "data": result_dict,
                "next": "review" if result.status == "success" else None,
                "error": result.error,
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
    Convenience function to run the Sonar Validation Agent.
    
    Args:
        context: Workflow context
        
    Returns:
        Workflow-compatible result
    """
    agent = SonarValidationAgent()
    return agent.run(context)


def validate_for_pr(
    branch: str = "master",
    repo_path: Optional[str] = None,
    project_key: str = "pandora-jewelry_spark_pandora-group"
) -> Dict[str, Any]:
    """
    Validate code for PR readiness.
    
    Args:
        branch: Branch to validate
        repo_path: Path to repository
        project_key: SonarCloud project key
        
    Returns:
        Validation results with fix plans
    """
    agent = SonarValidationAgent(project_key=project_key)
    result = agent.validate(branch, repo_path)
    
    return {
        "result": result.to_dict(),
        "checklist": agent.generate_pr_checklist(result),
        "readyForPR": result.status == "success" and result.quality_gate_status == "OK",
    }
