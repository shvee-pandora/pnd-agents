# PR Review Agent

A reusable agent for reviewing Pull Requests from Azure DevOps. Provides structured, role-aware PR reviews based on detected tech stack.

## Overview

The PR Review Agent connects to Azure DevOps and reviews Pull Requests based on the detected technology stack. It supports multiple review personas and provides comprehensive, actionable feedback without requiring repository cloning.

## Features

- **PR Access**: Fetch PR metadata, changed files, and diffs from Azure DevOps REST API
- **Tech Stack Detection**: Automatically identify Frontend, Backend, QA, and Infrastructure changes
- **Role-Aware Reviews**: Support for FE, QA, Platform, Backend, and General review modes
- **Structured Output**: Summary, Code Quality, Risk Analysis, Test Coverage, Architecture, Recommendations

## Installation

The PR Review Agent is part of pnd-agents. Install via:

```bash
pip install git+https://github.com/shvee-pandora/pnd-agents.git
```

Or if you have the repo cloned:

```bash
cd pnd-agents
pip install -e .
```

## Configuration

### Environment Variables

Set the following environment variable for Azure DevOps API access:

```bash
export AZURE_DEVOPS_PAT="your-personal-access-token"
# or
export AZURE_DEVOPS_TOKEN="your-personal-access-token"
```

Optional configuration:

```bash
export AZURE_DEVOPS_ORG="pandora-jewelry"  # Default organization
export AZURE_DEVOPS_PROJECT="Spark"        # Default project
```

### Getting an Azure DevOps PAT

1. Go to Azure DevOps > User Settings > Personal Access Tokens
2. Create a new token with the following scopes:
   - Code (Read)
   - Pull Request Threads (Read)
3. Copy the token and set it as `AZURE_DEVOPS_PAT`

## Usage

### Claude Desktop / Claude Code

Use the `/review-pr` slash command:

```
/review-pr https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034
/review-pr https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034 qa
/review-pr https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034 fe
```

Or use the MCP tools directly:

```
pr_review(pr_url="https://dev.azure.com/.../pullrequest/89034", role="fe")
pr_review_get_pr_data(pr_url="https://dev.azure.com/.../pullrequest/89034")
pr_review_detect_tech_stack(pr_url="https://dev.azure.com/.../pullrequest/89034")
```

### Python API

```python
from agents.pr_review_agent import PRReviewAgent, ReviewRole

# Create agent
agent = PRReviewAgent()

# Review a PR
result = agent.review_pr(
    "https://dev.azure.com/pandora-jewelry/Spark/_git/pandora-group/pullrequest/89034",
    role=ReviewRole.FRONTEND
)

# Get markdown output
print(result.to_markdown())

# Get JSON output
print(result.to_dict())

# Clean up
agent.close()
```

### Context Manager

```python
from agents.pr_review_agent import PRReviewAgent, ReviewRole

with PRReviewAgent() as agent:
    result = agent.review_pr(pr_url, ReviewRole.QA)
    print(result.to_markdown())
```

### Convenience Functions

```python
from agents.pr_review_agent import review_pr, review_pr_markdown

# Get JSON result
result = review_pr("https://dev.azure.com/.../pullrequest/89034", role="fe")

# Get markdown result
markdown = review_pr_markdown("https://dev.azure.com/.../pullrequest/89034", role="qa")
```

## Supported Roles

| Role | Description | Focus Areas |
|------|-------------|-------------|
| `general` | General PR Review (default) | Auto-detects tech stack and adapts review |
| `fe` / `frontend` | Frontend Reviewer | React, Next.js, Chakra, PWA Kit, TypeScript, accessibility |
| `qa` | QA Reviewer | Cypress, Playwright, Jest, test coverage, test quality |
| `platform` | Platform/Architecture Reviewer | YAML, pipelines, Docker, infrastructure, configuration |
| `backend` | Backend Reviewer | Node.js, Java, .NET, SFCC, API design, error handling |

## Tech Stack Detection

The agent automatically detects the following technology stacks:

### Frontend
- React (`.tsx`, `.jsx`, React imports)
- Next.js (next imports, `getServerSideProps`, `app/` directory)
- Chakra UI (`@chakra-ui` imports)
- PWA Kit (`@salesforce/pwa-kit`)

### Backend
- Node.js (Express, `package.json`)
- Java (`.java`, Spring Boot, Maven/Gradle)
- .NET (`.cs`, `.csproj`)
- SFCC (cartridge, `dw/`)

### QA
- Cypress (`.cy.ts`, `cy.` commands)
- Playwright (`@playwright/test`, `page.` commands)
- Jest (`.test.ts`, `describe`, `it`, `expect`)

### Infrastructure
- YAML (`.yaml`, `.yml`)
- Azure Pipelines (`azure-pipelines`)
- Docker (`Dockerfile`, `docker-compose`)

## Review Output Structure

Each review includes:

### 1. Summary
- What the PR does
- Scope and impact assessment

### 2. Code Quality Review
- Readability assessment
- Maintainability assessment
- Best practices compliance
- Specific notes and observations

### 3. Risk Analysis
- Breaking changes
- Performance risks
- Security concerns
- Detailed risk items

### 4. Test Coverage Review
- Existing tests in the PR
- Missing test coverage
- Cypress coverage (if applicable)

### 5. Architecture & Standards
- Design consistency
- Pandora standards alignment
- Tech debt assessment

### 6. Actionable Recommendations
- Specific suggestions with severity levels (High/Medium/Low)
- Clear action items for the PR author

## MCP Tools

The following MCP tools are available:

| Tool | Description |
|------|-------------|
| `pr_review` | Review a PR with structured, role-aware feedback |
| `pr_review_get_pr_data` | Fetch raw PR data without performing a review |
| `pr_review_detect_tech_stack` | Detect tech stack from a PR |

## Known Limitations

- **Read-only access**: The agent does not comment on PRs directly
- **No code generation**: The agent analyzes but does not generate code
- **Azure DevOps only**: Currently supports Azure DevOps PRs only (GitHub/GitLab not yet supported)
- **API rate limits**: Large PRs with many files may hit API rate limits
- **Binary files**: Binary file changes are not analyzed

## Troubleshooting

### Authentication Errors

If you see authentication errors:

1. Verify your PAT is set correctly: `echo $AZURE_DEVOPS_PAT`
2. Ensure the PAT has not expired
3. Verify the PAT has Code (Read) scope

### PR Not Found

If the PR is not found:

1. Verify the PR URL format is correct
2. Ensure you have access to the repository
3. Check that the PR exists and is not deleted

### Timeout Errors

For large PRs:

1. The agent may take longer to fetch all file contents
2. Consider using `pr_review_get_pr_data` with `include_content=False` for faster results

## Contributing

Contributions are welcome! Please follow the existing code patterns and ensure all tests pass before submitting a PR.

## License

Part of pnd-agents. See the main repository for license information.
