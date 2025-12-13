# Optimization Suggest

Generate specific performance optimization suggestions with implementation details.

## Context

This command provides detailed, actionable optimization suggestions based on performance analysis, including code examples and expected impact.

## Requirements

- Performance analysis results
- Current implementation details
- Technology stack information

## Workflow

### 1. Categorize Optimizations

```markdown
## Optimization Categories

### Image Optimization
- Format conversion (WebP, AVIF)
- Responsive images
- Lazy loading
- Compression

### JavaScript Optimization
- Code splitting
- Tree shaking
- Lazy loading
- Minification

### CSS Optimization
- Critical CSS
- Unused CSS removal
- Minification

### Caching
- Browser caching
- CDN caching
- API caching
- Service workers

### Network
- Preconnect/preload
- HTTP/2
- Compression
- CDN

### Server
- TTFB optimization
- Edge caching
- Database optimization
```

### 2. Generate Suggestions

For each optimization:

```markdown
## Optimization: {Title}

### Problem
{Description of the performance issue}

### Impact
- **Metric Affected**: {LCP/INP/CLS/TTFB}
- **Expected Improvement**: {quantified improvement}
- **Effort**: {Low/Medium/High}
- **Risk**: {Low/Medium/High}

### Current State
```{language}
{Current code or configuration}
```

### Recommended Solution
```{language}
{Optimized code or configuration}
```

### Implementation Steps
1. {Step 1}
2. {Step 2}
3. {Step 3}

### Verification
- {How to verify the optimization worked}
- {Metrics to check}

### Caveats
- {Any trade-offs or considerations}
```

## Common Optimizations

### Image Optimization

```markdown
## Optimization: Convert Images to WebP

### Problem
JPEG/PNG images are larger than necessary.

### Impact
- **Metric Affected**: LCP
- **Expected Improvement**: 25-35% size reduction
- **Effort**: Low
- **Risk**: Low

### Current State
```html
<img src="/images/hero.jpg" alt="Hero" />
```

### Recommended Solution
```tsx
// Using Next.js Image component
import Image from 'next/image';

<Image
  src="/images/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority
  sizes="100vw"
/>
```

Or with Amplience:
```typescript
const imageUrl = buildImageUrl(image, {
  width: 1200,
  aspectRatio: '2:1',
  query: 'fmt=auto&qlt=80'
});
```

### Implementation Steps
1. Update image URLs to use `fmt=auto` parameter
2. Add width/height attributes to prevent CLS
3. Use `priority` for above-fold images
4. Implement responsive `sizes` attribute

### Verification
- Check Network tab for WebP format
- Measure LCP improvement in Lighthouse
```

### JavaScript Code Splitting

```markdown
## Optimization: Code Split Heavy Components

### Problem
Large JavaScript bundle blocks main thread.

### Impact
- **Metric Affected**: TBT, INP
- **Expected Improvement**: 30-50% reduction in initial JS
- **Effort**: Medium
- **Risk**: Low

### Current State
```typescript
import HeavyComponent from './HeavyComponent';

export default function Page() {
  return <HeavyComponent />;
}
```

### Recommended Solution
```typescript
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(
  () => import('./HeavyComponent'),
  {
    loading: () => <Skeleton />,
    ssr: false // if client-only
  }
);

export default function Page() {
  return <HeavyComponent />;
}
```

### Implementation Steps
1. Identify components > 50KB
2. Wrap with `dynamic()` import
3. Add loading fallback
4. Test functionality

### Verification
- Check bundle analyzer for chunk sizes
- Verify component loads correctly
- Measure TBT improvement
```

### Caching Strategy

```markdown
## Optimization: Implement Amplience Content Caching

### Problem
Amplience API calls add latency to every request.

### Impact
- **Metric Affected**: TTFB, LCP
- **Expected Improvement**: 200-500ms reduction
- **Effort**: Medium
- **Risk**: Low

### Current State
```typescript
const content = await fetch(amplienceUrl);
```

### Recommended Solution
```typescript
// In API route or server component
const content = await fetch(amplienceUrl, {
  next: {
    revalidate: 300, // 5 minutes
    tags: ['amplience-content']
  }
});

// For preview mode (VSE)
const cacheOption = vse ? 'no-store' : 'force-cache';
const content = await fetch(amplienceUrl, {
  cache: cacheOption
});
```

### Implementation Steps
1. Add `next.revalidate` to fetch calls
2. Implement cache tags for invalidation
3. Bypass cache for preview mode
4. Set up revalidation webhook

### Verification
- Check response headers for cache status
- Measure TTFB with/without cache
- Verify preview mode bypasses cache
```

### Critical CSS

```markdown
## Optimization: Inline Critical CSS

### Problem
External CSS blocks rendering.

### Impact
- **Metric Affected**: FCP, LCP
- **Expected Improvement**: 100-300ms reduction
- **Effort**: Medium
- **Risk**: Medium

### Current State
```html
<link rel="stylesheet" href="/styles/main.css" />
```

### Recommended Solution
```tsx
// In _document.tsx or layout.tsx
import { getCriticalCSS } from '@/utils/critical-css';

export default function Document() {
  return (
    <html>
      <head>
        <style dangerouslySetInnerHTML={{ __html: criticalCSS }} />
        <link 
          rel="preload" 
          href="/styles/main.css" 
          as="style"
          onLoad="this.onload=null;this.rel='stylesheet'"
        />
        <noscript>
          <link rel="stylesheet" href="/styles/main.css" />
        </noscript>
      </head>
      <body>...</body>
    </html>
  );
}
```

### Implementation Steps
1. Extract critical CSS for above-fold content
2. Inline in document head
3. Async load remaining CSS
4. Test across pages

### Verification
- Check that above-fold renders without FOUC
- Measure FCP improvement
- Verify all styles load eventually
```

## Example

### Input
```
Performance Issue: LCP is 3.8s
LCP Element: Hero image (450KB JPEG)
Stack: Next.js, Amplience
```

### Output
```markdown
# Optimization Suggestions for LCP

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

### Verification
- Network tab shows WebP format
- Image size reduced to ~150KB
- LCP improved by ~1s

---

## 2. Preload Hero Image

### Problem
Hero image discovery is delayed until CSS/JS loads.

### Impact
- **Metric Affected**: LCP
- **Expected Improvement**: -300ms
- **Effort**: Low
- **Risk**: Low

### Recommended Solution
```tsx
// In page head
<link
  rel="preload"
  as="image"
  href={heroUrl}
  imageSrcSet={`${heroUrl}&w=640 640w, ${heroUrl}&w=1200 1200w`}
  imageSizes="100vw"
/>
```

### Implementation Steps
1. Add preload link in document head
2. Match srcset with Image component
3. Test on slow connections

### Verification
- Network waterfall shows early image request
- LCP improved by ~300ms
```

## Summary

The optimization-suggest command provides detailed, actionable optimization suggestions with code examples, implementation steps, and expected impact for each recommendation.
