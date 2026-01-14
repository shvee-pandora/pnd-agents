"""
PR Review Agent

A reusable agent for reviewing Pull Requests from Azure DevOps.
Provides structured, role-aware PR reviews based on detected tech stack.

Key capabilities:
1. PR ACCESS: Fetch PR metadata, changed files, and diffs from Azure DevOps
2. TECH STACK DETECTION: Automatically identify Frontend, Backend, QA, Infra
3. ROLE-AWARE REVIEW: Support FE, QA, Platform, and General review modes
4. STRUCTURED OUTPUT: Summary, Code Quality, Risk Analysis, Test Coverage, Recommendations
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from tools.azure_devops_pr_client import (
    AzureDevOpsPRClient,
    PRReviewData,
    PRFileChange,
    PRDiff,
)

logger = logging.getLogger("pnd_agents.pr_review_agent")


class ReviewRole(Enum):
    """Review role/persona for the PR review."""
    GENERAL = "general"
    FRONTEND = "fe"
    QA = "qa"
    PLATFORM = "platform"
    BACKEND = "backend"


class TechStack(Enum):
    """Detected technology stack."""
    FRONTEND_REACT = "frontend_react"
    FRONTEND_NEXTJS = "frontend_nextjs"
    FRONTEND_CHAKRA = "frontend_chakra"
    FRONTEND_PWA_KIT = "frontend_pwa_kit"
    BACKEND_NODE = "backend_node"
    BACKEND_JAVA = "backend_java"
    BACKEND_DOTNET = "backend_dotnet"
    BACKEND_SFCC = "backend_sfcc"
    QA_CYPRESS = "qa_cypress"
    QA_PLAYWRIGHT = "qa_playwright"
    QA_JEST = "qa_jest"
    INFRA_YAML = "infra_yaml"
    INFRA_PIPELINE = "infra_pipeline"
    INFRA_DOCKER = "infra_docker"
    UNKNOWN = "unknown"


class Severity(Enum):
    """Finding severity level."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ReviewFinding:
    """A single finding from the PR review."""
    category: str
    title: str
    description: str
    severity: Severity
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "filePath": self.file_path,
            "lineNumber": self.line_number,
            "suggestion": self.suggestion,
        }


