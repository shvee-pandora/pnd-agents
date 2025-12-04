"""
Figma Reader Agent

An agent that reads Figma designs via the Figma API and extracts
component metadata, design tokens, and generates React component
specifications for the Frontend Engineer Agent.
"""

import os
import re
import json
import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class FigmaNodeType(Enum):
    """Types of Figma nodes."""
    DOCUMENT = "DOCUMENT"
    CANVAS = "CANVAS"
    FRAME = "FRAME"
    GROUP = "GROUP"
    COMPONENT = "COMPONENT"
    COMPONENT_SET = "COMPONENT_SET"
    INSTANCE = "INSTANCE"
    TEXT = "TEXT"
    RECTANGLE = "RECTANGLE"
    ELLIPSE = "ELLIPSE"
    VECTOR = "VECTOR"
    LINE = "LINE"
    BOOLEAN_OPERATION = "BOOLEAN_OPERATION"


@dataclass
class FigmaColor:
    """Represents a Figma color."""
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
        """Convert to rgba string."""
        r = int(self.r * 255)
        g = int(self.g * 255)
        b = int(self.b * 255)
        return f"rgba({r}, {g}, {b}, {self.a:.2f})"


@dataclass
class TextStyle:
    """Represents a text style from Figma."""
    name: str
    font_family: str
    font_size: float
    font_weight: int
    line_height: Optional[float] = None
    letter_spacing: Optional[float] = None
    text_transform: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "fontFamily": self.font_family,
            "fontSize": self.font_size,
            "fontWeight": self.font_weight,
            "lineHeight": self.line_height,
            "letterSpacing": self.letter_spacing,
            "textTransform": self.text_transform,
        }


@dataclass
class ColorStyle:
    """Represents a color style from Figma."""
    name: str
    color: FigmaColor
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hex": self.color.to_hex(),
            "rgba": self.color.to_rgba(),
        }


@dataclass
class LayoutConstraints:
    """Represents layout constraints from Figma."""
    horizontal: str = "LEFT"
    vertical: str = "TOP"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "horizontal": self.horizontal,
            "vertical": self.vertical,
        }


@dataclass
class AutoLayout:
    """Represents auto-layout settings from Figma."""
    mode: str  # HORIZONTAL, VERTICAL, NONE
    padding_top: float = 0
    padding_right: float = 0
    padding_bottom: float = 0
    padding_left: float = 0
    item_spacing: float = 0
    counter_axis_sizing: str = "AUTO"  # AUTO, FIXED
    primary_axis_sizing: str = "AUTO"  # AUTO, FIXED
    primary_axis_align: str = "MIN"  # MIN, CENTER, MAX, SPACE_BETWEEN
    counter_axis_align: str = "MIN"  # MIN, CENTER, MAX
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "padding": {
                "top": self.padding_top,
                "right": self.padding_right,
                "bottom": self.padding_bottom,
                "left": self.padding_left,
            },
            "itemSpacing": self.item_spacing,
            "counterAxisSizing": self.counter_axis_sizing,
            "primaryAxisSizing": self.primary_axis_sizing,
            "primaryAxisAlign": self.primary_axis_align,
            "counterAxisAlign": self.counter_axis_align,
        }
    
    def to_css_suggestion(self) -> str:
        """Generate CSS suggestion based on auto-layout."""
        if self.mode == "NONE":
            return "position: relative;"
        
        css = ["display: flex;"]
        css.append(f"flex-direction: {'row' if self.mode == 'HORIZONTAL' else 'column'};")
        css.append(f"gap: {self.item_spacing}px;")
        css.append(f"padding: {self.padding_top}px {self.padding_right}px {self.padding_bottom}px {self.padding_left}px;")
        
        # Alignment
        align_map = {"MIN": "flex-start", "CENTER": "center", "MAX": "flex-end", "SPACE_BETWEEN": "space-between"}
        css.append(f"justify-content: {align_map.get(self.primary_axis_align, 'flex-start')};")
        css.append(f"align-items: {align_map.get(self.counter_axis_align, 'flex-start')};")
        
        return " ".join(css)


