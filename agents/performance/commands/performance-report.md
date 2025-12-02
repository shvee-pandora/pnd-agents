# Performance Report

Generate comprehensive performance reports with Core Web Vitals analysis.

## Context

This command generates detailed performance reports combining HAR analysis, Core Web Vitals, and optimization recommendations.

## Requirements

- HAR file or performance metrics
- Core Web Vitals data (if available)
- Page context and performance targets

## Workflow

### 1. Collect Metrics

Gather performance data from multiple sources:

```markdown
## Data Sources

### HAR File
- Request/response timing
- Resource sizes
- Waterfall analysis

### Core Web Vitals
- LCP (Largest Contentful Paint)
- FID (First Input Delay) / INP (Interaction to Next Paint)
- CLS (Cumulative Layout Shift)
- TTFB (Time to First Byte)

### Lighthouse
- Performance score
- Opportunities
- Diagnostics
```

### 2. Analyze Core Web Vitals

```markdown
## Core Web Vitals Analysis

### LCP (Largest Contentful Paint)
**Target**: < 2.5s
**Measured**: {value}s
**Status**: {Good/Needs Improvement/Poor}

**LCP Element**: {element description}
**Breakdown**:
- TTFB: {value}ms
- Resource Load: {value}ms
- Render Delay: {value}ms

**Optimization**:
- {Specific recommendation}

### INP (Interaction to Next Paint)
**Target**: < 200ms
**Measured**: {value}ms
**Status**: {Good/Needs Improvement/Poor}

**Slowest Interaction**: {interaction description}

**Optimization**:
- {Specific recommendation}

### CLS (Cumulative Layout Shift)
**Target**: < 0.1
**Measured**: {value}
**Status**: {Good/Needs Improvement/Poor}

**Largest Shift**: {element description}

**Optimization**:
- {Specific recommendation}

### TTFB (Time to First Byte)
**Target**: < 800ms
**Measured**: {value}ms
**Status**: {Good/Needs Improvement/Poor}

**Optimization**:
- {Specific recommendation}
```

### 3. Generate Performance Score

```markdown
## Performance Score

### Overall: {score}/100

### Category Breakdown
| Category | Score | Weight |
|----------|-------|--------|
| First Contentful Paint | {score} | 10% |
| Largest Contentful Paint | {score} | 25% |
| Total Blocking Time | {score} | 30% |
| Cumulative Layout Shift | {score} | 25% |
| Speed Index | {score} | 10% |
```

### 4. Identify Opportunities

```markdown
## Optimization Opportunities

### High Impact

#### 1. {Opportunity Title}
**Potential Savings**: {time/size}
**Effort**: {Low/Medium/High}

**Current State**:
{Description of current issue}

**Recommended Action**:
{Specific steps to implement}

**Expected Result**:
{Measurable improvement}

### Medium Impact
...

### Low Impact
...
```

### 5. Generate Full Report

```markdown
# Performance Report

## Executive Summary

**Page**: {URL}
**Date**: {Date}
**Overall Score**: {score}/100

### Key Findings
- {Finding 1}
- {Finding 2}
- {Finding 3}

### Quick Wins
1. {Quick win with expected impact}
2. {Quick win with expected impact}

---

## Core Web Vitals

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| LCP | {value}s | < 2.5s | {status} |
| INP | {value}ms | < 200ms | {status} |
| CLS | {value} | < 0.1 | {status} |
| TTFB | {value}ms | < 800ms | {status} |

### LCP Analysis
{Detailed LCP analysis}

### INP Analysis
{Detailed INP analysis}

### CLS Analysis
{Detailed CLS analysis}

---

## Resource Analysis

### Summary
| Metric | Value | Budget | Status |
|--------|-------|--------|--------|
| Total Requests | {n} | 50 | {status} |
| Total Size | {n} MB | 2 MB | {status} |
| JavaScript | {n} KB | 300 KB | {status} |
| CSS | {n} KB | 100 KB | {status} |
| Images | {n} KB | 1 MB | {status} |

### Critical Path
{Analysis of render-blocking resources}

### Third Party Impact
{Analysis of third-party scripts}

---

## Optimization Roadmap

### Phase 1: Quick Wins (1-2 days)
| Action | Impact | Effort |
|--------|--------|--------|
| {Action} | {Impact} | Low |

### Phase 2: Medium Term (1-2 weeks)
| Action | Impact | Effort |
|--------|--------|--------|
| {Action} | {Impact} | Medium |

### Phase 3: Long Term (1+ month)
| Action | Impact | Effort |
|--------|--------|--------|
| {Action} | {Impact} | High |

---

## Implementation Details

### 1. {Optimization Title}

**Problem**:
{Description of the issue}

**Solution**:
```{language}
{Code example}
```

**Verification**:
{How to verify the fix}

---

## Monitoring Recommendations

### Metrics to Track
- {Metric 1}
- {Metric 2}

### Alerting Thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| LCP | > 2.5s | > 4s |
| INP | > 200ms | > 500ms |
| CLS | > 0.1 | > 0.25 |

### Tools
- {Recommended monitoring tool}
```

## Example

### Input
```
Page: https://www.pandoragroup.com/
HAR file: homepage.har
Lighthouse report: homepage-lighthouse.json
```

### Output
```markdown
# Performance Report

## Executive Summary

**Page**: https://www.pandoragroup.com/
**Date**: March 15, 2024
**Overall Score**: 62/100

### Key Findings
- LCP is 3.8s, primarily due to unoptimized hero image
- 380KB of unused JavaScript loaded on initial page
- Third-party scripts add 1.2s to load time

### Quick Wins
1. Convert hero image to WebP (-0.8s LCP)
2. Defer non-critical JavaScript (-0.5s TBT)
3. Add preconnect hints for CDN (-200ms)

---

## Core Web Vitals

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| LCP | 3.8s | < 2.5s | 🔴 Poor |
| INP | 180ms | < 200ms | 🟢 Good |
| CLS | 0.15 | < 0.1 | 🟡 Needs Improvement |
| TTFB | 650ms | < 800ms | 🟢 Good |

### LCP Analysis
The LCP element is the hero image (`<img class="hero-image">`).

**Breakdown**:
- TTFB: 650ms (17%)
- Resource Load: 2,400ms (63%)
- Render Delay: 750ms (20%)

The hero image is 450KB JPEG. Converting to WebP and using responsive images could reduce this by 60%.

---

## Optimization Roadmap

### Phase 1: Quick Wins (1-2 days)
| Action | Impact | Effort |
|--------|--------|--------|
| Convert images to WebP | -0.8s LCP | Low |
| Add preconnect hints | -200ms | Low |
| Defer analytics scripts | -0.3s TBT | Low |

### Phase 2: Medium Term (1-2 weeks)
| Action | Impact | Effort |
|--------|--------|--------|
| Code split vendor bundle | -0.5s TBT | Medium |
| Implement lazy loading | -1MB initial | Medium |
| Cache Amplience content | -0.5s TTFB | Medium |
```

## Summary

The performance-report command generates comprehensive performance reports combining Core Web Vitals analysis, resource analysis, and a prioritized optimization roadmap.
