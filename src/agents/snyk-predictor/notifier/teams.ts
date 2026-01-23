import {
  TeamsNotification,
  DependencyRisk,
  SuggestedFix,
  PredictionResult,
} from '../types/index.js';

interface TeamsAdaptiveCard {
  type: string;
  attachments: TeamsAttachment[];
}

interface TeamsAttachment {
  contentType: string;
  contentUrl: string | null;
  content: AdaptiveCardContent;
}

interface AdaptiveCardContent {
  $schema: string;
  type: string;
  version: string;
  body: AdaptiveCardElement[];
  actions?: AdaptiveCardAction[];
}

interface AdaptiveCardElement {
  type: string;
  text?: string;
  weight?: string;
  size?: string;
  color?: string;
  wrap?: boolean;
  spacing?: string;
  separator?: boolean;
  items?: AdaptiveCardElement[];
  columns?: AdaptiveCardColumn[];
  facts?: AdaptiveCardFact[];
}

interface AdaptiveCardColumn {
  type: string;
  width: string;
  items: AdaptiveCardElement[];
}

interface AdaptiveCardFact {
  title: string;
  value: string;
}

interface AdaptiveCardAction {
  type: string;
  title: string;
  url?: string;
}

export class TeamsNotifier {
  private webhookUrl: string;

  constructor(webhookUrl?: string) {
    this.webhookUrl = webhookUrl || process.env.TEAMS_WEBHOOK_URL || '';
    
    if (!this.webhookUrl) {
      throw new Error('TEAMS_WEBHOOK_URL environment variable is not set');
    }
  }

  async sendNotification(prediction: PredictionResult): Promise<boolean> {
    const notification: TeamsNotification = {
      title: 'Snyk Early Warning (Daily Scan)',
      repoName: prediction.repoName,
      highRiskDependencies: prediction.highRiskDependencies,
      mediumRiskDependencies: prediction.mediumRiskDependencies,
      suggestedFixes: prediction.suggestedFixes,
      scanDate: prediction.scanDate,
    };

    const card = this.buildAdaptiveCard(notification);

    try {
      const response = await fetch(this.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(card),
      });

      if (!response.ok) {
        console.error(`Teams notification failed: ${response.status} ${response.statusText}`);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Failed to send Teams notification:', error);
      return false;
    }
  }

  private buildAdaptiveCard(notification: TeamsNotification): TeamsAdaptiveCard {
    const hasHighRisk = notification.highRiskDependencies.length > 0;
    const hasMediumRisk = notification.mediumRiskDependencies.length > 0;
    const hasAnyRisk = hasHighRisk || hasMediumRisk;
    const headerColor = hasHighRisk ? 'attention' : hasMediumRisk ? 'warning' : 'good';

    const body: AdaptiveCardElement[] = [
      {
        type: 'TextBlock',
        text: `⚠️ ${notification.title}`,
        weight: 'bolder',
        size: 'large',
        color: headerColor,
      },
      {
        type: 'FactSet',
        facts: [
          {
            title: 'Repository',
            value: notification.repoName,
          },
          {
            title: 'Scan Date',
            value: new Date(notification.scanDate).toLocaleString(),
          },
        ],
      },
    ];

    if (hasHighRisk) {
      body.push({
        type: 'TextBlock',
        text: '🔴 High Risk Dependencies',
        weight: 'bolder',
        size: 'medium',
        spacing: 'large',
        separator: true,
      });

      for (const risk of notification.highRiskDependencies.slice(0, 5)) {
        body.push(this.buildDependencyBlock(risk));
      }

      if (notification.highRiskDependencies.length > 5) {
        body.push({
          type: 'TextBlock',
          text: `... and ${notification.highRiskDependencies.length - 5} more high-risk dependencies`,
          wrap: true,
          color: 'attention',
        });
      }
    } else if (!hasMediumRisk) {
      body.push({
        type: 'TextBlock',
        text: '✅ No High Risk Dependencies Found',
        weight: 'bolder',
        size: 'medium',
        spacing: 'large',
        separator: true,
        color: 'good',
      });
      body.push({
        type: 'TextBlock',
        text: 'All dependencies passed the security scan. No immediate action required.',
        wrap: true,
        size: 'small',
      });
    }

    // Add medium risk dependencies section
    if (hasMediumRisk) {
      body.push({
        type: 'TextBlock',
        text: '🟡 Medium Risk Dependencies',
        weight: 'bolder',
        size: 'medium',
        spacing: 'large',
        separator: true,
      });

      for (const risk of notification.mediumRiskDependencies.slice(0, 5)) {
        body.push(this.buildDependencyBlock(risk));
      }

      if (notification.mediumRiskDependencies.length > 5) {
        body.push({
          type: 'TextBlock',
          text: `... and ${notification.mediumRiskDependencies.length - 5} more medium-risk dependencies`,
          wrap: true,
          color: 'warning',
        });
      }
    }

    if (notification.suggestedFixes.length > 0) {
      body.push({
        type: 'TextBlock',
        text: '📋 Suggested Fixes',
        weight: 'bolder',
        size: 'medium',
        spacing: 'large',
        separator: true,
      });

      for (const fix of notification.suggestedFixes.slice(0, 5)) {
        body.push(this.buildFixBlock(fix));
      }
    }

    if (hasHighRisk) {
      body.push({
        type: 'TextBlock',
        text: '**Action:** Fix before next deployment',
        wrap: true,
        spacing: 'large',
        color: 'attention',
      });
    } else if (hasMediumRisk) {
      body.push({
        type: 'TextBlock',
        text: '**Action:** Review and plan fixes for medium-risk dependencies',
        wrap: true,
        spacing: 'large',
        color: 'warning',
      });
    } else {
      body.push({
        type: 'TextBlock',
        text: '**Status:** Ready for deployment',
        wrap: true,
        spacing: 'large',
        color: 'good',
      });
    }

    return {
      type: 'message',
      attachments: [
        {
          contentType: 'application/vnd.microsoft.card.adaptive',
          contentUrl: null,
          content: {
            $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
            type: 'AdaptiveCard',
            version: '1.4',
            body,
          },
        },
      ],
    };
  }

