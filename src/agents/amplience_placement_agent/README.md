# Amplience Placement Agent

A Human-in-the-Loop AI Agent that assists engineers and content editors in placing existing Amplience modules into the correct page sections based on Figma designs.

## Overview

The Amplience Placement Agent is designed to bridge the gap between design (Figma) and content management (Amplience CMS). It analyzes Figma page structures, discovers available Amplience content types, and generates placement recommendations with confidence scores.

**This agent is NOT autonomous.** It requires explicit human approval before any write operations.

## What This Agent Does

The agent provides five core capabilities:

1. **Figma Analysis**: Extracts page structure, sections, components, and hierarchy from Figma designs
2. **Amplience Discovery**: Catalogs available Pandora content types and slots from the CMS
3. **Mapping Recommendations**: Maps Figma components to Amplience content types with confidence scores
4. **Human Review**: Generates review summaries for human approval before any changes
5. **Draft Execution**: Creates draft content only (never publishes automatically)

## What This Agent Does NOT Do

- **No autonomous publishing**: The agent never publishes content automatically
- **No visual/design decisions**: Only structural analysis, no design interpretation
- **No content creation from scratch**: Only places existing modules
- **No replacing CMS editors**: Assists, does not replace human decision-making

## Supported Pandora Content Types

The agent recognizes 35+ Pandora-specific content types including:

| Module | Schema URI |
|--------|-----------|
| hero-banner | https://schema-pandora.net/hero-banner |
| category-module | https://schema-pandora.net/category-module |
| product-slider-module | https://schema-pandora.net/product-slider-module |
| mega-spotter | https://schema-pandora.net/mega-spotter |
| feature-module | https://schema-pandora.net/feature-module |
| gallery-module | https://schema-pandora.net/gallery-module |
| usp-module | https://schema-pandora.net/usp-module |
| horizontal-styling-module | https://schema-pandora.net/horizontal-styling-module |
| plp-hero-banner | https://schema-pandora.net/plp-hero-banner |
| promotion-module | https://schema-pandora.net/promotion-module |
| link-list-module | https://schema-pandora.net/link-list-module |
| discover-module | https://schema-pandora.net/discover-module |
| accordion-module | https://schema-pandora.net/accordion-module |
| bazaarvoice-module | https://schema-pandora.net/bazaarvoice-module |
| copy-module | https://schema-pandora.net/copy-module |
| plp-widget | https://schema-pandora.net/plp-widget |
| two-image-module | https://schema-pandora.net/two-image-module |
| most-popular-carousel-module | https://schema-pandora.net/most-popular-carousel-module |
| contextual-product-row-module | https://schema-pandora.net/contextual-product-row-module |
| explore-module | https://schema-pandora.net/explore-module |
| image | https://schema-pandora.net/image |
| page-container | https://schema-pandora.net/page-container |
| sfcc-slot-accelerators | https://schema-pandora.net/sfcc-slot-accelerators |
| grid | https://schema-pandora.net/grid |
| page-hierarchy | https://schema-pandora.net/page-hierarchy |
| page | https://schema-pandora.net/page |
| page-cover | https://schema-pandora.net/page-cover |
| details | https://schema-pandora.net/details |
| qna-multiple | https://schema-pandora.net/qna-multiple |
| executives | https://schema-pandora.net/executives |
| text-and-media | https://schema-pandora.net/text-and-media |
| entry-points | https://schema-pandora.net/entry-points |
| feature-video | https://schema-pandora.net/feature-video |
| emtn-drawer | https://schema-pandora.net/emtn-drawer |
| iframe-renderer | https://schema-pandora.net/iframe-renderer |

## Operation Modes

The agent supports three operation modes:

| Mode | Description | Write Operations |
|------|-------------|------------------|
| `read_only` | Analysis and recommendations only | None |
| `draft_only` | Can create drafts after approval | Draft creation only |
| `full` | Full capabilities with approval gates | Draft creation only (never publishes) |

## Confidence Levels

Each mapping recommendation includes a confidence level:

| Level | Score Range | Description |
|-------|-------------|-------------|
| HIGH | 0.8 - 1.0 | Strong pattern match, safe to proceed |
| MEDIUM | 0.5 - 0.79 | Partial match, review recommended |
| LOW | 0.0 - 0.49 | Weak match, manual decision required |

## Usage

### Basic Usage

```python
from agents.amplience_placement_agent import AmplicencePlacementAgent, OperationMode

# Create agent in read-only mode (default)
agent = AmplicencePlacementAgent(mode=OperationMode.READ_ONLY)

# Run with Figma URL
result = agent.run({
    "task_description": "Map Figma design to Amplience modules",
    "input_data": {
        "figma_url": "https://www.figma.com/file/abc123/Homepage-Design"
    }
})

# Review the placement plan
print(result["data"]["review_summary"])
```

