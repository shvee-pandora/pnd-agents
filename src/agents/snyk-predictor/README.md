# Snyk Predictor Agent

Proactively detect and predict Snyk vulnerabilities before CI/CD pipelines are blocked.

## Problem Statement

Security vulnerabilities in dependencies can block CI/CD pipelines unexpectedly, causing deployment delays and developer frustration. The Snyk Predictor Agent addresses this by:

1. **Proactive Detection**: Scanning dependencies before they cause pipeline failures
2. **Risk Prediction**: Using heuristics to identify dependencies likely to cause future issues
3. **Early Warning**: Sending Teams notifications so teams can address issues before they become blockers
4. **Actionable Insights**: Providing specific upgrade recommendations with priority levels

## Features

- **Dependency Scanning**: Reads package.json and lock files (npm, pnpm, yarn)
- **Snyk Integration**: Runs `snyk test --json` to get vulnerability data
- **Heuristic Risk Scoring**: Calculates risk scores (0-100) based on:
  - Historical CVE frequency
  - Transitive dependency depth
  - Package release age
  - Known high-risk libraries
- **Risk Classification**: Categorizes dependencies as High/Medium/Low risk
- **Teams Notifications**: Sends formatted Adaptive Cards to Microsoft Teams
- **JSON Reports**: Generates structured reports for further processing
- **Azure DevOps Integration**: Includes ready-to-use scheduled pipeline

## Installation

The Snyk Predictor Agent is part of the pnd-agents platform. Ensure you have:

```bash
# Clone pnd-agents if not already done
git clone https://github.com/shvee-pandora/pnd-agents.git
cd pnd-agents

# Install dependencies
npm install

# Build TypeScript
npm run build
```

### Prerequisites

- Node.js 18+ 
- Snyk CLI installed and authenticated (`npm install -g snyk && snyk auth`)
- SNYK_TOKEN environment variable set
- TEAMS_WEBHOOK_URL environment variable (for notifications)

## Usage

### Manual Execution

```bash
# Basic scan
pnd-agents run snyk-predictor \
  --repo pandora-ecom-web \
  --repoPath ./pandora-ecom-web \
  --packageManager pnpm

# With Teams notifications
pnd-agents run snyk-predictor \
  --repo pandora-ecom-web \
  --repoPath ./pandora-ecom-web \
  --packageManager pnpm \
  --notify teams \
  --severity high,critical

# Save report to file
pnd-agents run snyk-predictor \
  --repo pandora-ecom-web \
  --repoPath ./pandora-ecom-web \
  --packageManager pnpm \
  --output ./reports/snyk-report.json
```

### Direct TypeScript Execution

```bash
cd src/agents/snyk-predictor
npx ts-node index.ts \
  --repo my-app \
  --repoPath /path/to/my-app \
  --packageManager npm \
  --notify teams
```

### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--repo` | `-r` | Repository name for reporting | Directory name |
| `--repoPath` | `-p` | Path to repository to scan | Current directory |
| `--packageManager` | `-m` | Package manager (npm/pnpm/yarn) | npm |
| `--notify` | `-n` | Notification channel (teams/none) | none |
| `--severity` | `-s` | Severity levels to report | high,critical |
| `--output` | `-o` | Output JSON report path | - |
| `--help` | `-h` | Show help message | - |

## Automated Execution (Daily Cron)

### Azure DevOps Pipeline

The agent includes a ready-to-use Azure DevOps pipeline at `pipelines/azure-devops-daily.yml`.

#### Setup Steps

1. **Create Variable Group**: In Azure DevOps, create a variable group named `snyk-credentials` with:
   - `SNYK_TOKEN`: Your Snyk API token
   - `TEAMS_WEBHOOK_URL`: Your Microsoft Teams webhook URL

2. **Import Pipeline**: Import `pipelines/azure-devops-daily.yml` into your Azure DevOps project

3. **Configure Repositories**: Edit the `repositories` parameter to include your repos:

```yaml
parameters:
  - name: repositories
    type: object
    default:
      - name: pandora-ecom-web
        path: $(Build.SourcesDirectory)/pandora-ecom-web
        packageManager: pnpm
      - name: pandora-api
        path: $(Build.SourcesDirectory)/pandora-api
        packageManager: npm
```

4. **Schedule**: The pipeline runs daily at 6 AM UTC by default. Modify the cron expression as needed:

```yaml
schedules:
  - cron: "0 6 * * *"  # 6 AM UTC daily
```

### GitHub Actions (Alternative)

```yaml
name: Snyk Predictor Daily Scan

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install Snyk
        run: npm install -g snyk
        
      - name: Run Snyk Predictor
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
          TEAMS_WEBHOOK_URL: ${{ secrets.TEAMS_WEBHOOK_URL }}
        run: |
          npx ts-node src/agents/snyk-predictor/index.ts \
            --repo ${{ github.repository }} \
            --repoPath . \
            --packageManager npm \
            --notify teams \
            --severity high,critical
```

## Teams Notifications

When high-risk dependencies are detected, the agent sends an Adaptive Card to Microsoft Teams:

