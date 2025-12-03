"""
Amplience API Tool

Provides Amplience CMS integration capabilities for agents including
content fetching, filtering, hierarchy navigation, and image URL building.
"""

import json
import hashlib
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from urllib.parse import urlencode, quote
import os


@dataclass
class ContentMeta:
    """Metadata for Amplience content."""
    schema: str
    name: str
    delivery_id: str
    delivery_key: Optional[str] = None
    hierarchy: Optional[Dict[str, Any]] = None


@dataclass
class ContentItem:
    """Represents an Amplience content item."""
    meta: ContentMeta
    data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'ContentItem':
        """Create ContentItem from API response."""
        meta_data = response.get('_meta', {})
        meta = ContentMeta(
            schema=meta_data.get('schema', ''),
            name=meta_data.get('name', ''),
            delivery_id=meta_data.get('deliveryId', ''),
            delivery_key=meta_data.get('deliveryKey'),
            hierarchy=meta_data.get('hierarchy'),
        )
        
        # Remove _meta from data
        data = {k: v for k, v in response.items() if k != '_meta'}
        
        return cls(meta=meta, data=data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            '_meta': {
                'schema': self.meta.schema,
                'name': self.meta.name,
                'deliveryId': self.meta.delivery_id,
                'deliveryKey': self.meta.delivery_key,
                'hierarchy': self.meta.hierarchy,
            },
            **self.data
        }


