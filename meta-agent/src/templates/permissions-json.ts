import { AgentConfig, TOOL_DESCRIPTIONS, READ_ONLY_TOOLS, WRITE_TOOLS, type AvailableTool } from "../types/agent-config.js";

export interface AgentPermissions {
  $schema: string;
  agentName: string;
  permissionLevel: string;
  isReadOnly: boolean;
  constraints: {
    canModifyFiles: boolean;
    canExecuteCommands: boolean;
    canAccessNetwork: boolean;
    canAccessDatabase: boolean;
    canModifyGit: boolean;
  };
  allowedOperations: string[];
  deniedOperations: string[];
  toolPermissions: Record<string, {
    allowed: boolean;
    readOnly: boolean;
    description: string;
  }>;
  runtimeEnforcement: {
    validateBeforeExecution: boolean;
    logAllOperations: boolean;
    failOnViolation: boolean;
  };
}

export function generatePermissionsJson(config: AgentConfig): AgentPermissions {
  const isReadOnly = config.permissionLevel === "read_only";
  
  const toolPermissions: Record<string, { allowed: boolean; readOnly: boolean; description: string }> = {};
  
  for (const [tool, info] of Object.entries(TOOL_DESCRIPTIONS)) {
    const isAllowed = config.allowedTools.includes(tool as AvailableTool);
    toolPermissions[tool] = {
      allowed: isAllowed,
      readOnly: info.readOnly,
      description: info.description,
    };
  }
  
  const allowedOperations: string[] = [];
  const deniedOperations: string[] = [];
  
  // Determine allowed/denied operations based on tools and permission level
  if (config.allowedTools.includes("filesystem_read")) {
    allowedOperations.push("read_files", "list_directories", "check_file_exists");
  }
  
  if (config.allowedTools.includes("filesystem_write") && !isReadOnly) {
    allowedOperations.push("write_files", "create_directories", "delete_files");
  } else {
    deniedOperations.push("write_files", "create_directories", "delete_files");
  }
  
  if (config.allowedTools.includes("test_runner")) {
    allowedOperations.push("run_tests", "analyze_test_output");
  }
  
  if (config.allowedTools.includes("coverage_analyzer")) {
    allowedOperations.push("read_coverage_reports", "analyze_coverage");
  }
  
  if (config.allowedTools.includes("code_parser")) {
    allowedOperations.push("parse_source_code", "extract_code_structure");
  }
  
  if (config.allowedTools.includes("git_operations") && !isReadOnly) {
    allowedOperations.push("git_commit", "git_push", "git_branch");
  } else {
    deniedOperations.push("git_commit", "git_push", "git_branch");
  }
  
  if (config.allowedTools.includes("http_client")) {
    allowedOperations.push("http_get", "http_post");
  }
  
  if (config.allowedTools.includes("database_query")) {
    allowedOperations.push("database_select");
    if (!isReadOnly) {
      allowedOperations.push("database_insert", "database_update", "database_delete");
    } else {
      deniedOperations.push("database_insert", "database_update", "database_delete");
    }
  }
  
  if (config.allowedTools.includes("command_runner") && !isReadOnly) {
    allowedOperations.push("execute_shell_commands");
  } else {
    deniedOperations.push("execute_shell_commands");
  }
  
  return {
    $schema: "https://pnd-agents.pandora.net/schemas/permissions.json",
    agentName: config.name,
    permissionLevel: config.permissionLevel,
    isReadOnly,
    constraints: {
      canModifyFiles: !isReadOnly && config.allowedTools.includes("filesystem_write"),
      canExecuteCommands: !isReadOnly && config.allowedTools.includes("command_runner"),
      canAccessNetwork: config.allowedTools.includes("http_client"),
      canAccessDatabase: config.allowedTools.includes("database_query"),
      canModifyGit: !isReadOnly && config.allowedTools.includes("git_operations"),
    },
    allowedOperations,
    deniedOperations,
    toolPermissions,
    runtimeEnforcement: {
      validateBeforeExecution: true,
      logAllOperations: true,
      failOnViolation: true,
    },
  };
}
