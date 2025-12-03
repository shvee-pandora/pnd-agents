# Payload Example

Generate example Amplience content payloads for testing and documentation.

## Context

This command generates realistic example content payloads that conform to Amplience content type schemas, useful for frontend development, testing, and documentation.

## Requirements

- Content type schema
- Realistic sample data
- All required fields populated
- Optional fields demonstrated

## Workflow

### 1. Analyze Schema

Extract from the JSON Schema:
- Required fields
- Field types and formats
- Validation constraints
- References to partials

### 2. Generate Base Structure

```json
{
  "_meta": {
    "schema": "https://schema-pandora.net/{content-type}",
    "name": "{Content Name}",
    "deliveryId": "{uuid}",
    "deliveryKey": "{delivery-key}",
    "hierarchy": {
      "parentId": "{parent-uuid}",
      "root": false
    }
  },
  // Content fields...
}
```

### 3. Populate Fields

Generate realistic values for each field type:

```json
{
  // String
  "title": "Discover the New Collection",
  
  // Markdown
  "description": "Explore our **latest designs** featuring:\n\n- Elegant rings\n- Stunning necklaces\n- Beautiful bracelets",
  
  // Date
  "publishDate": "2024-03-15",
  
  // DateTime
  "createdAt": "2024-03-15T10:30:00Z",
  
  // Number
  "price": 299.99,
  
  // Integer
  "sortOrder": 1,
  
  // Boolean
  "isActive": true,
  
  // Enum
  "status": "published",
  
  // Array of strings
  "tags": ["jewelry", "collection", "new-arrivals"],
  
  // Array of objects
  "items": [
    { "name": "Item 1", "value": 100 },
    { "name": "Item 2", "value": 200 }
  ]
}
```

### 4. Generate Media Objects

```json
{
  "media": {
    "desktopImg": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "hero-banner-desktop",
      "endpoint": "pandoragroup",
      "defaultHost": "cdn.media.amplience.net"
    },
    "mobileImg": {
      "id": "f1e2d3c4-b5a6-0987-fedc-ba0987654321",
      "name": "hero-banner-mobile",
      "endpoint": "pandoragroup",
      "defaultHost": "cdn.media.amplience.net"
    },
    "desktopMediaType": "image",
    "mobileMediaType": "image",
    "imageAltText": "Spring collection hero banner featuring new jewelry designs"
  }
}
```

### 5. Generate CTA Objects

```json
{
  "cta": {
    "ctaType": "category",
    "ctaValue": "new-arrivals",
    "ctaText": "Shop Now",
    "target": "_self"
  }
}

// Different CTA types
{
  // URL link
  "cta": {
    "ctaType": "url",
    "ctaValue": "https://www.pandora.net/about",
    "ctaText": "Learn More",
    "target": "_blank"
  }
}

{
  // Product link
  "cta": {
    "ctaType": "product",
    "ctaValue": "590702HV",
    "ctaText": "View Product",
    "target": "_self"
  }
}

{
  // Search link
  "cta": {
    "ctaType": "search",
    "ctaValue": "rings",
    "ctaText": "Search Rings",
    "target": "_self"
  }
}
```

### 6. Generate Shop The Look

```json
{
  "shopTheLook": [
    {
      "productIDs": "590702HV,590703HV,590704HV",
      "position": {
        "x": 25,
        "y": 40
      },
      "color": "#ff93a0"
    },
    {
      "productIDs": "590705HV",
      "position": {
        "x": 75,
        "y": 60
      },
      "color": "#ffffff"
    }
  ]
}
```

### 7. Generate Monetate Variations

```json
{
  "monetate_variations": {
    "is_variation": {
      "online": true,
      "searchable": true
    },
    "variations": {
      "has_variations": true,
      "variation": [
        {
          "id": "variation-a",
          "name": "Control",
          "weight": 50
        },
        {
          "id": "variation-b",
          "name": "Test",
          "weight": 50
        }
      ]
    }
  }
}
```

## Example

### Input
```
Content Type: Hero Banner
Schema: https://schema-pandora.net/hero-banner
```

### Output

```json
{
  "_meta": {
    "schema": "https://schema-pandora.net/hero-banner",
    "name": "Spring Collection Hero",
    "deliveryId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "deliveryKey": "spring-collection-hero",
    "hierarchy": {
      "parentId": "f1e2d3c4-b5a6-0987-fedc-ba0987654321",
      "root": false
    }
  },
  "title": "Discover Spring Elegance",
  "subtitle": "New arrivals that capture the essence of the season",
  "media": {
    "desktopImg": {
      "id": "img-desktop-001",
      "name": "spring-hero-desktop",
      "endpoint": "pandoragroup",
      "defaultHost": "cdn.media.amplience.net"
    },
    "mobileImg": {
      "id": "img-mobile-001",
      "name": "spring-hero-mobile",
      "endpoint": "pandoragroup",
      "defaultHost": "cdn.media.amplience.net"
    },
    "desktopMediaType": "image",
    "mobileMediaType": "image",
    "imageAltText": "Spring collection featuring floral-inspired jewelry"
  },
  "cta": {
    "ctaType": "category",
    "ctaValue": "spring-collection",
    "ctaText": "Shop the Collection",
    "target": "_self"
  },
  "colorTheme": "white",
  "alignment": "center"
}
```

### TypeScript Interface

```typescript
interface HeroBannerContent {
  _meta: {
    schema: string;
    name: string;
    deliveryId: string;
    deliveryKey?: string;
    hierarchy?: {
      parentId?: string;
      root: boolean;
    };
  };
  title: string;
  subtitle?: string;
  media?: {
    desktopImg?: AmplenceImage;
    mobileImg?: AmplenceImage;
    desktopVideo?: string;
    mobileVideo?: string;
    desktopMediaType?: 'image' | 'video';
    mobileMediaType?: 'image' | 'video';
    imageAltText?: string;
  };
  cta?: {
    ctaType: 'url' | 'product' | 'category' | 'content' | 'search';
    ctaValue: string;
    ctaText: string;
    target: '_self' | '_blank';
  };
  colorTheme?: 'white' | 'black';
  alignment?: 'left' | 'center' | 'right';
}
```

## Validation Checklist

- [ ] All required fields populated
- [ ] Values conform to schema constraints
- [ ] Realistic sample data used
- [ ] Media objects properly structured
- [ ] CTA demonstrates correct type
- [ ] _meta section complete
- [ ] TypeScript interface generated

## Summary

The payload-example command generates realistic, schema-compliant content payloads for Amplience content types, useful for frontend development, testing, and documentation.