### Generate Placement Plan

```python
from agents.amplience_placement_agent import generate_placement_plan

# Generate a placement plan from Figma
plan = generate_placement_plan(
    figma_url="https://www.figma.com/file/abc123/Homepage-Design"
)

# Review mappings
for mapping in plan.mappings:
    print(f"{mapping.figma_component} -> {mapping.amplience_content_type}")
    print(f"  Confidence: {mapping.confidence_level.value} ({mapping.confidence_score})")
    if mapping.warnings:
        print(f"  Warnings: {mapping.warnings}")
```

### Execute Approved Plan

```python
from agents.amplience_placement_agent import execute_approved_plan

# After human review and approval
result = execute_approved_plan(
    plan=plan,
    approved_by="editor@pandora.net"
)

# Check draft IDs
for draft_id in result.draft_ids:
    print(f"Created draft: {draft_id}")
```

## Example Input/Output

### Input: Figma Design

```json
{
  "figma_url": "https://www.figma.com/file/abc123/Homepage-Design",
  "figma_file_id": "abc123",
  "figma_node_id": "1:2"
}
```

### Output: Placement Plan

```json
{
  "status": "success",
  "data": {
    "page_blueprint": {
      "page_name": "Homepage",
      "sections": [
        {"name": "Hero Section", "order": 0, "components": ["Hero Banner"]},
        {"name": "Featured Products", "order": 1, "components": ["Product Slider"]},
        {"name": "Categories", "order": 2, "components": ["Category Grid"]}
      ]
    },
    "model_catalog": {
      "content_types": ["hero-banner", "product-slider-module", "category-module"],
      "slots": ["homepage-hero", "homepage-featured", "homepage-categories"]
    },
    "placement_plan": {
      "mappings": [
        {
          "figma_component": "Hero Banner",
          "amplience_content_type": "hero-banner",
          "target_slot": "homepage-hero",
          "confidence_score": 0.95,
          "confidence_level": "HIGH"
        },
        {
          "figma_component": "Product Slider",
          "amplience_content_type": "product-slider-module",
          "target_slot": "homepage-featured",
          "confidence_score": 0.88,
          "confidence_level": "HIGH"
        },
        {
          "figma_component": "Category Grid",
          "amplience_content_type": "category-module",
          "target_slot": "homepage-categories",
          "confidence_score": 0.72,
          "confidence_level": "MEDIUM",
          "warnings": ["Multiple category modules available, verify selection"]
        }
      ]
    },
    "review_summary": "3 mappings proposed. 2 HIGH confidence, 1 MEDIUM confidence requiring review."
  }
}
```

## Demo Scenario

### Scenario: Map Homepage Figma Design to Amplience

1. **Designer** creates a homepage design in Figma with sections: Hero, Featured Products, Categories
2. **Content Editor** invokes the Amplience Placement Agent with the Figma URL
3. **Agent** analyzes the Figma structure and discovers available Amplience modules
4. **Agent** generates placement recommendations with confidence scores
5. **Content Editor** reviews the recommendations:
   - Hero Banner -> hero-banner (HIGH confidence)
   - Product Slider -> product-slider-module (HIGH confidence)
   - Category Grid -> category-module (MEDIUM confidence - needs review)
6. **Content Editor** approves the plan after verifying the category module selection
7. **Agent** creates draft content in Amplience (does NOT publish)
8. **Content Editor** reviews drafts in Amplience and publishes manually

## Safety Features

1. **Mandatory Human Approval**: No write operations without explicit approval
2. **Draft-Only Mode**: Never publishes content automatically
3. **Confidence Scoring**: Clear indication of mapping certainty
4. **Warning System**: Flags ambiguous or uncertain mappings
5. **Audit Logging**: All decisions and approvals are logged
6. **Operation Mode Control**: Configurable read-only, draft-only, or full modes

## Integration

### MCP Tools

The agent exposes the following MCP tools:

- `amplience_placement_analyze_figma`: Analyze Figma design structure
- `amplience_placement_discover_modules`: Discover available Amplience modules
- `amplience_placement_generate_plan`: Generate placement recommendations
- `amplience_placement_execute_plan`: Execute approved placement plan

### Workflow Integration

The agent integrates with the pnd-agents workflow system:

```json
{
  "workflows": {
    "amplience_placement": ["amplience_placement"]
  },
  "keywords": {
    "amplience_placement": [
      "placement", "place modules", "figma to amplience",
      "design to cms", "slot placement", "module placement"
    ]
  }
}
```

## Requirements

- Python 3.9+
- Figma API access (FIGMA_TOKEN environment variable)
- Amplience API access (for draft execution)

## License

Proprietary - Pandora Group