@dataclass
class ComponentVariant:
    """Represents a component variant."""
    name: str
    properties: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "properties": self.properties,
        }


@dataclass
class Asset:
    """Represents an asset to be exported."""
    node_id: str
    name: str
    format: str  # SVG, PNG, JPG, PDF
    scale: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodeId": self.node_id,
            "name": self.name,
            "format": self.format,
            "scale": self.scale,
        }


@dataclass
class ComponentMetadata:
    """Metadata extracted from a Figma component."""
    component_name: str
    figma_id: str
    figma_name: str
    description: str = ""
    props: Dict[str, str] = field(default_factory=dict)
    design_tokens: Dict[str, Any] = field(default_factory=dict)
    assets: List[Asset] = field(default_factory=list)
    variants: List[ComponentVariant] = field(default_factory=list)
    auto_layout: Optional[AutoLayout] = None
    constraints: Optional[LayoutConstraints] = None
    width: float = 0
    height: float = 0
    notes: str = ""
    children: List['ComponentMetadata'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary matching the expected output format."""
        result = {
            "componentName": self.component_name,
            "figmaId": self.figma_id,
            "figmaName": self.figma_name,
            "description": self.description,
            "props": self.props,
            "designTokens": self.design_tokens,
            "assets": [a.to_dict() for a in self.assets],
            "variants": [v.to_dict() for v in self.variants],
            "dimensions": {
                "width": self.width,
                "height": self.height,
            },
            "notes": self.notes,
        }
        
        if self.auto_layout:
            result["autoLayout"] = self.auto_layout.to_dict()
            result["notes"] += f" CSS suggestion: {self.auto_layout.to_css_suggestion()}"
        
        if self.constraints:
            result["constraints"] = self.constraints.to_dict()
        
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        
        return result


class FigmaReaderAgent:
    """
    Agent for reading Figma designs and extracting component metadata.
    
    This agent connects to the Figma API to fetch design data and
    normalizes it into a format that the Frontend Engineer Agent
    can consume to generate React components.
    """
    
    FIGMA_API_BASE = "https://api.figma.com/v1"
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the Figma Reader Agent.
        
        Args:
            access_token: Figma API access token. If not provided,
                         reads from FIGMA_ACCESS_TOKEN environment variable.
        """
        self.access_token = access_token or os.environ.get("FIGMA_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError(
                "Figma access token is required. "
                "Set FIGMA_ACCESS_TOKEN environment variable or pass access_token parameter."
            )
        
        self.client = httpx.Client(
            headers={
                "X-Figma-Token": self.access_token,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        
        # Cache for styles
        self._color_styles: Dict[str, ColorStyle] = {}
        self._text_styles: Dict[str, TextStyle] = {}
    
    def _parse_figma_url(self, url: str) -> tuple[str, Optional[str]]:
        """
        Parse a Figma URL to extract file key and node ID.
        
        Args:
            url: Figma file URL or node URL.
            
        Returns:
            Tuple of (file_key, node_id or None).
        """
        # Match patterns like:
        # https://www.figma.com/file/ABC123/FileName
        # https://www.figma.com/design/ABC123/FileName?node-id=123-456
        # https://www.figma.com/file/ABC123/FileName?node-id=123%3A456
        
        file_pattern = r"figma\.com/(?:file|design)/([a-zA-Z0-9]+)"
        node_pattern = r"node-id=([0-9]+[-:][0-9]+|[0-9]+%3A[0-9]+)"
        
        file_match = re.search(file_pattern, url)
        if not file_match:
            raise ValueError(f"Invalid Figma URL: {url}")
        
        file_key = file_match.group(1)
        
        node_match = re.search(node_pattern, url)
        node_id = None
        if node_match:
            # Normalize node ID format: convert dashes and URL-encoded colons to colons
            node_id = node_match.group(1).replace("%3A", ":").replace("-", ":")
        
        return file_key, node_id
    
    def _fetch_file(self, file_key: str) -> Dict[str, Any]:
        """Fetch a Figma file."""
        response = self.client.get(f"{self.FIGMA_API_BASE}/files/{file_key}")
        response.raise_for_status()
        return response.json()
    
    def _fetch_file_nodes(self, file_key: str, node_ids: List[str]) -> Dict[str, Any]:
        """Fetch specific nodes from a Figma file."""
        ids_param = ",".join(node_ids)
        response = self.client.get(
            f"{self.FIGMA_API_BASE}/files/{file_key}/nodes",
            params={"ids": ids_param}
        )
        response.raise_for_status()
        return response.json()
    
    def _fetch_file_styles(self, file_key: str) -> Dict[str, Any]:
        """Fetch styles from a Figma file."""
        response = self.client.get(f"{self.FIGMA_API_BASE}/files/{file_key}/styles")
        response.raise_for_status()
        return response.json()
    
    def _fetch_image_urls(
        self,
        file_key: str,
        node_ids: List[str],
        format: str = "svg",
        scale: float = 1.0
    ) -> Dict[str, str]:
        """Fetch image URLs for nodes."""
        ids_param = ",".join(node_ids)
        response = self.client.get(
            f"{self.FIGMA_API_BASE}/images/{file_key}",
            params={
                "ids": ids_param,
                "format": format,
                "scale": scale,
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("images", {})
    
    def _extract_color(self, color_data: Dict[str, float]) -> FigmaColor:
        """Extract color from Figma color data."""
        return FigmaColor(
            r=color_data.get("r", 0),
            g=color_data.get("g", 0),
            b=color_data.get("b", 0),
            a=color_data.get("a", 1),
        )
    
    def _extract_auto_layout(self, node: Dict[str, Any]) -> Optional[AutoLayout]:
        """Extract auto-layout settings from a node."""
        layout_mode = node.get("layoutMode")
        if not layout_mode or layout_mode == "NONE":
            return None
        
        return AutoLayout(
            mode=layout_mode,
            padding_top=node.get("paddingTop", 0),
            padding_right=node.get("paddingRight", 0),
            padding_bottom=node.get("paddingBottom", 0),
            padding_left=node.get("paddingLeft", 0),
            item_spacing=node.get("itemSpacing", 0),
            counter_axis_sizing=node.get("counterAxisSizingMode", "AUTO"),
            primary_axis_sizing=node.get("primaryAxisSizingMode", "AUTO"),
            primary_axis_align=node.get("primaryAxisAlignItems", "MIN"),
            counter_axis_align=node.get("counterAxisAlignItems", "MIN"),
        )
    
    def _extract_constraints(self, node: Dict[str, Any]) -> Optional[LayoutConstraints]:
        """Extract layout constraints from a node."""
        constraints = node.get("constraints")
        if not constraints:
            return None
        
        return LayoutConstraints(
            horizontal=constraints.get("horizontal", "LEFT"),
            vertical=constraints.get("vertical", "TOP"),
        )
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert a name to PascalCase for React component naming."""
        # Remove special characters and split
        clean = re.sub(r"[^a-zA-Z0-9\s_-]", "", name)
        words = re.split(r"[\s_-]+", clean)
        return "".join(word.capitalize() for word in words if word)
    
    def _infer_props_from_node(self, node: Dict[str, Any]) -> Dict[str, str]:
        """Infer React props from a Figma node."""
        props = {}
        node_type = node.get("type")
        
        # Check for text content
        if node_type == "TEXT":
            characters = node.get("characters", "")
            # Infer prop name from layer name or content
            prop_name = self._to_camel_case(node.get("name", "text"))
            props[prop_name] = "string"
        
        # Check for images
        fills = node.get("fills", [])
        for fill in fills:
            if fill.get("type") == "IMAGE":
                props["image"] = "asset"
                break
        
        # Check for component properties
        component_props = node.get("componentProperties", {})
        for prop_name, prop_data in component_props.items():
            prop_type = prop_data.get("type", "TEXT")
            if prop_type == "TEXT":
                props[self._to_camel_case(prop_name)] = "string"
            elif prop_type == "BOOLEAN":
                props[self._to_camel_case(prop_name)] = "boolean"
            elif prop_type == "INSTANCE_SWAP":
                props[self._to_camel_case(prop_name)] = "ReactNode"
            elif prop_type == "VARIANT":
                props[self._to_camel_case(prop_name)] = "string"
        
        return props
    
    def _to_camel_case(self, name: str) -> str:
        """Convert a name to camelCase."""
        pascal = self._to_pascal_case(name)
        if pascal:
            return pascal[0].lower() + pascal[1:]
        return name
    
    def _extract_design_tokens(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract design tokens from a node."""
        tokens = {
            "colors": {},
            "spacing": [],
            "textStyles": {},
            "borderRadius": {},
        }
        
        # Extract colors from fills
        fills = node.get("fills", [])
        for i, fill in enumerate(fills):
            if fill.get("type") == "SOLID" and fill.get("visible", True):
                color = self._extract_color(fill.get("color", {}))
                tokens["colors"][f"fill{i}"] = color.to_hex()
        
        # Extract colors from strokes
        strokes = node.get("strokes", [])
        for i, stroke in enumerate(strokes):
            if stroke.get("type") == "SOLID" and stroke.get("visible", True):
                color = self._extract_color(stroke.get("color", {}))
                tokens["colors"][f"stroke{i}"] = color.to_hex()
        
        # Extract spacing from padding
        padding_values = set()
        for key in ["paddingTop", "paddingRight", "paddingBottom", "paddingLeft"]:
            if key in node:
                padding_values.add(node[key])
        
        item_spacing = node.get("itemSpacing")
        if item_spacing:
            padding_values.add(item_spacing)
        
        tokens["spacing"] = sorted(list(padding_values))
        
        # Extract text styles
        if node.get("type") == "TEXT":
            style = node.get("style", {})
            tokens["textStyles"]["default"] = {
                "fontFamily": style.get("fontFamily", "Inter"),
                "fontSize": style.get("fontSize", 16),
                "fontWeight": style.get("fontWeight", 400),
                "lineHeight": style.get("lineHeightPx"),
                "letterSpacing": style.get("letterSpacing"),
            }
        
        # Extract border radius
        corner_radius = node.get("cornerRadius")
        if corner_radius:
            tokens["borderRadius"]["default"] = corner_radius
        
        # Check for individual corner radii
        for corner in ["topLeftRadius", "topRightRadius", "bottomLeftRadius", "bottomRightRadius"]:
            if corner in node:
                tokens["borderRadius"][corner] = node[corner]
        
        return tokens
    
    def _extract_variants(self, node: Dict[str, Any]) -> List[ComponentVariant]:
        """Extract variants from a component set."""
        variants = []
        
        if node.get("type") != "COMPONENT_SET":
            return variants
        
        # Get variant properties from component property definitions
        prop_defs = node.get("componentPropertyDefinitions", {})
        variant_props = {}
        
        for prop_name, prop_def in prop_defs.items():
            if prop_def.get("type") == "VARIANT":
                variant_props[prop_name] = prop_def.get("variantOptions", [])
        
        # Extract variants from children
        for child in node.get("children", []):
            if child.get("type") == "COMPONENT":
                variant_name = child.get("name", "")
                # Parse variant properties from name (e.g., "Size=Large, State=Hover")
                props = {}
                for part in variant_name.split(","):
                    if "=" in part:
                        key, value = part.strip().split("=", 1)
                        props[key.strip()] = value.strip()
                
                variants.append(ComponentVariant(
                    name=variant_name,
                    properties=props,
                ))
        
        return variants
    
    def _identify_assets(self, node: Dict[str, Any]) -> List[Asset]:
        """Identify assets that need to be exported."""
        assets = []
        node_id = node.get("id", "")
        node_name = node.get("name", "")
        node_type = node.get("type", "")
        
        # Check for vector/icon nodes
        if node_type in ["VECTOR", "BOOLEAN_OPERATION", "LINE"]:
            assets.append(Asset(
                node_id=node_id,
                name=self._to_camel_case(node_name),
                format="SVG",
            ))
        
        # Check for image fills
        fills = node.get("fills", [])
        for fill in fills:
            if fill.get("type") == "IMAGE":
                assets.append(Asset(
                    node_id=node_id,
                    name=self._to_camel_case(node_name),
                    format="PNG",
                    scale=2.0,  # Export at 2x for retina
                ))
                break
        
        # Check export settings
        export_settings = node.get("exportSettings", [])
        for setting in export_settings:
            assets.append(Asset(
                node_id=node_id,
                name=self._to_camel_case(node_name),
                format=setting.get("format", "PNG"),
                scale=setting.get("constraint", {}).get("value", 1.0),
            ))
        
        return assets
    
    def _parse_node(
        self,
        node: Dict[str, Any],
        depth: int = 0,
        max_depth: int = 10
    ) -> Optional[ComponentMetadata]:
        """
        Parse a Figma node into ComponentMetadata.
        
        Args:
            node: The Figma node data.
            depth: Current recursion depth.
            max_depth: Maximum recursion depth.
            
        Returns:
            ComponentMetadata or None if node should be skipped.
        """
        if depth > max_depth:
            return None
        
        node_type = node.get("type", "")
        node_name = node.get("name", "")
        
        # Only process component-like nodes at top level
        if depth == 0 and node_type not in ["COMPONENT", "COMPONENT_SET", "FRAME"]:
            return None
        
        # Extract bounding box
        bbox = node.get("absoluteBoundingBox", {})
        
        # Build component metadata
        metadata = ComponentMetadata(
            component_name=self._to_pascal_case(node_name),
            figma_id=node.get("id", ""),
            figma_name=node_name,
            description=node.get("description", ""),
            width=bbox.get("width", 0),
            height=bbox.get("height", 0),
        )
        
        # Extract props
        metadata.props = self._infer_props_from_node(node)
        
        # Extract design tokens
        metadata.design_tokens = self._extract_design_tokens(node)
        
        # Extract auto-layout
        metadata.auto_layout = self._extract_auto_layout(node)
        
        # Extract constraints
        metadata.constraints = self._extract_constraints(node)
        
        # Extract variants (for component sets)
        metadata.variants = self._extract_variants(node)
        
        # Identify assets
        metadata.assets = self._identify_assets(node)
        
        # Generate notes
        notes = []
        if metadata.auto_layout:
            if metadata.auto_layout.mode == "HORIZONTAL":
                notes.append("Auto layout -> Use Flex row.")
            elif metadata.auto_layout.mode == "VERTICAL":
                notes.append("Auto layout -> Use Flex column.")
            
            if metadata.auto_layout.item_spacing:
                notes.append(f"{metadata.auto_layout.item_spacing}px gap.")
            
            padding = metadata.auto_layout
            if any([padding.padding_top, padding.padding_right, padding.padding_bottom, padding.padding_left]):
                notes.append(f"Padding: {padding.padding_top}px {padding.padding_right}px {padding.padding_bottom}px {padding.padding_left}px.")
        
        if metadata.variants:
            variant_props = set()
            for v in metadata.variants:
                variant_props.update(v.properties.keys())
            if variant_props:
                notes.append(f"Variants: {', '.join(variant_props)}.")
        
        metadata.notes = " ".join(notes)
        
        # Parse children (for frames and component sets)
        children = node.get("children", [])
        for child in children:
            child_type = child.get("type", "")
            # Only include significant children
            if child_type in ["COMPONENT", "FRAME", "GROUP", "TEXT", "INSTANCE"]:
                child_metadata = self._parse_node(child, depth + 1, max_depth)
                if child_metadata:
                    metadata.children.append(child_metadata)
                    # Merge child props into parent
                    for prop_name, prop_type in child_metadata.props.items():
                        if prop_name not in metadata.props:
                            metadata.props[prop_name] = prop_type
                    # Merge child assets
                    metadata.assets.extend(child_metadata.assets)
        
        return metadata
    
    def read_figma_url(self, url: str) -> Dict[str, Any]:
        """
        Read a Figma design from a URL.
        
        Args:
            url: Figma file URL or node URL.
            
        Returns:
            Component metadata dictionary.
        """
        file_key, node_id = self._parse_figma_url(url)
        
        if node_id:
            return self.read_node(file_key, node_id)
        else:
            return self.read_file(file_key)
    
    def read_file(self, file_key: str) -> Dict[str, Any]:
        """
        Read all components from a Figma file.
        
        Args:
            file_key: The Figma file key.
            
        Returns:
            Dictionary with file info and components.
        """
        file_data = self._fetch_file(file_key)
        
        result = {
            "fileName": file_data.get("name", ""),
            "lastModified": file_data.get("lastModified", ""),
            "version": file_data.get("version", ""),
            "components": [],
        }
        
        # Find all components in the document
        document = file_data.get("document", {})
        self._find_components(document, result["components"])
        
        return result
    
    def _find_components(self, node: Dict[str, Any], components: List[Dict[str, Any]]):
        """Recursively find components in a node tree."""
        node_type = node.get("type", "")
        
        if node_type in ["COMPONENT", "COMPONENT_SET"]:
            metadata = self._parse_node(node)
            if metadata:
                components.append(metadata.to_dict())
        
        # Recurse into children
        for child in node.get("children", []):
            self._find_components(child, components)
    
    def read_node(self, file_key: str, node_id: str) -> Dict[str, Any]:
        """
        Read a specific node from a Figma file.
        
        Args:
            file_key: The Figma file key.
            node_id: The node ID to read.
            
        Returns:
            Component metadata dictionary or list of components for CANVAS/DOCUMENT nodes.
        """
        nodes_data = self._fetch_file_nodes(file_key, [node_id])
        
        nodes = nodes_data.get("nodes", {})
        if node_id not in nodes:
            raise ValueError(f"Node {node_id} not found in file {file_key}")
        
        node_data = nodes[node_id]
        document = node_data.get("document", {})
        node_type = document.get("type", "")
        
        # Handle CANVAS (page) and DOCUMENT nodes by extracting their children
        if node_type in ["CANVAS", "DOCUMENT"]:
            components = []
            self._find_components(document, components)
            
            # If no components found, try to parse frames as components
            if not components:
                for child in document.get("children", []):
                    child_type = child.get("type", "")
                    if child_type in ["FRAME", "COMPONENT", "COMPONENT_SET", "INSTANCE"]:
                        metadata = self._parse_node(child)
                        if metadata:
                            components.append(metadata.to_dict())
            
            return {
                "nodeName": document.get("name", ""),
                "nodeId": node_id,
                "nodeType": node_type,
                "components": components,
            }
        
        # For other node types, parse directly
        metadata = self._parse_node(document)
        if not metadata:
            raise ValueError(f"Could not parse node {node_id}")
        
        return metadata.to_dict()
    
    def get_component_for_frontend_agent(
        self,
        url_or_file_key: str,
        node_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get component metadata formatted for the Frontend Engineer Agent.
        
        This is the main entry point for the figma-read command.
        
        Args:
            url_or_file_key: Figma URL or file key.
            node_id: Optional node ID (if not in URL).
            
        Returns:
            Component metadata in the format expected by Frontend Engineer Agent.
        """
        # Check if it's a URL
        if url_or_file_key.startswith("http"):
            return self.read_figma_url(url_or_file_key)
        
        # It's a file key
        if node_id:
            return self.read_node(url_or_file_key, node_id)
        else:
            return self.read_file(url_or_file_key)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience function for quick usage
def read_figma(url_or_file_key: str, node_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick function to read Figma design.
    
    Args:
        url_or_file_key: Figma URL or file key.
        node_id: Optional node ID.
        
    Returns:
        Component metadata dictionary.
    """
    with FigmaReaderAgent() as agent:
        return agent.get_component_for_frontend_agent(url_or_file_key, node_id)
