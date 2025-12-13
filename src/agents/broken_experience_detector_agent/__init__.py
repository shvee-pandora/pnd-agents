"""
Broken Experience Detector Agent Package

Exports the BrokenExperienceDetectorAgent class and helper functions.
"""

from .agent import (
    BrokenExperienceDetectorAgent,
    IssueSeverity,
    IssueCategory,
    Issue,
    BrokenResource,
    ConsoleError,
    PerformanceFinding,
    ScanReport,
    scan_site,
    async_scan_site,
)

__all__ = [
    "BrokenExperienceDetectorAgent",
    "IssueSeverity",
    "IssueCategory",
    "Issue",
    "BrokenResource",
    "ConsoleError",
    "PerformanceFinding",
    "ScanReport",
    "scan_site",
    "async_scan_site",
]
