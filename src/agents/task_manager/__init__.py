"""
Compatibility shim for agents.task_manager

This module re-exports TaskManagerAgent from agents.task_manager_agent
to maintain backward compatibility with older imports and configurations
that reference agents.task_manager instead of agents.task_manager_agent.
"""

from ..task_manager_agent import TaskManagerAgent

__all__ = ["TaskManagerAgent"]
