import {
  ScanResult,
  PredictionResult,
  DependencyRisk,
  RiskScore,
  RiskFactor,
  RiskLevel,
  SuggestedFix,
  DependencyInfo,
  HIGH_RISK_PACKAGES,
  SEVERITY_WEIGHTS,
} from '../types/index.js';

export class RiskPredictor {
  private scanResult: ScanResult;

  constructor(scanResult: ScanResult) {
    this.scanResult = scanResult;
  }

  predict(): PredictionResult {
    const dependencyRisks = this.calculateAllRisks();
    
    const highRisk = dependencyRisks.filter((d) => d.riskScore.level === 'high');
    const mediumRisk = dependencyRisks.filter((d) => d.riskScore.level === 'medium');
    const lowRisk = dependencyRisks.filter((d) => d.riskScore.level === 'low');

    const suggestedFixes = this.generateSuggestedFixes(dependencyRisks);
    const riskSummary = this.calculateRiskSummary(highRisk, mediumRisk, lowRisk);

    return {
      scanDate: this.scanResult.scanDate,
      repoName: this.scanResult.repoName,
      riskSummary,
      highRiskDependencies: highRisk.sort((a, b) => b.riskScore.score - a.riskScore.score),
      mediumRiskDependencies: mediumRisk.sort((a, b) => b.riskScore.score - a.riskScore.score),
      lowRiskDependencies: lowRisk.sort((a, b) => b.riskScore.score - a.riskScore.score),
      suggestedFixes,
    };
  }

  private calculateAllRisks(): DependencyRisk[] {
    return this.scanResult.dependencies.map((dep) => this.calculateDependencyRisk(dep));
  }

  private calculateDependencyRisk(dependency: DependencyInfo): DependencyRisk {
    const factors: RiskFactor[] = [];
    let totalScore = 0;

    const vulnFactor = this.calculateVulnerabilityFactor(dependency);
    factors.push(vulnFactor);
    totalScore += vulnFactor.value * vulnFactor.weight;

    const depthFactor = this.calculateDepthFactor(dependency);
    factors.push(depthFactor);
    totalScore += depthFactor.value * depthFactor.weight;

    const knownRiskFactor = this.calculateKnownRiskFactor(dependency);
    factors.push(knownRiskFactor);
    totalScore += knownRiskFactor.value * knownRiskFactor.weight;

    const ageFactor = this.calculateAgeFactor(dependency);
    factors.push(ageFactor);
    totalScore += ageFactor.value * ageFactor.weight;

    const directFactor = this.calculateDirectDependencyFactor(dependency);
    factors.push(directFactor);
    totalScore += directFactor.value * directFactor.weight;

    const normalizedScore = Math.min(100, Math.max(0, totalScore));
    const level = this.scoreToLevel(normalizedScore);

    const riskScore: RiskScore = {
      score: normalizedScore,
      level,
      factors,
    };

    return {
      dependency,
      riskScore,
      suggestedFix: this.getSuggestedFix(dependency),
      urgency: this.determineUrgency(normalizedScore, dependency),
    };
  }

  private calculateVulnerabilityFactor(dependency: DependencyInfo): RiskFactor {
    const vulns = dependency.vulnerabilities;
    let score = 0;

    for (const vuln of vulns) {
      score += SEVERITY_WEIGHTS[vuln.severity] || 0;
    }

    const normalizedValue = Math.min(1, score / 100);

    return {
      name: 'Historical CVE Frequency',
      weight: 0.35,
      value: normalizedValue * 100,
      description: `${vulns.length} known vulnerabilities (${vulns.filter((v) => v.severity === 'critical' || v.severity === 'high').length} critical/high)`,
    };
  }

  private calculateDepthFactor(dependency: DependencyInfo): RiskFactor {
    const depth = dependency.depth;
    const normalizedValue = Math.min(1, depth / 5);

    return {
      name: 'Transitive Dependency Depth',
      weight: 0.2,
      value: normalizedValue * 100,
      description: `Depth level ${depth} in dependency tree`,
    };
  }

  private calculateKnownRiskFactor(dependency: DependencyInfo): RiskFactor {
    const isHighRisk = HIGH_RISK_PACKAGES.some(
      (pkg) => dependency.name.toLowerCase().includes(pkg.toLowerCase())
    );

    return {
      name: 'Known High-Risk Library',
      weight: 0.25,
      value: isHighRisk ? 80 : 0,
      description: isHighRisk
        ? `${dependency.name} is a known high-risk package with historical vulnerabilities`
        : 'Not in known high-risk package list',
    };
  }

  private calculateAgeFactor(dependency: DependencyInfo): RiskFactor {
    const version = dependency.version;
    const majorVersion = parseInt(version.split('.')[0], 10) || 0;
    
    let ageScore = 0;
    if (majorVersion === 0) {
      ageScore = 60;
    } else if (majorVersion < 2) {
      ageScore = 30;
    }

    const hasOldPatterns = /^[0-3]\.\d+\.\d+$/.test(version);
    if (hasOldPatterns && majorVersion < 4) {
      ageScore = Math.max(ageScore, 40);
    }

    return {
      name: 'Package Release Age',
      weight: 0.1,
      value: ageScore,
      description: `Version ${version} - ${ageScore > 30 ? 'potentially outdated' : 'reasonably current'}`,
    };
  }

