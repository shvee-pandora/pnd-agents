---
description: Scan websites for broken experiences, dead links, and user journey issues.
---

# /bx-scan

Scan websites to detect broken experiences, dead links, missing images, and user journey blockers.

## Usage

```
/bx-scan [URL to scan or describe the pages to check]
```

## Examples

```
/bx-scan https://www.pandora.net/en-us
/bx-scan Scan the checkout flow for broken experiences
/bx-scan Check all product pages for missing images
```

## What This Command Does

1. **Crawls** specified URLs and linked pages
2. **Detects** broken links (404, 500 errors)
3. **Finds** missing images and assets
4. **Identifies** JavaScript errors
5. **Checks** form functionality
6. **Reports** accessibility issues

## Output Format

The agent provides:
- Scan summary with issue counts
- Broken links list with status codes
- Missing asset inventory
- JavaScript error log
- Form validation issues
- Accessibility violations
- Priority-ranked fix recommendations

## Issue Categories

- **Broken Links**: 404s, redirects, timeouts
- **Missing Assets**: Images, scripts, stylesheets
- **JavaScript Errors**: Console errors, exceptions
- **Form Issues**: Validation, submission failures
- **Performance**: Slow resources, blocking scripts
- **Accessibility**: WCAG violations

## Scan Depth Options

- Single page scan
- Full site crawl
- Specific user journey
- Category/section scan

## Pandora BX Standards

- Zero tolerance for 404 errors
- All images must have alt text
- Forms must have proper validation
- Critical paths must be error-free
- Mobile experience parity
