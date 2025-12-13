# Mock API Create

Create mock API responses for development and testing.

## Context

This command creates mock API services using MSW (Mock Service Worker) for development and testing, following Pandora's patterns.

## Requirements

- API endpoints to mock
- Response schemas
- Realistic test data
- Error scenarios

## Workflow

### 1. Define Mock Data

```typescript
// __mocks__/data/{resource}.ts

export const mock{Resource}s = [
  {
    id: '1',
    name: 'Mock Item 1',
    // ... other fields
  },
  {
    id: '2',
    name: 'Mock Item 2',
    // ... other fields
  },
];

export const mock{Resource}ById = (id: string) => 
  mock{Resource}s.find(item => item.id === id);
```

### 2. Create MSW Handlers

```typescript
// __mocks__/handlers/{resource}.ts
import { http, HttpResponse, delay } from 'msw';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';

export const {resource}Handlers = [
  // GET list
  http.get(`${API_URL}/{resources}`, async ({ request }) => {
    await delay(100); // Simulate network latency
    
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');
    
    const start = (page - 1) * limit;
    const end = start + limit;
    const paginatedData = mock{Resource}s.slice(start, end);
    
    return HttpResponse.json({
      data: paginatedData,
      meta: {
        page,
        limit,
        total: mock{Resource}s.length,
      },
    });
  }),

  // GET by ID
  http.get(`${API_URL}/{resources}/:id`, async ({ params }) => {
    await delay(100);
    
    const { id } = params;
    const item = mock{Resource}ById(id as string);
    
    if (!item) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: '{Resource} not found' } },
        { status: 404 }
      );
    }
    
    return HttpResponse.json({ data: item });
  }),

  // POST create
  http.post(`${API_URL}/{resources}`, async ({ request }) => {
    await delay(200);
    
    const body = await request.json();
    
    // Validate required fields
    if (!body.name) {
      return HttpResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Name is required' } },
        { status: 400 }
      );
    }
    
    const newItem = {
      id: String(mock{Resource}s.length + 1),
      ...body,
      createdAt: new Date().toISOString(),
    };
    
    return HttpResponse.json({ data: newItem }, { status: 201 });
  }),

  // PUT update
  http.put(`${API_URL}/{resources}/:id`, async ({ params, request }) => {
    await delay(200);
    
    const { id } = params;
    const body = await request.json();
    const existingItem = mock{Resource}ById(id as string);
    
    if (!existingItem) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: '{Resource} not found' } },
        { status: 404 }
      );
    }
    
    const updatedItem = { ...existingItem, ...body, updatedAt: new Date().toISOString() };
    
    return HttpResponse.json({ data: updatedItem });
  }),

  // DELETE
  http.delete(`${API_URL}/{resources}/:id`, async ({ params }) => {
    await delay(100);
    
    const { id } = params;
    const existingItem = mock{Resource}ById(id as string);
    
    if (!existingItem) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: '{Resource} not found' } },
        { status: 404 }
      );
    }
    
    return new HttpResponse(null, { status: 204 });
  }),
];
```

### 3. Setup MSW Server

```typescript
// __mocks__/server.ts
import { setupServer } from 'msw/node';
import { {resource}Handlers } from './handlers/{resource}';
// Import other handlers

export const server = setupServer(
  ...{resource}Handlers,
  // ...other handlers
);
```

### 4. Setup MSW Browser

```typescript
// __mocks__/browser.ts
import { setupWorker } from 'msw/browser';
import { {resource}Handlers } from './handlers/{resource}';

export const worker = setupWorker(
  ...{resource}Handlers,
);
```

### 5. Configure Test Setup

```typescript
// jest.setup.ts
import { server } from './__mocks__/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### 6. Create Error Scenarios

```typescript
// __mocks__/handlers/{resource}-errors.ts
import { http, HttpResponse, delay } from 'msw';

export const {resource}ErrorHandlers = [
  // Network error
  http.get(`${API_URL}/{resources}`, () => {
    return HttpResponse.error();
  }),

  // Server error
  http.get(`${API_URL}/{resources}`, () => {
    return HttpResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Server error' } },
      { status: 500 }
    );
  }),

  // Timeout
  http.get(`${API_URL}/{resources}`, async () => {
    await delay('infinite');
  }),

  // Rate limit
  http.get(`${API_URL}/{resources}`, () => {
    return HttpResponse.json(
      { error: { code: 'RATE_LIMIT', message: 'Too many requests' } },
      { status: 429 }
    );
  }),
];
```

## Mock Data Patterns

### Amplience Content Mock
```typescript
// __mocks__/data/amplience-content.ts
export const mockHeroBanner = {
  _meta: {
    schema: 'https://schema-pandora.net/hero-banner',
    name: 'Mock Hero Banner',
    deliveryId: 'mock-hero-123',
    deliveryKey: 'mock-hero-banner',
  },
  title: 'Welcome to Pandora',
  subtitle: 'Discover our latest collection',
  media: {
    desktopImg: {
      id: 'mock-img-desktop',
      name: 'hero-desktop',
      endpoint: 'pandoragroup',
      defaultHost: 'cdn.media.amplience.net',
    },
    mobileImg: {
      id: 'mock-img-mobile',
      name: 'hero-mobile',
      endpoint: 'pandoragroup',
      defaultHost: 'cdn.media.amplience.net',
    },
    desktopMediaType: 'image',
    mobileMediaType: 'image',
    imageAltText: 'Pandora jewelry collection',
  },
  cta: {
    ctaType: 'category',
    ctaValue: 'new-arrivals',
    ctaText: 'Shop Now',
    target: '_self',
  },
};

