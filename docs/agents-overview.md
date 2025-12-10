# Agents Overview

This document provides a comprehensive overview of all available agents in the PG AI Squad system, their capabilities, and links to detailed documentation.

## Agent Summary

| Agent | Category | Purpose | Key Capabilities |
|-------|----------|---------|-----------------|
| [Task Manager](#task-manager-agent) | Orchestration | Multi-agent workflow coordination | Task decomposition, agent routing, output merging |
| [Frontend Engineer](#frontend-engineer-agent) | Development | React/Next.js component development | Component generation, Storybook stories, accessibility |
| [Figma Reader](#figma-reader-agent) | Design | Figma design extraction | Design tokens, metadata, variants extraction |
| [Amplience CMS](#amplience-cms-agent) | CMS | Content type management | JSON schemas, content types, payload examples |
| [Code Review](#code-review-agent) | Quality | Code standards validation | Pandora standards, TypeScript, accessibility |
| [Unit Test](#unit-test-agent) | Testing | Test generation | 100% coverage target, jest-axe, edge cases |
| [Sonar Validation](#sonar-validation-agent) | Quality | Quality gate enforcement | 0 errors, 0 duplication, coverage validation |
| [Performance](#performance-agent) | Optimization | Performance analysis | HAR analysis, Core Web Vitals, caching |
| [QA](#qa-agent) | Testing | E2E and integration testing | Playwright, acceptance criteria validation |
| [Backend](#backend-agent) | Development | API and server development | API routes, Server Components, mock services |
| [Commerce](#commerce-agent) | Commerce | Product discovery | AI-powered search, cart preparation |
| [Analytics & Reporting](#analytics--reporting-agent) | Analytics | Task tracking and reporting | JIRA integration, metrics, dashboards |
| [Broken Experience Detector](#broken-experience-detector-agent) | Quality | UX issue detection | Broken links, UI issues, accessibility problems |

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

**Documentation:** [agents/task_manager/agents/task-manager-agent.md](../agents/task_manager/agents/task-manager-agent.md)

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

**Documentation:** [agents/frontend/agents/frontend-engineer-agent.md](../agents/frontend/agents/frontend-engineer-agent.md)

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

**Documentation:** [agents/figma_reader/agents/figma-reader-agent.md](../agents/figma_reader/agents/figma-reader-agent.md)

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

**Documentation:** [agents/amplience/agents/amplience-cms-agent.md](../agents/amplience/agents/amplience-cms-agent.md)

---

### Code Review Agent

The Code Review Agent validates generated code against Pandora coding standards, including TypeScript rules, accessibility, and architectural patterns.

**Capabilities:**
- Pandora coding standards validation
- TypeScript strict mode compliance
- Accessibility review
- INS-2509 technical architecture validation
- Atomic design pattern verification

**Commands:**
- `review-code` - Review code for standards compliance
- `validate-standards` - Validate against specific standards
- `pr-comment` - Generate PR review comments

**Documentation:** [agents/code_review/agents/code-review-agent.md](../agents/code_review/agents/code-review-agent.md)

---

### Unit Test Agent

The Unit Test Agent generates comprehensive unit tests targeting 100% code coverage, including accessibility tests using jest-axe.

**Capabilities:**
- Unit test generation
- 100% coverage targeting
- Edge case identification
- Accessibility testing with jest-axe
- Mock generation

**Documentation:** Located in `agents/unit_test_agent.py`

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

**Documentation:** Located in `agents/sonar_validation_agent.py`

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

**Documentation:** [agents/performance/agents/performance-agent.md](../agents/performance/agents/performance-agent.md)

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

**Documentation:** [agents/qa/agents/qa-agent.md](../agents/qa/agents/qa-agent.md)

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

**Documentation:** [agents/backend/agents/backend-agent.md](../agents/backend/agents/backend-agent.md)

---

### Commerce Agent

The Commerce Agent provides AI-powered product search and cart preparation capabilities for the Pandora e-commerce platform.

**Capabilities:**
- Natural language product search
- Price and attribute filtering
- Cart data preparation
- Product recommendations

**Documentation:** Located in `agents/commerce_agent.py`

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

**Documentation:** [agents/analytics_agent/](../agents/analytics_agent/)

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

**Documentation:** [agents/broken_experience_detector/agents/broken-experience-detector-agent.md](../agents/broken_experience_detector/agents/broken-experience-detector-agent.md)

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

All agents are available through Claude Desktop/Code via MCP (Model Context Protocol). See the [Claude Usage Guide](./claude-usage.md) for configuration instructions.

## Related Documentation

- [Setup Guide](./setup.md) - Installation and configuration
- [Architecture](./architecture.md) - System architecture and design
- [Quick Reference](./quick-reference.md) - Quick lookup card
- [Examples](../examples/) - Usage examples

---

**Last Updated**: December 2025  
**Version**: 1.0.0  
**Maintained by**: Pandora Group