  private calculateDirectDependencyFactor(dependency: DependencyInfo): RiskFactor {
    return {
      name: 'Direct Dependency Impact',
      weight: 0.1,
      value: dependency.isDirect ? 50 : 20,
      description: dependency.isDirect
        ? 'Direct dependency - easier to update'
        : 'Transitive dependency - may require upstream updates',
    };
  }

  private scoreToLevel(score: number): RiskLevel {
    if (score >= 60) return 'high';
    if (score >= 30) return 'medium';
    return 'low';
  }

  private determineUrgency(
    score: number,
    dependency: DependencyInfo
  ): 'immediate' | 'soon' | 'planned' {
    const hasCritical = dependency.vulnerabilities.some(
      (v) => v.severity === 'critical'
    );
    const hasHigh = dependency.vulnerabilities.some(
      (v) => v.severity === 'high'
    );

    if (hasCritical || score >= 80) return 'immediate';
    if (hasHigh || score >= 50) return 'soon';
    return 'planned';
  }

  private getSuggestedFix(dependency: DependencyInfo): string | null {
    const upgradableVulns = dependency.vulnerabilities.filter(
      (v) => v.isUpgradable && v.fixedIn
    );

    if (upgradableVulns.length > 0) {
      const highestFix = upgradableVulns.reduce((max, v) => {
        if (!max.fixedIn) return v;
        if (!v.fixedIn) return max;
        return v.fixedIn > max.fixedIn ? v : max;
      });

      if (highestFix.fixedIn) {
        return `Upgrade to ${highestFix.fixedIn}`;
      }
    }

    if (dependency.vulnerabilities.length > 0) {
      return 'Review and consider alternative packages';
    }

    return null;
  }

  private generateSuggestedFixes(risks: DependencyRisk[]): SuggestedFix[] {
    const fixes: SuggestedFix[] = [];

    for (const risk of risks) {
      if (risk.riskScore.level === 'low') continue;

      const dep = risk.dependency;
      const criticalVulns = dep.vulnerabilities.filter(
        (v) => v.severity === 'critical'
      );
      const highVulns = dep.vulnerabilities.filter((v) => v.severity === 'high');

      if (criticalVulns.length > 0 || highVulns.length > 0) {
        const fixVersion = this.findBestFixVersion(dep);
        
        fixes.push({
          packageName: dep.name,
          currentVersion: dep.version,
          suggestedVersion: fixVersion || 'latest',
          reason: this.generateFixReason(dep, risk),
          priority: criticalVulns.length > 0 ? 'critical' : 'high',
        });
      } else if (risk.riskScore.level === 'high') {
        fixes.push({
          packageName: dep.name,
          currentVersion: dep.version,
          suggestedVersion: 'latest',
          reason: `High risk score (${risk.riskScore.score.toFixed(0)}) - consider updating`,
          priority: 'medium',
        });
      }
    }

    return fixes.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }

  private findBestFixVersion(dependency: DependencyInfo): string | null {
    const fixVersions = dependency.vulnerabilities
      .filter((v) => v.fixedIn)
      .map((v) => v.fixedIn!)
      .sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));

    return fixVersions[0] || null;
  }

  private generateFixReason(
    dependency: DependencyInfo,
    risk: DependencyRisk
  ): string {
    const criticalCount = dependency.vulnerabilities.filter(
      (v) => v.severity === 'critical'
    ).length;
    const highCount = dependency.vulnerabilities.filter(
      (v) => v.severity === 'high'
    ).length;

    const parts: string[] = [];

    if (criticalCount > 0) {
      parts.push(`${criticalCount} critical CVE${criticalCount > 1 ? 's' : ''}`);
    }
    if (highCount > 0) {
      parts.push(`${highCount} high severity CVE${highCount > 1 ? 's' : ''}`);
    }

    if (parts.length === 0) {
      return `Risk score: ${risk.riskScore.score.toFixed(0)}`;
    }

    return parts.join(', ');
  }

  private calculateRiskSummary(
    highRisk: DependencyRisk[],
    mediumRisk: DependencyRisk[],
    lowRisk: DependencyRisk[]
  ): PredictionResult['riskSummary'] {
    const total = highRisk.length + mediumRisk.length + lowRisk.length;
    
    let overallRiskLevel: RiskLevel = 'low';
    if (highRisk.length > 0) {
      overallRiskLevel = 'high';
    } else if (mediumRisk.length > 5) {
      overallRiskLevel = 'medium';
    }

    const pipelineBlockProbability = this.calculateBlockProbability(
      highRisk,
      mediumRisk
    );

    return {
      totalDependencies: total,
      highRiskCount: highRisk.length,
      mediumRiskCount: mediumRisk.length,
      lowRiskCount: lowRisk.length,
      overallRiskLevel,
      pipelineBlockProbability,
    };
  }

  private calculateBlockProbability(
    highRisk: DependencyRisk[],
    mediumRisk: DependencyRisk[]
  ): number {
    const criticalVulns = highRisk.filter((r) =>
      r.dependency.vulnerabilities.some((v) => v.severity === 'critical')
    ).length;

    const highVulns = highRisk.filter((r) =>
      r.dependency.vulnerabilities.some((v) => v.severity === 'high')
    ).length;

    let probability = 0;
    probability += criticalVulns * 0.3;
    probability += highVulns * 0.15;
    probability += mediumRisk.length * 0.02;

    return Math.min(1, probability);
  }
}

export function predictRisks(scanResult: ScanResult): PredictionResult {
  const predictor = new RiskPredictor(scanResult);
  return predictor.predict();
}
