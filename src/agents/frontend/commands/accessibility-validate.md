# Accessibility Validate

Validate React components for WCAG 2.1 AA accessibility compliance.

## Context

This command performs comprehensive accessibility validation on React components, checking for WCAG 2.1 AA compliance and providing actionable remediation guidance.

## Requirements

- Component to validate
- Component rendered output (HTML)
- Interactive behavior documentation

## Workflow

### 1. Semantic HTML Check

Verify proper use of semantic elements:

```markdown
## Semantic HTML Checklist

### Headings
- [ ] Heading hierarchy is logical (h1 → h2 → h3)
- [ ] No skipped heading levels
- [ ] Only one h1 per page/section

### Landmarks
- [ ] Main content in <main>
- [ ] Navigation in <nav>
- [ ] Footer in <footer>
- [ ] Sections have appropriate roles

### Interactive Elements
- [ ] Buttons use <button> not <div>
- [ ] Links use <a> with href
- [ ] Form inputs have associated labels
- [ ] Lists use <ul>/<ol>/<dl>
```

### 2. ARIA Validation

Check ARIA attribute usage:

```markdown
## ARIA Checklist

### Required Attributes
- [ ] aria-label for icon-only buttons
- [ ] aria-expanded for collapsible content
- [ ] aria-selected for tabs/options
- [ ] aria-describedby for form errors
- [ ] aria-live for dynamic content

### Forbidden Patterns
- [ ] No aria-label on non-interactive elements
- [ ] No redundant roles (button role on <button>)
- [ ] No aria-hidden on focusable elements
- [ ] No conflicting ARIA attributes
```

### 3. Keyboard Navigation

Test keyboard accessibility:

```markdown
## Keyboard Checklist

### Focus Management
- [ ] All interactive elements focusable
- [ ] Logical tab order
- [ ] No keyboard traps
- [ ] Focus visible on all elements

### Key Bindings
- [ ] Enter/Space activates buttons
- [ ] Escape closes modals/drawers
- [ ] Arrow keys navigate within components
- [ ] Tab moves between components

### Focus Indicators
- [ ] Visible focus ring (min 2px)
- [ ] Sufficient contrast (3:1 ratio)
- [ ] Not relying solely on color
```

### 4. Color and Contrast

Validate visual accessibility:

```markdown
## Visual Checklist

### Color Contrast
- [ ] Text contrast >= 4.5:1 (normal text)
- [ ] Text contrast >= 3:1 (large text, 18px+)
- [ ] UI component contrast >= 3:1
- [ ] Focus indicator contrast >= 3:1

### Color Independence
- [ ] Information not conveyed by color alone
- [ ] Error states have text/icon indicators
- [ ] Links distinguishable without color

### Motion
- [ ] Respects prefers-reduced-motion
- [ ] No auto-playing animations > 5s
- [ ] Pause/stop controls for animations
```

### 5. Screen Reader Testing

Verify screen reader compatibility:

```markdown
## Screen Reader Checklist

### Content
- [ ] All images have alt text
- [ ] Decorative images have alt=""
- [ ] Complex images have long descriptions
- [ ] Icons have accessible names

### Forms
- [ ] Labels associated with inputs
- [ ] Error messages announced
- [ ] Required fields indicated
- [ ] Instructions provided

### Dynamic Content
- [ ] Live regions for updates
- [ ] Focus moves appropriately
- [ ] Loading states announced
```

## Validation Report Template

```markdown
# Accessibility Validation Report

## Component: {ComponentName}
**Date**: {Date}
**WCAG Level**: AA
**Status**: {Pass/Fail}

## Summary
- Critical Issues: {count}
- Warnings: {count}
- Passed Checks: {count}

## Critical Issues

### Issue 1: {Title}
**WCAG Criterion**: {X.X.X - Name}
**Impact**: {High/Medium/Low}
**Element**: `{selector}`

**Problem**:
{Description of the issue}

**Current Code**:
```html
{Current problematic code}
```

**Recommended Fix**:
```html
{Fixed code}
```

## Warnings

### Warning 1: {Title}
**WCAG Criterion**: {X.X.X - Name}
**Recommendation**: {Suggestion}

## Passed Checks
- [x] {Check 1}
- [x] {Check 2}
- [x] {Check 3}
```

## Common Issues and Fixes

### Missing Alt Text
```tsx
// Bad
<img src="hero.jpg" />

// Good
<img src="hero.jpg" alt="Pandora jewelry collection display" />

// Decorative
<img src="decoration.svg" alt="" role="presentation" />
```

### Missing Button Label
```tsx
// Bad
<button><Icon name="close" /></button>

// Good
<button aria-label="Close dialog">
  <Icon name="close" aria-hidden="true" />
</button>
```

### Missing Form Labels
```tsx
// Bad
<input type="email" placeholder="Email" />

// Good
<label htmlFor="email">Email</label>
<input id="email" type="email" placeholder="john@example.com" />

// Or with aria-label
<input type="email" aria-label="Email address" placeholder="Email" />
```

### Focus Management
```tsx
// Bad - no focus management
const Modal = ({ isOpen }) => {
  if (!isOpen) return null;
  return <div>...</div>;
};

// Good - focus trapped and managed
const Modal = ({ isOpen, onClose }) => {
  const closeRef = useRef<HTMLButtonElement>(null);
  
  useEffect(() => {
    if (isOpen) {
      closeRef.current?.focus();
    }
  }, [isOpen]);
  
  return (
    <FocusTrap>
      <div role="dialog" aria-modal="true">
        <button ref={closeRef} onClick={onClose}>Close</button>
        ...
      </div>
    </FocusTrap>
  );
};
```

### Color Contrast
```css
/* Bad - insufficient contrast */
.text {
  color: #999; /* 2.85:1 on white */
}

/* Good - sufficient contrast */
.text {
  color: #767676; /* 4.54:1 on white */
}
```

### Reduced Motion
```css
/* Respect user preference */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Testing Tools

### Automated
- axe-core / @axe-core/react
- eslint-plugin-jsx-a11y
- Storybook a11y addon

### Manual
- Keyboard-only navigation
- Screen reader testing (VoiceOver, NVDA)
- Color contrast analyzers
- Browser DevTools accessibility panel

## Summary

The accessibility-validate command performs comprehensive WCAG 2.1 AA validation, identifying issues and providing specific remediation guidance for React components.
