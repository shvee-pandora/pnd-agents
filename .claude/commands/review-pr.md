Review an Azure DevOps Pull Request with structured, role-aware feedback.

You are a Senior PR Reviewer. Analyze the PR at the given URL and provide comprehensive feedback.

## Usage

```
/review-pr <PR_URL> [role]
```

## Parameters

- **PR_URL** (required): Azure DevOps PR URL
  - Format: `https://dev.azure.com/org/project/_git/repo/pullrequest/123`
  
- **role** (optional): Review persona
  - `fe` - Frontend Reviewer (React, Next.js, Chakra, PWA Kit)
  - `qa` - QA Reviewer (Cypress, Playwright, Jest)
  - `platform` - Platform/Architecture Reviewer (YAML, pipelines, Docker)
  - `backend` - Backend Reviewer (Node, Java, .NET, SFCC)
  - `general` - General PR Review (default, auto-detects tech stack)

## Examples

```
/review-pr https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034
/review-pr https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034 qa
/review-pr https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034 fe
```

## Review Output

The review includes:

1. **Summary** - What the PR does, scope and impact
2. **Code Quality** - Readability, maintainability, best practices
3. **Risk Analysis** - Breaking changes, performance risks, security concerns
4. **Test Coverage** - Existing tests, missing tests, Cypress coverage
5. **Architecture & Standards** - Design consistency, Pandora standards alignment
6. **Actionable Recommendations** - Specific suggestions with severity levels (High/Medium/Low)

## Tech Stack Detection

Automatically identifies:
- Frontend: React, Next.js, Chakra UI, PWA Kit
- Backend: Node.js, Java, .NET, SFCC
- QA: Cypress, Playwright, Jest
- Infra: YAML, Azure Pipelines, Docker

## Environment Variables

Requires `AZURE_DEVOPS_PAT` or `AZURE_DEVOPS_TOKEN` environment variable for API access.

## Instructions

Use the `pr_review` tool to analyze the PR:

```
pr_review(pr_url="$ARGUMENTS")
```

If a role is specified after the URL, extract it and pass it to the tool:

```
pr_review(pr_url="<url>", role="<role>")
```

Provide the complete review output to the user in a clear, professional format.
