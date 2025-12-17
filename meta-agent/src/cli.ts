#!/usr/bin/env node
/**
 * PND Meta-Agent CLI
 * 
 * A command-line interface for the Mastra-based Meta-Agent that generates
 * pnd-agents compatible agent packages through a guided interview process.
 */

import * as readline from "readline";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import {
  AgentConfig,
  AvailableTool,
  TOOL_DESCRIPTIONS,
  READ_ONLY_TOOLS,
  WRITE_TOOLS,
} from "./types/agent-config.js";
import {
  generateAgentPy,
  generateManifestJson,
  generatePermissionsJson,
  generateToolsJson,
  generateReadme,
} from "./templates/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface InterviewState {
  name: string;
  displayName: string;
  description: string;
  responsibility: string;
  allowedTools: AvailableTool[];
  permissionLevel: "read_only" | "read_write";
  memoryEnabled: boolean;
  executionEnvironment: "local" | "ci" | "both";
  outputFormat: "report" | "suggestions" | "structured_data" | "markdown";
  customInstructions?: string;
}

class MetaAgentCLI {
  private rl: readline.Interface;
  private state: Partial<InterviewState> = {};

  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
  }

  private async question(prompt: string): Promise<string> {
    return new Promise((resolve) => {
      this.rl.question(prompt, (answer) => {
        resolve(answer.trim());
      });
    });
  }

  private async selectFromList<T extends string>(
    prompt: string,
    options: T[],
    descriptions?: Record<T, string>
  ): Promise<T> {
    console.log(`\n${prompt}`);
    options.forEach((opt, i) => {
      const desc = descriptions?.[opt] ? ` - ${descriptions[opt]}` : "";
      console.log(`  ${i + 1}. ${opt}${desc}`);
    });

    while (true) {
      const answer = await this.question("\nEnter number: ");
      const index = parseInt(answer, 10) - 1;
      if (index >= 0 && index < options.length) {
        return options[index];
      }
      console.log("Invalid selection. Please try again.");
    }
  }

  private async selectMultipleFromList<T extends string>(
    prompt: string,
    options: T[],
    descriptions?: Record<T, string>
  ): Promise<T[]> {
    console.log(`\n${prompt}`);
    options.forEach((opt, i) => {
      const desc = descriptions?.[opt] ? ` - ${descriptions[opt]}` : "";
      console.log(`  ${i + 1}. ${opt}${desc}`);
    });

    while (true) {
      const answer = await this.question(
        "\nEnter numbers separated by commas (e.g., 1,3,5): "
      );
      const indices = answer.split(",").map((s) => parseInt(s.trim(), 10) - 1);
      const valid = indices.every((i) => i >= 0 && i < options.length);
      if (valid && indices.length > 0) {
        return indices.map((i) => options[i]);
      }
      console.log("Invalid selection. Please try again.");
    }
  }

  private async confirmYesNo(prompt: string, defaultValue = false): Promise<boolean> {
    const defaultStr = defaultValue ? "[Y/n]" : "[y/N]";
    const answer = await this.question(`${prompt} ${defaultStr}: `);
    if (answer === "") return defaultValue;
    return answer.toLowerCase().startsWith("y");
  }

  private printHeader(): void {
    console.log("\n" + "=".repeat(60));
    console.log("  PND Meta-Agent - Agent Factory");
    console.log("  Generate pnd-agents compatible agent packages");
    console.log("=".repeat(60) + "\n");
  }

  private printSection(title: string): void {
    console.log("\n" + "-".repeat(40));
    console.log(`  ${title}`);
    console.log("-".repeat(40));
  }

  async runInterview(): Promise<InterviewState> {
    this.printHeader();
    console.log("This wizard will guide you through creating a new agent.\n");

    // 1. Agent Name
    this.printSection("1. Agent Identity");
    while (true) {
      const name = await this.question(
        "Agent name (snake_case, e.g., unit_test_advisor): "
      );
      if (/^[a-z][a-z0-9_]*$/.test(name)) {
        this.state.name = name;
        break;
      }
      console.log(
        "Invalid name. Use lowercase letters, numbers, and underscores only."
      );
    }

    this.state.displayName = await this.question(
      "Display name (human-readable, e.g., Unit Test Advisor): "
    );

    // 2. Responsibility
    this.printSection("2. Agent Responsibility");
    this.state.description = await this.question(
      "Brief description (one sentence): "
    );
    this.state.responsibility = await this.question(
      "Single responsibility (what does this agent do?): "
    );

    // 3. Permission Level
    this.printSection("3. Permission Level");
    console.log("\nChoose the permission level for this agent:");
    console.log("  - read_only: Agent can only read data, cannot modify anything");
    console.log("  - read_write: Agent can read and write data");
    this.state.permissionLevel = await this.selectFromList(
      "Select permission level:",
      ["read_only", "read_write"] as const
    );

    // 4. Tools
    this.printSection("4. Allowed Tools");
    const availableTools =
      this.state.permissionLevel === "read_only" ? READ_ONLY_TOOLS : Object.keys(TOOL_DESCRIPTIONS) as AvailableTool[];

    const toolDescriptions: Record<string, string> = {};
    for (const tool of availableTools) {
      toolDescriptions[tool] = TOOL_DESCRIPTIONS[tool].description;
    }

    if (this.state.permissionLevel === "read_only") {
      console.log("\nNote: Read-only agents can only use read-only tools.");
    }

    this.state.allowedTools = await this.selectMultipleFromList(
      "Select the tools this agent can use:",
      availableTools,
      toolDescriptions as Record<AvailableTool, string>
    );

    // 5. Memory
    this.printSection("5. Memory Configuration");
    this.state.memoryEnabled = await this.confirmYesNo(
      "Enable memory (agent can remember previous interactions)?",
      false
    );

    // 6. Execution Environment
    this.printSection("6. Execution Environment");
    this.state.executionEnvironment = await this.selectFromList(
      "Where will this agent run?",
      ["local", "ci", "both"] as const,
      {
        local: "Developer machine only",
        ci: "CI/CD pipeline only",
        both: "Both local and CI environments",
      }
    );

    // 7. Output Format
    this.printSection("7. Output Format");
    this.state.outputFormat = await this.selectFromList(
      "What format should the agent output?",
      ["report", "suggestions", "structured_data", "markdown"] as const,
      {
        report: "Detailed analysis report",
        suggestions: "List of actionable suggestions",
        structured_data: "JSON/structured data",
        markdown: "Markdown-formatted output",
      }
    );

    // 8. Custom Instructions (optional)
    this.printSection("8. Custom Instructions (Optional)");
    const addCustom = await this.confirmYesNo(
      "Add custom instructions for the agent?",
      false
    );
    if (addCustom) {
      this.state.customInstructions = await this.question(
        "Enter custom instructions: "
      );
    }

    return this.state as InterviewState;
  }

  async generateAgent(config: InterviewState, outputDir: string): Promise<void> {
    console.log("\n" + "=".repeat(60));
    console.log("  Generating Agent Package");
    console.log("=".repeat(60) + "\n");

    const agentConfig: AgentConfig = {
      name: config.name,
      displayName: config.displayName,
      description: config.description,
      responsibility: config.responsibility,
      allowedTools: config.allowedTools,
      permissionLevel: config.permissionLevel,
      memoryEnabled: config.memoryEnabled,
      executionEnvironment: config.executionEnvironment,
      outputFormat: config.outputFormat,
      customInstructions: config.customInstructions,
    };

    // Create output directory
    const agentDir = path.join(outputDir, config.name);
    if (!fs.existsSync(agentDir)) {
      fs.mkdirSync(agentDir, { recursive: true });
    }

    const files: { name: string; content: string }[] = [];

    // Generate files
    console.log("Generating agent.py...");
    files.push({ name: "agent.py", content: generateAgentPy(agentConfig) });

    console.log("Generating manifest.json...");
    files.push({
      name: "manifest.json",
      content: JSON.stringify(generateManifestJson(agentConfig), null, 2),
    });

    console.log("Generating permissions.json...");
    files.push({
      name: "permissions.json",
      content: JSON.stringify(generatePermissionsJson(agentConfig), null, 2),
    });

    console.log("Generating tools.json...");
    files.push({
      name: "tools.json",
      content: JSON.stringify(generateToolsJson(agentConfig), null, 2),
    });

    console.log("Generating README.md...");
    files.push({ name: "README.md", content: generateReadme(agentConfig) });

    console.log("Generating __init__.py...");
    const className = config.name
      .split("_")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join("");
    files.push({
      name: "__init__.py",
      content: `"""
${config.displayName}

${config.description}
"""

from .agent import ${className}Agent

__all__ = ["${className}Agent"]
`,
    });

    // Write files
    for (const file of files) {
      const filePath = path.join(agentDir, file.name);
      fs.writeFileSync(filePath, file.content);
      console.log(`  Created: ${filePath}`);
    }

    console.log("\n" + "=".repeat(60));
    console.log("  Agent Generated Successfully!");
    console.log("=".repeat(60));
    console.log(`\nOutput directory: ${agentDir}`);
    console.log("\nGenerated files:");
    files.forEach((f) => console.log(`  - ${f.name}`));
    console.log("\nNext steps:");
    console.log("  1. Review the generated files");
    console.log("  2. Copy to src/agents/ in your pnd-agents installation");
    console.log("  3. Register the agent in workflows/agent_dispatcher.py");
    console.log("  4. Test the agent with: python -m " + config.name);
  }

  async runDemo(): Promise<void> {
    this.printHeader();
    console.log("Running demo: Generating Read-Only Unit Test Advisor Agent\n");

    const demoConfig: InterviewState = {
      name: "unit_test_advisor",
      displayName: "Unit Test Advisor",
      description:
        "A read-only agent that analyzes test coverage and suggests improvements without modifying code.",
      responsibility:
        "Analyze test coverage, identify gaps, and provide actionable suggestions for improving test quality.",
      allowedTools: [
        "filesystem_read",
        "test_runner",
        "coverage_analyzer",
        "code_parser",
      ],
      permissionLevel: "read_only",
      memoryEnabled: false,
      executionEnvironment: "both",
      outputFormat: "report",
    };

    console.log("Demo Configuration:");
    console.log(JSON.stringify(demoConfig, null, 2));

    const outputDir = path.join(__dirname, "..", "..", "generated-agents");
    await this.generateAgent(demoConfig, outputDir);
  }

  async run(): Promise<void> {
    const args = process.argv.slice(2);

    if (args.includes("--demo")) {
      await this.runDemo();
    } else if (args.includes("--help") || args.includes("-h")) {
      console.log(`
PND Meta-Agent CLI

Usage:
  npm run interview    Run the guided interview to create a new agent
  npm run generate-demo    Generate the demo Unit Test Advisor agent

Options:
  --demo    Generate the demo agent without interview
  --help    Show this help message
      `);
    } else {
      const config = await this.runInterview();

      console.log("\n" + "=".repeat(60));
      console.log("  Configuration Summary");
      console.log("=".repeat(60));
      console.log(JSON.stringify(config, null, 2));

      const confirm = await this.confirmYesNo(
        "\nGenerate agent with this configuration?",
        true
      );

      if (confirm) {
        let outputDir = await this.question(
          "Output directory (default: ./generated-agents): "
        );
        if (!outputDir) {
          outputDir = path.join(__dirname, "..", "..", "generated-agents");
        }
        await this.generateAgent(config, outputDir);
      } else {
        console.log("Agent generation cancelled.");
      }
    }

    this.rl.close();
  }
}

// Main entry point
const cli = new MetaAgentCLI();
cli.run().catch((error) => {
  console.error("Error:", error);
  process.exit(1);
});
