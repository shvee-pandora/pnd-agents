/**
 * SQLiteStore - Local Persistence Layer for JIRA Data
 *
 * Provides offline resilience and caching for JIRA issues.
 * Enables read-only access when JIRA is unavailable and
 * periodic sync when connectivity is restored.
 *
 * Features:
 * - Local SQLite cache for issue state
 * - Configurable sync interval
 * - Conflict resolution: REST → SQLite priority
 * - Automatic cache expiry
 */

import type {
  JiraIssueFull,
  JiraIssueSummary,
  JiraIssueDetails,
  CachedIssue,
  SQLiteStoreConfig,
  FetchMode,
  SearchResult,
} from './types.js';

const DEFAULT_CONFIG: Partial<SQLiteStoreConfig> = {
  syncIntervalMs: 5 * 60 * 1000,
  cacheExpiryMs: 24 * 60 * 60 * 1000,
};

type Database = {
  exec(sql: string): void;
  prepare(sql: string): Statement;
  close(): void;
};

type Statement = {
  run(...params: unknown[]): { changes: number };
  get(...params: unknown[]): Record<string, unknown> | undefined;
  all(...params: unknown[]): Record<string, unknown>[];
  finalize(): void;
};

export class SQLiteStore {
  private readonly config: Required<SQLiteStoreConfig>;
  private db: Database | null = null;
  private syncTimer: ReturnType<typeof setInterval> | null = null;
  private onSyncCallback: (() => Promise<void>) | null = null;

