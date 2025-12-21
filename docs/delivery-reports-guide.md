# Delivery Reports Guide

This guide explains the three delivery report tools available in pnd-agents and when to use each one.

## Overview: Three Tools for Different Needs

| Tool | Best For | Key Output |
|------|----------|------------|
| `sprint_value_delivered_report` | Single board, single sprint | Value delivered with Initiative/OKR linking |
| `delivery_report_generate` | Velocity trends over time | Multi-sprint velocity charts |
| `multi_board_value_delivered_report` | Cross-team comparison | Multi-board value reports with comparison |

---

## Tool 1: sprint_value_delivered_report

**Purpose:** Generate a detailed end-of-sprint value delivered report for a single board.

**Best for:**
- Sprint retrospectives
- Single team reporting
- Initiative/OKR progress tracking
- AI contribution analysis for one team

**What it includes:**
- Executive summary (story points, delivery rate)
- Reliability metrics (commitment vs delivery, carryover rate, bug fix rate)
- Value delivered by Initiative/OKR (traces Story to Epic to Initiative)
- Team breakdown by project
- AI contribution metrics (AI-assisted issues, commits, time saved)
- Key outcomes summary

**How to use:**

Via Claude Code:
```
Use sprint_value_delivered_report with board_id: 847
```

With specific sprint:
```
Use sprint_value_delivered_report with board_id: 847 and sprint_id: 12345
```

**Example output:**
```
Sprint Value Delivered Report: FIND Sprint_2025_25
Period: 2025-12-02 to 2025-12-15

Executive Summary
| Metric | Value |
|--------|-------|
| Total Story Points | 45 |
| Delivered Story Points | 38 |
| Delivery Rate | 84.4% |

Reliability Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Commitment | 45 SP | - |
| Delivered | 38 SP | On Track |
| Carryover | 7 SP (3 issues) | Low |
| Bug Fix Rate | 100% (2/2) | Good |

Value Delivered by Initiative/OKR
| Initiative | Delivered SP | Total SP | Completion |
|------------|--------------|----------|------------|
| Gemini Integration | 15 | 15 | 100% |
| Search Optimization | 12 | 18 | 67% |
```

---

## Tool 2: delivery_report_generate

**Purpose:** Generate velocity reports across multiple sprints to track trends over time.

**Best for:**
- Quarterly planning
- Velocity trend analysis
- Capacity planning
- Historical performance review

**What it includes:**
- Sprint-by-sprint velocity breakdown
- Committed vs delivered story points per sprint
- Carryover trends
- ASCII velocity charts
- Multi-board support for trend comparison

**How to use:**

Via Claude Code:
```
Generate a delivery report for board 847 with the last 3 closed sprints
```

Multiple boards:
```
Generate a delivery report for boards 847 and 852 with the last 5 sprints
```

**Example output:**
```
Delivery Report: Board 847
Sprints Analyzed: 3

Sprint Velocity Breakdown:
| Sprint | Committed | Delivered | Carryover | Rate |
|--------|-----------|-----------|-----------|------|
| Sprint_2025_23 | 42 | 38 | 4 | 90% |
| Sprint_2025_24 | 45 | 40 | 5 | 89% |
| Sprint_2025_25 | 45 | 38 | 7 | 84% |

Velocity Trend Chart:
Sprint_2025_23 |=====================================| 38 SP
Sprint_2025_24 |========================================| 40 SP
Sprint_2025_25 |=====================================| 38 SP
```

---

## Tool 3: multi_board_value_delivered_report

**Purpose:** Generate comprehensive value delivered reports for multiple boards with cross-board comparison.

**Best for:**
- Delivery managers overseeing multiple teams
- Online vs Retail comparison
- Cross-team performance reviews
- Executive reporting
- Sprint demos with multiple teams

**What it includes:**
- Full value delivered report for EACH board (same as Tool 1)
- Cross-board comparison summary table
- AI contribution comparison across boards
- ASCII charts comparing:
  - Delivery rates
  - Story points delivered
  - Carryover

**How to use:**

Via Claude Code - Online teams:
```
Use multi_board_value_delivered_report with board_configs:
- {board_id: 549, name: "Decide"}
- {board_id: 795, name: "Inspire"}
- {board_id: 847, name: "Find"}
- {board_id: 852, name: "Delivery"}
```