@dataclass
class FilterCriteria:
    """Filter criteria for content queries."""
    path: str
    value: Union[str, int, bool, List[str]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format."""
        return {
            'path': self.path,
            'value': self.value
        }


@dataclass
class AmplienceConfig:
    """Configuration for Amplience API."""
    hub_name: str
    base_url: str = "https://cdn.content.amplience.net"
    locale: str = "en"
    depth: str = "all"
    format: str = "inlined"
    cache_ttl: int = 300000  # 5 minutes in ms
    
    @classmethod
    def from_env(cls) -> 'AmplienceConfig':
        """Create config from environment variables."""
        return cls(
            hub_name=os.environ.get('AMPLIENCE_HUB_NAME', 'pandoragroup'),
            base_url=os.environ.get('AMPLIENCE_BASE_URL', 'https://cdn.content.amplience.net'),
            locale=os.environ.get('AMPLIENCE_LOCALE', 'en'),
            cache_ttl=int(os.environ.get('AMPLIENCE_CACHE_TTL', '300000')),
        )


class AmplienceAPI:
    """
    Amplience CMS API client for agents.
    
    Provides methods for fetching content, filtering, navigating
    hierarchies, and building image URLs.
    """
    
    # Pandora schema base URL
    SCHEMA_BASE = "https://schema-pandora.net"
    
    # Common schemas
    SCHEMAS = {
        'PAGE_HIERARCHY': f"{SCHEMA_BASE}/page-hierarchy",
        'PAGE_JSON': f"{SCHEMA_BASE}/page",
        'HERO_BANNER': f"{SCHEMA_BASE}/hero-banner",
        'GALLERY': f"{SCHEMA_BASE}/gallery",
        'CONTACTS': f"{SCHEMA_BASE}/contacts",
    }
    
    def __init__(self, config: Optional[AmplienceConfig] = None):
        """
        Initialize the Amplience API client.
        
        Args:
            config: Optional configuration. Uses env vars if not provided.
        """
        self.config = config or AmplienceConfig.from_env()
        self._cache: Dict[str, Any] = {}
    
    def _get_base_url(self, vse: Optional[str] = None) -> str:
        """Get the base URL, optionally with VSE for preview."""
        if vse:
            return f"https://{vse}"
        return f"{self.config.base_url}/content/id"
    
    def _get_default_params(self) -> Dict[str, str]:
        """Get default query parameters."""
        return {
            'depth': self.config.depth,
            'format': self.config.format,
            'locale': self.config.locale,
        }
    
    def _generate_cache_key(self, *args) -> str:
        """Generate a cache key from arguments."""
        key_str = json.dumps(args, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def fetch_by_id(
        self,
        content_id: str,
        vse: Optional[str] = None
    ) -> Optional[ContentItem]:
        """
        Fetch content by delivery ID.
        
        Args:
            content_id: The content delivery ID.
            vse: Optional VSE domain for preview.
            
        Returns:
            ContentItem or None if not found.
        """
        # Check cache
        cache_key = self._generate_cache_key('id', content_id, vse)
        if cache_key in self._cache and not vse:
            return self._cache[cache_key]
        
        # Build URL
        base_url = self._get_base_url(vse)
        params = self._get_default_params()
        url = f"{base_url}/{content_id}?{urlencode(params)}"
        
        # In a real implementation, this would make an HTTP request
        # For now, return a mock structure showing the expected format
        response = self._mock_fetch(url)
        
        if response:
            item = ContentItem.from_response(response)
            if not vse:
                self._cache[cache_key] = item
            return item
        
        return None
    
    def fetch_by_key(
        self,
        delivery_key: str,
        vse: Optional[str] = None
    ) -> Optional[ContentItem]:
        """
        Fetch content by delivery key.
        
        Args:
            delivery_key: The content delivery key.
            vse: Optional VSE domain for preview.
            
        Returns:
            ContentItem or None if not found.
        """
        # Check cache
        cache_key = self._generate_cache_key('key', delivery_key, vse)
        if cache_key in self._cache and not vse:
            return self._cache[cache_key]
        
        # Build URL
        base_url = f"{self.config.base_url}/content/key/{delivery_key}"
        if vse:
            base_url = f"https://{vse}/content/key/{delivery_key}"
        
        params = self._get_default_params()
        url = f"{base_url}?{urlencode(params)}"
        
        response = self._mock_fetch(url)
        
        if response:
            item = ContentItem.from_response(response)
            if not vse:
                self._cache[cache_key] = item
            return item
        
        return None
    
    def fetch_by_filter(
        self,
        filters: List[FilterCriteria],
        schema: Optional[str] = None,
        vse: Optional[str] = None
    ) -> List[ContentItem]:
        """
        Fetch content by filter criteria.
        
        Args:
            filters: List of filter criteria.
            schema: Optional schema to filter by.
            vse: Optional VSE domain for preview.
            
        Returns:
            List of matching ContentItems.
        """
        # Build filter request
        filter_request = {
            'filterBy': [f.to_dict() for f in filters]
        }
        
        if schema:
            filter_request['filterBy'].append({
                'path': '/_meta/schema',
                'value': schema
            })
        
        # Check cache
        cache_key = self._generate_cache_key('filter', filter_request, vse)
        if cache_key in self._cache and not vse:
            return self._cache[cache_key]
        
        # Build URL
        base_url = f"{self.config.base_url}/content/filter"
        if vse:
            base_url = f"https://{vse}/content/filter"
        
        # In real implementation, this would POST to the filter endpoint
        response = self._mock_filter_fetch(filter_request)
        
        items = []
        for resp in response.get('responses', []):
            if 'content' in resp:
                items.append(ContentItem.from_response(resp['content']))
        
        if not vse:
            self._cache[cache_key] = items
        
        return items
    
    def get_hierarchy_ancestors(
        self,
        content_id: str,
        vse: Optional[str] = None
    ) -> List[ContentItem]:
        """
        Get all ancestors of a content item in the hierarchy.
        
        Args:
            content_id: The content delivery ID.
            vse: Optional VSE domain for preview.
            
        Returns:
            List of ancestor ContentItems from deepest to root.
        """
        ancestors = []
        current_id = content_id
        
        while current_id:
            item = self.fetch_by_id(current_id, vse)
            if not item:
                break
            
            ancestors.append(item)
            
            # Get parent ID from hierarchy
            hierarchy = item.meta.hierarchy
            if hierarchy and hierarchy.get('parentId'):
                current_id = hierarchy['parentId']
            else:
                break
        
        return ancestors
    
    def get_breadcrumb_path(
        self,
        content_id: str,
        vse: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get breadcrumb path for a content item.
        
        Args:
            content_id: The content delivery ID.
            vse: Optional VSE domain for preview.
            
        Returns:
            List of breadcrumb items with title and url.
        """
        ancestors = self.get_hierarchy_ancestors(content_id, vse)
        
        breadcrumbs = []
        for item in reversed(ancestors):
            # Get title from various sources
            title = (
                item.data.get('metaSEO', {}).get('title') or
                item.data.get('title') or
                item.meta.name or
                item.meta.delivery_key or
                ''
            )
            
            # Get URL from seoUrl or delivery key
            url = item.data.get('seoUrl') or f"/{item.meta.delivery_key}"
            
            breadcrumbs.append({
                'title': title,
                'url': url
            })
        
        return breadcrumbs
    
    @staticmethod
    def build_image_url(
        image: Dict[str, Any],
        width: Optional[int] = None,
        height: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        quality: int = 80,
        format: str = 'auto'
    ) -> str:
        """
        Build an Amplience Dynamic Media image URL.
        
        Args:
            image: Image object with id, name, endpoint, defaultHost.
            width: Optional width in pixels.
            height: Optional height in pixels.
            aspect_ratio: Optional aspect ratio (e.g., "16:9").
            quality: Image quality (1-100).
            format: Image format (auto, webp, jpg, png).
            
        Returns:
            Complete image URL with transformations.
        """
        endpoint = image.get('endpoint', 'pandoragroup')
        name = image.get('name', '')
        default_host = image.get('defaultHost', 'cdn.media.amplience.net')
        
        # Build base URL
        base_url = f"https://{default_host}/i/{endpoint}/{name}"
        
        # Build query parameters
        params = []
        
        if width:
            params.append(f"w={width}")
        
        if height:
            params.append(f"h={height}")
        
        if aspect_ratio:
            params.append("sm=aspect")
            params.append(f"aspect={aspect_ratio}")
        
        params.append(f"fmt={format}")
        params.append(f"qlt={quality}")
        
        # Add existing query if present
        existing_query = image.get('query', '')
        if existing_query:
            params.append(existing_query)
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        
        return base_url
    
    def clear_cache(self):
        """Clear the content cache."""
        self._cache.clear()
    
    def _mock_fetch(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Mock fetch for demonstration.
        In real implementation, this would make HTTP requests.
        """
        # Return mock data structure
        return {
            '_meta': {
                'schema': self.SCHEMAS['PAGE_HIERARCHY'],
                'name': 'Mock Content',
                'deliveryId': 'mock-id-123',
                'deliveryKey': 'mock-content',
                'hierarchy': {
                    'parentId': None,
                    'root': True
                }
            },
            'title': 'Mock Title',
            'description': 'Mock description'
        }
    
    def _mock_filter_fetch(self, filter_request: Dict) -> Dict[str, Any]:
        """
        Mock filter fetch for demonstration.
        In real implementation, this would POST to filter endpoint.
        """
        return {
            'responses': [
                {
                    'content': {
                        '_meta': {
                            'schema': self.SCHEMAS['PAGE_HIERARCHY'],
                            'name': 'Filtered Content',
                            'deliveryId': 'filtered-id-123',
                            'deliveryKey': 'filtered-content',
                        },
                        'title': 'Filtered Title'
                    }
                }
            ]
        }


# Schema helpers
def get_schema_url(schema_name: str) -> str:
    """Get full schema URL from name."""
    return f"{AmplienceAPI.SCHEMA_BASE}/{schema_name}"


def build_image_url(
    image: Dict[str, Any],
    width: Optional[int] = None,
    aspect_ratio: Optional[str] = None
) -> str:
    """Quick image URL builder."""
    return AmplienceAPI.build_image_url(
        image,
        width=width,
        aspect_ratio=aspect_ratio
    )


# Content type helpers
def create_content_type_schema(
    name: str,
    title: str,
    description: str,
    properties: Dict[str, Any],
    required: List[str] = None
) -> Dict[str, Any]:
    """
    Create a content type JSON schema.
    
    Args:
        name: Schema name (will be used in URL).
        title: Human-readable title.
        description: Schema description.
        properties: Property definitions.
        required: List of required property names.
        
    Returns:
        JSON Schema dictionary.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"{AmplienceAPI.SCHEMA_BASE}/{name}",
        "title": title,
        "description": description,
        "type": "object",
        "allOf": [
            {"$ref": f"{AmplienceAPI.SCHEMA_BASE}/global-partials#/definitions/base"}
        ],
        "properties": properties,
        "required": required or [],
        "propertyOrder": list(properties.keys())
    }
