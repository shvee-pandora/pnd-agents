import { createTool } from "@mastra/core/tools";
import { z } from "zod";
import {
  AgentConfig,
  PermissionLevel,
  READ_ONLY_TOOLS,
  WRITE_TOOLS,
  TOOL_DESCRIPTIONS,
  type AvailableTool,
} from "../types/agent-config.js";

export const validateConfigTool = createTool({
  id: "validate-agent-config",
  description: "Validates an agent configuration for safety and consistency",
  inputSchema: z.object({
    config: z.object({
      name: z.string(),
      displayName: z.string(),
      description: z.string(),
      responsibility: z.string(),
      allowedTools: z.array(z.string()),
      permissionLevel: z.string(),
      memoryEnabled: z.boolean(),
      executionEnvironment: z.string(),
      outputFormat: z.string(),
      customInstructions: z.string().optional(),
    }),
  }),
  outputSchema: z.object({
    valid: z.boolean(),
    errors: z.array(z.string()),
    warnings: z.array(z.string()),
    sanitizedConfig: z.any().optional(),
  }),
  execute: async ({ context }) => {
    const { config } = context;
    const errors: string[] = [];
    const warnings: string[] = [];

    // Validate name format (snake_case)
    if (!/^[a-z][a-z0-9_]*$/.test(config.name)) {
      errors.push(
        `Agent name "${config.name}" must be in snake_case format (lowercase letters, numbers, underscores)`
      );
    }

    // Validate permission level
    if (!["read_only", "read_write"].includes(config.permissionLevel)) {
      errors.push(
        `Invalid permission level "${config.permissionLevel}". Must be "read_only" or "read_write"`
      );
    }

    // Validate tools against permission level
    if (config.permissionLevel === "read_only") {
      const writeToolsUsed = config.allowedTools.filter((tool: string) =>
        WRITE_TOOLS.includes(tool as AvailableTool)
      );
      if (writeToolsUsed.length > 0) {
        errors.push(
          `Read-only agent cannot use write tools: ${writeToolsUsed.join(", ")}. ` +
            `Allowed read-only tools: ${READ_ONLY_TOOLS.join(", ")}`
        );
      }
    }

    // Validate all tools are known
    const unknownTools = config.allowedTools.filter(
      (tool: string) => !Object.keys(TOOL_DESCRIPTIONS).includes(tool)
    );
    if (unknownTools.length > 0) {
      errors.push(
        `Unknown tools: ${unknownTools.join(", ")}. ` +
          `Available tools: ${Object.keys(TOOL_DESCRIPTIONS).join(", ")}`
      );
    }

    // Validate execution environment
    if (!["local", "ci", "both"].includes(config.executionEnvironment)) {
      errors.push(
        `Invalid execution environment "${config.executionEnvironment}". Must be "local", "ci", or "both"`
      );
    }

    // Validate output format
    if (
      !["report", "suggestions", "structured_data", "markdown"].includes(
        config.outputFormat
      )
    ) {
      errors.push(
        `Invalid output format "${config.outputFormat}". Must be "report", "suggestions", "structured_data", or "markdown"`
      );
    }

    // Warnings
    if (config.allowedTools.length === 0) {
      warnings.push("Agent has no tools configured. It will only be able to generate text.");
    }

    if (config.memoryEnabled && config.executionEnvironment === "ci") {
      warnings.push(
        "Memory is enabled for CI environment. Memory state may not persist between CI runs."
      );
    }

    // Sanitize config if valid
    let sanitizedConfig: AgentConfig | undefined;
    if (errors.length === 0) {
      sanitizedConfig = {
        name: config.name.toLowerCase().replace(/[^a-z0-9_]/g, "_"),
        displayName: config.displayName,
        description: config.description,
        responsibility: config.responsibility,
        allowedTools: config.allowedTools as AvailableTool[],
        permissionLevel: config.permissionLevel as PermissionLevel,
        memoryEnabled: config.memoryEnabled,
        executionEnvironment: config.executionEnvironment as any,
        outputFormat: config.outputFormat as any,
        customInstructions: config.customInstructions,
      };
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      sanitizedConfig,
    };
  },
});
