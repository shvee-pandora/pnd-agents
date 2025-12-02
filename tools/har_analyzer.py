"""
HAR Analyzer Tool

Provides HTTP Archive (HAR) file analysis capabilities for agents
including performance metrics extraction, slow request detection,
and optimization recommendations.
"""

import json
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ResourceType(Enum):
    """Types of web resources."""
    DOCUMENT = "document"
    SCRIPT = "script"
    STYLESHEET = "stylesheet"
    IMAGE = "image"
    FONT = "font"
    XHR = "xhr"
    FETCH = "fetch"
    WEBSOCKET = "websocket"
    MEDIA = "media"
    OTHER = "other"


class PerformanceStatus(Enum):
    """Performance status indicators."""
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@dataclass
class TimingBreakdown:
    """Detailed timing breakdown for a request."""
    blocked: float = 0  # Time spent in queue
    dns: float = 0  # DNS lookup time
    connect: float = 0  # TCP connection time
    ssl: float = 0  # SSL/TLS handshake time
    send: float = 0  # Time to send request
    wait: float = 0  # Time waiting for response (TTFB)
    receive: float = 0  # Time to download response
    
    @property
    def total(self) -> float:
        """Total time in milliseconds."""
        return (
            self.blocked + self.dns + self.connect +
            self.ssl + self.send + self.wait + self.receive
        )


@dataclass
class RequestEntry:
    """Represents a single HAR request entry."""
    url: str
    method: str
    status: int
    resource_type: ResourceType
    size: int  # Response size in bytes
    time: float  # Total time in ms
    timings: TimingBreakdown
    mime_type: str
    is_cached: bool = False
    is_compressed: bool = False
    compression_ratio: float = 0
    
    @property
    def is_slow(self) -> bool:
        """Check if request is considered slow (> 1s)."""
        return self.time > 1000
    
    @property
    def is_large(self) -> bool:
        """Check if resource is considered large (> 100KB)."""
        return self.size > 100000
    
    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(self.url).netloc


@dataclass
class ResourceMetrics:
    """Metrics for a resource type."""
    count: int = 0
    total_size: int = 0
    total_time: float = 0
    
    @property
    def avg_size(self) -> float:
        """Average size in bytes."""
        return self.total_size / self.count if self.count > 0 else 0
    
    @property
    def avg_time(self) -> float:
        """Average time in ms."""
        return self.total_time / self.count if self.count > 0 else 0


@dataclass
class PerformanceSummary:
    """Overall performance summary."""
    total_requests: int = 0
    total_size: int = 0
    total_time: float = 0
    dom_content_loaded: float = 0
    on_load: float = 0
    
    # Core Web Vitals targets
    TTFB_TARGET = 800  # ms
    LCP_TARGET = 2500  # ms
    REQUEST_TARGET = 50
    SIZE_TARGET = 2 * 1024 * 1024  # 2MB
    
    @property
    def ttfb_status(self) -> PerformanceStatus:
        """TTFB performance status."""
        # Approximate TTFB from first document request
        return PerformanceStatus.GOOD
    
    @property
    def size_status(self) -> PerformanceStatus:
        """Page size performance status."""
        if self.total_size <= self.SIZE_TARGET:
            return PerformanceStatus.GOOD
        elif self.total_size <= self.SIZE_TARGET * 1.5:
            return PerformanceStatus.NEEDS_IMPROVEMENT
        return PerformanceStatus.POOR
    
    @property
    def request_count_status(self) -> PerformanceStatus:
        """Request count performance status."""
        if self.total_requests <= self.REQUEST_TARGET:
            return PerformanceStatus.GOOD
        elif self.total_requests <= self.REQUEST_TARGET * 1.5:
            return PerformanceStatus.NEEDS_IMPROVEMENT
        return PerformanceStatus.POOR


@dataclass
class Recommendation:
    """Performance optimization recommendation."""
    title: str
    description: str
    impact: str  # high, medium, low
    effort: str  # low, medium, high
    category: str  # images, javascript, css, caching, network
    affected_urls: List[str] = field(default_factory=list)
    expected_savings: str = ""


