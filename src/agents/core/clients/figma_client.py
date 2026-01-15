"""
Figma Client

Shared client for interacting with Figma REST APIs.
Used by figma_reader_agent and other design-integrated agents.

Usage:
    from src.agents.core.clients.figma_client import FigmaClient
    
    client = FigmaClient(token="your_token")
    file_data = client.get_file("file_key")
    components = client.get_components("file_key")
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pnd_agents.core.clients.figma")


@dataclass
class FigmaColor:
    """A color from Figma."""
    r: float
    g: float
    b: float
    a: float = 1.0
    
    def to_hex(self) -> str:
        """Convert to hex color string."""
        return f"#{int(self.r * 255):02x}{int(self.g * 255):02x}{int(self.b * 255):02x}"
    
    def to_rgba(self) -> str:
        """Convert to rgba() CSS string."""
        return f"rgba({int(self.r * 255)}, {int(self.g * 255)}, {int(self.b * 255)}, {self.a})"


@dataclass
class FigmaComponent:
    """A component from Figma."""
    id: str
    name: str
    description: str = ""
    component_set_id: Optional[str] = None
    containing_frame: Optional[str] = None


@dataclass
class FigmaStyle:
    """A style from Figma (color, text, effect, grid)."""
    key: str
    name: str
    style_type: str  # FILL, TEXT, EFFECT, GRID
    description: str = ""


class FigmaClient:
    """
    Client for Figma REST API.
    
    Provides methods for fetching files, components, and styles.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Figma client.
        
        Args:
            token: Figma access token (defaults to FIGMA_ACCESS_TOKEN env var)
        """
        self.token = token or os.environ.get("FIGMA_ACCESS_TOKEN", "")
        self.base_url = "https://api.figma.com/v1"
    
    def get_file(self, file_key: str) -> Dict[str, Any]:
        """
        Get a Figma file.
        
        Args:
            file_key: Figma file key (from URL)
            
        Returns:
            Dictionary with file data.
        """
        raise NotImplementedError("FigmaClient.get_file() not yet implemented")
    
    def get_components(self, file_key: str) -> List[FigmaComponent]:
        """
        Get components from a Figma file.
        
        Args:
            file_key: Figma file key
            
        Returns:
            List of FigmaComponent objects.
        """
        raise NotImplementedError("FigmaClient.get_components() not yet implemented")
    
    def get_styles(self, file_key: str) -> List[FigmaStyle]:
        """
        Get styles from a Figma file.
        
        Args:
            file_key: Figma file key
            
        Returns:
            List of FigmaStyle objects.
        """
        raise NotImplementedError("FigmaClient.get_styles() not yet implemented")
    
    def get_images(
        self,
        file_key: str,
        node_ids: List[str],
        format: str = "png",
        scale: float = 1.0
    ) -> Dict[str, str]:
        """
        Get rendered images for nodes.
        
        Args:
            file_key: Figma file key
            node_ids: List of node IDs to render
            format: Image format (png, jpg, svg, pdf)
            scale: Scale factor
            
        Returns:
            Dictionary mapping node IDs to image URLs.
        """
        raise NotImplementedError("FigmaClient.get_images() not yet implemented")
    
    def parse_figma_url(self, url: str) -> Dict[str, str]:
        """
        Parse a Figma URL to extract file key and node ID.
        
        Args:
            url: Figma URL
            
        Returns:
            Dictionary with file_key and optional node_id.
        """
        raise NotImplementedError("FigmaClient.parse_figma_url() not yet implemented")


__all__ = ["FigmaClient", "FigmaComponent", "FigmaStyle", "FigmaColor"]
