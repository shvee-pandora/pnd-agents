# Example Task: Performance Optimization

This example demonstrates how the PG AI Squad agents collaborate to analyze performance and implement optimizations.

## Task Description

```
Analyze the HAR file from the homepage and optimize performance.
Target metrics:
- LCP < 2.5s
- Page weight < 2MB
- Total requests < 50

HAR file: homepage.har
```

## Agent Workflow

### 1. Task Manager Agent

**Input**: Natural language task description

**Action**: Decomposes task into subtasks

```markdown
## Task Decomposition

### Subtask 1: Analyze HAR File
- Agent: Performance
- Command: har-analyze
- Input: homepage.har
- Output: Performance analysis

### Subtask 2: Generate Performance Report
- Agent: Performance
- Command: performance-report
- Input: HAR analysis
- Output: Detailed report with metrics

### Subtask 3: Generate Optimization Suggestions
- Agent: Performance
- Command: optimization-suggest
- Input: Performance report
- Output: Prioritized optimizations

### Subtask 4: Implement Image Optimizations
- Agent: Frontend Engineer
- Command: component-generate
- Input: Image optimization suggestions
- Output: Updated components

### Subtask 5: Code Review
- Agent: Code Review
- Command: review-code
- Input: Optimized code
- Output: Review approval

### Subtask 6: Merge Outputs
- Agent: Task Manager
- Command: task-merge
- Input: All outputs
- Output: Final deliverable
```

### 2. Performance Agent

**Subtask 1: Analyze HAR File**

```markdown
# HAR Analysis Results

## Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Requests | 87 | < 50 | Over |
| Page Weight | 3.2 MB | < 2 MB | Over |
| Load Time | 4.2s | < 3s | Over |
| TTFB | 650ms | < 800ms | Good |

## Resource Breakdown

| Type | Count | Size | Time |
|------|-------|------|------|
| Document | 1 | 45 KB | 650ms |
| Script | 24 | 1.2 MB | 1.8s |
| Stylesheet | 8 | 180 KB | 400ms |
| Image | 42 | 1.6 MB | 2.1s |
| Font | 6 | 150 KB | 300ms |
| XHR/Fetch | 6 | 85 KB | 800ms |

## Slow Requests (> 1s)

| URL | Time | Size | Type |
|-----|------|------|------|
| /api/content/homepage | 1,850ms | 45KB | XHR |
| /images/hero-desktop.jpg | 1,200ms | 450KB | Image |
| /scripts/analytics.js | 1,100ms | 120KB | Script |

## Large Resources (> 100KB)

| URL | Size | Type |
|-----|------|------|
| /images/hero-desktop.jpg | 450KB | Image |
| /scripts/vendor.js | 380KB | Script |
| /images/collection-1.jpg | 280KB | Image |
| /images/collection-2.jpg | 260KB | Image |
```

**Subtask 2: Generate Performance Report**

```markdown
# Performance Report

## Page: https://www.pandoragroup.com/
**Date**: March 15, 2024
**Overall Score**: 62/100

## Core Web Vitals

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| LCP | 3.8s | < 2.5s | Poor |
| INP | 180ms | < 200ms | Good |
| CLS | 0.15 | < 0.1 | Needs Improvement |
| TTFB | 650ms | < 800ms | Good |

### LCP Analysis

The LCP element is the hero image (`<img class="hero-image">`).

**Breakdown**:
- TTFB: 650ms (17%)
- Resource Load: 2,400ms (63%)
- Render Delay: 750ms (20%)

The hero image is 450KB JPEG. Converting to WebP and using responsive images could reduce this by 60%.

### CLS Analysis

Layout shift caused by:
1. Hero image without explicit dimensions
2. Font loading causing text reflow
3. Late-loading navigation elements

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

**Subtask 3: Generate Optimization Suggestions**

```markdown
# Optimization Suggestions

## 1. Convert Hero Image to WebP

### Problem
The hero image is a 450KB JPEG, which is the LCP element taking 2.4s to load.

### Impact
- **Metric Affected**: LCP
- **Expected Improvement**: -1.0s (3.8s → 2.8s)
- **Effort**: Low
- **Risk**: Low

### Recommended Solution
```typescript
// Use Amplience Dynamic Media with auto format
const heroUrl = buildImageUrl(heroImage, {
  width: 1200,
  aspectRatio: '5:2',
  query: 'fmt=auto&qlt=80'
});

// In component
<Image
  src={heroUrl}
  alt={heroAltText}
  width={1200}
  height={480}
  priority
  sizes="100vw"
/>
```

