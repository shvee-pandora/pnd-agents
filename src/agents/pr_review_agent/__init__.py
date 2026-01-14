"""
PR Review Agent

A reusable agent for reviewing Pull Requests from Azure DevOps.
Supports tech stack detection and role-aware review modes.
"""

from .agent import (
    PRReviewAgent,
    ReviewRole,
    TechStack,
    PRReviewResult,
    ReviewFinding,
    review_pr,
)

__all__ = [
    "PRReviewAgent",
    "ReviewRole",
    "TechStack",
    "PRReviewResult",
    "ReviewFinding",
    "review_pr",
]
