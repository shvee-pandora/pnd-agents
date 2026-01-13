---
description: Convert PRD documents into Jira-ready epics, stories, and acceptance criteria.
---

# /prd-to-jira

Transform Product Requirements Documents (PRDs) into structured Jira tickets with epics, user stories, and Gherkin acceptance criteria.

## Usage

```
/prd-to-jira [paste your PRD content or describe the feature]
```

## Examples

```
/prd-to-jira [paste PRD content here]
/prd-to-jira Convert the checkout redesign requirements into Jira stories
/prd-to-jira Break down the new loyalty program feature into epics
```

## What This Command Does

1. **Parses** PRD content and requirements
2. **Identifies** epics and feature boundaries
3. **Creates** user stories with proper format
4. **Writes** Gherkin acceptance criteria
5. **Maps** dependencies between stories
6. **Estimates** complexity and effort

## Output Format

The agent provides:
- Epic definitions with descriptions
- User stories in "As a... I want... So that..." format
- Acceptance criteria in Gherkin (Given/When/Then)
- Story point estimates
- Dependency mapping
- Risk identification
- Technical considerations

## Story Components

- **Epic**: High-level feature container
- **Story**: User-focused requirement
- **Acceptance Criteria**: Testable conditions
- **Dependencies**: Blocking relationships
- **Labels**: Categorization tags

## Gherkin Format

```gherkin
Given [precondition]
When [action]
Then [expected result]
```

## Pandora PM Standards

- Clear, testable acceptance criteria
- No technical jargon in stories
- Realistic story point estimates
- Explicit dependency documentation
- Risk and assumption callouts
