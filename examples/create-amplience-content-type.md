# Example Task: Create Amplience Content Type

This example demonstrates how the PG AI Squad agents collaborate to create an Amplience content type with schema, UI configuration, and example payload.

## Task Description

```
Create an Amplience content type for a Hero Banner component with:
- Title and subtitle text
- Desktop and mobile images
- CTA button
- Color theme (light/dark)
- Alignment options

Follow Pandora Amplience patterns and include example payload.
```

## Agent Workflow

### 1. Task Manager Agent

**Input**: Natural language task description

**Action**: Decomposes task into subtasks

```markdown
## Task Decomposition

### Subtask 1: Design Content Type Structure
- Agent: Amplience CMS
- Command: content-type-create
- Input: Requirements
- Output: Content type design document

### Subtask 2: Generate JSON Schema
- Agent: Amplience CMS
- Command: schema-generate
- Input: Content type design
- Output: hero-banner-schema.json

### Subtask 3: Generate Example Payload
- Agent: Amplience CMS
- Command: payload-example
- Input: JSON Schema
- Output: hero-banner-example.json, TypeScript interface

### Subtask 4: Validate Standards
- Agent: Code Review
- Command: validate-standards
- Input: Generated files
- Output: Validation report

### Subtask 5: Merge Outputs
- Agent: Task Manager
- Command: task-merge
- Input: All subtask outputs
- Output: Final deliverable
```

### 2. Amplience CMS Agent

**Subtask 1: Design Content Type Structure**

```markdown
## Content Type: Hero Banner

### Purpose
Full-width hero banner for page headers with responsive media support.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Main heading text |
| subtitle | string | No | Secondary text |
| media | desktopMobileMedia | Yes | Responsive images/video |
| cta | cta | No | Call-to-action button |
| colorTheme | enum | Yes | Text color theme |
| alignment | enum | Yes | Content alignment |

### Enums
- colorTheme: "light", "dark"
- alignment: "left", "center", "right"

### References
- Uses global-partials: desktopMobileMedia, cta
```

**Subtask 2: Generate JSON Schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schema-pandora.net/hero-banner",
  "title": "Hero Banner",
  "description": "Full-width hero banner with responsive media and CTA",
  "type": "object",
  "allOf": [
    {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/base"
    }
  ],
  "properties": {
    "title": {
      "type": "string",
      "title": "Title",
      "description": "Main heading text",
      "minLength": 1,
      "maxLength": 100
    },
    "subtitle": {
      "type": "string",
      "title": "Subtitle",
      "description": "Secondary text below title",
      "maxLength": 200
    },
    "media": {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/desktopMobileMedia",
      "title": "Media",
      "description": "Desktop and mobile images or video"
    },
    "cta": {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/cta",
      "title": "Call to Action",
      "description": "Button linking to content"
    },
    "colorTheme": {
      "type": "string",
      "title": "Color Theme",
      "description": "Text and button color scheme",
      "enum": ["light", "dark"],
      "default": "light"
    },
    "alignment": {
      "type": "string",
      "title": "Content Alignment",
      "description": "Horizontal alignment of text content",
      "enum": ["left", "center", "right"],
      "default": "center"
    }
  },
  "required": ["title", "media", "colorTheme", "alignment"],
  "propertyOrder": [
    "title",
    "subtitle",
    "media",
    "cta",
    "colorTheme",
    "alignment"
  ]
}
```

**Subtask 3: Generate Example Payload**

```json
{
  "_meta": {
    "schema": "https://schema-pandora.net/hero-banner",
    "name": "Homepage Hero Banner",
    "deliveryId": "hero-banner-homepage-001",
    "deliveryKey": "homepage-hero"
  },
  "title": "Discover the New Collection",
  "subtitle": "Explore our latest jewelry designs crafted with passion",
  "media": {
    "desktopImg": {
      "id": "img-hero-desktop-001",
      "name": "hero-homepage-desktop",
      "endpoint": "pandoragroup",
      "defaultHost": "cdn.media.amplience.net"
    },
    "mobileImg": {
      "id": "img-hero-mobile-001",
      "name": "hero-homepage-mobile",
      "endpoint": "pandoragroup",
      "defaultHost": "cdn.media.amplience.net"
    },
    "desktopMediaType": "image",
    "mobileMediaType": "image",
    "imageAltText": "Pandora jewelry collection showcase"
  },
  "cta": {
    "ctaType": "category",
    "ctaValue": "new-arrivals",
    "ctaText": "Shop Now",
    "target": "_self"
  },
  "colorTheme": "light",
  "alignment": "center"
}
```

**TypeScript Interface**

```typescript
// types/amplience/hero-banner.ts
import type { ContentMeta, DesktopMobileMedia, CTA } from './global-partials';

export interface HeroBanner {
  _meta: ContentMeta;
  title: string;
  subtitle?: string;
  media: DesktopMobileMedia;
  cta?: CTA;
  colorTheme: 'light' | 'dark';
  alignment: 'left' | 'center' | 'right';
}
```

### 3. Code Review Agent

**Subtask 4: Validate Standards**

```markdown
## Validation Report: Hero Banner Content Type

### Schema Validation
- JSON Schema Draft-07: Pass
- $id URL format: Pass
- Required fields defined: Pass
- Property order specified: Pass

### Pandora Standards
- Uses global-partials references: Pass
- Follows naming conventions: Pass
- Includes proper descriptions: Pass
- Has sensible defaults: Pass

### Amplience Compatibility
- Schema structure valid: Pass
- Content type registrable: Pass
- UI configuration compatible: Pass

### Issues Found
None

### Recommendation
Approved - Ready for registration in Amplience
```

### 4. Task Manager Agent

**Subtask 5: Merge Outputs**

```markdown
## Final Deliverable

### Files Created
1. `contents/content-type-schema/schemas/content/hero-banner-schema.json`
2. `contents/content-type-schema/hero-banner.json` (registration)
3. `contents/content-type/hero-banner.json` (UI config)
4. `examples/payloads/hero-banner-example.json`
5. `types/amplience/hero-banner.ts`

### Validation Results
- JSON Schema: Valid
- Pandora Standards: Compliant
- Amplience Compatibility: Verified

### Registration Steps
1. Upload schema to Amplience Hub
2. Register content type
3. Configure UI settings
4. Test with example payload

### Ready for Deployment
All files are ready to be deployed to Amplience.
```

## Running This Example

1. Start the Task Manager Agent
2. Provide the content type requirements
3. The Task Manager will orchestrate the Amplience CMS Agent
4. Review the generated schema and payload
5. Deploy to Amplience Hub

## Expected Output

```
contents/
├── content-type-schema/
│   ├── schemas/content/
│   │   └── hero-banner-schema.json
│   └── hero-banner.json
└── content-type/
    └── hero-banner.json

examples/payloads/
└── hero-banner-example.json

types/amplience/
└── hero-banner.ts
```
