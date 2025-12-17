import { createTool } from "@mastra/core/tools";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import {
  AgentConfig,
  TOOL_DESCRIPTIONS,
  type AvailableTool,
} from "../types/agent-config.js";
import {
  generateAgentPy,
  generateManifestJson,
  generatePermissionsJson,
  generateToolsJson,
  generateReadme,
} from "../templates/index.js";

export const generateAgentTool = createTool({
  id: "generate-agent-package",
  description: "Generates a complete pnd-agents compatible agent package from configuration",
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
    outputDir: z.string().describe("Directory to output the generated agent package"),
  }),
  outputSchema: z.object({
    success: z.boolean(),
    outputPath: z.string(),
    generatedFiles: z.array(z.string()),
    error: z.string().optional(),
  }),
  execute: async ({ context }) => {
    const { config, outputDir } = context;
    const agentConfig = config as AgentConfig;

    try {
      // Create output directory
      const agentDir = path.join(outputDir, agentConfig.name);
      if (!fs.existsSync(agentDir)) {
        fs.mkdirSync(agentDir, { recursive: true });
      }

      const generatedFiles: string[] = [];

      // Generate agent.py
      const agentPy = generateAgentPy(agentConfig);
      const agentPyPath = path.join(agentDir, "agent.py");
      fs.writeFileSync(agentPyPath, agentPy);
      generatedFiles.push("agent.py");

      // Generate manifest.json
      const manifestJson = generateManifestJson(agentConfig);
      const manifestPath = path.join(agentDir, "manifest.json");
      fs.writeFileSync(manifestPath, JSON.stringify(manifestJson, null, 2));
      generatedFiles.push("manifest.json");

      // Generate permissions.json
      const permissionsJson = generatePermissionsJson(agentConfig);
      const permissionsPath = path.join(agentDir, "permissions.json");
      fs.writeFileSync(permissionsPath, JSON.stringify(permissionsJson, null, 2));
      generatedFiles.push("permissions.json");

      // Generate tools.json
      const toolsJson = generateToolsJson(agentConfig);
      const toolsPath = path.join(agentDir, "tools.json");
      fs.writeFileSync(toolsPath, JSON.stringify(toolsJson, null, 2));
      generatedFiles.push("tools.json");

      // Generate README.md
      const readme = generateReadme(agentConfig);
      const readmePath = path.join(agentDir, "README.md");
      fs.writeFileSync(readmePath, readme);
      generatedFiles.push("README.md");

      // Generate __init__.py
      const initPy = `"""
${agentConfig.displayName}

${agentConfig.description}
"""

from .agent import ${toPascalCase(agentConfig.name)}Agent

__all__ = ["${toPascalCase(agentConfig.name)}Agent"]
`;
      const initPath = path.join(agentDir, "__init__.py");
      fs.writeFileSync(initPath, initPy);
      generatedFiles.push("__init__.py");

      return {
        success: true,
        outputPath: agentDir,
        generatedFiles,
      };
    } catch (error) {
      return {
        success: false,
        outputPath: "",
        generatedFiles: [],
        error: error instanceof Error ? error.message : String(error),
      };
    }
  },
});

function toPascalCase(str: string): string {
  return str
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join("");
}
