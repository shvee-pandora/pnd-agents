# Pandora Unit Test Agent Plugin

A comprehensive Claude Code plugin for generating unit tests with full coverage for Pandora repositories.

## Supported Repositories

| Repository | Framework | Testing Stack |
|------------|-----------|---------------|
| pandora-ecom-web | PWA Kit / React | Jest + React Testing Library |
| pandora-sfra | SFCC / SFRA | Mocha + Chai + Sinon |
| pandora-group | Next.js 15 | Jest + React Testing Library + TypeScript |

## Installation

### Option 1: Add to Local Marketplace (Recommended)

1. Create a local marketplace directory:
```bash
mkdir -p ~/claude-plugins
```

2. Copy or symlink this plugin:
```bash
ln -s /path/to/pnd-agents/unit-test-agent-plugin ~/claude-plugins/pandora-unit-test-agent
```

3. In Claude Code, add the marketplace:
```
/plugin marketplace add ~/claude-plugins
```

4. Install the plugin:
```
/plugin install pandora-unit-test-agent
```

### Option 2: Direct Installation

Copy the plugin folder to your Claude plugins directory:
```bash
cp -r unit-test-agent-plugin ~/.claude/plugins/pandora-unit-test-agent
```

## Usage

### Commands

The plugin provides three slash commands for each repository type:

#### PWA (pandora-ecom-web)
```
/unit-test-pwa apps/content/overrides/app/components/entry-points-tile/index.jsx
```

#### SFRA (pandora-sfra)
```
/unit-test-sfra cartridges/app_storefront_custom/cartridge/scripts/checkout/checkoutHelpers.js
```

#### Pandora Group (pandora-group)
```
/unit-test-pgroup app/components/ui/button.tsx
```

### Agents

You can also invoke the agents directly:

```
Use the pwa-unit-test agent to generate tests for apps/product-list/...
Use the sfra-unit-test agent to generate tests for cartridges/...
Use the pandora-group-unit-test agent to generate tests for app/components/...
```

Or use the orchestrator to auto-detect the repository:
```
Use the unit-test-orchestrator agent to generate tests for this file
```

## Features

### Comprehensive Test Generation

- **Happy path tests** - Normal usage scenarios
- **Edge case tests** - Empty inputs, boundary values
- **Error handling tests** - Invalid inputs, API failures
- **Async operation tests** - Loading states, success/error flows
- **User interaction tests** - Clicks, typing, form submissions

### Framework-Specific Patterns

Each agent understands the specific testing patterns for its repository:

**PWA Agent:**
- Chakra UI component mocking
- React Router mocking
- Custom hook testing
- Nx workspace test commands

**SFRA Agent:**
- Demandware API mocking
- SuperModule inheritance patterns
- proxyquire dependency injection
- nyc coverage reporting

**Pandora Group Agent:**
- Next.js feature mocking (navigation, image, intl)
- Radix UI component mocking
- TypeScript type safety
- happy-dom test environment

### Coverage Analysis

All agents target 100% coverage across:
- Statements
- Branches
- Functions
- Lines

## File Structure

```
unit-test-agent-plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── agents/
│   ├── pwa-unit-test.md     # PWA/React agent
│   ├── sfra-unit-test.md    # SFRA/SFCC agent
│   ├── pandora-group-unit-test.md  # Next.js agent
│   └── unit-test-orchestrator.md   # Auto-detection agent
├── commands/
│   ├── unit-test-pwa.md     # /unit-test-pwa command
│   ├── unit-test-sfra.md    # /unit-test-sfra command
│   └── unit-test-pgroup.md  # /unit-test-pgroup command
├── skills/
│   └── unit-test-generation/
│       └── SKILL.md         # Core test generation skill
└── README.md
```

## Running Generated Tests

### PWA (pandora-ecom-web)
```bash
nx test content
nx test product-list
nx test product-details
nx test pandora-shared-app
nx test {app} --coverage
```

### SFRA (pandora-sfra)
```bash
npm run test:unit:pandora
npm run test:cover
npm run test:unit:pandora:mocha -- --grep "pattern"
```

### Pandora Group (pandora-group)
```bash
npm test
npm run test:watch
npm run testcoverage
npm run test:ci
```

## Examples

### Generate Tests for a React Component (PWA)

```
/unit-test-pwa apps/content/overrides/app/components/entry-points-tile/index.jsx
```

Output: Creates `apps/content/overrides/app/components/entry-points-tile/__tests__/index.test.js`

### Generate Tests for an SFRA Module

```
/unit-test-sfra cartridges/int_clutch_sfra_custom/cartridge/scripts/checkout/checkoutHelpers.js
```

Output: Creates `test/unit/tests/int_clutch_sfra_custom/cartridge/scripts/checkout/checkoutHelpers.spec.js`

### Generate Tests for a Next.js Component

```
/unit-test-pgroup app/components/ui/accordion.tsx
```

Output: Creates `app/components/ui/accordion.test.tsx`

## Contributing

To add support for additional repositories or testing frameworks:

1. Create a new agent in `agents/`
2. Create a corresponding command in `commands/`
3. Update `plugin.json` to include the new files
4. Update this README with the new repository details

## License

MIT
