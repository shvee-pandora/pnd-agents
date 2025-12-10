# Analytics Agent Examples

This directory contains examples demonstrating how to use the Analytics & Reporting Agent.

## Examples

### basic_usage.py

Demonstrates basic usage of the Analytics Agent:
- Tracking task start and completion
- Tracking task failures
- Using the `record_event` convenience function
- Generating reports (JSON and Markdown)
- Listing analytics data
- Generating agent-specific reports

Run with:
```bash
python examples/analytics/basic_usage.py
```

### mcp_usage.py

Demonstrates MCP (Model Context Protocol) integration:
- Listing available MCP tools
- Tracking tasks via MCP commands
- Generating reports via MCP
- Managing configuration via MCP

Run with:
```bash
python examples/analytics/mcp_usage.py
```

## Quick Start

### Track a Task

```python
from agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent()

# Start tracking
agent.on_task_started(
    agent_name="Frontend Engineer Agent",
    task_description="Create Header Component",
    jira_task_id="EPA-123",
)

# Complete tracking
agent.on_task_completed(
    agent_name="Frontend Engineer Agent",
    jira_task_id="EPA-123",
    metrics={
        "duration": 208000,
        "iterations": 4,
        "errors": [],
        "effectivenessScore": 92.0,
    },
)
```

### Using the Convenience Function

```python
from tools.analytics_store import record_event

# Record task start
record_event(
    event_type="task_started",
    agent_name="Code Review Agent",
    task_description="Review PR #42",
    jira_task_id="EPA-456",
)

# Record task completion
record_event(
    event_type="task_completed",
    agent_name="Code Review Agent",
    jira_task_id="EPA-456",
    metrics={"duration": 45000},
)
```

### Generate Reports

```python
from agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent()

# JSON report
json_report = agent.generate_json_report(days=14)

# Markdown report (for Confluence)
md_report = agent.generate_markdown_report(days=14)
```

## MCP Commands

The following MCP commands are available for Claude Desktop/Code:

| Command | Description |
|---------|-------------|
| `analytics_track_task_start` | Record the start of a task |
| `analytics_track_task_end` | Record task completion |
| `analytics_track_task_failure` | Record task failure |
| `analytics_update_jira_task` | Update JIRA with AI metrics |
| `analytics_generate_report` | Generate performance report |
| `analytics_list` | List stored analytics |
| `analytics_get_config` | Get current configuration |
| `analytics_update_config` | Update configuration |

## Configuration

Analytics configuration is stored in `config/analytics.config.json`:

```json
{
  "log_directory": "logs/agent-analytics",
  "log_retention_days": 90,
  "estimated_time_saved_per_task": 2.0,
  "jira_comment_enabled": true,
  "jira_custom_fields_enabled": true,
  "auto_update_jira": true
}
```

JIRA configuration is stored in `config/jira.config.json`:

```json
{
  "base_url": "https://your-instance.atlassian.net",
  "email": "your-email@example.com",
  "project_key": "EPA",
  "field_ai_used": "customfield_ai_used",
  "field_agent_name": "customfield_agent_name",
  "field_efficiency_score": "customfield_ai_efficiency_score",
  "field_duration": "customfield_ai_duration"
}
```

## Environment Variables

Set these environment variables for JIRA integration:

```bash
export JIRA_BASE_URL="https://your-instance.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```
