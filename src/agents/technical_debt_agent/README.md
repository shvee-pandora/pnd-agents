# Technical Debt Agent

A dedicated agent for identifying, classifying, prioritizing, and explaining technical debt across a repository using static analysis, repository context, and optional SonarCloud data.

## Purpose

The Technical Debt Agent performs **READ-ONLY** analysis to help engineers, tech leads, and leadership understand and prioritize technical debt in their codebase. It produces actionable, structured outputs suitable for sprint planning, architecture reviews, and executive reporting.

## Capabilities

### 1. Repository Analysis
- Scans the current workspace (repo-aware)
- Identifies:
  - TODO / FIXME / HACK / BUG comments
  - Deprecated APIs or patterns
  - High cyclomatic complexity
  - Large functions and files
  - Legacy patterns mixed with modern ones
  - Missing or weak test coverage

### 2. Technical Debt Classification
Classifies debt into five categories:
- **Code Debt**: TODO comments, deprecated code, high complexity, large files/functions
- **Test Debt**: Missing tests, no coverage reporting, missing test configuration
- **Architecture Debt**: Mixed patterns, deep nesting, structural issues
- **Dependency Debt**: Outdated packages, deprecated dependencies, lock file issues
- **Process/Documentation Debt**: Missing README, documentation gaps

### 3. Severity & Impact Scoring
For each debt item:
- **Severity**: Low / Medium / High
- **Impact**: Delivery Risk / Maintenance Cost / Stability Risk
- **Estimated Fix Effort**: S (Small) / M (Medium) / L (Large)

### 4. Context-Aware Reasoning
- Uses repo structure and conventions
- Respects repo profile (if `.claude/repo-profile.json` exists)
- Provides specific file and function references
- Avoids generic advice

### 5. SonarCloud Integration (Optional)
When `SONAR_TOKEN` is available:
- Pulls maintainability, reliability, and security issues
- Translates Sonar findings into human-readable debt items
- De-duplicates overlapping issues

The agent works fully without SonarCloud as well.

## Usage

The Technical Debt Agent is designed to work with **any repository** - not just pnd-agents. You can analyze any codebase by providing the path to the repository.

### Via Claude Desktop / Claude Code

When working in any repository, simply ask Claude:

```
"Analyze technical debt in this repository"
"Generate a technical debt register"
"Assess technical debt risks in the checkout flow"
"Summarize technical debt for leadership"
"What are the highest priority technical debt items to fix?"
```

### Via Slash Commands

```
/tech-debt              # Full analysis of current repository
/tech-debt summary      # Executive summary for leadership
/tech-debt register     # Detailed inventory for sprint planning
```

### Via Python API

```python
from agents.technical_debt_agent import TechnicalDebtAgent, analyze_technical_debt

# Quick analysis of ANY repository
report = analyze_technical_debt("/path/to/any/repo")
print(report.to_markdown())

# Analyze multiple repositories
repos = [
    "/home/ubuntu/repos/pandora-frontend",
    "/home/ubuntu/repos/pandora-backend",
    "/home/ubuntu/repos/pandora-cms"
]
for repo_path in repos:
    report = analyze_technical_debt(repo_path)
    print(f"\n=== {repo_path} ===")
    print(f"Total items: {report.summary.total_items}")
    print(f"High severity: {report.summary.by_severity.get('High', 0)}")

# Full control with SonarCloud integration
agent = TechnicalDebtAgent()
report = agent.analyze(
    repo_path="/path/to/repo",
    include_sonarcloud=True,
    sonar_project_key="my-project-key",
    sonar_branch="main"
)

# Generate specific outputs
summary = agent.generate_summary("/path/to/repo")
register = agent.generate_register("/path/to/repo")
```

### Via Task Manager

```python
from agents.task_manager_agent import TaskManagerAgent

tm = TaskManagerAgent()
result = tm.run_task("Analyze technical debt in this repository")
```

### Via MCP Tools (for integrations)

```python
# The agent exposes three MCP tools that can be called from Claude Desktop:
# - tech_debt_analyze: Full repository analysis
# - tech_debt_summary: Executive summary
# - tech_debt_register: Detailed debt inventory

# Each tool accepts a repo_path parameter to analyze any repository
```

## Best Use Cases

### 1. Sprint Planning & Backlog Grooming
Use the debt register to identify and prioritize technical debt items for upcoming sprints:
```
/tech-debt register
```
The tabular output makes it easy to copy items into Jira or your project management tool.

### 2. Architecture Reviews
Before major refactoring or architecture changes, get a comprehensive view of existing debt:
```python
report = agent.analyze("/path/to/repo")
# Focus on Architecture Debt category
for item in report.items:
    if item.category == DebtCategory.ARCHITECTURE:
        print(f"{item.title}: {item.recommendation}")
```

### 3. Executive Reporting
Generate leadership-friendly summaries for stakeholder updates:
```
/tech-debt summary
```
This produces a concise report with risk levels, key findings, and recommended actions.

