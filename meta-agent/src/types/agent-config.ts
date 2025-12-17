import { z } from "zod";

export const PermissionLevel = z.enum(["read_only", "read_write"]);
export type PermissionLevel = z.infer<typeof PermissionLevel>;

export const ExecutionEnvironment = z.enum(["local", "ci", "both"]);
export type ExecutionEnvironment = z.infer<typeof ExecutionEnvironment>;

export const OutputFormat = z.enum(["report", "suggestions", "structured_data", "markdown"]);
export type OutputFormat = z.infer<typeof OutputFormat>;

export const AvailableTool = z.enum([
  "filesystem_read",
  "filesystem_write",
  "test_runner",
  "coverage_analyzer",
  "code_parser",
  "git_operations",
  "http_client",
  "database_query",
  "command_runner",
]);
export type AvailableTool = z.infer<typeof AvailableTool>;

export const AgentConfigSchema = z.object({
  name: z.string().min(1).describe("Agent name in snake_case"),
  displayName: z.string().min(1).describe("Human-readable agent name"),
  description: z.string().min(1).describe("Single responsibility description"),
  responsibility: z.string().min(1).describe("What the agent does (single responsibility)"),
  allowedTools: z.array(AvailableTool).min(1).describe("List of allowed tools"),
  permissionLevel: PermissionLevel.describe("Read-only or read-write permissions"),
  memoryEnabled: z.boolean().describe("Whether the agent uses memory"),
  executionEnvironment: ExecutionEnvironment.describe("Where the agent runs"),
  outputFormat: OutputFormat.describe("Output format for the agent"),
  customInstructions: z.string().optional().describe("Additional custom instructions"),
});

export type AgentConfig = z.infer<typeof AgentConfigSchema>;

export const TOOL_DESCRIPTIONS: Record<AvailableTool, { description: string; readOnly: boolean }> = {
  filesystem_read: {
    description: "Read files from the filesystem",
    readOnly: true,
  },
  filesystem_write: {
    description: "Write files to the filesystem",
    readOnly: false,
  },
  test_runner: {
    description: "Run test suites (Jest, Vitest, Playwright)",
    readOnly: true,
  },
  coverage_analyzer: {
    description: "Analyze test coverage reports",
    readOnly: true,
  },
  code_parser: {
    description: "Parse and analyze source code",
    readOnly: true,
  },
  git_operations: {
    description: "Perform git operations (commit, push, branch)",
    readOnly: false,
  },
  http_client: {
    description: "Make HTTP requests to external APIs",
    readOnly: true,
  },
  database_query: {
    description: "Query databases",
    readOnly: true,
  },
  command_runner: {
    description: "Run shell commands",
    readOnly: false,
  },
};

export const READ_ONLY_TOOLS: AvailableTool[] = Object.entries(TOOL_DESCRIPTIONS)
  .filter(([_, config]) => config.readOnly)
  .map(([tool]) => tool as AvailableTool);

export const WRITE_TOOLS: AvailableTool[] = Object.entries(TOOL_DESCRIPTIONS)
  .filter(([_, config]) => !config.readOnly)
  .map(([tool]) => tool as AvailableTool);
