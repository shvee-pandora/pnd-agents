# API Route Create

Create Next.js API routes with proper validation and error handling.

## Context

This command creates Next.js App Router API routes following Pandora's backend patterns, including request validation, error handling, and caching strategies.

## Requirements

- Route path and HTTP methods
- Request/response schemas
- Authentication requirements
- Caching strategy

## Workflow

### 1. Define Route Structure

```markdown
## API Route Design

### Endpoint
- **Path**: /api/{resource}
- **Methods**: GET, POST, PUT, DELETE
- **Authentication**: Required/Optional

### Request
- **Query Parameters**: {params}
- **Body Schema**: {schema}
- **Headers**: {required headers}

### Response
- **Success**: {status code, schema}
- **Errors**: {error codes and messages}
```

### 2. Generate Route Handler

```typescript
// app/api/{resource}/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// Request validation schema
const RequestSchema = z.object({
  // Define request body schema
});

// Response type
interface ApiResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

export async function GET(request: NextRequest) {
  try {
    // Extract query parameters
    const searchParams = request.nextUrl.searchParams;
    const param = searchParams.get('param');

    // Validate parameters
    if (!param) {
      return NextResponse.json<ApiResponse<null>>(
        { error: { code: 'INVALID_PARAMS', message: 'Missing required parameter' } },
        { status: 400 }
      );
    }

    // Fetch data
    const data = await fetchData(param);

    // Return response with caching
    return NextResponse.json<ApiResponse<typeof data>>(
      { data },
      {
        status: 200,
        headers: {
          'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600',
        },
      }
    );
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json<ApiResponse<null>>(
      { error: { code: 'INTERNAL_ERROR', message: 'Internal server error' } },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    // Parse and validate request body
    const body = await request.json();
    const validatedData = RequestSchema.parse(body);

    // Process request
    const result = await processData(validatedData);

    return NextResponse.json<ApiResponse<typeof result>>(
      { data: result },
      { status: 201 }
    );
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json<ApiResponse<null>>(
        { 
          error: { 
            code: 'VALIDATION_ERROR', 
            message: error.errors.map(e => e.message).join(', ') 
          } 
        },
        { status: 400 }
      );
    }

    console.error('API Error:', error);
    return NextResponse.json<ApiResponse<null>>(
      { error: { code: 'INTERNAL_ERROR', message: 'Internal server error' } },
      { status: 500 }
    );
  }
}
```

### 3. Add Dynamic Route Parameters

```typescript
// app/api/{resource}/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

interface RouteParams {
  params: {
    id: string;
  };
}

export async function GET(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = params;

  try {
    const data = await fetchById(id);

    if (!data) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Resource not found' } },
        { status: 404 }
      );
    }

    return NextResponse.json({ data });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Internal server error' } },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = params;

  try {
    const body = await request.json();
    const result = await updateById(id, body);

    return NextResponse.json({ data: result });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Internal server error' } },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = params;

  try {
    await deleteById(id);
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Internal server error' } },
      { status: 500 }
    );
  }
}
```

### 4. Implement Caching Strategies

```typescript
// No caching (dynamic data)
export const dynamic = 'force-dynamic';

// Static caching
export const revalidate = 3600; // 1 hour

// Conditional caching
export async function GET(request: NextRequest) {
  const isPreview = request.nextUrl.searchParams.has('preview');
  
  const cacheControl = isPreview
    ? 'no-store'
    : 'public, s-maxage=300, stale-while-revalidate=600';

  return NextResponse.json(
    { data },
    { headers: { 'Cache-Control': cacheControl } }
  );
}
```

### 5. Add Error Handling Utilities

```typescript
// lib/api/errors.ts
export class ApiError extends Error {
  constructor(
    public code: string,
    public message: string,
    public status: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const handleApiError = (error: unknown) => {
  if (error instanceof ApiError) {
    return NextResponse.json(
      { error: { code: error.code, message: error.message } },
      { status: error.status }
    );
  }

  if (error instanceof z.ZodError) {
    return NextResponse.json(
      { error: { code: 'VALIDATION_ERROR', message: 'Invalid request data' } },
      { status: 400 }
    );
  }

  console.error('Unhandled API Error:', error);
  return NextResponse.json(
    { error: { code: 'INTERNAL_ERROR', message: 'Internal server error' } },
    { status: 500 }
  );
};
```

## Example

### Input
```
Resource: contacts
Methods: GET (list), POST (create), GET/:id, PUT/:id, DELETE/:id
Validation: name (required), email (required, valid email)
```

### Output

```typescript
// app/api/contacts/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const ContactSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  title: z.string().optional(),
});

type Contact = z.infer<typeof ContactSchema>;

interface ApiResponse<T> {
  data?: T;
  error?: { code: string; message: string };
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');

    const contacts = await getContacts({ page, limit });

    return NextResponse.json<ApiResponse<Contact[]>>(
      { data: contacts },
      {
        headers: {
          'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
        },
      }
    );
  } catch (error) {
    console.error('GET /api/contacts error:', error);
    return NextResponse.json<ApiResponse<null>>(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch contacts' } },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = ContactSchema.parse(body);

    const contact = await createContact(validatedData);

    return NextResponse.json<ApiResponse<Contact>>(
      { data: contact },
      { status: 201 }
    );
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json<ApiResponse<null>>(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: error.errors.map(e => `${e.path}: ${e.message}`).join(', '),
          },
        },
        { status: 400 }
      );
    }

    console.error('POST /api/contacts error:', error);
    return NextResponse.json<ApiResponse<null>>(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to create contact' } },
      { status: 500 }
    );
  }
}
```

```typescript
// app/api/contacts/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

interface RouteParams {
  params: { id: string };
}

export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const contact = await getContactById(params.id);

    if (!contact) {
      return NextResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Contact not found' } },
        { status: 404 }
      );
    }

    return NextResponse.json({ data: contact });
  } catch (error) {
    console.error(`GET /api/contacts/${params.id} error:`, error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch contact' } },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest, { params }: RouteParams) {
  try {
    const body = await request.json();
    const contact = await updateContact(params.id, body);

    return NextResponse.json({ data: contact });
  } catch (error) {
    console.error(`PUT /api/contacts/${params.id} error:`, error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to update contact' } },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest, { params }: RouteParams) {
  try {
    await deleteContact(params.id);
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error(`DELETE /api/contacts/${params.id} error:`, error);
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to delete contact' } },
      { status: 500 }
    );
  }
}
```

## Validation Checklist

- [ ] Route path follows REST conventions
- [ ] Request validation with Zod
- [ ] Proper error handling
- [ ] Appropriate HTTP status codes
- [ ] Caching strategy defined
- [ ] TypeScript types for request/response
- [ ] Error logging implemented

## Summary

The api-route-create command generates Next.js API routes with proper validation, error handling, and caching strategies following Pandora's backend patterns.
