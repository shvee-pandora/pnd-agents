# JIRA Storage - REST-First Integration Layer

A token-efficient, agent-friendly JIRA integration layer using direct REST API v3 calls. Designed for autonomous agent workflows with minimal token overhead.

## Why REST-Only (No MCP)

The Model Context Protocol (MCP) introduces significant token overhead due to:

1. **Schema Registration**: MCP requires eager schema definitions that consume tokens even when not used
2. **Metadata Fetching**: MCP tools often fetch full metadata by default, increasing response sizes
3. **Abstraction Cost**: Additional protocol layers add latency and token consumption
4. **Tool Discovery**: MCP's tool listing mechanism adds overhead to every session

By using direct REST API calls, this integration achieves:

- **Minimal Token Footprint**: Only requested fields are fetched
- **Predictable Responses**: No schema overhead or metadata bloat
- **Direct Control**: Fine-grained control over pagination, retries, and field selection
- **Environment Agnostic**: Works in any Node.js environment without MCP dependencies

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Application                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   CachingJIRAStorage                         │
│  (Combines REST + SQLite with automatic fallback)           │
└─────────────────────────────────────────────────────────────┘
                    │                    │
                    ▼                    ▼
┌──────────────────────────┐  ┌──────────────────────────────┐
│      JIRAStorage         │  │       SQLiteStore            │
│  (Primary REST Layer)    │  │   (Local Cache Layer)        │
│                          │  │                              │
│  - Direct REST API v3    │  │  - Offline resilience        │
│  - Rate limit handling   │  │  - Configurable sync         │
│  - Exponential backoff   │  │  - Cache expiry              │
│  - ADF support           │  │  - Pending changes queue     │
│  - Fetch modes           │  │                              │
└──────────────────────────┘  └──────────────────────────────┘
```

## Token Efficiency

### Fetch Modes

The integration supports three fetch modes to minimize token usage:

| Mode | Fields | Use Case |
|------|--------|----------|
| `summary` | key, summary, status, issueType | Listing, quick lookups |
| `details` | + description, assignee, reporter, priority, labels, dates | Issue details view |
| `full` | + components, versions, comments, transitions, custom fields | Complete issue data |

**Default is `summary`** - agents should explicitly request more data only when needed.

### Field Selection

```typescript
// Minimal token usage - only 4 fields
const issue = await jira.getIssue('PROJ-123', 'summary');

// Moderate token usage - 12 fields
const issue = await jira.getIssue('PROJ-123', 'details');

// Full data - use sparingly
const issue = await jira.getIssue('PROJ-123', 'full');
```

### Search Optimization

```typescript
// Paginated search - fetch only what's needed
const result = await jira.search('project = PROJ', {
  maxResults: 10,
  fields: ['key', 'summary', 'status'],
});

// Fetch all (use with caution)
const allIssues = await jira.search('project = PROJ', {
  fetchAll: true,
});
```

## Installation

```bash
# Required
npm install

# Optional: For SQLite caching
npm install better-sqlite3
```

## Usage

### Basic Usage

```typescript
import { JIRAStorage } from './JIRAStorage.js';

const jira = new JIRAStorage({
  baseUrl: 'https://your-org.atlassian.net',
  email: 'your-email@example.com',
  apiToken: process.env.JIRA_API_TOKEN,
});

// Test connection
const user = await jira.testConnection();
console.log(`Connected as ${user.displayName}`);

// Get issue (minimal fields by default)
const issue = await jira.getIssue('PROJ-123');

// Search issues
const results = await jira.search('project = PROJ AND status = "In Progress"');

// Create issue
const newIssue = await jira.createIssue({
  projectKey: 'PROJ',
  issueType: 'Task',
  summary: 'New task from agent',
  description: 'Task description with **markdown** support',
});

// Update issue
await jira.updateIssue('PROJ-123', {
  summary: 'Updated summary',
  labels: ['agent-updated'],
});

// Transition issue
await jira.transitionIssue('PROJ-123', 'Done');

// Add comment
await jira.addComment('PROJ-123', 'Comment from agent');
```

### With SQLite Caching

```typescript
import { JIRAStorage } from './JIRAStorage.js';
import { SQLiteStore, CachingJIRAStorage } from './SQLiteStore.js';

