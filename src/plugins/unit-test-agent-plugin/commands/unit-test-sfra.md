---
description: Generate unit tests for pandora-sfra (SFCC/SFRA) modules using Mocha, Chai, and Sinon.
---

# /unit-test-sfra

Generate comprehensive unit tests for SFCC modules in the pandora-sfra repository.

## Usage

```
/unit-test-sfra [file-path-or-pattern]
```

## Examples

```
/unit-test-sfra cartridges/app_storefront_custom/cartridge/scripts/checkout/checkoutHelpers.js
/unit-test-sfra cartridges/int_adyen_*/cartridge/scripts/**/*.js
/unit-test-sfra --coverage cartridges/plugin_custom_api_pdp
```

## Options

- `--coverage` - Analyze existing coverage and generate tests for uncovered code
- `--with-mocks` - Also generate any missing mock files
- `--dry-run` - Show what tests would be generated without creating files

## What This Command Does

1. **Analyzes** the specified SFCC module(s)
2. **Identifies** exports, dependencies, and DW API usage
3. **Generates** comprehensive test files with:
   - Function unit tests
   - SuperModule inheritance tests
   - DW API mock setup
   - Error handling tests
   - Edge case tests
4. **Creates** test files in `test/unit/tests/` mirroring cartridge structure
5. **Creates** any necessary mock files in `test/unit/mocks/`
6. **Suggests** the command to run the tests

## Test File Location

Tests are created following the pattern:
```
test/unit/tests/{cartridge}/cartridge/scripts/{path}/{file}.spec.js
```

## Framework Details

- **Test Runner**: Mocha
- **Assertions**: Chai (assert style)
- **Mocking**: Sinon + proxyquire
- **Coverage**: nyc (Istanbul)

## Mock Aliases

The test configuration provides these aliases:
- `@mocks/` - test/unit/mocks/
- `@dw_api_mocks/` - test/unit/mocks/dw/
- `@super_module/` - test/unit/mocks/super_module/
- `@cartridge/` - Cartridge paths
- `@integrations/` - Integration cartridge paths

## Run Tests After Generation

```bash
npm run test:unit:pandora
npm run test:cover
npm run test:unit:pandora:mocha -- --grep "ModuleName"
```
