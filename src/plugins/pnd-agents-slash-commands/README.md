# PND Agents Slash Commands Plugin

A comprehensive Claude Desktop plugin that provides instant access to all PND Agents via slash commands. No MCP server setup required - just install and use.

## Installation

### Step 1: Locate Your Claude Desktop Plugins Folder

**macOS:**
```
~/Library/Application Support/Claude/plugins/
```

**Windows:**
```
%APPDATA%\Claude\plugins\
```

### Step 2: Copy the Plugin

Copy the entire `pnd-agents-slash-commands` folder to your Claude Desktop plugins directory:

```bash
# macOS
cp -r pnd-agents-slash-commands ~/Library/Application\ Support/Claude/plugins/

# Windows (PowerShell)
Copy-Item -Recurse pnd-agents-slash-commands $env:APPDATA\Claude\plugins\
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop to load the new plugin.

### Step 4: Verify Installation

Type `/` in Claude Desktop - you should see all the PND Agent slash commands available.

## Available Slash Commands

### Development Agents

| Command | Description |
|---------|-------------|
| `/task-manager` | Orchestrate complex tasks across specialized agents |
| `/frontend` | Generate React/Next.js components |
| `/backend` | Create API routes and serverless functions |
| `/unit-test` | Generate comprehensive unit tests |
| `/code-review` | Review code for quality and security |

### CMS & Content

| Command | Description |
|---------|-------------|
| `/amplience` | Create Amplience CMS content types |
| `/amplience-placement` | Configure content placements and slots |

### Quality & Performance

| Command | Description |
|---------|-------------|
| `/qa` | Analyze test coverage and generate scenarios |
| `/performance` | Analyze HAR files and Core Web Vitals |
| `/sonar` | Validate SonarCloud compliance |
| `/bx-scan` | Detect broken experiences and dead links |

### Commerce

| Command | Description |
|---------|-------------|
| `/commerce` | SFCC product search and integration |
| `/figma` | Extract design tokens from Figma |

### Product Management

| Command | Description |
|---------|-------------|
| `/prd-to-jira` | Convert PRDs to Jira epics and stories |
| `/exec-summary` | Generate executive summaries |
| `/roadmap-review` | Critique roadmaps and OKRs |
| `/analytics` | Generate sprint reports and metrics |

## Usage Examples

### Generate a React Component
```
/frontend Create a product card with image, title, price, and add-to-cart button
```

### Convert PRD to Jira Stories
```
/prd-to-jira

[Paste your PRD content here]
```

### Review Code
```
/code-review

[Paste your code here]
```

### Generate Unit Tests
```
/unit-test

[Paste your component code here]
```

### Create Executive Summary
```
/exec-summary

Sprint 42 completed with 45 story points. Key deliverables:
- Checkout redesign (15 points)
- Product search improvements (12 points)
- Bug fixes (18 points)

Blockers: Payment gateway integration delayed by vendor.
```

## Who Should Use This

- **Developers**: Frontend, backend, and full-stack engineers
- **QA Engineers**: Test coverage and scenario generation
- **Product Managers**: PRD conversion, roadmap review, exec summaries
- **Tech Leads**: Code review, architecture decisions
- **Engineering Managers**: Sprint analytics, team metrics

## Pandora Standards

All agents enforce Pandora's coding standards:
- TypeScript strict mode
- 80% minimum test coverage
- WCAG 2.1 AA accessibility
- Mobile-first responsive design
- Semantic HTML structure

## Troubleshooting

### Commands Not Appearing
1. Ensure the plugin folder is in the correct location
2. Check that `plugin.json` exists in `.claude-plugin/`
3. Restart Claude Desktop completely

### Plugin Not Loading
1. Verify folder structure matches expected layout
2. Check for JSON syntax errors in `plugin.json`
3. Review Claude Desktop logs for errors

## Support

- **Repository**: https://github.com/shvee-pandora/pnd-agents
- **Slack**: #pnd-agents-support
- **Documentation**: https://pandoradigital.atlassian.net/wiki/spaces/~712020a796c84908ee48a8bc04950e7f6fb704/pages/5115445591

## License

MIT License - Pandora Digital