// Initialize primary storage
const jira = new JIRAStorage({
  baseUrl: 'https://your-org.atlassian.net',
  email: 'your-email@example.com',
  apiToken: process.env.JIRA_API_TOKEN,
});

// Initialize cache
const cache = new SQLiteStore({
  dbPath: './jira-cache.db',
  syncIntervalMs: 5 * 60 * 1000, // 5 minutes
  cacheExpiryMs: 24 * 60 * 60 * 1000, // 24 hours
});
await cache.initialize();

// Create caching wrapper
const cachedJira = new CachingJIRAStorage(jira, cache);

// Use normally - automatically falls back to cache when offline
const issue = await cachedJira.getIssue('PROJ-123');

// Start periodic sync
cache.startPeriodicSync(async () => {
  const keys = cache.getAllCachedIssueKeys();
  for (const key of keys) {
    const issue = await jira.getIssue(key, 'full');
    if (issue) {
      cache.cacheIssue(issue);
    }
  }
});

// Clean up
cache.stopPeriodicSync();
cache.close();
```

## API Reference

### JIRAStorage

#### Constructor

```typescript
new JIRAStorage(config: JiraConfig)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `baseUrl` | string | required | JIRA instance URL |
| `email` | string | required | User email for authentication |
| `apiToken` | string | required | JIRA API token |
| `maxRetries` | number | 3 | Maximum retry attempts |
| `retryDelayMs` | number | 1000 | Base delay between retries |
| `timeoutMs` | number | 30000 | Request timeout |

#### Methods

| Method | Description |
|--------|-------------|
| `testConnection()` | Verify API connectivity |
| `getIssue(key, mode?)` | Fetch single issue |
| `search(jql, options?)` | Search issues with JQL |
| `createIssue(payload)` | Create new issue |
| `updateIssue(key, payload)` | Update existing issue |
| `transitionIssue(key, transition)` | Change issue status |
| `addComment(key, body)` | Add comment to issue |
| `getProject(key)` | Get project metadata |
| `getTransitions(key)` | Get available transitions |

### SQLiteStore

#### Constructor

```typescript
new SQLiteStore(config: SQLiteStoreConfig)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dbPath` | string | required | Path to SQLite database file |
| `syncIntervalMs` | number | 300000 | Sync interval (5 min) |
| `cacheExpiryMs` | number | 86400000 | Cache expiry (24 hours) |

#### Methods

| Method | Description |
|--------|-------------|
| `initialize()` | Initialize database |
| `cacheIssue(issue)` | Cache single issue |
| `getCachedIssue(key, mode?)` | Get cached issue |
| `cacheSearchResult(jql, result)` | Cache search result |
| `getCachedSearchResult(jql)` | Get cached search |
| `cleanExpiredCache()` | Remove expired entries |
| `startPeriodicSync(callback)` | Start sync timer |
| `stopPeriodicSync()` | Stop sync timer |
| `close()` | Close database |

## Error Handling

The integration provides structured errors with retry information:

```typescript
try {
  await jira.getIssue('PROJ-123');
} catch (error) {
  if (error.statusCode === 429) {
    console.log(`Rate limited. Retry after ${error.rateLimitInfo.retryAfterMs}ms`);
  } else if (error.isRetryable) {
    console.log('Transient error, can retry');
  } else {
    console.log('Permanent error:', error.message);
  }
}
```

## ADF (Atlassian Document Format) Support

The integration automatically converts markdown-like text to ADF:

```typescript
// Markdown-like input
await jira.addComment('PROJ-123', `
**Bold text** and _italic text_

- Bullet point 1
- Bullet point 2

1. Numbered item 1
2. Numbered item 2

Inline \`code\` is supported
`);

// Or use ADF directly
await jira.addComment('PROJ-123', {
  type: 'doc',
  version: 1,
  content: [
    {
      type: 'paragraph',
      content: [{ type: 'text', text: 'Direct ADF content' }]
    }
  ]
});
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `JIRA_BASE_URL` | JIRA instance URL |
| `JIRA_EMAIL` | User email |
| `JIRA_API_TOKEN` | API token |

## License

MIT
