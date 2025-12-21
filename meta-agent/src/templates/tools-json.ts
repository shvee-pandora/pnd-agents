import { AgentConfig, TOOL_DESCRIPTIONS, type AvailableTool } from "../types/agent-config.js";

export interface ToolDefinition {
  id: string;
  name: string;
  description: string;
  readOnly: boolean;
  inputSchema: {
    type: string;
    properties: Record<string, { type: string; description: string }>;
    required: string[];
  };
  outputSchema: {
    type: string;
    properties: Record<string, { type: string; description: string }>;
  };
}

export interface AgentTools {
  $schema: string;
  agentName: string;
  tools: ToolDefinition[];
}

const TOOL_SCHEMAS: Record<AvailableTool, Omit<ToolDefinition, "id" | "readOnly">> = {
  filesystem_read: {
    name: "Filesystem Read",
    description: "Read files from the filesystem",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Path to the file or directory" },
        pattern: { type: "string", description: "Glob pattern for file matching" },
      },
      required: ["path"],
    },
    outputSchema: {
      type: "object",
      properties: {
        content: { type: "string", description: "File content" },
        files: { type: "array", description: "List of files" },
      },
    },
  },
  filesystem_write: {
    name: "Filesystem Write",
    description: "Write files to the filesystem",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Path to write the file" },
        content: { type: "string", description: "Content to write" },
      },
      required: ["path", "content"],
    },
    outputSchema: {
      type: "object",
      properties: {
        success: { type: "boolean", description: "Whether the write succeeded" },
        path: { type: "string", description: "Path of the written file" },
      },
    },
  },
  test_runner: {
    name: "Test Runner",
    description: "Run test suites (Jest, Vitest, Playwright)",
    inputSchema: {
      type: "object",
      properties: {
        command: { type: "string", description: "Test command to run" },
        timeout: { type: "number", description: "Timeout in seconds" },
      },
      required: [],
    },
    outputSchema: {
      type: "object",
      properties: {
        success: { type: "boolean", description: "Whether tests passed" },
        stdout: { type: "string", description: "Test output" },
        stderr: { type: "string", description: "Error output" },
        return_code: { type: "number", description: "Exit code" },
      },
    },
  },
  coverage_analyzer: {
    name: "Coverage Analyzer",
    description: "Analyze test coverage reports",
    inputSchema: {
      type: "object",
      properties: {
        coverage_path: { type: "string", description: "Path to coverage report" },
      },
      required: [],
    },
    outputSchema: {
      type: "object",
      properties: {
        lines: { type: "number", description: "Line coverage percentage" },
        statements: { type: "number", description: "Statement coverage percentage" },
        functions: { type: "number", description: "Function coverage percentage" },
        branches: { type: "number", description: "Branch coverage percentage" },
      },
    },
  },
  code_parser: {
    name: "Code Parser",
    description: "Parse and analyze source code",
    inputSchema: {
      type: "object",
      properties: {
        file_path: { type: "string", description: "Path to source file" },
      },
      required: ["file_path"],
    },
    outputSchema: {
      type: "object",
      properties: {
        functions: { type: "array", description: "List of functions" },
        classes: { type: "array", description: "List of classes" },
        lines: { type: "number", description: "Number of lines" },
      },
    },
  },
  git_operations: {
    name: "Git Operations",
    description: "Perform git operations (commit, push, branch)",
    inputSchema: {
      type: "object",
      properties: {
        operation: { type: "string", description: "Git operation (commit, push, branch)" },
        message: { type: "string", description: "Commit message" },
        branch: { type: "string", description: "Branch name" },
      },
      required: ["operation"],
    },
    outputSchema: {
      type: "object",
      properties: {
        success: { type: "boolean", description: "Whether operation succeeded" },
        output: { type: "string", description: "Git output" },
      },
    },
  },
  http_client: {
    name: "HTTP Client",
    description: "Make HTTP requests to external APIs",
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string", description: "URL to request" },
        method: { type: "string", description: "HTTP method" },
        headers: { type: "object", description: "Request headers" },
        body: { type: "string", description: "Request body" },
      },
      required: ["url"],
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "number", description: "HTTP status code" },
        body: { type: "string", description: "Response body" },
        headers: { type: "object", description: "Response headers" },
      },
    },
  },
  database_query: {
    name: "Database Query",
    description: "Query databases",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "SQL query" },
        params: { type: "array", description: "Query parameters" },
      },
      required: ["query"],
    },
    outputSchema: {
      type: "object",
      properties: {
        rows: { type: "array", description: "Query results" },
        rowCount: { type: "number", description: "Number of rows" },
      },
    },
  },
  command_runner: {
    name: "Command Runner",
    description: "Run shell commands",
    inputSchema: {
      type: "object",
      properties: {
        command: { type: "string", description: "Shell command to run" },
        timeout: { type: "number", description: "Timeout in seconds" },
      },
      required: ["command"],
    },
    outputSchema: {
      type: "object",
      properties: {
        success: { type: "boolean", description: "Whether command succeeded" },
        stdout: { type: "string", description: "Standard output" },
        stderr: { type: "string", description: "Standard error" },
        return_code: { type: "number", description: "Exit code" },
      },
    },
  },
};

export function generateToolsJson(config: AgentConfig): AgentTools {
  const tools: ToolDefinition[] = [];
  
  for (const toolId of config.allowedTools) {
    const schema = TOOL_SCHEMAS[toolId];
    const toolInfo = TOOL_DESCRIPTIONS[toolId];
    
    if (schema && toolInfo) {
      tools.push({
        id: toolId,
        readOnly: toolInfo.readOnly,
        ...schema,
      });
    }
  }
  
  return {
    $schema: "https://pnd-agents.pandora.net/schemas/tools.json",
    agentName: config.name,
    tools,
  };
}
