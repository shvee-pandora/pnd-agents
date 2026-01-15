"""
Coverage Analyzer

Shared utilities for analyzing code coverage reports.
Used by unit_test_agent, sonar_validation_agent, and code_review agents.

Usage:
    from src.agents.core.analyzers.coverage_analyzer import CoverageAnalyzer
    
    analyzer = CoverageAnalyzer()
    report = analyzer.parse_lcov("coverage/lcov.info")
    summary = analyzer.get_summary(report)
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pnd_agents.core.analyzers.coverage")


@dataclass
class FileCoverage:
    """Coverage data for a single file."""
    path: str
    lines_found: int = 0
    lines_hit: int = 0
    branches_found: int = 0
    branches_hit: int = 0
    functions_found: int = 0
    functions_hit: int = 0
    uncovered_lines: List[int] = field(default_factory=list)
    
    @property
    def line_coverage(self) -> float:
        """Calculate line coverage percentage."""
        if self.lines_found == 0:
            return 100.0
        return (self.lines_hit / self.lines_found) * 100
    
    @property
    def branch_coverage(self) -> float:
        """Calculate branch coverage percentage."""
        if self.branches_found == 0:
            return 100.0
        return (self.branches_hit / self.branches_found) * 100


@dataclass
class CoverageReport:
    """Complete coverage report."""
    files: List[FileCoverage] = field(default_factory=list)
    total_lines_found: int = 0
    total_lines_hit: int = 0
    total_branches_found: int = 0
    total_branches_hit: int = 0
    
    @property
    def overall_line_coverage(self) -> float:
        """Calculate overall line coverage percentage."""
        if self.total_lines_found == 0:
            return 100.0
        return (self.total_lines_hit / self.total_lines_found) * 100
    
    @property
    def overall_branch_coverage(self) -> float:
        """Calculate overall branch coverage percentage."""
        if self.total_branches_found == 0:
            return 100.0
        return (self.total_branches_hit / self.total_branches_found) * 100


class CoverageAnalyzer:
    """
    Analyzer for code coverage reports.
    
    Supports multiple coverage formats: LCOV, Cobertura, Istanbul JSON.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the coverage analyzer.
        
        Args:
            base_path: Base path for resolving relative file paths
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    def parse_lcov(self, lcov_path: str) -> CoverageReport:
        """
        Parse an LCOV coverage report.
        
        Args:
            lcov_path: Path to lcov.info file
            
        Returns:
            CoverageReport with parsed data.
        """
        raise NotImplementedError("CoverageAnalyzer.parse_lcov() not yet implemented")
    
    def parse_cobertura(self, xml_path: str) -> CoverageReport:
        """
        Parse a Cobertura XML coverage report.
        
        Args:
            xml_path: Path to cobertura.xml file
            
        Returns:
            CoverageReport with parsed data.
        """
        raise NotImplementedError("CoverageAnalyzer.parse_cobertura() not yet implemented")
    
    def parse_istanbul_json(self, json_path: str) -> CoverageReport:
        """
        Parse an Istanbul JSON coverage report.
        
        Args:
            json_path: Path to coverage-final.json file
            
        Returns:
            CoverageReport with parsed data.
        """
        raise NotImplementedError("CoverageAnalyzer.parse_istanbul_json() not yet implemented")
    
    def get_uncovered_files(
        self,
        report: CoverageReport,
        threshold: float = 80.0
    ) -> List[FileCoverage]:
        """
        Get files below coverage threshold.
        
        Args:
            report: Coverage report to analyze
            threshold: Minimum coverage percentage
            
        Returns:
            List of FileCoverage objects below threshold.
        """
        return [f for f in report.files if f.line_coverage < threshold]
    
    def format_summary(self, report: CoverageReport) -> str:
        """
        Format a human-readable coverage summary.
        
        Args:
            report: Coverage report to summarize
            
        Returns:
            Formatted summary string.
        """
        return (
            f"Coverage Summary:\n"
            f"  Lines: {report.overall_line_coverage:.1f}% "
            f"({report.total_lines_hit}/{report.total_lines_found})\n"
            f"  Branches: {report.overall_branch_coverage:.1f}% "
            f"({report.total_branches_hit}/{report.total_branches_found})\n"
            f"  Files: {len(report.files)}"
        )


__all__ = ["CoverageAnalyzer", "CoverageReport", "FileCoverage"]
