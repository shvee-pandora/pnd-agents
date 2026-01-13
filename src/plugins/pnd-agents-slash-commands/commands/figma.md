---
description: Extract design tokens, components, and specifications from Figma designs.
---

# /figma

Extract design information from Figma files including tokens, component specs, and implementation details.

## Usage

```
/figma [Figma URL or describe what to extract]
```

## Examples

```
/figma https://figma.com/file/abc123/Design-System
/figma Extract color tokens from the brand guidelines frame
/figma Get component specs for the product card design
```

## What This Command Does

1. **Reads** Figma file structure and frames
2. **Extracts** design tokens (colors, typography, spacing)
3. **Analyzes** component specifications
4. **Generates** CSS/SCSS variables
5. **Creates** TypeScript theme definitions
6. **Documents** responsive breakpoints

## Output Format

The agent provides:
- Design token definitions (CSS variables)
- Typography scale specifications
- Color palette with semantic naming
- Spacing and sizing tokens
- Component dimension specs
- Asset export recommendations

## Extraction Categories

- **Colors**: Primary, secondary, semantic, gradients
- **Typography**: Font families, sizes, weights, line heights
- **Spacing**: Margins, padding, gaps
- **Shadows**: Box shadows, drop shadows
- **Borders**: Radius, widths, styles
- **Breakpoints**: Responsive design points

## Output Formats

- CSS Custom Properties
- SCSS Variables
- TypeScript theme objects
- Tailwind config
- Styled-components theme

## Pandora Design Standards

- Semantic color naming
- 8px grid system
- Accessible color contrast
- Consistent component sizing
- Mobile-first breakpoints