### 4. PR Reviews & Code Quality Gates
Integrate debt analysis into your PR review workflow to catch new debt before it's merged:
```python
# In a PR review workflow
from agents.technical_debt_agent import TechnicalDebtAgent

agent = TechnicalDebtAgent()
report = agent.analyze(repo_path, include_sonarcloud=True)

if report.summary.by_severity.get("High", 0) > 0:
    print("WARNING: This PR introduces high-severity technical debt")
```

### 5. New Team Member Onboarding
Help new engineers understand the codebase's pain points:
```
"Analyze technical debt in this repository and explain the top 5 issues a new developer should know about"
```

### 6. Multi-Repository Analysis
Compare debt across multiple services in a microservices architecture:
```python
from agents.technical_debt_agent import analyze_technical_debt

repos = {
    "frontend": "/path/to/frontend",
    "api": "/path/to/api",
    "auth-service": "/path/to/auth",
}

for name, path in repos.items():
    report = analyze_technical_debt(path)
    print(f"{name}: {report.summary.total_items} items, "
          f"{report.summary.by_severity.get('High', 0)} high severity")
```

### 7. Pre-Release Quality Check
Before major releases, assess technical debt risk:
```python
report = agent.analyze("/path/to/repo")
if report.summary.by_severity.get("High", 0) > 10:
    print("RISK: High technical debt may impact release stability")
```

### 8. Continuous Improvement Tracking
Run periodic analyses to track debt reduction over time:
```python
# Weekly debt tracking
import json
from datetime import datetime

report = agent.analyze("/path/to/repo")
metrics = {
    "date": datetime.now().isoformat(),
    "total_items": report.summary.total_items,
    "high_severity": report.summary.by_severity.get("High", 0),
    "by_category": report.summary.by_category,
}
# Store metrics for trend analysis
with open("debt_metrics.jsonl", "a") as f:
    f.write(json.dumps(metrics) + "\n")
```

## Cross-Repository Usage Examples

### Analyzing a Frontend Repository
```python
report = analyze_technical_debt("/home/ubuntu/repos/pandora-frontend")
# Common findings: Large components, missing tests, deprecated React patterns
```

### Analyzing a Backend Repository
```python
report = analyze_technical_debt("/home/ubuntu/repos/pandora-api")
# Common findings: TODO comments, complex functions, outdated dependencies
```

### Analyzing a Monorepo
```python
# Analyze specific packages within a monorepo
report = analyze_technical_debt("/home/ubuntu/repos/monorepo/packages/core")
report = analyze_technical_debt("/home/ubuntu/repos/monorepo/packages/ui")
```

### With SonarCloud Integration
```python
# Set SONAR_TOKEN environment variable first
import os
os.environ["SONAR_TOKEN"] = "your-token-here"

agent = TechnicalDebtAgent()
report = agent.analyze(
    repo_path="/path/to/repo",
    include_sonarcloud=True,
    sonar_project_key="org_project-key",
    sonar_branch="main"
)
# Report now includes SonarCloud issues merged with static analysis
```

## Output Format

All outputs are structured and markdown-friendly with:

1. **Executive Summary** - High-level overview with risk assessment
2. **Technical Debt Breakdown** - Items grouped by category
3. **High-Risk Hotspots** - Files with highest debt concentration
4. **Recommendations** - Prioritized action items
5. **Suggested Next Actions** - Concrete steps to reduce debt

### Example Output

```markdown
# Technical Debt Analysis Report

**Repository:** pandora-group
**Total Debt Items:** 47
**Estimated Total Effort:** 2 weeks

## Executive Summary

| Severity | Count |
|----------|-------|
| High     | 8     |
| Medium   | 23    |
| Low      | 16    |

## High-Risk Hotspots

1. **src/components/checkout/CartSummary.tsx** - 5 issues (Risk Score: 12)
2. **src/utils/formatters.ts** - 4 issues (Risk Score: 9)

## Recommendations (Prioritized)

1. Address 8 high-severity items first, focusing on FIXME/BUG comments
2. Improve test coverage by adding unit tests for critical business logic
3. Audit and update dependencies, removing deprecated packages
```

## Integration Points

### MCP Tools
- `tech_debt_analyze` - Full repository analysis
- `tech_debt_summary` - Executive summary
- `tech_debt_register` - Detailed debt inventory

### Task Manager Workflows
The agent can be invoked as part of:
- PR Review workflows
- Sprint Review workflows
- Architecture Review workflows

### Slash Commands
- `/tech-debt` - Full analysis
- `/tech-debt summary` - Executive summary for leadership
- `/tech-debt register` - Detailed inventory for tracking

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SONAR_TOKEN` | SonarCloud API token | No (optional) |

### Repo Profile Support

If `.claude/repo-profile.json` exists, the agent uses it for:
- Repository name identification
- Custom analysis thresholds
- Project-specific conventions

## Limitations

- **READ-ONLY**: This agent does not modify any code
- **Static Analysis**: Does not execute code or run tests
- **Heuristic-based**: Complexity and size estimates are approximations
- **No Runtime Analysis**: Cannot detect runtime performance issues

## Quality Standards

Output adheres to Staff/Principal Engineer analysis quality:
- No hallucinated code references
- Actionable, realistic recommendations
- Clear separation between facts and suggestions
- Specific file and line references where applicable
