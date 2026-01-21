/**
 * JIRAStorage - REST-first JIRA Integration Layer
 *
 * A token-efficient, agent-friendly JIRA client using direct REST API v3 calls.
 * Optimized for autonomous agent workflows with minimal token overhead.
 *
 * Features:
 * - Direct REST API calls (no MCP dependency)
 * - Rate-limit handling with exponential backoff
 * - Pagination support for large result sets
 * - ADF (Atlassian Document Format) support
 * - Configurable fetch modes (summary, details, full)
 */

import type {
  JiraConfig,
  JiraUser,
  JiraIssueSummary,
  JiraIssueDetails,
  JiraIssueFull,
  JiraProject,
  JiraComment,
  JiraTransition,
  CreateIssuePayload,
  UpdateIssuePayload,
  SearchResult,
  PaginatedSearchOptions,
  FetchMode,
  ADFDocument,
  ADFNode,
  IssueTracker,
  JiraStorageError,
  RateLimitInfo,
} from './types.js';

import { getFieldsForMode, FULL_FIELDS } from './types.js';

const DEFAULT_CONFIG: Partial<JiraConfig> = {
  maxRetries: 3,
  retryDelayMs: 1000,
  timeoutMs: 30000,
};

export class JIRAStorage implements IssueTracker {
  private readonly config: Required<JiraConfig>;
  private readonly baseApiUrl: string;
  private readonly authHeader: string;

  constructor(config: JiraConfig) {
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
    } as Required<JiraConfig>;