```
⚠️ Snyk Early Warning (Daily Scan)

Repository: pandora-ecom-web
Scan Date: 1/16/2026, 6:00:00 AM

🔴 High Risk Dependencies
• axios@1.5.0 → upgrade to ^1.6.2
• lodash@4.17.21 → transitive CVE risk

📋 Suggested Fixes
🔴 axios@1.5.0 → upgrade to `1.6.2`
🟠 minimist@1.2.5 → upgrade to `1.2.8`

Action: Fix before next deployment
```

### Setting Up Teams Webhook

1. In Microsoft Teams, go to the channel where you want notifications
2. Click `...` → `Connectors` → `Incoming Webhook`
3. Name it "Snyk Predictor" and create
4. Copy the webhook URL
5. Set as `TEAMS_WEBHOOK_URL` environment variable

## Risk Scoring Algorithm

The agent uses a heuristic-based risk scoring system (no ML models):

### Risk Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Historical CVE Frequency | 35% | Number and severity of known vulnerabilities |
| Transitive Dependency Depth | 20% | How deep in the dependency tree |
| Known High-Risk Library | 25% | Package is in known high-risk list |
| Package Release Age | 10% | Version age and update frequency |
| Direct Dependency Impact | 10% | Direct vs transitive dependency |

### Risk Levels

| Score Range | Level | Action |
|-------------|-------|--------|
| 60-100 | 🔴 High | Immediate attention required |
| 30-59 | 🟠 Medium | Plan to address soon |
| 0-29 | 🟢 Low | Monitor in future scans |

### Known High-Risk Packages

The agent flags these packages as higher risk due to historical vulnerability patterns:

- lodash, moment, request
- node-fetch, axios, express
- minimist, qs, serialize-javascript
- ini, y18n, glob-parent
- trim-newlines, path-parse, hosted-git-info
- ssri, normalize-url, trim, tar, ansi-regex

## Output Format

### JSON Report Structure

```json
{
  "scanDate": "2026-01-16T06:00:00.000Z",
  "repoName": "pandora-ecom-web",
  "riskSummary": {
    "totalDependencies": 1250,
    "highRiskCount": 5,
    "mediumRiskCount": 23,
    "lowRiskCount": 1222,
    "overallRiskLevel": "high",
    "pipelineBlockProbability": 0.45
  },
  "highRiskDependencies": [
    {
      "name": "axios",
      "version": "1.5.0",
      "riskScore": 78,
      "riskLevel": "high",
      "suggestedFix": "Upgrade to 1.6.2",
      "urgency": "immediate",
      "vulnerabilities": [
        {
          "id": "SNYK-JS-AXIOS-6032459",
          "severity": "high",
          "title": "Cross-Site Request Forgery"
        }
      ]
    }
  ],
  "suggestedFixes": [
    {
      "packageName": "axios",
      "currentVersion": "1.5.0",
      "suggestedVersion": "1.6.2",
      "reason": "1 high severity CVE",
      "priority": "high"
    }
  ]
}
```

## Constraints

This agent is designed with the following constraints:

- ❌ Does **NOT** block pipelines
- ❌ Does **NOT** auto-merge dependency updates
- ❌ Does **NOT** use ML models (heuristics only)
- ✅ Read-only analysis
- ✅ Non-blocking notifications
- ✅ Works across multiple repositories

## Troubleshooting

### Snyk Authentication Failed

```bash
# Ensure SNYK_TOKEN is set
export SNYK_TOKEN=your-token-here

# Or authenticate interactively
snyk auth
```

### Teams Notification Not Sent

1. Verify `TEAMS_WEBHOOK_URL` is set correctly
2. Test the webhook manually:
```bash
curl -H "Content-Type: application/json" \
  -d '{"text": "Test message"}' \
  $TEAMS_WEBHOOK_URL
```

### Lock File Not Found

Ensure the repository has a lock file matching the package manager:
- npm: `package-lock.json`
- pnpm: `pnpm-lock.yaml`
- yarn: `yarn.lock`

### No Vulnerabilities Detected

If Snyk returns no vulnerabilities but you expect some:
1. Ensure Snyk CLI is up to date: `npm update -g snyk`
2. Check if the project is monitored in Snyk: `snyk monitor`
3. Verify the lock file is committed and up to date

## API Reference

### SnykPredictorAgent

```typescript
import { SnykPredictorAgent } from './index';

const agent = new SnykPredictorAgent({
  repo: 'my-app',
  repoPath: '/path/to/repo',
  packageManager: 'npm',
  notify: 'teams',
  severity: ['high', 'critical'],
  teamsWebhookUrl: process.env.TEAMS_WEBHOOK_URL,
  snykToken: process.env.SNYK_TOKEN,
});

const result = await agent.run();
console.log(result.predictionResult);
```

### Programmatic Usage

```typescript
import { scanDependencies } from './scanner';
import { predictRisks } from './predictor';
import { sendTeamsNotification } from './notifier/teams';

// Scan dependencies
const scanResult = await scanDependencies('./my-repo', 'npm');

// Predict risks
const prediction = predictRisks(scanResult);

// Send notification
if (prediction.highRiskDependencies.length > 0) {
  await sendTeamsNotification(prediction);
}
```

## Contributing

1. Follow existing code patterns in pnd-agents
2. Add tests for new functionality
3. Update this README for any new features
4. Ensure TypeScript compiles without errors

## License

MIT - See pnd-agents LICENSE file
