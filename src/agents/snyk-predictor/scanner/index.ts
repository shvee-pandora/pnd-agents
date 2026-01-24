import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import {
  PackageManager,
  ScanResult,
  SnykVulnerability,
  DependencyInfo,
  SeverityLevel,
} from '../types/index.js';

interface PackageJson {
  name?: string;
  dependencies?: Record<string, string>;
  devDependencies?: Record<string, string>;
}

interface SnykTestResult {
  ok: boolean;
  vulnerabilities?: SnykVulnerabilityRaw[];
  dependencyCount?: number;
}

interface SnykVulnerabilityRaw {
  id: string;
  title: string;
  severity: string;
  packageName: string;
  version: string;
  fixedIn?: string[];
  CVSSv3?: string;
  identifiers?: { CWE?: string[] };
  exploit?: string;
  isUpgradable?: boolean;
  isPatchable?: boolean;
  from?: string[];
  description?: string;
  publicationTime?: string;
}

export class DependencyScanner {
  private repoPath: string;
  private packageManager: PackageManager;
  private snykToken: string | undefined;

  constructor(
    repoPath: string,
    packageManager: PackageManager,
    snykToken?: string
  ) {
    this.repoPath = path.resolve(repoPath);
    this.packageManager = packageManager;
    this.snykToken = snykToken || process.env.SNYK_TOKEN;
  }

  async scan(): Promise<ScanResult> {
    const packageJson = this.readPackageJson();
    const repoName = packageJson.name || path.basename(this.repoPath);

    const dependencies = this.parseDependencies(packageJson);
    const vulnerabilities = await this.runSnykTest();

    this.enrichDependenciesWithVulnerabilities(dependencies, vulnerabilities);

    const directDeps = dependencies.filter((d) => d.isDirect);
    const transitiveDeps = dependencies.filter((d) => !d.isDirect);

    return {
      scanDate: new Date().toISOString(),
      repoName,
      packageManager: this.packageManager,
      totalDependencies: dependencies.length,
      directDependencies: directDeps.length,
      transitiveDependencies: transitiveDeps.length,
      vulnerabilities,
      dependencies,
    };
  }

  private readPackageJson(): PackageJson {
    const packageJsonPath = path.join(this.repoPath, 'package.json');
    if (!fs.existsSync(packageJsonPath)) {
      throw new Error(`package.json not found at ${packageJsonPath}`);
    }
    return JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
  }

  private parseDependencies(packageJson: PackageJson): DependencyInfo[] {
    const dependencies: DependencyInfo[] = [];
    const lockFile = this.readLockFile();

    const directDeps = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies,
    };

    for (const [name, versionRange] of Object.entries(directDeps)) {
      const resolvedVersion = this.resolveVersion(name, versionRange, lockFile);
      dependencies.push({
        name,
        version: resolvedVersion,
        isDirect: true,
        depth: 0,
        lastPublished: null,
        weeklyDownloads: null,
        maintainers: 0,
        hasKnownVulnerabilities: false,
        vulnerabilities: [],
      });
    }

    const transitiveDeps = this.parseTransitiveDependencies(lockFile, directDeps);
    dependencies.push(...transitiveDeps);

