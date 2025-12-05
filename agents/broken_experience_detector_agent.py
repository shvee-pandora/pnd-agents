"""
Broken Experience Detector Agent (BX Agent)

An agent that autonomously scans any given URL and detects issues in
performance, UI, UX, accessibility, SEO, code quality signals, broken links,
missing images, and JS errors. Outputs a structured JSON report and a
human-readable markdown summary.
"""

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin
from enum import Enum


class IssueSeverity(Enum):
    """Severity levels for detected issues."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(Enum):
    """Categories of detected issues."""
    NETWORK = "network"
    PERFORMANCE = "performance"
    SEO = "seo"
    ACCESSIBILITY = "accessibility"
    UX = "ux"
    SECURITY = "security"


@dataclass
class Issue:
    """Represents a detected issue."""
    category: str
    severity: str
    message: str
    element: Optional[str] = None
    selector: Optional[str] = None
    recommendation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "element": self.element,
            "selector": self.selector,
            "recommendation": self.recommendation,
        }


@dataclass
class BrokenResource:
    """Represents a broken resource (image or link)."""
    url: str
    status_code: Optional[int] = None
    error: Optional[str] = None
    source_element: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "statusCode": self.status_code,
            "error": self.error,
            "sourceElement": self.source_element,
        }


@dataclass
class ConsoleError:
    """Represents a console error."""
    type: str
    message: str
    url: Optional[str] = None
    line: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "message": self.message,
            "url": self.url,
            "line": self.line,
        }


@dataclass
class PerformanceFinding:
    """Represents a performance-related finding."""
    metric: str
    value: Any
    threshold: Optional[Any] = None
    status: str = "info"
    recommendation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "status": self.status,
            "recommendation": self.recommendation,
        }


@dataclass
class ScanReport:
    """Complete scan report."""
    url: str
    score: int = 100
    scan_duration_ms: int = 0
    timestamp: str = ""
    errors: List[Issue] = field(default_factory=list)
    warnings: List[Issue] = field(default_factory=list)
    broken_images: List[BrokenResource] = field(default_factory=list)
    broken_links: List[BrokenResource] = field(default_factory=list)
    console_errors: List[ConsoleError] = field(default_factory=list)
    seo_issues: List[Issue] = field(default_factory=list)
    accessibility_issues: List[Issue] = field(default_factory=list)
    performance_findings: List[PerformanceFinding] = field(default_factory=list)
    ux_issues: List[Issue] = field(default_factory=list)
    recommended_fixes: List[str] = field(default_factory=list)
    failed_requests: List[BrokenResource] = field(default_factory=list)
    slow_resources: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "score": self.score,
            "scanDurationMs": self.scan_duration_ms,
            "timestamp": self.timestamp,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "broken_images": [b.to_dict() for b in self.broken_images],
            "broken_links": [b.to_dict() for b in self.broken_links],
            "console_errors": [c.to_dict() for c in self.console_errors],
            "seo_issues": [s.to_dict() for s in self.seo_issues],
            "accessibility_issues": [a.to_dict() for a in self.accessibility_issues],
            "performance_findings": [p.to_dict() for p in self.performance_findings],
            "ux_issues": [u.to_dict() for u in self.ux_issues],
            "recommended_fixes": self.recommended_fixes,
            "failed_requests": [f.to_dict() for f in self.failed_requests],
            "slow_resources": self.slow_resources,
        }
    
    def to_markdown(self) -> str:
        """Generate a human-readable markdown report."""
        lines = []
        
        # Header
        lines.append("# Broken Experience Scan Report")
        lines.append("")
        lines.append(f"**URL:** {self.url}")
        lines.append(f"**Scan Date:** {self.timestamp}")
        lines.append(f"**Duration:** {self.scan_duration_ms}ms")
        lines.append("")
        
        # Score meter
        lines.append(f"## Overall Score: {self.score}/100")
        lines.append("")
        score_bar = self._generate_score_bar(self.score)
        lines.append(f"{score_bar}")
        lines.append("")
        
        # Risk level
        risk_level = self._get_risk_level(self.score)
        lines.append(f"**Risk Level:** {risk_level}")
        lines.append("")
        
        # Summary counts
        lines.append("## Summary")
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|----------|-------|")
        lines.append(f"| Critical Errors | {len([e for e in self.errors if e.severity == 'critical'])} |")
        lines.append(f"| Errors | {len(self.errors)} |")
        lines.append(f"| Warnings | {len(self.warnings)} |")
        lines.append(f"| Broken Images | {len(self.broken_images)} |")
        lines.append(f"| Broken Links | {len(self.broken_links)} |")
        lines.append(f"| Console Errors | {len(self.console_errors)} |")
        lines.append(f"| SEO Issues | {len(self.seo_issues)} |")
        lines.append(f"| Accessibility Issues | {len(self.accessibility_issues)} |")
        lines.append(f"| UX Issues | {len(self.ux_issues)} |")
        lines.append(f"| Performance Findings | {len(self.performance_findings)} |")
        lines.append("")
        
        # Top 5 issues
        lines.append("## Top Issues")
        lines.append("")
        top_issues = self._get_top_issues(5)
        for i, issue in enumerate(top_issues, 1):
            severity_emoji = {"critical": "🔴", "error": "🟠", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
            lines.append(f"{i}. {severity_emoji} **[{issue.category.upper()}]** {issue.message}")
            if issue.recommendation:
                lines.append(f"   - *Fix:* {issue.recommendation}")
        lines.append("")
        
        # Broken Images
        if self.broken_images:
            lines.append(f"## Broken Images ({len(self.broken_images)})")
            lines.append("")
            lines.append("| URL | Status | Source |")
            lines.append("|-----|--------|--------|")
            for img in self.broken_images[:10]:
                url_short = img.url[:50] + "..." if len(img.url) > 50 else img.url
                lines.append(f"| {url_short} | {img.status_code or img.error} | {img.source_element or 'N/A'} |")
            if len(self.broken_images) > 10:
                lines.append(f"| ... and {len(self.broken_images) - 10} more | | |")
            lines.append("")
        
        # Broken Links
        if self.broken_links:
            lines.append(f"## Broken Links ({len(self.broken_links)})")
            lines.append("")
            lines.append("| URL | Status |")
            lines.append("|-----|--------|")
            for link in self.broken_links[:10]:
                url_short = link.url[:60] + "..." if len(link.url) > 60 else link.url
                lines.append(f"| {url_short} | {link.status_code or link.error} |")
            if len(self.broken_links) > 10:
                lines.append(f"| ... and {len(self.broken_links) - 10} more | |")
            lines.append("")
        
        # Console Errors
        if self.console_errors:
            lines.append(f"## Console Errors ({len(self.console_errors)})")
            lines.append("")
            for err in self.console_errors[:5]:
                lines.append(f"- **{err.type}:** {err.message[:100]}{'...' if len(err.message) > 100 else ''}")
            if len(self.console_errors) > 5:
                lines.append(f"- ... and {len(self.console_errors) - 5} more")
            lines.append("")
        
        # SEO Checklist
        lines.append("## SEO Checklist")
        lines.append("")
        seo_checks = {
            "title": "Page has <title> tag",
            "meta_description": "Page has meta description",
            "h1": "Page has single H1",
            "canonical": "Page has valid canonical URL",
        }
        seo_issues_set = {issue.message.lower() for issue in self.seo_issues}
        for check_id, check_name in seo_checks.items():
            has_issue = any(check_id.replace("_", " ") in msg or check_id in msg for msg in seo_issues_set)
            status = "❌" if has_issue else "✅"
            lines.append(f"- {status} {check_name}")
        lines.append("")
        
        # Accessibility Summary
        if self.accessibility_issues:
            lines.append(f"## Accessibility Issues ({len(self.accessibility_issues)})")
            lines.append("")
            for issue in self.accessibility_issues[:10]:
                lines.append(f"- **{issue.message}**")
                if issue.selector:
                    lines.append(f"  - Selector: `{issue.selector}`")
                if issue.recommendation:
                    lines.append(f"  - Fix: {issue.recommendation}")
            if len(self.accessibility_issues) > 10:
                lines.append(f"- ... and {len(self.accessibility_issues) - 10} more")
            lines.append("")
        
        # Performance Insights
        if self.performance_findings:
            lines.append("## Performance Insights")
            lines.append("")
            lines.append("| Metric | Value | Status |")
            lines.append("|--------|-------|--------|")
            for finding in self.performance_findings:
                status_emoji = {"good": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}.get(finding.status, "ℹ️")
                lines.append(f"| {finding.metric} | {finding.value} | {status_emoji} |")
            lines.append("")
        
        # UX Issues
        if self.ux_issues:
            lines.append(f"## UX Issues ({len(self.ux_issues)})")
            lines.append("")
            for issue in self.ux_issues[:10]:
                lines.append(f"- {issue.message}")
                if issue.recommendation:
                    lines.append(f"  - *Fix:* {issue.recommendation}")
            if len(self.ux_issues) > 10:
                lines.append(f"- ... and {len(self.ux_issues) - 10} more")
            lines.append("")
        
        # Recommended Fixes
        if self.recommended_fixes:
            lines.append("## Recommended Fixes")
            lines.append("")
            for i, fix in enumerate(self.recommended_fixes[:10], 1):
                lines.append(f"{i}. {fix}")
            lines.append("")
        
        # Estimated Impact
        lines.append("## Estimated Impact")
        lines.append("")
        impact = self._estimate_impact()
        lines.append(f"**User Experience:** {impact['ux']}")
        lines.append(f"**SEO Ranking:** {impact['seo']}")
        lines.append(f"**Conversion Rate:** {impact['conversion']}")
        lines.append(f"**Page Load Time:** {impact['performance']}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_score_bar(self, score: int) -> str:
        """Generate a visual score bar."""
        filled = int(score / 10)
        empty = 10 - filled
        if score >= 80:
            color = "🟢"
        elif score >= 60:
            color = "🟡"
        elif score >= 40:
            color = "🟠"
        else:
            color = "🔴"
        return f"[{'█' * filled}{'░' * empty}] {color}"
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level based on score."""
        if score >= 90:
            return "🟢 Low Risk"
        elif score >= 70:
            return "🟡 Medium Risk"
        elif score >= 50:
            return "🟠 High Risk"
        else:
            return "🔴 Critical Risk"
    
    def _get_top_issues(self, count: int) -> List[Issue]:
        """Get top issues sorted by severity."""
        all_issues = (
            self.errors + 
            self.warnings + 
            self.seo_issues + 
            self.accessibility_issues + 
            self.ux_issues
        )
        severity_order = {"critical": 0, "error": 1, "warning": 2, "info": 3}
        sorted_issues = sorted(all_issues, key=lambda x: severity_order.get(x.severity, 4))
        return sorted_issues[:count]
    
    def _estimate_impact(self) -> Dict[str, str]:
        """Estimate impact of issues on various metrics."""
        ux_impact = "Low"
        seo_impact = "Low"
        conversion_impact = "Low"
        performance_impact = "Low"
        
        # UX impact
        if len(self.broken_images) > 5 or len(self.ux_issues) > 10:
            ux_impact = "High"
        elif len(self.broken_images) > 0 or len(self.ux_issues) > 3:
            ux_impact = "Medium"
        
        # SEO impact
        critical_seo = len([i for i in self.seo_issues if i.severity in ["critical", "error"]])
        if critical_seo > 3:
            seo_impact = "High"
        elif critical_seo > 0:
            seo_impact = "Medium"
        
        # Conversion impact
        if len(self.broken_links) > 5 or len(self.console_errors) > 10:
            conversion_impact = "High"
        elif len(self.broken_links) > 0 or len(self.console_errors) > 3:
            conversion_impact = "Medium"
        
        # Performance impact
        perf_issues = len([p for p in self.performance_findings if p.status in ["warning", "error"]])
        if perf_issues > 5:
            performance_impact = "High"
        elif perf_issues > 2:
            performance_impact = "Medium"
        
        return {
            "ux": ux_impact,
            "seo": seo_impact,
            "conversion": conversion_impact,
            "performance": performance_impact,
        }


