"""
Measure Agent Implementation.

The Measure Agent extracts quantities from architectural drawings following
measurement standards (SA Standard System / UK NRM). It:
1. Receives intake results with measurement scope
2. Analyzes drawings using vision to extract dimensions and quantities
3. Produces structured quantity data with audit trail
4. Flags clarifications needed from architects

Outputs:
- quantities.json: Structured quantity data by element
- take_off_notes.md: Methodology and assumptions
- clarifications.md: Questions for architect/engineer
- measurement_confidence.json: Per-element confidence scores
"""

import asyncio
import base64
import json
import logging
import re
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from ..tools.common import (
    ToolResult,
    ToolStatus,
    DrawingType,
    DrawingInfo,
    MeasurementScope,
    MeasurableElement,
)

logger = logging.getLogger(__name__)


class MeasurementStandard(Enum):
    """Measurement standard to apply."""
    SA_STANDARD = "sa_standard"  # South African Standard System
    NRM1 = "nrm1"  # UK NRM1 - Cost estimating
    NRM2 = "nrm2"  # UK NRM2 - Detailed measurement


class ElementCategory(Enum):
    """High-level element categories per measurement hierarchy."""
    SUBSTRUCTURE = "substructure"
    SUPERSTRUCTURE = "superstructure"
    EXTERNAL_ENVELOPE = "external_envelope"
    INTERNAL_FINISHES = "internal_finishes"
    SERVICES = "services"
    EXTERNAL_WORKS = "external_works"


class UnitOfMeasure(Enum):
    """Standard units of measurement."""
    SQUARE_METRES = "m²"
    CUBIC_METRES = "m³"
    LINEAR_METRES = "m"
    NUMBER = "nr"
    KILOGRAMS = "kg"
    TONNES = "t"
    ITEM = "item"


@dataclass
class QuantityItem:
    """A single measured quantity item."""
    item_id: str
    element_ref: str  # e.g., "1.1.1" for hierarchy
    description: str
    quantity: float
    unit: UnitOfMeasure
    nrm_reference: Optional[str] = None
    source_drawing: Optional[str] = None
    source_page: Optional[int] = None
    measurement_method: str = ""  # How the measurement was taken
    calculation: Optional[str] = None  # e.g., "10.5m x 3.2m = 33.6m²"
    confidence: float = 0.0
    assumptions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "element_ref": self.element_ref,
            "description": self.description,
            "quantity": self.quantity,
            "unit": self.unit.value,
            "nrm_reference": self.nrm_reference,
            "source_drawing": self.source_drawing,
            "source_page": self.source_page,
            "measurement_method": self.measurement_method,
            "calculation": self.calculation,
            "confidence": self.confidence,
            "assumptions": self.assumptions,
            "notes": self.notes,
        }


@dataclass
class ElementGroup:
    """A group of quantity items under an element category."""
    category: ElementCategory
    element_code: str  # e.g., "1.1"
    element_name: str  # e.g., "Substructure - Foundations"
    items: list[QuantityItem] = field(default_factory=list)
    subtotal_value: float = 0.0  # For QS summary

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "element_code": self.element_code,
            "element_name": self.element_name,
            "items": [i.to_dict() for i in self.items],
            "item_count": len(self.items),
        }


@dataclass
class ClarificationItem:
    """An item requiring clarification from the design team."""
    clarification_id: str
    priority: str  # "high", "medium", "low"
    category: str  # e.g., "dimensions", "specification", "scope"
    question: str
    context: str
    affected_elements: list[str] = field(default_factory=list)
    suggested_assumption: Optional[str] = None
    source_drawing: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "clarification_id": self.clarification_id,
            "priority": self.priority,
            "category": self.category,
            "question": self.question,
            "context": self.context,
            "affected_elements": self.affected_elements,
            "suggested_assumption": self.suggested_assumption,
            "source_drawing": self.source_drawing,
        }


@dataclass
class MeasurementConfidence:
    """Confidence assessment for a measurement category."""
    category: str
    overall_confidence: float
    factors: dict[str, float] = field(default_factory=dict)
    limiting_factors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "overall_confidence": self.overall_confidence,
            "factors": self.factors,
            "limiting_factors": self.limiting_factors,
            "recommendations": self.recommendations,
        }


