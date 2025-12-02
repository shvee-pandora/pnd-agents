# Schema Generate

Generate JSON Schema definitions for Amplience content types.

## Context

This command generates JSON Schema Draft-07 compliant schemas for Amplience content types, following Pandora's schema patterns and best practices.

## Requirements

- Content structure definition
- Field types and validation rules
- References to global partials
- Localization requirements

## Workflow

### 1. Analyze Content Structure

Map content requirements to JSON Schema types:

```markdown
## Type Mapping

| Content Need | JSON Schema Type | Notes |
|--------------|------------------|-------|
| Text | string | Add format for special types |
| Number | number/integer | Use integer for whole numbers |
| Boolean | boolean | True/false values |
| Date | string + format: date | ISO 8601 format |
| DateTime | string + format: date-time | ISO 8601 format |
| Markdown | string + format: markdown | Rich text support |
| Image | $ref to diImage | Amplience image reference |
| Link | $ref to cta | CTA with type routing |
| List | array | Specify items type |
| Object | object | Nested properties |
| Enum | string + enum | Fixed options |
```

### 2. Generate Schema Structure

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schema-pandora.net/{schema-name}",
  "title": "{Schema Title}",
  "description": "{Schema description}",
  "type": "object",
  
  "allOf": [
    { "$ref": "https://schema-pandora.net/global-partials#/definitions/base" }
  ],
  
  "properties": {
    // Field definitions
  },
  
  "required": [],
  "propertyOrder": [],
  
  "definitions": {
    // Local definitions if needed
  }
}
```

### 3. Define Properties

```json
{
  "properties": {
    // Simple string
    "title": {
      "type": "string",
      "title": "Title",
      "description": "The main title",
      "minLength": 1,
      "maxLength": 200
    },
    
    // String with format
    "email": {
      "type": "string",
      "title": "Email",
      "format": "email"
    },
    
    // Markdown text
    "body": {
      "type": "string",
      "title": "Body Content",
      "format": "markdown"
    },
    
    // Number with constraints
    "price": {
      "type": "number",
      "title": "Price",
      "minimum": 0,
      "multipleOf": 0.01
    },
    
    // Integer
    "quantity": {
      "type": "integer",
      "title": "Quantity",
      "minimum": 1,
      "maximum": 100
    },
    
    // Boolean
    "isActive": {
      "type": "boolean",
      "title": "Active",
      "default": true
    },
    
    // Enum
    "status": {
      "type": "string",
      "title": "Status",
      "enum": ["draft", "published", "archived"],
      "default": "draft"
    },
    
    // Date
    "publishDate": {
      "type": "string",
      "title": "Publish Date",
      "format": "date"
    },
    
    // Reference to partial
    "media": {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/desktopMobileMedia"
    },
    
    // Array of strings
    "tags": {
      "type": "array",
      "title": "Tags",
      "items": {
        "type": "string"
      },
      "minItems": 0,
      "maxItems": 10
    },
    
    // Array of objects
    "items": {
      "type": "array",
      "title": "Items",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "value": { "type": "number" }
        },
        "required": ["name"]
      }
    },
    
    // Nested object
    "settings": {
      "type": "object",
      "title": "Settings",
      "properties": {
        "theme": { "type": "string" },
        "layout": { "type": "string" }
      }
    },
    
    // Content link
    "relatedContent": {
      "allOf": [
        { "$ref": "http://bigcontent.io/cms/schema/v1/core#/definitions/content-link" },
        {
          "properties": {
            "contentType": {
              "enum": ["https://schema-pandora.net/article"]
            }
          }
        }
      ]
    }
  }
}
```

### 4. Add Validation Rules

```json
{
  "properties": {
    "url": {
      "type": "string",
      "pattern": "^https?://.*$"
    },
    "phone": {
      "type": "string",
      "pattern": "^\\+?[0-9\\s-]+$"
    },
    "slug": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$"
    }
  }
}
```

### 5. Define Conditional Logic

```json
{
  "if": {
    "properties": {
      "mediaType": { "const": "video" }
    }
  },
  "then": {
    "required": ["videoUrl"]
  },
  "else": {
    "required": ["image"]
  }
}
```

## Example

### Input
```
Schema: Hero Banner
Fields:
- title (required, max 100 chars)
- subtitle (optional)
- media (desktop/mobile images or video)
- cta (optional call-to-action)
- colorTheme (white or black)
- alignment (left, center, right)
```

### Output

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
      "description": "Main headline text",
      "minLength": 1,
      "maxLength": 100
    },
    "subtitle": {
      "type": "string",
      "title": "Subtitle",
      "description": "Optional supporting text",
      "maxLength": 200
    },
    "media": {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/desktopMobileMedia"
    },
    "cta": {
      "$ref": "https://schema-pandora.net/global-partials#/definitions/cta"
    },
    "colorTheme": {
      "type": "string",
      "title": "Color Theme",
      "description": "Text and button color scheme",
      "enum": ["white", "black"],
      "default": "white"
    },
    "alignment": {
      "type": "string",
      "title": "Content Alignment",
      "description": "Horizontal alignment of text content",
      "enum": ["left", "center", "right"],
      "default": "center"
    }
  },
  "required": ["title"],
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

## Validation Checklist

- [ ] Valid JSON Schema Draft-07
- [ ] Schema ID follows convention
- [ ] All properties have titles and descriptions
- [ ] Required fields specified
- [ ] Validation rules appropriate
- [ ] References to partials correct
- [ ] Property order defined
- [ ] Default values set where appropriate

## Summary

The schema-generate command creates JSON Schema Draft-07 compliant definitions for Amplience content types with proper validation, references, and documentation.