  private buildDependencyBlock(risk: DependencyRisk): AdaptiveCardElement {
    const dep = risk.dependency;
    const vulnCount = dep.vulnerabilities.length;
    const criticalCount = dep.vulnerabilities.filter(
      (v) => v.severity === 'critical'
    ).length;
    const highCount = dep.vulnerabilities.filter(
      (v) => v.severity === 'high'
    ).length;

    let vulnSummary = '';
    if (criticalCount > 0) {
      vulnSummary += `${criticalCount} critical`;
    }
    if (highCount > 0) {
      vulnSummary += vulnSummary ? `, ${highCount} high` : `${highCount} high`;
    }
    if (vulnSummary) {
      vulnSummary = ` (${vulnSummary})`;
    }

    // Get the most severe vulnerability for detailed info
    const mostSevereVuln = dep.vulnerabilities.find((v) => v.severity === 'critical') 
      || dep.vulnerabilities.find((v) => v.severity === 'high')
      || dep.vulnerabilities[0];

    const items: AdaptiveCardElement[] = [
      {
        type: 'TextBlock',
        text: `• **${dep.name}@${dep.version}**`,
        wrap: true,
      },
    ];

    // Add vulnerability title
    if (mostSevereVuln?.title) {
      items.push({
        type: 'TextBlock',
        text: `🔍 **${mostSevereVuln.title}**`,
        wrap: true,
        size: 'small',
        color: 'attention',
      });
    }

    // Add severity and CVSS score
    if (mostSevereVuln) {
      const severityEmoji = mostSevereVuln.severity === 'critical' ? '🔴' : 
                           mostSevereVuln.severity === 'high' ? '🟠' : 
                           mostSevereVuln.severity === 'medium' ? '🟡' : '🟢';
      const cvssText = mostSevereVuln.cvssScore ? ` | CVSS: ${mostSevereVuln.cvssScore}` : '';
      items.push({
        type: 'TextBlock',
        text: `${severityEmoji} Severity: **${mostSevereVuln.severity.toUpperCase()}**${cvssText}`,
        wrap: true,
        size: 'small',
      });
    }

    // Add CVE/CWE identifiers
    if (mostSevereVuln?.cwe && mostSevereVuln.cwe.length > 0) {
      const cweText = mostSevereVuln.cwe.slice(0, 3).join(', ');
      items.push({
        type: 'TextBlock',
        text: `📋 CWE: ${cweText}${mostSevereVuln.cwe.length > 3 ? '...' : ''}`,
        wrap: true,
        size: 'small',
      });
    }

    // Add brief description
    if (mostSevereVuln?.description) {
      items.push({
        type: 'TextBlock',
        text: this.truncateText(mostSevereVuln.description, 200),
        wrap: true,
        size: 'small',
      });
    }

    // Add dependency path (introduced through)
    if (mostSevereVuln?.introducedThrough && mostSevereVuln.introducedThrough.length > 0) {
      const pathText = mostSevereVuln.introducedThrough.slice(0, 3).join(' > ');
      items.push({
        type: 'TextBlock',
        text: `📦 Path: ${pathText}${mostSevereVuln.introducedThrough.length > 3 ? '...' : ''}`,
        wrap: true,
        size: 'small',
        color: 'accent',
      });
    }

    // Add upgrade/patch status
    if (mostSevereVuln) {
      const upgradeStatus = mostSevereVuln.isUpgradable ? '✅ Upgradable' : 
                           mostSevereVuln.isPatchable ? '🔧 Patchable' : '❌ No fix available';
      const fixedInText = mostSevereVuln.fixedIn ? ` (fixed in ${mostSevereVuln.fixedIn})` : '';
      items.push({
        type: 'TextBlock',
        text: `${upgradeStatus}${fixedInText}`,
        wrap: true,
        size: 'small',
        color: mostSevereVuln.isUpgradable || mostSevereVuln.isPatchable ? 'good' : 'attention',
      });
    }

    // Add fix suggestion if available
    if (risk.suggestedFix) {
      items.push({
        type: 'TextBlock',
        text: `💡 **Fix:** ${risk.suggestedFix}`,
        wrap: true,
        size: 'small',
        color: 'accent',
      });
    }

    // Add total vulnerability count if more than one
    if (vulnCount > 1) {
      items.push({
        type: 'TextBlock',
        text: `⚠️ Total: ${vulnCount} vulnerabilities${vulnSummary}`,
        wrap: true,
        size: 'small',
      });
    }

    return {
      type: 'ColumnSet',
      columns: [
        {
          type: 'Column',
          width: 'stretch',
          items,
        },
      ],
    };
  }

  private truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }

  private buildFixBlock(fix: SuggestedFix): AdaptiveCardElement {
    const priorityEmoji =
      fix.priority === 'critical'
        ? '🔴'
        : fix.priority === 'high'
          ? '🟠'
          : '🟡';

    return {
      type: 'TextBlock',
      text: `${priorityEmoji} **${fix.packageName}@${fix.currentVersion}** → upgrade to \`${fix.suggestedVersion}\``,
      wrap: true,
      size: 'small',
    };
  }
}

export async function sendTeamsNotification(
  prediction: PredictionResult,
  webhookUrl?: string
): Promise<boolean> {
  const notifier = new TeamsNotifier(webhookUrl);
  return notifier.sendNotification(prediction);
}
