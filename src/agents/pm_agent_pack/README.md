# PM Agent Pack

A collection of AI agents designed specifically for **Product Managers**, **Technical Program Managers**, and **Engineering Managers** to use via Claude Desktop. These agents help automate common PM tasks without requiring any coding or infrastructure setup.

## What's Included

| Agent | Purpose | Best For |
|-------|---------|----------|
| **PRD to Jira Breakdown** | Convert PRDs into Jira epics, stories, and acceptance criteria | Sprint planning, backlog grooming |
| **Stakeholder Update / Exec Summary** | Transform sprint data into executive-friendly updates | Weekly updates, steering committees |
| **Roadmap Review & Risk** | Critique roadmaps and OKRs with risk assessment | Quarterly planning, roadmap reviews |

## Who Should Use This

- **Product Managers** looking to streamline documentation and communication
- **Technical Program Managers** managing cross-team initiatives
- **Engineering Managers** preparing updates for leadership
- **Product Operations** teams standardizing PM workflows
- Anyone who needs to translate technical work into business language

## How to Use with Claude Desktop

### Step 1: Open Claude Desktop

Launch Claude Desktop on your computer. If you don't have it installed, download it from [claude.ai](https://claude.ai).

### Step 2: Set Up the System Prompt

Each agent has a specific system prompt that tells Claude how to behave. Copy the system prompt for your chosen agent and paste it into Claude Desktop's system prompt field (usually found in settings or at the start of a new conversation).

### Step 3: Paste Your Content

Simply paste your PRD, sprint data, or roadmap into the chat. Claude will process it according to the agent's instructions and produce formatted output.

### Step 4: Copy the Output

The output is formatted as Jira-ready markdown that you can copy directly into:
- Jira tickets
- Confluence pages
- Slack messages
- Email updates
- Presentation slides

---

## Agent 1: PRD to Jira Breakdown

### Purpose
Converts Product Requirements Documents (PRDs) or Confluence content into structured Jira work items.

### What It Produces
- **Epics** with business context
- **User Stories** with proper formatting
- **Acceptance Criteria** in Gherkin format (Given/When/Then)
- **Dependencies** (technical, cross-team, external)
- **Risks** with mitigation suggestions

### Example Prompt

Copy this into Claude Desktop:

```
You are a Senior Product Manager with expertise in Agile methodologies and Jira best practices. Your role is to convert Product Requirements Documents (PRDs) or Confluence content into well-structured Jira work items.

[Full system prompt available in prd_to_jira_agent.py]
```

### Example Input

```
# Product Requirements: Customer Wishlist Feature

## Overview
We need to implement a wishlist feature that allows customers to save products 
they're interested in for later purchase.

## User Needs
- Customers want to save products they like but aren't ready to buy
- Customers want to easily find their saved items later
- Customers want to share their wishlist with friends and family

## Functional Requirements
1. Add to Wishlist button on product pages
2. Wishlist page showing all saved items
3. Remove items from wishlist
4. Move items from wishlist to cart
5. Share wishlist via link or email
```

### Example Output

The agent will produce:
- Epic: Customer Wishlist with business value summary
- 5 User Stories with acceptance criteria in Gherkin format
- Dependency map (technical, cross-team, sequential)
- Risk register with mitigations
- Open questions for clarification

---

## Agent 2: Stakeholder Update / Exec Summary

### Purpose
Transforms sprint data, Jira summaries, or project updates into executive-friendly communications.

### What It Produces
- **TL;DR** summary (2-3 sentences)
- **Progress Highlights** with business impact
- **Metrics Dashboard** in table format
- **Risks & Mitigations** with RAG status
- **Decisions Required** with options and recommendations
- **Next Steps** and upcoming milestones

### Example Prompt

Copy this into Claude Desktop:

```
You are a Senior Product Manager with expertise in executive communication. 
Your role is to transform technical sprint data, Jira summaries, or project 
updates into clear, concise executive summaries suitable for Directors and VPs.

[Full system prompt available in exec_summary_agent.py]
```

