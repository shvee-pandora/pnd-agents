---
description: Validate code quality against SonarCloud rules and fix issues.
---

# /sonar

Analyze code for SonarCloud quality gate compliance, identify issues, and generate fixes.

## Usage

```
/sonar [paste code or describe what to analyze]
```

## Examples

```
/sonar [paste your code here for analysis]
/sonar Check this component for code smells
/sonar Analyze security vulnerabilities in the auth module
```

## What This Command Does

1. **Scans** code for SonarCloud rule violations
2. **Identifies** bugs, vulnerabilities, and code smells
3. **Calculates** technical debt estimates
4. **Checks** code coverage requirements
5. **Validates** duplication thresholds
6. **Generates** fix recommendations

## Output Format

The agent provides:
- Quality gate status (Pass/Fail)
- Issue breakdown by severity
- Bug and vulnerability report
- Code smell inventory
- Duplication analysis
- Technical debt estimate
- Fix suggestions with code

## Issue Categories

- **Bugs**: Logic errors, null pointers, resource leaks
- **Vulnerabilities**: Security issues, injection risks
- **Code Smells**: Maintainability issues, complexity
- **Duplication**: Copy-paste code, redundancy
- **Coverage**: Untested code paths

## Severity Levels

- **Blocker**: Must fix before release
- **Critical**: High priority fixes
- **Major**: Should fix soon
- **Minor**: Nice to fix
- **Info**: Suggestions

## Pandora Quality Gates

- 80% minimum code coverage
- Zero blocker/critical issues
- Less than 3% duplication
- A maintainability rating
- No new security vulnerabilities
