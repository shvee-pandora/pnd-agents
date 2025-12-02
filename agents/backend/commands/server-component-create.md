# Server Component Create

Create Next.js Server Components with data fetching patterns.

## Context

This command creates Next.js Server Components following Pandora's patterns for server-side data fetching, caching, and error handling.

## Requirements

- Component purpose and data needs
- Data sources (Amplience, API, etc.)
- Caching requirements
- Error handling strategy

## Workflow

### 1. Design Component Structure

```markdown
## Server Component Design

### Purpose
{What the component does}

### Data Requirements
- Source: {Amplience/API/Database}
- Endpoint: {URL or function}
- Caching: {Strategy}

### Props
- {prop}: {type} - {description}

### Error Handling
- Loading: {strategy}
- Error: {strategy}
- Not Found: {strategy}
```

### 2. Generate Server Component

```typescript
// lib/components/organisms/{ComponentName}/{ComponentName}.tsx

import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { {ComponentName}Skeleton } from './{ComponentName}Skeleton';
import { fetchData } from '@/services/{service}';
import type { {ComponentName}Props } from './types';

/**
 * {ComponentName} - Server Component
 * 
 * Fetches and displays {description}.
 */
export async function {ComponentName}({ id, ...props }: {ComponentName}Props) {
  // Fetch data on the server
  const data = await fetchData(id);

  // Handle not found
  if (!data) {
    notFound();
  }

  return (
    <div data-testid="{component-name}">
      {/* Render content */}
    </div>
  );
}

// Export with Suspense wrapper for streaming
export function {ComponentName}WithSuspense(props: {ComponentName}Props) {
  return (
    <Suspense fallback={<{ComponentName}Skeleton />}>
      <{ComponentName} {...props} />
    </Suspense>
  );
}
```

### 3. Implement Data Fetching

```typescript
// lib/services/{service}/index.ts

import { cache } from 'react';

// Cached fetch function (deduped within request)
export const fetchData = cache(async (id: string) => {
  const response = await fetch(`${API_URL}/data/${id}`, {
    next: {
      revalidate: 300, // 5 minutes
      tags: ['data', `data-${id}`],
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error(`Failed to fetch data: ${response.status}`);
  }

  return response.json();
});

// Parallel data fetching
export async function fetchPageData(slug: string) {
  const [content, navigation, footer] = await Promise.all([
    fetchContent(slug),
    fetchNavigation(),
    fetchFooter(),
  ]);

  return { content, navigation, footer };
}
```

### 4. Add Loading State

```typescript
// lib/components/organisms/{ComponentName}/{ComponentName}Skeleton.tsx

export function {ComponentName}Skeleton() {
  return (
    <div 
      className="animate-pulse"
      data-testid="{component-name}-skeleton"
      aria-busy="true"
      aria-label="Loading {component name}"
    >
      <div className="h-8 bg-gray-200 rounded w-3/4 mb-4" />
      <div className="h-4 bg-gray-200 rounded w-full mb-2" />
      <div className="h-4 bg-gray-200 rounded w-5/6" />
    </div>
  );
}
```

### 5. Add Error Boundary

```typescript
// lib/components/organisms/{ComponentName}/{ComponentName}Error.tsx
'use client';

import { useEffect } from 'react';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export function {ComponentName}Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error('{ComponentName} error:', error);
  }, [error]);

  return (
    <div 
      className="p-4 border border-red-200 rounded bg-red-50"
      role="alert"
    >
      <h2 className="text-lg font-medium text-red-800">
        Something went wrong
      </h2>
      <p className="text-sm text-red-600 mt-1">
        {error.message || 'Failed to load content'}
      </p>
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Try again
      </button>
    </div>
  );
}
```

### 6. Implement Caching Strategies

```typescript
// Force dynamic (no caching)
export const dynamic = 'force-dynamic';

// Static with revalidation
export const revalidate = 3600; // 1 hour

// Fetch with cache tags for on-demand revalidation
const data = await fetch(url, {
  next: {
    tags: ['content', `content-${id}`],
  },
});

// Revalidate on-demand (in API route)
import { revalidateTag } from 'next/cache';
revalidateTag('content');
```

## Patterns

