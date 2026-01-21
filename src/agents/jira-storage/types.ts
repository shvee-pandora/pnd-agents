/**
 * JIRA Storage Types
 *
 * Shared interfaces for the REST-first JIRA integration layer.
 * Optimized for low token usage and agent-friendly workflows.
 */

export type FetchMode = 'summary' | 'details' | 'full';

export type IssuePriority = 'Highest' | 'High' | 'Medium' | 'Low' | 'Lowest';

export type IssueStatus = string;

export interface JiraConfig {
  baseUrl: string;
  email: string;
  apiToken: string;
  maxRetries?: number;
  retryDelayMs?: number;
  timeoutMs?: number;
}

export interface JiraUser {
  accountId: string;
  displayName: string;
  emailAddress?: string;
  active: boolean;
}

export interface JiraIssueSummary {
  key: string;
  id: string;
  summary: string;
  status: IssueStatus;
  issueType: string;
}

export interface JiraIssueDetails extends JiraIssueSummary {
  description?: ADFDocument | null;
  assignee?: JiraUser | null;
  reporter?: JiraUser | null;
  priority?: IssuePriority | null;
  labels: string[];
  created: string;
  updated: string;
  projectKey: string;
}

export interface JiraIssueFull extends JiraIssueDetails {
  components: JiraComponent[];
  fixVersions: JiraVersion[];
  customFields: Record<string, unknown>;
  comments: JiraComment[];
  transitions: JiraTransition[];
}

export interface JiraComponent {
  id: string;
  name: string;
}

export interface JiraVersion {
  id: string;
  name: string;
  released: boolean;
}

export interface JiraComment {
  id: string;
  author: JiraUser;
  body: ADFDocument;
  created: string;
  updated: string;
}

export interface JiraTransition {
  id: string;
  name: string;
  to: {
    id: string;
    name: string;
  };
}

export interface JiraProject {
  id: string;
  key: string;
  name: string;
  projectTypeKey: string;
}

export interface ADFDocument {
  type: 'doc';
  version: 1;
  content: ADFNode[];
}

export interface ADFNode {
  type: string;
  content?: ADFNode[];
  text?: string;
  marks?: ADFMark[];
  attrs?: Record<string, unknown>;
}

export interface ADFMark {
  type: string;
  attrs?: Record<string, unknown>;
}

export interface CreateIssuePayload {
  projectKey: string;
  issueType: string;
  summary: string;
  description?: string | ADFDocument;
  assigneeAccountId?: string;
  priority?: IssuePriority;
  labels?: string[];
  components?: string[];
  customFields?: Record<string, unknown>;
}

export interface UpdateIssuePayload {
  summary?: string;
  description?: string | ADFDocument;
  assigneeAccountId?: string;
  priority?: IssuePriority;
  labels?: string[];
  components?: string[];
  customFields?: Record<string, unknown>;
}

export interface SearchOptions {
  maxResults?: number;
  startAt?: number;
  fields?: string[];
  expand?: string[];
}

export interface SearchResult<T> {
  issues: T[];
  total: number;
  startAt: number;
  maxResults: number;
  hasMore: boolean;
}

export interface PaginatedSearchOptions extends SearchOptions {
  fetchAll?: boolean;
}

export interface RateLimitInfo {
  remaining: number;
  resetAt: Date;
  retryAfterMs: number;
}

export interface JiraStorageError extends Error {
  statusCode?: number;
  rateLimitInfo?: RateLimitInfo;
  isRetryable: boolean;
}

export const SUMMARY_FIELDS = [
  'key',
  'summary',
  'status',
  'issuetype',
] as const;

export const DETAILS_FIELDS = [
  ...SUMMARY_FIELDS,
  'description',
  'assignee',
  'reporter',
  'priority',
  'labels',
  'created',
  'updated',
  'project',
] as const;

export const FULL_FIELDS = [
  ...DETAILS_FIELDS,
  'components',
  'fixVersions',
  'comment',
  'transitions',
] as const;

export function getFieldsForMode(mode: FetchMode): readonly string[] {
  switch (mode) {
    case 'summary':
      return SUMMARY_FIELDS;
    case 'details':
      return DETAILS_FIELDS;
    case 'full':
      return FULL_FIELDS;
    default:
      return SUMMARY_FIELDS;
  }
}

export interface IssueTracker {
  testConnection(): Promise<JiraUser>;

  getIssue(key: string, mode?: FetchMode): Promise<JiraIssueSummary | JiraIssueDetails | JiraIssueFull | null>;

  search(jql: string, options?: PaginatedSearchOptions): Promise<SearchResult<JiraIssueSummary>>;

  createIssue(payload: CreateIssuePayload): Promise<JiraIssueSummary>;

  updateIssue(key: string, payload: UpdateIssuePayload): Promise<boolean>;

  transitionIssue(key: string, transitionIdOrName: string): Promise<boolean>;

  addComment(key: string, body: string | ADFDocument): Promise<JiraComment>;

  getProject(projectKey: string): Promise<JiraProject | null>;

  getTransitions(key: string): Promise<JiraTransition[]>;
}

export interface CachedIssue {
  key: string;
  data: JiraIssueFull;
  cachedAt: number;
  expiresAt: number;
}

export interface SQLiteStoreConfig {
  dbPath: string;
  syncIntervalMs?: number;
  cacheExpiryMs?: number;
}