### Implementation Steps
1. Update `buildImageUrl` to include `fmt=auto`
2. Add `priority` attribute to hero Image
3. Set explicit width/height to prevent CLS
4. Add responsive `sizes` attribute

---

## 2. Code Split Vendor Bundle

### Problem
Large JavaScript bundle (380KB) blocks main thread.

### Impact
- **Metric Affected**: TBT, INP
- **Expected Improvement**: -0.5s TBT
- **Effort**: Medium
- **Risk**: Low

### Recommended Solution
```typescript
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(
  () => import('./HeavyComponent'),
  {
    loading: () => <Skeleton />,
    ssr: false
  }
);
```

---

## 3. Implement Amplience Content Caching

### Problem
Amplience API calls add 1.8s latency to every request.

### Impact
- **Metric Affected**: TTFB, LCP
- **Expected Improvement**: -1.0s
- **Effort**: Medium
- **Risk**: Low

### Recommended Solution
```typescript
const content = await fetch(amplienceUrl, {
  next: {
    revalidate: 300, // 5 minutes
    tags: ['amplience-content']
  }
});
```
```

### 3. Frontend Engineer Agent

**Subtask 4: Implement Image Optimizations**

```typescript
// lib/components/organisms/PageCover/PageCover.tsx
import Image from 'next/image';
import { buildImageUrl } from '@/services/amplience/utils/image';

export const PageCover: React.FC<PageCoverProps> = ({ media }) => {
  const desktopUrl = media?.desktopImg
    ? buildImageUrl(media.desktopImg, {
        width: 1920,
        aspectRatio: '5:2',
        query: 'fmt=auto&qlt=80'
      })
    : null;

  const mobileUrl = media?.mobileImg
    ? buildImageUrl(media.mobileImg, {
        width: 768,
        aspectRatio: '3:4',
        query: 'fmt=auto&qlt=80'
      })
    : null;

  return (
    <section className="relative w-full" data-testid="page-cover">
      {desktopUrl && (
        <picture>
          {mobileUrl && (
            <source
              media="(max-width: 767px)"
              srcSet={mobileUrl}
            />
          )}
          <Image
            src={desktopUrl}
            alt={media?.imageAltText || ''}
            width={1920}
            height={768}
            priority
            sizes="100vw"
            className="w-full h-auto object-cover"
          />
        </picture>
      )}
    </section>
  );
};
```

### 4. Code Review Agent

**Subtask 5: Code Review**

```markdown
## Code Review: Performance Optimizations

### Summary
- **Files Reviewed**: 3
- **Issues Found**: 0
- **Recommendation**: Approve

### Findings

All optimizations follow best practices:
- WebP format with fallback via `fmt=auto`
- Explicit dimensions prevent CLS
- `priority` attribute for LCP element
- Responsive `sizes` attribute for optimal loading

### Performance Impact
- Expected LCP improvement: -1.0s
- Expected page weight reduction: -300KB
- No regressions identified

### Approval
Approved - Ready for deployment
```

### 5. Task Manager Agent

**Subtask 6: Merge Outputs**

```markdown
## Final Deliverable

### Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| LCP | 3.8s | 2.8s | -1.0s |
| Page Weight | 3.2 MB | 2.5 MB | -700KB |
| Total Requests | 87 | 75 | -12 |

### Files Modified
1. `lib/components/organisms/PageCover/PageCover.tsx`
2. `lib/services/amplience/utils/image.ts`
3. `next.config.js` (image domains)

### Remaining Optimizations
1. Code split vendor bundle (Phase 2)
2. Implement lazy loading (Phase 2)
3. Cache Amplience content (Phase 2)

### Ready for PR
All Phase 1 optimizations are ready to be committed.
```

## Running This Example

1. Export HAR file from browser DevTools
2. Start the Task Manager Agent
3. Provide the HAR file and performance targets
4. Review the analysis and optimization suggestions
5. Implement approved optimizations
6. Create a PR with the changes

## Expected Output

```
Performance Report:
- HAR analysis with metrics
- Core Web Vitals assessment
- Prioritized optimization roadmap

Code Changes:
- Optimized image loading
- Updated build configuration
- Caching implementation
```
