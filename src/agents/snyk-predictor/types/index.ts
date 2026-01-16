export type PackageManager = 'npm' | 'pnpm' | 'yarn';

export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';

export type RiskLevel = 'low' | 'medium' | 'high';

export interface SnykVulnerability {
  id: string;
  title: string;
  severity: SeverityLevel;
  packageName: string;
  version: string;
  fixedIn: string | null;
  cvssScore: number | null;
  cwe: string[];
  exploitMaturity: string;
  isUpgradable: boolean;
  isPatchable: boolean;
  introducedThrough: string[];
  description: string;
  publicationTime: string;
}

export interface DependencyInfo {
  name: string;
  version: string;
  isDirect: boolean;
  depth: number;
  lastPublished: string | null;
  weeklyDownloads: number | null;
  maintainers: number;
  hasKnownVulnerabilities: boolean;
  vulnerabilities: SnykVulnerability[];
}

export interface RiskScore {
  score: number;
  level: RiskLevel;
  factors: RiskFactor[];
}

export interface RiskFactor {
  name: string;
  weight: number;
  value: number;
  description: string;
}

export interface DependencyRisk {
  dependency: DependencyInfo;
  riskScore: RiskScore;
  suggestedFix: string | null;
  urgency: 'immediate' | 'soon' | 'planned';
}

export interface ScanResult {
  scanDate: string;
  repoName: string;
  packageManager: PackageManager;
  totalDependencies: number;
  directDependencies: number;
  transitiveDependencies: number;
  vulnerabilities: SnykVulnerability[];
  dependencies: DependencyInfo[];
}

export interface PredictionResult {
  scanDate: string;
  repoName: string;
  riskSummary: RiskSummary;
  highRiskDependencies: DependencyRisk[];
  mediumRiskDependencies: DependencyRisk[];
  lowRiskDependencies: DependencyRisk[];
  suggestedFixes: SuggestedFix[];
}

export interface RiskSummary {
  totalDependencies: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;
  overallRiskLevel: RiskLevel;
  pipelineBlockProbability: number;
}

export interface SuggestedFix {
  packageName: string;
  currentVersion: string;
  suggestedVersion: string;
  reason: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
}

export interface TeamsNotification {
  title: string;
  repoName: string;
  highRiskDependencies: DependencyRisk[];
  suggestedFixes: SuggestedFix[];
  scanDate: string;
}

export interface AgentConfig {
  repo: string;
  repoPath: string;
  packageManager: PackageManager;
  notify: 'teams' | 'none';
  severity: SeverityLevel[];
  teamsWebhookUrl?: string;
  snykToken?: string;
  outputPath?: string;
}

export interface AgentResult {
  success: boolean;
  scanResult: ScanResult | null;
  predictionResult: PredictionResult | null;
  notificationSent: boolean;
  error?: string;
}

export const HIGH_RISK_PACKAGES = [
  'lodash',
  'moment',
  'request',
  'node-fetch',
  'axios',
  'express',
  'minimist',
  'qs',
  'serialize-javascript',
  'ini',
  'y18n',
  'glob-parent',
  'trim-newlines',
  'path-parse',
  'hosted-git-info',
  'ssri',
  'normalize-url',
  'trim',
  'tar',
  'ansi-regex',
];

export const SEVERITY_WEIGHTS: Record<SeverityLevel, number> = {
  critical: 40,
  high: 30,
  medium: 15,
  low: 5,
};
