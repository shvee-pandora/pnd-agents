# Snyk Predictor Agent - How It Works

This document explains the architecture, workflow, and implementation details of the Snyk Predictor Agent.

## Overview

The Snyk Predictor Agent is a TypeScript-based security scanning tool that proactively detects vulnerabilities in npm/pnpm/yarn projects and sends detailed notifications to Microsoft Teams. It combines Snyk CLI vulnerability scanning with heuristic-based risk prediction to help teams prioritize security fixes.

## Architecture

The agent consists of four main modules:

```
snyk-predictor/
├── index.ts          # Main entry point and CLI
├── scanner/          # Dependency scanning module
│   └── index.ts      # Parses dependencies and runs Snyk CLI
├── predictor/        # Risk prediction module
│   └── index.ts      # Calculates risk scores using heuristics
├── notifier/         # Notification module
│   └── teams.ts      # Sends Teams Adaptive Cards
└── types/            # TypeScript type definitions
    └── index.ts      # Shared interfaces and constants
```

## Workflow

### Step 1: Dependency Scanning

The scanner module performs two tasks:

**1.1 Parse Dependencies**
- Reads `package.json` and lock files (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`)
- Extracts direct and transitive dependencies
- Identifies dependency depth in the tree

**1.2 Run Snyk Test**
- Executes `snyk test --json` in the repository
- Parses the JSON output to extract vulnerability details
- Maps each vulnerability to its affected package

```typescript
// Scanner output structure
interface ScanResult {
  scanDate: string;
  repoName: string;
  packageManager: 'npm' | 'pnpm' | 'yarn';
  totalDependencies: number;
  directDependencies: number;
  transitiveDependencies: number;
  vulnerabilities: SnykVulnerability[];
  dependencies: DependencyInfo[];
}
```

### Step 2: Risk Prediction

The predictor module calculates a risk score (0-100) for each dependency using five weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Historical CVE Frequency | 35% | Number and severity of known vulnerabilities |
| Transitive Dependency Depth | 20% | How deep in the dependency tree (deeper = harder to fix) |
| Known High-Risk Library | 25% | Whether the package is in the known high-risk list |
| Package Release Age | 10% | Version maturity (v0.x = higher risk) |
| Direct Dependency Impact | 10% | Direct dependencies are easier to update |

**Risk Score Calculation:**

```typescript
// Severity weights for vulnerability scoring
const SEVERITY_WEIGHTS = {
  critical: 40,
  high: 30,
  medium: 15,
  low: 5,
};

// Risk level thresholds
function scoreToLevel(score: number): RiskLevel {
  if (score >= 60) return 'high';
  if (score >= 30) return 'medium';
  return 'low';
}
```

**Example Calculation (lodash@4.17.21):**

```
Factor                        | Value | Weight | Contribution
------------------------------|-------|--------|-------------
Historical CVE Frequency      | 15.0  | 0.35   | 5.25
Transitive Dependency Depth   | 20.0  | 0.20   | 4.00
Known High-Risk Library       | 80.0  | 0.25   | 20.00
Package Release Age           | 0.0   | 0.10   | 0.00
Direct Dependency Impact      | 20.0  | 0.10   | 2.00
------------------------------|-------|--------|-------------
Total Risk Score              |       |        | 31.25 (MEDIUM)
```

### Step 3: Severity Filtering

The agent filters results based on the `--severity` flag:

```typescript
// Default: medium, high, critical
const filterBySeverity = (prediction: PredictionResult) => {
  // Include dependencies that:
  // 1. Have vulnerabilities matching the severity filter, OR
  // 2. Have a high risk score level, OR
  // 3. Have a medium risk score level (if medium is in filter)
};
```

### Step 4: Teams Notification

The notifier module sends an Adaptive Card to Microsoft Teams with:

- Repository name and scan date
- High risk dependencies section (if any)
- Medium risk dependencies section (if any)
- Vulnerability details for each dependency:
  - Package name and version
  - Vulnerability title and severity
  - CVSS score and CWE identifiers
  - Dependency path (how it's introduced)
  - Upgrade/patch availability
  - Fix recommendations
- Action message based on risk level

**Notification Flow:**

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Scan Result   │────▶│  Build Adaptive │────▶│  POST to Teams  │
│   + Prediction  │     │      Card       │     │    Webhook      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Known High-Risk Packages

The agent maintains a list of packages with historical security issues:

```typescript
const HIGH_RISK_PACKAGES = [
  'lodash',      // Prototype pollution vulnerabilities
  'moment',      // ReDoS vulnerabilities
  'request',     // Deprecated, multiple CVEs
  'node-fetch',  // SSRF vulnerabilities
  'axios',       // SSRF vulnerabilities
  'express',     // Various security issues
  'minimist',    // Prototype pollution
  'qs',          // Prototype pollution
  'tar',         // Path traversal
  // ... and more
];
```

## CLI Usage

```bash
# Basic usage
node dist/index.js --repo my-app --repoPath /path/to/repo --notify teams

# Full options
node dist/index.js \
  --repo pandora-ecom-web \
  --repoPath /path/to/repo \
  --packageManager npm \
  --notify teams \
  --severity medium,high,critical \
  --output report.json
```

**Options:**

| Flag | Description | Default |
|------|-------------|---------|
| `-r, --repo` | Repository name for reporting | Directory name |
| `-p, --repoPath` | Path to repository | Current directory |
| `-m, --packageManager` | npm, pnpm, or yarn | npm |
| `-n, --notify` | Notification channel (teams, none) | none |
| `-s, --severity` | Severity levels to report | medium,high,critical |
| `-o, --output` | Output JSON report to file | - |

**Environment Variables:**

| Variable | Description |
|----------|-------------|
| `SNYK_TOKEN` | Snyk API token for authentication |
| `TEAMS_WEBHOOK_URL` | Microsoft Teams webhook URL |

## Azure DevOps Pipeline Integration

The agent is designed to run as a scheduled pipeline:

```yaml
# azure-pipelines/snyk-predictor-daily.yml
schedules:
  - cron: "0 18 * * *"  # Daily at 6 PM UTC
    branches:
      include:
        - trunk

steps:
  - script: |
      git clone --depth 1 --branch main https://github.com/shvee-pandora/pnd-agents.git
    displayName: "Clone pnd-agents"

  - script: |
      cd pnd-agents/src/agents/snyk-predictor
      npm install && npm run build
    displayName: "Build agent"

  - script: |
      cd pnd-agents/src/agents/snyk-predictor
      node dist/index.js \
        --repo $(Build.Repository.Name) \
        --repoPath $(Build.SourcesDirectory) \
        --notify teams \
        --severity medium,high,critical
    env:
      SNYK_TOKEN: $(SNYK_TOKEN)
      TEAMS_WEBHOOK_URL: $(TEAMS_WEBHOOK_URL)
```

## Output Examples

### Console Output

```
============================================================
SNYK PREDICTOR AGENT
============================================================

Repository: pandora-ecom-web
Path: /home/ubuntu/repos/pandora-ecom-web
Package Manager: npm
Severity Filter: medium, high, critical
Notifications: teams

[1/4] Scanning dependencies...
     Found 1678 dependencies
     - Direct: 67
     - Transitive: 1611
     - Vulnerabilities: 1

[2/4] Predicting risks...
     Risk Summary:
     - High Risk: 0
     - Medium Risk: 29
     - Low Risk: 1649
     - Pipeline Block Probability: 58.0%

[3/4] Generating report...
     Report saved to: snyk-predictor-report.json

[4/4] Sending notifications...
     Teams notification sent!

============================================================
SCAN COMPLETE
============================================================
```

### Teams Notification

The Teams notification displays as an Adaptive Card with:

```
+--------------------------------------------------+
| Snyk Early Warning (Daily Scan)                  |
|--------------------------------------------------|
| Repository: pandora-ecom-web                     |
| Scan Date: 1/22/2026, 6:10:05 PM                |
|--------------------------------------------------|
| Medium Risk Dependencies                         |
|                                                  |
| * lodash@4.17.21                                 |
|   Prototype Pollution                            |
|   Severity: MEDIUM | CVSS: 6.9                  |
|   CWE: CWE-1321                                  |
|   Path: @pandora-mfe/source > @salesforce/...   |
|   Upgradable (fixed in 4.17.23)                 |
|   Fix: Upgrade to 4.17.23                       |
|                                                  |
| ... and 24 more medium-risk dependencies        |
|--------------------------------------------------|
| Action: Review and plan fixes for medium-risk   |
| dependencies                                     |
+--------------------------------------------------+
```

## Error Handling

The agent handles common errors gracefully:

1. **Snyk authentication failure** - Prompts to set `SNYK_TOKEN`
2. **No package.json found** - Reports error and exits
3. **Teams webhook failure** - Logs error but doesn't fail pipeline
4. **Snyk test failure** - Still parses stdout for vulnerability data (Snyk exits with code 1 when vulnerabilities are found)

## Limitations

- **No ML models** - Uses heuristics only for risk prediction
- **npm/pnpm/yarn only** - Does not support pip, cargo, or other package managers
- **Single repository** - Scans one repository at a time
- **Snyk dependency** - Requires Snyk CLI and valid token

## Future Enhancements

Potential improvements for future versions:

1. Support for additional package managers (pip, cargo, maven)
2. Historical trend tracking across scans
3. Slack notification support
4. Custom risk factor weights via configuration
5. Integration with Jira for automatic ticket creation
