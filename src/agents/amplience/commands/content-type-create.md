# Content Type Create

Create Amplience content types with JSON Schema definitions and UI configurations.

## Context

This command creates complete Amplience content type definitions including JSON Schema, UI configuration, and schema registration files following Pandora's content modeling patterns.

## Requirements

- Content type name and purpose
- Field definitions with types
- Validation rules
- UI configuration preferences

## Workflow

### 1. Design Schema Structure

Determine the content type structure:

```markdown
## Content Type Design

### Basic Information
- **Name**: {content-type-name}
- **Schema ID**: https://schema-pandora.net/{content-type-name}
- **Description**: {Purpose of this content type}

### Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Main title |
| description | string | No | Description text |
| media | $ref | No | Desktop/mobile media |
| cta | $ref | No | Call-to-action button |
```

### 2. Create JSON Schema

```json
// contents/content-type-schema/schemas/content/{content-type-name}-schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schema-pandora.net/{content-type-name}",
  "title": "{Content Type Title}",
  "description": "{Description of the content type}",
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
      "description": "The main title for this content",
      "minLength": 1,
      "maxLength": 200
    },
    "description": {
      "type": "string",
      "title": "Description",
      "description": "Optional description text",
      "format": "markdown"
    },
    "media": {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/desktopMobileMedia"
    },
    "cta": {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/cta"
    }
  },
  "required": ["title"],
  "propertyOrder": ["title", "description", "media", "cta"]
}
```

### 3. Create Schema Registration

```json
// contents/content-type-schema/{content-type-name}.json
{
  "schemaId": "https://schema-pandora.net/{content-type-name}",
  "validationLevel": "CONTENT_TYPE",
  "body": "./schemas/content/{content-type-name}-schema.json"
}
```

### 4. Create UI Configuration

```json
// contents/content-type/{content-type-name}.json
{
  "contentTypeUri": "https://schema-pandora.net/{content-type-name}",
  "settings": {
    "label": "{Human Readable Label}",
    "icons": [
      {
        "size": 256,
        "url": "https://cdn.amplience.net/icons/{icon-name}.png"
      }
    ],
    "visualizations": [
      {
        "label": "Preview",
        "templatedUri": "https://preview.pandoragroup.com/preview?contentId={{content.sys.id}}&vse={{vse.domain}}",
        "default": true
      }
    ],
    "cards": [
      {
        "label": "Card",
        "templatedUri": "https://preview.pandoragroup.com/card?contentId={{content.sys.id}}",
        "default": true
      }
    ]
  }
}
```

### 5. Generate Example Payload

```json
// Example content payload
{
  "_meta": {
    "schema": "https://schema-pandora.net/{content-type-name}",
    "name": "Example {Content Type}",
    "deliveryId": "example-123",
    "deliveryKey": "example-content"
  },
  "title": "Example Title",
  "description": "Example description text with **markdown** support.",
  "media": {
    "desktopImg": {
      "id": "abc123",
      "name": "hero-desktop",
      "endpoint": "pandoragroup",
      "defaultHost": "cdn.media.amplience.net"
    },
    "mobileImg": {
      "id": "def456",
      "name": "hero-mobile",
      "endpoint": "pandoragroup",
      "defaultHost": "cdn.media.amplience.net"
    },
    "desktopMediaType": "image",
    "mobileMediaType": "image",
    "imageAltText": "Hero banner image"
  },
  "cta": {
    "ctaType": "url",
    "ctaValue": "/about",
    "ctaText": "Learn More",
    "target": "_self"
  }
}
```

## Global Partials Reference

### Available Definitions

```json
{
  "definitions": {
    "base": {
      "description": "Base properties for all content types"
    },
    "cta": {
      "type": "object",
      "properties": {
        "ctaType": { "enum": ["url", "product", "category", "content", "search"] },
        "ctaValue": { "type": "string" },
        "ctaText": { "type": "string" },
        "target": { "enum": ["_self", "_blank"] }
      }
    },
    "desktopMobileMedia": {
      "type": "object",
      "properties": {
        "desktopImg": { "$ref": "#/definitions/diImage" },
        "mobileImg": { "$ref": "#/definitions/diImage" },
        "desktopVideo": { "type": "string" },
        "mobileVideo": { "type": "string" },
        "desktopMediaType": { "enum": ["image", "video"] },
        "mobileMediaType": { "enum": ["image", "video"] },
        "imageAltText": { "type": "string" }
      }
    },
    "diImage": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "endpoint": { "type": "string" },
        "defaultHost": { "type": "string" }
      }
    },
    "shopTheLook": {
      "type": "object",
      "properties": {
        "productIDs": { "type": "string" },
        "position": {
          "type": "object",
          "properties": {
            "x": { "type": "number" },
            "y": { "type": "number" }
          }
        },
        "color": { "type": "string" }
      }
    },
    "monetate_variations": {
      "type": "object",
      "properties": {
        "is_variation": {
          "type": "object",
          "properties": {
            "online": { "type": "boolean" },
            "searchable": { "type": "boolean" }
          }
        },
        "variations": {
          "type": "object",
          "properties": {
            "has_variations": { "type": "boolean" },
            "variation": { "type": "array" }
          }
        }
      }
    }
  }
}
```

## Example

### Input
```
Content Type: Press Release
Fields:
- title (required)
- publishDate (required)
- summary
- body (markdown)
- featuredImage
- category
- tags
```

### Output

```json
// press-release-schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schema-pandora.net/press-release",
  "title": "Press Release",
  "description": "Press release content for media and news sections",
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
      "description": "Press release headline",
      "minLength": 1,
      "maxLength": 200
    },
    "publishDate": {
      "type": "string",
      "title": "Publish Date",
      "description": "Publication date",
      "format": "date"
    },
    "summary": {
      "type": "string",
      "title": "Summary",
      "description": "Brief summary for listings",
      "maxLength": 500
    },
    "body": {
      "type": "string",
      "title": "Body",
      "description": "Full press release content",
      "format": "markdown"
    },
    "featuredImage": {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/desktopMobileMedia"
    },
    "category": {
      "type": "string",
      "title": "Category",
      "enum": ["corporate", "product", "sustainability", "financial"]
    },
    "tags": {
      "type": "array",
      "title": "Tags",
      "items": {
        "type": "string"
      }
    }
  },
  "required": ["title", "publishDate"],
  "propertyOrder": ["title", "publishDate", "summary", "body", "featuredImage", "category", "tags"]
}
```

## Validation Checklist

- [ ] Schema ID follows naming convention
- [ ] Uses global partials where applicable
- [ ] Required fields specified
- [ ] Property order defined
- [ ] Validation rules added (min/max length, format)
- [ ] UI configuration created
- [ ] Schema registration file created
- [ ] Example payload generated

## Summary

The content-type-create command generates complete Amplience content type definitions including JSON Schema, UI configuration, and registration files following Pandora's content modeling patterns.
