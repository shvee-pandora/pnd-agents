# PG AI Squad - Quick Reference Card

## 🚀 Using with Claude (No Clone Required)

### Step 1: Configure Claude

Add to your Claude config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.claude.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pnd-agents": {
      "command": "npx",
      "args": ["-y", "github:shvee-pandora/pnd-agents"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "your-figma-token",
        "SONAR_TOKEN": "your-sonarcloud-token"
      }
    }
  }
}
```

### Step 2: Get API Tokens

**Figma Token** (required for Figma integration):
- Go to [Figma Settings](https://www.figma.com/settings) → Account → Personal access tokens
- Generate new token → Copy it

**SonarCloud Token** (optional):
- Go to [SonarCloud Security](https://sonarcloud.io/account/security)
- Generate token with "Analyze Projects" permission

### Step 3: Restart Claude

Close and reopen Claude Desktop/Code completely.

### Step 4: Verify

In Claude, ask:
```
What pnd-agents tools do you have access to?
```

---

## 🤖 Available Agents

| Agent | Use When You Need To... |
|-------|------------------------|
| **Task Manager** | Orchestrate complex multi-step tasks |
| **Frontend Engineer** | Create React/Next.js components |
| **Figma Reader** | Extract design metadata from Figma |
| **Amplience CMS** | Create content types and schemas |
| **Code Review** | Validate against Pandora standards |
| **Unit Test** | Generate tests with 100% coverage |
| **Sonar Validation** | Check quality gates (0 errors, 0 duplication) |
| **Performance** | Analyze HAR files and optimize |
| **QA** | Generate E2E and integration tests |
| **Backend** | Create API routes and Server Components |
| **Commerce** | Find products and prepare cart data |

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
- [Full Documentation](https://github.com/shvee-pandora/pnd-agents/blob/main/CLAUDE_USAGE.md)
- [Setup Guide](https://github.com/shvee-pandora/pnd-agents/blob/main/SETUP.md)
- [Architecture](https://github.com/shvee-pandora/pnd-agents/blob/main/ARCHITECTURE.md)

---

## 🔐 Security Best Practices

1. **Never commit tokens** - Add `.env` to `.gitignore`
2. **Use environment variables** - Reference with `${VARIABLE_NAME}`
3. **Minimal permissions** - Read-only for Figma, "Analyze Projects" for Sonar
4. **Rotate regularly** - Generate new tokens periodically

---

## 📚 Learn More

- **Repository**: [github.com/shvee-pandora/pnd-agents](https://github.com/shvee-pandora/pnd-agents)
- **Full Guide**: [CLAUDE_USAGE.md](https://github.com/shvee-pandora/pnd-agents/blob/main/CLAUDE_USAGE.md)
- **Examples**: [examples/](https://github.com/shvee-pandora/pnd-agents/tree/main/examples)

---

**Version**: 1.0.0 | **License**: MIT | **Maintained by**: Pandora Group