@dataclass
class MeasureResult:
    """Complete result of measurement extraction."""
    project_id: str
    measurement_standard: MeasurementStandard
    element_groups: list[ElementGroup] = field(default_factory=list)
    clarifications: list[ClarificationItem] = field(default_factory=list)
    confidence_scores: list[MeasurementConfidence] = field(default_factory=list)
    processing_time_ms: float = 0.0
    drawings_analyzed: int = 0
    total_items: int = 0
    assumptions_made: list[str] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "measurement_standard": self.measurement_standard.value,
            "measurement_date": datetime.now().isoformat(),
            "element_groups": [g.to_dict() for g in self.element_groups],
            "summary": {
                "drawings_analyzed": self.drawings_analyzed,
                "total_items": self.total_items,
                "element_group_count": len(self.element_groups),
                "clarifications_count": len(self.clarifications),
            },
            "assumptions_made": self.assumptions_made,
            "exclusions": self.exclusions,
            "processing_time_ms": self.processing_time_ms,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# Vision prompt for quantity extraction
MEASUREMENT_PROMPT = """You are an expert Quantity Surveyor analyzing architectural drawings to extract quantities.

Your task is to carefully measure and quantify elements visible in this drawing.

**Drawing Information:**
- Drawing Type: {drawing_type}
- Drawing Number: {drawing_number}
- Scale: {scale}

**Measurement Standard:** {standard}

**Elements to Measure (based on drawing type):**
{elements_to_measure}

For each measurable element, extract:
1. **Description** - Clear description of the element
2. **Quantity** - Numeric value (do NOT round - maintain precision)
3. **Unit** - One of: m², m³, m, nr, kg, item
4. **Calculation** - Show your working (e.g., "10.5m x 3.2m = 33.6m²")
5. **Confidence** - How confident are you? (0.0 to 1.0)
6. **Assumptions** - List any assumptions made
7. **Notes** - Relevant observations

**Important Rules:**
- Extract ALL visible dimensions from dimension strings
- If a dimension is unclear, provide BOTH interpretations with different confidence scores
- Note any dimensions that appear to be missing
- Flag discrepancies between noted dimensions and scaled measurements
- Include ALL rooms/spaces visible on floor plans
- Count ALL doors, windows, and other enumerable items

Respond in JSON format:
```json
{{
  "measurements": [
    {{
      "element_type": "floor_area",
      "description": "Ground Floor GIFA",
      "quantity": 245.5,
      "unit": "m²",
      "calculation": "Per room schedule: 12.5x8.2 + 10.3x7.1 + ...",
      "confidence": 0.85,
      "assumptions": ["Measured to internal face of external walls"],
      "notes": ["Dimension string clear", "Scale verified"]
    }}
  ],
  "clarifications_needed": [
    {{
      "question": "Confirm floor-to-floor height for first floor",
      "context": "Section drawing shows 2850mm but floor plan note says 3000mm",
      "priority": "high",
      "suggested_assumption": "Use 3000mm as noted on floor plan"
    }}
  ],
  "drawing_observations": {{
    "quality": "good",
    "dimensions_clear": true,
    "scale_verified": true,
    "notes": ["North arrow present", "All rooms labeled"]
  }}
}}
```"""


ELEMENT_MEASUREMENT_MAP = {
    DrawingType.FLOOR_PLAN: [
        "Gross Internal Floor Area (GIFA) - measure to internal face of external walls",
        "Net Internal Area (NIA) - exclude circulation, stairs, risers",
        "Individual room areas with room names",
        "Internal wall lengths by type (partition, loadbearing)",
        "Door positions and sizes (count and measure openings)",
        "Window positions (count openings)",
        "Stair openings and lift shafts",
        "Service risers and ducts",
    ],
    DrawingType.SITE_PLAN: [
        "Total site area within boundary",
        "Building footprint area",
        "Hard landscaping areas (paving, roads, parking)",
        "Soft landscaping areas (grass, planting)",
        "Boundary lengths by type (wall, fence, hedge)",
        "Parking spaces (count)",
        "Access road lengths and widths",
        "External drainage runs",
    ],
    DrawingType.ELEVATION: [
        "External wall areas by material/finish",
        "Window areas (height x width for each)",
        "Door areas (height x width for each)",
        "Cladding/facing areas",
        "Building height to eaves/parapet",
        "Roof visible area on elevation",
        "Rainwater pipes (count)",
        "External features (canopies, projections)",
    ],
    DrawingType.SECTION: [
        "Floor-to-floor heights for each storey",
        "Floor construction depths/buildups",
        "Roof construction depth",
        "Foundation depths below ground",
        "Basement excavation depths",
        "Stair flight dimensions (going, rise, number)",
        "Ceiling heights",
        "Parapet/upstand heights",
    ],
    DrawingType.ROOF_PLAN: [
        "Roof area by type (flat, pitched)",
        "Roof perimeter length",
        "Ridge lengths",
        "Hip lengths",
        "Valley lengths",
        "Eaves lengths",
        "Rainwater outlets (count)",
        "Rooflights (count and size)",
    ],
    DrawingType.REFLECTED_CEILING: [
        "Suspended ceiling areas by type",
        "Ceiling grid areas",
        "Light fittings (count by type)",
        "Access panels (count)",
        "Diffusers/grilles (count)",
        "Exposed services runs",
        "Bulkhead areas",
    ],
    DrawingType.STRUCTURAL: [
        "Foundation types and sizes",
        "Ground beams (lengths, sections)",
        "Columns (count, sizes)",
        "Beams (lengths, sections)",
        "Floor slab areas and thicknesses",
        "Retaining walls (areas, heights)",
        "Pile caps (count, sizes)",
    ],
}