@dataclass
class TechStackAnalysis:
    """Result of tech stack detection."""
    detected_stacks: List[TechStack] = field(default_factory=list)
    primary_stack: TechStack = TechStack.UNKNOWN
    confidence: float = 0.0
    evidence: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "detectedStacks": [s.value for s in self.detected_stacks],
            "primaryStack": self.primary_stack.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class PRReviewResult:
    """Complete PR review result."""
    pr_url: str
    pr_id: int
    title: str
    role: ReviewRole
    tech_stack: TechStackAnalysis
    summary: str
    scope_and_impact: str
    code_quality: Dict[str, Any] = field(default_factory=dict)
    risk_analysis: Dict[str, Any] = field(default_factory=dict)
    test_coverage: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    findings: List[ReviewFinding] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def high_severity_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)
    
    @property
    def medium_severity_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)
    
    @property
    def low_severity_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.LOW)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prUrl": self.pr_url,
            "prId": self.pr_id,
            "title": self.title,
            "role": self.role.value,
            "techStack": self.tech_stack.to_dict(),
            "summary": self.summary,
            "scopeAndImpact": self.scope_and_impact,
            "codeQuality": self.code_quality,
            "riskAnalysis": self.risk_analysis,
            "testCoverage": self.test_coverage,
            "architecture": self.architecture,
            "findings": [f.to_dict() for f in self.findings],
            "recommendations": self.recommendations,
            "severityCounts": {
                "high": self.high_severity_count,
                "medium": self.medium_severity_count,
                "low": self.low_severity_count,
            },
        }
    
    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            f"# PR Review: {self.title}",
            "",
            f"**PR ID:** {self.pr_id}",
            f"**Review Role:** {self.role.value.upper()}",
            f"**Tech Stack:** {self.tech_stack.primary_stack.value}",
            "",
            "---",
            "",
            "## 1. Summary",
            "",
            self.summary,
            "",
            "### Scope and Impact",
            "",
            self.scope_and_impact,
            "",
            "---",
            "",
            "## 2. Code Quality Review",
            "",
        ]
        
        if self.code_quality:
            lines.append(f"**Readability:** {self.code_quality.get('readability', 'N/A')}")
            lines.append(f"**Maintainability:** {self.code_quality.get('maintainability', 'N/A')}")
            lines.append(f"**Best Practices:** {self.code_quality.get('bestPractices', 'N/A')}")
            if self.code_quality.get("notes"):
                lines.append("")
                lines.append("**Notes:**")
                for note in self.code_quality.get("notes", []):
                    lines.append(f"- {note}")
        
        lines.extend([
            "",
            "---",
            "",
            "## 3. Risk Analysis",
            "",
        ])
        
        if self.risk_analysis:
            lines.append(f"**Breaking Changes:** {self.risk_analysis.get('breakingChanges', 'None identified')}")
            lines.append(f"**Performance Risks:** {self.risk_analysis.get('performanceRisks', 'None identified')}")
            lines.append(f"**Security Concerns:** {self.risk_analysis.get('securityConcerns', 'None identified')}")
        
        lines.extend([
            "",
            "---",
            "",
            "## 4. Test Coverage Review",
            "",
        ])
        
        if self.test_coverage:
            lines.append(f"**Existing Tests:** {self.test_coverage.get('existingTests', 'N/A')}")
            lines.append(f"**Missing Tests:** {self.test_coverage.get('missingTests', 'N/A')}")
            if self.test_coverage.get("cypressCoverage"):
                lines.append(f"**Cypress Coverage:** {self.test_coverage.get('cypressCoverage', 'N/A')}")
        
        lines.extend([
            "",
            "---",
            "",
            "## 5. Architecture & Standards",
            "",
        ])
        
        if self.architecture:
            lines.append(f"**Design Consistency:** {self.architecture.get('designConsistency', 'N/A')}")
            lines.append(f"**Pandora Standards:** {self.architecture.get('pandoraStandards', 'N/A')}")
            lines.append(f"**Tech Debt:** {self.architecture.get('techDebt', 'None introduced')}")
        
        lines.extend([
            "",
            "---",
            "",
            "## 6. Findings",
            "",
            f"**High:** {self.high_severity_count} | **Medium:** {self.medium_severity_count} | **Low:** {self.low_severity_count}",
            "",
        ])
        
        if self.findings:
            for finding in self.findings:
                severity_emoji = {"high": "!!!", "medium": "!!", "low": "!"}[finding.severity.value]
                lines.append(f"### [{severity_emoji}] {finding.title}")
                lines.append("")
                lines.append(f"**Category:** {finding.category}")
                if finding.file_path:
                    location = finding.file_path
                    if finding.line_number:
                        location += f":{finding.line_number}"
                    lines.append(f"**Location:** `{location}`")
                lines.append("")
                lines.append(finding.description)
                if finding.suggestion:
                    lines.append("")
                    lines.append(f"**Suggestion:** {finding.suggestion}")
                lines.append("")
        else:
            lines.append("No significant findings.")
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "## 7. Actionable Recommendations",
            "",
        ])
        
        if self.recommendations:
            for i, rec in enumerate(self.recommendations, 1):
                severity = rec.get("severity", "medium").upper()
                lines.append(f"{i}. **[{severity}]** {rec.get('title', 'Recommendation')}")
                lines.append(f"   {rec.get('description', '')}")
                lines.append("")
        else:
            lines.append("No specific recommendations at this time.")
        
        return "\n".join(lines)