    this.baseApiUrl = `${this.config.baseUrl.replace(/\/$/, '')}/rest/api/3`;
    this.authHeader = `Basic ${this.encodeBase64(`${this.config.email}:${this.config.apiToken}`)}`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount = 0
  ): Promise<T> {
    const url = `${this.baseApiUrl}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Authorization': this.authHeader,
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (response.status === 429) {
        const rateLimitInfo = this.parseRateLimitHeaders(response);
        if (retryCount < this.config.maxRetries) {
          const delay = rateLimitInfo.retryAfterMs || this.calculateBackoff(retryCount);
          await this.sleep(delay);
          return this.request<T>(endpoint, options, retryCount + 1);
        }
        throw this.createError(
          `Rate limit exceeded after ${this.config.maxRetries} retries`,
          429,
          rateLimitInfo,
          false
        );
      }

      if (response.status === 404) {
        return null as T;
      }

      if (!response.ok) {
        const errorBody = await response.text();
        const isRetryable = response.status >= 500 && retryCount < this.config.maxRetries;

        if (isRetryable) {
          await this.sleep(this.calculateBackoff(retryCount));
          return this.request<T>(endpoint, options, retryCount + 1);
        }

        throw this.createError(
          `JIRA API error: ${response.status} - ${errorBody}`,
          response.status,
          undefined,
          false
        );
      }

      if (response.status === 204) {
        return undefined as T;
      }

      return response.json() as Promise<T>;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error && error.name === 'AbortError') {
        if (retryCount < this.config.maxRetries) {
          await this.sleep(this.calculateBackoff(retryCount));
          return this.request<T>(endpoint, options, retryCount + 1);
        }
        throw this.createError('Request timeout', undefined, undefined, true);
      }

      if ((error as JiraStorageError).statusCode !== undefined) {
        throw error;
      }

      if (retryCount < this.config.maxRetries) {
        await this.sleep(this.calculateBackoff(retryCount));
        return this.request<T>(endpoint, options, retryCount + 1);
      }

      throw this.createError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        undefined,
        undefined,
        true
      );
    }
  }

  private parseRateLimitHeaders(response: Response): RateLimitInfo {
    const retryAfter = response.headers.get('Retry-After');
    const remaining = response.headers.get('X-RateLimit-Remaining');
    const reset = response.headers.get('X-RateLimit-Reset');

    let retryAfterMs = this.config.retryDelayMs * 2;
    if (retryAfter) {
      const seconds = parseInt(retryAfter, 10);
      if (!isNaN(seconds)) {
        retryAfterMs = seconds * 1000;
      }
    }

    return {
      remaining: remaining ? parseInt(remaining, 10) : 0,
      resetAt: reset ? new Date(parseInt(reset, 10) * 1000) : new Date(Date.now() + retryAfterMs),
      retryAfterMs,
    };
  }

  private calculateBackoff(retryCount: number): number {
    return Math.min(
      this.config.retryDelayMs * Math.pow(2, retryCount) + Math.random() * 1000,
      30000
    );
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private encodeBase64(str: string): string {
    return btoa(unescape(encodeURIComponent(str)));
  }

  private createError(
    message: string,
    statusCode?: number,
    rateLimitInfo?: RateLimitInfo,
    isRetryable = false
  ): JiraStorageError {
    const error = new Error(message) as JiraStorageError;
    error.statusCode = statusCode;
    error.rateLimitInfo = rateLimitInfo;
    error.isRetryable = isRetryable;
    return error;
  }

  async testConnection(): Promise<JiraUser> {
    const response = await this.request<{
      accountId: string;
      displayName: string;
      emailAddress?: string;
      active: boolean;
    }>('/myself');

    return {
      accountId: response.accountId,
      displayName: response.displayName,
      emailAddress: response.emailAddress,
      active: response.active,
    };
  }

  async getIssue(
    key: string,
    mode: FetchMode = 'summary'
  ): Promise<JiraIssueSummary | JiraIssueDetails | JiraIssueFull | null> {
    const fields = getFieldsForMode(mode);
    const expand = mode === 'full' ? 'transitions' : undefined;

    const params = new URLSearchParams();
    params.set('fields', fields.join(','));
    if (expand) {
      params.set('expand', expand);
    }

    const response = await this.request<JiraApiIssue | null>(
      `/issue/${key}?${params.toString()}`
    );

    if (!response) {
      return null;
    }

    return this.mapIssueResponse(response, mode);
  }

  async search(
    jql: string,
    options: PaginatedSearchOptions = {}
  ): Promise<SearchResult<JiraIssueSummary>> {
    const {
      maxResults = 50,
      startAt = 0,
      fields = [...getFieldsForMode('summary')],
      expand = [],
      fetchAll = false,
    } = options;

    if (fetchAll) {
      return this.searchAll(jql, { maxResults: 100, fields, expand });
    }

    const response = await this.request<JiraSearchResponse>('/search', {
      method: 'POST',
      body: JSON.stringify({
        jql,
        maxResults,
        startAt,
        fields,
        expand,
      }),
    });

    const issues = response.issues.map(issue => this.mapIssueResponse(issue, 'summary') as JiraIssueSummary);

    return {
      issues,
      total: response.total,
      startAt: response.startAt,
      maxResults: response.maxResults,
      hasMore: response.startAt + response.issues.length < response.total,
    };
  }

  private async searchAll(
    jql: string,
    options: { maxResults: number; fields: string[]; expand: string[] }
  ): Promise<SearchResult<JiraIssueSummary>> {
    const allIssues: JiraIssueSummary[] = [];
    let startAt = 0;
    let total = 0;

    do {
      const result = await this.search(jql, {
        ...options,
        startAt,
        fetchAll: false,
      });

      allIssues.push(...result.issues);
      total = result.total;
      startAt += result.maxResults;
    } while (startAt < total);

    return {
      issues: allIssues,
      total,
      startAt: 0,
      maxResults: allIssues.length,
      hasMore: false,
    };
  }

  async createIssue(payload: CreateIssuePayload): Promise<JiraIssueSummary> {
    const fields: Record<string, unknown> = {
      project: { key: payload.projectKey },
      issuetype: { name: payload.issueType },
      summary: payload.summary,
    };

    if (payload.description) {
      fields.description = typeof payload.description === 'string'
        ? this.textToADF(payload.description)
        : payload.description;
    }

    if (payload.assigneeAccountId) {
      fields.assignee = { accountId: payload.assigneeAccountId };
    }

    if (payload.priority) {
      fields.priority = { name: payload.priority };
    }

    if (payload.labels) {
      fields.labels = payload.labels;
    }

    if (payload.components) {
      fields.components = payload.components.map(name => ({ name }));
    }

    if (payload.customFields) {
      Object.assign(fields, payload.customFields);
    }

    const response = await this.request<{ id: string; key: string }>('/issue', {
      method: 'POST',
      body: JSON.stringify({ fields }),
    });

    const issue = await this.getIssue(response.key, 'summary');
    return issue as JiraIssueSummary;
  }

  async updateIssue(key: string, payload: UpdateIssuePayload): Promise<boolean> {
    const fields: Record<string, unknown> = {};

    if (payload.summary !== undefined) {
      fields.summary = payload.summary;
    }

    if (payload.description !== undefined) {
      fields.description = typeof payload.description === 'string'
        ? this.textToADF(payload.description)
        : payload.description;
    }

    if (payload.assigneeAccountId !== undefined) {
      fields.assignee = payload.assigneeAccountId
        ? { accountId: payload.assigneeAccountId }
        : null;
    }

    if (payload.priority !== undefined) {
      fields.priority = { name: payload.priority };
    }

    if (payload.labels !== undefined) {
      fields.labels = payload.labels;
    }

    if (payload.components !== undefined) {
      fields.components = payload.components.map(name => ({ name }));
    }

    if (payload.customFields) {
      Object.assign(fields, payload.customFields);
    }

    await this.request(`/issue/${key}`, {
      method: 'PUT',
      body: JSON.stringify({ fields }),
    });

    return true;
  }

  async transitionIssue(key: string, transitionIdOrName: string): Promise<boolean> {
    let transitionId = transitionIdOrName;

    if (!/^\d+$/.test(transitionIdOrName)) {
      const transitions = await this.getTransitions(key);
      const transition = transitions.find(
        t => t.name.toLowerCase() === transitionIdOrName.toLowerCase()
      );
      if (!transition) {
        throw this.createError(
          `Transition "${transitionIdOrName}" not found for issue ${key}`,
          400,
          undefined,
          false
        );
      }
      transitionId = transition.id;
    }

    await this.request(`/issue/${key}/transitions`, {
      method: 'POST',
      body: JSON.stringify({
        transition: { id: transitionId },
      }),
    });

    return true;
  }

  async addComment(key: string, body: string | ADFDocument): Promise<JiraComment> {
    const adfBody = typeof body === 'string' ? this.textToADF(body) : body;

    const response = await this.request<JiraApiComment>(`/issue/${key}/comment`, {
      method: 'POST',
      body: JSON.stringify({ body: adfBody }),
    });

    return {
      id: response.id,
      author: {
        accountId: response.author.accountId,
        displayName: response.author.displayName,
        emailAddress: response.author.emailAddress,
        active: response.author.active,
      },
      body: response.body,
      created: response.created,
      updated: response.updated,
    };
  }

  async getProject(projectKey: string): Promise<JiraProject | null> {
    const response = await this.request<JiraApiProject | null>(`/project/${projectKey}`);

    if (!response) {
      return null;
    }

    return {
      id: response.id,
      key: response.key,
      name: response.name,
      projectTypeKey: response.projectTypeKey,
    };
  }

  async getTransitions(key: string): Promise<JiraTransition[]> {
    const response = await this.request<{ transitions: JiraApiTransition[] }>(
      `/issue/${key}/transitions`
    );

    return response.transitions.map(t => ({
      id: t.id,
      name: t.name,
      to: {
        id: t.to.id,
        name: t.to.name,
      },
    }));
  }

  textToADF(text: string): ADFDocument {
    const paragraphs = text.split(/\n\n+/);
    const content: ADFNode[] = [];

    for (const para of paragraphs) {
      const lines = para.split('\n');

      if (lines.every(line => line.trim().startsWith('- ') || line.trim().startsWith('* '))) {
        const listItems: ADFNode[] = lines
          .filter(line => line.trim())
          .map(line => ({
            type: 'listItem',
            content: [{
              type: 'paragraph',
              content: [{ type: 'text', text: line.trim().slice(2) }],
            }],
          }));

        if (listItems.length > 0) {
          content.push({
            type: 'bulletList',
            content: listItems,
          });
        }
      } else if (lines.every(line => /^\d+\.\s/.test(line.trim()) || !line.trim())) {
        const listItems: ADFNode[] = lines
          .filter(line => line.trim())
          .map(line => ({
            type: 'listItem',
            content: [{
              type: 'paragraph',
              content: [{ type: 'text', text: line.trim().replace(/^\d+\.\s/, '') }],
            }],
          }));

        if (listItems.length > 0) {
          content.push({
            type: 'orderedList',
            content: listItems,
          });
        }
      } else {
        const textContent: ADFNode[] = [];

        for (let i = 0; i < lines.length; i++) {
          if (i > 0) {
            textContent.push({ type: 'hardBreak' });
          }
          textContent.push(...this.parseInlineFormatting(lines[i]));
        }

        if (textContent.length > 0) {
          content.push({
            type: 'paragraph',
            content: textContent,
          });
        }
      }
    }

    return {
      type: 'doc',
      version: 1,
      content,
    };
  }

  private parseInlineFormatting(text: string): ADFNode[] {
    const nodes: ADFNode[] = [];
    let remaining = text;

    while (remaining.length > 0) {
      const boldMatch = remaining.match(/^\*\*(.+?)\*\*/);
      if (boldMatch) {
        nodes.push({
          type: 'text',
          text: boldMatch[1],
          marks: [{ type: 'strong' }],
        });
        remaining = remaining.slice(boldMatch[0].length);
        continue;
      }

      const italicMatch = remaining.match(/^_(.+?)_/);
      if (italicMatch) {
        nodes.push({
          type: 'text',
          text: italicMatch[1],
          marks: [{ type: 'em' }],
        });
        remaining = remaining.slice(italicMatch[0].length);
        continue;
      }

      const codeMatch = remaining.match(/^`(.+?)`/);
      if (codeMatch) {
        nodes.push({
          type: 'text',
          text: codeMatch[1],
          marks: [{ type: 'code' }],
        });
        remaining = remaining.slice(codeMatch[0].length);
        continue;
      }

      const nextSpecial = remaining.search(/\*\*|_|`/);
      if (nextSpecial === -1) {
        nodes.push({ type: 'text', text: remaining });
        break;
      } else if (nextSpecial === 0) {
        nodes.push({ type: 'text', text: remaining[0] });
        remaining = remaining.slice(1);
      } else {
        nodes.push({ type: 'text', text: remaining.slice(0, nextSpecial) });
        remaining = remaining.slice(nextSpecial);
      }
    }

    return nodes;
  }

  adfToText(adf: ADFDocument): string {
    return this.extractTextFromNodes(adf.content);
  }

  private extractTextFromNodes(nodes: ADFNode[]): string {
    let text = '';

    for (const node of nodes) {
      if (node.type === 'text' && node.text) {
        text += node.text;
      } else if (node.type === 'hardBreak') {
        text += '\n';
      } else if (node.type === 'paragraph') {
        if (text && !text.endsWith('\n')) {
          text += '\n';
        }
        if (node.content) {
          text += this.extractTextFromNodes(node.content);
        }
        text += '\n';
      } else if (node.type === 'bulletList' || node.type === 'orderedList') {
        if (node.content) {
          const isOrdered = node.type === 'orderedList';
          node.content.forEach((item, index) => {
            const prefix = isOrdered ? `${index + 1}. ` : '- ';
            if (item.content) {
              text += prefix + this.extractTextFromNodes(item.content).trim() + '\n';
            }
          });
        }
      } else if (node.content) {
        text += this.extractTextFromNodes(node.content);
      }
    }

    return text;
  }

  private mapIssueResponse(
    response: JiraApiIssue,
    mode: FetchMode
  ): JiraIssueSummary | JiraIssueDetails | JiraIssueFull {
    const summary: JiraIssueSummary = {
      key: response.key,
      id: response.id,
      summary: response.fields.summary,
      status: response.fields.status?.name || 'Unknown',
      issueType: response.fields.issuetype?.name || 'Unknown',
    };

    if (mode === 'summary') {
      return summary;
    }

    const details: JiraIssueDetails = {
      ...summary,
      description: response.fields.description || null,
      assignee: response.fields.assignee
        ? {
            accountId: response.fields.assignee.accountId,
            displayName: response.fields.assignee.displayName,
            emailAddress: response.fields.assignee.emailAddress,
            active: response.fields.assignee.active,
          }
        : null,
      reporter: response.fields.reporter
        ? {
            accountId: response.fields.reporter.accountId,
            displayName: response.fields.reporter.displayName,
            emailAddress: response.fields.reporter.emailAddress,
            active: response.fields.reporter.active,
          }
        : null,
      priority: response.fields.priority?.name as JiraIssueDetails['priority'] || null,
      labels: response.fields.labels || [],
      created: response.fields.created || '',
      updated: response.fields.updated || '',
      projectKey: response.fields.project?.key || '',
    };

    if (mode === 'details') {
      return details;
    }

    const full: JiraIssueFull = {
      ...details,
      components: (response.fields.components || []).map(c => ({
        id: c.id,
        name: c.name,
      })),
      fixVersions: (response.fields.fixVersions || []).map(v => ({
        id: v.id,
        name: v.name,
        released: v.released || false,
      })),
      customFields: this.extractCustomFields(response.fields),
      comments: (response.fields.comment?.comments || []).map(c => ({
        id: c.id,
        author: {
          accountId: c.author.accountId,
          displayName: c.author.displayName,
          emailAddress: c.author.emailAddress,
          active: c.author.active,
        },
        body: c.body,
        created: c.created,
        updated: c.updated,
      })),
      transitions: (response.transitions || []).map(t => ({
        id: t.id,
        name: t.name,
        to: {
          id: t.to.id,
          name: t.to.name,
        },
      })),
    };

    return full;
  }

  private extractCustomFields(fields: Record<string, unknown>): Record<string, unknown> {
    const customFields: Record<string, unknown> = {};
    const standardFields = new Set([...FULL_FIELDS, 'id', 'key', 'self']);

    for (const [key, value] of Object.entries(fields)) {
      if (key.startsWith('customfield_') || !standardFields.has(key)) {
        customFields[key] = value;
      }
    }

    return customFields;
  }
}

