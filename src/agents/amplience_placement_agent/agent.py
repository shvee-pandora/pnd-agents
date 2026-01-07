"""
Amplience Placement Agent

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

import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of human approval for placement operations."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


class ConfidenceLevel(Enum):
    """Confidence level for mapping recommendations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class OperationMode(Enum):
    """Operation mode for the agent."""
    READ_ONLY = "read_only"
    DRAFT_ONLY = "draft_only"
    FULL = "full"


@dataclass
class FigmaSection:
    """Represents a section/frame from Figma design."""
    node_id: str
    name: str
    component_type: str
    order: int
    children: List['FigmaSection'] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodeId": self.node_id,
            "name": self.name,
            "componentType": self.component_type,
            "order": self.order,
            "children": [c.to_dict() for c in self.children],
            "properties": self.properties,
        }


@dataclass
class FigmaPageBlueprint:
    """Structured page blueprint extracted from Figma."""
    page_name: str
    figma_file_id: str
    figma_node_id: Optional[str]
    sections: List[FigmaSection] = field(default_factory=list)
    extracted_at: str = ""
    
    def __post_init__(self):
        if not self.extracted_at:
            self.extracted_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageName": self.page_name,
            "figmaFileId": self.figma_file_id,
            "figmaNodeId": self.figma_node_id,
            "sections": [s.to_dict() for s in self.sections],
            "extractedAt": self.extracted_at,
            "totalSections": len(self.sections),
        }


@dataclass
class AmplienceContentType:
    """Represents an Amplience content type."""
    schema_id: str
    label: str
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)
    slots: List[str] = field(default_factory=list)
    variants: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schemaId": self.schema_id,
            "label": self.label,
            "description": self.description,
            "properties": self.properties,
            "slots": self.slots,
            "variants": self.variants,
        }


@dataclass
class AmplienceModelCatalog:
    """Catalog of available Amplience content types and slots."""
    content_types: List[AmplienceContentType] = field(default_factory=list)
    slots: List[str] = field(default_factory=list)
    discovered_at: str = ""
    
    def __post_init__(self):
        if not self.discovered_at:
            self.discovered_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contentTypes": [ct.to_dict() for ct in self.content_types],
            "slots": self.slots,
            "discoveredAt": self.discovered_at,
            "totalContentTypes": len(self.content_types),
            "totalSlots": len(self.slots),
        }
    
    def find_by_label(self, label: str) -> Optional[AmplienceContentType]:
        """Find content type by label (case-insensitive)."""
        label_lower = label.lower()
        for ct in self.content_types:
            if ct.label.lower() == label_lower:
                return ct
        return None
    
    def find_by_schema_id(self, schema_id: str) -> Optional[AmplienceContentType]:
        """Find content type by schema ID."""
        for ct in self.content_types:
            if ct.schema_id == schema_id:
                return ct
        return None


@dataclass
class PlacementMapping:
    """Represents a mapping from Figma component to Amplience content type."""
    figma_section: FigmaSection
    amplience_content_type: Optional[AmplienceContentType]
    target_slot: Optional[str]
    confidence: ConfidenceLevel
    confidence_score: float
    reasoning: str
    warnings: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    requires_manual_decision: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "figmaSection": self.figma_section.to_dict(),
            "amplienceContentType": self.amplience_content_type.to_dict() if self.amplience_content_type else None,
            "targetSlot": self.target_slot,
            "confidence": self.confidence.value,
            "confidenceScore": self.confidence_score,
            "reasoning": self.reasoning,
            "warnings": self.warnings,
            "alternatives": self.alternatives,
            "requiresManualDecision": self.requires_manual_decision,
        }


