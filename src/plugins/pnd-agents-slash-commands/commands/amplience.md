---
description: Create Amplience CMS content types and schemas for headless content management.
---

# /amplience

Generate Amplience Dynamic Content schemas, content types, and visualization templates.

## Usage

```
/amplience [content type description]
```

## Examples

```
/amplience Create a hero banner content type with image, headline, CTA button
/amplience Build a product carousel schema with configurable item count
/amplience Generate a promotional tile content type for homepage
```

## What This Command Does

1. **Analyzes** your content requirements
2. **Generates** Amplience JSON schema definition
3. **Creates** content type registration code
4. **Includes** validation rules and constraints
5. **Provides** visualization template structure
6. **Suggests** delivery API query patterns

## Output Format

The agent provides:
- JSON Schema for the content type
- Content type registration configuration
- Field definitions with validation
- Localization setup
- Example content payload
- React component integration snippet

## Amplience Features Supported

- **Content Types** with nested properties
- **Content Links** for relationships
- **Enums** for controlled vocabularies
- **Localization** for multi-language content
- **Slots** for page composition
- **Visualizations** for preview

## Pandora CMS Standards

Content types follow:
- Consistent naming conventions
- Reusable component patterns
- SEO-friendly field structures
- Image optimization settings
- Delivery key conventions