class TechStackDetector:
    """Detects technology stack from PR file changes."""
    
    FRONTEND_EXTENSIONS = {".tsx", ".jsx", ".ts", ".js", ".css", ".scss", ".less"}
    BACKEND_EXTENSIONS = {".java", ".cs", ".py", ".go", ".rb"}
    CONFIG_EXTENSIONS = {".yaml", ".yml", ".json", ".xml", ".toml"}
    TEST_EXTENSIONS = {".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js", ".spec.js"}
    
    FRONTEND_PATTERNS = {
        TechStack.FRONTEND_REACT: [
            r"import.*from\s+['\"]react['\"]",
            r"React\.(Component|FC|useState|useEffect)",
            r"\.tsx$",
            r"\.jsx$",
        ],
        TechStack.FRONTEND_NEXTJS: [
            r"import.*from\s+['\"]next",
            r"getServerSideProps",
            r"getStaticProps",
            r"useRouter.*next/router",
            r"next\.config\.",
            r"app/.*page\.tsx",
            r"pages/.*\.tsx",
        ],
        TechStack.FRONTEND_CHAKRA: [
            r"import.*from\s+['\"]@chakra-ui",
            r"ChakraProvider",
            r"useColorMode",
        ],
        TechStack.FRONTEND_PWA_KIT: [
            r"@salesforce/pwa-kit",
            r"commerce-sdk",
            r"pwa-kit",
        ],
    }
    
    BACKEND_PATTERNS = {
        TechStack.BACKEND_NODE: [
            r"import.*from\s+['\"]express['\"]",
            r"require\(['\"]express['\"]",
            r"package\.json",
            r"node_modules",
        ],
        TechStack.BACKEND_JAVA: [
            r"\.java$",
            r"import\s+java\.",
            r"@SpringBoot",
            r"pom\.xml",
            r"build\.gradle",
        ],
        TechStack.BACKEND_DOTNET: [
            r"\.cs$",
            r"\.csproj$",
            r"using\s+System",
            r"namespace\s+\w+",
        ],
        TechStack.BACKEND_SFCC: [
            r"dw/",
            r"cartridge",
            r"\.ds$",
            r"SFCC",
            r"Salesforce Commerce Cloud",
        ],
    }
    
    QA_PATTERNS = {
        TechStack.QA_CYPRESS: [
            r"cypress",
            r"cy\.(visit|get|contains|click)",
            r"\.cy\.(ts|js)$",
            r"cypress\.config",
        ],
        TechStack.QA_PLAYWRIGHT: [
            r"playwright",
            r"@playwright/test",
            r"page\.(goto|click|fill)",
            r"\.spec\.(ts|js)$",
        ],
        TechStack.QA_JEST: [
            r"jest",
            r"describe\s*\(",
            r"it\s*\(",
            r"expect\s*\(",
            r"\.test\.(ts|tsx|js|jsx)$",
        ],
    }
    
    INFRA_PATTERNS = {
        TechStack.INFRA_YAML: [
            r"\.ya?ml$",
        ],
        TechStack.INFRA_PIPELINE: [
            r"azure-pipelines",
            r"\.github/workflows",
            r"Jenkinsfile",
            r"\.gitlab-ci",
        ],
        TechStack.INFRA_DOCKER: [
            r"Dockerfile",
            r"docker-compose",
            r"\.dockerignore",
        ],
    }
    
    def detect(self, files: List[PRFileChange], diffs: List[PRDiff]) -> TechStackAnalysis:
        """
        Detect tech stack from PR files and diffs.
        
        Args:
            files: List of changed files
            diffs: List of file diffs
            
        Returns:
            TechStackAnalysis with detected stacks
        """
        detected: Set[TechStack] = set()
        evidence: Dict[str, List[str]] = {}
        
        all_content = ""
        for diff in diffs:
            for block in diff.blocks:
                if isinstance(block.get("content"), str):
                    all_content += block["content"] + "\n"
                if isinstance(block.get("newContent"), str):
                    all_content += block["newContent"] + "\n"
        
        all_paths = [f.path for f in files]
        all_paths_str = "\n".join(all_paths)
        
        for stack, patterns in self.FRONTEND_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, all_content, re.IGNORECASE) or re.search(pattern, all_paths_str):
                    detected.add(stack)
                    evidence.setdefault(stack.value, []).append(f"Pattern: {pattern}")
        
        for stack, patterns in self.BACKEND_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, all_content, re.IGNORECASE) or re.search(pattern, all_paths_str):
                    detected.add(stack)
                    evidence.setdefault(stack.value, []).append(f"Pattern: {pattern}")
        
        for stack, patterns in self.QA_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, all_content, re.IGNORECASE) or re.search(pattern, all_paths_str):
                    detected.add(stack)
                    evidence.setdefault(stack.value, []).append(f"Pattern: {pattern}")
        
        for stack, patterns in self.INFRA_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, all_content, re.IGNORECASE) or re.search(pattern, all_paths_str):
                    detected.add(stack)
                    evidence.setdefault(stack.value, []).append(f"Pattern: {pattern}")
        
        primary = self._determine_primary_stack(detected, files)
        confidence = min(1.0, len(detected) * 0.2 + 0.3) if detected else 0.0
        
        return TechStackAnalysis(
            detected_stacks=list(detected),
            primary_stack=primary,
            confidence=confidence,
            evidence=evidence,
        )
    
    def _determine_primary_stack(
        self,
        detected: Set[TechStack],
        files: List[PRFileChange],
    ) -> TechStack:
        """Determine the primary tech stack based on file counts."""
        if not detected:
            return TechStack.UNKNOWN
        
        frontend_count = sum(1 for f in files if Path(f.path).suffix in self.FRONTEND_EXTENSIONS)
        backend_count = sum(1 for f in files if Path(f.path).suffix in self.BACKEND_EXTENSIONS)
        config_count = sum(1 for f in files if Path(f.path).suffix in self.CONFIG_EXTENSIONS)
        test_count = sum(1 for f in files if any(f.path.endswith(ext) for ext in [".test.ts", ".test.tsx", ".spec.ts", ".cy.ts"]))
        
        if test_count > frontend_count and test_count > backend_count:
            for stack in [TechStack.QA_CYPRESS, TechStack.QA_PLAYWRIGHT, TechStack.QA_JEST]:
                if stack in detected:
                    return stack
        
        if frontend_count > backend_count:
            for stack in [TechStack.FRONTEND_NEXTJS, TechStack.FRONTEND_REACT, TechStack.FRONTEND_CHAKRA, TechStack.FRONTEND_PWA_KIT]:
                if stack in detected:
                    return stack
        
        if backend_count > 0:
            for stack in [TechStack.BACKEND_NODE, TechStack.BACKEND_JAVA, TechStack.BACKEND_DOTNET, TechStack.BACKEND_SFCC]:
                if stack in detected:
                    return stack
        
        if config_count > 0:
            for stack in [TechStack.INFRA_PIPELINE, TechStack.INFRA_DOCKER, TechStack.INFRA_YAML]:
                if stack in detected:
                    return stack
        
        return list(detected)[0] if detected else TechStack.UNKNOWN