### Example Input

```
Sprint 47 Summary - Checkout Team

Completed Stories:
- CHKOUT-1234: Implement Apple Pay integration (8 points)
- CHKOUT-1235: Fix cart abandonment tracking bug (3 points)
- CHKOUT-1236: Add gift message field to checkout (5 points)

Carried Over:
- CHKOUT-1238: PayPal Express checkout (8 points) - blocked by PayPal API access

Sprint Metrics:
- Velocity: 21 points (target was 30)
- Bug count: 3 new, 5 resolved

Team Notes:
- Lost 2 days to production incident
- PayPal integration blocked - waiting on finance approval
```

### Example Output

The agent will produce:
- Overall status with RAG indicators
- Business impact of completed work
- Key metrics in scannable table format
- Decision request with options and recommendation
- Clear next steps

---

## Agent 3: Roadmap Review & Risk

### Purpose
Provides constructive critique of product roadmaps and OKRs to identify risks and improvement opportunities.

### What It Produces
- **Executive Summary** with overall assessment
- **Timeline Analysis** with realism score
- **Dependency Map** (identified and missing)
- **Risk Register** with impact/likelihood matrix
- **Improvement Recommendations** (quick wins, strategic changes)

### Example Prompt

Copy this into Claude Desktop:

```
You are a Senior Product Strategy Consultant with 15+ years of experience 
reviewing product roadmaps across various industries. Your role is to provide 
constructive, actionable critique of product roadmaps and OKRs.

[Full system prompt available in roadmap_review_agent.py]
```

### Example Input

```
Q1-Q2 2024 Product Roadmap - E-commerce Platform

## Team Context
- 2 backend engineers, 3 frontend engineers, 1 QA
- New PM started last month

## Q1 Initiatives
- Complete checkout redesign
- Launch Apple Pay integration
- Migrate 50% of traffic to new platform
- Launch guest checkout
- Begin mobile app development

## OKRs
O1: Increase mobile conversion by 40%
O2: Expand to international markets
O3: Improve customer retention
```

### Example Output

The agent will produce:
- Overall assessment (Strong/Moderate/Needs Work)
- Timeline realism score with specific concerns
- Missing dependencies identified
- Risk matrix with prioritized mitigations
- Recommended revised roadmap

---

## Tips for Best Results

### Be Specific
The more detail you provide, the better the output. Include:
- Team size and composition
- Timeline constraints
- Technical context
- Business priorities

### Iterate
Don't expect perfection on the first try. Ask follow-up questions like:
- "Can you add more detail to the acceptance criteria for Story X?"
- "What if we had 2 more engineers?"
- "Focus more on the mobile aspects"

### Customize
Feel free to modify the system prompts to match your organization's:
- Terminology and jargon
- Template formats
- Specific tools (Jira, Linear, Asana)
- Communication style

---

## Known Limitations

1. **No Real Jira Integration**: These agents produce markdown output that you copy into Jira manually. They don't create tickets automatically.

2. **No Date Awareness**: The agents don't know today's date and won't generate specific dates. Use placeholders like [DATE] and fill in manually.

3. **No Historical Context**: Each conversation starts fresh. The agents don't remember previous roadmaps or sprints.

4. **Estimation is Suggestive**: Story point estimates are suggestions based on typical complexity. Always validate with your team.

5. **No Proprietary Data**: Don't paste sensitive information. These agents run through Claude's standard infrastructure.

---

## Feedback & Support

These agents are part of the PG AI Squad (pnd-agents) project. For questions, feedback, or feature requests:

- **Slack**: #pg-ai-squad
- **Email**: tech@pandora.net
- **GitHub**: [shvee-pandora/pnd-agents](https://github.com/shvee-pandora/pnd-agents)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release with 3 agents |

---

*Built with care by the PG AI Squad for Product Managers everywhere.*
