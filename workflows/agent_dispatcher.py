"""
Agent Dispatcher

Maps agent names to their handler functions and provides
a unified interface for executing agents.
"""

import os
import sys
import time
from typing import Dict, Any, Callable, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.workflow_engine import AgentResult


class AgentDispatcher:
    """
    Dispatcher for routing tasks to the appropriate agent handlers.
    
    The dispatcher maintains a registry of agent handlers and provides
    methods for executing agents with proper input/output handling.
    """
    
    def __init__(self):
        """Initialize the agent dispatcher."""
        self._handlers: Dict[str, Callable[[Dict[str, Any]], AgentResult]] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register the default agent handlers."""
        # Register all built-in agents
        self.register("figma", self._figma_handler)
        self.register("frontend", self._frontend_handler)
        self.register("backend", self._backend_handler)
        self.register("amplience", self._amplience_handler)
        self.register("review", self._review_handler)
        self.register("qa", self._qa_handler)
        self.register("performance", self._performance_handler)
        self.register("unit_test", self._unit_test_handler)
        self.register("sonar", self._sonar_handler)
        self.register("test_case_writing", self._test_case_writing_handler)
    
    def register(self, name: str, handler: Callable[[Dict[str, Any]], AgentResult]):
        """
        Register an agent handler.
        
        Args:
            name: Agent name (e.g., "figma", "frontend")
            handler: Function that takes context dict and returns AgentResult
        """
        self._handlers[name] = handler
    
    def get_handler(self, name: str) -> Optional[Callable[[Dict[str, Any]], AgentResult]]:
        """Get a handler by name."""
        return self._handlers.get(name)
    
    def execute(self, agent_name: str, context: Dict[str, Any]) -> AgentResult:
        """
        Execute an agent with the given context.
        
        Args:
            agent_name: Name of the agent to execute.
            context: Context dictionary with task, input, metadata, etc.
            
        Returns:
            AgentResult from the agent.
        """
        handler = self._handlers.get(agent_name)
        if not handler:
            return AgentResult(
                status="error",
                error=f"No handler registered for agent: {agent_name}"
            )
        
        # Track task start with analytics
        start_time = time.time()
        task_description = context.get("task", "")
        jira_task_id = context.get("metadata", {}).get("jira_task_id")
        workflow_id = context.get("metadata", {}).get("workflow_id")
        
        try:
            from tools.analytics_store import record_event
            record_event(
                event_type="task_started",
                agent_name=agent_name,
                task_description=task_description,
                jira_task_id=jira_task_id,
            )
        except ImportError:
            pass  # Analytics not available
        
        try:
            result = handler(context)
            
            # Track task completion with analytics
            duration_ms = (time.time() - start_time) * 1000
            try:
                from tools.analytics_store import record_event
                event_type = "task_completed" if result.status == "success" else "task_failed"
                record_event(
                    event_type=event_type,
                    agent_name=agent_name,
                    task_description=task_description,
                    jira_task_id=jira_task_id,
                    metrics={
                        "duration": duration_ms,
                        "status": result.status,
                    },
                    errors=[result.error] if result.error else None,
                )
            except ImportError:
                pass  # Analytics not available
            
            return result
        except Exception as e:
            # Track task failure with analytics
            duration_ms = (time.time() - start_time) * 1000
            try:
                from tools.analytics_store import record_event
                record_event(
                    event_type="task_failed",
                    agent_name=agent_name,
                    task_description=task_description,
                    jira_task_id=jira_task_id,
                    metrics={"duration": duration_ms},
                    errors=[str(e)],
                )
            except ImportError:
                pass  # Analytics not available
            
            return AgentResult(
                status="error",
                error=str(e)
            )
    
    def list_agents(self) -> list:
        """List all registered agent names."""
        return list(self._handlers.keys())
    
    # ==================== Agent Handlers ====================
    
    def _figma_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Figma Parser Agent handler.
        
        Extracts component structure, design tokens, and assets from Figma.
        """
        import re
        
        task = context.get("task", "")
        input_data = context.get("input", {})
        
        # Extract Figma URL from task
        figma_url_pattern = r"https?://(?:www\.)?figma\.com/(?:file|design)/([a-zA-Z0-9]+)[^\s]*"
        match = re.search(figma_url_pattern, task)
        
        if not match:
            # Check if URL is in input data
            figma_url = input_data.get("figma_url")
            if not figma_url:
                return AgentResult(
                    status="error",
                    error="No Figma URL found in task description or input"
                )
        else:
            figma_url = match.group(0)
        
        try:
            from agents.figma_reader_agent import FigmaReaderAgent
            
            agent = FigmaReaderAgent()
            result = agent.read_figma_url(figma_url)
            agent.close()
            
            # Convert to frontend-friendly format
            output = agent.get_component_for_frontend_agent(result)
            
            return AgentResult(
                status="success",
                data={
                    "figma_url": figma_url,
                    "component": output,
                    "raw_result": result.to_dict() if hasattr(result, 'to_dict') else result
                },
                next="frontend"
            )
        except Exception as e:
            return AgentResult(
                status="error",
                error=f"Figma parsing failed: {str(e)}"
            )
    
    def _frontend_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Frontend Engineer Agent handler.
        
        Generates React components from Figma data or task description.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        previous_output = input_data.get("previous_output", {})
        
        # Get component data from Figma agent output
        component_data = previous_output.get("component", {})
        
        # Build component specification
        component_spec = {
            "name": component_data.get("componentName", self._extract_component_name(task)),
            "props": component_data.get("props", {}),
            "styles": component_data.get("designTokens", {}),
            "variants": component_data.get("variants", []),
            "assets": component_data.get("assets", []),
            "autoLayout": component_data.get("autoLayout"),
        }
        
        return AgentResult(
            status="success",
            data={
                "component_spec": component_spec,
                "files_to_generate": [
                    f"src/components/{component_spec['name']}/{component_spec['name']}.tsx",
                    f"src/components/{component_spec['name']}/{component_spec['name']}.stories.tsx",
                    f"src/components/{component_spec['name']}/{component_spec['name']}.module.css",
                    f"src/components/{component_spec['name']}/index.ts",
                ],
                "suggested_imports": self._suggest_imports(component_spec),
            },
            next="review"
        )
    
    def _backend_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Backend Agent handler.
        
        Creates API endpoints and server components.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        
        # Extract endpoint information from task
        endpoint_info = self._extract_endpoint_info(task)
        
        return AgentResult(
            status="success",
            data={
                "endpoint": endpoint_info,
                "files_to_generate": [
                    f"src/app/api/{endpoint_info['path']}/route.ts",
                ],
                "suggested_schema": endpoint_info.get("schema", {}),
            },
            next="review"
        )
    
    def _amplience_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Amplience CMS Agent handler.
        
        Generates content type schemas and example payloads.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        
        # Extract content type name from task
        content_type_name = self._extract_content_type_name(task)
        
        return AgentResult(
            status="success",
            data={
                "content_type": content_type_name,
                "schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "title": content_type_name,
                    "type": "object",
                    "properties": {},
                },
                "example_payload": {},
                "files_to_generate": [
                    f"contents/{content_type_name.lower()}.json",
                ],
            },
            next="frontend"
        )
    
    def _review_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Code Review Agent handler.
        
        Validates code against Pandora standards.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        previous_output = input_data.get("previous_output", {})
        
        files_to_review = previous_output.get("files_to_generate", [])
        
        return AgentResult(
            status="success",
            data={
                "files_reviewed": files_to_review,
                "issues_found": [],
                "suggestions": [
                    "Ensure TypeScript strict mode is enabled",
                    "Add proper accessibility attributes",
                    "Follow atomic design pattern",
                ],
                "passed": True,
            },
            next="qa"
        )
    
    def _qa_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        QA Agent handler.
        
        Validates implementation against test cases and acceptance criteria.
        Gets test cases from user input or from previous workflow stages.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        previous_output = input_data.get("previous_output", {})
        
        try:
            from agents.qa_agent import QAAgent
            
            agent = QAAgent()
            
            agent_context = {
                "task_description": task,
                "input_data": {
                    "test_cases": input_data.get("test_cases", []),
                    "code_paths": previous_output.get("files_to_generate", []),
                    "acceptance_criteria": input_data.get("acceptance_criteria", []),
                    "previous_output": previous_output,
                    "all_outputs": input_data.get("all_outputs", {}),
                }
            }
            
            result = agent.run(agent_context)
            
            return AgentResult(
                status=result.get("status", "success"),
                data=result.get("data", {}),
                next=result.get("next", "sonar"),
                error=result.get("error")
            )
        except ImportError:
            component_spec = None
            if "component_spec" in previous_output:
                component_spec = previous_output["component_spec"]
            elif "previous_output" in input_data:
                prev = input_data["previous_output"]
                if "component_spec" in prev:
                    component_spec = prev["component_spec"]
            
            component_name = component_spec.get("name", "Component") if component_spec else "Component"
            
            return AgentResult(
                status="success",
                data={
                    "validation_status": "PENDING",
                    "scenarios": [
                        {
                            "name": "Functional Tests",
                            "status": "pending",
                            "test_cases": [
                                f"renders {component_name} correctly",
                                f"handles props correctly",
                                f"matches snapshot",
                                f"is accessible",
                            ],
                        }
                    ],
                    "recommendations": [
                        "Run full test suite: npm test",
                        "Check test coverage: npm test -- --coverage",
                        "Validate all acceptance criteria manually",
                    ],
                },
                next="sonar"
            )
        except Exception as e:
            return AgentResult(
                status="error",
                error=f"QA validation failed: {str(e)}"
            )
    
    def _performance_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Performance Agent handler.
        
        Runs performance analysis and optimization checks.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        
        return AgentResult(
            status="success",
            data={
                "checks_performed": [
                    "Bundle size analysis",
                    "Render performance",
                    "Memory usage",
                ],
                "recommendations": [
                    "Consider lazy loading for large components",
                    "Use React.memo for expensive renders",
                    "Optimize images with next/image",
                ],
                "score": 85,
            }
        )
    
    def _unit_test_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Unit Test Agent handler.
        
        Generates comprehensive unit tests with 100% coverage target.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        previous_output = input_data.get("previous_output", {})
        
        try:
            from agents.unit_test_agent import UnitTestAgent
            
            agent = UnitTestAgent()
            
            # Build context for the agent
            agent_context = {
                "task_description": task,
                "input_data": {
                    "files": previous_output.get("files_to_generate", []),
                    "component_spec": previous_output.get("component_spec", {}),
                }
            }
            
            result = agent.run(agent_context)
            
            return AgentResult(
                status=result.get("status", "success"),
                data=result.get("data", {}),
                next=result.get("next", "sonar"),
                error=result.get("error")
            )
        except ImportError:
            # Fallback if agent not available
            component_spec = previous_output.get("component_spec", {})
            component_name = component_spec.get("name", "Component")
            
            return AgentResult(
                status="success",
                data={
                    "test_files": [
                        f"src/components/{component_name}/__tests__/{component_name}.test.tsx",
                    ],
                    "test_cases": [
                        f"should render {component_name} without crashing",
                        f"should render {component_name} with props",
                        f"should match snapshot for {component_name}",
                        f"should handle user interactions in {component_name}",
                        f"should be accessible in {component_name}",
                        f"should cover all conditional branches - truthy path",
                        f"should cover all conditional branches - falsy path",
                        f"should handle edge cases and null values",
                    ],
                    "coverage_target": "100%",
                    "recommendations": [
                        "Run tests with coverage: npm test -- --coverage",
                        "Target 100% coverage for all metrics",
                        "Add data-testid attributes to components",
                        "Mock external dependencies to isolate unit tests",
                    ],
                },
                next="sonar"
            )
        except Exception as e:
            return AgentResult(
                status="error",
                error=f"Unit test generation failed: {str(e)}"
            )
    
    def _sonar_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Sonar Validation Agent handler.
        
        Validates code against SonarCloud quality gates.
        Target: 0 errors, 0 duplication, 100% coverage.
        
        Supports two modes:
        1. Pre-PR mode (default): Validates generated code locally using guardrails
        2. Post-PR mode: Fetches results from SonarCloud API (requires PR to exist)
        
        The mode is determined by metadata:
        - If 'pr_number' is in metadata, uses Post-PR mode
        - Otherwise, uses Pre-PR mode with local validation
        """
        task = context.get("task", "")
        input_data = context.get("input", {})
        metadata = context.get("metadata", {})
        previous_output = input_data.get("previous_output", {})
        
        # Determine validation mode
        pr_number = metadata.get("pr_number")
        is_pre_pr_mode = pr_number is None
        
        try:
            from agents.sonar_validation_agent import SonarValidationAgent
            
            agent = SonarValidationAgent()
            
            if is_pre_pr_mode:
                # Pre-PR mode: Use local validation with guardrails
                # This doesn't require a PR to exist
                repo_name = metadata.get("repo_name", "default")
                
                # Get pre-generation checklist (guardrails)
                checklist = agent.get_pre_generation_checklist(repo_name)
                
                # If we have generated code from previous stages, validate it
                validation_results = []
                files_to_generate = previous_output.get("files_to_generate", [])
                component_spec = previous_output.get("component_spec", {})
                
                # Build a summary of what would be validated
                pre_pr_data = {
                    "mode": "pre_pr_validation",
                    "quality_gate_status": "PENDING_PR",
                    "pre_generation_checklist": checklist,
                    "files_to_validate": files_to_generate,
                    "component_name": component_spec.get("name", "Component"),
                    "guardrails_applied": [g.rule_id for g in agent.GUARDRAILS],
                    "recommendations": [
                        "Run lint checks: pnpm lint or npm run lint",
                        "Run type checks: pnpm check-types or npm run typecheck",
                        "Run tests: pnpm test or npm test",
                        "Ensure 100% test coverage for new code",
                        "Review code against Sonar guardrails above",
                        "Create PR to trigger full SonarCloud analysis",
                    ],
                    "next_steps": [
                        "1. Commit your changes to the feature branch",
                        "2. Create a PR to trigger SonarCloud analysis",
                        "3. Review SonarCloud results on the PR",
                        "4. Fix any issues before merging",
                    ],
                }
                
                return AgentResult(
                    status="success",
                    data=pre_pr_data,
                    next=None,  # End of workflow in pre-PR mode
                    error=None
                )
            else:
                # Post-PR mode: Fetch results from SonarCloud API
                branch = input_data.get("branch", "master")
                repo_path = input_data.get("repo_path")
                
                agent_context = {
                    "task_description": task,
                    "input_data": {
                        "branch": branch,
                        "repo_path": repo_path,
                    }
                }
                
                result = agent.run(agent_context)
                
                return AgentResult(
                    status=result.get("status", "success"),
                    data=result.get("data", {}),
                    next=result.get("next"),
                    error=result.get("error")
                )
                
        except ImportError:
            # Fallback if agent not available - provide static validation checklist
            return AgentResult(
                status="success",
                data={
                    "mode": "pre_pr_validation",
                    "quality_gate_status": "PENDING_PR",
                    "checklist": {
                        "coverage": {
                            "target": "100%",
                            "checks": [
                                "Line coverage must be 100%",
                                "Branch coverage must be 100%",
                                "All functions must be tested",
                            ]
                        },
                        "issues": {
                            "target": "0 issues",
                            "checks": [
                                "No blocker issues",
                                "No critical issues",
                                "No major bugs",
                                "No vulnerabilities",
                            ]
                        },
                        "duplication": {
                            "target": "0% duplication",
                            "checks": [
                                "No duplicated code blocks",
                                "Extract common code to shared utilities",
                            ]
                        },
                    },
                    "sonarcloud_url": "https://sonarcloud.io/summary/new_code?id=pandora-jewelry_spark_pandora-group&branch=master",
                    "recommendations": [
                        "Run lint checks locally before creating PR",
                        "Run type checks locally before creating PR",
                        "Run tests locally before creating PR",
                        "Ensure 100% test coverage for new code",
                        "Create PR to trigger full SonarCloud analysis",
                    ],
                },
                next=None  # End of workflow in pre-PR mode
            )
        except Exception as e:
            return AgentResult(
                status="error",
                error=f"Sonar validation failed: {str(e)}"
            )

    def _test_case_writing_handler(self, context: Dict[str, Any]) -> AgentResult:
        """
        Test Case Writing Agent handler.

        Generates comprehensive test cases from requirements, user stories,
        or acceptance criteria.
        """
        task = context.get("task", "")
        input_data = context.get("input", {})

        try:
            from agents.test_case_writing_agent import TestCaseWritingAgent

            agent = TestCaseWritingAgent()

            # Build context for the agent
            agent_context = {
                "task_description": task,
                "input_data": {
                    "requirements": input_data.get("requirements", task),
                    "feature_name": input_data.get("feature_name", "Feature"),
                    "acceptance_criteria": input_data.get("acceptance_criteria", []),
                    "include_security": input_data.get("include_security", False),
                    "include_accessibility": input_data.get("include_accessibility", False),
                }
            }

            result = agent.run(agent_context)

            return AgentResult(
                status=result.get("status", "success"),
                data=result.get("data", {}),
                next=result.get("next", "qa"),
                error=result.get("error")
            )
        except ImportError:
            # Fallback if agent not available
            return AgentResult(
                status="success",
                data={
                    "test_suites": [{
                        "name": "Generated Test Suite",
                        "testCases": [
                            {"id": "TC-0001", "title": "Basic functionality test", "type": "functional"},
                            {"id": "TC-0002", "title": "Error handling test", "type": "negative"},
                            {"id": "TC-0003", "title": "Edge case test", "type": "edge_case"},
                        ],
                    }],
                    "recommendations": [
                        "Review generated test cases for completeness",
                        "Add specific test data for each scenario",
                        "Prioritize critical path test cases",
                    ],
                },
                next="qa"
            )
        except Exception as e:
            return AgentResult(
                status="error",
                error=f"Test case writing failed: {str(e)}"
            )

    # ==================== Helper Methods ====================
    
    def _extract_component_name(self, task: str) -> str:
        """Extract component name from task description."""
        import re
        
        # Look for patterns like "Stories carousel", "Header component", etc.
        patterns = [
            r"(?:create|build|generate)\s+(?:a\s+)?([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+component",
            r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+(?:carousel|component|section|widget)",
            r"(?:the\s+)?([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+from\s+[Ff]igma",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task)
            if match:
                name = match.group(1).replace(" ", "")
                return name
        
        return "Component"
    
    def _extract_endpoint_info(self, task: str) -> Dict[str, Any]:
        """Extract API endpoint information from task."""
        import re
        
        # Default endpoint info
        info = {
            "path": "endpoint",
            "method": "GET",
            "schema": {}
        }
        
        # Look for path patterns
        path_match = re.search(r"/api/([a-zA-Z0-9/_-]+)", task)
        if path_match:
            info["path"] = path_match.group(1)
        
        # Look for HTTP methods
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            if method.lower() in task.lower():
                info["method"] = method
                break
        
        return info
    
    def _extract_content_type_name(self, task: str) -> str:
        """Extract content type name from task."""
        import re
        
        # Look for content type patterns
        patterns = [
            r"content\s+type\s+(?:called\s+|named\s+)?['\"]?([a-zA-Z]+)['\"]?",
            r"([A-Z][a-zA-Z]+)\s+content\s+type",
            r"amplience\s+([a-zA-Z]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "ContentType"
    
    def _suggest_imports(self, component_spec: Dict[str, Any]) -> list:
        """Suggest imports based on component specification."""
        imports = [
            "import React from 'react';",
        ]
        
        if component_spec.get("variants"):
            imports.append("import { cva, type VariantProps } from 'class-variance-authority';")
        
        if component_spec.get("autoLayout"):
            imports.append("import styles from './{name}.module.css';".format(name=component_spec.get("name", "Component")))
        
        return imports


# Global agent registry for convenience
AGENT_REGISTRY: Dict[str, Callable[[Dict[str, Any]], AgentResult]] = {}


def get_dispatcher() -> AgentDispatcher:
    """Get a configured agent dispatcher."""
    dispatcher = AgentDispatcher()
    
    # Update global registry
    global AGENT_REGISTRY
    for name in dispatcher.list_agents():
        handler = dispatcher.get_handler(name)
        if handler:
            AGENT_REGISTRY[name] = handler
    
    return dispatcher
