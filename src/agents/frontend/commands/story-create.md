# Story Create

Create Storybook stories for React components with comprehensive documentation.

## Context

This command generates Storybook stories that document component usage, variants, and interactive controls following Pandora's documentation standards.

## Requirements

- Component to document
- All props and their types
- Visual variants to showcase
- Usage examples

## Workflow

### 1. Analyze Component

Review the component to identify:
- All props and their types
- Visual variants and states
- Interactive behaviors
- Edge cases to document

### 2. Generate Story File

```typescript
// {ComponentName}.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { {ComponentName} } from './{ComponentName}';

const meta: Meta<typeof {ComponentName}> = {
  title: '{Level}/{ComponentName}',
  component: {ComponentName},
  tags: ['autodocs'],
  parameters: {
    layout: 'centered', // or 'fullscreen', 'padded'
    docs: {
      description: {
        component: '{Component description for documentation}',
      },
    },
  },
  argTypes: {
    prop1: {
      control: 'text',
      description: 'Description of prop1',
      table: {
        type: { summary: 'string' },
        defaultValue: { summary: 'undefined' },
      },
    },
    prop2: {
      control: 'select',
      options: ['option1', 'option2', 'option3'],
      description: 'Description of prop2',
    },
    onClick: {
      action: 'clicked',
      description: 'Click handler',
    },
  },
};

export default meta;
type Story = StoryObj<typeof {ComponentName}>;

// Default story
export const Default: Story = {
  args: {
    prop1: 'Default value',
  },
};

// Variant stories
export const Variant1: Story = {
  args: {
    prop1: 'Variant 1 value',
    prop2: 'option1',
  },
};

export const Variant2: Story = {
  args: {
    prop1: 'Variant 2 value',
    prop2: 'option2',
  },
};

// Interactive story
export const Interactive: Story = {
  args: {
    prop1: 'Interactive',
  },
  play: async ({ canvasElement }) => {
    // Add interaction tests here
  },
};

// Responsive story
export const Responsive: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
  },
  args: {
    prop1: 'Mobile view',
  },
};
```

### 3. Add Control Types

```typescript
// Common control types
argTypes: {
  // Text input
  text: { control: 'text' },
  
  // Number input
  number: { control: 'number' },
  
  // Boolean toggle
  boolean: { control: 'boolean' },
  
  // Select dropdown
  select: { 
    control: 'select',
    options: ['a', 'b', 'c'],
  },
  
  // Radio buttons
  radio: {
    control: 'radio',
    options: ['a', 'b', 'c'],
  },
  
  // Color picker
  color: { control: 'color' },
  
  // Date picker
  date: { control: 'date' },
  
  // Object editor
  object: { control: 'object' },
  
  // Array editor
  array: { control: 'array' },
  
  // Action logger
  onClick: { action: 'clicked' },
}
```

### 4. Document Variants

Create stories for each visual variant:

```typescript
// States
export const Default: Story = { args: { state: 'default' } };
export const Hover: Story = { args: { state: 'hover' } };
export const Focus: Story = { args: { state: 'focus' } };
export const Disabled: Story = { args: { disabled: true } };
export const Error: Story = { args: { error: 'Error message' } };

// Sizes
export const Small: Story = { args: { size: 'small' } };
export const Medium: Story = { args: { size: 'medium' } };
export const Large: Story = { args: { size: 'large' } };

// Themes
export const Light: Story = { args: { theme: 'light' } };
export const Dark: Story = { args: { theme: 'dark' } };
```

### 5. Add Accessibility Testing

```typescript
import { within, userEvent } from '@storybook/testing-library';
import { expect } from '@storybook/jest';

export const AccessibilityTest: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    
    // Test keyboard navigation
    const button = canvas.getByRole('button');
    await userEvent.tab();
    expect(button).toHaveFocus();
    
    // Test ARIA attributes
    expect(button).toHaveAttribute('aria-label');
  },
};
```

## Example

### Input
```
Component: ContactCard
Props: name, title, email, phone, image
Variants: Default, WithImage, WithoutImage, Loading
```

### Output

```typescript
// ContactCard.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { ContactCard } from './ContactCard';

const meta: Meta<typeof ContactCard> = {
  title: 'Molecules/ContactCard',
  component: ContactCard,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Displays contact information with optional profile image.',
      },
    },
  },
  argTypes: {
    name: {
      control: 'text',
      description: 'Full name of the contact',
    },
    title: {
      control: 'text',
      description: 'Job title or role',
    },
    email: {
      control: 'text',
      description: 'Email address',
    },
    phone: {
      control: 'text',
      description: 'Phone number',
    },
    image: {
      control: 'text',
      description: 'Profile image URL',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ContactCard>;

export const Default: Story = {
  args: {
    name: 'John Doe',
    title: 'Software Engineer',
    email: 'john.doe@pandora.net',
    phone: '+1 234 567 8900',
  },
};

export const WithImage: Story = {
  args: {
    ...Default.args,
    image: 'https://via.placeholder.com/150',
  },
};

export const WithoutImage: Story = {
  args: {
    name: 'Jane Smith',
    title: 'Product Manager',
    email: 'jane.smith@pandora.net',
  },
};

export const MinimalInfo: Story = {
  args: {
    name: 'Bob Wilson',
  },
};

export const Mobile: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
  },
  args: {
    ...WithImage.args,
  },
};
```

## Validation Checklist

- [ ] Meta configuration complete
- [ ] All props documented in argTypes
- [ ] Default story present
- [ ] All variants covered
- [ ] Responsive stories included
- [ ] Accessibility tests added
- [ ] autodocs tag included

## Summary

The story-create command generates comprehensive Storybook documentation for React components, including all variants, controls, and accessibility tests.
