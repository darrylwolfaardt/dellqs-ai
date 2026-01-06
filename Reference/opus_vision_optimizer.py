"""
Opus Vision Optimizer for Architectural Measurement Extraction
===============================================================

High-level interface optimized for feeding architectural drawings to
Claude Opus for measurement extraction. Handles batching, context
preservation, and provides structured recommendations for API calls.

Designed for integration with PydanticAI agents.

Usage:
    from opus_vision_optimizer import OpusVisionOptimizer, ImageBatch

    optimizer = OpusVisionOptimizer()
    batches = optimizer.prepare_for_extraction("drawing.pdf")

    for batch in batches:
        # Send batch.images to Claude Opus with batch.context_prompt
        response = await agent.run(batch.context_prompt, images=batch.images)

Dependencies:
    pip install PyMuPDF numpy pillow

Author: DELLQS-AI
Version: 1.0.0
"""

import base64
import json
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Iterator
from dataclasses import dataclass, field
from enum import Enum

from adaptive_pdf_processor import (
    AdaptivePDFProcessor,
    ProcessingResult,
    PageAnalysis,
    DensityLevel,
    ProcessingStrategy,
)


class ExtractionMode(Enum):
    """Mode for measurement extraction."""

    FULL_TAKEOFF = "full_takeoff"  # Complete quantity extraction
    DIMENSIONS_ONLY = "dimensions_only"  # Just measurements, no calculations
    VERIFICATION = "verification"  # Cross-check existing measurements
    SCHEDULE_EXTRACT = "schedule_extract"  # Extract from schedules/tables


@dataclass
class ImageData:
    """Image data ready for API submission."""

    file_path: str
    base64_data: Optional[str] = None
    width: int = 0
    height: int = 0
    source_page: int = 0
    tile_position: Optional[str] = None  # e.g., "r1c2" for row 1, col 2
    region_description: Optional[str] = None
    estimated_tokens: int = 0

    def load_base64(self) -> str:
        """Load and cache base64 data."""
        if self.base64_data is None:
            with open(self.file_path, "rb") as f:
                self.base64_data = base64.standard_b64encode(f.read()).decode("utf-8")
        return self.base64_data

    @property
    def media_type(self) -> str:
        """Get media type for API."""
        ext = Path(self.file_path).suffix.lower()
        return "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

    def to_api_format(self) -> Dict[str, Any]:
        """Format for Claude API image content."""
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": self.media_type,
                "data": self.load_base64(),
            },
        }


@dataclass
class ImageBatch:
    """A batch of images to send in a single API call."""

    images: List[ImageData]
    source_file: str
    page_numbers: List[int]
    batch_index: int
    total_batches: int
    context_prompt: str
    extraction_guidance: str
    estimated_tokens: int
    is_continuation: bool = False
    previous_context: Optional[str] = None

    def get_api_content(self) -> List[Dict[str, Any]]:
        """Get content array for Claude API messages."""
        content = []

        # Add images
        for img in self.images:
            content.append(img.to_api_format())

        # Add text prompt
        content.append({"type": "text", "text": self.context_prompt})

        return content

    @property
    def image_count(self) -> int:
        return len(self.images)


@dataclass
class PreparationResult:
    """Result of preparing a PDF for extraction."""

    source_file: str
    total_pages: int
    total_images: int
    batches: List[ImageBatch]
    processing_result: ProcessingResult
    recommendations: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

    def __iter__(self) -> Iterator[ImageBatch]:
        """Iterate over batches."""
        return iter(self.batches)

    def __len__(self) -> int:
        return len(self.batches)


