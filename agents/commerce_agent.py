"""
Commerce Agent

An agent that fetches real products from Pandora e-commerce APIs,
understands shopping goals, filters products based on criteria,
and prepares cart-add metadata for the frontend.
"""

import os
import re
import json
import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class ProductCategory(Enum):
    """Common product categories."""
    BRACELETS = "bracelets"
    CHARMS = "charms"
    RINGS = "rings"
    NECKLACES = "necklaces"
    EARRINGS = "earrings"
    PENDANTS = "pendants"
    WATCHES = "watches"
    GIFT_SETS = "gift-sets"


class Material(Enum):
    """Common materials/colors."""
    SILVER = "silver"
    GOLD = "gold"
    ROSE_GOLD = "rose-gold"
    TWO_TONE = "two-tone"


@dataclass
class ProductResult:
    """Result of a product search and selection."""
    product_id: str
    name: str
    price: float
    currency: str
    image_url: Optional[str] = None
    category: Optional[str] = None
    material: Optional[str] = None
    description: Optional[str] = None
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "productId": self.product_id,
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "imageUrl": self.image_url,
            "category": self.category,
            "material": self.material,
            "description": self.description,
            "message": self.message
        }


@dataclass
class ShoppingGoal:
    """Parsed shopping goal from natural language."""
    query: str
    category: Optional[str] = None
    material: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    currency: str = "DKK"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CommerceAgent:
    """
    Agent for finding products and preparing cart-add operations.
    
    This agent connects to Pandora e-commerce APIs to fetch real products,
    understands natural language shopping goals, filters products based on
    criteria like price, material, and category, and prepares cart metadata.
    """
    
    # SFCC OCAPI base URL patterns
    OCAPI_BASE_PATTERNS = [
        "https://{instance}/s/{site_id}/dw/shop/v23_2",
        "https://{instance}/s/{site_id}/dw/shop/v20_4",
    ]
    
    # Default configuration
    DEFAULT_SITE_ID = "en-GB"
    DEFAULT_CURRENCY = "GBP"
    
    # Currency mappings
    CURRENCY_MAP = {
        "DKK": {"site_id": "da-DK", "locale": "da-DK"},
        "GBP": {"site_id": "en-GB", "locale": "en-GB"},
        "EUR": {"site_id": "de-DE", "locale": "de-DE"},
        "USD": {"site_id": "en-US", "locale": "en-US"},
    }
    
    def __init__(
        self,
        ocapi_instance: Optional[str] = None,
        client_id: Optional[str] = None,
        site_id: Optional[str] = None
    ):
        """
        Initialize the Commerce Agent.
        
        Args:
            ocapi_instance: SFCC OCAPI instance hostname
            client_id: OCAPI client ID for authentication
            site_id: Site ID for the storefront
        """
        self.ocapi_instance = ocapi_instance or os.environ.get(
            "SFCC_OCAPI_INSTANCE",
            "production-emea-pandora.demandware.net"
        )
        self.client_id = client_id or os.environ.get(
            "SFCC_CLIENT_ID",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # Default placeholder
        )
        self.site_id = site_id or os.environ.get(
            "SFCC_SITE_ID",
            self.DEFAULT_SITE_ID
        )
        
        self.client = httpx.Client(
            headers={
                "Content-Type": "application/json",
                "x-dw-client-id": self.client_id,
            },
            timeout=30.0,
        )
        
        self._auth_token: Optional[str] = None
    
    def _get_ocapi_base_url(self, api_version: str = "v23_2") -> str:
        """Get the OCAPI base URL."""
        return f"https://{self.ocapi_instance}/s/{self.site_id}/dw/shop/{api_version}"
    
    def _authenticate_guest(self) -> str:
        """
        Authenticate as a guest to get a bearer token.
        
        Returns:
            Bearer token for API requests.
        """
        if self._auth_token:
            return self._auth_token
        
        url = f"{self._get_ocapi_base_url()}/customers/auth"
        
        try:
            response = self.client.post(
                url,
                json={"type": "guest"}
            )
            response.raise_for_status()
            self._auth_token = response.headers.get("authorization", "")
            return self._auth_token
        except Exception as e:
            # If authentication fails, continue without token
            # Some endpoints work without authentication
            return ""
    
    def parse_shopping_goal(self, goal: str) -> ShoppingGoal:
        """
        Parse a natural language shopping goal into structured criteria.
        
        Args:
            goal: Natural language goal like "silver bracelet under 700 DKK"
            
        Returns:
            ShoppingGoal with parsed criteria.
        """
        goal_lower = goal.lower()
        
        # Extract currency and price
        currency = "DKK"  # Default
        max_price = None
        min_price = None
        
        # Currency patterns
        currency_patterns = [
            (r"(\d+(?:\.\d+)?)\s*(dkk|kr)", "DKK"),
            (r"(\d+(?:\.\d+)?)\s*(gbp|pounds?|£)", "GBP"),
            (r"(\d+(?:\.\d+)?)\s*(eur|euros?|€)", "EUR"),
            (r"(\d+(?:\.\d+)?)\s*(usd|dollars?|\$)", "USD"),
            (r"(£)(\d+(?:\.\d+)?)", "GBP"),
            (r"(\$)(\d+(?:\.\d+)?)", "USD"),
            (r"(€)(\d+(?:\.\d+)?)", "EUR"),
        ]
        
        for pattern, curr in currency_patterns:
            match = re.search(pattern, goal_lower)
            if match:
                currency = curr
                # Extract price value
                groups = match.groups()
                for g in groups:
                    try:
                        price_val = float(g)
                        if "under" in goal_lower or "below" in goal_lower or "less than" in goal_lower:
                            max_price = price_val
                        elif "over" in goal_lower or "above" in goal_lower or "more than" in goal_lower:
                            min_price = price_val
                        else:
                            max_price = price_val  # Default to max price
                        break
                    except ValueError:
                        continue
                break
        
        # Extract category
        category = None
        category_keywords = {
            "bracelet": "bracelets",
            "charm": "charms",
            "ring": "rings",
            "necklace": "necklaces",
            "earring": "earrings",
            "pendant": "pendants",
            "watch": "watches",
            "gift": "gift-sets",
            "set": "gift-sets",
        }
        
        for keyword, cat in category_keywords.items():
            if keyword in goal_lower:
                category = cat
                break
        
        # Extract material
        material = None
        material_keywords = {
            "silver": "silver",
            "gold": "gold",
            "rose gold": "rose-gold",
            "rose-gold": "rose-gold",
            "two-tone": "two-tone",
            "two tone": "two-tone",
        }
        
        for keyword, mat in material_keywords.items():
            if keyword in goal_lower:
                material = mat
                break
        
        # Build search query from goal
        # Remove price and currency info for cleaner search
        query = re.sub(r"under\s+\d+\s*\w*", "", goal_lower)
        query = re.sub(r"below\s+\d+\s*\w*", "", query)
        query = re.sub(r"less than\s+\d+\s*\w*", "", query)
        query = re.sub(r"over\s+\d+\s*\w*", "", query)
        query = re.sub(r"above\s+\d+\s*\w*", "", query)
        query = re.sub(r"\d+\s*(dkk|gbp|eur|usd|kr|pounds?|euros?|dollars?|£|€|\$)", "", query)
        query = query.strip()
        
        if not query:
            query = category or "jewelry"
        
        return ShoppingGoal(
            query=query,
            category=category,
            material=material,
            max_price=max_price,
            min_price=min_price,
            currency=currency
        )
    
    def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        count: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Search for products using SFCC OCAPI.
        
        Args:
            query: Search query string
            category: Optional category ID to filter
            max_price: Maximum price filter
            min_price: Minimum price filter
            count: Number of results to return
            
        Returns:
            List of product data dictionaries.
        """
        # Build search URL
        base_url = self._get_ocapi_base_url()
        search_url = f"{base_url}/product_search"
        
        params = {
            "q": query,
            "count": count,
            "refine_1": "orderable_only=true"
        }
        
        if category:
            params["refine_2"] = f"cgid={category}"
        
        if max_price:
            params["pmax"] = max_price
        
        if min_price:
            params["pmin"] = min_price
        
        try:
            # Try to authenticate first
            auth_token = self._authenticate_guest()
            headers = {}
            if auth_token:
                headers["authorization"] = auth_token
            
            response = self.client.get(search_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return data.get("hits", [])
        except Exception as e:
            # If OCAPI fails, return mock data for POC
            return self._get_mock_products(query, category, max_price, min_price)
    
    def _get_mock_products(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Return mock product data for POC when API is unavailable.
        
        This allows the POC to work even without live API access.
        """
        mock_products = [
            {
                "product_id": "599114C00",
                "product_name": "Pandora Moments Silver Heart Clasp Snake Chain Bracelet",
                "price": 599,
                "currency": "DKK",
                "image": {
                    "link": "https://us.pandora.net/dw/image/v2/AAVX_PRD/on/demandware.static/-/Sites-pandora-master-catalog/default/dw12345678/productimages/main/599114C00_RGB.jpg"
                },
                "c_material": "silver",
                "c_category": "bracelets"
            },
            {
                "product_id": "792137C01",
                "product_name": "Sparkling Heart Charm",
                "price": 349,
                "currency": "DKK",
                "image": {
                    "link": "https://us.pandora.net/dw/image/v2/AAVX_PRD/on/demandware.static/-/Sites-pandora-master-catalog/default/dw87654321/productimages/main/792137C01_RGB.jpg"
                },
                "c_material": "silver",
                "c_category": "charms"
            },
            {
                "product_id": "580719",
                "product_name": "Pandora Moments Silver Bracelet with Heart Clasp",
                "price": 549,
                "currency": "DKK",
                "image": {
                    "link": "https://us.pandora.net/dw/image/v2/AAVX_PRD/on/demandware.static/-/Sites-pandora-master-catalog/default/dw11111111/productimages/main/580719_RGB.jpg"
                },
                "c_material": "silver",
                "c_category": "bracelets"
            },
            {
                "product_id": "791725CZ",
                "product_name": "Heart of Winter Charm",
                "price": 299,
                "currency": "DKK",
                "image": {
                    "link": "https://us.pandora.net/dw/image/v2/AAVX_PRD/on/demandware.static/-/Sites-pandora-master-catalog/default/dw22222222/productimages/main/791725CZ_RGB.jpg"
                },
                "c_material": "silver",
                "c_category": "charms"
            },
            {
                "product_id": "590702HV",
                "product_name": "Pandora Moments Gold Heart Clasp Snake Chain Bracelet",
                "price": 2499,
                "currency": "DKK",
                "image": {
                    "link": "https://us.pandora.net/dw/image/v2/AAVX_PRD/on/demandware.static/-/Sites-pandora-master-catalog/default/dw33333333/productimages/main/590702HV_RGB.jpg"
                },
                "c_material": "gold",
                "c_category": "bracelets"
            },
            {
                "product_id": "196242CZ",
                "product_name": "Sparkling Wishbone Ring",
                "price": 449,
                "currency": "DKK",
                "image": {
                    "link": "https://us.pandora.net/dw/image/v2/AAVX_PRD/on/demandware.static/-/Sites-pandora-master-catalog/default/dw44444444/productimages/main/196242CZ_RGB.jpg"
                },
                "c_material": "silver",
                "c_category": "rings"
            },
        ]
        
        # Filter by query keywords
        query_lower = query.lower()
        filtered = []
        
        for product in mock_products:
            name_lower = product["product_name"].lower()
            material = product.get("c_material", "").lower()
            cat = product.get("c_category", "").lower()
            
            # Check if query matches
            query_match = any(
                word in name_lower or word in material or word in cat
                for word in query_lower.split()
            )
            
            if not query_match and query_lower not in ["jewelry", ""]:
                continue
            
            # Filter by category
            if category and cat != category.lower():
                continue
            
            # Filter by price
            price = product.get("price", 0)
            if max_price and price > max_price:
                continue
            if min_price and price < min_price:
                continue
            
            filtered.append(product)
        
        return filtered if filtered else mock_products[:3]
    
    def select_best_product(
        self,
        products: List[Dict[str, Any]],
        goal: ShoppingGoal
    ) -> Optional[Dict[str, Any]]:
        """
        Select the best product from search results based on the goal.
        
        Args:
            products: List of product data from search
            goal: Parsed shopping goal
            
        Returns:
            Best matching product or None.
        """
        if not products:
            return None
        
        scored_products = []
        
        for product in products:
            score = 0
            
            # Get product details
            name = product.get("product_name", product.get("name", "")).lower()
            price = product.get("price", 0)
            material = product.get("c_material", "").lower()
            category = product.get("c_category", "").lower()
            
            # Score based on material match
            if goal.material and goal.material.lower() in material:
                score += 30
            elif goal.material and goal.material.lower() in name:
                score += 20
            
            # Score based on category match
            if goal.category and goal.category.lower() in category:
                score += 25
            elif goal.category and goal.category.lower().rstrip("s") in name:
                score += 15
            
            # Score based on price (prefer products closer to max price but under it)
            if goal.max_price:
                if price <= goal.max_price:
                    # Higher score for prices closer to max (better value)
                    price_ratio = price / goal.max_price
                    score += int(price_ratio * 20)
                else:
                    score -= 50  # Penalize over-budget items
            
            # Score based on query keywords in name
            for word in goal.query.lower().split():
                if len(word) > 2 and word in name:
                    score += 10
            
            scored_products.append((score, product))
        
        # Sort by score descending
        scored_products.sort(key=lambda x: x[0], reverse=True)
        
        return scored_products[0][1] if scored_products else None
    
    def find_product_and_prepare_cart(
        self,
        goal: str,
        currency: Optional[str] = None
    ) -> ProductResult:
        """
        Main method: Find a product matching the goal and prepare cart metadata.
        
        Args:
            goal: Natural language shopping goal
            currency: Optional currency override
            
        Returns:
            ProductResult with product details and cart metadata.
        """
        # Parse the shopping goal
        parsed_goal = self.parse_shopping_goal(goal)
        
        if currency:
            parsed_goal.currency = currency
        
        # Search for products
        products = self.search_products(
            query=parsed_goal.query,
            category=parsed_goal.category,
            max_price=parsed_goal.max_price,
            min_price=parsed_goal.min_price
        )
        
        if not products:
            return ProductResult(
                product_id="",
                name="",
                price=0,
                currency=parsed_goal.currency,
                message=f"No products found matching: {goal}"
            )
        
        # Select the best product
        best_product = self.select_best_product(products, parsed_goal)
        
        if not best_product:
            return ProductResult(
                product_id="",
                name="",
                price=0,
                currency=parsed_goal.currency,
                message=f"Could not find a suitable product for: {goal}"
            )
        
        # Extract product details
        product_id = best_product.get("product_id", best_product.get("id", ""))
        name = best_product.get("product_name", best_product.get("name", "Unknown Product"))
        price = best_product.get("price", 0)
        
        # Get image URL
        image_data = best_product.get("image", {})
        image_url = image_data.get("link", "") if isinstance(image_data, dict) else ""
        
        # Build result
        result = ProductResult(
            product_id=product_id,
            name=name,
            price=price,
            currency=parsed_goal.currency,
            image_url=image_url,
            category=best_product.get("c_category", parsed_goal.category),
            material=best_product.get("c_material", parsed_goal.material),
            description=best_product.get("short_description", ""),
            message=f"Found {name} ({price} {parsed_goal.currency}) - Ready to add to cart."
        )
        
        return result
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def find_product_and_prepare_cart(goal: str, currency: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to find a product and prepare cart metadata.
    
    Args:
        goal: Natural language shopping goal (e.g., "silver bracelet under 700 DKK")
        currency: Optional currency override
        
    Returns:
        Dictionary with product details and cart metadata.
    """
    with CommerceAgent() as agent:
        result = agent.find_product_and_prepare_cart(goal, currency)
        return result.to_dict()