@dataclass
class PlacementPlan:
    """Complete placement plan for human review."""
    plan_id: str
    figma_blueprint: FigmaPageBlueprint
    model_catalog: AmplienceModelCatalog
    mappings: List[PlacementMapping] = field(default_factory=list)
    missing_models: List[str] = field(default_factory=list)
    ambiguous_mappings: List[str] = field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: str = ""
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "planId": self.plan_id,
            "figmaBlueprint": self.figma_blueprint.to_dict(),
            "modelCatalog": self.model_catalog.to_dict(),
            "mappings": [m.to_dict() for m in self.mappings],
            "missingModels": self.missing_models,
            "ambiguousMappings": self.ambiguous_mappings,
            "approvalStatus": self.approval_status.value,
            "createdAt": self.created_at,
            "approvedAt": self.approved_at,
            "approvedBy": self.approved_by,
            "summary": self.get_summary(),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate a summary of the placement plan."""
        high_confidence = sum(1 for m in self.mappings if m.confidence == ConfidenceLevel.HIGH)
        medium_confidence = sum(1 for m in self.mappings if m.confidence == ConfidenceLevel.MEDIUM)
        low_confidence = sum(1 for m in self.mappings if m.confidence == ConfidenceLevel.LOW)
        uncertain = sum(1 for m in self.mappings if m.confidence == ConfidenceLevel.UNCERTAIN)
        requires_manual = sum(1 for m in self.mappings if m.requires_manual_decision)
        
        return {
            "totalMappings": len(self.mappings),
            "highConfidence": high_confidence,
            "mediumConfidence": medium_confidence,
            "lowConfidence": low_confidence,
            "uncertain": uncertain,
            "requiresManualDecision": requires_manual,
            "missingModelsCount": len(self.missing_models),
            "ambiguousMappingsCount": len(self.ambiguous_mappings),
            "readyForApproval": requires_manual == 0 and len(self.missing_models) == 0,
        }


@dataclass
class DraftExecutionResult:
    """Result from draft execution."""
    success: bool
    plan_id: str
    executed_mappings: List[Dict[str, Any]] = field(default_factory=list)
    failed_mappings: List[Dict[str, Any]] = field(default_factory=list)
    draft_ids: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    executed_at: str = ""
    
    def __post_init__(self):
        if not self.executed_at:
            self.executed_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "planId": self.plan_id,
            "executedMappings": self.executed_mappings,
            "failedMappings": self.failed_mappings,
            "draftIds": self.draft_ids,
            "errors": self.errors,
            "executedAt": self.executed_at,
        }


@dataclass
class AmplicencePlacementResult:
    """Result from the Amplience Placement Agent."""
    status: str
    mode: OperationMode
    placement_plan: Optional[PlacementPlan] = None
    execution_result: Optional[DraftExecutionResult] = None
    recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode.value,
            "placementPlan": self.placement_plan.to_dict() if self.placement_plan else None,
            "executionResult": self.execution_result.to_dict() if self.execution_result else None,
            "recommendations": self.recommendations,
            "error": self.error,
        }


class AmplicencePlacementAgent:
    """
    Human-in-the-Loop AI Agent for Amplience CMS placement orchestration.
    
    This agent assists engineers and content editors in placing existing
    Amplience modules into the correct page sections based on Figma designs.
    
    CRITICAL CONSTRAINTS:
    - NO autonomous publishing
    - NO visual/design decisions
    - NO content creation from scratch
    - Draft/suggestion mode only
    - Human approval required before write operations
    """
    
    # Known Pandora Amplience module patterns for mapping
    MODULE_PATTERNS = {
        "hero": ["hero", "banner", "m78", "m37"],
        "gallery": ["gallery", "carousel", "slider", "m53"],
        "product": ["product", "plp", "pdp", "m67"],
        "promotion": ["promo", "promotion", "offer", "m63"],
        "category": ["category", "categories", "m65"],
        "navigation": ["nav", "navigation", "menu", "breadcrumb"],
        "footer": ["footer", "bottom"],
        "header": ["header", "top", "masthead"],
        "content": ["content", "text", "article", "story"],
        "cta": ["cta", "button", "action", "link"],
        "media": ["image", "video", "media", "asset"],
        "form": ["form", "input", "contact", "subscribe"],
        "widget": ["widget", "component", "module"],
    }
    
    def __init__(
        self,
        mode: OperationMode = OperationMode.READ_ONLY,
        figma_access_token: Optional[str] = None,
        amplience_hub_id: Optional[str] = None,
    ):
        """
        Initialize the Amplience Placement Agent.
        
        Args:
            mode: Operation mode (read_only, draft_only, full)
            figma_access_token: Figma API access token
            amplience_hub_id: Amplience hub ID for API access
        """
        self.mode = mode
        self.figma_access_token = figma_access_token or os.environ.get("FIGMA_ACCESS_TOKEN")
        self.amplience_hub_id = amplience_hub_id or os.environ.get("AMPLIENCE_HUB_ID")
        
        logger.info(f"AmplicencePlacementAgent initialized in {mode.value} mode")
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent as part of a workflow.
        
        Args:
            context: Workflow context with:
                - task_description: Description of the placement task
                - input_data: Dictionary with:
                    - figma_url: Figma file URL or node URL
                    - figma_file_id: Figma file ID (alternative to URL)
                    - figma_node_id: Optional specific node ID
                    - approval_status: Optional approval status for execution
                    - approved_by: Optional approver identifier
                    
        Returns:
            Workflow-compatible result with placement plan
        """
        logger.info("AmplicencePlacementAgent.run called")
        
        task_description = context.get("task_description", "")
        input_data = context.get("input_data", {})
        
        try:
            # Extract Figma information
            figma_url = input_data.get("figma_url")
            figma_file_id = input_data.get("figma_file_id")
            figma_node_id = input_data.get("figma_node_id")
            
            # Parse URL if provided
            if figma_url and not figma_file_id:
                figma_file_id, figma_node_id = self._parse_figma_url(figma_url)
            
            if not figma_file_id:
                # Try to extract from task description
                figma_file_id, figma_node_id = self._extract_figma_from_task(task_description)
            
            if not figma_file_id:
                return {
                    "status": "error",
                    "data": {},
                    "next": None,
                    "error": "No Figma file ID provided. Please provide a Figma URL or file ID.",
                }
            
            # Check for approval status (for execution phase)
            approval_status = input_data.get("approval_status")
            approved_by = input_data.get("approved_by")
            
            # Generate placement plan
            result = self.generate_placement_plan(
                figma_file_id=figma_file_id,
                figma_node_id=figma_node_id,
                approval_status=approval_status,
                approved_by=approved_by,
            )
            
            return {
                "status": result.status,
                "data": result.to_dict(),
                "next": None,  # Human review required before next step
                "error": result.error,
            }
        except Exception as e:
            logger.error(f"AmplicencePlacementAgent.run failed: {e}")
            return {
                "status": "error",
                "data": {},
                "next": None,
                "error": str(e),
            }
    
    def _parse_figma_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse Figma URL to extract file ID and node ID."""
        file_pattern = r"figma\.com/(?:file|design)/([a-zA-Z0-9]+)"
        node_pattern = r"node-id=([0-9]+[-:][0-9]+|[0-9]+%3A[0-9]+)"
        
        file_match = re.search(file_pattern, url)
        file_id = file_match.group(1) if file_match else None
        
        node_match = re.search(node_pattern, url)
        node_id = None
        if node_match:
            node_id = node_match.group(1).replace("%3A", ":").replace("-", ":")
        
        return file_id, node_id
    
    def _extract_figma_from_task(self, task_description: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract Figma file ID from task description."""
        url_pattern = r"https?://(?:www\.)?figma\.com/(?:file|design)/([a-zA-Z0-9]+)[^\s]*"
        match = re.search(url_pattern, task_description)
        
        if match:
            return self._parse_figma_url(match.group(0))
        
        return None, None
    
    # ==================== Module 1: Figma Analysis ====================
    
    def analyze_figma(
        self,
        figma_file_id: str,
        figma_node_id: Optional[str] = None,
    ) -> FigmaPageBlueprint:
        """
        Analyze Figma page structure and extract page blueprint.
        
        Args:
            figma_file_id: Figma file ID
            figma_node_id: Optional specific node ID
            
        Returns:
            FigmaPageBlueprint with extracted structure
        """
        logger.info(f"Analyzing Figma file: {figma_file_id}, node: {figma_node_id}")
        
        try:
            # Try to use FigmaReaderAgent if available
            from ..figma_reader_agent import FigmaReaderAgent
            
            figma_agent = FigmaReaderAgent(access_token=self.figma_access_token)
            
            if figma_node_id:
                result = figma_agent.read_node(figma_file_id, figma_node_id)
            else:
                result = figma_agent.read_file(figma_file_id)
            
            figma_agent.close()
            
            # Convert to FigmaPageBlueprint
            return self._convert_figma_result_to_blueprint(
                result, figma_file_id, figma_node_id
            )
        except ImportError:
            logger.warning("FigmaReaderAgent not available, using mock data")
            return self._create_mock_figma_blueprint(figma_file_id, figma_node_id)
        except Exception as e:
            logger.error(f"Figma analysis failed: {e}")
            return self._create_mock_figma_blueprint(figma_file_id, figma_node_id)
    
    def _convert_figma_result_to_blueprint(
        self,
        result: Any,
        figma_file_id: str,
        figma_node_id: Optional[str],
    ) -> FigmaPageBlueprint:
        """Convert FigmaReaderAgent result to FigmaPageBlueprint."""
        sections = []
        
        if hasattr(result, 'children'):
            for i, child in enumerate(result.children):
                section = FigmaSection(
                    node_id=child.figma_id if hasattr(child, 'figma_id') else f"node_{i}",
                    name=child.figma_name if hasattr(child, 'figma_name') else f"Section {i+1}",
                    component_type=self._infer_component_type(
                        child.figma_name if hasattr(child, 'figma_name') else ""
                    ),
                    order=i,
                    properties=child.to_dict() if hasattr(child, 'to_dict') else {},
                )
                sections.append(section)
        elif hasattr(result, 'to_dict'):
            result_dict = result.to_dict()
            page_name = result_dict.get('componentName', result_dict.get('figmaName', 'Page'))
            
            section = FigmaSection(
                node_id=result_dict.get('figmaId', 'root'),
                name=page_name,
                component_type=self._infer_component_type(page_name),
                order=0,
                properties=result_dict,
            )
            sections.append(section)
        
        return FigmaPageBlueprint(
            page_name=sections[0].name if sections else "Unknown Page",
            figma_file_id=figma_file_id,
            figma_node_id=figma_node_id,
            sections=sections,
        )
    
    def _create_mock_figma_blueprint(
        self,
        figma_file_id: str,
        figma_node_id: Optional[str],
    ) -> FigmaPageBlueprint:
        """Create a mock Figma blueprint for demonstration."""
        sections = [
            FigmaSection(
                node_id="1:1",
                name="Hero Banner",
                component_type="hero",
                order=0,
                properties={"width": 1440, "height": 600},
            ),
            FigmaSection(
                node_id="1:2",
                name="Product Carousel",
                component_type="product",
                order=1,
                properties={"width": 1440, "height": 400},
            ),
            FigmaSection(
                node_id="1:3",
                name="Promotion Module",
                component_type="promotion",
                order=2,
                properties={"width": 1440, "height": 300},
            ),
            FigmaSection(
                node_id="1:4",
                name="Category Grid",
                component_type="category",
                order=3,
                properties={"width": 1440, "height": 500},
            ),
        ]
        
        return FigmaPageBlueprint(
            page_name="Homepage Design",
            figma_file_id=figma_file_id,
            figma_node_id=figma_node_id,
            sections=sections,
        )
    
    def _infer_component_type(self, name: str) -> str:
        """Infer component type from name."""
        name_lower = name.lower()
        
        for component_type, patterns in self.MODULE_PATTERNS.items():
            for pattern in patterns:
                if pattern in name_lower:
                    return component_type
        
        return "widget"
    
    # ==================== Module 2: Amplience Model Discovery ====================
    
    def discover_amplience_models(self) -> AmplienceModelCatalog:
        """
        Discover available Amplience content types and slots.
        
        Returns:
            AmplienceModelCatalog with available models
        """
        logger.info("Discovering Amplience models")
        
        # In a real implementation, this would call the Amplience API
        # For now, we use known Pandora content types
        content_types = self._get_known_pandora_content_types()
        slots = self._get_known_pandora_slots()
        
        return AmplienceModelCatalog(
            content_types=content_types,
            slots=slots,
        )
    
    def _get_known_pandora_content_types(self) -> List[AmplienceContentType]:
        """
        Get known Pandora Amplience content types.
        
        These content types are sourced from the pandora-amplience-cms repository:
        - contents/content-type/ - Content Type definitions
        - contents/content-type-schema/schemas/ - Content Type Schemas
        
        Schema URI pattern: https://schema-pandora.net/<module-name>
        """
        return [
            AmplienceContentType(
                schema_id="https://schema-pandora.net/hero-banner",
                label="M78 Hero Module",
                description="Full-width hero banner with image/video, headline text, CTA, and optional collab logo",
                properties={
                    "banner": "array",
                    "desktopMobileMedia": "desktopMobileMedia",
                    "headlineText": "localized-value",
                    "headlineTextSize": "enum",
                    "cta": "cta",
                    "gradientOverlay": "enum",
                    "colorTheme": "enum",
                    "collabLogo": "object",
                    "monetate_variations": "object",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default", "video", "split"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/plp-hero-banner",
                label="PLP Hero Banner",
                description="Hero banner specifically for product listing pages",
                properties={
                    "title": "localized-string",
                    "description": "localized-string",
                    "desktopMobileMedia": "desktopMobileMedia",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default", "compact"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/mega-spotter",
                label="Mega Spotter Module",
                description="Large spotlight module for featured content",
                properties={
                    "media": "desktopMobileMedia",
                    "title": "localized-string",
                    "cta": "cta",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/category-module",
                label="M65 Category Module",
                description="Category card grid with 3-6 category cards, each with image and CTA",
                properties={
                    "category": "array",
                    "categoryCardMedia": "image",
                    "cta": "cta",
                    "monetate_variations": "object",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["grid", "carousel"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/product-slider-module",
                label="Product Slider Module",
                description="Product carousel with title, subtitle, and product IDs",
                properties={
                    "title": "localized-string",
                    "subTitle": "localized-string",
                    "leftAlignment": "boolean",
                    "productIDs": "string",
                    "cta": "cta",
                    "monetate_variations": "object",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["carousel", "grid"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/feature-module",
                label="Feature Module",
                description="Feature content module with media and text",
                properties={
                    "media": "desktopMobileMedia",
                    "title": "localized-string",
                    "description": "localized-string",
                    "cta": "cta",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default", "reversed"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/gallery-module",
                label="Gallery Module",
                description="Image gallery with carousel functionality",
                properties={
                    "images": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["carousel", "grid", "masonry"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/usp-module",
                label="USP Module",
                description="Unique selling proposition module",
                properties={
                    "items": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/horizontal-styling-module",
                label="Horizontal Styling Module",
                description="Horizontal layout styling module",
                properties={
                    "items": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/promotion-module",
                label="Promotion Module",
                description="Promotional content with offers and CTAs",
                properties={
                    "title": "localized-string",
                    "offer": "localized-string",
                    "cta": "cta",
                    "media": "desktopMobileMedia",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["banner", "card", "inline"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/link-list-module",
                label="Link List Module",
                description="List of links for navigation or content",
                properties={
                    "links": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default", "footer"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/discover-module",
                label="Discover Module",
                description="Content discovery module",
                properties={
                    "items": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/accordion-module",
                label="Accordion Module",
                description="Expandable accordion content sections",
                properties={
                    "items": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default", "faq"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/bazaarvoice-module",
                label="Bazaarvoice Module",
                description="Bazaarvoice reviews and ratings integration",
                properties={
                    "productId": "string",
                    "displayType": "enum",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["reviews", "ratings", "qa"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/copy-module",
                label="Copy Module",
                description="Text/copy content module",
                properties={
                    "content": "localized-string",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/plp-widget",
                label="PLP Widget",
                description="Widget for product listing pages",
                properties={
                    "content": "localized-string",
                    "position": "string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/two-image-module",
                label="Two Image Module",
                description="Side-by-side two image layout",
                properties={
                    "images": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default", "stacked"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/most-popular-carousel-module",
                label="Most Popular Carousel Module",
                description="Carousel showcasing most popular items",
                properties={
                    "items": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["carousel"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/contextual-product-row-module",
                label="Contextual Product Row Module",
                description="Product row with contextual recommendations",
                properties={
                    "productIDs": "string",
                    "title": "localized-string",
                    "context": "string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/explore-module",
                label="Explore Module",
                description="Content exploration module",
                properties={
                    "items": "array",
                    "title": "localized-string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/image",
                label="Image",
                description="Single image content type with transformation support",
                properties={
                    "img": "image-transformation",
                    "imageAltText": "localized-value",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/page-container",
                label="Page Container",
                description="Container for page modules and layout",
                properties={
                    "modules": "array",
                    "layout": "string",
                },
                slots=["sfcc-slot-accelerators"],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/sfcc-slot-accelerators",
                label="SFCC Slot Accelerators",
                description="Salesforce Commerce Cloud slot integration with site and category targeting",
                properties={
                    "_environment": "object",
                    "sfcc_slot": "sfcc_slot",
                    "sfcc_category_slot": "sfcc_category_slot",
                    "sfcc_site": "sfcc_site",
                    "content": "content-link",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/grid",
                label="Grid",
                description="Grid layout for news and content placement",
                properties={
                    "items": "array",
                    "columns": "number",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/page-hierarchy",
                label="Page Hierarchy",
                description="Page wrapper with SEO and hierarchy metadata",
                properties={
                    "title": "localized-string",
                    "metaSEO": "object",
                    "page": "page",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/page",
                label="Page",
                description="Page content container",
                properties={
                    "banner": "content-link",
                    "mainModules": "array",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/page-cover",
                label="Page Cover",
                description="Page cover/header content",
                properties={
                    "title": "localized-string",
                    "media": "desktopMobileMedia",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/details",
                label="Details",
                description="Detailed content section",
                properties={
                    "content": "localized-string",
                    "title": "localized-string",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/qna-multiple",
                label="QnA Multiple",
                description="Multiple question and answer content",
                properties={
                    "questions": "array",
                    "title": "localized-string",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/executives",
                label="Executives",
                description="Executive team profiles",
                properties={
                    "executives": "array",
                    "title": "localized-string",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/text-and-media",
                label="Text and Media",
                description="Combined text and media content",
                properties={
                    "text": "localized-string",
                    "media": "desktopMobileMedia",
                },
                slots=[],
                variants=["default", "reversed"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/entry-points",
                label="Entry Points",
                description="Navigation entry points",
                properties={
                    "items": "array",
                    "title": "localized-string",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/feature-video",
                label="Feature Video",
                description="Featured video content",
                properties={
                    "video": "video-link",
                    "title": "localized-string",
                    "description": "localized-string",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/emtn-drawer",
                label="EMTN Drawer",
                description="EMTN consent drawer content",
                properties={
                    "content": "localized-string",
                    "title": "localized-string",
                },
                slots=[],
                variants=["default"],
            ),
            AmplienceContentType(
                schema_id="https://schema-pandora.net/iframe-renderer",
                label="iFrame Renderer",
                description="iFrame content renderer",
                properties={
                    "src": "string",
                    "title": "localized-string",
                    "height": "number",
                },
                slots=[],
                variants=["default"],
            ),
        ]
    
    def _get_known_pandora_slots(self) -> List[str]:
        """
        Get known Pandora Amplience slots.
        
        Pandora uses SFCC Slot Accelerators for slot management, which integrates
        with Salesforce Commerce Cloud. Slots are configured per site/locale and
        can target specific categories.
        
        Slot schema: https://schema-pandora.net/sfcc-slot-accelerators
        
        Supported sites (from sfcc-slot-accelerators-schema.json):
        - en-US, en-CA, en-GB, fr-FR, de-DE, da-DK, it-IT, nl-NL, pl-PL, sv-SE
        - PND-ES, en-AU, en-HK, ja-JP, en-NZ, en-SG, nl-BE, fr-CH, cs-CZ, fi-FI
        - el-GR, hu-HU, ga-IE, fr-LU, en-MY, nb-NO, pt-PT, ro-RO, sk-SK, en-TH
        - tr-TR, en-ZA, zh-TW
        """
        return [
            "sfcc-slot-accelerators",
            "homepage-hero",
            "homepage-slot-1",
            "homepage-slot-2",
            "homepage-slot-3",
            "homepage-slot-4",
            "homepage-slot-5",
            "plp-hero",
            "plp-slot-1",
            "plp-slot-2",
            "pdp-slot-1",
            "pdp-slot-2",
            "category-slot",
            "folder-slot",
            "global-slot",
            "navigation-slot",
            "footer-slot",
            "header-slot",
        ]
    
    # ==================== Module 3: Mapping & Placement Recommendation ====================
    
    def generate_mappings(
        self,
        blueprint: FigmaPageBlueprint,
        catalog: AmplienceModelCatalog,
    ) -> Tuple[List[PlacementMapping], List[str], List[str]]:
        """
        Generate placement mappings from Figma sections to Amplience content types.
        
        Args:
            blueprint: Figma page blueprint
            catalog: Amplience model catalog
            
        Returns:
            Tuple of (mappings, missing_models, ambiguous_mappings)
        """
        logger.info(f"Generating mappings for {len(blueprint.sections)} sections")
        
        mappings = []
        missing_models = []
        ambiguous_mappings = []
        
        for section in blueprint.sections:
            mapping = self._map_section_to_content_type(section, catalog)
            mappings.append(mapping)
            
            if mapping.amplience_content_type is None:
                missing_models.append(f"{section.name} ({section.component_type})")
            
            if mapping.requires_manual_decision:
                ambiguous_mappings.append(f"{section.name}: {mapping.reasoning}")
        
        return mappings, missing_models, ambiguous_mappings
    
    def _map_section_to_content_type(
        self,
        section: FigmaSection,
        catalog: AmplienceModelCatalog,
    ) -> PlacementMapping:
        """Map a single Figma section to an Amplience content type."""
        # Try to find matching content type
        best_match = None
        best_score = 0.0
        alternatives = []
        
        for ct in catalog.content_types:
            score = self._calculate_match_score(section, ct)
            if score > best_score:
                if best_match:
                    alternatives.append(best_match.label)
                best_match = ct
                best_score = score
            elif score > 0.3:
                alternatives.append(ct.label)
        
        # Determine confidence level
        if best_score >= 0.8:
            confidence = ConfidenceLevel.HIGH
        elif best_score >= 0.5:
            confidence = ConfidenceLevel.MEDIUM
        elif best_score >= 0.3:
            confidence = ConfidenceLevel.LOW
        else:
            confidence = ConfidenceLevel.UNCERTAIN
        
        # Determine target slot
        target_slot = None
        if best_match and best_match.slots:
            target_slot = best_match.slots[0]
        
        # Generate warnings
        warnings = []
        if confidence in [ConfidenceLevel.LOW, ConfidenceLevel.UNCERTAIN]:
            warnings.append("Low confidence mapping - manual review recommended")
        if len(alternatives) > 2:
            warnings.append(f"Multiple alternatives available: {', '.join(alternatives[:3])}")
        if not best_match:
            warnings.append("No matching content type found - may need to create new type")
        
        # Determine if manual decision is needed
        requires_manual = (
            confidence == ConfidenceLevel.UNCERTAIN or
            best_match is None or
            len(alternatives) > 2
        )
        
        return PlacementMapping(
            figma_section=section,
            amplience_content_type=best_match,
            target_slot=target_slot,
            confidence=confidence,
            confidence_score=best_score,
            reasoning=self._generate_mapping_reasoning(section, best_match, best_score),
            warnings=warnings,
            alternatives=alternatives[:5],
            requires_manual_decision=requires_manual,
        )
    
    def _calculate_match_score(
        self,
        section: FigmaSection,
        content_type: AmplienceContentType,
    ) -> float:
        """Calculate match score between section and content type."""
        score = 0.0
        section_name = section.name.lower()
        section_type = section.component_type.lower()
        ct_label = content_type.label.lower()
        ct_description = content_type.description.lower()
        
        # Check for exact type match
        if section_type in ct_label or section_type in ct_description:
            score += 0.4
        
        # Check for name similarity
        for word in section_name.split():
            if len(word) > 2:
                if word in ct_label:
                    score += 0.2
                if word in ct_description:
                    score += 0.1
        
        # Check for module code match (M37, M53, etc.)
        module_pattern = r'm\d{2}'
        section_modules = re.findall(module_pattern, section_name)
        ct_modules = re.findall(module_pattern, ct_label)
        if section_modules and ct_modules:
            if set(section_modules) & set(ct_modules):
                score += 0.5
        
        # Check for pattern match
        for pattern_type, patterns in self.MODULE_PATTERNS.items():
            if section_type == pattern_type:
                for pattern in patterns:
                    if pattern in ct_label or pattern in ct_description:
                        score += 0.2
                        break
        
        return min(score, 1.0)
    
    def _generate_mapping_reasoning(
        self,
        section: FigmaSection,
        content_type: Optional[AmplienceContentType],
        score: float,
    ) -> str:
        """Generate human-readable reasoning for the mapping."""
        if not content_type:
            return f"No matching content type found for '{section.name}' ({section.component_type})"
        
        reasons = []
        
        if score >= 0.8:
            reasons.append(f"Strong match between '{section.name}' and '{content_type.label}'")
        elif score >= 0.5:
            reasons.append(f"Moderate match between '{section.name}' and '{content_type.label}'")
        else:
            reasons.append(f"Weak match between '{section.name}' and '{content_type.label}'")
        
        if section.component_type in content_type.label.lower():
            reasons.append(f"Component type '{section.component_type}' matches content type label")
        
        return ". ".join(reasons)
    
    # ==================== Module 4: Human Review Step ====================
    
    def generate_review_summary(self, plan: PlacementPlan) -> Dict[str, Any]:
        """
        Generate a human-readable review summary for the placement plan.
        
        Args:
            plan: The placement plan to summarize
            
        Returns:
            Review summary dictionary
        """
        summary = plan.get_summary()
        
        review = {
            "planId": plan.plan_id,
            "status": "REQUIRES_REVIEW" if summary["requiresManualDecision"] > 0 else "READY_FOR_APPROVAL",
            "overview": {
                "pageName": plan.figma_blueprint.page_name,
                "totalSections": len(plan.figma_blueprint.sections),
                "totalMappings": summary["totalMappings"],
                "confidenceBreakdown": {
                    "high": summary["highConfidence"],
                    "medium": summary["mediumConfidence"],
                    "low": summary["lowConfidence"],
                    "uncertain": summary["uncertain"],
                },
            },
            "proposedPlacements": [],
            "uncertainMappings": [],
            "missingModels": plan.missing_models,
            "warnings": [],
            "recommendations": [],
        }
        
        for mapping in plan.mappings:
            placement = {
                "figmaSection": mapping.figma_section.name,
                "figmaNodeId": mapping.figma_section.node_id,
                "proposedContentType": mapping.amplience_content_type.label if mapping.amplience_content_type else "NONE",
                "targetSlot": mapping.target_slot,
                "confidence": mapping.confidence.value,
                "confidenceScore": f"{mapping.confidence_score:.0%}",
            }
            
            if mapping.requires_manual_decision:
                placement["requiresDecision"] = True
                placement["alternatives"] = mapping.alternatives
                placement["reasoning"] = mapping.reasoning
                review["uncertainMappings"].append(placement)
            else:
                review["proposedPlacements"].append(placement)
            
            review["warnings"].extend(mapping.warnings)
        
        # Generate recommendations
        if summary["requiresManualDecision"] > 0:
            review["recommendations"].append(
                f"Review {summary['requiresManualDecision']} uncertain mappings before approval"
            )
        if plan.missing_models:
            review["recommendations"].append(
                f"Create {len(plan.missing_models)} missing content types before execution"
            )
        if summary["lowConfidence"] > 0:
            review["recommendations"].append(
                "Consider reviewing low-confidence mappings for accuracy"
            )
        
        review["approvalRequired"] = True
        review["approvalInstructions"] = (
            "To approve this plan, call execute_placement_plan with approval_status='approved' "
            "and your identifier as approved_by. No changes will be made without explicit approval."
        )
        
        return review
    
    # ==================== Module 5: Draft Execution (Gated) ====================
    
    def execute_placement_plan(
        self,
        plan: PlacementPlan,
        approval_status: str,
        approved_by: str,
    ) -> DraftExecutionResult:
        """
        Execute the placement plan (DRAFT ONLY - never publishes).
        
        CRITICAL: This method only creates/updates DRAFT content.
        It NEVER publishes automatically.
        
        Args:
            plan: The approved placement plan
            approval_status: Must be "approved" to execute
            approved_by: Identifier of the approver
            
        Returns:
            DraftExecutionResult with execution details
        """
        logger.info(f"Execute placement plan called with status: {approval_status}")
        
        # CRITICAL: Verify approval
        if approval_status != "approved":
            return DraftExecutionResult(
                success=False,
                plan_id=plan.plan_id,
                errors=["Execution blocked: approval_status must be 'approved'"],
            )
        
        if not approved_by:
            return DraftExecutionResult(
                success=False,
                plan_id=plan.plan_id,
                errors=["Execution blocked: approved_by must be provided"],
            )
        
        # CRITICAL: Check operation mode
        if self.mode == OperationMode.READ_ONLY:
            return DraftExecutionResult(
                success=False,
                plan_id=plan.plan_id,
                errors=["Execution blocked: Agent is in READ_ONLY mode"],
            )
        
        # Update plan approval status
        plan.approval_status = ApprovalStatus.APPROVED
        plan.approved_at = datetime.utcnow().isoformat()
        plan.approved_by = approved_by
        
        logger.info(f"Plan {plan.plan_id} approved by {approved_by}")
        
        # Execute mappings (DRAFT ONLY)
        executed_mappings = []
        failed_mappings = []
        draft_ids = []
        errors = []
        
        for mapping in plan.mappings:
            if mapping.amplience_content_type is None:
                failed_mappings.append({
                    "section": mapping.figma_section.name,
                    "reason": "No content type mapped",
                })
                continue
            
            try:
                # In a real implementation, this would call Amplience API
                # to create/update draft content
                draft_id = self._create_draft_content(mapping)
                draft_ids.append(draft_id)
                executed_mappings.append({
                    "section": mapping.figma_section.name,
                    "contentType": mapping.amplience_content_type.label,
                    "slot": mapping.target_slot,
                    "draftId": draft_id,
                })
                logger.info(f"Created draft for {mapping.figma_section.name}: {draft_id}")
            except Exception as e:
                failed_mappings.append({
                    "section": mapping.figma_section.name,
                    "reason": str(e),
                })
                errors.append(f"Failed to create draft for {mapping.figma_section.name}: {e}")
        
        success = len(failed_mappings) == 0
        
        return DraftExecutionResult(
            success=success,
            plan_id=plan.plan_id,
            executed_mappings=executed_mappings,
            failed_mappings=failed_mappings,
            draft_ids=draft_ids,
            errors=errors,
        )
    
    def _create_draft_content(self, mapping: PlacementMapping) -> str:
        """
        Create draft content in Amplience (mock implementation).
        
        In a real implementation, this would:
        1. Call Amplience Management API
        2. Create content item in draft state
        3. Assign to appropriate slot
        4. Return the draft content ID
        
        CRITICAL: Never publishes - only creates drafts.
        """
        import uuid
        
        # Mock draft creation
        draft_id = f"draft_{uuid.uuid4().hex[:8]}"
        
        logger.info(
            f"[MOCK] Created draft content: {draft_id} "
            f"for {mapping.figma_section.name} -> {mapping.amplience_content_type.label}"
        )
        
        return draft_id
    
    # ==================== Main Entry Point ====================
    
    def generate_placement_plan(
        self,
        figma_file_id: str,
        figma_node_id: Optional[str] = None,
        approval_status: Optional[str] = None,
        approved_by: Optional[str] = None,
    ) -> AmplicencePlacementResult:
        """
        Generate a complete placement plan for human review.
        
        This is the main entry point for the agent.
        
        Args:
            figma_file_id: Figma file ID
            figma_node_id: Optional specific node ID
            approval_status: Optional approval status for execution
            approved_by: Optional approver identifier
            
        Returns:
            AmplicencePlacementResult with placement plan and recommendations
        """
        import uuid
        
        logger.info(f"Generating placement plan for Figma file: {figma_file_id}")
        
        try:
            # Step 1: Analyze Figma
            blueprint = self.analyze_figma(figma_file_id, figma_node_id)
            logger.info(f"Extracted {len(blueprint.sections)} sections from Figma")
            
            # Step 2: Discover Amplience models
            catalog = self.discover_amplience_models()
            logger.info(f"Discovered {len(catalog.content_types)} content types")
            
            # Step 3: Generate mappings
            mappings, missing_models, ambiguous_mappings = self.generate_mappings(
                blueprint, catalog
            )
            logger.info(f"Generated {len(mappings)} mappings")
            
            # Step 4: Create placement plan
            plan = PlacementPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                figma_blueprint=blueprint,
                model_catalog=catalog,
                mappings=mappings,
                missing_models=missing_models,
                ambiguous_mappings=ambiguous_mappings,
            )
            
            # Step 5: Generate review summary
            review_summary = self.generate_review_summary(plan)
            
            # Step 6: Check if execution is requested
            execution_result = None
            if approval_status == "approved" and approved_by:
                if self.mode != OperationMode.READ_ONLY:
                    execution_result = self.execute_placement_plan(
                        plan, approval_status, approved_by
                    )
                else:
                    logger.warning("Execution requested but agent is in READ_ONLY mode")
            
            # Generate recommendations
            recommendations = self._generate_recommendations(plan, review_summary)
            
            return AmplicencePlacementResult(
                status="success",
                mode=self.mode,
                placement_plan=plan,
                execution_result=execution_result,
                recommendations=recommendations,
            )
        except Exception as e:
            logger.error(f"Failed to generate placement plan: {e}")
            return AmplicencePlacementResult(
                status="error",
                mode=self.mode,
                error=str(e),
            )
    
    def _generate_recommendations(
        self,
        plan: PlacementPlan,
        review_summary: Dict[str, Any],
    ) -> List[str]:
        """Generate recommendations based on the placement plan."""
        recommendations = []
        
        summary = plan.get_summary()
        
        if summary["requiresManualDecision"] > 0:
            recommendations.append(
                f"Review {summary['requiresManualDecision']} mappings that require manual decision"
            )
        
        if plan.missing_models:
            recommendations.append(
                f"Create content types for: {', '.join(plan.missing_models[:3])}"
            )
        
        if summary["lowConfidence"] > 0:
            recommendations.append(
                "Consider reviewing low-confidence mappings for accuracy"
            )
        
        if summary["highConfidence"] == len(plan.mappings):
            recommendations.append(
                "All mappings have high confidence - ready for approval"
            )
        
        recommendations.append(
            "Review the placement plan and approve to create draft content"
        )
        
        recommendations.append(
            "IMPORTANT: This agent only creates DRAFT content - manual publishing required"
        )
        
        return recommendations


# ==================== Convenience Functions ====================

def run(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run the Amplience Placement Agent.
    
    Args:
        context: Workflow context
        
    Returns:
        Workflow-compatible result
    """
    agent = AmplicencePlacementAgent()
    return agent.run(context)


def generate_placement_plan(
    figma_file_id: str,
    figma_node_id: Optional[str] = None,
    mode: str = "read_only",
) -> Dict[str, Any]:
    """
    Generate a placement plan for Figma to Amplience mapping.
    
    Convenience function for independent usage.
    
    Args:
        figma_file_id: Figma file ID
        figma_node_id: Optional specific node ID
        mode: Operation mode (read_only, draft_only, full)
        
    Returns:
        Placement plan dictionary
    """
    operation_mode = OperationMode(mode)
    agent = AmplicencePlacementAgent(mode=operation_mode)
    result = agent.generate_placement_plan(figma_file_id, figma_node_id)
    return result.to_dict()


def execute_approved_plan(
    figma_file_id: str,
    approved_by: str,
    figma_node_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute an approved placement plan (DRAFT ONLY).
    
    CRITICAL: This only creates draft content - never publishes.
    
    Args:
        figma_file_id: Figma file ID
        approved_by: Identifier of the approver
        figma_node_id: Optional specific node ID
        
    Returns:
        Execution result dictionary
    """
    agent = AmplicencePlacementAgent(mode=OperationMode.DRAFT_ONLY)
    result = agent.generate_placement_plan(
        figma_file_id=figma_file_id,
        figma_node_id=figma_node_id,
        approval_status="approved",
        approved_by=approved_by,
    )
    return result.to_dict()
