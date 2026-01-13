---
description: Generate React/Next.js components following Pandora coding standards.
---

# /frontend

Generate production-ready React and Next.js components with TypeScript, following Pandora's coding standards and best practices.

## Usage

```
/frontend [component description or requirements]
```

## Examples

```
/frontend Create a product card component with image, title, price, and add-to-cart button
/frontend Build a responsive navigation header with mobile menu
/frontend Generate a form component for user address input with validation
```

## What This Command Does

1. **Analyzes** your component requirements
2. **Generates** TypeScript React/Next.js component code
3. **Includes** proper typing, props interfaces, and exports
4. **Applies** Pandora styling conventions (CSS modules or styled-components)
5. **Adds** accessibility attributes (ARIA labels, semantic HTML)
6. **Suggests** companion test file structure

## Output Format

The agent provides:
- Complete component file with TypeScript
- Props interface definition
- Styled component or CSS module imports
- Usage example
- Suggested test cases

## Framework Support

- **Next.js 14/15** with App Router
- **React 18** with hooks
- **TypeScript** strict mode
- **CSS Modules** or **Styled Components**
- **React Testing Library** compatible

## Pandora Standards

Components follow:
- Functional components with hooks
- Proper TypeScript interfaces
- Semantic HTML structure
- WCAG 2.1 accessibility guidelines
- Mobile-first responsive design