Via Claude Code - All teams (Online + Retail):
```
Use multi_board_value_delivered_report with board_configs:
- {board_id: 549, name: "Decide"}
- {board_id: 795, name: "Inspire"}
- {board_id: 847, name: "Find"}
- {board_id: 852, name: "Delivery"}
- {board_id: 995, name: "DOL"}
- {board_id: 4121, name: "Marketplace"}
```

**Example output:**
```
# Multi-Board Value Delivered Report

Boards Analyzed: 4
Generated: 2025-12-17 20:00

---

# Section 1: Decide

Sprint: Decide Sprint_2025_25
Period: 2025-12-02 to 2025-12-15

## Executive Summary
| Metric | Value |
|--------|-------|
| Total Story Points | 32 |
| Delivered Story Points | 28 |
| Delivery Rate | 87.5% |

[... full report for Decide ...]

---

# Section 2: Inspire

[... full report for Inspire ...]

---

# Section 3: Find

[... full report for Find ...]

---

# Section 4: Delivery

[... full report for Delivery ...]

---

# Section 5: Cross-Board Comparison

## Summary Comparison Table
| Board | Sprint | Committed SP | Delivered SP | Delivery Rate | Carryover |
|-------|--------|--------------|--------------|---------------|-----------|
| Decide | Sprint_2025_25 | 32 | 28 | 87.5% | 4 SP |
| Inspire | Sprint_2025_25 | 40 | 35 | 87.5% | 5 SP |
| Find | Sprint_2025_25 | 45 | 38 | 84.4% | 7 SP |
| Delivery | Sprint_2025_25 | 38 | 34 | 89.5% | 4 SP |

## Delivery Rate Comparison Chart
```
Decide               |*********************************   | 87.5% [OK]
Inspire              |*********************************   | 87.5% [OK]
Find                 |*********************************   | 84.4% [OK]
Delivery             |***********************************  | 89.5% [OK]
```

## Story Points Delivered Chart
```
Decide               |============================        | 28 SP
Inspire              |===================================  | 35 SP
Find                 |======================================| 38 SP
Delivery             |==================================   | 34 SP
```

## Carryover Comparison Chart
```
Decide               |################                    | 4 SP [OK]
Inspire              |####################                | 5 SP [OK]
Find                 |############################        | 7 SP [OK]
Delivery             |################                    | 4 SP [OK]
```
```

---

## Decision Matrix: Which Tool Should I Use?

| Scenario | Recommended Tool |
|----------|------------------|
| "I need a sprint report for my team" | `sprint_value_delivered_report` |
| "I want to see our velocity trend over the last quarter" | `delivery_report_generate` |
| "I need to compare all Online teams" | `multi_board_value_delivered_report` |
| "I'm preparing for sprint retrospective" | `sprint_value_delivered_report` |
| "I need to report to leadership on all teams" | `multi_board_value_delivered_report` |
| "I want to track Initiative/OKR progress" | `sprint_value_delivered_report` or `multi_board_value_delivered_report` |
| "I need to see carryover trends" | `delivery_report_generate` |
| "I want AI contribution metrics" | `sprint_value_delivered_report` or `multi_board_value_delivered_report` |

---

## Board Reference

### Online Teams
| Board Name | Board ID |
|------------|----------|
| Decide | 549 |
| Inspire | 795 |
| Find | 847 |
| Delivery | 852 |

### Retail Teams
| Board Name | Board ID |
|------------|----------|
| DOL | 995 |
| Marketplace | 4121 |

---

## Environment Setup

All three tools require JIRA access. Set these environment variables:

```bash
export JIRA_BASE_URL="https://pandoradigital.atlassian.net"
export JIRA_EMAIL="your-email@pandora.net"
export JIRA_API_TOKEN="your-jira-api-token"
```

For AI contribution metrics, also set:
```bash
export AZURE_DEVOPS_PAT="your-azure-devops-pat"
```

---

## Troubleshooting

**"No active sprint found"**
- The board may not have an active sprint
- Use a specific `sprint_id` parameter instead

**"AI metrics not showing"**
- Ensure `AZURE_DEVOPS_PAT` is set
- AI metrics require Azure DevOps access to identify AI commits

**"Tool not found in Claude"**
- Pull the latest pnd-agents code: `git pull origin main`
- Restart Claude Code/Desktop

---

## Related Documentation

- [Setup Guide](setup.md) - Initial installation and configuration
- [Claude Usage](claude-usage.md) - Using agents with Claude
- [Quick Reference](quick-reference.md) - All available agents

---

**Version**: 1.0.0 | **Last Updated**: December 2025
