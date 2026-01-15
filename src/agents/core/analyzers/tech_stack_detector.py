"""
Tech Stack Detector

Shared utilities for detecting technology stacks in repositories.
Used by pr_review_agent, code_review, and other analysis agents.

Usage:
    from src.agents.core.analyzers.tech_stack_detector import TechStackDetector
    
    detector = TechStackDetector()
    stack = detector.detect("/path/to/repo")
    print(stack.frameworks)  # ['react', 'next.js']
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("pnd_agents.core.analyzers.tech_stack")


@dataclass
class TechStack:
    """Detected technology stack for a repository."""
    languages: Set[str] = field(default_factory=set)
    frameworks: Set[str] = field(default_factory=set)
    build_tools: Set[str] = field(default_factory=set)
    testing_frameworks: Set[str] = field(default_factory=set)
    package_managers: Set[str] = field(default_factory=set)
    ci_cd: Set[str] = field(default_factory=set)
    databases: Set[str] = field(default_factory=set)
    cloud_providers: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary with sorted lists."""
        return {
            "languages": sorted(self.languages),
            "frameworks": sorted(self.frameworks),
            "build_tools": sorted(self.build_tools),
            "testing_frameworks": sorted(self.testing_frameworks),
            "package_managers": sorted(self.package_managers),
            "ci_cd": sorted(self.ci_cd),
            "databases": sorted(self.databases),
            "cloud_providers": sorted(self.cloud_providers),
        }


# File patterns for detection
DETECTION_PATTERNS: Dict[str, Dict[str, Any]] = {
    # Languages
    "typescript": {"files": ["tsconfig.json", "*.ts", "*.tsx"], "category": "languages"},
    "javascript": {"files": ["*.js", "*.jsx", "*.mjs"], "category": "languages"},
    "python": {"files": ["*.py", "pyproject.toml", "setup.py"], "category": "languages"},
    "go": {"files": ["go.mod", "*.go"], "category": "languages"},
    "rust": {"files": ["Cargo.toml", "*.rs"], "category": "languages"},
    "java": {"files": ["pom.xml", "build.gradle", "*.java"], "category": "languages"},
    
    # Frameworks
    "react": {"files": ["package.json"], "content": ["react", "react-dom"], "category": "frameworks"},
    "next.js": {"files": ["next.config.js", "next.config.mjs"], "category": "frameworks"},
    "vue": {"files": ["vue.config.js"], "content": ["vue"], "category": "frameworks"},
    "angular": {"files": ["angular.json"], "category": "frameworks"},
    "express": {"content": ["express"], "category": "frameworks"},
    "fastapi": {"content": ["fastapi"], "category": "frameworks"},
    "django": {"files": ["manage.py"], "content": ["django"], "category": "frameworks"},
    
    # Testing
    "jest": {"files": ["jest.config.js", "jest.config.ts"], "content": ["jest"], "category": "testing_frameworks"},
    "pytest": {"files": ["pytest.ini", "conftest.py"], "content": ["pytest"], "category": "testing_frameworks"},
    "vitest": {"content": ["vitest"], "category": "testing_frameworks"},
    "playwright": {"content": ["playwright"], "category": "testing_frameworks"},
    
    # Build tools
    "webpack": {"files": ["webpack.config.js"], "content": ["webpack"], "category": "build_tools"},
    "vite": {"files": ["vite.config.js", "vite.config.ts"], "category": "build_tools"},
    "turbo": {"files": ["turbo.json"], "category": "build_tools"},
    
    # Package managers
    "npm": {"files": ["package-lock.json"], "category": "package_managers"},
    "yarn": {"files": ["yarn.lock"], "category": "package_managers"},
    "pnpm": {"files": ["pnpm-lock.yaml"], "category": "package_managers"},
    "poetry": {"files": ["poetry.lock"], "category": "package_managers"},
    
    # CI/CD
    "github_actions": {"files": [".github/workflows/*.yml"], "category": "ci_cd"},
    "azure_pipelines": {"files": ["azure-pipelines.yml"], "category": "ci_cd"},
    "gitlab_ci": {"files": [".gitlab-ci.yml"], "category": "ci_cd"},
}


class TechStackDetector:
    """
    Detector for repository technology stacks.
    
    Analyzes file patterns and package manifests to identify technologies.
    """
    
    def __init__(self):
        """Initialize the tech stack detector."""
        self.patterns = DETECTION_PATTERNS
    
    def detect(self, repo_path: str) -> TechStack:
        """
        Detect the technology stack of a repository.
        
        Args:
            repo_path: Path to the repository root
            
        Returns:
            TechStack with detected technologies.
        """
        raise NotImplementedError("TechStackDetector.detect() not yet implemented")
    
    def detect_from_files(self, file_list: List[str]) -> TechStack:
        """
        Detect technology stack from a list of file paths.
        
        Args:
            file_list: List of file paths in the repository
            
        Returns:
            TechStack with detected technologies.
        """
        raise NotImplementedError("TechStackDetector.detect_from_files() not yet implemented")
    
    def get_review_context(self, stack: TechStack) -> Dict[str, Any]:
        """
        Get code review context based on detected stack.
        
        Args:
            stack: Detected technology stack
            
        Returns:
            Dictionary with review guidelines and focus areas.
        """
        raise NotImplementedError("TechStackDetector.get_review_context() not yet implemented")


__all__ = ["TechStackDetector", "TechStack", "DETECTION_PATTERNS"]
