# Pillar 3 Report Generator

The Pillar 3 Report Generator fetches data from JIRA and generates executive-ready status reports following the Pandora Pillar 3 template 2026 (HYBRID v2 format).

## Overview

This tool enables automated generation of Pillar 3 status reports by:
- Fetching data from JIRA Epics, Initiatives, or via JQL queries
- Extracting objectives, key results, milestones, and outcomes from JIRA issues
- Automatically deriving RAG status from child issue statuses
- Generating reports in Markdown (for Confluence), JSON, or PDF format
- Publishing directly to Confluence

## Prerequisites

Set these environment variables before using the tool:

```bash
export JIRA_BASE_URL="https://your-company.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-jira-api-token"

# For Confluence publishing (optional):
export CONFLUENCE_BASE_URL="https://your-company.atlassian.net/wiki"
export CONFLUENCE_EMAIL="your-email@company.com"
export CONFLUENCE_API_TOKEN="your-confluence-api-token"
```

## Example Prompts

### Generate a PDF Report from a JIRA Epic

```
Generate a Pillar 3 PDF report for Epic INS-2508
```

```
Create a status report PDF for the ENGRAVING epic (ENG-100) and save it to /tmp/engraving-report.pdf
```

### Generate a Report and Publish to Confluence

```
Generate a Pillar 3 report for Epic EPA-456 and publish it to the TEAM Confluence space
```

```
Create a status report for Initiative INIT-789 and publish to Confluence space "ONLINE" with title "Q1 2026 Status"
```

### Generate Reports Using JQL

```
Generate a Pillar 3 report for all issues in project EPA that are in progress
```

```
Create a status report for all stories assigned to the Analytics team using JQL: project = EPA AND labels = "analytics-team"
```

### Get Report in Different Formats

```
Generate a Pillar 3 report for Epic INS-2508 in markdown format
```

```
Get the JSON data for a Pillar 3 report from Epic ENG-100
```

## Usage Examples

### Via MCP Tools (Claude Desktop/Code)

```python
# Generate a report from a JIRA Epic
pillar3_generate_report(epic_key="EPA-123", output_format="markdown")

# Generate from an Initiative
pillar3_generate_report(initiative_key="INIT-456", output_format="json")

# Generate from a JQL query
pillar3_generate_report(
    jql='project = EPA AND type = Story',
    team_name="Analytics Team",
    output_format="pdf"
)

# Publish directly to Confluence
pillar3_publish_to_confluence(
    epic_key="EPA-123",
    space_key="TEAM",
    page_title="Q1 2026 Status Report"
)

# Generate a standalone PDF
pillar3_generate_pdf(
    epic_key="EPA-123",
    output_path="/tmp/my_report.pdf"
)
```

### Via Analytics Agent (Python API)

```python
from agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent()

# Generate report from Epic
result = agent.run({
    'input_data': {
        'action': 'pillar3_report',
        'epic_key': 'EPA-123',
        'generate_pdf': True
    }
})
print(result['data']['markdown'])  # Markdown content
print(result['data']['pdf_path'])  # Path to PDF

# Generate and publish to Confluence
result = agent.run({
    'input_data': {
        'action': 'pillar3_report',
        'epic_key': 'EPA-123',
        'confluence_space_key': 'TEAM',
        'page_title': 'Analytics Agent - Pillar 3 Report',
        'generate_pdf': True
    }
})
print(result['data']['confluence']['url'])  # Confluence page URL
```

### Direct Python Import

```python
from tools.pillar3_report import (
    Pillar3ReportGenerator,
    generate_pillar3_pdf,
    generate_pillar3_report,
    generate_and_publish_pillar3_report
)

# Quick report generation
result = generate_pillar3_report(epic_key="EPA-123", output_format="markdown")
print(result['content'])

# Full control with generator class
with Pillar3ReportGenerator() as generator:
    report = generator.generate_report_from_epic("EPA-123")
    
    # Get markdown for Confluence
    markdown = generator.to_markdown(report)
    
    # Get JSON
    json_data = generator.to_json(report)
    
    # Generate PDF
    generate_pillar3_pdf(report, "/tmp/pillar3_report.pdf")

# Generate and publish in one call
result = generate_and_publish_pillar3_report(
    epic_key="EPA-123",
    space_key="TEAM",
    page_title="My Report",
    also_generate_pdf=True
)
```

