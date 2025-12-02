# Component Generate

Generate React/Next.js components following Pandora UI Toolkit patterns.

## Context

This command creates production-ready React components from Figma designs or specifications, following Pandora's atomic design patterns and coding standards.

## Requirements

- Component name and type (atom/molecule/organism)
- Figma design reference or specifications
- Props interface definition
- Responsive requirements

## Workflow

### 1. Analyze Requirements

Extract from Figma or specifications:
- Component structure and hierarchy
- Visual variants and states
- Responsive breakpoints
- Interactive behaviors
- Accessibility requirements

### 2. Determine Atomic Level

```markdown
## Atomic Classification

| Level | Criteria | Examples |
|-------|----------|----------|
| Atom | Single-purpose, no children | Input, Button, Link, Icon |
| Molecule | Combines atoms, simple logic | FieldContainer, NavMenu |
| Organism | Complex, multiple molecules | PageCover, Contacts, Drawer |
| Template | Page-level layout | PageLayout, ContentLayout |
```

### 3. Generate Component Structure

```bash
# Create component directory
mkdir -p lib/components/{level}/{ComponentName}

# Create files
touch lib/components/{level}/{ComponentName}/{ComponentName}.tsx
touch lib/components/{level}/{ComponentName}/types.ts
touch lib/components/{level}/{ComponentName}/index.ts
touch lib/components/{level}/{ComponentName}/{ComponentName}.stories.tsx
touch lib/components/{level}/{ComponentName}/{ComponentName}.test.tsx
```

### 4. Implement Component

```typescript
// {ComponentName}.tsx
'use client'; // Only if client-side interactivity needed

import React from 'react';
import { cn } from '@/utils/cn';
import type { {ComponentName}Props } from './types';

/**
 * {ComponentName} - {Brief description}
 * 
 * @example
 * <{ComponentName} prop1="value" />
 */
export const {ComponentName}: React.FC<{ComponentName}Props> = ({
  prop1,
  prop2,
  className,
  children,
  ...rest
}) => {
  // Hooks
  
  // Event handlers
  
  // Render
  return (
    <div 
      className={cn('base-styles', className)}
      data-testid="{component-name}"
      {...rest}
    >
      {children}
    </div>
  );
};

{ComponentName}.displayName = '{ComponentName}';
```

### 5. Define Types

```typescript
// types.ts
export interface {ComponentName}Props {
  /** Description of prop1 */
  prop1: string;
  /** Description of prop2 (optional) */
  prop2?: number;
  /** Additional CSS classes */
  className?: string;
  /** Child elements */
  children?: React.ReactNode;
}
```

### 6. Create Index Export

```typescript
// index.ts
export { {ComponentName} } from './{ComponentName}';
export type { {ComponentName}Props } from './types';
```

### 7. Update Parent Index

```typescript
// lib/components/{level}/index.ts
export * from './{ComponentName}';
```

## Example

### Input
```
Component: ContactCard
Type: Molecule
Props: name, title, email, phone, image
Responsive: Stack on mobile, inline on desktop
```

### Output

```typescript
// ContactCard.tsx
import React from 'react';
import { cn } from '@/utils/cn';
import { Link } from '@/atoms/Link';
import type { ContactCardProps } from './types';

export const ContactCard: React.FC<ContactCardProps> = ({
  name,
  title,
  email,
  phone,
  image,
  className,
}) => {
  return (
    <div 
      className={cn(
        'flex flex-col md:flex-row gap-4 p-4',
        className
      )}
      data-testid="contact-card"
    >
      {image && (
        <img 
          src={image} 
          alt={name}
          className="w-16 h-16 rounded-full object-cover"
        />
      )}
      <div className="flex flex-col gap-1">
        <h3 
          className="text-lg font-medium"
          data-testid="contact-card-fullname"
        >
          {name}
        </h3>
        {title && (
          <p className="text-sm text-neutral-600">{title}</p>
        )}
        {email && (
          <Link href={`mailto:${email}`} className="text-sm">
            {email}
          </Link>
        )}
        {phone && (
          <Link href={`tel:${phone}`} className="text-sm">
            {phone}
          </Link>
        )}
      </div>
    </div>
  );
};

ContactCard.displayName = 'ContactCard';
```

```typescript
// types.ts
export interface ContactCardProps {
  /** Full name of the contact */
  name: string;
  /** Job title or role */
  title?: string;
  /** Email address */
  email?: string;
  /** Phone number */
  phone?: string;
  /** Profile image URL */
  image?: string;
  /** Additional CSS classes */
  className?: string;
}
```

## Validation Checklist

- [ ] Component follows atomic design level
- [ ] TypeScript strict mode compliant
- [ ] Props properly typed with JSDoc
- [ ] Responsive design implemented
- [ ] Accessibility attributes added
- [ ] Test IDs for testing
- [ ] Display name set
- [ ] Index exports created

## Summary

The component-generate command creates production-ready React components following Pandora's atomic design patterns, TypeScript standards, and accessibility requirements.
