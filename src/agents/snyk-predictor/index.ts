#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';
import { parseArgs } from 'util';
import { scanDependencies } from './scanner/index.js';
import { predictRisks } from './predictor/index.js';
import { sendTeamsNotification } from './notifier/teams.js';
import {
  AgentConfig,
  AgentResult,
  PackageManager,
  SeverityLevel,
  PredictionResult,
  ScanResult,
} from './types/index.js';

export class SnykPredictorAgent {
  private config: AgentConfig;

  constructor(config: AgentConfig) {
    this.config = config;
  }

  async run(): Promise<AgentResult> {
    console.log(`\n${'='.repeat(60)}`);
    console.log('SNYK PREDICTOR AGENT');
    console.log(`${'='.repeat(60)}\n`);
    console.log(`Repository: ${this.config.repo}`);
    console.log(`Path: ${this.config.repoPath}`);
    console.log(`Package Manager: ${this.config.packageManager}`);
    console.log(`Severity Filter: ${this.config.severity.join(', ')}`);
    console.log(`Notifications: ${this.config.notify}`);
    console.log('');

    let scanResult: ScanResult | null = null;
    let predictionResult: PredictionResult | null = null;
    let notificationSent = false;

    try {
      console.log('[1/4] Scanning dependencies...');
      scanResult = await scanDependencies(
        this.config.repoPath,
        this.config.packageManager,
        this.config.snykToken
      );
      console.log(`     Found ${scanResult.totalDependencies} dependencies`);
      console.log(`     - Direct: ${scanResult.directDependencies}`);
      console.log(`     - Transitive: ${scanResult.transitiveDependencies}`);
      console.log(`     - Vulnerabilities: ${scanResult.vulnerabilities.length}`);

      console.log('\n[2/4] Predicting risks...');
      predictionResult = predictRisks(scanResult);
      console.log(`     Risk Summary:`);
      console.log(`     - High Risk: ${predictionResult.riskSummary.highRiskCount}`);
      console.log(`     - Medium Risk: ${predictionResult.riskSummary.mediumRiskCount}`);
      console.log(`     - Low Risk: ${predictionResult.riskSummary.lowRiskCount}`);
      console.log(`     - Pipeline Block Probability: ${(predictionResult.riskSummary.pipelineBlockProbability * 100).toFixed(1)}%`);

      const filteredPrediction = this.filterBySeverity(predictionResult);

      console.log('\n[3/4] Generating report...');
      const report = this.generateReport(filteredPrediction);
      
      if (this.config.outputPath) {
        fs.writeFileSync(this.config.outputPath, JSON.stringify(report, null, 2));
        console.log(`     Report saved to: ${this.config.outputPath}`);
      } else {
        console.log('\n' + this.formatMarkdownReport(filteredPrediction));
      }

      console.log('\n[4/4] Sending notifications...');
      if (this.config.notify === 'teams') {
        try {
          notificationSent = await sendTeamsNotification(
            filteredPrediction,
            this.config.teamsWebhookUrl
          );
          console.log(notificationSent ? '     Teams notification sent!' : '     Failed to send Teams notification');
        } catch (error) {
          console.log(`     Teams notification error: ${error}`);
        }
      } else if (this.config.notify === 'none') {
        console.log('     Notifications disabled');
      }

      console.log(`\n${'='.repeat(60)}`);
      console.log('SCAN COMPLETE');
      console.log(`${'='.repeat(60)}\n`);

      return {
        success: true,
        scanResult,
        predictionResult: filteredPrediction,
        notificationSent,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error(`\nError: ${errorMessage}`);
      
      return {
        success: false,
        scanResult,
        predictionResult,
        notificationSent,
        error: errorMessage,
      };
    }
  }

  private filterBySeverity(prediction: PredictionResult): PredictionResult {
    const severitySet = new Set(this.config.severity);
    
    const filterDependencies = (deps: typeof prediction.highRiskDependencies) => {
      return deps.filter((dep) => {
        const hasMatchingSeverity = dep.dependency.vulnerabilities.some(
          (v) => severitySet.has(v.severity)
        );
        return hasMatchingSeverity || dep.riskScore.level === 'high';
      });
    };

    return {
      ...prediction,
      highRiskDependencies: filterDependencies(prediction.highRiskDependencies),
      suggestedFixes: prediction.suggestedFixes.filter(
        (fix) => fix.priority === 'critical' || fix.priority === 'high'
      ),
    };
  }

  private generateReport(prediction: PredictionResult): object {
    return {
      scanDate: prediction.scanDate,
      repoName: prediction.repoName,
      riskSummary: prediction.riskSummary,
      highRiskDependencies: prediction.highRiskDependencies.map((d) => ({
        name: d.dependency.name,
        version: d.dependency.version,
        riskScore: d.riskScore.score,
        riskLevel: d.riskScore.level,
        suggestedFix: d.suggestedFix,
        urgency: d.urgency,
        vulnerabilities: d.dependency.vulnerabilities.map((v) => ({
          id: v.id,
          severity: v.severity,
          title: v.title,
        })),
      })),
      suggestedFixes: prediction.suggestedFixes,
    };
  }

  private formatMarkdownReport(prediction: PredictionResult): string {
    const lines: string[] = [];
    
    lines.push('## Snyk Predictor Report');
    lines.push('');
    lines.push(`**Repository:** ${prediction.repoName}`);
    lines.push(`**Scan Date:** ${new Date(prediction.scanDate).toLocaleString()}`);
    lines.push('');
    
    lines.push('### Risk Summary');
    lines.push('');
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Total Dependencies | ${prediction.riskSummary.totalDependencies} |`);
    lines.push(`| High Risk | ${prediction.riskSummary.highRiskCount} |`);
    lines.push(`| Medium Risk | ${prediction.riskSummary.mediumRiskCount} |`);
    lines.push(`| Low Risk | ${prediction.riskSummary.lowRiskCount} |`);
    lines.push(`| Overall Risk Level | ${prediction.riskSummary.overallRiskLevel.toUpperCase()} |`);
    lines.push(`| Pipeline Block Probability | ${(prediction.riskSummary.pipelineBlockProbability * 100).toFixed(1)}% |`);
    lines.push('');

    if (prediction.highRiskDependencies.length > 0) {
      lines.push('### High Risk Dependencies');
      lines.push('');
      lines.push('| Package | Version | Risk Score | Suggested Fix |');
      lines.push('|---------|---------|------------|---------------|');
      
      for (const risk of prediction.highRiskDependencies) {
        const fix = risk.suggestedFix || 'Review required';
        lines.push(`| ${risk.dependency.name} | ${risk.dependency.version} | ${risk.riskScore.score.toFixed(0)} | ${fix} |`);
      }
      lines.push('');
    }

    if (prediction.suggestedFixes.length > 0) {
      lines.push('### Suggested Fixes');
      lines.push('');
      
      for (const fix of prediction.suggestedFixes) {
        const emoji = fix.priority === 'critical' ? '🔴' : fix.priority === 'high' ? '🟠' : '🟡';
        lines.push(`${emoji} **${fix.packageName}@${fix.currentVersion}** → upgrade to \`${fix.suggestedVersion}\``);
        lines.push(`   - ${fix.reason}`);
        lines.push('');
      }
    }

    return lines.join('\n');
  }
}

