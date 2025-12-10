#!/usr/bin/env python3
"""
Analytics Report Generator

Generates analytics reports in various formats:
- JSON summary report
- Markdown report for Confluence upload
- JIRA dashboard data source (API-ready)

Usage:
    python generate_report.py --format json --days 14 --output report.json
    python generate_report.py --format markdown --days 14 --output report.md
    python generate_report.py --format all --days 14 --output-dir ./reports
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analytics_agent import AnalyticsAgent


def generate_json_report(agent: AnalyticsAgent, days: int) -> dict:
    """Generate JSON summary report."""
    return agent.generate_json_report(days=days)


def generate_markdown_report(agent: AnalyticsAgent, days: int) -> str:
    """Generate markdown report for Confluence upload."""
    return agent.generate_markdown_report(days=days)


def generate_jira_dashboard_data(agent: AnalyticsAgent, days: int) -> dict:
    """
    Generate JIRA dashboard data source.
    
    Returns data formatted for JIRA dashboard gadgets.
    """
    sprint_report = agent.generate_sprint_report()
    
    # Format for JIRA dashboard
    dashboard_data = {
        "gadgetType": "ai-productivity-tracker",
        "version": "1.0.0",
        "generatedAt": datetime.utcnow().isoformat(),
        "period": {
            "startDate": sprint_report.start_date,
            "endDate": sprint_report.end_date,
            "days": days,
        },
        "summary": {
            "totalAiTasks": sprint_report.total_ai_tasks,
            "averageEffectivenessScore": round(sprint_report.average_effectiveness_score, 1),
            "timeSavedHours": round(sprint_report.time_saved_hours, 1),
            "tasksRequiringReview": sprint_report.tasks_requiring_review,
        },
        "agentDistribution": [
            {"agent": agent, "count": count}
            for agent, count in sprint_report.agent_distribution.items()
        ],
        "trendData": sprint_report.trend_data,
        "charts": {
            "pieChart": {
                "title": "Tasks by Agent",
                "data": [
                    {"label": agent, "value": count}
                    for agent, count in sprint_report.agent_distribution.items()
                ],
            },
            "lineChart": {
                "title": "Daily Task Completion",
                "xAxis": "Date",
                "yAxis": "Tasks",
                "data": [
                    {"x": d["date"], "y": d["completedTasks"]}
                    for d in sprint_report.trend_data
                ],
            },
            "barChart": {
                "title": "Effectiveness Score Trend",
                "xAxis": "Date",
                "yAxis": "Score (%)",
                "data": [
                    {"x": d["date"], "y": round(d["averageEffectiveness"], 1)}
                    for d in sprint_report.trend_data
                ],
            },
        },
    }
    
    return dashboard_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate analytics reports for PG AI Squad"
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "jira", "all"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=14,
        help="Number of days to include in report (default: 14)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (for single format)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./reports",
        help="Output directory (for 'all' format)"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        help="Analytics log directory (default: logs/agent-analytics)"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = AnalyticsAgent(log_dir=args.log_dir)
    
    # Generate reports
    if args.format == "all":
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # JSON report
        json_report = generate_json_report(agent, args.days)
        json_path = output_dir / f"report_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(json_report, f, indent=2)
        print(f"JSON report saved to: {json_path}")
        
        # Markdown report
        md_report = generate_markdown_report(agent, args.days)
        md_path = output_dir / f"report_{timestamp}.md"
        with open(md_path, "w") as f:
            f.write(md_report)
        print(f"Markdown report saved to: {md_path}")
        
        # JIRA dashboard data
        jira_data = generate_jira_dashboard_data(agent, args.days)
        jira_path = output_dir / f"jira_dashboard_{timestamp}.json"
        with open(jira_path, "w") as f:
            json.dump(jira_data, f, indent=2)
        print(f"JIRA dashboard data saved to: {jira_path}")
        
    else:
        if args.format == "json":
            report = generate_json_report(agent, args.days)
            output = json.dumps(report, indent=2)
        elif args.format == "markdown":
            output = generate_markdown_report(agent, args.days)
        elif args.format == "jira":
            report = generate_jira_dashboard_data(agent, args.days)
            output = json.dumps(report, indent=2)
        
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Report saved to: {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    main()