class PRReviewAgent:
    """
    Agent for reviewing Pull Requests from Azure DevOps.
    
    Provides structured, role-aware PR reviews based on detected tech stack.
    
    Example usage:
        agent = PRReviewAgent()
        result = agent.review_pr(
            "https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034",
            role=ReviewRole.FRONTEND
        )
        print(result.to_markdown())
    """
    
    def __init__(self):
        """Initialize the PR Review Agent."""
        self.pr_client = AzureDevOpsPRClient()
        self.stack_detector = TechStackDetector()
    
    def close(self):
        """Close resources."""
        self.pr_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def review_pr(
        self,
        pr_url: str,
        role: Optional[ReviewRole] = None,
    ) -> PRReviewResult:
        """
        Review a Pull Request.
        
        Args:
            pr_url: Azure DevOps PR URL
            role: Review role/persona (defaults to GENERAL)
            
        Returns:
            PRReviewResult with complete review
        """
        if role is None:
            role = ReviewRole.GENERAL
        
        logger.info(f"Reviewing PR: {pr_url} with role: {role.value}")
        
        pr_data = self.pr_client.get_pr_for_review(pr_url)
        
        tech_stack = self.stack_detector.detect(pr_data.files, pr_data.diffs)
        
        if role == ReviewRole.GENERAL:
            role = self._suggest_role_from_stack(tech_stack)
        
        summary = self._generate_summary(pr_data)
        scope_impact = self._analyze_scope_and_impact(pr_data)
        code_quality = self._analyze_code_quality(pr_data, role)
        risk_analysis = self._analyze_risks(pr_data, role)
        test_coverage = self._analyze_test_coverage(pr_data, role)
        architecture = self._analyze_architecture(pr_data, role)
        findings = self._generate_findings(pr_data, role, tech_stack)
        recommendations = self._generate_recommendations(findings, role)
        
        return PRReviewResult(
            pr_url=pr_url,
            pr_id=pr_data.metadata.pr_id,
            title=pr_data.metadata.title,
            role=role,
            tech_stack=tech_stack,
            summary=summary,
            scope_and_impact=scope_impact,
            code_quality=code_quality,
            risk_analysis=risk_analysis,
            test_coverage=test_coverage,
            architecture=architecture,
            findings=findings,
            recommendations=recommendations,
        )
    
    def _suggest_role_from_stack(self, tech_stack: TechStackAnalysis) -> ReviewRole:
        """Suggest review role based on detected tech stack."""
        primary = tech_stack.primary_stack
        
        if primary in [TechStack.FRONTEND_REACT, TechStack.FRONTEND_NEXTJS, TechStack.FRONTEND_CHAKRA, TechStack.FRONTEND_PWA_KIT]:
            return ReviewRole.FRONTEND
        elif primary in [TechStack.QA_CYPRESS, TechStack.QA_PLAYWRIGHT, TechStack.QA_JEST]:
            return ReviewRole.QA
        elif primary in [TechStack.BACKEND_NODE, TechStack.BACKEND_JAVA, TechStack.BACKEND_DOTNET, TechStack.BACKEND_SFCC]:
            return ReviewRole.BACKEND
        elif primary in [TechStack.INFRA_YAML, TechStack.INFRA_PIPELINE, TechStack.INFRA_DOCKER]:
            return ReviewRole.PLATFORM
        
        return ReviewRole.GENERAL
    
    def _generate_summary(self, pr_data: PRReviewData) -> str:
        """Generate PR summary."""
        metadata = pr_data.metadata
        
        summary_parts = [
            f"This PR ({metadata.pr_id}) titled '{metadata.title}' was created by {metadata.created_by}.",
            f"It proposes to merge '{metadata.source_branch}' into '{metadata.target_branch}'.",
            f"The PR modifies {pr_data.total_files_changed} file(s): {pr_data.files_added} added, {pr_data.files_modified} modified, {pr_data.files_deleted} deleted.",
        ]
        
        if metadata.description:
            desc_preview = metadata.description[:200]
            if len(metadata.description) > 200:
                desc_preview += "..."
            summary_parts.append(f"Description: {desc_preview}")
        
        return " ".join(summary_parts)
    
    def _analyze_scope_and_impact(self, pr_data: PRReviewData) -> str:
        """Analyze PR scope and potential impact."""
        impact_areas = []
        
        for file in pr_data.files:
            path = file.path.lower()
            if "component" in path or "ui" in path:
                impact_areas.append("UI Components")
            elif "api" in path or "service" in path:
                impact_areas.append("API/Services")
            elif "test" in path or "spec" in path or "cy" in path:
                impact_areas.append("Tests")
            elif "config" in path or "pipeline" in path:
                impact_areas.append("Configuration/CI")
            elif "style" in path or "css" in path or "scss" in path:
                impact_areas.append("Styling")
            elif "util" in path or "helper" in path:
                impact_areas.append("Utilities")
        
        unique_areas = list(set(impact_areas))
        
        if not unique_areas:
            return "General code changes with limited scope."
        
        scope = f"This PR impacts the following areas: {', '.join(unique_areas)}."
        
        if pr_data.total_files_changed > 20:
            scope += " This is a large PR that may require careful review."
        elif pr_data.total_files_changed > 10:
            scope += " This is a medium-sized PR."
        else:
            scope += " This is a focused PR with limited scope."
        
        return scope
    
    def _analyze_code_quality(self, pr_data: PRReviewData, role: ReviewRole) -> Dict[str, Any]:
        """Analyze code quality aspects."""
        quality = {
            "readability": "Good",
            "maintainability": "Good",
            "bestPractices": "Followed",
            "notes": [],
        }
        
        for diff in pr_data.diffs:
            for block in diff.blocks:
                content = block.get("content", "") or block.get("newContent", "")
                if not content:
                    continue
                
                if "TODO" in content or "FIXME" in content:
                    quality["notes"].append(f"TODO/FIXME comment found in {diff.path}")
                
                if "console.log" in content and not diff.path.endswith((".test.ts", ".test.tsx", ".spec.ts")):
                    quality["notes"].append(f"console.log statement found in {diff.path}")
                
                if "any" in content and diff.path.endswith((".ts", ".tsx")):
                    if re.search(r":\s*any\b", content):
                        quality["notes"].append(f"TypeScript 'any' type usage in {diff.path}")
                
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if len(line) > 120:
                        quality["notes"].append(f"Long line (>{120} chars) in {diff.path}")
                        break
        
        if len(quality["notes"]) > 5:
            quality["readability"] = "Needs Improvement"
        elif len(quality["notes"]) > 2:
            quality["readability"] = "Acceptable"
        
        return quality
    
    def _analyze_risks(self, pr_data: PRReviewData, role: ReviewRole) -> Dict[str, Any]:
        """Analyze potential risks in the PR."""
        risks = {
            "breakingChanges": "None identified",
            "performanceRisks": "None identified",
            "securityConcerns": "None identified",
            "details": [],
        }
        
        for diff in pr_data.diffs:
            content = ""
            for block in diff.blocks:
                content += block.get("content", "") or block.get("newContent", "") or ""
            
            if re.search(r"(password|secret|api[_-]?key|token)\s*[:=]", content, re.IGNORECASE):
                risks["securityConcerns"] = "Potential sensitive data exposure"
                risks["details"].append(f"Possible sensitive data in {diff.path}")
            
            if re.search(r"dangerouslySetInnerHTML", content):
                risks["securityConcerns"] = "XSS risk with dangerouslySetInnerHTML"
                risks["details"].append(f"dangerouslySetInnerHTML usage in {diff.path}")
            
            if re.search(r"eval\s*\(", content):
                risks["securityConcerns"] = "eval() usage detected"
                risks["details"].append(f"eval() usage in {diff.path}")
            
            if re.search(r"while\s*\(\s*true\s*\)", content):
                risks["performanceRisks"] = "Potential infinite loop"
                risks["details"].append(f"Infinite loop pattern in {diff.path}")
            
            if re.search(r"\.forEach\s*\([^)]*\.forEach", content):
                risks["performanceRisks"] = "Nested loops detected"
                risks["details"].append(f"Nested forEach in {diff.path}")
        
        for file in pr_data.files:
            if file.is_deleted:
                if "index" in file.path.lower() or "main" in file.path.lower():
                    risks["breakingChanges"] = "Core file deletion"
                    risks["details"].append(f"Deleted core file: {file.path}")
            
            if "api" in file.path.lower() and file.is_modified:
                risks["breakingChanges"] = "API changes detected"
                risks["details"].append(f"API modification: {file.path}")
        
        return risks
    
    def _analyze_test_coverage(self, pr_data: PRReviewData, role: ReviewRole) -> Dict[str, Any]:
        """Analyze test coverage aspects."""
        coverage = {
            "existingTests": "None found",
            "missingTests": "Unable to determine",
            "cypressCoverage": None,
            "details": [],
        }
        
        test_files = []
        source_files = []
        cypress_files = []
        
        for file in pr_data.files:
            path = file.path.lower()
            if ".test." in path or ".spec." in path:
                test_files.append(file.path)
            elif ".cy." in path or "cypress" in path:
                cypress_files.append(file.path)
            elif path.endswith((".ts", ".tsx", ".js", ".jsx")) and "test" not in path:
                source_files.append(file.path)
        
        if test_files:
            coverage["existingTests"] = f"{len(test_files)} test file(s) modified"
            coverage["details"].extend([f"Test file: {f}" for f in test_files])
        
        if cypress_files:
            coverage["cypressCoverage"] = f"{len(cypress_files)} Cypress test file(s)"
            coverage["details"].extend([f"Cypress: {f}" for f in cypress_files])
        
        untested_sources = []
        for src in source_files:
            base_name = Path(src).stem
            has_test = any(base_name in t for t in test_files + cypress_files)
            if not has_test:
                untested_sources.append(src)
        
        if untested_sources:
            coverage["missingTests"] = f"{len(untested_sources)} source file(s) may need tests"
            if len(untested_sources) <= 5:
                coverage["details"].extend([f"May need tests: {f}" for f in untested_sources])
        elif source_files:
            coverage["missingTests"] = "All source files appear to have corresponding tests"
        
        return coverage
    
    def _analyze_architecture(self, pr_data: PRReviewData, role: ReviewRole) -> Dict[str, Any]:
        """Analyze architecture and standards compliance."""
        arch = {
            "designConsistency": "Consistent",
            "pandoraStandards": "Followed",
            "techDebt": "None introduced",
            "details": [],
        }
        
        for file in pr_data.files:
            path = file.path
            
            if path.endswith(".tsx") or path.endswith(".jsx"):
                name = Path(path).stem
                if name[0].islower() and not name.startswith("use"):
                    arch["details"].append(f"Component naming: {path} should be PascalCase")
                    arch["pandoraStandards"] = "Minor deviations"
            
            if path.endswith(".ts") and "use" in Path(path).stem.lower():
                name = Path(path).stem
                if not name.startswith("use"):
                    arch["details"].append(f"Hook naming: {path} should start with 'use'")
        
        for diff in pr_data.diffs:
            content = ""
            for block in diff.blocks:
                content += block.get("content", "") or block.get("newContent", "") or ""
            
            if re.search(r"interface\s+\w+", content) and diff.path.endswith((".ts", ".tsx")):
                if re.search(r"type\s+\w+\s*=", content):
                    arch["details"].append(f"Mixed interface/type usage in {diff.path}")
        
        if len(arch["details"]) > 3:
            arch["designConsistency"] = "Needs Review"
        
        return arch
    
    def _generate_findings(
        self,
        pr_data: PRReviewData,
        role: ReviewRole,
        tech_stack: TechStackAnalysis,
    ) -> List[ReviewFinding]:
        """Generate review findings based on role and tech stack."""
        findings = []
        
        for diff in pr_data.diffs:
            content = ""
            for block in diff.blocks:
                content += block.get("content", "") or block.get("newContent", "") or ""
            
            if not content:
                continue
            
            if re.search(r"(password|secret|api[_-]?key)\s*[:=]\s*['\"][^'\"]+['\"]", content, re.IGNORECASE):
                findings.append(ReviewFinding(
                    category="Security",
                    title="Hardcoded Credentials",
                    description="Potential hardcoded credentials detected. Use environment variables instead.",
                    severity=Severity.HIGH,
                    file_path=diff.path,
                    suggestion="Move sensitive values to environment variables or a secrets manager.",
                ))
            
            if "dangerouslySetInnerHTML" in content:
                findings.append(ReviewFinding(
                    category="Security",
                    title="XSS Risk",
                    description="dangerouslySetInnerHTML usage detected. Ensure content is properly sanitized.",
                    severity=Severity.HIGH,
                    file_path=diff.path,
                    suggestion="Use DOMPurify or similar library to sanitize HTML content.",
                ))
            
            if role in [ReviewRole.FRONTEND, ReviewRole.GENERAL]:
                if re.search(r"console\.(log|debug|info)\s*\(", content):
                    if not diff.path.endswith((".test.ts", ".test.tsx", ".spec.ts")):
                        findings.append(ReviewFinding(
                            category="Code Quality",
                            title="Console Statement",
                            description="Console statement found in production code.",
                            severity=Severity.LOW,
                            file_path=diff.path,
                            suggestion="Remove console statements or use a proper logging utility.",
                        ))
                
                if re.search(r":\s*any\b", content) and diff.path.endswith((".ts", ".tsx")):
                    findings.append(ReviewFinding(
                        category="TypeScript",
                        title="Any Type Usage",
                        description="TypeScript 'any' type usage reduces type safety.",
                        severity=Severity.MEDIUM,
                        file_path=diff.path,
                        suggestion="Replace 'any' with a proper type definition.",
                    ))
            
            if role in [ReviewRole.QA, ReviewRole.GENERAL]:
                if ".cy." in diff.path or "cypress" in diff.path.lower():
                    if re.search(r"cy\.wait\s*\(\s*\d{4,}\s*\)", content):
                        findings.append(ReviewFinding(
                            category="Test Quality",
                            title="Hard-coded Wait",
                            description="Hard-coded wait time in Cypress test. Use cy.intercept() or assertions instead.",
                            severity=Severity.MEDIUM,
                            file_path=diff.path,
                            suggestion="Replace cy.wait(ms) with cy.intercept() or assertion-based waiting.",
                        ))
            
            if role in [ReviewRole.PLATFORM, ReviewRole.GENERAL]:
                if diff.path.endswith((".yaml", ".yml")):
                    if "latest" in content:
                        findings.append(ReviewFinding(
                            category="Infrastructure",
                            title="Latest Tag Usage",
                            description="Using 'latest' tag in configuration. Pin to specific versions for reproducibility.",
                            severity=Severity.MEDIUM,
                            file_path=diff.path,
                            suggestion="Pin to a specific version instead of 'latest'.",
                        ))
        
        return findings[:20]
    
    def _generate_recommendations(
        self,
        findings: List[ReviewFinding],
        role: ReviewRole,
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on findings."""
        recommendations = []
        
        high_findings = [f for f in findings if f.severity == Severity.HIGH]
        medium_findings = [f for f in findings if f.severity == Severity.MEDIUM]
        
        for finding in high_findings:
            recommendations.append({
                "severity": "high",
                "title": f"Address: {finding.title}",
                "description": finding.suggestion or finding.description,
                "relatedFinding": finding.title,
            })
        
        for finding in medium_findings[:5]:
            recommendations.append({
                "severity": "medium",
                "title": f"Consider: {finding.title}",
                "description": finding.suggestion or finding.description,
                "relatedFinding": finding.title,
            })
        
        if role == ReviewRole.FRONTEND:
            recommendations.append({
                "severity": "low",
                "title": "Verify Accessibility",
                "description": "Ensure all interactive elements have proper ARIA labels and keyboard navigation.",
            })
        elif role == ReviewRole.QA:
            recommendations.append({
                "severity": "low",
                "title": "Review Test Coverage",
                "description": "Verify that all critical user flows are covered by tests.",
            })
        elif role == ReviewRole.PLATFORM:
            recommendations.append({
                "severity": "low",
                "title": "Verify Pipeline Configuration",
                "description": "Ensure CI/CD pipeline changes don't break existing workflows.",
            })
        
        return recommendations


def review_pr(pr_url: str, role: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to review a PR.
    
    Args:
        pr_url: Azure DevOps PR URL
        role: Review role (fe, qa, platform, backend, general)
        
    Returns:
        Dictionary with review results
    """
    review_role = ReviewRole.GENERAL
    if role:
        role_lower = role.lower()
        role_map = {
            "fe": ReviewRole.FRONTEND,
            "frontend": ReviewRole.FRONTEND,
            "qa": ReviewRole.QA,
            "platform": ReviewRole.PLATFORM,
            "backend": ReviewRole.BACKEND,
            "general": ReviewRole.GENERAL,
        }
        review_role = role_map.get(role_lower, ReviewRole.GENERAL)
    
    with PRReviewAgent() as agent:
        result = agent.review_pr(pr_url, review_role)
        return result.to_dict()


def review_pr_markdown(pr_url: str, role: Optional[str] = None) -> str:
    """
    Convenience function to review a PR and return markdown.
    
    Args:
        pr_url: Azure DevOps PR URL
        role: Review role (fe, qa, platform, backend, general)
        
    Returns:
        Markdown formatted review
    """
    review_role = ReviewRole.GENERAL
    if role:
        role_lower = role.lower()
        role_map = {
            "fe": ReviewRole.FRONTEND,
            "frontend": ReviewRole.FRONTEND,
            "qa": ReviewRole.QA,
            "platform": ReviewRole.PLATFORM,
            "backend": ReviewRole.BACKEND,
            "general": ReviewRole.GENERAL,
        }
        review_role = role_map.get(role_lower, ReviewRole.GENERAL)
    
    with PRReviewAgent() as agent:
        result = agent.review_pr(pr_url, review_role)
        return result.to_markdown()
