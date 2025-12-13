"""
Figma Reader Agent Package

Exports the FigmaReaderAgent class and helper functions.
"""

from .agent import (
    FigmaReaderAgent,
    FigmaNodeType,
    FigmaColor,
    TextStyle,
    ColorStyle,
    LayoutConstraints,
    AutoLayout,
    ComponentVariant,
    Asset,
    ComponentMetadata,
    read_figma,
    run,
)

__all__ = [
    "FigmaReaderAgent",
    "FigmaNodeType",
    "FigmaColor",
    "TextStyle",
    "ColorStyle",
    "LayoutConstraints",
    "AutoLayout",
    "ComponentVariant",
    "Asset",
    "ComponentMetadata",
    "read_figma",
    "run",
]