@dataclass
class HARAnalysisReport:
    """Complete HAR analysis report."""
    url: str
    timestamp: str
    summary: PerformanceSummary
    by_type: Dict[ResourceType, ResourceMetrics]
    slow_requests: List[RequestEntry]
    large_resources: List[RequestEntry]
    third_party: Dict[str, ResourceMetrics]
    recommendations: List[Recommendation]


class HARAnalyzer:
    """
    HAR file analyzer for performance optimization.
    
    Parses HAR files to extract performance metrics, identify
    bottlenecks, and generate optimization recommendations.
    """
    
    # Thresholds
    SLOW_REQUEST_THRESHOLD = 1000  # ms
    LARGE_RESOURCE_THRESHOLD = 100000  # bytes (100KB)
    
    def __init__(self):
        """Initialize the HAR analyzer."""
        self.entries: List[RequestEntry] = []
        self.summary = PerformanceSummary()
        self.by_type: Dict[ResourceType, ResourceMetrics] = {}
    
    def parse_file(self, file_path: str) -> HARAnalysisReport:
        """
        Parse a HAR file and generate analysis report.
        
        Args:
            file_path: Path to the HAR file.
            
        Returns:
            HARAnalysisReport with complete analysis.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self.parse_data(data)
    
    def parse_data(self, data: Dict[str, Any]) -> HARAnalysisReport:
        """
        Parse HAR data and generate analysis report.
        
        Args:
            data: HAR JSON data.
            
        Returns:
            HARAnalysisReport with complete analysis.
        """
        self.entries = []
        self.summary = PerformanceSummary()
        self.by_type = {rt: ResourceMetrics() for rt in ResourceType}
        
        log = data.get('log', {})
        entries = log.get('entries', [])
        pages = log.get('pages', [])
        
        # Parse page timings
        if pages:
            page = pages[0]
            page_timings = page.get('pageTimings', {})
            self.summary.dom_content_loaded = page_timings.get('onContentLoad', 0)
            self.summary.on_load = page_timings.get('onLoad', 0)
        
        # Parse entries
        for entry in entries:
            request_entry = self._parse_entry(entry)
            self.entries.append(request_entry)
            
            # Update summary
            self.summary.total_requests += 1
            self.summary.total_size += request_entry.size
            self.summary.total_time = max(
                self.summary.total_time,
                request_entry.time
            )
            
            # Update by type metrics
            type_metrics = self.by_type[request_entry.resource_type]
            type_metrics.count += 1
            type_metrics.total_size += request_entry.size
            type_metrics.total_time += request_entry.time
        
        # Generate report
        return self._generate_report(log)
    
    def _parse_entry(self, entry: Dict[str, Any]) -> RequestEntry:
        """Parse a single HAR entry."""
        request = entry.get('request', {})
        response = entry.get('response', {})
        timings = entry.get('timings', {})
        
        # Determine resource type
        mime_type = response.get('content', {}).get('mimeType', '')
        resource_type = self._get_resource_type(mime_type, request.get('url', ''))
        
        # Parse timings
        timing_breakdown = TimingBreakdown(
            blocked=max(0, timings.get('blocked', 0)),
            dns=max(0, timings.get('dns', 0)),
            connect=max(0, timings.get('connect', 0)),
            ssl=max(0, timings.get('ssl', 0)),
            send=max(0, timings.get('send', 0)),
            wait=max(0, timings.get('wait', 0)),
            receive=max(0, timings.get('receive', 0)),
        )
        
        # Check compression
        content = response.get('content', {})
        body_size = response.get('bodySize', 0)
        content_size = content.get('size', body_size)
        is_compressed = body_size < content_size if body_size > 0 else False
        compression_ratio = (
            (content_size - body_size) / content_size
            if content_size > 0 and is_compressed else 0
        )
        
        # Check caching
        headers = {h['name'].lower(): h['value'] for h in response.get('headers', [])}
        is_cached = (
            response.get('status') == 304 or
            'from cache' in headers.get('x-cache', '').lower()
        )
        
        return RequestEntry(
            url=request.get('url', ''),
            method=request.get('method', 'GET'),
            status=response.get('status', 0),
            resource_type=resource_type,
            size=body_size if body_size > 0 else content_size,
            time=entry.get('time', 0),
            timings=timing_breakdown,
            mime_type=mime_type,
            is_cached=is_cached,
            is_compressed=is_compressed,
            compression_ratio=compression_ratio,
        )
    
    def _get_resource_type(self, mime_type: str, url: str) -> ResourceType:
        """Determine resource type from MIME type and URL."""
        mime_lower = mime_type.lower()
        url_lower = url.lower()
        
        if 'html' in mime_lower:
            return ResourceType.DOCUMENT
        elif 'javascript' in mime_lower or url_lower.endswith('.js'):
            return ResourceType.SCRIPT
        elif 'css' in mime_lower or url_lower.endswith('.css'):
            return ResourceType.STYLESHEET
        elif any(t in mime_lower for t in ['image', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg']):
            return ResourceType.IMAGE
        elif 'font' in mime_lower or any(url_lower.endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.otf']):
            return ResourceType.FONT
        elif 'json' in mime_lower or 'xml' in mime_lower:
            return ResourceType.XHR
        elif any(t in mime_lower for t in ['video', 'audio']):
            return ResourceType.MEDIA
        
        return ResourceType.OTHER
    
    def _generate_report(self, log: Dict[str, Any]) -> HARAnalysisReport:
        """Generate the analysis report."""
        # Get page URL
        pages = log.get('pages', [])
        url = pages[0].get('title', 'Unknown') if pages else 'Unknown'
        
        # Find slow requests
        slow_requests = [e for e in self.entries if e.is_slow]
        slow_requests.sort(key=lambda x: x.time, reverse=True)
        
        # Find large resources
        large_resources = [e for e in self.entries if e.is_large]
        large_resources.sort(key=lambda x: x.size, reverse=True)
        
        # Analyze third-party requests
        third_party = self._analyze_third_party()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            slow_requests, large_resources, third_party
        )
        
        return HARAnalysisReport(
            url=url,
            timestamp=datetime.now().isoformat(),
            summary=self.summary,
            by_type=self.by_type,
            slow_requests=slow_requests[:10],  # Top 10
            large_resources=large_resources[:10],  # Top 10
            third_party=third_party,
            recommendations=recommendations,
        )
    
    def _analyze_third_party(self) -> Dict[str, ResourceMetrics]:
        """Analyze third-party requests by domain."""
        # Get first-party domain from document request
        first_party_domain = None
        for entry in self.entries:
            if entry.resource_type == ResourceType.DOCUMENT:
                first_party_domain = entry.domain
                break
        
        third_party: Dict[str, ResourceMetrics] = {}
        
        for entry in self.entries:
            if first_party_domain and entry.domain != first_party_domain:
                if entry.domain not in third_party:
                    third_party[entry.domain] = ResourceMetrics()
                
                metrics = third_party[entry.domain]
                metrics.count += 1
                metrics.total_size += entry.size
                metrics.total_time += entry.time
        
        return third_party
    
    def _generate_recommendations(
        self,
        slow_requests: List[RequestEntry],
        large_resources: List[RequestEntry],
        third_party: Dict[str, ResourceMetrics]
    ) -> List[Recommendation]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Large images
        large_images = [r for r in large_resources if r.resource_type == ResourceType.IMAGE]
        if large_images:
            recommendations.append(Recommendation(
                title="Optimize Images",
                description="Convert large images to WebP format and use responsive images with srcset.",
                impact="high",
                effort="low",
                category="images",
                affected_urls=[r.url for r in large_images[:5]],
                expected_savings=f"-{sum(r.size for r in large_images) // 1024}KB"
            ))
        
        # Large JavaScript
        large_js = [r for r in large_resources if r.resource_type == ResourceType.SCRIPT]
        if large_js:
            recommendations.append(Recommendation(
                title="Code Split JavaScript",
                description="Split large JavaScript bundles and lazy load non-critical code.",
                impact="high",
                effort="medium",
                category="javascript",
                affected_urls=[r.url for r in large_js[:5]],
                expected_savings=f"-{sum(r.size for r in large_js) // 1024}KB initial"
            ))
        
        # Uncompressed resources
        uncompressed = [
            e for e in self.entries
            if not e.is_compressed and e.size > 1000 and
            e.resource_type in [ResourceType.SCRIPT, ResourceType.STYLESHEET, ResourceType.DOCUMENT]
        ]
        if uncompressed:
            recommendations.append(Recommendation(
                title="Enable Compression",
                description="Enable gzip or Brotli compression for text resources.",
                impact="medium",
                effort="low",
                category="network",
                affected_urls=[r.url for r in uncompressed[:5]],
                expected_savings="-60-80% transfer size"
            ))
        
        # Slow API requests
        slow_api = [r for r in slow_requests if r.resource_type in [ResourceType.XHR, ResourceType.FETCH]]
        if slow_api:
            recommendations.append(Recommendation(
                title="Optimize API Responses",
                description="Implement caching, pagination, or optimize backend queries for slow API endpoints.",
                impact="high",
                effort="medium",
                category="caching",
                affected_urls=[r.url for r in slow_api[:5]],
                expected_savings=f"-{int(sum(r.time for r in slow_api) / 1000)}s"
            ))
        
        # Third-party impact
        if third_party:
            total_third_party_time = sum(m.total_time for m in third_party.values())
            if total_third_party_time > 2000:  # > 2s
                recommendations.append(Recommendation(
                    title="Reduce Third-Party Impact",
                    description="Defer non-critical third-party scripts or use facade patterns.",
                    impact="medium",
                    effort="medium",
                    category="javascript",
                    affected_urls=list(third_party.keys())[:5],
                    expected_savings=f"-{int(total_third_party_time / 1000)}s"
                ))
        
        # Too many requests
        if self.summary.total_requests > 50:
            recommendations.append(Recommendation(
                title="Reduce Request Count",
                description="Bundle resources, use sprites for icons, and implement lazy loading.",
                impact="medium",
                effort="medium",
                category="network",
                affected_urls=[],
                expected_savings=f"-{self.summary.total_requests - 50} requests"
            ))
        
        return recommendations
    
    def to_markdown_report(self, report: HARAnalysisReport) -> str:
        """Generate a markdown report from analysis."""
        lines = [
            f"# HAR Analysis Report",
            f"",
            f"## Page: {report.url}",
            f"**Date**: {report.timestamp}",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value | Target | Status |",
            f"|--------|-------|--------|--------|",
            f"| Total Requests | {report.summary.total_requests} | < 50 | {report.summary.request_count_status.value} |",
            f"| Page Weight | {report.summary.total_size / 1024 / 1024:.2f} MB | < 2 MB | {report.summary.size_status.value} |",
            f"| Load Time | {report.summary.on_load / 1000:.2f}s | < 3s | - |",
            f"",
            f"## Resource Breakdown",
            f"",
            f"| Type | Count | Size | Time |",
            f"|------|-------|------|------|",
        ]
        
        for rt, metrics in report.by_type.items():
            if metrics.count > 0:
                lines.append(
                    f"| {rt.value.title()} | {metrics.count} | "
                    f"{metrics.total_size / 1024:.0f} KB | "
                    f"{metrics.total_time:.0f}ms |"
                )
        
        if report.slow_requests:
            lines.extend([
                f"",
                f"## Slow Requests",
                f"",
                f"| URL | Time | TTFB | Size |",
                f"|-----|------|------|------|",
            ])
            for req in report.slow_requests[:5]:
                lines.append(
                    f"| {req.url[:50]}... | {req.time:.0f}ms | "
                    f"{req.timings.wait:.0f}ms | {req.size / 1024:.0f}KB |"
                )
        
        if report.recommendations:
            lines.extend([
                f"",
                f"## Recommendations",
                f"",
            ])
            for i, rec in enumerate(report.recommendations, 1):
                lines.extend([
                    f"### {i}. {rec.title}",
                    f"**Impact**: {rec.impact} | **Effort**: {rec.effort}",
                    f"",
                    f"{rec.description}",
                    f"",
                    f"**Expected Savings**: {rec.expected_savings}",
                    f"",
                ])
        
        return "\n".join(lines)


# Convenience functions
def analyze_har_file(file_path: str) -> HARAnalysisReport:
    """Quick HAR file analysis."""
    return HARAnalyzer().parse_file(file_path)


def generate_har_report(file_path: str) -> str:
    """Generate markdown report from HAR file."""
    analyzer = HARAnalyzer()
    report = analyzer.parse_file(file_path)
    return analyzer.to_markdown_report(report)
