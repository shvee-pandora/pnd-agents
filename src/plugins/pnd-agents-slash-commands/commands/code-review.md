---
description: Review code for quality, security, performance, and Pandora standards compliance.
---

# /code-review

Perform comprehensive code review analyzing quality, security vulnerabilities, performance issues, and adherence to Pandora coding standards.

## Usage

```
/code-review [paste your code or describe the file to review]
```

## Examples

```
/code-review [paste component code here]
/code-review Review the checkout API endpoint for security issues
/code-review Analyze this React hook for performance optimizations
```

## What This Command Does

1. **Scans** code for common issues and anti-patterns
2. **Checks** security vulnerabilities (XSS, injection, etc.)
3. **Analyzes** performance bottlenecks
4. **Validates** TypeScript type safety
5. **Verifies** Pandora coding standards compliance
6. **Suggests** specific improvements with code examples

## Output Format

The agent provides:
- Summary of findings by severity (Critical, Warning, Info)
- Security vulnerability report
- Performance optimization suggestions
- Code quality improvements
- Pandora standards compliance checklist
- Refactored code snippets where applicable

## Review Categories

- **Security**: XSS, CSRF, injection, authentication
- **Performance**: Re-renders, memory leaks, bundle size
- **Quality**: DRY, SOLID, complexity, readability
- **TypeScript**: Type safety, any usage, proper interfaces
- **Testing**: Testability, coverage suggestions
- **Accessibility**: ARIA, semantic HTML, keyboard navigation

## Pandora Standards Checked

- TypeScript strict mode compliance
- Component structure and naming
- Error handling patterns
- Logging and monitoring hooks
- API response handling
