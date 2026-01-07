# How the Amplience Placement Agent Works

This guide explains how developers and content editors can use the Amplience Placement Agent to map Figma designs to Amplience CMS modules, with step-by-step instructions from initial prompt to final publication.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [How to Use the Agent](#how-to-use-the-agent)
4. [Example Prompts](#example-prompts)
5. [Understanding the Output](#understanding-the-output)
6. [Implementing in Amplience](#implementing-in-amplience)
7. [Publishing Your Content](#publishing-your-content)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Amplience Placement Agent is a Human-in-the-Loop AI assistant that:

1. **Analyzes** your Figma design to extract page structure
2. **Discovers** available Amplience content types in your CMS
3. **Maps** Figma components to the most appropriate Amplience modules
4. **Generates** a placement plan with confidence scores
5. **Waits** for your approval before any changes
6. **Creates** draft content (never publishes automatically)

The agent ensures you maintain full control over your CMS while accelerating the design-to-content workflow.

---

## Prerequisites

Before using the agent, ensure you have:

1. **Figma Access**: A Figma file URL or file ID containing your design
2. **Environment Variables**:
   ```bash
   export FIGMA_ACCESS_TOKEN="your-figma-token"
   ```
3. **pnd-agents Installed**: The agent system should be configured in your environment
4. **Amplience Access**: Credentials for your Amplience hub (for draft execution)

---

## How to Use the Agent

### Method 1: Via Claude Desktop (MCP Integration)

If you have pnd-agents configured with Claude Desktop, simply describe your task:

```
I need to map my Figma homepage design to Amplience modules.
Figma URL: https://www.figma.com/file/abc123/Homepage-Design
```

### Method 2: Via CLI

```bash
pnd-agents run-task "Map Figma design to Amplience modules" \
  --input figma_url=https://www.figma.com/file/abc123/Homepage-Design
```

### Method 3: Via Python API

```python
from agents.amplience_placement_agent import AmplicencePlacementAgent, OperationMode

# Create agent
agent = AmplicencePlacementAgent(mode=OperationMode.READ_ONLY)

# Run with your Figma URL
result = agent.run({
    "task_description": "Map Figma homepage to Amplience",
    "input_data": {
        "figma_url": "https://www.figma.com/file/abc123/Homepage-Design"
    }
})

# Review the placement plan
print(result["data"]["review_summary"])
```

---

## Example Prompts

### Prompt 1: Basic Homepage Mapping

```
Map my Figma homepage design to Amplience modules.

Figma URL: https://www.figma.com/file/abc123/Homepage-Design

I need to know which Amplience content types to use for each section.
```

### Prompt 2: PLP (Product Listing Page) Mapping

```
I have a new PLP design in Figma that needs to be implemented in Amplience.

Figma file: https://www.figma.com/file/xyz789/PLP-Redesign-2024
Node ID: 1:234 (the main PLP frame)

Please analyze the design and recommend which Pandora modules to use.
```

### Prompt 3: Campaign Landing Page

```
We're launching a Valentine's Day campaign and I need to set up the landing page in Amplience.

Design: https://www.figma.com/file/vday2024/Valentines-Campaign

The page has:
- Hero banner with video
- Product carousel
- Gift guide section
- Promotional banner

Map these to our existing Amplience modules and tell me what I need to configure.
```

### Prompt 4: Review and Execute

```
I've reviewed the placement plan for the homepage. Please proceed with creating the draft content in Amplience.

Approved by: john.doe@pandora.net
```

---

## Understanding the Output

When you run the agent, you'll receive a structured output with several key sections:

### 1. Page Blueprint

The extracted structure from your Figma design:

```json
{
  "page_blueprint": {
    "page_name": "Homepage",
    "figma_file_id": "abc123",
    "sections": [
      {
        "nodeId": "1:1",
        "name": "Hero Banner",
        "componentType": "hero",
        "order": 0,
        "properties": {
          "width": 1440,
          "height": 600
        }
      },
      {
        "nodeId": "1:2",
        "name": "Product Carousel",
        "componentType": "product",
        "order": 1
      }
    ]
  }
}
```

### 2. Model Catalog

Available Amplience content types discovered:

```json
{
  "model_catalog": {
    "content_types": [
      {
        "schemaId": "https://schema-pandora.net/hero-banner",
        "label": "M78 Hero Module",
        "description": "Full-width hero banner with image/video, headline text, CTA",
        "slots": ["sfcc-slot-accelerators"],
        "variants": ["default", "video", "split"]
      }
    ],
    "slots": [
      "sfcc-slot-accelerators",
      "homepage-hero",
      "homepage-slot-1"
    ],
    "totalContentTypes": 35,
    "totalSlots": 18
  }
}
```

### 3. Placement Mappings

The recommended mappings with confidence scores:

```json
{
  "mappings": [
    {
      "figmaSection": {
        "name": "Hero Banner",
        "componentType": "hero"
      },
      "amplienceContentType": {
        "schemaId": "https://schema-pandora.net/hero-banner",
        "label": "M78 Hero Module"
      },
      "targetSlot": "sfcc-slot-accelerators",
      "confidence": "high",
      "confidenceScore": 0.95,
      "reasoning": "Strong match between 'Hero Banner' and 'M78 Hero Module'",
      "warnings": [],
      "alternatives": ["PLP Hero Banner"],
      "requiresManualDecision": false
    }
  ]
}
```

### 4. Review Summary

A human-readable summary for approval:

```json
{
  "review_summary": "AMPLIENCE PLACEMENT REVIEW SUMMARY\n================================\n\nPage: Homepage\nTotal Sections: 4\nTotal Mappings: 4\n\nCONFIDENCE BREAKDOWN:\n- HIGH confidence: 3 mappings\n- MEDIUM confidence: 1 mapping\n- LOW confidence: 0 mappings\n\nACTION REQUIRED:\n- 1 mapping requires manual decision\n\nRECOMMENDATION: Review the MEDIUM confidence mapping before approval."
}
```

### 5. Confidence Levels Explained

| Level | Score | Meaning | Action |
|-------|-------|---------|--------|
| HIGH | 0.8-1.0 | Strong pattern match | Safe to proceed |
| MEDIUM | 0.5-0.79 | Partial match | Review recommended |
| LOW | 0.3-0.49 | Weak match | Manual decision needed |
| UNCERTAIN | 0.0-0.29 | No clear match | Create new type or skip |

---

## Implementing in Amplience

Once you have the placement plan, follow these steps to implement in Amplience:

### Step 1: Log into Amplience Dynamic Content

1. Go to your Amplience hub (e.g., `https://content.amplience.net`)
2. Navigate to **Content** > **Content Library**

### Step 2: Create Content Items for Each Mapping

For each mapping in the placement plan:

#### Example: Creating a Hero Banner

Based on the mapping:
```json
{
  "figmaSection": "Hero Banner",
  "amplienceContentType": "M78 Hero Module",
  "schemaId": "https://schema-pandora.net/hero-banner"
}
```

**In Amplience:**

1. Click **Create Content**
2. Select schema: **M78 Hero Module** (`hero-banner`)
3. Fill in the required fields:

```
Content Name: homepage-hero-banner-2024
Label: Homepage Hero Banner

Fields to configure:
- desktopMobileMedia:
  - Desktop Image: [Upload from Figma export]
  - Mobile Image: [Upload mobile version]
  
- headlineText:
  - en-US: "Discover Our New Collection"
  - da-DK: "Opdag vores nye kollektion"
  
- headlineTextSize: "large"

- cta:
  - label: "Shop Now"
  - url: "/new-collection"
  
- colorTheme: "light"
- gradientOverlay: "none"
```

4. Click **Save** (creates as draft)

### Step 3: Create SFCC Slot Accelerator

To place the content in a slot:

1. Create new content with schema: **SFCC Slot Accelerators**
2. Configure:

```
Content Name: homepage-hero-slot
Label: Homepage Hero Slot

Fields:
- sfcc_slot:
  - slotId: "homepage-hero"
  
- sfcc_site:
  - Select your target sites (e.g., en-US, en-GB, da-DK)
  
- content:
  - Link to: homepage-hero-banner-2024 (the content you just created)
```

3. Click **Save**

### Step 4: Repeat for All Mappings

Follow the same process for each mapping in your placement plan:

| Figma Section | Amplience Content Type | Slot |
|---------------|----------------------|------|
| Hero Banner | M78 Hero Module | homepage-hero |
| Product Carousel | Product Slider Module | homepage-slot-1 |
| Category Grid | M65 Category Module | homepage-slot-2 |
| Promo Banner | Promotion Module | homepage-slot-3 |

### Step 5: Preview Your Content

1. In Amplience, select your content item
2. Click **Preview**
3. Select the visualization (e.g., "Homepage Preview")
4. Verify the content renders correctly

---

## Publishing Your Content

**IMPORTANT**: The agent only creates DRAFT content. You must manually publish.

### Publishing Workflow

#### Option A: Publish Individual Items

1. Select the content item in Amplience
2. Click **Publish**
3. Choose publish date (immediate or scheduled)
4. Confirm publication

#### Option B: Publish via Edition (Recommended for Campaigns)

1. Go to **Planning** > **Editions**
2. Create new Edition: "Homepage Launch 2024"
3. Add all related content items to the Edition
4. Schedule the Edition for your launch date
5. Publish the entire Edition at once

### Publishing Checklist

Before publishing, verify:

- [ ] All content items are in DRAFT status
- [ ] Preview renders correctly on desktop and mobile
- [ ] All localized content is filled in (en-US, da-DK, etc.)
- [ ] Images are optimized and properly sized
- [ ] CTAs link to correct URLs
- [ ] SFCC slots are configured for correct sites
- [ ] Stakeholder approval obtained

### Post-Publication Verification

After publishing:

1. Clear CDN cache if needed
2. Verify content appears on live site
3. Test on multiple devices/browsers
4. Monitor for any errors in Amplience logs

---

## Troubleshooting

### Issue: Agent returns "No matching content type found"

**Cause**: The Figma component name doesn't match any known Pandora modules.

**Solution**:
1. Check the `alternatives` field in the mapping
2. Manually select the appropriate content type
3. Or create a new content type in Amplience if needed

### Issue: Low confidence score on mapping

**Cause**: The component name is ambiguous or doesn't clearly match a module.

**Solution**:
1. Review the `reasoning` field to understand why
2. Check `alternatives` for better matches
3. Make a manual decision based on your design intent

### Issue: "Figma access token is required"

**Cause**: FIGMA_ACCESS_TOKEN environment variable not set.

**Solution**:
```bash
export FIGMA_ACCESS_TOKEN="your-token-here"
```

### Issue: Draft execution fails

**Cause**: Amplience API credentials not configured or insufficient permissions.

**Solution**:
1. Verify AMPLIENCE_HUB_ID and AMPLIENCE_API_KEY are set
2. Ensure your API key has write permissions
3. Check hub access in Amplience settings

---

## Quick Reference Card

### Agent Commands

| Action | Command |
|--------|---------|
| Analyze Figma | `agent.analyze_figma(figma_url)` |
| Discover modules | `agent.discover_amplience_models()` |
| Generate plan | `agent.generate_placement_plan(context)` |
| Execute (after approval) | `agent.execute_placement_plan(plan, approved_by)` |

### Supported Content Types

| Module Code | Amplience Schema | Use Case |
|-------------|------------------|----------|
| M78 | hero-banner | Hero sections |
| M65 | category-module | Category grids |
| - | product-slider-module | Product carousels |
| - | promotion-module | Promotional banners |
| - | feature-module | Feature highlights |
| - | gallery-module | Image galleries |
| - | usp-module | USP displays |
| - | accordion-module | FAQ sections |
| - | copy-module | Text content |

### Environment Variables

```bash
FIGMA_ACCESS_TOKEN=xxx      # Required for Figma analysis
AMPLIENCE_HUB_ID=xxx        # Required for draft execution
AMPLIENCE_API_KEY=xxx       # Required for draft execution
```

---

## Support

For issues or questions:
- Check the [README.md](./README.md) for technical details
- Review the [agent documentation](./agents/amplience-placement-agent.md)
- Contact the PG AI Squad team

---

*Last updated: January 2026*