interface JiraApiIssue {
  id: string;
  key: string;
  fields: {
    summary: string;
    status?: { name: string };
    issuetype?: { name: string };
    description?: ADFDocument;
    assignee?: {
      accountId: string;
      displayName: string;
      emailAddress?: string;
      active: boolean;
    };
    reporter?: {
      accountId: string;
      displayName: string;
      emailAddress?: string;
      active: boolean;
    };
    priority?: { name: string };
    labels?: string[];
    created?: string;
    updated?: string;
    project?: { key: string };
    components?: Array<{ id: string; name: string }>;
    fixVersions?: Array<{ id: string; name: string; released?: boolean }>;
    comment?: {
      comments: JiraApiComment[];
    };
    [key: string]: unknown;
  };
  transitions?: JiraApiTransition[];
}

interface JiraApiComment {
  id: string;
  author: {
    accountId: string;
    displayName: string;
    emailAddress?: string;
    active: boolean;
  };
  body: ADFDocument;
  created: string;
  updated: string;
}

interface JiraApiTransition {
  id: string;
  name: string;
  to: {
    id: string;
    name: string;
  };
}

interface JiraApiProject {
  id: string;
  key: string;
  name: string;
  projectTypeKey: string;
}

interface JiraSearchResponse {
  issues: JiraApiIssue[];
  total: number;
  startAt: number;
  maxResults: number;
}

export default JIRAStorage;