  constructor(config: SQLiteStoreConfig) {
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
    } as Required<SQLiteStoreConfig>;
  }

  async initialize(): Promise<void> {
    const BetterSqlite3 = await this.loadSqliteModule();
    this.db = new BetterSqlite3(this.config.dbPath) as Database;
    this.createTables();
  }

  private async loadSqliteModule(): Promise<new (path: string) => Database> {
    try {
      const module = await (import('better-sqlite3') as Promise<{ default: new (path: string) => Database }>);
      return module.default;
    } catch {
      throw new Error(
        'better-sqlite3 is required for SQLiteStore. Install it with: npm install better-sqlite3'
      );
    }
  }

  private createTables(): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    this.db.exec(`
      CREATE TABLE IF NOT EXISTS issues (
        key TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        cached_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
      );

      CREATE TABLE IF NOT EXISTS search_cache (
        jql_hash TEXT PRIMARY KEY,
        jql TEXT NOT NULL,
        result TEXT NOT NULL,
        cached_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
      );

      CREATE TABLE IF NOT EXISTS sync_state (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        last_sync_at INTEGER,
        last_sync_status TEXT,
        pending_changes TEXT
      );

      CREATE INDEX IF NOT EXISTS idx_issues_expires_at ON issues(expires_at);
      CREATE INDEX IF NOT EXISTS idx_search_cache_expires_at ON search_cache(expires_at);
    `);

    const syncState = this.db.prepare('SELECT id FROM sync_state WHERE id = 1').get();
    if (!syncState) {
      this.db.prepare(
        'INSERT INTO sync_state (id, last_sync_at, last_sync_status, pending_changes) VALUES (1, NULL, NULL, ?)'
      ).run(JSON.stringify([]));
    }
  }

  cacheIssue(issue: JiraIssueFull): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const now = Date.now();
    const expiresAt = now + this.config.cacheExpiryMs;

    this.db.prepare(`
      INSERT OR REPLACE INTO issues (key, data, cached_at, expires_at)
      VALUES (?, ?, ?, ?)
    `).run(issue.key, JSON.stringify(issue), now, expiresAt);
  }

  cacheIssues(issues: JiraIssueFull[]): void {
    for (const issue of issues) {
      this.cacheIssue(issue);
    }
  }

  getCachedIssue(key: string, mode: FetchMode = 'summary'): JiraIssueSummary | JiraIssueDetails | JiraIssueFull | null {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const row = this.db.prepare(`
      SELECT data, cached_at, expires_at FROM issues
      WHERE key = ? AND expires_at > ?
    `).get(key, Date.now()) as { data: string; cached_at: number; expires_at: number } | undefined;

    if (!row) {
      return null;
    }

    const fullIssue = JSON.parse(row.data) as JiraIssueFull;
    return this.projectIssueToMode(fullIssue, mode);
  }

  private projectIssueToMode(
    issue: JiraIssueFull,
    mode: FetchMode
  ): JiraIssueSummary | JiraIssueDetails | JiraIssueFull {
    if (mode === 'full') {
      return issue;
    }

    if (mode === 'details') {
      const { components, fixVersions, customFields, comments, transitions, ...details } = issue;
      return details as JiraIssueDetails;
    }

    return {
      key: issue.key,
      id: issue.id,
      summary: issue.summary,
      status: issue.status,
      issueType: issue.issueType,
    };
  }

  cacheSearchResult(jql: string, result: SearchResult<JiraIssueSummary>): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const now = Date.now();
    const expiresAt = now + this.config.cacheExpiryMs;
    const jqlHash = this.hashJql(jql);

    this.db.prepare(`
      INSERT OR REPLACE INTO search_cache (jql_hash, jql, result, cached_at, expires_at)
      VALUES (?, ?, ?, ?, ?)
    `).run(jqlHash, jql, JSON.stringify(result), now, expiresAt);
  }

  getCachedSearchResult(jql: string): SearchResult<JiraIssueSummary> | null {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const jqlHash = this.hashJql(jql);

    const row = this.db.prepare(`
      SELECT result FROM search_cache
      WHERE jql_hash = ? AND expires_at > ?
    `).get(jqlHash, Date.now()) as { result: string } | undefined;

    if (!row) {
      return null;
    }

    return JSON.parse(row.result) as SearchResult<JiraIssueSummary>;
  }

  private hashJql(jql: string): string {
    const normalized = jql.trim().toLowerCase();
    let h1 = 0xdeadbeef;
    let h2 = 0x41c6ce57;
    for (let i = 0; i < normalized.length; i++) {
      const char = normalized.charCodeAt(i);
      h1 = Math.imul(h1 ^ char, 2654435761);
      h2 = Math.imul(h2 ^ char, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
    h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
    h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    const combined = 4294967296 * (2097151 & h2) + (h1 >>> 0);
    return combined.toString(36);
  }

  getAllCachedIssueKeys(): string[] {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const rows = this.db.prepare(`
      SELECT key FROM issues WHERE expires_at > ?
    `).all(Date.now()) as Array<{ key: string }>;

    return rows.map(row => row.key);
  }

  getCacheStats(): {
    issueCount: number;
    searchCacheCount: number;
    oldestCacheAt: number | null;
    newestCacheAt: number | null;
  } {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const now = Date.now();

    const issueCount = this.db.prepare(
      'SELECT COUNT(*) as count FROM issues WHERE expires_at > ?'
    ).get(now) as { count: number };

    const searchCacheCount = this.db.prepare(
      'SELECT COUNT(*) as count FROM search_cache WHERE expires_at > ?'
    ).get(now) as { count: number };

    const oldest = this.db.prepare(
      'SELECT MIN(cached_at) as oldest FROM issues WHERE expires_at > ?'
    ).get(now) as { oldest: number | null };

    const newest = this.db.prepare(
      'SELECT MAX(cached_at) as newest FROM issues WHERE expires_at > ?'
    ).get(now) as { newest: number | null };

    return {
      issueCount: issueCount.count,
      searchCacheCount: searchCacheCount.count,
      oldestCacheAt: oldest.oldest,
      newestCacheAt: newest.newest,
    };
  }

  cleanExpiredCache(): number {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const now = Date.now();

    const issuesDeleted = this.db.prepare(
      'DELETE FROM issues WHERE expires_at <= ?'
    ).run(now);

    const searchDeleted = this.db.prepare(
      'DELETE FROM search_cache WHERE expires_at <= ?'
    ).run(now);

    return issuesDeleted.changes + searchDeleted.changes;
  }

  clearAllCache(): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    this.db.exec('DELETE FROM issues');
    this.db.exec('DELETE FROM search_cache');
  }

  invalidateIssue(key: string): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    this.db.prepare('DELETE FROM issues WHERE key = ?').run(key);
  }

  invalidateSearchCache(): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    this.db.exec('DELETE FROM search_cache');
  }

  recordPendingChange(change: {
    type: 'create' | 'update' | 'transition' | 'comment';
    key?: string;
    payload: unknown;
    timestamp: number;
  }): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const row = this.db.prepare(
      'SELECT pending_changes FROM sync_state WHERE id = 1'
    ).get() as { pending_changes: string };

    const pendingChanges = JSON.parse(row.pending_changes) as unknown[];
    pendingChanges.push(change);

    this.db.prepare(
      'UPDATE sync_state SET pending_changes = ? WHERE id = 1'
    ).run(JSON.stringify(pendingChanges));
  }

  getPendingChanges(): Array<{
    type: 'create' | 'update' | 'transition' | 'comment';
    key?: string;
    payload: unknown;
    timestamp: number;
  }> {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const row = this.db.prepare(
      'SELECT pending_changes FROM sync_state WHERE id = 1'
    ).get() as { pending_changes: string };

    return JSON.parse(row.pending_changes);
  }

  clearPendingChanges(): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    this.db.prepare(
      'UPDATE sync_state SET pending_changes = ? WHERE id = 1'
    ).run(JSON.stringify([]));
  }

  updateSyncState(status: 'success' | 'failed' | 'partial'): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    this.db.prepare(
      'UPDATE sync_state SET last_sync_at = ?, last_sync_status = ? WHERE id = 1'
    ).run(Date.now(), status);
  }

  getSyncState(): {
    lastSyncAt: number | null;
    lastSyncStatus: string | null;
    pendingChangesCount: number;
  } {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const row = this.db.prepare(
      'SELECT last_sync_at, last_sync_status, pending_changes FROM sync_state WHERE id = 1'
    ).get() as {
      last_sync_at: number | null;
      last_sync_status: string | null;
      pending_changes: string;
    };

    const pendingChanges = JSON.parse(row.pending_changes) as unknown[];

    return {
      lastSyncAt: row.last_sync_at,
      lastSyncStatus: row.last_sync_status,
      pendingChangesCount: pendingChanges.length,
    };
  }

  startPeriodicSync(onSync: () => Promise<void>): void {
    this.onSyncCallback = onSync;

    if (this.syncTimer) {
      clearInterval(this.syncTimer);
    }

    this.syncTimer = setInterval(async () => {
      if (this.onSyncCallback) {
        try {
          await this.onSyncCallback();
          this.updateSyncState('success');
        } catch {
          this.updateSyncState('failed');
        }
      }
    }, this.config.syncIntervalMs);
  }

  stopPeriodicSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
      this.syncTimer = null;
    }
    this.onSyncCallback = null;
  }

  close(): void {
    this.stopPeriodicSync();
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

export class CachingJIRAStorage {
  private readonly primary: {
    getIssue(key: string, mode?: FetchMode): Promise<JiraIssueSummary | JiraIssueDetails | JiraIssueFull | null>;
    search(jql: string, options?: unknown): Promise<SearchResult<JiraIssueSummary>>;
  };
  private readonly cache: SQLiteStore;
  private isOnline = true;

  constructor(
    primaryStorage: {
      getIssue(key: string, mode?: FetchMode): Promise<JiraIssueSummary | JiraIssueDetails | JiraIssueFull | null>;
      search(jql: string, options?: unknown): Promise<SearchResult<JiraIssueSummary>>;
    },
    cache: SQLiteStore
  ) {
    this.primary = primaryStorage;
    this.cache = cache;
  }

  async getIssue(
    key: string,
    mode: FetchMode = 'summary'
  ): Promise<JiraIssueSummary | JiraIssueDetails | JiraIssueFull | null> {
    if (this.isOnline) {
      try {
        const issue = await this.primary.getIssue(key, 'full');
        if (issue) {
          this.cache.cacheIssue(issue as JiraIssueFull);
          return this.projectToMode(issue as JiraIssueFull, mode);
        }
        return null;
      } catch (error) {
        this.isOnline = false;
        console.warn('JIRA API unavailable, falling back to cache:', error);
      }
    }

    return this.cache.getCachedIssue(key, mode);
  }

  async search(
    jql: string,
    options?: unknown
  ): Promise<SearchResult<JiraIssueSummary>> {
    if (this.isOnline) {
      try {
        const result = await this.primary.search(jql, options);
        this.cache.cacheSearchResult(jql, result);
        return result;
      } catch (error) {
        this.isOnline = false;
        console.warn('JIRA API unavailable, falling back to cache:', error);
      }
    }

    const cached = this.cache.getCachedSearchResult(jql);
    if (cached) {
      return cached;
    }

    return {
      issues: [],
      total: 0,
      startAt: 0,
      maxResults: 0,
      hasMore: false,
    };
  }

  private projectToMode(
    issue: JiraIssueFull,
    mode: FetchMode
  ): JiraIssueSummary | JiraIssueDetails | JiraIssueFull {
    if (mode === 'full') {
      return issue;
    }

    if (mode === 'details') {
      const { components, fixVersions, customFields, comments, transitions, ...details } = issue;
      return details as JiraIssueDetails;
    }

    return {
      key: issue.key,
      id: issue.id,
      summary: issue.summary,
      status: issue.status,
      issueType: issue.issueType,
    };
  }

  setOnlineStatus(online: boolean): void {
    this.isOnline = online;
  }

  getOnlineStatus(): boolean {
    return this.isOnline;
  }

  async checkConnectivity(testConnection?: () => Promise<unknown>): Promise<boolean> {
    try {
      if (testConnection) {
        await testConnection();
      } else {
        await this.primary.getIssue('CONNECTIVITY-CHECK', 'summary');
      }
      this.isOnline = true;
    } catch {
      this.isOnline = false;
    }
    return this.isOnline;
  }
}

export default SQLiteStore;
