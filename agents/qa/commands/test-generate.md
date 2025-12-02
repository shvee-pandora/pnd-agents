# Test Generate

Generate comprehensive tests for React components and services.

## Context

This command generates unit tests, integration tests, and E2E tests following Pandora's testing patterns and best practices.

## Requirements

- Component or service to test
- Test type (unit/integration/E2E)
- Coverage requirements

## Workflow

### 1. Analyze Test Subject

Identify what needs to be tested:
- Component props and behavior
- User interactions
- Edge cases
- Error states
- Accessibility

### 2. Generate Unit Tests

```typescript
// {ComponentName}.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { {ComponentName} } from './{ComponentName}';

describe('{ComponentName}', () => {
  const defaultProps = {
    // Default test props
  };

  const renderComponent = (props = {}) => {
    return render(<{ComponentName} {...defaultProps} {...props} />);
  };

  describe('rendering', () => {
    it('renders with default props', () => {
      renderComponent();
      expect(screen.getByTestId('{component-name}')).toBeInTheDocument();
    });

    it('renders children correctly', () => {
      renderComponent({ children: 'Test content' });
      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      renderComponent({ className: 'custom-class' });
      expect(screen.getByTestId('{component-name}')).toHaveClass('custom-class');
    });
  });

  describe('interactions', () => {
    it('calls onClick when clicked', async () => {
      const onClick = jest.fn();
      renderComponent({ onClick });
      
      await userEvent.click(screen.getByRole('button'));
      
      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('handles keyboard events', async () => {
      const onKeyDown = jest.fn();
      renderComponent({ onKeyDown });
      
      const element = screen.getByTestId('{component-name}');
      fireEvent.keyDown(element, { key: 'Enter' });
      
      expect(onKeyDown).toHaveBeenCalled();
    });
  });

  describe('states', () => {
    it('renders disabled state', () => {
      renderComponent({ disabled: true });
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('renders loading state', () => {
      renderComponent({ isLoading: true });
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('renders error state', () => {
      renderComponent({ error: 'Error message' });
      expect(screen.getByText('Error message')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has correct ARIA attributes', () => {
      renderComponent({ ariaLabel: 'Test label' });
      expect(screen.getByLabelText('Test label')).toBeInTheDocument();
    });

    it('is keyboard accessible', () => {
      renderComponent();
      const element = screen.getByTestId('{component-name}');
      element.focus();
      expect(element).toHaveFocus();
    });
  });

  describe('edge cases', () => {
    it('handles empty props gracefully', () => {
      renderComponent({});
      expect(screen.getByTestId('{component-name}')).toBeInTheDocument();
    });

    it('handles null values', () => {
      renderComponent({ value: null });
      expect(screen.getByTestId('{component-name}')).toBeInTheDocument();
    });

    it('handles undefined values', () => {
      renderComponent({ value: undefined });
      expect(screen.getByTestId('{component-name}')).toBeInTheDocument();
    });
  });
});
```

### 3. Generate Hook Tests

```typescript
// use{HookName}.test.ts
import { renderHook, act } from '@testing-library/react';
import { use{HookName} } from './use{HookName}';

describe('use{HookName}', () => {
  it('returns initial state', () => {
    const { result } = renderHook(() => use{HookName}());
    
    expect(result.current.value).toBe(initialValue);
    expect(result.current.isLoading).toBe(false);
  });

  it('updates state on action', () => {
    const { result } = renderHook(() => use{HookName}());
    
    act(() => {
      result.current.setValue('new value');
    });
    
    expect(result.current.value).toBe('new value');
  });

  it('handles async operations', async () => {
    const { result } = renderHook(() => use{HookName}());
    
    await act(async () => {
      await result.current.fetchData();
    });
    
    expect(result.current.data).toBeDefined();
    expect(result.current.isLoading).toBe(false);
  });

  it('handles errors', async () => {
    const { result } = renderHook(() => use{HookName}());
    
    await act(async () => {
      await result.current.fetchData('invalid');
    });
    
    expect(result.current.error).toBeDefined();
  });

  it('cleans up on unmount', () => {
    const { unmount } = renderHook(() => use{HookName}());
    
    unmount();
    
    // Verify cleanup occurred (no memory leaks, subscriptions cancelled)
  });
});
```

### 4. Generate Service Tests

```typescript
// {serviceName}.test.ts
import { {functionName} } from './{serviceName}';

// Mock fetch
global.fetch = jest.fn();

describe('{serviceName}', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('{functionName}', () => {
    it('fetches data successfully', async () => {
      const mockData = { id: '123', title: 'Test' };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ content: mockData })
      });

      const result = await {functionName}('123');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/content/id/123'),
        expect.any(Object)
      );
      expect(result).toEqual(mockData);
    });

    it('handles 404 responses', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404
      });

      const result = await {functionName}('invalid-id');

      expect(result).toBeNull();
    });

    it('handles network errors', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect({functionName}('123')).rejects.toThrow('Network error');
    });

    it('handles timeout', async () => {
      (fetch as jest.Mock).mockImplementationOnce(
        () => new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 100)
        )
      );

      await expect({functionName}('123')).rejects.toThrow('Timeout');
    });
  });
});
```