## Report Structure (HYBRID v2 Template)

The generated PDF follows the Pandora Pillar 3 template 2026 HYBRID v2 format with a two-column layout:

### Header
- **PL**: Product Line (e.g., Online, Retail)
- **TEAM/INITIATIVE**: Team or initiative name
- **TYPE**: HYBRID v2

### Left Column
- **Objectives**: Key objectives extracted from Epic/Initiative description
- **Status**: RAG indicators for Resources, Timing, Budget, Scope
- **Route to Green & Key Watchouts**: Blockers and risks
- **Progress last month**: Recently completed work
- **Plan for this month**: Upcoming planned work

### Right Column
- **Key Results**: Measurable outcomes
- **Outcomes**: Progress on deliverables with status
- **Key Milestones**: Important dates with completion status

### Footer
- Team/Initiative name
- Classification: Pandora Internal

## Data Extraction from JIRA

| Report Field | JIRA Source |
|--------------|-------------|
| Team/Initiative | Epic/Initiative summary |
| Product Line | Custom field or project name |
| Objectives | Epic description (bullet points) or child issue summaries |
| Key Results | Completed/in-progress child issues |
| RAG Status | Derived from child issue statuses (blocked=RED, slow progress=AMBER, on track=GREEN) |
| Milestones | Child issues with due dates |
| Outcomes | Completed or in-progress child issues |
| Progress last month | Issues completed in last 30 days |
| Plan this month | In-progress or upcoming issues due within 30 days |
| Route to Green | Blocked/overdue issues |

## RAG Status Rules

The tool automatically derives RAG status from JIRA issue statuses:

- **GREEN**: On track - majority of issues are progressing normally
- **AMBER**: At risk - some issues are delayed or have dependencies
- **RED**: Blocked - issues are blocked or significantly overdue

Default behavior:
- If no risk is documented, default to GREEN
- If dependency or uncertainty exists, use AMBER
- Never mark RED unless explicitly blocked

## Output Formats

### Markdown
Tables and sections formatted for Confluence publishing. Includes all report sections with proper formatting.

### JSON
Full report data structure for programmatic use. Contains all fields as a dictionary.

### PDF
Professional 960x540 widescreen format matching the Pandora Pillar 3 template 2026 with:
- Two-column layout
- RAG indicator circles with color coding
- Proper typography and spacing
- Classification footer

## Troubleshooting

### 410 Gone Error
If you see a "410 Gone" error, the JIRA API endpoint may have been deprecated. The tool automatically falls back to the legacy endpoint, but ensure you have the latest version.

### No Issues Found
Ensure your JQL query is correct and you have access to the project. Try running the query directly in JIRA first.

### Missing Data
If report sections are empty, check that:
- The Epic has child issues (stories/tasks)
- Issues have proper status categories set
- Due dates are populated for milestone tracking

## MCP Tool Reference

### pillar3_generate_report
Generate a Pillar 3 status report from JIRA data.

Parameters:
- `epic_key` (string): JIRA Epic key (e.g., "EPA-123")
- `initiative_key` (string): JIRA Initiative key
- `jql` (string): JQL query to fetch issues
- `team_name` (string): Team name (used with JQL)
- `output_format` (string): "markdown", "json", or "pdf"

### pillar3_publish_to_confluence
Generate and publish a Pillar 3 report to Confluence.

Parameters:
- `epic_key` (string): JIRA Epic key
- `initiative_key` (string): JIRA Initiative key
- `jql` (string): JQL query
- `team_name` (string): Team name
- `space_key` (string, required): Confluence space key
- `page_title` (string): Page title
- `parent_page_id` (string): Parent page ID
- `also_generate_pdf` (boolean): Also generate PDF

### pillar3_generate_pdf
Generate a Pillar 3 report PDF from JIRA data.

Parameters:
- `epic_key` (string): JIRA Epic key
- `initiative_key` (string): JIRA Initiative key
- `jql` (string): JQL query
- `team_name` (string): Team name
- `output_path` (string): Path for output PDF
