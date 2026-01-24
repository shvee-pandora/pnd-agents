"""
Amplience Placement Agent Package

A Human-in-the-Loop AI Agent that assists engineers and content editors in placing
existing Amplience modules into the correct page sections based on Figma designs.

This agent:
1. Analyzes Figma page structure
2. Maps Figma components to existing Amplience content types
3. Recommends section/slot placement
4. Produces a reviewable plan
5. Executes CMS updates ONLY after explicit human approval

CRITICAL CONSTRAINTS:
- NO autonomous publishing
- NO visual/design decisions
- NO content creation from scratch
- Draft/suggestion mode only
- Human approval required before write operations
"""

from .agent import (
    AmplicencePlacementAgent,
    ApprovalStatus,
    ConfidenceLevel,
    OperationMode,
    FigmaSection,
    FigmaPageBlueprint,
    AmplienceContentType,
    AmplienceModelCatalog,
    PlacementMapping,
    PlacementPlan,
    DraftExecutionResult,
    AmplicencePlacementResult,
    run,
    generate_placement_plan,
    execute_approved_plan,
)

__all__ = [
    "AmplicencePlacementAgent",
    "ApprovalStatus",
    "ConfidenceLevel",
    "OperationMode",
    "FigmaSection",
    "FigmaPageBlueprint",
    "AmplienceContentType",
    "AmplienceModelCatalog",
    "PlacementMapping",
    "PlacementPlan",
    "DraftExecutionResult",
    "AmplicencePlacementResult",
    "run",
    "generate_placement_plan",
    "execute_approved_plan",
]
