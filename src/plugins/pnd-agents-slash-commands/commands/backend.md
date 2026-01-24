---
description: Generate API routes, serverless functions, and backend logic with TypeScript.
---

# /backend

Generate production-ready API routes, serverless functions, and backend logic following Pandora's backend standards.

## Usage

```
/backend [describe the API endpoint or backend functionality needed]
```

## Examples

```
/backend Create a REST API endpoint for user profile CRUD operations
/backend Build a serverless function to process order webhooks
/backend Generate an API route for product search with filtering
```

## What This Command Does

1. **Analyzes** your API requirements
2. **Generates** TypeScript API route code
3. **Includes** request/response validation
4. **Adds** error handling and logging
5. **Implements** authentication checks where needed
6. **Provides** OpenAPI documentation

## Output Format

The agent provides:
- Complete API route implementation
- Request/response TypeScript interfaces
- Validation schemas (Zod or Yup)
- Error handling middleware
- Authentication integration
- API documentation (OpenAPI/Swagger)

## Framework Support

- **Next.js API Routes** (App Router)
- **Express.js** middleware patterns
- **Serverless Functions** (Vercel, AWS Lambda)
- **tRPC** for type-safe APIs
- **GraphQL** resolvers

## API Features

- RESTful design patterns
- Request validation
- Response serialization
- Rate limiting setup
- Caching strategies
- Error response formatting

## Pandora Backend Standards

- TypeScript strict mode
- Zod schema validation
- Structured error responses
- Request logging with correlation IDs
- Environment-based configuration
- Secure header handling