function parseCliArgs(): AgentConfig {
  const { values } = parseArgs({
    options: {
      repo: { type: 'string', short: 'r' },
      repoPath: { type: 'string', short: 'p' },
      packageManager: { type: 'string', short: 'm' },
      notify: { type: 'string', short: 'n' },
      severity: { type: 'string', short: 's' },
      output: { type: 'string', short: 'o' },
      help: { type: 'boolean', short: 'h' },
    },
    allowPositionals: true,
  });

  if (values.help) {
    console.log(`
Snyk Predictor Agent - Proactively detect and predict Snyk vulnerabilities

Usage:
  pnd-agents run snyk-predictor [options]
  npx ts-node index.ts [options]

Options:
  -r, --repo <name>           Repository name for reporting
  -p, --repoPath <path>       Path to the repository to scan (default: current directory)
  -m, --packageManager <pm>   Package manager: npm, pnpm, yarn (default: npm)
  -n, --notify <channel>      Notification channel: teams, none (default: none)
  -s, --severity <levels>     Severity levels to report: low,medium,high,critical (default: high,critical)
  -o, --output <path>         Output JSON report to file
  -h, --help                  Show this help message

Environment Variables:
  SNYK_TOKEN          Snyk API token for vulnerability scanning
  TEAMS_WEBHOOK_URL   Microsoft Teams webhook URL for notifications

Examples:
  pnd-agents run snyk-predictor --repo pandora-ecom-web --repoPath ./pandora-ecom-web --packageManager pnpm --notify teams --severity high,critical
  npx ts-node index.ts -r my-app -p . -m npm -n teams
`);
    process.exit(0);
  }

  const repoPath = values.repoPath || process.cwd();
  const repo = values.repo || path.basename(repoPath);

  return {
    repo,
    repoPath,
    packageManager: (values.packageManager as PackageManager) || 'npm',
    notify: (values.notify as 'teams' | 'none') || 'none',
    severity: values.severity
      ? (values.severity.split(',') as SeverityLevel[])
      : ['high', 'critical'],
    teamsWebhookUrl: process.env.TEAMS_WEBHOOK_URL,
    snykToken: process.env.SNYK_TOKEN,
    outputPath: values.output,
  };
}

async function main(): Promise<void> {
  const config = parseCliArgs();
  const agent = new SnykPredictorAgent(config);
  const result = await agent.run();
  
  process.exit(result.success ? 0 : 1);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { parseCliArgs };
export default SnykPredictorAgent;
