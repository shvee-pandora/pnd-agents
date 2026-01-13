# Pandora Coding Standards

This skill defines the coding standards and best practices that all PND Agents enforce.

## TypeScript Standards

### Strict Mode
All TypeScript code must use strict mode with these compiler options:
- `strict: true`
- `noImplicitAny: true`
- `strictNullChecks: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`

### Type Definitions
- Use explicit types for function parameters and return values
- Prefer interfaces over type aliases for object shapes
- Use generics for reusable type-safe code
- Never use `any` - use `unknown` if type is truly unknown

## React/Next.js Standards

### Component Structure
```typescript
// 1. Imports (external, then internal)
import React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui';
import styles from './Component.module.css';

// 2. Types/Interfaces
interface ComponentProps {
  title: string;
  onAction?: () => void;
}

// 3. Component
export const Component: React.FC<ComponentProps> = ({ title, onAction }) => {
  // 3a. Hooks
  const router = useRouter();
  const [state, setState] = useState(false);

  // 3b. Handlers
  const handleClick = useCallback(() => {
    onAction?.();
  }, [onAction]);

  // 3c. Render
  return (
    <div className={styles.container}>
      <h1>{title}</h1>
      <Button onClick={handleClick}>Action</Button>
    </div>
  );
};
```

### Naming Conventions
- Components: PascalCase (`ProductCard.tsx`)
- Hooks: camelCase with `use` prefix (`useCart.ts`)
- Utilities: camelCase (`formatPrice.ts`)
- Constants: SCREAMING_SNAKE_CASE (`MAX_ITEMS`)
- CSS Modules: camelCase (`styles.container`)

## Testing Standards

### Coverage Requirements
- Minimum 80% code coverage for new code
- 100% coverage for critical paths (checkout, auth)

### Test Structure
- Use AAA pattern (Arrange, Act, Assert)
- Descriptive test names that explain behavior
- One assertion per test when possible
- Use React Testing Library queries by accessibility

## Accessibility Standards

### WCAG 2.1 AA Compliance
- All interactive elements keyboard accessible
- Color contrast ratio minimum 4.5:1
- All images have meaningful alt text
- Form inputs have associated labels
- Focus indicators visible

### Semantic HTML
- Use appropriate heading hierarchy
- Use landmark elements (main, nav, aside)
- Use button for actions, anchor for navigation

## Code Quality

### Error Handling
- Always handle errors explicitly
- Use try/catch for async operations
- Provide meaningful error messages
- Log errors with context

### Performance
- Memoize expensive calculations
- Use dynamic imports for code splitting
- Optimize images (WebP, lazy loading)
- Avoid unnecessary re-renders
