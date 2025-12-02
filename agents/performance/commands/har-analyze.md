# HAR Analyze

Analyze HTTP Archive (HAR) files to identify performance bottlenecks.

## Context

This command parses HAR files to extract performance metrics, identify slow requests, and provide optimization recommendations.

## Requirements

- HAR file from browser DevTools or performance testing tool
- Performance thresholds and targets
- Context about the page being analyzed

## Workflow

### 1. Parse HAR File

Extract key data from HAR structure:

```typescript
interface HARAnalysis {
  summary: {
    totalRequests: number;
    totalSize: number;
    totalTime: number;
    onContentLoad: number;
    onLoad: number;
  };
  byType: Record<ResourceType, ResourceMetrics>;
  slowRequests: SlowRequest[];
  largeResources: LargeResource[];
  blockingResources: BlockingResource[];
  thirdParty: ThirdPartyRequest[];
}
```

### 2. Calculate Metrics

```markdown
## Key Metrics

### Timing Metrics
- **TTFB (Time to First Byte)**: Time until first byte received
- **DNS Lookup**: Time for DNS resolution
- **TCP Connect**: Time to establish TCP connection
- **SSL/TLS**: Time for SSL handshake
- **Request**: Time to send request
- **Wait**: Server processing time
- **Receive**: Time to download response

### Size Metrics
- **Total Page Weight**: Sum of all resource sizes
- **By Type**: Breakdown by resource type
- **Compression**: Gzip/Brotli savings

### Count Metrics
- **Total Requests**: Number of HTTP requests
- **By Type**: Requests per resource type
- **Third Party**: External domain requests
```

### 3. Identify Issues

```markdown
## Issue Detection

### Slow Requests (> 1s)
Requests taking longer than 1 second to complete.

### Large Resources (> 100KB)
Resources exceeding 100KB uncompressed.

### Blocking Resources
CSS/JS in head blocking render.

### Uncompressed Resources
Text resources without gzip/brotli.

### Cache Misses
Resources without proper caching headers.

### Redirect Chains
Multiple redirects before final resource.

### Third Party Impact
External resources affecting performance.
```

### 4. Generate Report

```markdown
# HAR Analysis Report

## Page: {URL}
**Date**: {Date}
**Browser**: {Browser}

## Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Requests | {n} | < 50 | {status} |
| Page Weight | {n} MB | < 2 MB | {status} |
| Load Time | {n}s | < 3s | {status} |
| TTFB | {n}ms | < 800ms | {status} |

## Resource Breakdown

| Type | Count | Size | Time |
|------|-------|------|------|
| Document | {n} | {size} | {time} |
| Script | {n} | {size} | {time} |
| Stylesheet | {n} | {size} | {time} |
| Image | {n} | {size} | {time} |
| Font | {n} | {size} | {time} |
| XHR/Fetch | {n} | {size} | {time} |
| Other | {n} | {size} | {time} |

## Slow Requests

| URL | Time | TTFB | Size | Type |
|-----|------|------|------|------|
| {url} | {time}ms | {ttfb}ms | {size}KB | {type} |

## Large Resources

| URL | Size | Type | Suggestion |
|-----|------|------|------------|
| {url} | {size}KB | {type} | {suggestion} |

## Blocking Resources

| URL | Type | Impact |
|-----|------|--------|
| {url} | {type} | {impact} |

## Third Party Analysis

| Domain | Requests | Size | Time |
|--------|----------|------|------|
| {domain} | {n} | {size} | {time} |

## Recommendations

### Critical (High Impact)
1. {Recommendation with expected improvement}
2. {Recommendation with expected improvement}

### Important (Medium Impact)
1. {Recommendation}
2. {Recommendation}

### Nice to Have (Low Impact)
1. {Recommendation}
2. {Recommendation}
```

## Analysis Functions

### Slow Request Detection
```typescript
function findSlowRequests(entries: HAREntry[], threshold = 1000): SlowRequest[] {
  return entries
    .filter(entry => entry.time > threshold)
    .map(entry => ({
      url: entry.request.url,
      method: entry.request.method,
      time: entry.time,
      ttfb: entry.timings.wait,
      size: entry.response.content.size,
      type: getResourceType(entry),
      suggestion: generateSuggestion(entry)
    }))
    .sort((a, b) => b.time - a.time);
}
```

### Large Resource Detection
```typescript
function findLargeResources(entries: HAREntry[], threshold = 100000): LargeResource[] {
  return entries
    .filter(entry => entry.response.content.size > threshold)
    .map(entry => ({
      url: entry.request.url,
      size: entry.response.content.size,
      type: getResourceType(entry),
      compressed: hasCompression(entry),
      suggestion: generateSizeSuggestion(entry)
    }))
    .sort((a, b) => b.size - a.size);
}
```

### Blocking Resource Detection
```typescript
function findBlockingResources(entries: HAREntry[]): BlockingResource[] {
  return entries
    .filter(entry => {
      const type = getResourceType(entry);
      return (type === 'script' || type === 'stylesheet') && 
             isRenderBlocking(entry);
    })
    .map(entry => ({
      url: entry.request.url,
      type: getResourceType(entry),
      size: entry.response.content.size,
      time: entry.time
    }));
}
```

## Example

### Input
```
HAR file from homepage load
URL: https://www.pandoragroup.com/
```

### Output
```markdown
# HAR Analysis Report

## Page: https://www.pandoragroup.com/
**Date**: 2024-03-15
**Browser**: Chrome 122

## Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Requests | 87 | < 50 | ⚠️ Over |
| Page Weight | 3.2 MB | < 2 MB | ⚠️ Over |
| Load Time | 4.2s | < 3s | ⚠️ Over |
| TTFB | 650ms | < 800ms | ✅ Good |

## Resource Breakdown

| Type | Count | Size | Time |
|------|-------|------|------|
| Document | 1 | 45 KB | 650ms |
| Script | 24 | 1.2 MB | 1.8s |
| Stylesheet | 8 | 180 KB | 400ms |
| Image | 42 | 1.6 MB | 2.1s |
| Font | 6 | 150 KB | 300ms |
| XHR/Fetch | 6 | 85 KB | 800ms |

## Slow Requests

| URL | Time | TTFB | Size | Type |
|-----|------|------|------|------|
| /api/content/homepage | 1,850ms | 1,200ms | 45KB | XHR |
| /images/hero-desktop.jpg | 1,200ms | 100ms | 450KB | Image |
| /scripts/analytics.js | 1,100ms | 800ms | 120KB | Script |

## Large Resources

| URL | Size | Type | Suggestion |
|-----|------|------|------------|
| /images/hero-desktop.jpg | 450KB | Image | Use WebP, resize to viewport |
| /scripts/vendor.js | 380KB | Script | Code split, lazy load |
| /images/collection-1.jpg | 280KB | Image | Compress, use srcset |

## Recommendations

### Critical (High Impact)
1. **Optimize hero image** - Convert to WebP and resize. Expected: -300KB, -0.8s
2. **Code split vendor bundle** - Lazy load non-critical JS. Expected: -200KB, -0.5s
3. **Reduce API response time** - Cache Amplience content. Expected: -1s

### Important (Medium Impact)
1. **Lazy load below-fold images** - Defer 30 images. Expected: -1MB initial
2. **Preconnect to CDN** - Add preconnect hints. Expected: -200ms

### Nice to Have (Low Impact)
1. **Remove unused CSS** - Purge unused styles. Expected: -50KB
```

## Summary

The har-analyze command parses HAR files to identify performance bottlenecks, providing detailed metrics and actionable optimization recommendations.
