# Using Agents Without MCP

This guide explains how to use Pandora AI Squad agents without Claude Desktop or MCP (Model Context Protocol). While MCP provides the best experience with natural language interaction, you can also use agents programmatically through Python APIs, CLI commands, and direct script execution.

## Table of Contents

1. [Overview](#overview)
2. [Python API](#python-api)
3. [CLI Commands](#cli-commands)
4. [Direct Script Execution](#direct-script-execution)
5. [Integration Examples](#integration-examples)
6. [API Reference](#api-reference)

---

## Overview

### When to Use Agents Without MCP

Using agents without MCP is useful when you need:

- **Automation**: Integrate agents into CI/CD pipelines, scheduled jobs, or automated workflows
- **Batch Processing**: Analyze multiple repositories or files in a single run
- **Custom Workflows**: Build custom tools that combine multiple agents
- **Programmatic Access**: Access agent functionality from other Python applications
- **Testing**: Test agent behavior in isolation without Claude Desktop

### What You Lose Without MCP

When using agents without MCP, you lose:

- Natural language interaction with Claude
- Automatic context from your current working directory in Claude
- Slash command support (`/tech-debt`, `/frontend`, etc.)
- Multi-agent orchestration via Task Manager
- Real-time conversation and follow-up questions

### What You Gain

However, you gain:

- Programmatic access for automation
- Integration with CI/CD pipelines
- Custom workflows and scripting
- Batch processing capabilities
- Reproducible, scriptable analysis

---

## Python API

The most powerful way to use agents without MCP is through the Python API. Each agent exposes classes and functions that you can import and use directly.

### Setup

First, ensure pnd-agents is installed:

```bash
cd /path/to/pnd-agents
pip install -e .
```

Add the pnd-agents directory to your Python path:

```python
import sys
sys.path.insert(0, '/path/to/pnd-agents/src')
```

Or set the environment variable:

```bash
export PYTHONPATH="/path/to/pnd-agents/src:$PYTHONPATH"
```

### Technical Debt Agent

Analyze technical debt in any repository:

```python
from agents.technical_debt_agent.agent import TechnicalDebtAgent, analyze_technical_debt

# Quick analysis using the convenience function
report = analyze_technical_debt("/path/to/your/repo")
print(report.to_markdown())

# Or use the full agent class for more control
agent = TechnicalDebtAgent(
    token="your-sonarcloud-token",  # Optional, reads from SONAR_TOKEN env var
    organization="your-org",
    project_key="your-project"
)

# Analyze a repository
report = agent.analyze("/path/to/your/repo")

# Get different output formats
print(report.to_dict())      # JSON-serializable dictionary
print(report.to_markdown())  # Markdown report

# Generate specific reports
summary = agent.generate_summary("/path/to/your/repo")
register = agent.generate_register("/path/to/your/repo")

# Analyze a single file
items = agent.analyze_file("/path/to/file.ts")
for item in items:
    print(f"{item.severity.value}: {item.title}")
```

### Analytics Agent

Track agent performance and generate reports:

```python
from agents.analytics_agent.agent import AnalyticsAgent, TaskMetrics

# Initialize the agent
agent = AnalyticsAgent(
    log_dir="/path/to/logs",  # Optional, defaults to ./logs/agent-analytics
)

# Track a task lifecycle
metrics = agent.on_task_started(
    agent_name="frontend-engineer",
    task_description="Create Button component",
    jira_task_id="PROJ-123",  # Optional
    workflow_id="wf-001"      # Optional
)

# ... task executes ...

# Record completion
completed_metrics = agent.on_task_completed(
    agent_name="frontend-engineer",
    jira_task_id="PROJ-123",
    metrics={
        "duration": 5000,           # milliseconds
        "iterations": 2,
        "errors": [],
        "effectivenessScore": 95.0,
        "requiresHumanReview": False,
        "confidenceScore": 0.9
    }
)

# Or record failure
failed_metrics = agent.on_task_failed(
    agent_name="frontend-engineer",
    jira_task_id="PROJ-123",
    errors=["Component validation failed", "Missing required props"]
)

# Generate reports
agent_report = agent.generate_agent_report("frontend-engineer", days=7)
sprint_report = agent.generate_sprint_report("Sprint 42", "2026-01-01", "2026-01-14")

# Get markdown report
markdown = agent.generate_markdown_report(days=7)
print(markdown)

# Get JSON report
json_report = agent.generate_json_report(days=7)
```

### Sonar Validation Agent

Validate code against SonarCloud quality gates:

```python
from agents.sonar_validation_agent.agent import SonarValidationAgent

# Initialize with token (or set SONAR_TOKEN env var)
agent = SonarValidationAgent(
    token="your-sonarcloud-token",
    organization="pandora-jewelry",
    project_key="pandora-jewelry_spark_pandora-group"
)

# Fetch current quality gate status
status = agent.fetch_quality_gate_status()
print(f"Quality Gate: {status['status']}")

# Fetch issues
issues = agent.fetch_issues(severities=["BLOCKER", "CRITICAL"])
for issue in issues:
    print(f"{issue['severity']}: {issue['message']}")

# Fetch coverage metrics
coverage = agent.fetch_coverage()
print(f"Coverage: {coverage['coverage']}%")

# Run full validation
result = agent.validate()
print(result.to_markdown())
```

### Unit Test Agent

Generate unit tests for your code:

```python
from agents.unit_test_agent.agent import UnitTestAgent

# Initialize the agent
agent = UnitTestAgent()

# Analyze a file and generate test suggestions
analysis = agent.analyze_file("/path/to/src/components/Button.tsx")
print(f"Suggested tests: {len(analysis['test_cases'])}")

# Generate test file content
test_content = agent.generate_tests(
    source_file="/path/to/src/components/Button.tsx",
    test_framework="jest",  # or "vitest", "mocha"
    coverage_target=100
)
print(test_content)
```

### QA Agent

Validate implementation against acceptance criteria:

```python
from agents.qa_agent.agent import QAAgent

# Initialize the agent
agent = QAAgent()

# Validate against Gherkin acceptance criteria
result = agent.validate(
    implementation_path="/path/to/src/components/Button.tsx",
    acceptance_criteria="""
    Feature: Button Component
    
    Scenario: Primary button renders correctly
      Given a Button component with variant "primary"
      When the component is rendered
      Then it should have the primary color scheme
      And it should be accessible
    """
)

print(f"Passed: {result['passed']}")
print(f"Failed: {result['failed']}")
for failure in result['failures']:
    print(f"  - {failure['scenario']}: {failure['reason']}")
```

### Figma Reader Agent

Extract design information from Figma:

```python
from agents.figma_reader_agent.agent import FigmaReaderAgent

# Initialize with token (or set FIGMA_ACCESS_TOKEN env var)
agent = FigmaReaderAgent(token="your-figma-token")

# Extract component metadata from a Figma URL
metadata = agent.extract_component(
    "https://www.figma.com/design/ABC123/My-Design?node-id=123-456"
)

print(f"Component: {metadata['name']}")
print(f"Dimensions: {metadata['width']}x{metadata['height']}")
print(f"Colors: {metadata['colors']}")
print(f"Typography: {metadata['typography']}")
```

### PR Review Agent

Review pull requests from Azure DevOps:

```python
from agents.pr_review_agent.agent import PRReviewAgent

# Initialize with credentials (or set env vars)
agent = PRReviewAgent(
    pat="your-azure-devops-pat",  # or AZURE_DEVOPS_PAT env var
    organization="pandora-jewelry",
    project="Spark"
)

# Review a pull request
review = agent.review_pr(pr_id=12345)

print(f"Overall Score: {review['score']}/100")
print(f"Issues Found: {len(review['issues'])}")

for issue in review['issues']:
    print(f"  [{issue['severity']}] {issue['file']}:{issue['line']}")
    print(f"    {issue['message']}")
```

---

## CLI Commands

The pnd-agents CLI provides several commands that work without MCP:

### Check Installation Status

```bash
pnd-agents status
```

Shows:
- Installation path
- Whether main.py exists
- Agent configuration status
- Claude config status

### View Configuration

```bash
# Show current configuration
pnd-agents config --show

# Reconfigure agents
pnd-agents config --agents

# Reconfigure environment variables
pnd-agents config --env
```

### Run Tasks (Experimental)

```bash
# Run a task description
pnd-agents run-task "Analyze technical debt in this repository"

# Analyze a task without executing
pnd-agents analyze-task "Create a Button component"
```

### Generate Sprint Reports

```bash
# Generate a sprint report
pnd-agents sprint-report --sprint "Sprint 42" --start "2026-01-01" --end "2026-01-14"
```

### Scan Repository

```bash
# Scan current directory for issues
pnd-agents scan

# Scan a specific directory
pnd-agents scan --path /path/to/repo
```

---

## Direct Script Execution

You can also run agent modules directly as scripts:

### Technical Debt Analysis

```bash
# Run technical debt analysis
python -m agents.technical_debt_agent.agent analyze /path/to/repo

# Generate summary report
python -m agents.technical_debt_agent.agent summary /path/to/repo

# Generate detailed register
python -m agents.technical_debt_agent.agent register /path/to/repo
```

### Analytics Reports

```bash
# Track task start
python -m agents.analytics_agent.agent track-start frontend-engineer "Create component"

# Track task completion
python -m agents.analytics_agent.agent track-end frontend-engineer

# Generate report
python -m agents.analytics_agent.agent report --days 7

# List all tracked tasks
python -m agents.analytics_agent.agent list
```

### Run MCP Server Manually

For debugging or testing MCP tools:

```bash
# Start the MCP server (will wait for client connections)
python main.py

# Or run with debug output
python main.py --debug
```

---

## Integration Examples

### CI/CD Pipeline Integration

Add technical debt analysis to your CI/CD pipeline:

```yaml
# .github/workflows/tech-debt.yml
name: Technical Debt Analysis

on:
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install pnd-agents
        run: |
          git clone https://github.com/shvee-pandora/pnd-agents.git
          cd pnd-agents
          pip install -e .
      
      - name: Run Technical Debt Analysis
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          PYTHONPATH: ./pnd-agents/src
        run: |
          python -c "
          from agents.technical_debt_agent.agent import analyze_technical_debt
          report = analyze_technical_debt('.')
          print(report.to_markdown())
          
          # Fail if too many high-severity items
          high_severity = [i for i in report.items if i.severity.value == 'High']
          if len(high_severity) > 10:
              print(f'::error::Found {len(high_severity)} high-severity debt items')
              exit(1)
          "
```

### Pre-commit Hook

Add code review to your pre-commit hooks:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run technical debt check on staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|js|jsx)$')

if [ -n "$STAGED_FILES" ]; then
    python -c "
import sys
sys.path.insert(0, '/path/to/pnd-agents/src')
from agents.technical_debt_agent.agent import TechnicalDebtAgent

agent = TechnicalDebtAgent()
issues = []

for file in '''$STAGED_FILES'''.split():
    items = agent.analyze_file(file)
    high_severity = [i for i in items if i.severity.value == 'High']
    issues.extend(high_severity)

if issues:
    print('High-severity technical debt found:')
    for issue in issues:
        print(f'  {issue.file_path}: {issue.title}')
    sys.exit(1)
"
fi
```

### Scheduled Analysis

Run weekly technical debt reports:

```python
#!/usr/bin/env python3
"""Weekly technical debt report generator."""

import sys
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

sys.path.insert(0, '/path/to/pnd-agents/src')
from agents.technical_debt_agent.agent import TechnicalDebtAgent

def generate_weekly_report(repo_path: str, recipients: list[str]):
    """Generate and email weekly technical debt report."""
    agent = TechnicalDebtAgent()
    report = agent.analyze(repo_path)
    
    # Generate markdown report
    markdown = report.to_markdown()
    
    # Create email
    msg = MIMEText(markdown)
    msg['Subject'] = f'Weekly Technical Debt Report - {datetime.now().strftime("%Y-%m-%d")}'
    msg['From'] = 'tech-debt-bot@company.com'
    msg['To'] = ', '.join(recipients)
    
    # Send email (configure SMTP as needed)
    with smtplib.SMTP('smtp.company.com') as server:
        server.send_message(msg)
    
    print(f"Report sent to {len(recipients)} recipients")

if __name__ == '__main__':
    generate_weekly_report(
        repo_path='/path/to/your/repo',
        recipients=['team@company.com']
    )
```

### Custom Analysis Tool

Build a custom tool that combines multiple agents:

```python
#!/usr/bin/env python3
"""Custom repository health check tool."""

import sys
import json
from pathlib import Path

sys.path.insert(0, '/path/to/pnd-agents/src')

from agents.technical_debt_agent.agent import TechnicalDebtAgent
from agents.sonar_validation_agent.agent import SonarValidationAgent

def health_check(repo_path: str) -> dict:
    """Run comprehensive health check on a repository."""
    results = {
        "repo_path": repo_path,
        "checks": {}
    }
    
    # Technical Debt Analysis
    print("Running technical debt analysis...")
    debt_agent = TechnicalDebtAgent()
    debt_report = debt_agent.analyze(repo_path)
    
    results["checks"]["technical_debt"] = {
        "total_items": debt_report.summary.total_items if debt_report.summary else 0,
        "high_severity": debt_report.summary.by_severity.get("High", 0) if debt_report.summary else 0,
        "status": "pass" if (debt_report.summary and debt_report.summary.by_severity.get("High", 0) < 5) else "fail"
    }
    
    # SonarCloud Validation (if token available)
    import os
    if os.environ.get("SONAR_TOKEN"):
        print("Running SonarCloud validation...")
        sonar_agent = SonarValidationAgent()
        try:
            quality_gate = sonar_agent.fetch_quality_gate_status()
            results["checks"]["sonarcloud"] = {
                "quality_gate": quality_gate.get("status", "UNKNOWN"),
                "status": "pass" if quality_gate.get("status") == "OK" else "fail"
            }
        except Exception as e:
            results["checks"]["sonarcloud"] = {
                "error": str(e),
                "status": "skip"
            }
    
    # Calculate overall health
    passed = sum(1 for c in results["checks"].values() if c.get("status") == "pass")
    total = sum(1 for c in results["checks"].values() if c.get("status") != "skip")
    results["overall_health"] = f"{passed}/{total} checks passed"
    results["healthy"] = passed == total
    
    return results

if __name__ == '__main__':
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    results = health_check(repo)
    print(json.dumps(results, indent=2))
    
    sys.exit(0 if results["healthy"] else 1)
```

---

## API Reference

### Agent Classes

| Agent | Class | Module |
|-------|-------|--------|
| Technical Debt | `TechnicalDebtAgent` | `agents.technical_debt_agent.agent` |
| Analytics | `AnalyticsAgent` | `agents.analytics_agent.agent` |
| Sonar Validation | `SonarValidationAgent` | `agents.sonar_validation_agent.agent` |
| Unit Test | `UnitTestAgent` | `agents.unit_test_agent.agent` |
| QA | `QAAgent` | `agents.qa_agent.agent` |
| Figma Reader | `FigmaReaderAgent` | `agents.figma_reader_agent.agent` |
| PR Review | `PRReviewAgent` | `agents.pr_review_agent.agent` |
| Commerce | `CommerceAgent` | `agents.commerce_agent.agent` |

### Common Methods

Most agents follow a similar pattern:

```python
# Initialize
agent = AgentClass(token="optional-token")

# Analyze
result = agent.analyze(path_or_input)

# Get output formats
result.to_dict()      # JSON-serializable dictionary
result.to_markdown()  # Markdown report

# Run with action
agent.run(action="analyze", input_data={...})
```

### Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `SONAR_TOKEN` | Sonar Validation, Technical Debt | SonarCloud API token |
| `FIGMA_ACCESS_TOKEN` | Figma Reader | Figma API token |
| `JIRA_BASE_URL` | Analytics, PRD to Jira | Jira instance URL |
| `JIRA_EMAIL` | Analytics, PRD to Jira | Jira authentication email |
| `JIRA_API_TOKEN` | Analytics, PRD to Jira | Jira API token |
| `AZURE_DEVOPS_PAT` | PR Review | Azure DevOps PAT |
| `AZURE_DEVOPS_ORG` | PR Review | Azure DevOps organization |
| `AZURE_DEVOPS_PROJECT` | PR Review | Azure DevOps project |

---

## Troubleshooting

### Import Errors

If you get import errors, ensure the PYTHONPATH is set correctly:

```bash
export PYTHONPATH="/path/to/pnd-agents/src:$PYTHONPATH"
```

Or add it programmatically:

```python
import sys
sys.path.insert(0, '/path/to/pnd-agents/src')
```

### Missing Dependencies

Install all dependencies:

```bash
cd /path/to/pnd-agents
pip install -e .
```

### Token/Authentication Issues

Ensure environment variables are set:

```bash
export SONAR_TOKEN="your-token"
export FIGMA_ACCESS_TOKEN="your-token"
```

Or pass tokens directly to agent constructors:

```python
agent = TechnicalDebtAgent(token="your-token")
```

---

**Last Updated**: January 2026  
**Version**: 2.0.0  
**Maintained by**: Pandora Group