### 5. Generate E2E Tests

```typescript
// {feature}.spec.ts
import { test, expect } from '@playwright/test';

test.describe('{Feature Name}', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/{page-path}');
  });

  test('displays correctly', async ({ page }) => {
    await expect(page.getByTestId('{element}')).toBeVisible();
    await expect(page.getByRole('heading')).toContainText('{expected text}');
  });

  test('handles user interaction', async ({ page }) => {
    await page.getByRole('button', { name: '{button name}' }).click();
    await expect(page.getByTestId('{result element}')).toBeVisible();
  });

  test('submits form successfully', async ({ page }) => {
    await page.getByLabel('{field label}').fill('{value}');
    await page.getByRole('button', { name: 'Submit' }).click();
    
    await expect(page.getByText('{success message}')).toBeVisible();
  });

  test('handles errors gracefully', async ({ page }) => {
    // Trigger error condition
    await page.getByRole('button', { name: 'Submit' }).click();
    
    await expect(page.getByText('{error message}')).toBeVisible();
  });

  test('is accessible', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('works on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await expect(page.getByTestId('{mobile element}')).toBeVisible();
  });
});
```

## Test Patterns

### Testing Async Components
```typescript
it('loads data asynchronously', async () => {
  renderComponent();
  
  // Wait for loading to complete
  await waitFor(() => {
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
  });
  
  // Verify data is displayed
  expect(screen.getByText('Loaded data')).toBeInTheDocument();
});
```

### Testing Form Validation
```typescript
it('shows validation errors', async () => {
  renderComponent();
  
  // Submit without filling required fields
  await userEvent.click(screen.getByRole('button', { name: 'Submit' }));
  
  // Check for error messages
  expect(screen.getByText('Name is required')).toBeInTheDocument();
  expect(screen.getByText('Email is required')).toBeInTheDocument();
});
```

### Testing Context Providers
```typescript
const wrapper = ({ children }) => (
  <ThemeProvider theme="dark">
    <UserProvider user={mockUser}>
      {children}
    </UserProvider>
  </ThemeProvider>
);

it('uses context values', () => {
  render(<Component />, { wrapper });
  expect(screen.getByTestId('theme')).toHaveTextContent('dark');
});
```

## Example

### Input
```
Component: ContactCard
Props: name, title, email, phone, image
Interactions: Click email/phone links
```

### Output
```typescript
// ContactCard.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContactCard } from './ContactCard';

describe('ContactCard', () => {
  const defaultProps = {
    name: 'John Doe',
    title: 'Software Engineer',
    email: 'john@example.com',
    phone: '+1 234 567 8900',
    image: 'https://example.com/avatar.jpg'
  };

  const renderComponent = (props = {}) => {
    return render(<ContactCard {...defaultProps} {...props} />);
  };

  describe('rendering', () => {
    it('renders contact name', () => {
      renderComponent();
      expect(screen.getByTestId('contact-card-fullname')).toHaveTextContent('John Doe');
    });

    it('renders contact title', () => {
      renderComponent();
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });

    it('renders email link', () => {
      renderComponent();
      const emailLink = screen.getByRole('link', { name: /john@example.com/i });
      expect(emailLink).toHaveAttribute('href', 'mailto:john@example.com');
    });

    it('renders phone link', () => {
      renderComponent();
      const phoneLink = screen.getByRole('link', { name: /\+1 234 567 8900/i });
      expect(phoneLink).toHaveAttribute('href', 'tel:+1 234 567 8900');
    });

    it('renders profile image', () => {
      renderComponent();
      const image = screen.getByRole('img');
      expect(image).toHaveAttribute('src', 'https://example.com/avatar.jpg');
      expect(image).toHaveAttribute('alt', 'John Doe');
    });
  });

  describe('optional fields', () => {
    it('renders without title', () => {
      renderComponent({ title: undefined });
      expect(screen.getByTestId('contact-card-fullname')).toBeInTheDocument();
      expect(screen.queryByText('Software Engineer')).not.toBeInTheDocument();
    });

    it('renders without email', () => {
      renderComponent({ email: undefined });
      expect(screen.queryByRole('link', { name: /mailto:/i })).not.toBeInTheDocument();
    });

    it('renders without image', () => {
      renderComponent({ image: undefined });
      expect(screen.queryByRole('img')).not.toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has accessible name', () => {
      renderComponent();
      expect(screen.getByTestId('contact-card')).toBeInTheDocument();
    });

    it('links are keyboard accessible', async () => {
      renderComponent();
      const emailLink = screen.getByRole('link', { name: /john@example.com/i });
      
      emailLink.focus();
      expect(emailLink).toHaveFocus();
    });
  });
});
```

## Summary

The test-generate command creates comprehensive tests for React components and services, covering rendering, interactions, states, accessibility, and edge cases.
