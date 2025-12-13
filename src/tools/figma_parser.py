"""
Figma Parser Tool

Provides Figma design parsing capabilities for agents including
extracting component names, colors, spacing, and typography from
Figma file metadata or JSON exports.
"""

import json
import re
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ComponentType(Enum):
    """Types of Figma components."""
    FRAME = "FRAME"
    COMPONENT = "COMPONENT"
    COMPONENT_SET = "COMPONENT_SET"
    INSTANCE = "INSTANCE"
    TEXT = "TEXT"
    RECTANGLE = "RECTANGLE"
    ELLIPSE = "ELLIPSE"
    VECTOR = "VECTOR"
    GROUP = "GROUP"


@dataclass
class Color:
    """Represents a color value."""
    r: float
    g: float
    b: float
    a: float = 1.0
    
    def to_hex(self) -> str:
        """Convert to hex color string."""
        r = int(self.r * 255)
        g = int(self.g * 255)
        b = int(self.b * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def to_rgba(self) -> str:
        """Convert to rgba color string."""
        r = int(self.r * 255)
        g = int(self.g * 255)
        b = int(self.b * 255)
        return f"rgba({r}, {g}, {b}, {self.a})"
    
    def to_css_var(self, name: str) -> str:
        """Generate CSS variable declaration."""
        return f"--color-{name}: {self.to_hex()};"


@dataclass
class Typography:
    """Represents typography settings."""
    font_family: str
    font_size: float
    font_weight: int
    line_height: Optional[float] = None
    letter_spacing: Optional[float] = None
    text_transform: Optional[str] = None
    
    def to_css(self) -> Dict[str, str]:
        """Convert to CSS properties."""
        css = {
            'font-family': f"'{self.font_family}', sans-serif",
            'font-size': f"{self.font_size}px",
            'font-weight': str(self.font_weight),
        }
        if self.line_height:
            css['line-height'] = str(self.line_height)
        if self.letter_spacing:
            css['letter-spacing'] = f"{self.letter_spacing}px"
        if self.text_transform:
            css['text-transform'] = self.text_transform
        return css


@dataclass
class Spacing:
    """Represents spacing values."""
    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0
    
    def to_css_padding(self) -> str:
        """Convert to CSS padding."""
        return f"{self.top}px {self.right}px {self.bottom}px {self.left}px"
    
    def to_css_margin(self) -> str:
        """Convert to CSS margin."""
        return f"{self.top}px {self.right}px {self.bottom}px {self.left}px"


@dataclass
class FigmaComponent:
    """Represents a parsed Figma component."""
    id: str
    name: str
    type: ComponentType
    width: float
    height: float
    x: float = 0
    y: float = 0
    fills: List[Color] = field(default_factory=list)
    strokes: List[Color] = field(default_factory=list)
    stroke_weight: float = 0
    corner_radius: float = 0
    padding: Optional[Spacing] = None
    typography: Optional[Typography] = None
    children: List['FigmaComponent'] = field(default_factory=list)
    variants: Dict[str, str] = field(default_factory=dict)
    
    def to_react_name(self) -> str:
        """Convert Figma name to React component name."""
        # Remove special characters and convert to PascalCase
        name = re.sub(r'[^a-zA-Z0-9\s]', '', self.name)
        words = name.split()
        return ''.join(word.capitalize() for word in words)
    
    def to_css_class(self) -> str:
        """Convert Figma name to CSS class name."""
        # Convert to kebab-case
        name = re.sub(r'[^a-zA-Z0-9\s]', '', self.name)
        return '-'.join(name.lower().split())


@dataclass
class DesignTokens:
    """Collection of design tokens extracted from Figma."""
    colors: Dict[str, Color] = field(default_factory=dict)
    typography: Dict[str, Typography] = field(default_factory=dict)
    spacing: Dict[str, float] = field(default_factory=dict)
    border_radius: Dict[str, float] = field(default_factory=dict)
    shadows: Dict[str, str] = field(default_factory=dict)
    
    def to_css_variables(self) -> str:
        """Generate CSS custom properties."""
        lines = [":root {"]
        
        # Colors
        for name, color in self.colors.items():
            lines.append(f"  --color-{name}: {color.to_hex()};")
        
        # Spacing
        for name, value in self.spacing.items():
            lines.append(f"  --spacing-{name}: {value}px;")
        
        # Border radius
        for name, value in self.border_radius.items():
            lines.append(f"  --radius-{name}: {value}px;")
        
        lines.append("}")
        return "\n".join(lines)
    
    def to_tailwind_config(self) -> Dict[str, Any]:
        """Generate Tailwind CSS config extension."""
        return {
            "theme": {
                "extend": {
                    "colors": {
                        name: color.to_hex()
                        for name, color in self.colors.items()
                    },
                    "spacing": {
                        name: f"{value}px"
                        for name, value in self.spacing.items()
                    },
                    "borderRadius": {
                        name: f"{value}px"
                        for name, value in self.border_radius.items()
                    },
                }
            }
        }


class FigmaParser:
    """
    Figma design parser for extracting component information.
    
    Parses Figma JSON exports or API responses to extract
    component structure, colors, typography, and spacing.
    """
    
    def __init__(self):
        """Initialize the Figma parser."""
        self.components: List[FigmaComponent] = []
        self.tokens = DesignTokens()
    
    def parse_file(self, file_path: str) -> List[FigmaComponent]:
        """
        Parse a Figma JSON export file.
        
        Args:
            file_path: Path to the JSON file.
            
        Returns:
            List of parsed FigmaComponent objects.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self.parse_data(data)
    
    def parse_data(self, data: Dict[str, Any]) -> List[FigmaComponent]:
        """
        Parse Figma JSON data.
        
        Args:
            data: Figma JSON data (from file or API).
            
        Returns:
            List of parsed FigmaComponent objects.
        """
        self.components = []
        
        # Handle different Figma data structures
        if 'document' in data:
            # Full file export
            self._parse_node(data['document'])
        elif 'nodes' in data:
            # API response with specific nodes
            for node_id, node_data in data['nodes'].items():
                if 'document' in node_data:
                    self._parse_node(node_data['document'])
        elif 'children' in data:
            # Direct node data
            self._parse_node(data)
        
        return self.components
    
    def _parse_node(self, node: Dict[str, Any]) -> Optional[FigmaComponent]:
        """
        Parse a single Figma node.
        
        Args:
            node: Node data dictionary.
            
        Returns:
            Parsed FigmaComponent or None.
        """
        node_type = node.get('type', '')
        
        # Skip non-component nodes
        if node_type not in [t.value for t in ComponentType]:
            # Still process children
            for child in node.get('children', []):
                self._parse_node(child)
            return None
        
        # Extract basic properties
        component = FigmaComponent(
            id=node.get('id', ''),
            name=node.get('name', ''),
            type=ComponentType(node_type),
            width=node.get('absoluteBoundingBox', {}).get('width', 0),
            height=node.get('absoluteBoundingBox', {}).get('height', 0),
            x=node.get('absoluteBoundingBox', {}).get('x', 0),
            y=node.get('absoluteBoundingBox', {}).get('y', 0),
        )
        
        # Extract fills (colors)
        for fill in node.get('fills', []):
            if fill.get('type') == 'SOLID' and fill.get('visible', True):
                color_data = fill.get('color', {})
                component.fills.append(Color(
                    r=color_data.get('r', 0),
                    g=color_data.get('g', 0),
                    b=color_data.get('b', 0),
                    a=fill.get('opacity', 1)
                ))
        
        # Extract strokes
        for stroke in node.get('strokes', []):
            if stroke.get('type') == 'SOLID' and stroke.get('visible', True):
                color_data = stroke.get('color', {})
                component.strokes.append(Color(
                    r=color_data.get('r', 0),
                    g=color_data.get('g', 0),
                    b=color_data.get('b', 0),
                    a=stroke.get('opacity', 1)
                ))
        
        component.stroke_weight = node.get('strokeWeight', 0)
        component.corner_radius = node.get('cornerRadius', 0)
        
        # Extract padding
        if 'paddingTop' in node or 'paddingRight' in node:
            component.padding = Spacing(
                top=node.get('paddingTop', 0),
                right=node.get('paddingRight', 0),
                bottom=node.get('paddingBottom', 0),
                left=node.get('paddingLeft', 0)
            )
        
        # Extract typography for text nodes
        if node_type == 'TEXT':
            style = node.get('style', {})
            component.typography = Typography(
                font_family=style.get('fontFamily', 'Inter'),
                font_size=style.get('fontSize', 16),
                font_weight=style.get('fontWeight', 400),
                line_height=style.get('lineHeightPx'),
                letter_spacing=style.get('letterSpacing'),
            )
        
        # Extract variants for component sets
        if node_type == 'COMPONENT_SET':
            for prop in node.get('componentPropertyDefinitions', {}).values():
                if prop.get('type') == 'VARIANT':
                    component.variants[prop.get('name', '')] = prop.get('defaultValue', '')
        
        # Parse children
        for child in node.get('children', []):
            child_component = self._parse_node(child)
            if child_component:
                component.children.append(child_component)
        
        # Add to components list if it's a component or component set
        if node_type in ['COMPONENT', 'COMPONENT_SET']:
            self.components.append(component)
        
        return component
    
    def extract_colors(self) -> Dict[str, Color]:
        """
        Extract all unique colors from parsed components.
        
        Returns:
            Dictionary of color name to Color object.
        """
        colors = {}
        color_count = {}
        
        def extract_from_component(comp: FigmaComponent):
            for fill in comp.fills:
                hex_color = fill.to_hex()
                if hex_color not in color_count:
                    color_count[hex_color] = 0
                color_count[hex_color] += 1
                
                # Generate name based on component
                name = f"{comp.to_css_class()}-fill"
                colors[name] = fill
            
            for child in comp.children:
                extract_from_component(child)
        
        for component in self.components:
            extract_from_component(component)
        
        self.tokens.colors = colors
        return colors
    
    def extract_typography(self) -> Dict[str, Typography]:
        """
        Extract all typography styles from parsed components.
        
        Returns:
            Dictionary of style name to Typography object.
        """
        typography = {}
        
        def extract_from_component(comp: FigmaComponent):
            if comp.typography:
                name = comp.to_css_class()
                typography[name] = comp.typography
            
            for child in comp.children:
                extract_from_component(child)
        
        for component in self.components:
            extract_from_component(component)
        
        self.tokens.typography = typography
        return typography
    
    def extract_spacing(self) -> Dict[str, float]:
        """
        Extract common spacing values from parsed components.
        
        Returns:
            Dictionary of spacing name to value.
        """
        spacing_values = set()
        
        def extract_from_component(comp: FigmaComponent):
            if comp.padding:
                spacing_values.add(comp.padding.top)
                spacing_values.add(comp.padding.right)
                spacing_values.add(comp.padding.bottom)
                spacing_values.add(comp.padding.left)
            
            for child in comp.children:
                extract_from_component(child)
        
        for component in self.components:
            extract_from_component(component)
        
        # Create named spacing scale
        sorted_values = sorted(spacing_values)
        spacing = {}
        for i, value in enumerate(sorted_values):
            if value > 0:
                spacing[str(i + 1)] = value
        
        self.tokens.spacing = spacing
        return spacing
    
    def generate_component_code(
        self,
        component: FigmaComponent,
        framework: str = 'react'
    ) -> str:
        """
        Generate component code from Figma component.
        
        Args:
            component: FigmaComponent to generate code for.
            framework: Target framework ('react', 'vue', etc.).
            
        Returns:
            Generated component code as string.
        """
        if framework == 'react':
            return self._generate_react_component(component)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _generate_react_component(self, component: FigmaComponent) -> str:
        """Generate React component code."""
        name = component.to_react_name()
        css_class = component.to_css_class()
        
        # Build styles
        styles = []
        if component.fills:
            styles.append(f"backgroundColor: '{component.fills[0].to_hex()}'")
        if component.corner_radius:
            styles.append(f"borderRadius: {component.corner_radius}")
        if component.padding:
            styles.append(f"padding: '{component.padding.to_css_padding()}'")
        
        style_str = ', '.join(styles)
        
        # Generate component
        code = f'''import React from 'react';
import {{ cn }} from '@/utils/cn';

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export const {name}: React.FC<{name}Props> = ({{
  className,
  children,
}}) => {{
  return (
    <div
      className={{cn('{css_class}', className)}}
      style={{{{ {style_str} }}}}
      data-testid="{css_class}"
    >
      {{children}}
    </div>
  );
}};

{name}.displayName = '{name}';
'''
        return code
    
    def get_design_tokens(self) -> DesignTokens:
        """
        Extract all design tokens from parsed components.
        
        Returns:
            DesignTokens object with all extracted values.
        """
        self.extract_colors()
        self.extract_typography()
        self.extract_spacing()
        return self.tokens


# Convenience functions
def parse_figma_file(file_path: str) -> List[FigmaComponent]:
    """Quick parse Figma file."""
    return FigmaParser().parse_file(file_path)


def extract_design_tokens(file_path: str) -> DesignTokens:
    """Quick extract design tokens from Figma file."""
    parser = FigmaParser()
    parser.parse_file(file_path)
    return parser.get_design_tokens()
