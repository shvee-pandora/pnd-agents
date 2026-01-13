---
description: Analyze HAR files and performance metrics to identify optimization opportunities.
---

# /performance

Analyze web performance using HAR files, Lighthouse reports, or performance descriptions to identify bottlenecks and optimization opportunities.

## Usage

```
/performance [paste HAR data, metrics, or describe performance issue]
```

## Examples

```
/performance Analyze this HAR file for slow API calls [paste HAR]
/performance Our LCP is 4.2s on product pages, help identify causes
/performance Review these Core Web Vitals and suggest improvements
```

## What This Command Does

1. **Parses** HAR files or performance data
2. **Identifies** slow requests and bottlenecks
3. **Analyzes** Core Web Vitals (LCP, FID, CLS)
4. **Detects** render-blocking resources
5. **Finds** optimization opportunities
6. **Provides** actionable recommendations

## Output Format

The agent provides:
- Performance summary with key metrics
- Waterfall analysis of critical path
- Slow request identification (>500ms)
- Resource optimization suggestions
- Caching recommendations
- Code-level fixes where applicable

## Metrics Analyzed

- **Core Web Vitals**: LCP, FID/INP, CLS
- **Loading**: TTFB, FCP, Speed Index
- **Resources**: Bundle size, image optimization
- **Network**: Request count, payload size
- **Caching**: Cache hit rates, TTL recommendations

## Optimization Categories

- Image optimization (WebP, lazy loading, sizing)
- JavaScript bundle splitting
- CSS critical path optimization
- API response caching
- CDN configuration
- Preloading and prefetching strategies
