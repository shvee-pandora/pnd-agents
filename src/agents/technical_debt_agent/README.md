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

### Via Claude Desktop / Claude Code

```
"Analyze technical debt in this repository"
"Generate a technical debt register"
"Assess technical debt risks in the checkout flow"
"Summarize technical debt for leadership"
```

### Via Slash Commands

```
/tech-debt              # Full analysis
/tech-debt summary      # Executive summary
/tech-debt register     # Detailed inventory
```

### Via Python API

```python
from agents.technical_debt_agent import TechnicalDebtAgent, analyze_technical_debt

# Quick analysis
report = analyze_technical_debt("/path/to/repo")
print(report.to_markdown())

# Full control
agent = TechnicalDebtAgent()
report = agent.analyze(
    repo_path="/path/to/repo",
    include_sonarcloud=True,
    sonar_project_key="my-project-key"
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