class MeasureAgent:
    """
    Measure Agent - Senior Measurer extracting quantities from drawings.

    Follows measurement standards rigorously, documents all assumptions,
    maintains full audit trail, and flags clarifications rather than guessing.

    Principles:
    - Follow the Standard System rigorously
    - Document every measurement assumption
    - Calculate both interpretations when drawings are ambiguous
    - Never round until final presentation
    - Maintain full audit trail of take-off logic
    """

    # NRM element hierarchy codes
    ELEMENT_CODES = {
        ElementCategory.SUBSTRUCTURE: {
            "prefix": "1",
            "elements": {
                "1.1": "Substructure",
                "1.1.1": "Standard foundations",
                "1.1.2": "Specialist foundations",
                "1.1.3": "Basement excavation",
                "1.1.4": "Basement retaining walls",
                "1.1.5": "Basement ground floor",
            }
        },
        ElementCategory.SUPERSTRUCTURE: {
            "prefix": "2",
            "elements": {
                "2.1": "Frame",
                "2.2": "Upper floors",
                "2.3": "Roof",
                "2.4": "Stairs and ramps",
                "2.5": "External walls",
                "2.6": "Windows and external doors",
                "2.7": "Internal walls and partitions",
                "2.8": "Internal doors",
            }
        },
        ElementCategory.INTERNAL_FINISHES: {
            "prefix": "3",
            "elements": {
                "3.1": "Wall finishes",
                "3.2": "Floor finishes",
                "3.3": "Ceiling finishes",
            }
        },
        ElementCategory.SERVICES: {
            "prefix": "5",
            "elements": {
                "5.1": "Sanitary installations",
                "5.2": "Services equipment",
                "5.3": "Disposal installations",
                "5.4": "Water installations",
                "5.5": "Heat source",
                "5.6": "Space heating and air conditioning",
                "5.7": "Ventilation",
                "5.8": "Electrical installations",
            }
        },
        ElementCategory.EXTERNAL_WORKS: {
            "prefix": "8",
            "elements": {
                "8.1": "Site preparation",
                "8.2": "Roads, paths, pavings",
                "8.3": "Soft landscaping",
                "8.4": "Fencing, railings, walls",
                "8.5": "External drainage",
                "8.6": "External services",
            }
        },
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the Measure Agent.

        Args:
            config: Configuration dict with optional keys:
                - output_dir: Directory for output files
                - measurement_standard: "sa_standard", "nrm1", or "nrm2"
                - vision_provider: "claude" (default), "anthropic", or "openai"
                - anthropic_api_key: API key for Anthropic
                - openai_api_key: API key for OpenAI
                - region: Project region for standard selection
        """
        self.config = config or {}
        self.output_dir = Path(config.get("output_dir", "./measure_output")) if config else Path("./measure_output")

        # Determine measurement standard
        standard_str = config.get("measurement_standard", "sa_standard") if config else "sa_standard"
        region = config.get("region", "za") if config else "za"

        # UK projects default to NRM2
        if region.lower() in ["uk", "gb", "england", "scotland", "wales"]:
            self.measurement_standard = MeasurementStandard.NRM2
        else:
            try:
                self.measurement_standard = MeasurementStandard(standard_str)
            except ValueError:
                self.measurement_standard = MeasurementStandard.SA_STANDARD

        # Vision config
        self.vision_provider = config.get("vision_provider", "claude") if config else "claude"
        self.api_key = config.get("anthropic_api_key") or config.get("openai_api_key") if config else None

        self.logger = logging.getLogger(self.__class__.__name__)

        # Track item IDs for uniqueness
        self._item_counter = 0

    def _generate_item_id(self) -> str:
        """Generate unique item ID."""
        self._item_counter += 1
        return f"QTY-{self._item_counter:04d}"

    def _generate_clarification_id(self) -> str:
        """Generate unique clarification ID."""
        return f"CLR-{uuid.uuid4().hex[:6].upper()}"

    async def measure(
        self,
        project_id: str,
        drawings: list[DrawingInfo],
        measurement_scope: Optional[MeasurementScope] = None,
        intake_output_dir: Optional[Path] = None,
    ) -> MeasureResult:
        """
        Extract quantities from drawings.

        Args:
            project_id: Project identifier
            drawings: List of DrawingInfo from intake
            measurement_scope: Optional scope from intake (defines what to measure)
            intake_output_dir: Path to intake output (for reading images)

        Returns:
            MeasureResult with quantities, clarifications, and confidence scores
        """
        start_time = time.time()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._item_counter = 0

        errors: list[dict[str, Any]] = []
        warnings: list[str] = []
        all_clarifications: list[ClarificationItem] = []
        all_items: list[QuantityItem] = []
        assumptions_made: list[str] = []

        self.logger.info(f"[{project_id}] Starting measurement extraction for {len(drawings)} drawings")
        self.logger.info(f"[{project_id}] Measurement standard: {self.measurement_standard.value}")

        # Filter drawings that are measurable
        measurable_drawings = [
            d for d in drawings
            if d.drawing_type in ELEMENT_MEASUREMENT_MAP
            and d.drawing_type != DrawingType.UNKNOWN
        ]

        if not measurable_drawings:
            warnings.append("No measurable drawings found in package")
            return MeasureResult(
                project_id=project_id,
                measurement_standard=self.measurement_standard,
                processing_time_ms=(time.time() - start_time) * 1000,
                errors=errors,
                warnings=warnings,
            )

        self.logger.info(f"[{project_id}] Found {len(measurable_drawings)} measurable drawings")

        # Process each drawing
        drawings_analyzed = 0
        for drawing in measurable_drawings:
            try:
                self.logger.info(f"[{project_id}] Analyzing: {drawing.drawing_type.value} - {drawing.drawing_number or 'Unknown'}")

                # Get the image path
                image_path = self._get_drawing_image_path(drawing, intake_output_dir)

                if not image_path or not image_path.exists():
                    warnings.append(f"Image not found for drawing {drawing.drawing_number or drawing.page_number}")
                    continue

                # Extract measurements using vision
                extraction_result = await self._extract_measurements_from_drawing(
                    drawing,
                    image_path,
                    project_id,
                )

                if extraction_result.get("measurements"):
                    items = self._convert_to_quantity_items(
                        extraction_result["measurements"],
                        drawing,
                    )
                    all_items.extend(items)

                if extraction_result.get("clarifications_needed"):
                    clarifications = self._convert_to_clarifications(
                        extraction_result["clarifications_needed"],
                        drawing,
                    )
                    all_clarifications.extend(clarifications)

                if extraction_result.get("assumptions"):
                    assumptions_made.extend(extraction_result["assumptions"])

                drawings_analyzed += 1

            except Exception as e:
                self.logger.error(f"[{project_id}] Failed to process drawing: {e}")
                errors.append({
                    "type": "MEASUREMENT_ERROR",
                    "drawing": drawing.drawing_number or str(drawing.page_number),
                    "message": str(e),
                })

        # Organize items into element groups
        element_groups = self._organize_into_groups(all_items)

        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(
            element_groups,
            drawings,
            measurement_scope,
        )

        # Determine exclusions based on what couldn't be measured
        exclusions = self._determine_exclusions(drawings, measurement_scope)

        processing_time = (time.time() - start_time) * 1000

        result = MeasureResult(
            project_id=project_id,
            measurement_standard=self.measurement_standard,
            element_groups=element_groups,
            clarifications=all_clarifications,
            confidence_scores=confidence_scores,
            processing_time_ms=processing_time,
            drawings_analyzed=drawings_analyzed,
            total_items=len(all_items),
            assumptions_made=list(set(assumptions_made)),
            exclusions=exclusions,
            errors=errors,
            warnings=warnings,
        )

        # Save outputs
        await self._save_outputs(project_id, result, all_clarifications, confidence_scores)

        self.logger.info(f"[{project_id}] Measurement complete: {len(all_items)} items from {drawings_analyzed} drawings")

        return result

    def _get_drawing_image_path(
        self,
        drawing: DrawingInfo,
        intake_output_dir: Optional[Path],
    ) -> Optional[Path]:
        """Get the image path for a drawing."""
        # First check if drawing has direct image path
        if drawing.image_path:
            path = Path(drawing.image_path)
            if path.exists():
                return path

        # Try to find in intake output directory
        if intake_output_dir:
            # Standard naming convention: filename_page_N.png
            source_file = Path(drawing.file_path).stem
            image_name = f"{source_file}_page_{drawing.page_number}.png"
            image_path = intake_output_dir / "images" / image_name
            if image_path.exists():
                return image_path

        return None

    async def _extract_measurements_from_drawing(
        self,
        drawing: DrawingInfo,
        image_path: Path,
        project_id: str,
    ) -> dict[str, Any]:
        """Extract measurements from a single drawing using vision."""
        # Build the prompt
        elements_to_measure = ELEMENT_MEASUREMENT_MAP.get(drawing.drawing_type, [])
        elements_list = "\n".join(f"- {e}" for e in elements_to_measure)

        prompt = MEASUREMENT_PROMPT.format(
            drawing_type=drawing.drawing_type.value.replace("_", " ").title(),
            drawing_number=drawing.drawing_number or "Not specified",
            scale=drawing.scale or "Not specified",
            standard=self.measurement_standard.value.upper(),
            elements_to_measure=elements_list,
        )

        try:
            if self.vision_provider == "claude":
                response = await self._analyze_with_claude(image_path, prompt)
            elif self.vision_provider == "anthropic":
                response = await self._analyze_with_anthropic(image_path, prompt)
            elif self.vision_provider == "openai":
                response = await self._analyze_with_openai(image_path, prompt)
            else:
                raise ValueError(f"Unknown vision provider: {self.vision_provider}")

            # Parse JSON response
            return self._parse_measurement_response(response)

        except Exception as e:
            self.logger.error(f"Vision analysis failed: {e}")
            return {
                "measurements": [],
                "clarifications_needed": [],
                "error": str(e),
            }

    async def _analyze_with_claude(self, image_path: Path, prompt: str) -> str:
        """Analyze drawing using Claude CLI."""
        full_prompt = f"""Please analyze this architectural drawing image at: {image_path}

{prompt}"""

        try:
            result = subprocess.run(
                [
                    "claude",
                    "--print",
                    "--allowedTools", "Read",
                    "-p", full_prompt,
                    str(image_path),
                ],
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout for measurement
                cwd=str(image_path.parent),
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude CLI failed: {result.stderr}")

            return result.stdout

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude CLI timed out during measurement analysis")
        except FileNotFoundError:
            raise RuntimeError("Claude CLI not found")

    async def _analyze_with_anthropic(self, image_path: Path, prompt: str) -> str:
        """Analyze drawing using Anthropic API directly."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        image_data, media_type = self._encode_image(image_path)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )

        return message.content[0].text

    async def _analyze_with_openai(self, image_path: Path, prompt: str) -> str:
        """Analyze drawing using OpenAI Vision API."""
        import openai

        client = openai.OpenAI(api_key=self.api_key)
        image_data, media_type = self._encode_image(image_path)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=4096,
        )

        return response.choices[0].message.content

    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        """Encode image to base64."""
        suffix = image_path.suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }
        media_type = media_types.get(suffix, "image/png")

        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        return image_data, media_type

    def _parse_measurement_response(self, response: str) -> dict[str, Any]:
        """Parse the vision model response."""
        # Extract JSON from response
        json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                return {"measurements": [], "clarifications_needed": [], "error": "No JSON found"}

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            return {"measurements": [], "clarifications_needed": [], "error": f"JSON parse error: {e}"}

    def _convert_to_quantity_items(
        self,
        measurements: list[dict[str, Any]],
        drawing: DrawingInfo,
    ) -> list[QuantityItem]:
        """Convert raw measurements to QuantityItem objects."""
        items = []

        for m in measurements:
            # Map unit string to enum
            unit_str = m.get("unit", "item").lower()
            unit_map = {
                "m²": UnitOfMeasure.SQUARE_METRES,
                "m2": UnitOfMeasure.SQUARE_METRES,
                "sqm": UnitOfMeasure.SQUARE_METRES,
                "m³": UnitOfMeasure.CUBIC_METRES,
                "m3": UnitOfMeasure.CUBIC_METRES,
                "cum": UnitOfMeasure.CUBIC_METRES,
                "m": UnitOfMeasure.LINEAR_METRES,
                "lm": UnitOfMeasure.LINEAR_METRES,
                "nr": UnitOfMeasure.NUMBER,
                "no": UnitOfMeasure.NUMBER,
                "kg": UnitOfMeasure.KILOGRAMS,
                "t": UnitOfMeasure.TONNES,
                "item": UnitOfMeasure.ITEM,
            }
            unit = unit_map.get(unit_str, UnitOfMeasure.ITEM)

            # Determine element reference based on element type
            element_ref = self._determine_element_ref(m.get("element_type", ""))

            # Get NRM reference
            nrm_ref = self._get_nrm_reference(m.get("element_type", ""))

            item = QuantityItem(
                item_id=self._generate_item_id(),
                element_ref=element_ref,
                description=m.get("description", "Unknown element"),
                quantity=float(m.get("quantity", 0)),
                unit=unit,
                nrm_reference=nrm_ref,
                source_drawing=drawing.drawing_number or f"Page {drawing.page_number}",
                source_page=drawing.page_number,
                measurement_method=m.get("measurement_method", "Vision extraction"),
                calculation=m.get("calculation"),
                confidence=float(m.get("confidence", 0.5)),
                assumptions=m.get("assumptions", []),
                notes=m.get("notes", []),
            )
            items.append(item)

        return items

    def _convert_to_clarifications(
        self,
        clarifications: list[dict[str, Any]],
        drawing: DrawingInfo,
    ) -> list[ClarificationItem]:
        """Convert raw clarifications to ClarificationItem objects."""
        items = []

        for c in clarifications:
            item = ClarificationItem(
                clarification_id=self._generate_clarification_id(),
                priority=c.get("priority", "medium"),
                category=c.get("category", "general"),
                question=c.get("question", ""),
                context=c.get("context", ""),
                affected_elements=c.get("affected_elements", []),
                suggested_assumption=c.get("suggested_assumption"),
                source_drawing=drawing.drawing_number or f"Page {drawing.page_number}",
            )
            items.append(item)

        return items

    def _determine_element_ref(self, element_type: str) -> str:
        """Determine NRM element reference from element type."""
        element_type_lower = element_type.lower()

        # Map common element types to NRM codes
        type_to_ref = {
            "floor_area": "2.2",
            "gifa": "2.2",
            "wall": "2.5",
            "external_wall": "2.5",
            "internal_wall": "2.7",
            "partition": "2.7",
            "window": "2.6",
            "door": "2.6",
            "external_door": "2.6",
            "internal_door": "2.8",
            "roof": "2.3",
            "foundation": "1.1",
            "substructure": "1.1",
            "stair": "2.4",
            "ceiling": "3.3",
            "floor_finish": "3.2",
            "wall_finish": "3.1",
            "site": "8.1",
            "paving": "8.2",
            "landscaping": "8.3",
            "fence": "8.4",
            "drainage": "8.5",
        }

        for key, ref in type_to_ref.items():
            if key in element_type_lower:
                return ref

        return "9.0"  # Default to "other" if not mapped

    def _get_nrm_reference(self, element_type: str) -> Optional[str]:
        """Get NRM reference for an element type."""
        element_type_lower = element_type.lower()

        nrm_map = {
            "gifa": "NRM1 2.6",
            "floor_area": "NRM1 2.6",
            "nia": "NRM1 2.7",
            "external_wall": "NRM1 2.5.1",
            "roof": "NRM1 2.5.2",
            "window": "NRM2 L10/L20",
            "door": "NRM2 L20",
            "ceiling": "NRM2 K10/K40",
            "floor_construction": "NRM1 2.4.3",
            "foundation": "NRM2 E10",
            "partition": "NRM2 K10",
            "stair": "NRM2 L30",
        }

        for key, ref in nrm_map.items():
            if key in element_type_lower:
                return ref

        return None

    def _organize_into_groups(self, items: list[QuantityItem]) -> list[ElementGroup]:
        """Organize quantity items into element groups."""
        groups_dict: dict[str, ElementGroup] = {}

        for item in items:
            # Get the major element code (e.g., "2" from "2.5.1")
            major_code = item.element_ref.split(".")[0] if item.element_ref else "9"

            # Find corresponding category
            category = ElementCategory.SUPERSTRUCTURE  # default
            element_name = "Miscellaneous"

            for cat, info in self.ELEMENT_CODES.items():
                if info["prefix"] == major_code:
                    category = cat
                    # Get element name from sub-code
                    for code, name in info["elements"].items():
                        if item.element_ref.startswith(code):
                            element_name = name
                            break
                    else:
                        element_name = list(info["elements"].values())[0] if info["elements"] else cat.value
                    break

            group_key = f"{major_code}-{category.value}"

            if group_key not in groups_dict:
                groups_dict[group_key] = ElementGroup(
                    category=category,
                    element_code=major_code,
                    element_name=element_name,
                )

            groups_dict[group_key].items.append(item)

        return list(groups_dict.values())

    def _calculate_confidence_scores(
        self,
        element_groups: list[ElementGroup],
        drawings: list[DrawingInfo],
        measurement_scope: Optional[MeasurementScope],
    ) -> list[MeasurementConfidence]:
        """Calculate confidence scores for each element category."""
        scores = []

        for group in element_groups:
            if not group.items:
                continue

            # Average confidence from items
            avg_confidence = sum(i.confidence for i in group.items) / len(group.items)

            # Factors affecting confidence
            factors = {
                "item_confidence": avg_confidence,
                "drawing_quality": self._assess_drawing_quality(drawings),
                "dimension_availability": self._assess_dimension_availability(drawings),
            }

            # Identify limiting factors
            limiting_factors = []
            if factors["drawing_quality"] < 0.7:
                limiting_factors.append("Drawing quality affects measurement accuracy")
            if factors["dimension_availability"] < 0.7:
                limiting_factors.append("Some dimensions not annotated - scaled from drawing")

            # Items with assumptions
            items_with_assumptions = [i for i in group.items if i.assumptions]
            if items_with_assumptions:
                limiting_factors.append(f"{len(items_with_assumptions)} items include assumptions")

            # Recommendations
            recommendations = []
            if avg_confidence < 0.6:
                recommendations.append("Consider requesting clearer drawings for verification")
            if factors["dimension_availability"] < 0.5:
                recommendations.append("Request dimensioned drawings to improve accuracy")

            overall = sum(factors.values()) / len(factors)

            scores.append(MeasurementConfidence(
                category=group.category.value,
                overall_confidence=overall,
                factors=factors,
                limiting_factors=limiting_factors,
                recommendations=recommendations,
            ))

        return scores

    def _assess_drawing_quality(self, drawings: list[DrawingInfo]) -> float:
        """Assess overall drawing quality."""
        if not drawings:
            return 0.0

        quality_scores = []
        for d in drawings:
            score = d.confidence
            if d.dimensions_present:
                score += 0.2
            if d.annotations_present:
                score += 0.1
            quality_scores.append(min(score, 1.0))

        return sum(quality_scores) / len(quality_scores)

    def _assess_dimension_availability(self, drawings: list[DrawingInfo]) -> float:
        """Assess how many drawings have dimension annotations."""
        if not drawings:
            return 0.0

        dimensioned = sum(1 for d in drawings if d.dimensions_present)
        return dimensioned / len(drawings)

    def _determine_exclusions(
        self,
        drawings: list[DrawingInfo],
        measurement_scope: Optional[MeasurementScope],
    ) -> list[str]:
        """Determine what couldn't be measured and should be excluded."""
        exclusions = []

        present_types = set(d.drawing_type for d in drawings)

        # Standard exclusions based on missing drawings
        if DrawingType.STRUCTURAL not in present_types:
            exclusions.append("Structural frame quantities - no structural drawings")
        if DrawingType.MECHANICAL not in present_types:
            exclusions.append("Mechanical services - no M&E drawings")
        if DrawingType.ELECTRICAL not in present_types:
            exclusions.append("Electrical installations - no electrical drawings")
        if DrawingType.PLUMBING not in present_types:
            exclusions.append("Plumbing installations - no plumbing drawings")

        # Add exclusions from measurement scope if available
        if measurement_scope and measurement_scope.unmeasurable_elements:
            for item in measurement_scope.unmeasurable_elements:
                element = item.get("element", "Unknown")
                reason = item.get("reason", "")
                exclusions.append(f"{element} - {reason}")

        return exclusions

    async def _save_outputs(
        self,
        project_id: str,
        result: MeasureResult,
        clarifications: list[ClarificationItem],
        confidence_scores: list[MeasurementConfidence],
    ) -> None:
        """Save output files."""
        project_dir = self.output_dir
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save quantities.json
        quantities_path = project_dir / "quantities.json"
        with open(quantities_path, "w") as f:
            f.write(result.to_json(indent=2))
        self.logger.info(f"Saved: {quantities_path}")

        # Save take_off_notes.md
        notes_path = project_dir / "take_off_notes.md"
        with open(notes_path, "w") as f:
            f.write(self._generate_take_off_notes(project_id, result))
        self.logger.info(f"Saved: {notes_path}")

        # Save clarifications.md
        clarifications_path = project_dir / "clarifications.md"
        with open(clarifications_path, "w") as f:
            f.write(self._generate_clarifications_md(project_id, clarifications))
        self.logger.info(f"Saved: {clarifications_path}")

        # Save measurement_confidence.json
        confidence_path = project_dir / "measurement_confidence.json"
        with open(confidence_path, "w") as f:
            json.dump(
                {
                    "project_id": project_id,
                    "assessment_date": datetime.now().isoformat(),
                    "scores": [s.to_dict() for s in confidence_scores],
                },
                f,
                indent=2,
            )
        self.logger.info(f"Saved: {confidence_path}")

    def _generate_take_off_notes(self, project_id: str, result: MeasureResult) -> str:
        """Generate take-off notes markdown."""
        lines = [
            "# Take-Off Notes",
            "",
            f"**Project ID:** {project_id}",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Measurement Standard:** {result.measurement_standard.value.upper()}",
            "",
            "---",
            "",
            "## Summary",
            "",
            f"- **Drawings Analyzed:** {result.drawings_analyzed}",
            f"- **Total Items Measured:** {result.total_items}",
            f"- **Element Groups:** {len(result.element_groups)}",
            f"- **Clarifications Required:** {len(result.clarifications)}",
            "",
            "---",
            "",
            "## Methodology",
            "",
            "Quantities were extracted using vision-based analysis of architectural drawings. ",
            "Measurements follow the element hierarchy defined in NRM1/NRM2 where applicable.",
            "",
            "### Measurement Approach",
            "",
            "1. Floor areas measured to internal face of external walls (GIFA)",
            "2. Wall areas measured as gross, with openings deducted",
            "3. Linear items measured along centerline unless noted",
            "4. Enumerated items counted from drawings and schedules",
            "",
            "---",
            "",
            "## Assumptions Made",
            "",
        ]

        if result.assumptions_made:
            for assumption in result.assumptions_made:
                lines.append(f"- {assumption}")
        else:
            lines.append("*No significant assumptions required*")

        lines.extend([
            "",
            "---",
            "",
            "## Exclusions",
            "",
        ])

        if result.exclusions:
            for exclusion in result.exclusions:
                lines.append(f"- {exclusion}")
        else:
            lines.append("*No exclusions*")

        lines.extend([
            "",
            "---",
            "",
            "## Element Summary",
            "",
        ])

        for group in result.element_groups:
            lines.append(f"### {group.element_code} - {group.element_name}")
            lines.append("")
            lines.append(f"*{len(group.items)} items measured*")
            lines.append("")

            if group.items:
                lines.append("| Description | Qty | Unit | Confidence |")
                lines.append("|-------------|-----|------|------------|")
                for item in group.items[:10]:  # Limit to first 10
                    lines.append(f"| {item.description[:40]} | {item.quantity:.2f} | {item.unit.value} | {item.confidence:.0%} |")
                if len(group.items) > 10:
                    lines.append(f"| *...and {len(group.items) - 10} more items* | | | |")
            lines.append("")

        if result.warnings:
            lines.extend([
                "---",
                "",
                "## Warnings",
                "",
            ])
            for warning in result.warnings:
                lines.append(f"- {warning}")

        return "\n".join(lines)

    def _generate_clarifications_md(
        self,
        project_id: str,
        clarifications: list[ClarificationItem],
    ) -> str:
        """Generate clarifications markdown."""
        lines = [
            "# Clarifications Required",
            "",
            f"**Project ID:** {project_id}",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "The following items require clarification from the design team before ",
            "quantities can be finalized.",
            "",
            "---",
            "",
        ]

        if not clarifications:
            lines.append("*No clarifications required - all measurements complete*")
            return "\n".join(lines)

        # Group by priority
        high = [c for c in clarifications if c.priority == "high"]
        medium = [c for c in clarifications if c.priority == "medium"]
        low = [c for c in clarifications if c.priority == "low"]

        if high:
            lines.extend([
                "## High Priority",
                "",
                "*Must be resolved before proceeding to costing*",
                "",
            ])
            for c in high:
                lines.extend([
                    f"### {c.clarification_id}",
                    "",
                    f"**Question:** {c.question}",
                    "",
                    f"**Context:** {c.context}",
                    "",
                    f"**Source Drawing:** {c.source_drawing or 'Not specified'}",
                    "",
                ])
                if c.suggested_assumption:
                    lines.append(f"**Suggested Assumption:** {c.suggested_assumption}")
                    lines.append("")
                if c.affected_elements:
                    lines.append(f"**Affected Elements:** {', '.join(c.affected_elements)}")
                    lines.append("")
                lines.append("---")
                lines.append("")

        if medium:
            lines.extend([
                "## Medium Priority",
                "",
                "*Should be clarified to improve accuracy*",
                "",
            ])
            for c in medium:
                lines.extend([
                    f"### {c.clarification_id}",
                    "",
                    f"**Question:** {c.question}",
                    "",
                    f"**Context:** {c.context}",
                    "",
                ])
                if c.suggested_assumption:
                    lines.append(f"**Suggested Assumption:** {c.suggested_assumption}")
                lines.append("")

        if low:
            lines.extend([
                "## Low Priority",
                "",
                "*For information/record*",
                "",
            ])
            for c in low:
                lines.append(f"- **{c.clarification_id}:** {c.question}")
            lines.append("")

        return "\n".join(lines)


async def run_measure(
    project_id: str,
    drawings: list[DrawingInfo],
    measurement_scope: Optional[MeasurementScope] = None,
    intake_output_dir: Optional[str] = None,
    output_dir: str = "./measure_output",
    **kwargs,
) -> MeasureResult:
    """
    Convenience function to run measurement extraction.

    Args:
        project_id: Project identifier
        drawings: List of DrawingInfo from intake
        measurement_scope: Optional scope from intake
        intake_output_dir: Path to intake output directory
        output_dir: Output directory for results
        **kwargs: Additional config options

    Returns:
        MeasureResult
    """
    config = {
        "output_dir": output_dir,
        **kwargs,
    }

    agent = MeasureAgent(config)
    return await agent.measure(
        project_id=project_id,
        drawings=drawings,
        measurement_scope=measurement_scope,
        intake_output_dir=Path(intake_output_dir) if intake_output_dir else None,
    )
