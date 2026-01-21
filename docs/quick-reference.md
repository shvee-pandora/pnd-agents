# Pandora AI Squad - Quick Reference Card

## Two Usage Modes

Pandora AI Squad can be used in two ways:
- **Mode A**: With Claude Desktop/Claude Code (MCP integration)
- **Mode B**: Without Claude - CLI only (VS Code terminal)

Both modes use the same installation. The difference is whether you run `setup` to configure Claude integration.

---

## Mode A: With Claude Desktop/Claude Code

### Step 1: Install

```bash
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents
pip3 install -e .
```

### Step 2: Run Setup Wizard

```bash
python3 -m pnd_agents setup
```

This will:
- Let you choose which agents to enable
- Configure environment variables (Figma token, etc.)
- Automatically update your Claude configuration

### Step 3: Restart Claude

Close and reopen Claude Desktop/Code completely.

### Step 4: Validate

In Claude, ask:
```
What pnd-agents tools do you have access to?
```

Then try a task:
```
Create a simple React component using pnd-agents
```

---

## Mode B: Without Claude - CLI Only (VS Code)

### Step 1: Install

```bash
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents
pip3 install -e .
```

### Step 2: Use from Any Directory

```bash
cd /path/to/your-project

# Check installation
python3 -m pnd_agents status

# Analyze a task (shows workflow plan)
python3 -m pnd_agents analyze-task "Create an Amplience schema"

# Run a task
python3 -m pnd_agents run-task "Create a React component"
```

### Step 3: (Optional) Add Alias

```bash
echo 'alias pnd-agents="python3 -m pnd_agents"' >> ~/.zshrc
source ~/.zshrc

# Then use:
pnd-agents run-task "your task"
```

### Step 4: Validate

```bash
# Should complete without errors:
python3 -m pnd_agents status
python3 -m pnd_agents analyze-task "Create a React component"
```

---

## API Tokens (Optional)

**Figma Token** (for Figma integration):
- Go to [Figma Settings](https://www.figma.com/settings) → Account → Personal access tokens
- Generate new token → Copy it

**SonarCloud Token** (for quality gate validation):
- Go to [SonarCloud Security](https://sonarcloud.io/account/security)
- Generate token with "Analyze Projects" permission

Set tokens in your environment or `.env` file:
```bash
export FIGMA_ACCESS_TOKEN="your-figma-token"
export SONAR_TOKEN="your-sonarcloud-token"
```

---

## Available Agents (20 Total)

### Universal Agents (16)

| Agent | Use When You Need To... |
|-------|------------------------|
| **Task Manager** | Orchestrate complex multi-step tasks |
| **Frontend Engineer** | Create React/Next.js components |
| **Backend** | Create API routes and Server Components |
| **Figma Reader** | Extract design metadata from Figma |
| **Code Review** | Validate against any JS/TS framework standards (Context7 + Pandora) |
| **Unit Test** | Generate tests with 100% coverage |
| **Sonar Validation** | Check quality gates (0 errors, 0 duplication) |
| **QA** | Generate E2E and integration tests |
| **PR Review** | Automate pull request reviews |
| **Technical Debt** | Identify and classify tech debt |
| **Performance** | Analyze HAR files and optimize |
| **Broken Experience Detector** | Find UX issues and broken links |
| **PRD to Jira** | Convert PRDs to JIRA work items |
| **Exec Summary** | Create stakeholder summaries |
| **Roadmap Review** | Critique roadmaps and OKRs |
| **Analytics** | Track task metrics and reporting |

### Platform Agents (3)

| Agent | Use When You Need To... |
|-------|------------------------|
| **Commerce** | Find products and prepare cart data (Pandora SFCC) |
| **Amplience CMS** | Create content types and schemas |
| **Amplience Placement** | Map content to Amplience modules |

---

## 💬 Example Prompts

### Component from Figma
```
Create a Stories carousel component from this Figma design:
https://www.figma.com/design/ABC123/My-Design?node-id=123-456
```

### Unit Tests
```
Write unit tests for src/components/Button/Button.tsx with 100% coverage
```

### Code Validation
```
Validate my feature/new-header branch against SonarCloud quality gates
```

### Content Type
```
Create an Amplience content type for a homepage hero with title, 
description, image, and CTA button
```

### Performance Analysis
```
Analyze this HAR file and suggest performance optimizations
```

### Product Search
```
Find a silver bracelet under 700 DKK
```

---

## 🔄 Workflow Pipelines

Tasks are automatically routed through agent pipelines:

| Task Type | Pipeline |
|-----------|----------|
| **Figma** | Figma Reader → Frontend → Code Review → Unit Test → Sonar → Performance |
| **Frontend** | Frontend → Code Review → Unit Test → Sonar → Performance |
| **Backend** | Backend → Code Review → Unit Test → Sonar |
| **Unit Test** | Unit Test → Sonar |
| **Sonar** | Sonar → Code Review |

---

## 📋 Quality Standards

All agents follow Pandora coding standards:

✅ **Next.js App Router** - Server Components, streaming, caching  
✅ **Atomic Design** - atoms, molecules, organisms, templates  
✅ **TypeScript Strict** - no `any`, proper typing  
✅ **Accessibility** - WCAG 2.1 AA compliance  
✅ **SonarCloud** - 0 errors, 0 duplication, 100% coverage  

---

## 🔧 Troubleshooting

**Agents not showing in Claude?**
- Check config file syntax (valid JSON)
- Verify paths are absolute
- Restart Claude completely

**Figma API errors?**
- Verify `FIGMA_ACCESS_TOKEN` is set
- Check token hasn't expired
- Ensure token has read access to file

**Need help?**
- [Setup Guide](https://github.com/shvee-pandora/pnd-agents/blob/main/docs/setup.md)
- [How Agents Work](https://github.com/shvee-pandora/pnd-agents/blob/main/docs/how-agents-work.md)
- [Architecture](https://github.com/shvee-pandora/pnd-agents/blob/main/docs/architecture.md)

---

## 🔐 Security Best Practices

1. **Never commit tokens** - Add `.env` to `.gitignore`
2. **Use environment variables** - Reference with `${VARIABLE_NAME}`
3. **Minimal permissions** - Read-only for Figma, "Analyze Projects" for Sonar
4. **Rotate regularly** - Generate new tokens periodically

---

## Learn More

- **Repository**: [github.com/shvee-pandora/pnd-agents](https://github.com/shvee-pandora/pnd-agents)
- **Setup Guide**: [setup.md](./setup.md)
- **How Agents Work**: [how-agents-work.md](./how-agents-work.md)
- **Examples**: [examples/](https://github.com/shvee-pandora/pnd-agents/tree/main/examples)

---

**Version**: 2.0.0 | **Last Updated**: January 2026 | **Maintained by**: Pandora Group
