---
description: Search products, manage commerce data, and integrate with Salesforce Commerce Cloud.
---

# /commerce

Work with Salesforce Commerce Cloud (SFCC) data, search products, and generate commerce-related code.

## Usage

```
/commerce [describe the commerce functionality or product query]
```

## Examples

```
/commerce Search for products in the rings category with price under $500
/commerce Generate a product listing component with SFCC integration
/commerce Create a cart management hook for SFCC
```

## What This Command Does

1. **Queries** product catalogs and categories
2. **Generates** commerce integration code
3. **Creates** product display components
4. **Implements** cart and checkout logic
5. **Handles** pricing and promotions
6. **Integrates** with SFCC APIs

## Output Format

The agent provides:
- Product search results (when querying)
- Commerce component code
- API integration snippets
- Type definitions for commerce data
- Hook implementations
- Error handling for commerce operations

## Commerce Features

- **Product Search**: Full-text and filtered search
- **Category Navigation**: Hierarchical browsing
- **Cart Management**: Add, update, remove items
- **Pricing**: Price books, promotions, discounts
- **Inventory**: Stock availability checks
- **Checkout**: Order creation and processing

## SFCC Integration

- OCAPI/SCAPI endpoints
- Authentication handling
- Session management
- Basket operations
- Customer data handling

## Pandora Commerce Standards

- Type-safe product interfaces
- Optimistic UI updates
- Error recovery patterns
- Price formatting utilities
- Inventory status handling
