#!/usr/bin/env python3
"""
Basic Usage Example for Analytics Agent

This example demonstrates how to use the Analytics Agent to track
agent performance metrics and generate reports.
"""

import os
import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.analytics_agent import AnalyticsAgent, record_event


def example_track_task():
    """Example: Track a task from start to completion."""
    print("=" * 60)
    print("Example: Track a Task")
    print("=" * 60)
    
    # Initialize the analytics agent
    agent = AnalyticsAgent()
    
    # Track task start
    print("\n1. Starting task...")
    metrics = agent.on_task_started(
        agent_name="Frontend Engineer Agent",
        task_description="Create Header Component from Figma design",
        jira_task_id="EPA-123",
    )
    print(f"   Task started at: {metrics.start_time}")
    
    # Simulate some work
    print("\n2. Simulating work...")
    time.sleep(1)
    
    # Track task completion
    print("\n3. Completing task...")
    metrics = agent.on_task_completed(
        agent_name="Frontend Engineer Agent",
        jira_task_id="EPA-123",
        metrics={
            "duration": 208000,  # 3m 28s in milliseconds
            "iterations": 4,
            "errors": ["Minor styling issue (auto-fixed)"],
            "effectivenessScore": 92.0,
            "requiresHumanReview": False,
        },
    )
    
    print(f"   Task completed!")
    print(f"   Duration: {metrics.duration_ms}ms")
    print(f"   Effectiveness Score: {metrics.effectiveness_score}%")
    print(f"   Status: {metrics.status}")


def example_track_failure():
    """Example: Track a failed task."""
    print("\n" + "=" * 60)
    print("Example: Track a Failed Task")
    print("=" * 60)
    
    agent = AnalyticsAgent()
    
    # Track task start
    print("\n1. Starting task...")
    agent.on_task_started(
        agent_name="Unit Test Agent",
        task_description="Generate tests for complex component",
        jira_task_id="EPA-456",
    )
    
    # Track task failure
    print("\n2. Task failed...")
    metrics = agent.on_task_failed(
        agent_name="Unit Test Agent",
        jira_task_id="EPA-456",
        errors=[
            "Unable to parse component structure",
            "Missing type definitions",
            "Circular dependency detected",
        ],
    )
    
    print(f"   Task failed!")
    print(f"   Errors: {len(metrics.errors)}")
    print(f"   Requires Human Review: {metrics.requires_human_review}")


def example_using_convenience_function():
    """Example: Using the record_event convenience function."""
    print("\n" + "=" * 60)
    print("Example: Using record_event Convenience Function")
    print("=" * 60)
    
    # This is the recommended way for other agents to record events
    print("\n1. Recording task start...")
    record_event(
        event_type="start",
        agent_name="Code Review Agent",
        task_description="Review PR #42",
        jira_task_id="EPA-789",
    )
    print("   Event recorded!")
    
    print("\n2. Recording task completion...")
    record_event(
        event_type="complete",
        agent_name="Code Review Agent",
        jira_task_id="EPA-789",
        metrics={
            "duration": 45000,
            "iterations": 1,
            "effectivenessScore": 100.0,
        },
    )
    print("   Event recorded!")


def example_generate_report():
    """Example: Generate analytics reports."""
    print("\n" + "=" * 60)
    print("Example: Generate Reports")
    print("=" * 60)
    
    agent = AnalyticsAgent()
    
    # Generate JSON report
    print("\n1. Generating JSON report...")
    json_report = agent.generate_json_report(days=7)
    print(f"   Report type: {json_report.get('reportType')}")
    print(f"   Total tasks: {json_report.get('sprint', {}).get('totalAiTasks', 0)}")
    
    # Generate Markdown report
    print("\n2. Generating Markdown report...")
    md_report = agent.generate_markdown_report(days=7)
    print(f"   Report length: {len(md_report)} characters")
    print(f"   Preview: {md_report[:100]}...")


def example_list_analytics():
    """Example: List stored analytics data."""
    print("\n" + "=" * 60)
    print("Example: List Analytics Data")
    print("=" * 60)
    
    agent = AnalyticsAgent()
    
    # List all analytics
    print("\n1. Listing all analytics (last 7 days)...")
    analytics = agent.list_analytics(days=7)
    print(f"   Found {len(analytics)} tasks")
    
    # List by agent
    print("\n2. Listing analytics for specific agent...")
    agent_analytics = agent.list_analytics(
        days=7,
        agent_name="Frontend Engineer Agent",
    )
    print(f"   Found {len(agent_analytics)} tasks for Frontend Engineer Agent")
    
    # List by status
    print("\n3. Listing completed tasks...")
    completed = agent.list_analytics(
        days=7,
        status="completed",
    )
    print(f"   Found {len(completed)} completed tasks")


def example_agent_report():
    """Example: Generate agent-specific report."""
    print("\n" + "=" * 60)
    print("Example: Agent-Specific Report")
    print("=" * 60)
    
    agent = AnalyticsAgent()
    
    # Generate report for specific agent
    print("\n1. Generating report for Frontend Engineer Agent...")
    report = agent.generate_agent_report("Frontend Engineer Agent", days=7)
    
    print(f"   Agent: {report.agent_name}")
    print(f"   Total Tasks: {report.total_tasks}")
    print(f"   Completed: {report.completed_tasks}")
    print(f"   Failed: {report.failed_tasks}")
    print(f"   Avg Effectiveness: {report.average_effectiveness_score:.1f}%")


def main():
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# Analytics Agent - Usage Examples")
    print("#" * 60)
    
    example_track_task()
    example_track_failure()
    example_using_convenience_function()
    example_generate_report()
    example_list_analytics()
    example_agent_report()
    
    print("\n" + "#" * 60)
    print("# Examples Complete!")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    main()