class OpusVisionOptimizer:
    """
    Optimizes architectural PDFs for Claude Opus vision extraction.

    Handles:
    - Adaptive PDF processing based on density/scale
    - Intelligent batching to maximize context while respecting limits
    - Context-aware prompts for each batch
    - Tile overlap handling for seamless extraction
    """

    # Token limits (conservative estimates)
    MAX_TOKENS_PER_CALL = 150_000  # Leave headroom from 200k
    MAX_IMAGES_PER_CALL = 20  # API limit
    RECOMMENDED_IMAGES_PER_CALL = 5  # Optimal for quality

    # Extraction prompt templates
    PROMPTS = {
        ExtractionMode.FULL_TAKEOFF: """Analyze this architectural drawing for quantity surveying measurement extraction.

Extract ALL measurable elements with their dimensions:

1. **Identification**: Drawing ref, title, scale, level
2. **Walls**: Type, thickness (mm), length (mm), grid references
3. **Openings**: Ref, type (door/window), W×H (mm), wall location
4. **Rooms**: Name, L×W (mm), area (m²), floor/wall finishes
5. **Structural**: Columns, beams, slab thickness
6. **Annotations**: Levels (FFL, NGL), specs, notes

For each measurement:
- State confidence: CLEAR (readable), INFERRED (calculated), UNCERTAIN (needs clarification)
- Note any ambiguities or required clarifications

Output as structured JSON following the extraction schema.""",
        ExtractionMode.DIMENSIONS_ONLY: """Extract all visible dimensions from this architectural drawing.

Focus on:
- Linear dimensions (mm)
- Room dimensions (L×W)
- Opening sizes (W×H)
- Level annotations (FFL, NGL, SSL)
- Grid references

Output as a simple list with location references.""",
        ExtractionMode.VERIFICATION: """Cross-check the measurements in this drawing against the provided data.

Flag any discrepancies between:
- Stated dimensions vs scaled measurements
- Annotations vs drawing content
- Inconsistencies between drawings

Note confidence level for each verification.""",
        ExtractionMode.SCHEDULE_EXTRACT: """Extract all tabular/schedule data from this drawing.

Look for:
- Door schedules
- Window schedules  
- Finish schedules
- Room data schedules
- Steel/reinforcement schedules

Preserve all columns and maintain row relationships.""",
    }

    TILE_CONTEXT = """This is tile {tile_pos} of a {grid} grid covering page {page}.
Adjacent tiles have {overlap}% overlap - elements near edges may appear in multiple tiles.
Focus on elements clearly within this tile's center region."""

    CONTINUATION_CONTEXT = """This continues the extraction from the previous image(s).
Maintain consistency with previously extracted data.
Reference earlier elements by their IDs when relationships exist."""

    def __init__(
        self,
        default_dpi: int = 180,
        max_dpi: int = 300,
        tile_overlap: float = 12.0,
        output_format: str = "png",
        images_per_batch: int = 5,
        preload_base64: bool = False,
    ):
        """
        Initialize the optimizer.

        Args:
            default_dpi: Default rendering DPI
            max_dpi: Maximum DPI cap
            tile_overlap: Overlap percentage for tiles
            output_format: 'png' or 'jpg'
            images_per_batch: Target images per API call
            preload_base64: Whether to preload base64 data
        """
        self.processor = AdaptivePDFProcessor(
            default_dpi=default_dpi,
            max_dpi=max_dpi,
            tile_overlap_percent=tile_overlap,
            output_format=output_format,
        )
        self.images_per_batch = min(images_per_batch, self.MAX_IMAGES_PER_CALL)
        self.preload_base64 = preload_base64

    def prepare_for_extraction(
        self,
        file_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        mode: ExtractionMode = ExtractionMode.FULL_TAKEOFF,
        pages: Optional[List[int]] = None,
        custom_prompt: Optional[str] = None,
        drawing_context: Optional[Dict[str, Any]] = None,
    ) -> PreparationResult:
        """
        Prepare a PDF for measurement extraction.

        Args:
            file_path: Path to PDF
            output_dir: Output directory for images
            mode: Extraction mode
            pages: Specific pages (0-indexed), None for all
            custom_prompt: Override default extraction prompt
            drawing_context: Additional context (project name, etc.)

        Returns:
            PreparationResult with batched images ready for API calls
        """
        file_path = Path(file_path)

        # Process the PDF
        result = self.processor.process_for_vision(
            file_path, output_dir=output_dir, pages=pages
        )

        if not result.success:
            return PreparationResult(
                source_file=str(file_path),
                total_pages=0,
                total_images=0,
                batches=[],
                processing_result=result,
                recommendations={},
                success=False,
                error_message=result.error_message,
            )

        # Build image data objects
        images = self._build_image_data(result)

        # Create batches
        batches = self._create_batches(
            images=images,
            source_file=str(file_path),
            mode=mode,
            custom_prompt=custom_prompt,
            drawing_context=drawing_context,
            page_analyses=result.page_analyses,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(result, batches)

        return PreparationResult(
            source_file=str(file_path),
            total_pages=result.page_count,
            total_images=len(images),
            batches=batches,
            processing_result=result,
            recommendations=recommendations,
            success=True,
        )

    def _build_image_data(self, result: ProcessingResult) -> List[ImageData]:
        """Build ImageData objects from processing result."""
        images = []

        for file_path in result.output_files:
            path = Path(file_path)

            # Parse filename for metadata
            # Format: {stem}_p{page}_tile{n}_r{row}c{col}.{ext}
            name = path.stem

            page_num = 0
            tile_pos = None

            if "_p" in name:
                try:
                    page_part = name.split("_p")[1].split("_")[0]
                    page_num = int(page_part) - 1
                except (IndexError, ValueError):
                    pass

            if "_tile" in name and "_r" in name:
                try:
                    tile_part = name.split("_r")[1]
                    tile_pos = f"r{tile_part}"
                except IndexError:
                    pass

            # Get image dimensions
            width, height = self._get_image_dimensions(file_path)

            # Estimate tokens
            megapixels = (width * height) / 1_000_000
            estimated_tokens = int(megapixels * 850)

            img_data = ImageData(
                file_path=file_path,
                width=width,
                height=height,
                source_page=page_num,
                tile_position=tile_pos,
                estimated_tokens=estimated_tokens,
            )

            if self.preload_base64:
                img_data.load_base64()

            images.append(img_data)

        return images

    def _get_image_dimensions(self, file_path: str) -> tuple:
        """Get image dimensions."""
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                return img.width, img.height
        except ImportError:
            # Fallback estimate
            return 2000, 2000

    def _create_batches(
        self,
        images: List[ImageData],
        source_file: str,
        mode: ExtractionMode,
        custom_prompt: Optional[str],
        drawing_context: Optional[Dict[str, Any]],
        page_analyses: List[PageAnalysis],
    ) -> List[ImageBatch]:
        """Create optimized batches for API calls."""
        batches = []

        # Group images by page
        images_by_page: Dict[int, List[ImageData]] = {}
        for img in images:
            if img.source_page not in images_by_page:
                images_by_page[img.source_page] = []
            images_by_page[img.source_page].append(img)

        # Base prompt
        base_prompt = custom_prompt or self.PROMPTS[mode]

        # Add drawing context if provided
        if drawing_context:
            context_str = "\n".join(f"- {k}: {v}" for k, v in drawing_context.items())
            base_prompt = f"**Drawing Context:**\n{context_str}\n\n{base_prompt}"

        # Create batches
        current_batch_images = []
        current_batch_pages = set()
        current_tokens = 0
        batch_index = 0

        for page_num in sorted(images_by_page.keys()):
            page_images = images_by_page[page_num]

            for img in page_images:
                # Check if adding this image would exceed limits
                would_exceed_images = len(current_batch_images) >= self.images_per_batch
                would_exceed_tokens = (
                    current_tokens + img.estimated_tokens
                ) > self.MAX_TOKENS_PER_CALL

                if current_batch_images and (
                    would_exceed_images or would_exceed_tokens
                ):
                    # Finalize current batch
                    batch = self._finalize_batch(
                        images=current_batch_images,
                        pages=list(current_batch_pages),
                        source_file=source_file,
                        batch_index=batch_index,
                        base_prompt=base_prompt,
                        mode=mode,
                        is_continuation=batch_index > 0,
                    )
                    batches.append(batch)
                    batch_index += 1

                    # Start new batch
                    current_batch_images = []
                    current_batch_pages = set()
                    current_tokens = 0

                current_batch_images.append(img)
                current_batch_pages.add(page_num)
                current_tokens += img.estimated_tokens

        # Finalize last batch
        if current_batch_images:
            batch = self._finalize_batch(
                images=current_batch_images,
                pages=list(current_batch_pages),
                source_file=source_file,
                batch_index=batch_index,
                base_prompt=base_prompt,
                mode=mode,
                is_continuation=batch_index > 0,
            )
            batches.append(batch)

        # Update total_batches count
        total = len(batches)
        for batch in batches:
            batch.total_batches = total

        return batches

    def _finalize_batch(
        self,
        images: List[ImageData],
        pages: List[int],
        source_file: str,
        batch_index: int,
        base_prompt: str,
        mode: ExtractionMode,
        is_continuation: bool,
    ) -> ImageBatch:
        """Create a finalized batch with appropriate prompts."""

        # Build context prompt
        prompt_parts = []

        if is_continuation:
            prompt_parts.append(self.CONTINUATION_CONTEXT)

        # Add tile context if applicable
        tiled_images = [img for img in images if img.tile_position]
        if tiled_images:
            # Determine grid size from tile positions
            rows = set()
            cols = set()
            for img in tiled_images:
                if img.tile_position:
                    parts = img.tile_position.replace("r", "").split("c")
                    if len(parts) == 2:
                        rows.add(parts[0])
                        cols.add(parts[1])

            grid = f"{len(rows)}×{len(cols)}"

            for img in tiled_images:
                prompt_parts.append(
                    self.TILE_CONTEXT.format(
                        tile_pos=img.tile_position,
                        grid=grid,
                        page=img.source_page + 1,
                        overlap=int(self.processor.tile_overlap_percent),
                    )
                )

        # Add main extraction prompt
        prompt_parts.append(base_prompt)

        # Add batch position info
        prompt_parts.append(
            f"\n[Batch {batch_index + 1}, Pages: {', '.join(str(p + 1) for p in sorted(pages))}]"
        )

        context_prompt = "\n\n".join(prompt_parts)

        # Extraction guidance based on mode
        guidance = self._get_extraction_guidance(mode, images)

        return ImageBatch(
            images=images,
            source_file=source_file,
            page_numbers=pages,
            batch_index=batch_index,
            total_batches=0,  # Updated later
            context_prompt=context_prompt,
            extraction_guidance=guidance,
            estimated_tokens=sum(img.estimated_tokens for img in images),
            is_continuation=is_continuation,
        )

    def _get_extraction_guidance(
        self, mode: ExtractionMode, images: List[ImageData]
    ) -> str:
        """Generate extraction guidance based on mode and images."""

        if mode == ExtractionMode.FULL_TAKEOFF:
            return """Focus on extracting:
- Wall lengths and thicknesses
- Opening dimensions (doors, windows)
- Room areas and perimeters
- Structural element sizes
- Level annotations
- Grid references for spatial context"""

        elif mode == ExtractionMode.DIMENSIONS_ONLY:
            return """Extract numerical dimensions only:
- State value, unit, and location
- Note scale for any scaled measurements
- Flag any unclear or conflicting dimensions"""

        elif mode == ExtractionMode.VERIFICATION:
            return """For each element, verify:
- Dimension consistency across views
- Annotation accuracy
- Cross-reference alignment"""

        else:  # SCHEDULE_EXTRACT
            return """Extract schedule data maintaining:
- Column headers
- Row relationships
- Cell values with units
- Any footnotes or references"""

    def _generate_recommendations(
        self, result: ProcessingResult, batches: List[ImageBatch]
    ) -> Dict[str, Any]:
        """Generate recommendations for optimal extraction."""

        # Analyze complexity
        high_density_pages = sum(
            1
            for a in result.page_analyses
            if a.density_level in [DensityLevel.HIGH, DensityLevel.VERY_HIGH]
        )

        total_tokens = sum(b.estimated_tokens for b in batches)

        recommendations = {
            "total_api_calls": len(batches),
            "estimated_total_tokens": total_tokens,
            "high_density_pages": high_density_pages,
            "processing_strategy": result.strategy_used.value,
            "suggestions": [],
        }

        # Add suggestions
        if high_density_pages > 0:
            recommendations["suggestions"].append(
                f"{high_density_pages} high-density pages detected - "
                "consider processing complex areas separately with process_region()"
            )

        if len(batches) > 5:
            recommendations["suggestions"].append(
                "Multiple batches required - consider implementing "
                "result aggregation across batches"
            )

        if total_tokens > 100_000:
            recommendations["suggestions"].append(
                f"High token count ({total_tokens:,}) - consider processing "
                "pages in groups rather than all at once"
            )

        # Add scale information
        detected_scales = set()
        for a in result.page_analyses:
            if a.detected_scale:
                detected_scales.add(a.detected_scale)

        if detected_scales:
            recommendations["detected_scales"] = list(detected_scales)

        return recommendations

    def prepare_region(
        self,
        file_path: Union[str, Path],
        page_number: int,
        region: tuple,
        output_dir: Optional[Union[str, Path]] = None,
        zoom_factor: float = 1.5,
        mode: ExtractionMode = ExtractionMode.DIMENSIONS_ONLY,
        region_description: Optional[str] = None,
    ) -> PreparationResult:
        """
        Prepare a specific region for detailed extraction.

        Use this for complex areas like:
        - Dense dimension clusters
        - Schedules and tables
        - Complex junctions
        - Title blocks

        Args:
            file_path: PDF path
            page_number: Page number (0-indexed)
            region: Crop rectangle (x0, y0, x1, y1) in points
            output_dir: Output directory
            zoom_factor: Zoom multiplier for detail
            mode: Extraction mode
            region_description: Description for context

        Returns:
            PreparationResult with single-image batch
        """
        result = self.processor.process_region(
            file_path,
            page_number=page_number,
            region=region,
            output_dir=output_dir,
            zoom_factor=zoom_factor,
        )

        if not result.success:
            return PreparationResult(
                source_file=str(file_path),
                total_pages=0,
                total_images=0,
                batches=[],
                processing_result=result,
                recommendations={},
                success=False,
                error_message=result.error_message,
            )

        # Build image data
        images = self._build_image_data(result)

        if region_description:
            for img in images:
                img.region_description = region_description

        # Create single batch
        prompt = self.PROMPTS[mode]
        if region_description:
            prompt = f"**Region Focus:** {region_description}\n\n{prompt}"

        batch = ImageBatch(
            images=images,
            source_file=str(file_path),
            page_numbers=[page_number],
            batch_index=0,
            total_batches=1,
            context_prompt=prompt,
            extraction_guidance=self._get_extraction_guidance(mode, images),
            estimated_tokens=sum(img.estimated_tokens for img in images),
        )

        return PreparationResult(
            source_file=str(file_path),
            total_pages=1,
            total_images=len(images),
            batches=[batch],
            processing_result=result,
            recommendations={
                "region": region,
                "zoom_factor": zoom_factor,
                "effective_dpi": result.metadata.get("effective_dpi", "unknown"),
            },
            success=True,
        )


# Convenience functions for common use cases


def prepare_drawing(
    file_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    high_density: bool = False,
) -> PreparationResult:
    """
    Quick preparation of a drawing for extraction.

    Args:
        file_path: PDF to process
        output_dir: Output directory
        high_density: Set True for known complex drawings

    Returns:
        PreparationResult ready for API calls
    """
    optimizer = OpusVisionOptimizer(default_dpi=200 if high_density else 150)
    return optimizer.prepare_for_extraction(file_path, output_dir)


def prepare_schedule(
    file_path: Union[str, Path],
    page_number: int,
    region: tuple,
    output_dir: Optional[Union[str, Path]] = None,
) -> PreparationResult:
    """
    Prepare a schedule/table region for extraction.

    Args:
        file_path: PDF path
        page_number: Page containing schedule (0-indexed)
        region: Crop region (x0, y0, x1, y1) in points
        output_dir: Output directory

    Returns:
        PreparationResult optimized for table extraction
    """
    optimizer = OpusVisionOptimizer(default_dpi=200)
    return optimizer.prepare_region(
        file_path,
        page_number=page_number,
        region=region,
        output_dir=output_dir,
        zoom_factor=1.8,
        mode=ExtractionMode.SCHEDULE_EXTRACT,
        region_description="Schedule/Table extraction",
    )


# Example integration with PydanticAI
PYDANTIC_AI_EXAMPLE = '''
"""Example integration with PydanticAI agent."""

from pydantic import BaseModel
from pydantic_ai import Agent
from opus_vision_optimizer import OpusVisionOptimizer, ExtractionMode

class DrawingExtraction(BaseModel):
    """Structured extraction result."""
    drawing_ref: str
    scale: str | None
    walls: list[dict]
    openings: list[dict]
    rooms: list[dict]
    ambiguities: list[str]

# Initialize
optimizer = OpusVisionOptimizer()
agent = Agent(
    'anthropic:claude-sonnet-4-20250514',
    result_type=DrawingExtraction,
    system_prompt="You are an expert quantity surveyor..."
)

async def extract_drawing(pdf_path: str) -> list[DrawingExtraction]:
    """Extract measurements from architectural drawing."""
    
    # Prepare images
    prep = optimizer.prepare_for_extraction(
        pdf_path,
        mode=ExtractionMode.FULL_TAKEOFF,
        drawing_context={
            "project": "Example Project",
            "discipline": "Architectural"
        }
    )
    
    if not prep.success:
        raise ValueError(f"Preparation failed: {prep.error_message}")
    
    results = []
    
    for batch in prep.batches:
        # Build message content
        content = batch.get_api_content()
        
        # Run agent (simplified - actual implementation varies)
        result = await agent.run(
            user_prompt=batch.context_prompt,
            # Pass images via appropriate method for your setup
        )
        
        results.append(result.data)
    
    return results
'''


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python opus_vision_optimizer.py <pdf_file> [output_dir]")
        print("\nExample:")
        print("  python opus_vision_optimizer.py drawing.pdf ./output")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\nPreparing: {pdf_path}")

    optimizer = OpusVisionOptimizer()
    result = optimizer.prepare_for_extraction(
        pdf_path, output_dir=output_dir, mode=ExtractionMode.FULL_TAKEOFF
    )

    print(f"\n{result.processing_result}")

    if result.success:
        print(f"\nCreated {len(result.batches)} batch(es):")
        for batch in result.batches:
            print(
                f"  Batch {batch.batch_index + 1}: "
                f"{batch.image_count} images, "
                f"~{batch.estimated_tokens:,} tokens, "
                f"pages {batch.page_numbers}"
            )

        print(f"\nRecommendations:")
        for key, value in result.recommendations.items():
            if key != "suggestions":
                print(f"  {key}: {value}")

        if result.recommendations.get("suggestions"):
            print(f"\n  Suggestions:")
            for s in result.recommendations["suggestions"]:
                print(f"    • {s}")
    else:
        print(f"\nFailed: {result.error_message}")
