---
name: figma-read
description: Read a Figma design and extract component metadata, design tokens, variants, and assets. Accepts a Figma file URL, node URL, or file key with optional node ID.
---

# figma-read

Read Figma designs and extract component metadata for the Frontend Engineer Agent.

## Usage

```
figma-read <figma_url_or_file_key> [node_id]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `figma_url_or_file_key` | Yes | Figma file URL, node URL, or file key |
| `node_id` | No | Specific node ID to read (if not in URL) |

## Examples

### Read from Figma URL

```
figma-read "https://www.figma.com/file/ABC123/Design-System"
```

### Read specific node from URL

```
figma-read "https://www.figma.com/file/ABC123/Design-System?node-id=123-456"
```

### Read using file key and node ID

```
figma-read ABC123 123:456
```

## Output

Returns JSON with component metadata:

```json
{
  "componentName": "HeroBanner",
  "figmaId": "123:456",
  "figmaName": "Hero Banner",
  "description": "Main hero section",
  "props": {
    "heading": "string",
    "subheading": "string",
    "image": "asset",
    "ctaText": "string"
  },
  "designTokens": {
    "colors": {
      "fill0": "#000000"
    },
    "spacing": [8, 16, 24],
    "textStyles": {
      "heading": {
        "fontFamily": "Inter",
        "fontSize": 48,
        "fontWeight": 700
      }
    },
    "borderRadius": {
      "default": 8
    }
  },
  "assets": [
    {
      "nodeId": "789:012",
      "name": "heroIcon",
      "format": "SVG",
      "scale": 1.0
    }
  ],
  "variants": [
    {
      "name": "Size=Large",
      "properties": {
        "Size": "Large"
      }
    }
  ],
  "autoLayout": {
    "mode": "VERTICAL",
    "padding": {
      "top": 24,
      "right": 24,
      "bottom": 24,
      "left": 24
    },
    "itemSpacing": 16
  },
  "dimensions": {
    "width": 1200,
    "height": 600
  },
  "notes": "Auto layout -> Use Flex column. 16px gap."
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FIGMA_ACCESS_TOKEN` | Yes | Figma API personal access token |

## Workflow Integration

This command is typically called by the Task Manager Agent when processing tasks that contain Figma URLs. The output is then passed to the Frontend Engineer Agent for component generation.

```
Task Manager -> figma-read -> Frontend Engineer -> Code Review -> QA
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Figma access token is required" | Missing FIGMA_ACCESS_TOKEN | Set the environment variable |
| "Invalid Figma URL" | URL doesn't match expected format | Use format: figma.com/file/KEY/Name |
| "Node not found" | Node ID doesn't exist in file | Check node ID in Figma URL |
| "Rate limit exceeded" | Too many API requests | Wait and retry |

## Related Commands

- `component-generate`: Generate React component from Figma metadata
- `story-create`: Create Storybook story from component
- `task-decompose`: Break down Figma-to-component tasks
