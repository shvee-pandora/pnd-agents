"""
PM Agent Pack

A collection of AI agents designed for Product Managers to use via Claude Desktop.
These agents help with common PM tasks like PRD breakdown, executive summaries,
and roadmap reviews.

Agents included:
- PRDToJiraAgent: Convert PRDs into Jira epics, stories, and acceptance criteria
- ExecSummaryAgent: Transform sprint data into executive-friendly updates
- RoadmapReviewAgent: Critique roadmaps and OKRs with risk assessment

Usage:
    from agents.pm_agent_pack import (
        PRDToJiraAgent,
        ExecSummaryAgent,
        RoadmapReviewAgent,
    )
    
    # Get an agent instance
    prd_agent = PRDToJiraAgent()
    
    # Get the system prompt for Claude Desktop
    system_prompt = prd_agent.get_system_prompt()
    
    # Get example input/output
    example_input = prd_agent.get_example_input()
    example_output = prd_agent.get_example_output()
"""

from .prd_to_jira_agent import (
    PRDToJiraAgent,
    PRDToJiraAgentConfig,
    get_agent as get_prd_to_jira_agent,
    get_agent_config as get_prd_to_jira_config,
)

from .exec_summary_agent import (
    ExecSummaryAgent,
    ExecSummaryAgentConfig,
    get_agent as get_exec_summary_agent,
    get_agent_config as get_exec_summary_config,
)

from .roadmap_review_agent import (
    RoadmapReviewAgent,
    RoadmapReviewAgentConfig,
    get_agent as get_roadmap_review_agent,
    get_agent_config as get_roadmap_review_config,
)

__all__ = [
    # PRD to Jira Agent
    "PRDToJiraAgent",
    "PRDToJiraAgentConfig",
    "get_prd_to_jira_agent",
    "get_prd_to_jira_config",
    # Executive Summary Agent
    "ExecSummaryAgent",
    "ExecSummaryAgentConfig",
    "get_exec_summary_agent",
    "get_exec_summary_config",
    # Roadmap Review Agent
    "RoadmapReviewAgent",
    "RoadmapReviewAgentConfig",
    "get_roadmap_review_agent",
    "get_roadmap_review_config",
]

# Package metadata
PM_AGENT_PACK_VERSION = "1.0.0"
PM_AGENT_PACK_CATEGORY = "Product Management"
PM_AGENT_PACK_DESCRIPTION = (
    "A collection of AI agents for Product Managers, designed for use with "
    "Claude Desktop. Includes PRD breakdown, executive summaries, and roadmap review."
)


def get_all_agents():
    """Return instances of all PM agents."""
    return {
        "prd_to_jira": PRDToJiraAgent(),
        "exec_summary": ExecSummaryAgent(),
        "roadmap_review": RoadmapReviewAgent(),
    }


def get_all_agent_metadata():
    """Return metadata for all PM agents (for marketplace registration)."""
    agents = get_all_agents()
    return {
        name: agent.get_agent_metadata()
        for name, agent in agents.items()
    }
