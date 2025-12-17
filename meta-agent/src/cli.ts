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

// Paths relative to meta-agent directory
const PND_AGENTS_ROOT = path.join(__dirname, "..", "..");
const SRC_AGENTS_DIR = path.join(PND_AGENTS_ROOT, "src", "agents");
const AGENTS_INIT_FILE = path.join(SRC_AGENTS_DIR, "__init__.py");
const AGENT_DISPATCHER_FILE = path.join(PND_AGENTS_ROOT, "workflows", "agent_dispatcher.py");

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

  private toPascalCase(name: string): string {
    return name
      .split("_")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join("");
  }

  private canAutoRegister(): boolean {
    return fs.existsSync(AGENTS_INIT_FILE) && fs.existsSync(AGENT_DISPATCHER_FILE);
  }

  private async registerInAgentsInit(agentName: string, className: string): Promise<boolean> {
    try {
      let content = fs.readFileSync(AGENTS_INIT_FILE, "utf-8");
      
      // Check if already registered
      if (content.includes(`from .${agentName}`)) {
        console.log(`  Agent already imported in __init__.py`);
        return true;
      }

      // Find the last import line and add new import after it
      const importPattern = /^from \.\w+ import \w+$/gm;
      const imports = content.match(importPattern);
      if (imports && imports.length > 0) {
        const lastImport = imports[imports.length - 1];
        const newImport = `from .${agentName} import ${className}Agent`;
        content = content.replace(lastImport, `${lastImport}\n${newImport}`);
      }

      // Add to __all__ list
      const allPattern = /__all__ = \[([\s\S]*?)\]/;
      const allMatch = content.match(allPattern);
      if (allMatch) {
        const allContent = allMatch[1];
        if (!allContent.includes(`"${className}Agent"`)) {
          // Find the last entry and add new one
          const newAllContent = allContent.trimEnd() + `\n    "${className}Agent",`;
          content = content.replace(allPattern, `__all__ = [${newAllContent}\n]`);
        }
      }

      fs.writeFileSync(AGENTS_INIT_FILE, content);
      console.log(`  Updated: ${AGENTS_INIT_FILE}`);
      return true;
    } catch (error) {
      console.error(`  Failed to update __init__.py: ${error}`);
      return false;
    }
  }

  private async registerInDispatcher(agentName: string, className: string): Promise<boolean> {
    try {
      let content = fs.readFileSync(AGENT_DISPATCHER_FILE, "utf-8");
      
      // Check if already registered
      if (content.includes(`"${agentName}"`)) {
        console.log(`  Agent already registered in agent_dispatcher.py`);
        return true;
      }

      // Find _register_default_handlers and add new registration
      const registerPattern = /self\.register\("(\w+)", self\._\w+_handler\)/g;
      const registers = [...content.matchAll(registerPattern)];
      if (registers.length > 0) {
        const lastRegister = registers[registers.length - 1][0];
        const newRegister = `self.register("${agentName}", self._${agentName}_handler)`;
        content = content.replace(lastRegister, `${lastRegister}\n        ${newRegister}`);
      }

      // Add the handler method before the helper methods (before _extract_component_name)
      const handlerCode = `
    def _${agentName}_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        ${className} Agent handler.
        
        Generated by PND Meta-Agent.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        metadata = context.get("metadata", {})
        
        try:
            from agents.${agentName} import ${className}Agent
            
            agent = ${className}Agent()
            result = agent.run({
                "task_description": task,
                "input_data": input_data,
                "metadata": metadata,
            })
            
            return AgentResult(
                status=result.status if hasattr(result, 'status') else result.get("status", "success"),
                data=result.data if hasattr(result, 'data') else result.get("data", {}),
                error=result.error if hasattr(result, 'error') else result.get("error"),
            )
        except ImportError:
            return AgentResult(
                status="error",
                error=f"${className}Agent not found. Ensure it's installed in src/agents/${agentName}/"
            )
        except Exception as e:
            return AgentResult(
                status="error",
                error=f"${className} agent failed: {str(e)}"
            )
`;

      // Find the position to insert (before _extract_component_name or at end of class)
      const insertPattern = /(\n    def _extract_component_name)/;
      if (content.match(insertPattern)) {
        content = content.replace(insertPattern, `${handlerCode}$1`);
      } else {
        // Fallback: add before the last function outside the class
        const classEndPattern = /(\ndef get_dispatcher)/;
        if (content.match(classEndPattern)) {
          content = content.replace(classEndPattern, `${handlerCode}$1`);
        }
      }

      fs.writeFileSync(AGENT_DISPATCHER_FILE, content);
      console.log(`  Updated: ${AGENT_DISPATCHER_FILE}`);
      return true;
    } catch (error) {
      console.error(`  Failed to update agent_dispatcher.py: ${error}`);
      return false;
    }
  }

  async registerAgent(agentName: string, className: string): Promise<boolean> {
    console.log("\n" + "=".repeat(60));
    console.log("  Registering Agent in pnd-agents");
    console.log("=".repeat(60) + "\n");

    const initSuccess = await this.registerInAgentsInit(agentName, className);
    const dispatcherSuccess = await this.registerInDispatcher(agentName, className);

    if (initSuccess && dispatcherSuccess) {
      console.log("\n  Agent registered successfully!");
      console.log(`\n  You can now use the agent with:`);
      console.log(`    - Workflow: dispatcher.execute("${agentName}", context)`);
      console.log(`    - Direct: from agents.${agentName} import ${className}Agent`);
      return true;
    }
    return false;
  }

  async generateAgent(config: InterviewState, outputDir: string, autoRegister: boolean = false): Promise<void> {
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

    // Handle auto-registration
    if (autoRegister) {
      await this.registerAgent(config.name, className);
      console.log("\nNext steps:");
      console.log("  1. Review the generated files");
      console.log("  2. Test the agent with: python -m " + config.name);
    } else {
      console.log("\nNext steps:");
      console.log("  1. Review the generated files");
      console.log("  2. Copy to src/agents/ in your pnd-agents installation");
      console.log("  3. Register the agent in workflows/agent_dispatcher.py");
      console.log("  4. Test the agent with: python -m " + config.name);
    }
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
        // Check if auto-registration is available
        let autoRegister = false;
        let outputDir: string;

        if (this.canAutoRegister()) {
          this.printSection("9. Auto-Registration");
          console.log("\nAuto-registration is available!");
          console.log("This will:");
          console.log("  - Generate the agent directly to src/agents/");
          console.log("  - Update src/agents/__init__.py with the import");
          console.log("  - Add a handler to workflows/agent_dispatcher.py");
          
          autoRegister = await this.confirmYesNo(
            "\nAuto-register the agent in pnd-agents?",
            true
          );

          if (autoRegister) {
            outputDir = SRC_AGENTS_DIR;
          } else {
            outputDir = await this.question(
              "Output directory (default: ./generated-agents): "
            );
            if (!outputDir) {
              outputDir = path.join(__dirname, "..", "..", "generated-agents");
            }
          }
        } else {
          outputDir = await this.question(
            "Output directory (default: ./generated-agents): "
          );
          if (!outputDir) {
            outputDir = path.join(__dirname, "..", "..", "generated-agents");
          }
        }

        await this.generateAgent(config, outputDir, autoRegister);
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
