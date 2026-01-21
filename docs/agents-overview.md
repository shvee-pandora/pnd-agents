# Agents Overview

This document provides a comprehensive overview of all available agents in the Pandora AI Squad system, their capabilities, and links to detailed documentation.

## Agent Inventory

| Category | Universal | Platform-Specific |
|----------|-----------|-------------------|
| Orchestration | 1 | 0 |
| Development | 3 | 0 |
| Quality/Validation | 6 | 0 |
| Performance | 2 | 0 |
| Product Management | 3 | 0 |
| Analytics | 1 | 0 |
| CMS | 0 | 2 |
| Commerce | 0 | 1 |
| **Total** | **16** | **3** |

## Universal Agents (Work in Any Repository)

| Agent | Category | Purpose | Key Capabilities |
|-------|----------|---------|-----------------|
| [Task Manager](#task-manager-agent) | Orchestration | Multi-agent workflow coordination | Task decomposition, agent routing, output merging |
| [Frontend Engineer](#frontend-engineer-agent) | Development | React/Next.js component development | Component generation, Storybook stories, accessibility |
| [Backend](#backend-agent) | Development | API and server development | API routes, Server Components, mock services |
| [Figma Reader](#figma-reader-agent) | Development | Figma design extraction | Design tokens, metadata, variants extraction |
| [Code Review](#code-review-agent) | Quality | Universal code standards validation | Context7 integration, Pandora standards, any JS framework |
| [Unit Test](#unit-test-agent) | Quality | Test generation | 100% coverage target, jest-axe, edge cases |
| [Sonar Validation](#sonar-validation-agent) | Quality | Quality gate enforcement | 0 errors, 0 duplication, coverage validation |
| [QA](#qa-agent) | Quality | E2E and integration testing | Playwright, acceptance criteria validation |
| [PR Review](#pr-review-agent) | Quality | Pull request review automation | Azure DevOps, GitHub integration |
| [Technical Debt](#technical-debt-agent) | Quality | Tech debt identification | Debt classification, prioritization |
| [Performance](#performance-agent) | Performance | Performance analysis | HAR analysis, Core Web Vitals, caching |
| [Broken Experience Detector](#broken-experience-detector-agent) | Performance | UX issue detection | Broken links, UI issues, accessibility problems |
| [PRD to Jira](#prd-to-jira-agent) | Product Management | PRD conversion | Converts PRDs to JIRA work items |
| [Executive Summary](#executive-summary-agent) | Product Management | Stakeholder summaries | Creates executive summaries |
| [Roadmap Review](#roadmap-review-agent) | Product Management | Roadmap analysis | Critiques roadmaps and OKRs |
| [Analytics](#analytics-agent) | Analytics | Task tracking and reporting | JIRA integration, metrics, dashboards |

## Platform-Specific Agents (Pandora Infrastructure)

| Agent | Category | Dependency |
|-------|----------|------------|
| [Commerce](#commerce-agent) | Commerce | Requires Pandora's SFCC instance |
| [Amplience CMS](#amplience-cms-agent) | CMS | Requires Pandora's Amplience hub |
| [Amplience Placement](#amplience-placement-agent) | CMS | Maps to Pandora's Amplience modules |

## Detailed Agent Documentation

### Task Manager Agent

The Task Manager Agent serves as the orchestrator for multi-agent workflows, decomposing complex tasks into subtasks and routing them to specialist agents.

**Capabilities:**
- Task decomposition into subtasks
- Agent assignment based on task type
- Output merging from multiple agents
- Workflow pipeline management

**Commands:**
- `task-decompose` - Break down complex tasks
- `task-assign` - Route tasks to appropriate agents
- `task-merge` - Combine outputs from multiple agents

**Documentation:** [agents/task_manager_agent/agents/task-manager-agent.md](../src/agents/task_manager_agent/agents/task-manager-agent.md)

---

### Frontend Engineer Agent

The Frontend Engineer Agent generates React/Next.js components following Pandora coding standards, including Storybook stories and accessibility validation.

**Capabilities:**
- React/Next.js component generation
- Storybook story creation
- Accessibility validation (WCAG 2.1 AA)
- Design token integration
- Atomic Design patterns

**Commands:**
- `component-generate` - Generate React components
- `story-create` - Create Storybook stories
- `accessibility-validate` - Validate accessibility compliance

**Documentation:** [agents/frontend/agents/frontend-engineer-agent.md](../src/agents/frontend/agents/frontend-engineer-agent.md)

---

### Figma Reader Agent

The Figma Reader Agent extracts design metadata, tokens, and component specifications from Figma files via the Figma API.

**Capabilities:**
- Design metadata extraction
- Design token extraction (colors, typography, spacing)
- Component variant detection
- Frame and layer analysis

**Commands:**
- `figma-read` - Extract design data from Figma URL

**Documentation:** [agents/figma_reader_agent/agents/figma-reader-agent.md](../src/agents/figma_reader_agent/agents/figma-reader-agent.md)

**Required Environment Variable:** `FIGMA_ACCESS_TOKEN`

---

### Amplience CMS Agent

The Amplience CMS Agent creates and manages content types, JSON schemas, and payload examples for the Amplience CMS platform.

**Capabilities:**
- Content type creation
- JSON schema generation
- Payload example generation
- Content scaffolding

**Commands:**
- `content-type-create` - Create new content types
- `schema-generate` - Generate JSON schemas
- `payload-example` - Create example payloads

**Documentation:** [agents/amplience/agents/amplience-cms-agent.md](../src/agents/amplience/agents/amplience-cms-agent.md)

---

### Code Review Agent

The Code Review Agent is a **universal** agent that validates JavaScript/TypeScript code against coding standards for any framework. It uses Context7 MCP (when available) to fetch the latest best practices for the detected framework, with Pandora standards always taking precedence.

**Standards Hierarchy:**
1. **Pandora Standards** (from `coding_standards.py`) - ALWAYS enforced, highest priority
2. **Context7 Framework Standards** - Latest best practices for detected framework (optional)
3. **Universal JS/TS Standards** - General best practices (fallback)

**Pandora Standards Enforced:**
- Use `type` over `interface` for object types
- No TODO comments in production code
- Prefer `for...of` over `forEach`
- Use `.at(-n)` for negative indexing
- Avoid negated conditions with else blocks
- Use `globalThis` instead of `global`
- Compare with `undefined` directly
- Use nullish coalescing (`??`) over logical OR (`||`)
- Use optional chaining (`?.`)

**Supported Frameworks (via Context7):**
- React, Vue, Angular, Svelte
- Next.js, Nuxt, SvelteKit
- Node.js, Express, Fastify
- Any JavaScript/TypeScript library

**Commands:**
- `review-code` - Review code for standards compliance
- `validate-standards` - Validate against specific standards
- `pr-comment` - Generate PR review comments

**Documentation:** [agents/code_review/agents/code-review-agent.md](../src/agents/code_review/agents/code-review-agent.md)

---

### Unit Test Agent

The Unit Test Agent generates comprehensive unit tests targeting 100% code coverage, including accessibility tests using jest-axe.

**Capabilities:**
- Unit test generation
- 100% coverage targeting
- Edge case identification
- Accessibility testing with jest-axe
- Mock generation

**Documentation:** Located in `src/agents/unit_test_agent/`

---

### Sonar Validation Agent

The Sonar Validation Agent enforces SonarCloud quality gates, ensuring zero errors, zero duplication, and 100% test coverage.

**Capabilities:**
- SonarCloud quality gate validation
- Bug and vulnerability detection
- Code duplication analysis
- Coverage verification
- Fix plan generation

**Quality Gates:**
- 0 errors (bugs, vulnerabilities)
- 0 code duplication
- 100% test coverage

**Documentation:** Located in `src/agents/sonar_validation_agent/`

**Optional Environment Variable:** `SONAR_TOKEN`

---

### Performance Agent

The Performance Agent analyzes HAR files and provides optimization recommendations for Core Web Vitals and overall performance.

**Capabilities:**
- HAR file analysis
- Slow endpoint identification
- Caching recommendations
- CDN optimization suggestions
- Core Web Vitals metrics

**Commands:**
- `har-analyze` - Analyze HAR files
- `performance-report` - Generate performance reports
- `optimization-suggest` - Suggest optimizations

**Documentation:** [agents/performance/agents/performance-agent.md](../src/agents/performance/agents/performance-agent.md)

---

### QA Agent

The QA Agent generates E2E tests, integration tests, and validates acceptance criteria using Playwright and other testing frameworks.

**Capabilities:**
- E2E test generation (Playwright)
- Integration test creation
- Acceptance criteria validation
- Test coverage reporting

**Commands:**
- `test-generate` - Generate tests
- `coverage-report` - Generate coverage reports
- `acceptance-validate` - Validate acceptance criteria

**Documentation:** [agents/qa_agent/agents/qa-agent.md](../src/agents/qa_agent/agents/qa-agent.md)

---

### Backend Agent

The Backend Agent creates API routes, Server Components, and mock services following Next.js App Router patterns.

**Capabilities:**
- API route creation
- Server Component implementation
- Mock API service generation
- DOL/OMS integration

**Commands:**
- `api-route-create` - Create API routes
- `server-component-create` - Create Server Components
- `mock-api-create` - Create mock API services

**Documentation:** [agents/backend/agents/backend-agent.md](../src/agents/backend/agents/backend-agent.md)

---

### Commerce Agent

The Commerce Agent provides AI-powered product search and cart preparation capabilities for the Pandora e-commerce platform.

**Capabilities:**
- Natural language product search
- Price and attribute filtering
- Cart data preparation
- Product recommendations

**Documentation:** Located in `src/agents/commerce_agent/`

**Optional Environment Variables:**
- `SFCC_OCAPI_INSTANCE`
- `SFCC_CLIENT_ID`
- `SFCC_SITE_ID`

---

### Analytics & Reporting Agent

The Analytics & Reporting Agent tracks task metrics, integrates with JIRA, and generates reports on agent performance.

**Capabilities:**
- Task event tracking (started, completed, failed)
- JIRA integration (comments, custom fields)
- Metrics persistence (JSON logs)
- Report generation (JSON, Markdown, JIRA dashboard)
- MCP integration for Claude

**MCP Commands:**
- `track_task_start` - Record task start
- `track_task_end` - Record task completion with metrics
- `update_jira_task` - Update JIRA with AI metrics
- `generate_agent_report` - Generate performance reports
- `list_analytics` - List tracked analytics

**Metrics Tracked:**
- Duration, iterations, errors
- Effectiveness score
- Confidence score
- Human review requirements

**Documentation:** [agents/analytics_agent/](../src/agents/analytics_agent/)

**Configuration Files:**
- `config/analytics.config.json` - Analytics settings
- `config/jira.config.json` - JIRA credentials

---

### Broken Experience Detector Agent

The Broken Experience Detector Agent identifies UX issues, broken links, and accessibility problems in web applications.

**Capabilities:**
- Broken link detection
- UI issue identification
- Accessibility problem detection
- User experience analysis

**Documentation:** [agents/broken_experience_detector_agent/agents/broken-experience-detector-agent.md](../src/agents/broken_experience_detector_agent/agents/broken-experience-detector-agent.md)

---

### PR Review Agent

The PR Review Agent automates pull request reviews on Azure DevOps and GitHub, providing automated code analysis and feedback.

**Capabilities:**
- Azure DevOps PR integration
- GitHub PR integration
- Automated code analysis
- Review comment generation
- Tech stack detection

**Documentation:** Located in `src/agents/pr_review_agent/`

**Required Environment Variables:**
- `AZURE_DEVOPS_PAT` - Azure DevOps Personal Access Token
- `AZURE_DEVOPS_ORG` - Azure DevOps organization name
- `AZURE_DEVOPS_PROJECT` - Azure DevOps project name

---

### Technical Debt Agent

The Technical Debt Agent identifies, classifies, and prioritizes technical debt in codebases.

**Capabilities:**
- Tech debt identification
- Debt classification (code, architecture, test, documentation)
- Prioritization based on impact
- Remediation recommendations

**Documentation:** Located in `src/agents/technical_debt_agent/`

---

### PRD to Jira Agent

The PRD to Jira Agent converts Product Requirements Documents (PRDs) into structured JIRA work items.

**Capabilities:**
- PRD parsing and analysis
- Epic, Story, and Task creation
- Acceptance criteria extraction
- JIRA integration

**Documentation:** Located in `src/agents/pm_agent_pack/prd_to_jira_agent.py`

**Required Environment Variables:**
- `JIRA_BASE_URL` - JIRA instance URL
- `JIRA_EMAIL` - JIRA user email
- `JIRA_API_TOKEN` - JIRA API token

---

### Executive Summary Agent

The Executive Summary Agent creates stakeholder-friendly summaries of technical work and project status.

**Capabilities:**
- Technical summary generation
- Stakeholder-appropriate language
- Key metrics highlighting
- Risk and blocker identification

**Documentation:** Located in `src/agents/pm_agent_pack/exec_summary_agent.py`

---

### Roadmap Review Agent

The Roadmap Review Agent critiques product roadmaps and OKRs for completeness and alignment.

**Capabilities:**
- Roadmap analysis
- OKR validation
- Gap identification
- Alignment recommendations

**Documentation:** Located in `src/agents/pm_agent_pack/roadmap_review_agent.py`

---

### Amplience Placement Agent

The Amplience Placement Agent maps content to Pandora's Amplience module placements.

**Capabilities:**
- Module placement mapping
- Content slot configuration
- Placement validation
- Pandora-specific module support

**Documentation:** Located in `src/agents/amplience_placement_agent/`

**Required Environment Variables:**
- `AMPLIENCE_HUB_NAME` - Amplience hub name
- `AMPLIENCE_BASE_URL` - Amplience base URL

---

## Workflow Pipelines

The Task Manager automatically routes tasks through agent pipelines based on task type:

| Task Type | Detection Keywords | Pipeline |
|-----------|-------------------|----------|
| Figma | figma, design, frame | Figma Reader -> Frontend -> Code Review -> Unit Test -> Sonar -> Performance |
| Frontend | react, component, tsx | Frontend -> Code Review -> Unit Test -> Sonar -> Performance |
| Backend | api, endpoint, server | Backend -> Code Review -> Unit Test -> Sonar |
| Amplience | content type, cms, schema | Amplience -> Frontend -> Code Review -> Unit Test -> Sonar |
| Unit Test | unit tests, coverage, jest | Unit Test -> Sonar |
| Sonar | sonar, quality gate | Sonar -> Code Review |
| QA | tests, automation, playwright | QA -> Unit Test -> Sonar |
| Performance | performance, har, metrics | Performance |

## Claude Integration

All agents are available through Claude Desktop/Code via MCP (Model Context Protocol). See the [Setup Guide](./setup.md) for configuration instructions.

## Related Documentation

- [Setup Guide](./setup.md) - Installation and configuration
- [Architecture](./architecture.md) - System architecture and design
- [How Agents Work](./how-agents-work.md) - Low-level agent internals
- [Quick Reference](./quick-reference.md) - Quick lookup card
- [Examples](../examples/) - Usage examples

---

**Last Updated**: January 2026  
**Version**: 2.0.0  
**Maintained by**: Pandora Group
