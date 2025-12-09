#!/usr/bin/env python3
"""
Allow running pnd-agents as a module: python -m pnd_agents

This provides a fallback when the 'pnd-agents' CLI script is not on PATH.
"""

from pnd_agents.cli import main

if __name__ == "__main__":
    main()
