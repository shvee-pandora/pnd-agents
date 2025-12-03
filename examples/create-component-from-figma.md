# Example Task: Create Component from Figma

This example demonstrates how the PG AI Squad agents collaborate to create a React component from a Figma design.

## Task Description

```
Create a ContactCard component from the Figma design at:
https://www.figma.com/file/xxx/Pandora-Group-Components?node-id=123

The component should:
- Display contact name, title, email, phone, and image
- Follow Pandora UI Toolkit patterns
- Be accessible (WCAG 2.1 AA)
- Include Storybook story
- Include unit tests
```

## Agent Workflow

### 1. Task Manager Agent

**Input**: Natural language task description

**Action**: Decomposes task into subtasks

```markdown
## Task Decomposition

### Subtask 1: Parse Figma Design
- Agent: Frontend Engineer
- Command: component-generate
- Input: Figma file URL
- Output: Component structure, colors, typography, spacing

### Subtask 2: Generate React Component
- Agent: Frontend Engineer
- Command: component-generate
- Input: Figma analysis
- Output: ContactCard.tsx, types.ts, index.ts

### Subtask 3: Create Storybook Story
- Agent: Frontend Engineer
- Command: story-create
- Input: Component implementation
- Output: ContactCard.stories.tsx

### Subtask 4: Generate Unit Tests
- Agent: QA
- Command: test-generate
- Input: Component implementation
- Output: ContactCard.test.tsx

### Subtask 5: Validate Accessibility
- Agent: Frontend Engineer
- Command: accessibility-validate
- Input: Component implementation
- Output: Accessibility report

### Subtask 6: Code Review
- Agent: Code Review
- Command: review-code
- Input: All generated files
- Output: Review comments, approval/rejection

### Subtask 7: Merge Outputs
- Agent: Task Manager
- Command: task-merge
- Input: All subtask outputs
- Output: Final deliverable
```

### 2. Frontend Engineer Agent

**Subtask 1: Parse Figma Design**

```typescript
// Figma analysis output
{
  component: {
    name: "ContactCard",
    type: "molecule",
    width: 280,
    height: 320
  },
  colors: {
    background: "#FFFFFF",
    text: "#1A1A1A",
    secondary: "#666666",
    accent: "#FF93A0"
  },
  typography: {
    name: { fontSize: 18, fontWeight: 500 },
    title: { fontSize: 14, fontWeight: 400 },
    contact: { fontSize: 14, fontWeight: 400 }
  },
  spacing: {
    padding: 24,
    gap: 16
  }
}
```

**Subtask 2: Generate React Component**

```typescript
// lib/components/molecules/ContactCard/ContactCard.tsx
import { cn } from '@/utils/cn';
import Image from 'next/image';
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
    <article
      className={cn('flex flex-col items-center p-6 bg-white rounded-lg', className)}
      data-testid="contact-card"
    >
      {image && (
        <Image
          src={image}
          alt={name}
          width={120}
          height={120}
          className="rounded-full mb-4"
        />
      )}
      <h3
        className="text-lg font-medium text-neutral-900"
        data-testid="contact-card-fullname"
      >
        {name}
      </h3>
      {title && (
        <p className="text-sm text-neutral-600 mt-1">{title}</p>
      )}
      <div className="flex flex-col gap-2 mt-4">
        {email && (
          <a
            href={`mailto:${email}`}
            className="text-sm text-neutral-700 hover:text-accent"
          >
            {email}
          </a>
        )}
        {phone && (
          <a
            href={`tel:${phone}`}
            className="text-sm text-neutral-700 hover:text-accent"
          >
            {phone}
          </a>
        )}
      </div>
    </article>
  );
};

ContactCard.displayName = 'ContactCard';
```

### 3. QA Agent

**Subtask 4: Generate Unit Tests**

```typescript
// lib/components/molecules/ContactCard/ContactCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ContactCard } from './ContactCard';

describe('ContactCard', () => {
  const defaultProps = {
    name: 'John Doe',
    title: 'Software Engineer',
    email: 'john@example.com',
    phone: '+1 234 567 8900',
    image: 'https://example.com/avatar.jpg',
  };

  it('renders contact name', () => {
    render(<ContactCard {...defaultProps} />);
    expect(screen.getByTestId('contact-card-fullname')).toHaveTextContent('John Doe');
  });

  it('renders email link', () => {
    render(<ContactCard {...defaultProps} />);
    const emailLink = screen.getByRole('link', { name: /john@example.com/i });
    expect(emailLink).toHaveAttribute('href', 'mailto:john@example.com');
  });

  it('renders phone link', () => {
    render(<ContactCard {...defaultProps} />);
    const phoneLink = screen.getByRole('link', { name: /\+1 234 567 8900/i });
    expect(phoneLink).toHaveAttribute('href', 'tel:+1 234 567 8900');
  });

  it('renders without optional fields', () => {
    render(<ContactCard name="John Doe" />);
    expect(screen.getByTestId('contact-card')).toBeInTheDocument();
  });
});
```

### 4. Code Review Agent

**Subtask 6: Code Review**

```markdown
## Code Review: ContactCard Component

### Summary
- **Files Reviewed**: 4
- **Issues Found**: 2 (0 Critical, 1 Warning, 1 Suggestion)
- **Recommendation**: Approve with minor changes

### Findings

#### Warning: Missing aria-label on contact links
**File**: ContactCard.tsx:28-38
```tsx
<a href={`mailto:${email}`}>
```
**Suggestion**: Add descriptive aria-label for screen readers
```tsx
<a href={`mailto:${email}`} aria-label={`Email ${name}`}>
```

#### Suggestion: Consider lazy loading image
**File**: ContactCard.tsx:15-20
**Suggestion**: Add `loading="lazy"` for below-fold usage

### Approval
Approved with suggested changes.
```

### 5. Task Manager Agent

**Subtask 7: Merge Outputs**

```markdown
## Final Deliverable

### Files Created
1. `lib/components/molecules/ContactCard/ContactCard.tsx`
2. `lib/components/molecules/ContactCard/types.ts`
3. `lib/components/molecules/ContactCard/index.ts`
4. `lib/components/molecules/ContactCard/ContactCard.stories.tsx`
5. `lib/components/molecules/ContactCard/ContactCard.test.tsx`

### Validation Results
- TypeScript: Pass
- ESLint: Pass
- Prettier: Pass
- Unit Tests: 4/4 Pass
- Accessibility: WCAG 2.1 AA Compliant

### Code Review
- Status: Approved with minor changes
- Changes Applied: Yes

### Ready for PR
All files are ready to be committed and included in a pull request.
```

## Running This Example

1. Start the Task Manager Agent
2. Provide the task description
3. The Task Manager will orchestrate the other agents
4. Review the final deliverable
5. Create a PR with the generated files

## Expected Output

```
lib/components/molecules/ContactCard/
├── ContactCard.tsx
├── ContactCard.stories.tsx
├── ContactCard.test.tsx
├── types.ts
└── index.ts
```