### Amplience Content Fetching
```typescript
import { getContentWithFallback } from '@/services/amplience/helpers/content-fallback';

export async function PageContent({ slug }: { slug: string }) {
  const content = await getContentWithFallback(slug);

  if (!content) {
    notFound();
  }

  return <ContentRenderer content={content} />;
}
```

### Parallel Data Fetching
```typescript
export async function Page({ params }: { params: { slug: string } }) {
  // Fetch all data in parallel
  const [content, breadcrumbs, relatedContent] = await Promise.all([
    fetchContent(params.slug),
    fetchBreadcrumbs(params.slug),
    fetchRelatedContent(params.slug),
  ]);

  return (
    <>
      <Breadcrumb items={breadcrumbs} />
      <MainContent content={content} />
      <RelatedContent items={relatedContent} />
    </>
  );
}
```

### Streaming with Suspense
```typescript
export default function Page() {
  return (
    <main>
      {/* Critical content loads first */}
      <Header />
      
      {/* Stream in as ready */}
      <Suspense fallback={<HeroSkeleton />}>
        <Hero />
      </Suspense>
      
      <Suspense fallback={<ContentSkeleton />}>
        <MainContent />
      </Suspense>
      
      {/* Lower priority, streams last */}
      <Suspense fallback={<FooterSkeleton />}>
        <Footer />
      </Suspense>
    </main>
  );
}
```

## Example

### Input
```
Component: PageCover
Data: Amplience content with banner image
Caching: 5 minutes with on-demand revalidation
```

### Output

```typescript
// lib/components/organisms/PageCover/PageCover.tsx
import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import Image from 'next/image';
import { fetchBannerContent } from '@/services/amplience/content-api';
import { buildImageUrl } from '@/services/amplience/utils/image';
import { PageCoverSkeleton } from './PageCoverSkeleton';
import type { PageCoverProps } from './types';

export async function PageCover({ contentId }: PageCoverProps) {
  const banner = await fetchBannerContent(contentId);

  if (!banner) {
    return null;
  }

  const { title, subtitle, media } = banner;
  
  const desktopUrl = media?.desktopImg 
    ? buildImageUrl(media.desktopImg, { width: 1920, aspectRatio: '5:2' })
    : null;
  
  const mobileUrl = media?.mobileImg
    ? buildImageUrl(media.mobileImg, { width: 768, aspectRatio: '3:4' })
    : null;

  return (
    <section 
      className="relative w-full"
      data-testid="page-cover"
    >
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
            alt={media?.imageAltText || title}
            width={1920}
            height={768}
            priority
            className="w-full h-auto object-cover"
          />
        </picture>
      )}
      
      <div className="absolute inset-0 flex flex-col justify-center items-center text-center p-4">
        <h1 className="text-4xl md:text-6xl font-bold text-white">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-4 text-xl text-white/90">
            {subtitle}
          </p>
        )}
      </div>
    </section>
  );
}

export function PageCoverWithSuspense(props: PageCoverProps) {
  return (
    <Suspense fallback={<PageCoverSkeleton />}>
      <PageCover {...props} />
    </Suspense>
  );
}
```

```typescript
// lib/components/organisms/PageCover/PageCoverSkeleton.tsx
export function PageCoverSkeleton() {
  return (
    <div 
      className="relative w-full aspect-[5/2] bg-gray-200 animate-pulse"
      data-testid="page-cover-skeleton"
      aria-busy="true"
      aria-label="Loading page cover"
    >
      <div className="absolute inset-0 flex flex-col justify-center items-center">
        <div className="h-12 w-64 bg-gray-300 rounded mb-4" />
        <div className="h-6 w-48 bg-gray-300 rounded" />
      </div>
    </div>
  );
}
```

## Validation Checklist

- [ ] Server component (no 'use client')
- [ ] Data fetching with proper caching
- [ ] Loading state with Skeleton
- [ ] Error handling implemented
- [ ] Not found handling
- [ ] TypeScript types defined
- [ ] Accessibility attributes
- [ ] Test IDs for testing

## Summary

The server-component-create command generates Next.js Server Components with proper data fetching, caching, loading states, and error handling following Pandora's patterns.