    return dependencies;
  }

  private readLockFile(): Record<string, unknown> {
    const lockFiles: Record<PackageManager, string> = {
      npm: 'package-lock.json',
      pnpm: 'pnpm-lock.yaml',
      yarn: 'yarn.lock',
    };

    const lockFileName = lockFiles[this.packageManager];
    const lockFilePath = path.join(this.repoPath, lockFileName);

    if (!fs.existsSync(lockFilePath)) {
      console.warn(`Lock file ${lockFileName} not found, using package.json only`);
      return {};
    }

    if (this.packageManager === 'pnpm') {
      return this.parsePnpmLock(lockFilePath);
    } else if (this.packageManager === 'yarn') {
      return this.parseYarnLock(lockFilePath);
    } else {
      return JSON.parse(fs.readFileSync(lockFilePath, 'utf-8'));
    }
  }

  private parsePnpmLock(lockFilePath: string): Record<string, unknown> {
    const content = fs.readFileSync(lockFilePath, 'utf-8');
    const packages: Record<string, { version: string; dependencies?: Record<string, string> }> = {};
    
    const lines = content.split('\n');
    let currentPackage = '';
    let inPackages = false;
    
    for (const line of lines) {
      if (line.startsWith('packages:')) {
        inPackages = true;
        continue;
      }
      
      if (inPackages && line.match(/^  ['"]?([^:'"]+)['"]?:/)) {
        const match = line.match(/^  ['"]?([^:'"]+)['"]?:/);
        if (match) {
          currentPackage = match[1].replace(/^\//, '');
          packages[currentPackage] = { version: '', dependencies: {} };
        }
      }
      
      if (currentPackage && line.includes('version:')) {
        const versionMatch = line.match(/version:\s*['"]?([^'"]+)['"]?/);
        if (versionMatch) {
          packages[currentPackage].version = versionMatch[1];
        }
      }
    }
    
    return { packages };
  }

  private parseYarnLock(lockFilePath: string): Record<string, unknown> {
    const content = fs.readFileSync(lockFilePath, 'utf-8');
    const packages: Record<string, { version: string }> = {};
    
    const blocks = content.split('\n\n');
    for (const block of blocks) {
      const lines = block.split('\n');
      if (lines.length < 2) continue;
      
      const headerMatch = lines[0].match(/^"?([^@]+)@/);
      const versionMatch = block.match(/version\s+"([^"]+)"/);
      
      if (headerMatch && versionMatch) {
        packages[headerMatch[1]] = { version: versionMatch[1] };
      }
    }
    
    return { packages };
  }

  private resolveVersion(
    name: string,
    versionRange: string,
    lockFile: Record<string, unknown>
  ): string {
    if (this.packageManager === 'npm') {
      const npmLock = lockFile as { packages?: Record<string, { version?: string }> };
      const pkg = npmLock.packages?.[`node_modules/${name}`];
      if (pkg?.version) return pkg.version;
    }
    
    return versionRange.replace(/^[\^~]/, '');
  }

  private parseTransitiveDependencies(
    lockFile: Record<string, unknown>,
    directDeps: Record<string, string>
  ): DependencyInfo[] {
    const transitive: DependencyInfo[] = [];
    const seen = new Set(Object.keys(directDeps));

    if (this.packageManager === 'npm') {
      const npmLock = lockFile as { packages?: Record<string, { version?: string; dependencies?: Record<string, string> }> };
      const packages = npmLock.packages || {};
      
      for (const [pkgPath, pkgInfo] of Object.entries(packages)) {
        if (!pkgPath.startsWith('node_modules/')) continue;
        
        const name = pkgPath.replace('node_modules/', '').split('/node_modules/').pop() || '';
        if (seen.has(name) || !name) continue;
        
        seen.add(name);
        const depth = (pkgPath.match(/node_modules/g) || []).length;
        
        transitive.push({
          name,
          version: pkgInfo.version || 'unknown',
          isDirect: false,
          depth,
          lastPublished: null,
          weeklyDownloads: null,
          maintainers: 0,
          hasKnownVulnerabilities: false,
          vulnerabilities: [],
        });
      }
    }

    return transitive;
  }

  private async runSnykTest(): Promise<SnykVulnerability[]> {
    const vulnerabilities: SnykVulnerability[] = [];

    try {
      const env = this.snykToken ? { ...process.env, SNYK_TOKEN: this.snykToken } : process.env;
      
      const result = execSync('snyk test --json', {
        cwd: this.repoPath,
        env,
        maxBuffer: 50 * 1024 * 1024,
        encoding: 'utf-8',
      });

      const snykResult: SnykTestResult = JSON.parse(result);
      
      if (snykResult.vulnerabilities) {
        for (const vuln of snykResult.vulnerabilities) {
          vulnerabilities.push(this.mapSnykVulnerability(vuln));
        }
      }
    } catch (error) {
      if (error instanceof Error && 'stdout' in error) {
        try {
          const execError = error as { stdout?: string };
          const snykResult: SnykTestResult = JSON.parse(execError.stdout || '{}');
          if (snykResult.vulnerabilities) {
            for (const vuln of snykResult.vulnerabilities) {
              vulnerabilities.push(this.mapSnykVulnerability(vuln));
            }
          }
        } catch {
          console.warn('Failed to parse Snyk output, continuing without vulnerability data');
        }
      } else {
        console.warn('Snyk test failed, continuing without vulnerability data:', error);
      }
    }

    return vulnerabilities;
  }

  private mapSnykVulnerability(vuln: SnykVulnerabilityRaw): SnykVulnerability {
    return {
      id: vuln.id,
      title: vuln.title,
      severity: vuln.severity as SeverityLevel,
      packageName: vuln.packageName,
      version: vuln.version,
      fixedIn: vuln.fixedIn?.[0] || null,
      cvssScore: vuln.CVSSv3 ? parseFloat(vuln.CVSSv3.split('/')[0]) : null,
      cwe: vuln.identifiers?.CWE || [],
      exploitMaturity: vuln.exploit || 'unknown',
      isUpgradable: vuln.isUpgradable || false,
      isPatchable: vuln.isPatchable || false,
      introducedThrough: vuln.from || [],
      description: vuln.description || '',
      publicationTime: vuln.publicationTime || '',
    };
  }

  private enrichDependenciesWithVulnerabilities(
    dependencies: DependencyInfo[],
    vulnerabilities: SnykVulnerability[]
  ): void {
    const vulnByPackage = new Map<string, SnykVulnerability[]>();
    
    for (const vuln of vulnerabilities) {
      const key = vuln.packageName;
      if (!vulnByPackage.has(key)) {
        vulnByPackage.set(key, []);
      }
      vulnByPackage.get(key)!.push(vuln);
    }

    for (const dep of dependencies) {
      const depVulns = vulnByPackage.get(dep.name) || [];
      dep.vulnerabilities = depVulns;
      dep.hasKnownVulnerabilities = depVulns.length > 0;
    }
  }
}

export async function scanDependencies(
  repoPath: string,
  packageManager: PackageManager,
  snykToken?: string
): Promise<ScanResult> {
  const scanner = new DependencyScanner(repoPath, packageManager, snykToken);
  return scanner.scan();
}