// __mocks__/handlers/amplience.ts
export const amplienceHandlers = [
  http.get('https://*/content/id/:id', ({ params }) => {
    if (params.id === 'mock-hero-123') {
      return HttpResponse.json({ content: mockHeroBanner });
    }
    return HttpResponse.json(
      { error: 'Content not found' },
      { status: 404 }
    );
  }),

  http.post('https://*/content/filter', async ({ request }) => {
    const body = await request.json();
    // Return mock content based on filter
    return HttpResponse.json({
      responses: [{ content: mockHeroBanner }],
    });
  }),
];
```

### Contact Mock Data
```typescript
// __mocks__/data/contacts.ts
export const mockContacts = [
  {
    id: '1',
    name: 'John Doe',
    title: 'CEO',
    email: 'john.doe@pandora.net',
    phone: '+45 12 34 56 78',
    image: 'https://example.com/john.jpg',
  },
  {
    id: '2',
    name: 'Jane Smith',
    title: 'CTO',
    email: 'jane.smith@pandora.net',
    phone: '+45 87 65 43 21',
    image: 'https://example.com/jane.jpg',
  },
];
```

## Example

### Input
```
Resource: contacts
Endpoints: GET /api/contacts, GET /api/contacts/:id, POST /api/contacts
Fields: id, name, title, email, phone, image
```

### Output

```typescript
// __mocks__/data/contacts.ts
export const mockContacts = [
  {
    id: '1',
    name: 'Alexander Lacik',
    title: 'President and CEO',
    email: 'alexander.lacik@pandora.net',
    phone: '+45 3672 5000',
    image: 'https://cdn.pandora.net/team/alexander-lacik.jpg',
  },
  {
    id: '2',
    name: 'Anders Boyer',
    title: 'CFO',
    email: 'anders.boyer@pandora.net',
    phone: '+45 3672 5001',
    image: 'https://cdn.pandora.net/team/anders-boyer.jpg',
  },
  {
    id: '3',
    name: 'Martino Pessina',
    title: 'Chief Commercial Officer',
    email: 'martino.pessina@pandora.net',
    phone: '+45 3672 5002',
    image: null,
  },
];

export const mockContactById = (id: string) =>
  mockContacts.find(contact => contact.id === id);
```

```typescript
// __mocks__/handlers/contacts.ts
import { http, HttpResponse, delay } from 'msw';
import { mockContacts, mockContactById } from '../data/contacts';

const API_URL = 'http://localhost:3000/api';

export const contactHandlers = [
  http.get(`${API_URL}/contacts`, async ({ request }) => {
    await delay(100);
    
    const url = new URL(request.url);
    const search = url.searchParams.get('search')?.toLowerCase();
    
    let filteredContacts = mockContacts;
    if (search) {
      filteredContacts = mockContacts.filter(
        c => c.name.toLowerCase().includes(search) ||
             c.title.toLowerCase().includes(search)
      );
    }
    
    return HttpResponse.json({
      data: filteredContacts,
      meta: { total: filteredContacts.length },
    });
  }),

  http.get(`${API_URL}/contacts/:id`, async ({ params }) => {
    await delay(100);
    
    const contact = mockContactById(params.id as string);
    
    if (!contact) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Contact not found' } },
        { status: 404 }
      );
    }
    
    return HttpResponse.json({ data: contact });
  }),

  http.post(`${API_URL}/contacts`, async ({ request }) => {
    await delay(200);
    
    const body = await request.json();
    
    if (!body.name || !body.email) {
      return HttpResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Name and email are required' } },
        { status: 400 }
      );
    }
    
    const newContact = {
      id: String(mockContacts.length + 1),
      ...body,
    };
    
    return HttpResponse.json({ data: newContact }, { status: 201 });
  }),
];
```

## Validation Checklist

- [ ] Mock data is realistic
- [ ] All endpoints covered
- [ ] Error scenarios included
- [ ] Proper HTTP status codes
- [ ] Response format matches real API
- [ ] Latency simulation added
- [ ] Test setup configured

## Summary

The mock-api-create command generates MSW mock services for development and testing, including realistic data, error scenarios, and proper configuration.