class BrokenExperienceDetectorAgent:
    """
    Agent for detecting broken experiences on web pages.
    
    Scans URLs for performance issues, UI/UX problems, accessibility violations,
    SEO issues, broken links, missing images, and JavaScript errors.
    """
    
    # Thresholds for performance metrics
    SLOW_RESOURCE_THRESHOLD_MS = 1000  # Resources taking > 1s are slow
    LARGE_RESOURCE_THRESHOLD_KB = 500  # Resources > 500KB are large
    MIN_CLICK_TARGET_SIZE = 44  # Minimum touch target size in pixels
    
    # CDN patterns to check for
    CDN_PATTERNS = [
        r"cdn\.",
        r"cloudfront\.net",
        r"cloudflare",
        r"akamai",
        r"fastly",
        r"imgix",
        r"cloudinary",
        r"amplience\.net",
    ]
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize the Broken Experience Detector Agent.
        
        Args:
            headless: Run browser in headless mode (default: True)
            timeout: Page load timeout in milliseconds (default: 30000)
        """
        self.headless = headless
        self.timeout = timeout
        self._browser = None
        self._context = None
        self._page = None
        
        # Collected data during scan
        self._network_requests: List[Dict[str, Any]] = []
        self._console_messages: List[Dict[str, Any]] = []
        self._failed_requests: List[Dict[str, Any]] = []
    
    async def _init_browser(self):
        """Initialize the Playwright browser."""
        from playwright.async_api import async_playwright
        
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self._page = await self._context.new_page()
        
        # Set up network request monitoring
        self._page.on("request", self._on_request)
        self._page.on("response", self._on_response)
        self._page.on("requestfailed", self._on_request_failed)
        
        # Set up console message monitoring
        self._page.on("console", self._on_console)
    
    def _on_request(self, request):
        """Handle network request events."""
        self._network_requests.append({
            "url": request.url,
            "method": request.method,
            "resource_type": request.resource_type,
            "start_time": time.time() * 1000,
        })
    
    def _on_response(self, response):
        """Handle network response events."""
        for req in self._network_requests:
            if req["url"] == response.url and "status" not in req:
                req["status"] = response.status
                req["end_time"] = time.time() * 1000
                req["duration"] = req["end_time"] - req["start_time"]
                try:
                    headers = response.headers
                    content_length = headers.get("content-length")
                    if content_length:
                        req["size"] = int(content_length)
                except Exception:
                    pass
                break
    
    def _on_request_failed(self, request):
        """Handle failed network requests."""
        self._failed_requests.append({
            "url": request.url,
            "method": request.method,
            "resource_type": request.resource_type,
            "failure": request.failure,
        })
    
    def _on_console(self, message):
        """Handle console messages."""
        self._console_messages.append({
            "type": message.type,
            "text": message.text,
            "location": message.location,
        })
    
    async def _close_browser(self):
        """Close the browser and clean up."""
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if hasattr(self, '_playwright'):
            await self._playwright.stop()
    
    async def scan_site(self, url: str) -> ScanReport:
        """
        Scan a website and generate a comprehensive report.
        
        Args:
            url: The URL to scan
            
        Returns:
            ScanReport with all detected issues
        """
        from datetime import datetime
        
        start_time = time.time()
        report = ScanReport(
            url=url,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        # Reset collected data
        self._network_requests = []
        self._console_messages = []
        self._failed_requests = []
        
        try:
            await self._init_browser()
            
            # Navigate to the page
            try:
                await self._page.goto(url, wait_until="networkidle", timeout=self.timeout)
            except Exception as e:
                report.errors.append(Issue(
                    category=IssueCategory.NETWORK.value,
                    severity=IssueSeverity.CRITICAL.value,
                    message=f"Failed to load page: {str(e)}",
                    recommendation="Check if the URL is correct and the server is responding"
                ))
                return report
            
            # Wait a bit for any lazy-loaded content
            await asyncio.sleep(2)
            
            # Run all checks
            await self._check_console_errors(report)
            await self._check_network_issues(report)
            await self._check_broken_images(report)
            await self._check_broken_links(report)
            await self._check_seo_issues(report)
            await self._check_accessibility_issues(report)
            await self._check_performance_issues(report)
            await self._check_ux_issues(report)
            
            # Calculate score
            report.score = self._calculate_score(report)
            
            # Generate recommended fixes
            report.recommended_fixes = self._generate_recommendations(report)
            
        finally:
            await self._close_browser()
        
        report.scan_duration_ms = int((time.time() - start_time) * 1000)
        return report
    
    async def _check_console_errors(self, report: ScanReport):
        """Check for JavaScript console errors."""
        for msg in self._console_messages:
            if msg["type"] in ["error", "warning"]:
                report.console_errors.append(ConsoleError(
                    type=msg["type"],
                    message=msg["text"],
                    url=msg.get("location", {}).get("url"),
                    line=msg.get("location", {}).get("lineNumber"),
                ))
                
                if msg["type"] == "error":
                    report.errors.append(Issue(
                        category=IssueCategory.NETWORK.value,
                        severity=IssueSeverity.ERROR.value,
                        message=f"JavaScript error: {msg['text'][:100]}",
                        recommendation="Fix the JavaScript error to ensure proper functionality"
                    ))
    
    async def _check_network_issues(self, report: ScanReport):
        """Check for network-related issues."""
        # Check failed requests
        for req in self._failed_requests:
            report.failed_requests.append(BrokenResource(
                url=req["url"],
                error=req.get("failure", "Unknown error"),
            ))
            
            report.errors.append(Issue(
                category=IssueCategory.NETWORK.value,
                severity=IssueSeverity.ERROR.value,
                message=f"Failed request: {req['url'][:50]}",
                recommendation="Check if the resource exists and is accessible"
            ))
        
        # Check for 4xx and 5xx responses
        for req in self._network_requests:
            status = req.get("status", 0)
            if status >= 400:
                report.failed_requests.append(BrokenResource(
                    url=req["url"],
                    status_code=status,
                ))
                
                severity = IssueSeverity.CRITICAL.value if status >= 500 else IssueSeverity.ERROR.value
                report.errors.append(Issue(
                    category=IssueCategory.NETWORK.value,
                    severity=severity,
                    message=f"HTTP {status} error: {req['url'][:50]}",
                    recommendation="Fix the broken resource or remove the reference"
                ))
        
        # Check for slow resources
        for req in self._network_requests:
            duration = req.get("duration", 0)
            if duration > self.SLOW_RESOURCE_THRESHOLD_MS:
                report.slow_resources.append({
                    "url": req["url"],
                    "duration_ms": int(duration),
                    "type": req.get("resource_type", "unknown"),
                })
                
                report.warnings.append(Issue(
                    category=IssueCategory.PERFORMANCE.value,
                    severity=IssueSeverity.WARNING.value,
                    message=f"Slow resource ({int(duration)}ms): {req['url'][:50]}",
                    recommendation="Optimize or cache this resource"
                ))
    
    async def _check_broken_images(self, report: ScanReport):
        """Check for broken images."""
        images = await self._page.query_selector_all("img")
        
        for img in images:
            try:
                src = await img.get_attribute("src")
                if not src:
                    report.broken_images.append(BrokenResource(
                        url="",
                        error="Missing src attribute",
                        source_element=await img.get_attribute("outerHTML")[:100] if await img.get_attribute("outerHTML") else None,
                    ))
                    continue
                
                # Check if image loaded successfully
                natural_width = await img.evaluate("el => el.naturalWidth")
                if natural_width == 0:
                    # Check if it's in our failed requests
                    full_url = urljoin(report.url, src)
                    status = None
                    for req in self._network_requests:
                        if req["url"] == full_url or req["url"] == src:
                            status = req.get("status")
                            break
                    
                    report.broken_images.append(BrokenResource(
                        url=src,
                        status_code=status,
                        error="Image failed to load" if not status else None,
                    ))
            except Exception:
                pass
    
    async def _check_broken_links(self, report: ScanReport):
        """Check for broken links (based on network requests)."""
        links = await self._page.query_selector_all("a[href]")
        checked_urls = set()
        
        for link in links:
            try:
                href = await link.get_attribute("href")
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue
                
                full_url = urljoin(report.url, href)
                if full_url in checked_urls:
                    continue
                checked_urls.add(full_url)
                
                # Check if this URL had a failed request
                for req in self._failed_requests:
                    if req["url"] == full_url:
                        report.broken_links.append(BrokenResource(
                            url=full_url,
                            error=req.get("failure", "Request failed"),
                        ))
                        break
                
                # Check for 4xx/5xx status
                for req in self._network_requests:
                    if req["url"] == full_url and req.get("status", 0) >= 400:
                        report.broken_links.append(BrokenResource(
                            url=full_url,
                            status_code=req["status"],
                        ))
                        break
            except Exception:
                pass
    
    async def _check_seo_issues(self, report: ScanReport):
        """Check for SEO-related issues."""
        # Check title
        title = await self._page.title()
        if not title:
            report.seo_issues.append(Issue(
                category=IssueCategory.SEO.value,
                severity=IssueSeverity.CRITICAL.value,
                message="Missing page title",
                recommendation="Add a descriptive <title> tag to the page"
            ))
        elif len(title) < 10:
            report.seo_issues.append(Issue(
                category=IssueCategory.SEO.value,
                severity=IssueSeverity.WARNING.value,
                message=f"Page title is too short ({len(title)} characters)",
                recommendation="Use a title between 50-60 characters"
            ))
        elif len(title) > 60:
            report.seo_issues.append(Issue(
                category=IssueCategory.SEO.value,
                severity=IssueSeverity.WARNING.value,
                message=f"Page title is too long ({len(title)} characters)",
                recommendation="Keep title under 60 characters"
            ))
        
        # Check meta description
        meta_desc = await self._page.query_selector('meta[name="description"]')
        if not meta_desc:
            report.seo_issues.append(Issue(
                category=IssueCategory.SEO.value,
                severity=IssueSeverity.ERROR.value,
                message="Missing meta description",
                recommendation="Add a meta description tag with 150-160 characters"
            ))
        else:
            content = await meta_desc.get_attribute("content")
            if not content:
                report.seo_issues.append(Issue(
                    category=IssueCategory.SEO.value,
                    severity=IssueSeverity.ERROR.value,
                    message="Empty meta description",
                    recommendation="Add content to the meta description"
                ))
            elif len(content) < 50:
                report.seo_issues.append(Issue(
                    category=IssueCategory.SEO.value,
                    severity=IssueSeverity.WARNING.value,
                    message=f"Meta description is too short ({len(content)} characters)",
                    recommendation="Use a description between 150-160 characters"
                ))
        
        # Check H1 tags
        h1_tags = await self._page.query_selector_all("h1")
        h1_count = len(h1_tags)
        if h1_count == 0:
            report.seo_issues.append(Issue(
                category=IssueCategory.SEO.value,
                severity=IssueSeverity.ERROR.value,
                message="Missing H1 tag",
                recommendation="Add a single H1 tag to the page"
            ))
        elif h1_count > 1:
            report.seo_issues.append(Issue(
                category=IssueCategory.SEO.value,
                severity=IssueSeverity.WARNING.value,
                message=f"Multiple H1 tags found ({h1_count})",
                recommendation="Use only one H1 tag per page"
            ))
        
        # Check canonical URL
        canonical = await self._page.query_selector('link[rel="canonical"]')
        if not canonical:
            report.seo_issues.append(Issue(
                category=IssueCategory.SEO.value,
                severity=IssueSeverity.WARNING.value,
                message="Missing canonical URL",
                recommendation="Add a canonical link tag to prevent duplicate content issues"
            ))
        else:
            href = await canonical.get_attribute("href")
            if not href:
                report.seo_issues.append(Issue(
                    category=IssueCategory.SEO.value,
                    severity=IssueSeverity.ERROR.value,
                    message="Canonical URL is empty",
                    recommendation="Set a valid href for the canonical link"
                ))
    
    async def _check_accessibility_issues(self, report: ScanReport):
        """Check for accessibility issues."""
        # Check images without alt text
        images = await self._page.query_selector_all("img")
        for img in images:
            try:
                alt = await img.get_attribute("alt")
                src = await img.get_attribute("src") or "unknown"
                if alt is None:
                    report.accessibility_issues.append(Issue(
                        category=IssueCategory.ACCESSIBILITY.value,
                        severity=IssueSeverity.ERROR.value,
                        message="Image missing alt attribute",
                        selector=f'img[src="{src[:50]}"]',
                        recommendation="Add descriptive alt text to the image"
                    ))
            except Exception:
                pass
        
        # Check buttons without accessible names
        buttons = await self._page.query_selector_all("button")
        for button in buttons:
            try:
                text = await button.inner_text()
                aria_label = await button.get_attribute("aria-label")
                aria_labelledby = await button.get_attribute("aria-labelledby")
                title = await button.get_attribute("title")
                
                if not text.strip() and not aria_label and not aria_labelledby and not title:
                    report.accessibility_issues.append(Issue(
                        category=IssueCategory.ACCESSIBILITY.value,
                        severity=IssueSeverity.ERROR.value,
                        message="Button without accessible name",
                        recommendation="Add text content, aria-label, or title to the button"
                    ))
            except Exception:
                pass
        
        # Check for missing aria-labels on interactive elements
        interactive_elements = await self._page.query_selector_all(
            'input:not([type="hidden"]), select, textarea'
        )
        for elem in interactive_elements:
            try:
                elem_id = await elem.get_attribute("id")
                aria_label = await elem.get_attribute("aria-label")
                aria_labelledby = await elem.get_attribute("aria-labelledby")
                
                # Check if there's an associated label
                has_label = False
                if elem_id:
                    label = await self._page.query_selector(f'label[for="{elem_id}"]')
                    has_label = label is not None
                
                if not has_label and not aria_label and not aria_labelledby:
                    elem_type = await elem.get_attribute("type") or "input"
                    report.accessibility_issues.append(Issue(
                        category=IssueCategory.ACCESSIBILITY.value,
                        severity=IssueSeverity.WARNING.value,
                        message=f"Form {elem_type} without label or aria-label",
                        recommendation="Add a label element or aria-label attribute"
                    ))
            except Exception:
                pass
        
        # Check for empty links
        links = await self._page.query_selector_all("a")
        for link in links:
            try:
                text = await link.inner_text()
                aria_label = await link.get_attribute("aria-label")
                title = await link.get_attribute("title")
                
                # Check for image inside link
                img = await link.query_selector("img")
                img_alt = None
                if img:
                    img_alt = await img.get_attribute("alt")
                
                if not text.strip() and not aria_label and not title and not img_alt:
                    href = await link.get_attribute("href") or ""
                    if href and not href.startswith("#"):
                        report.accessibility_issues.append(Issue(
                            category=IssueCategory.ACCESSIBILITY.value,
                            severity=IssueSeverity.ERROR.value,
                            message="Link without accessible name",
                            recommendation="Add text content, aria-label, or title to the link"
                        ))
            except Exception:
                pass
    
    async def _check_performance_issues(self, report: ScanReport):
        """Check for performance-related issues."""
        # Check images without dimensions
        images = await self._page.query_selector_all("img")
        images_without_dimensions = 0
        non_lazy_images = 0
        non_cdn_images = 0
        
        for img in images:
            try:
                width = await img.get_attribute("width")
                height = await img.get_attribute("height")
                style = await img.get_attribute("style") or ""
                
                # Check for dimensions in style
                has_style_dimensions = "width" in style and "height" in style
                
                if not width and not height and not has_style_dimensions:
                    images_without_dimensions += 1
                
                # Check for lazy loading
                loading = await img.get_attribute("loading")
                if loading != "lazy":
                    non_lazy_images += 1
                
                # Check for CDN usage
                src = await img.get_attribute("src") or ""
                if src and not any(re.search(pattern, src, re.I) for pattern in self.CDN_PATTERNS):
                    if src.startswith("http"):
                        non_cdn_images += 1
            except Exception:
                pass
        
        if images_without_dimensions > 0:
            report.performance_findings.append(PerformanceFinding(
                metric="Images without dimensions",
                value=images_without_dimensions,
                status="warning" if images_without_dimensions > 3 else "info",
                recommendation="Add width and height attributes to prevent layout shifts"
            ))
        
        if non_lazy_images > 5:
            report.performance_findings.append(PerformanceFinding(
                metric="Non-lazy images",
                value=non_lazy_images,
                status="warning",
                recommendation="Add loading='lazy' to images below the fold"
            ))
        
        if non_cdn_images > 0:
            report.performance_findings.append(PerformanceFinding(
                metric="Images not served from CDN",
                value=non_cdn_images,
                status="info",
                recommendation="Consider serving images from a CDN for better performance"
            ))
        
        # Check for render-blocking scripts
        scripts = await self._page.query_selector_all("script[src]")
        blocking_scripts = 0
        for script in scripts:
            try:
                is_async = await script.get_attribute("async")
                is_defer = await script.get_attribute("defer")
                script_type = await script.get_attribute("type")
                
                if not is_async and not is_defer and script_type != "module":
                    blocking_scripts += 1
            except Exception:
                pass
        
        if blocking_scripts > 0:
            report.performance_findings.append(PerformanceFinding(
                metric="Render-blocking scripts",
                value=blocking_scripts,
                status="warning" if blocking_scripts > 2 else "info",
                recommendation="Add async or defer attributes to non-critical scripts"
            ))
        
        # Calculate total page size
        total_size = sum(req.get("size", 0) for req in self._network_requests)
        total_size_kb = total_size / 1024
        report.performance_findings.append(PerformanceFinding(
            metric="Total page size",
            value=f"{total_size_kb:.1f} KB",
            threshold="< 3000 KB",
            status="error" if total_size_kb > 5000 else "warning" if total_size_kb > 3000 else "good"
        ))
        
        # Count total requests
        total_requests = len(self._network_requests)
        report.performance_findings.append(PerformanceFinding(
            metric="Total requests",
            value=total_requests,
            threshold="< 100",
            status="warning" if total_requests > 100 else "good"
        ))
        
        # Estimate LCP (rough)
        lcp_estimate = max(
            (req.get("duration", 0) for req in self._network_requests 
             if req.get("resource_type") in ["image", "document"]),
            default=0
        )
        report.performance_findings.append(PerformanceFinding(
            metric="Estimated LCP",
            value=f"{int(lcp_estimate)}ms",
            threshold="< 2500ms",
            status="error" if lcp_estimate > 4000 else "warning" if lcp_estimate > 2500 else "good"
        ))
    
    async def _check_ux_issues(self, report: ScanReport):
        """Check for UX-related issues."""
        # Check for small click targets
        clickable_elements = await self._page.query_selector_all(
            "button, a, input[type='button'], input[type='submit'], [role='button']"
        )
        
        small_targets = 0
        for elem in clickable_elements:
            try:
                box = await elem.bounding_box()
                if box:
                    if box["width"] < self.MIN_CLICK_TARGET_SIZE or box["height"] < self.MIN_CLICK_TARGET_SIZE:
                        small_targets += 1
            except Exception:
                pass
        
        if small_targets > 0:
            report.ux_issues.append(Issue(
                category=IssueCategory.UX.value,
                severity=IssueSeverity.WARNING.value,
                message=f"{small_targets} click targets smaller than {self.MIN_CLICK_TARGET_SIZE}px",
                recommendation=f"Increase touch target size to at least {self.MIN_CLICK_TARGET_SIZE}x{self.MIN_CLICK_TARGET_SIZE}px"
            ))
        
        # Check for buttons without visible labels
        buttons = await self._page.query_selector_all("button")
        unlabeled_buttons = 0
        for button in buttons:
            try:
                text = await button.inner_text()
                if not text.strip():
                    # Check if it has an icon or image
                    has_icon = await button.query_selector("svg, img, i, span[class*='icon']")
                    if has_icon:
                        aria_label = await button.get_attribute("aria-label")
                        title = await button.get_attribute("title")
                        if not aria_label and not title:
                            unlabeled_buttons += 1
            except Exception:
                pass
        
        if unlabeled_buttons > 0:
            report.ux_issues.append(Issue(
                category=IssueCategory.UX.value,
                severity=IssueSeverity.WARNING.value,
                message=f"{unlabeled_buttons} icon buttons without visible labels",
                recommendation="Add aria-label or visible text to icon buttons"
            ))
        
        # Check for potential contrast issues (simplified check)
        # This is a basic check - for full contrast checking, use a dedicated tool
        try:
            low_contrast_elements = await self._page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('p, span, a, button, h1, h2, h3, h4, h5, h6');
                    let lowContrast = 0;
                    
                    for (const el of elements) {
                        const style = window.getComputedStyle(el);
                        const color = style.color;
                        const bgColor = style.backgroundColor;
                        
                        // Very basic check for light gray text
                        if (color && color.includes('rgb')) {
                            const match = color.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                            if (match) {
                                const [_, r, g, b] = match.map(Number);
                                // Check if text is very light gray
                                if (r > 180 && g > 180 && b > 180) {
                                    lowContrast++;
                                }
                            }
                        }
                    }
                    return lowContrast;
                }
            """)
            
            if low_contrast_elements > 5:
                report.ux_issues.append(Issue(
                    category=IssueCategory.UX.value,
                    severity=IssueSeverity.WARNING.value,
                    message=f"Potential low contrast text detected ({low_contrast_elements} elements)",
                    recommendation="Ensure text has sufficient contrast ratio (4.5:1 for normal text)"
                ))
        except Exception:
            pass
    
    def _calculate_score(self, report: ScanReport) -> int:
        """Calculate overall score based on issues found."""
        score = 100
        
        # Deduct points for errors
        score -= len(report.errors) * 5
        score -= len([e for e in report.errors if e.severity == "critical"]) * 10
        
        # Deduct points for warnings
        score -= len(report.warnings) * 2
        
        # Deduct points for broken resources
        score -= len(report.broken_images) * 3
        score -= len(report.broken_links) * 3
        
        # Deduct points for console errors
        score -= len(report.console_errors) * 2
        
        # Deduct points for SEO issues
        score -= len([i for i in report.seo_issues if i.severity == "critical"]) * 8
        score -= len([i for i in report.seo_issues if i.severity == "error"]) * 5
        score -= len([i for i in report.seo_issues if i.severity == "warning"]) * 2
        
        # Deduct points for accessibility issues
        score -= len([i for i in report.accessibility_issues if i.severity == "error"]) * 4
        score -= len([i for i in report.accessibility_issues if i.severity == "warning"]) * 2
        
        # Deduct points for UX issues
        score -= len(report.ux_issues) * 2
        
        # Deduct points for performance issues
        for finding in report.performance_findings:
            if finding.status == "error":
                score -= 5
            elif finding.status == "warning":
                score -= 2
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, report: ScanReport) -> List[str]:
        """Generate prioritized recommendations based on issues found."""
        recommendations = []
        
        # Critical issues first
        if any(e.severity == "critical" for e in report.errors):
            recommendations.append("Fix critical errors that may prevent page functionality")
        
        if report.broken_images:
            recommendations.append(f"Fix {len(report.broken_images)} broken images to improve user experience")
        
        if report.broken_links:
            recommendations.append(f"Fix {len(report.broken_links)} broken links to improve navigation")
        
        if report.console_errors:
            recommendations.append(f"Resolve {len(report.console_errors)} JavaScript errors")
        
        # SEO recommendations
        seo_critical = [i for i in report.seo_issues if i.severity in ["critical", "error"]]
        if seo_critical:
            recommendations.append("Address critical SEO issues (title, meta description, H1)")
        
        # Accessibility recommendations
        a11y_errors = [i for i in report.accessibility_issues if i.severity == "error"]
        if a11y_errors:
            recommendations.append(f"Fix {len(a11y_errors)} accessibility errors for WCAG compliance")
        
        # Performance recommendations
        perf_warnings = [p for p in report.performance_findings if p.status in ["warning", "error"]]
        if perf_warnings:
            recommendations.append("Optimize page performance (images, scripts, resources)")
        
        # UX recommendations
        if report.ux_issues:
            recommendations.append("Improve UX by fixing touch targets and button labels")
        
        return recommendations[:10]  # Return top 10 recommendations


def scan_site(url: str, headless: bool = True) -> Dict[str, Any]:
    """
    Convenience function to scan a site and return results.
    
    Args:
        url: The URL to scan
        headless: Run browser in headless mode (default: True)
        
    Returns:
        Dictionary with scan results
    """
    agent = BrokenExperienceDetectorAgent(headless=headless)
    report = asyncio.run(agent.scan_site(url))
    return {
        "json": report.to_dict(),
        "markdown": report.to_markdown(),
    }


async def async_scan_site(url: str, headless: bool = True) -> Dict[str, Any]:
    """
    Async convenience function to scan a site and return results.
    
    Args:
        url: The URL to scan
        headless: Run browser in headless mode (default: True)
        
    Returns:
        Dictionary with scan results
    """
    agent = BrokenExperienceDetectorAgent(headless=headless)
    report = await agent.scan_site(url)
    return {
        "json": report.to_dict(),
        "markdown": report.to_markdown(),
    }
