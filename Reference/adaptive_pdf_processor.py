"""
Adaptive PDF Processor for Architectural Drawing Analysis
==========================================================

Optimizes high-density architectural PDFs for Claude Opus vision extraction.
Handles variable scale and density by analyzing content and adapting output strategy.

Key Features:
- Density analysis to detect information-rich regions
- Adaptive DPI based on drawing scale and content density
- Intelligent tiling with configurable overlap for dense drawings
- Scale detection from title blocks and annotations
- Output optimized for vision API token efficiency

Usage:
    from adaptive_pdf_processor import AdaptivePDFProcessor

    processor = AdaptivePDFProcessor()
    result = processor.process_for_vision("drawing.pdf")

    for image_path in result.output_files:
        # Send to Claude Opus vision API
        pass

Dependencies:
    pip install PyMuPDF numpy pillow

Author: DELLQS-AI
Version: 1.0.0
"""

import os
import re
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import math


class DensityLevel(Enum):
    """Classification of drawing density."""

    LOW = "low"  # Simple drawings, large text
    MEDIUM = "medium"  # Standard architectural plans
    HIGH = "high"  # Dense details, small annotations
    VERY_HIGH = "very_high"  # Complex M&E, dense schedules


class ProcessingStrategy(Enum):
    """Strategy for processing the PDF."""

    DIRECT = "direct"  # Single image, standard DPI
    ENHANCED = "enhanced"  # Single image, higher DPI
    TILED = "tiled"  # Split into overlapping tiles
    ADAPTIVE_TILED = "adaptive"  # Variable DPI tiles based on region density


@dataclass
class RegionInfo:
    """Information about a specific region of a page."""

    x0: float
    y0: float
    x1: float
    y1: float
    density_score: float
    text_count: int
    line_count: int
    recommended_dpi: int

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def rect(self) -> tuple:
        return (self.x0, self.y0, self.x1, self.y1)


@dataclass
class PageAnalysis:
    """Analysis results for a single page."""

    page_number: int
    width_pts: float
    height_pts: float
    total_text_blocks: int
    total_drawings: int
    density_level: DensityLevel
    detected_scale: Optional[str]
    recommended_strategy: ProcessingStrategy
    recommended_base_dpi: int
    regions: List[RegionInfo] = field(default_factory=list)

    @property
    def aspect_ratio(self) -> float:
        return self.width_pts / self.height_pts if self.height_pts > 0 else 1.0


@dataclass
class ProcessingResult:
    """Result of processing a PDF for vision extraction."""

    original_path: str
    page_count: int
    output_files: List[str]
    page_analyses: List[PageAnalysis]
    strategy_used: ProcessingStrategy
    total_tiles: int
    estimated_tokens: int  # Rough estimate for vision API
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        if self.success:
            return (
                f"Processed '{Path(self.original_path).name}': "
                f"{self.page_count} pages → {len(self.output_files)} images "
                f"(~{self.estimated_tokens:,} tokens)"
            )
        return f"Failed: {self.error_message}"


class AdaptivePDFProcessor:
    """
    Processes architectural PDFs with adaptive strategies for optimal
    vision model extraction of measurements and annotations.
    """

    # DPI recommendations based on drawing scale
    SCALE_DPI_MAP = {
        "1:1": 72,
        "1:2": 100,
        "1:5": 120,
        "1:10": 150,
        "1:20": 150,
        "1:50": 200,
        "1:100": 250,
        "1:200": 300,
        "1:500": 350,
    }

    # Base DPI for density levels (when scale unknown)
    DENSITY_DPI_MAP = {
        DensityLevel.LOW: 120,
        DensityLevel.MEDIUM: 150,
        DensityLevel.HIGH: 200,
        DensityLevel.VERY_HIGH: 250,
    }

    # Approximate tokens per megapixel for vision API
    TOKENS_PER_MEGAPIXEL = 850

    # Maximum recommended image dimension for API
    MAX_DIMENSION = 4096

    # Target file size in KB for optimal API performance
    TARGET_FILE_SIZE_KB = 1500

    def __init__(
        self,
        default_dpi: int = 150,
        max_dpi: int = 350,
        min_dpi: int = 100,
        tile_overlap_percent: float = 10.0,
        max_tiles_per_page: int = 9,
        output_format: str = "png",
        jpeg_quality: int = 90,
    ):
        """
        Initialize the processor with configuration.

        Args:
            default_dpi: Default rendering DPI when analysis inconclusive
            max_dpi: Maximum DPI cap to prevent huge files
            min_dpi: Minimum DPI floor to ensure readability
            tile_overlap_percent: Overlap between tiles (0-25%)
            max_tiles_per_page: Maximum tiles before raising DPI instead
            output_format: 'png' for quality, 'jpg' for smaller files
            jpeg_quality: Quality for JPEG output (1-100)
        """
        self.default_dpi = default_dpi
        self.max_dpi = max_dpi
        self.min_dpi = min_dpi
        self.tile_overlap_percent = min(25.0, max(0.0, tile_overlap_percent))
        self.max_tiles_per_page = max_tiles_per_page
        self.output_format = output_format.lower()
        self.jpeg_quality = jpeg_quality

        self._fitz = None

    @property
    def fitz(self):
        """Lazy load PyMuPDF."""
        if self._fitz is None:
            try:
                import fitz

                self._fitz = fitz
            except ImportError:
                raise ImportError("PyMuPDF required: pip install PyMuPDF")
        return self._fitz

    def analyze_page(self, page) -> PageAnalysis:
        """
        Analyze a single page to determine optimal processing strategy.

        Args:
            page: PyMuPDF page object

        Returns:
            PageAnalysis with recommendations
        """
        rect = page.rect
        width, height = rect.width, rect.height

        # Extract text blocks
        text_dict = page.get_text("dict", flags=self.fitz.TEXT_PRESERVE_WHITESPACE)
        text_blocks = text_dict.get("blocks", [])

        # Count text and drawing elements
        text_block_count = sum(1 for b in text_blocks if b.get("type") == 0)
        drawing_count = len(page.get_drawings())

        # Get all text for scale detection
        full_text = page.get_text()
        detected_scale = self._detect_scale(full_text)

        # Calculate density metrics
        page_area = width * height
        text_density = text_block_count / (page_area / 10000) if page_area > 0 else 0
        drawing_density = drawing_count / (page_area / 10000) if page_area > 0 else 0

        # Analyze text sizes (smaller text = higher density concern)
        min_text_size = float("inf")
        for block in text_blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        size = span.get("size", 12)
                        if size > 0:
                            min_text_size = min(min_text_size, size)

        if min_text_size == float("inf"):
            min_text_size = 12

        # Determine density level
        density_level = self._classify_density(
            text_density, drawing_density, min_text_size, text_block_count
        )

        # Determine recommended DPI
        if detected_scale:
            base_dpi = self.SCALE_DPI_MAP.get(detected_scale, self.default_dpi)
        else:
            base_dpi = self.DENSITY_DPI_MAP[density_level]

        # Adjust for very small text
        if min_text_size < 6:
            base_dpi = min(self.max_dpi, int(base_dpi * 1.5))
        elif min_text_size < 8:
            base_dpi = min(self.max_dpi, int(base_dpi * 1.25))

        # Determine strategy
        strategy = self._determine_strategy(width, height, base_dpi, density_level)

        # Analyze regions if tiling needed
        regions = []
        if strategy in [ProcessingStrategy.TILED, ProcessingStrategy.ADAPTIVE_TILED]:
            regions = self._analyze_regions(page, density_level)

        return PageAnalysis(
            page_number=page.number,
            width_pts=width,
            height_pts=height,
            total_text_blocks=text_block_count,
            total_drawings=drawing_count,
            density_level=density_level,
            detected_scale=detected_scale,
            recommended_strategy=strategy,
            recommended_base_dpi=base_dpi,
            regions=regions,
        )

    def _detect_scale(self, text: str) -> Optional[str]:
        """Extract drawing scale from text content."""
        # Common scale patterns
        patterns = [
            r"SCALE[:\s]+1[:\s]*[:/-]\s*(\d+)",
            r"1\s*:\s*(\d+)",
            r"SCALE\s+1/(\d+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return most common scale found
                scale_val = max(set(matches), key=matches.count)
                return f"1:{scale_val}"

        return None

    def _classify_density(
        self,
        text_density: float,
        drawing_density: float,
        min_text_size: float,
        text_count: int,
    ) -> DensityLevel:
        """Classify the overall density of the page."""
        # Combined score
        score = (text_density * 2) + drawing_density

        # Adjust for text size (smaller text = effectively denser)
        if min_text_size < 6:
            score *= 1.5
        elif min_text_size < 8:
            score *= 1.25

        # Adjust for absolute text count
        if text_count > 500:
            score *= 1.3
        elif text_count > 200:
            score *= 1.15

        if score < 5:
            return DensityLevel.LOW
        elif score < 15:
            return DensityLevel.MEDIUM
        elif score < 30:
            return DensityLevel.HIGH
        else:
            return DensityLevel.VERY_HIGH

    def _determine_strategy(
        self, width: float, height: float, base_dpi: int, density: DensityLevel
    ) -> ProcessingStrategy:
        """Determine the best processing strategy."""
        # Calculate output dimensions at base DPI
        scale = base_dpi / 72
        output_width = width * scale
        output_height = height * scale

        # Check if single image is feasible
        if output_width <= self.MAX_DIMENSION and output_height <= self.MAX_DIMENSION:
            if density in [DensityLevel.LOW, DensityLevel.MEDIUM]:
                return ProcessingStrategy.DIRECT
            else:
                return ProcessingStrategy.ENHANCED

        # Need tiling
        if density == DensityLevel.VERY_HIGH:
            return ProcessingStrategy.ADAPTIVE_TILED
        else:
            return ProcessingStrategy.TILED

    def _analyze_regions(self, page, overall_density: DensityLevel) -> List[RegionInfo]:
        """Analyze page regions for adaptive tiling."""
        rect = page.rect
        width, height = rect.width, rect.height

        # Create a grid for analysis (e.g., 4x4)
        grid_size = 4
        cell_width = width / grid_size
        cell_height = height / grid_size

        regions = []

        for row in range(grid_size):
            for col in range(grid_size):
                x0 = col * cell_width
                y0 = row * cell_height
                x1 = x0 + cell_width
                y1 = y0 + cell_height

                # Get content in this region
                clip_rect = self.fitz.Rect(x0, y0, x1, y1)

                # Count text in region
                text_in_region = page.get_text("text", clip=clip_rect)
                text_count = len(text_in_region.split())

                # Count drawings in region (approximate)
                drawings = page.get_drawings()
                line_count = sum(
                    1
                    for d in drawings
                    if clip_rect.intersects(self.fitz.Rect(d["rect"]))
                )

                # Calculate density score for region
                area = cell_width * cell_height
                density_score = (text_count + line_count * 0.5) / (area / 1000)

                # Determine recommended DPI for this region
                if density_score < 2:
                    rec_dpi = self.min_dpi
                elif density_score < 5:
                    rec_dpi = self.default_dpi
                elif density_score < 10:
                    rec_dpi = int(self.default_dpi * 1.3)
                else:
                    rec_dpi = min(self.max_dpi, int(self.default_dpi * 1.6))

                regions.append(
                    RegionInfo(
                        x0=x0,
                        y0=y0,
                        x1=x1,
                        y1=y1,
                        density_score=density_score,
                        text_count=text_count,
                        line_count=line_count,
                        recommended_dpi=rec_dpi,
                    )
                )

        return regions

    def _calculate_tile_grid(
        self, width: float, height: float, target_dpi: int
    ) -> Tuple[int, int]:
        """Calculate optimal tile grid dimensions."""
        scale = target_dpi / 72
        output_width = width * scale
        output_height = height * scale

        # Calculate tiles needed to stay under max dimension
        cols = max(1, math.ceil(output_width / self.MAX_DIMENSION))
        rows = max(1, math.ceil(output_height / self.MAX_DIMENSION))

        # Cap at max tiles
        total = cols * rows
        if total > self.max_tiles_per_page:
            # Reduce grid and increase DPI instead
            ratio = math.sqrt(self.max_tiles_per_page / total)
            cols = max(1, int(cols * ratio))
            rows = max(1, int(rows * ratio))

        return cols, rows

    def render_page(
        self, page, analysis: PageAnalysis, output_dir: Path, page_prefix: str
    ) -> List[str]:
        """
        Render a page according to analysis recommendations.

        Returns list of output file paths.
        """
        output_files = []

        if analysis.recommended_strategy == ProcessingStrategy.DIRECT:
            # Single image at standard DPI
            output_files.extend(
                self._render_single(
                    page, analysis.recommended_base_dpi, output_dir, page_prefix
                )
            )

        elif analysis.recommended_strategy == ProcessingStrategy.ENHANCED:
            # Single image at higher DPI
            enhanced_dpi = min(self.max_dpi, int(analysis.recommended_base_dpi * 1.3))
            output_files.extend(
                self._render_single(page, enhanced_dpi, output_dir, page_prefix)
            )

        elif analysis.recommended_strategy == ProcessingStrategy.TILED:
            # Uniform tiling
            output_files.extend(
                self._render_tiled(
                    page,
                    analysis,
                    output_dir,
                    page_prefix,
                    uniform_dpi=analysis.recommended_base_dpi,
                )
            )

        else:  # ADAPTIVE_TILED
            # Adaptive tiling with variable DPI per region
            output_files.extend(
                self._render_tiled(
                    page, analysis, output_dir, page_prefix, uniform_dpi=None
                )
            )

        return output_files

    def _render_single(
        self, page, dpi: int, output_dir: Path, prefix: str
    ) -> List[str]:
        """Render page as single image."""
        mat = self.fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        ext = "jpg" if self.output_format == "jpg" else "png"
        output_path = output_dir / f"{prefix}.{ext}"

        if ext == "jpg":
            pix.save(str(output_path), jpg_quality=self.jpeg_quality)
        else:
            pix.save(str(output_path))

        return [str(output_path)]

    def _render_tiled(
        self,
        page,
        analysis: PageAnalysis,
        output_dir: Path,
        prefix: str,
        uniform_dpi: Optional[int] = None,
    ) -> List[str]:
        """Render page as overlapping tiles."""
        output_files = []

        rect = page.rect
        width, height = rect.width, rect.height

        # Determine grid
        target_dpi = uniform_dpi or analysis.recommended_base_dpi
        cols, rows = self._calculate_tile_grid(width, height, target_dpi)

        # Calculate tile dimensions with overlap
        overlap_factor = self.tile_overlap_percent / 100

        base_tile_width = width / cols
        base_tile_height = height / rows

        overlap_x = base_tile_width * overlap_factor
        overlap_y = base_tile_height * overlap_factor

        tile_num = 0
        for row in range(rows):
            for col in range(cols):
                tile_num += 1

                # Calculate clip rectangle with overlap
                x0 = max(0, col * base_tile_width - overlap_x)
                y0 = max(0, row * base_tile_height - overlap_y)
                x1 = min(width, (col + 1) * base_tile_width + overlap_x)
                y1 = min(height, (row + 1) * base_tile_height + overlap_y)

                clip = self.fitz.Rect(x0, y0, x1, y1)

                # Determine DPI for this tile
                if uniform_dpi:
                    tile_dpi = uniform_dpi
                else:
                    # Find matching region analysis
                    tile_dpi = self._get_region_dpi(analysis.regions, x0, y0, x1, y1)

                # Render tile
                mat = self.fitz.Matrix(tile_dpi / 72, tile_dpi / 72)
                pix = page.get_pixmap(matrix=mat, clip=clip)

                ext = "jpg" if self.output_format == "jpg" else "png"
                tile_path = (
                    output_dir
                    / f"{prefix}_tile{tile_num:02d}_r{row + 1}c{col + 1}.{ext}"
                )

                if ext == "jpg":
                    pix.save(str(tile_path), jpg_quality=self.jpeg_quality)
                else:
                    pix.save(str(tile_path))

                output_files.append(str(tile_path))

        return output_files

    def _get_region_dpi(
        self, regions: List[RegionInfo], x0: float, y0: float, x1: float, y1: float
    ) -> int:
        """Get recommended DPI for a tile based on overlapping regions."""
        if not regions:
            return self.default_dpi

        tile_rect = self.fitz.Rect(x0, y0, x1, y1)

        # Find regions that overlap with this tile
        overlapping_dpis = []
        for region in regions:
            region_rect = self.fitz.Rect(region.x0, region.y0, region.x1, region.y1)
            if tile_rect.intersects(region_rect):
                # Weight by overlap area
                intersection = tile_rect & region_rect
                if intersection.is_empty:
                    continue
                weight = intersection.width * intersection.height
                overlapping_dpis.append((region.recommended_dpi, weight))

        if not overlapping_dpis:
            return self.default_dpi

        # Weighted average, biased toward higher DPI
        total_weight = sum(w for _, w in overlapping_dpis)
        if total_weight == 0:
            return self.default_dpi

        weighted_dpi = sum(dpi * w for dpi, w in overlapping_dpis) / total_weight

        # Bias toward max for safety
        max_dpi = max(dpi for dpi, _ in overlapping_dpis)
        return int(weighted_dpi * 0.7 + max_dpi * 0.3)

    def _estimate_tokens(self, output_files: List[str]) -> int:
        """Estimate vision API tokens for output images."""
        total_pixels = 0

        for filepath in output_files:
            try:
                # Quick size check without loading full image
                from PIL import Image

                with Image.open(filepath) as img:
                    total_pixels += img.width * img.height
            except ImportError:
                # Fallback: estimate from file size
                size_kb = Path(filepath).stat().st_size / 1024
                # Rough estimate: 1KB ≈ 1000 pixels for PNG
                total_pixels += int(size_kb * 1000)
            except Exception:
                total_pixels += 1_000_000  # Default 1MP per image

        megapixels = total_pixels / 1_000_000
        return int(megapixels * self.TOKENS_PER_MEGAPIXEL)

    def process_for_vision(
        self,
        file_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        pages: Optional[List[int]] = None,
        force_strategy: Optional[ProcessingStrategy] = None,
        force_dpi: Optional[int] = None,
    ) -> ProcessingResult:
        """
        Process a PDF for optimal vision model extraction.

        Args:
            file_path: Path to the PDF file
            output_dir: Output directory (default: temp directory)
            pages: Specific pages to process (0-indexed), None for all
            force_strategy: Override automatic strategy selection
            force_dpi: Override automatic DPI selection

        Returns:
            ProcessingResult with output files and metadata
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return ProcessingResult(
                original_path=str(file_path),
                page_count=0,
                output_files=[],
                page_analyses=[],
                strategy_used=ProcessingStrategy.DIRECT,
                total_tiles=0,
                estimated_tokens=0,
                success=False,
                error_message=f"File not found: {file_path}",
            )

        # Setup output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = Path(tempfile.mkdtemp(prefix="pdf_vision_"))
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            doc = self.fitz.open(str(file_path))
            total_pages = len(doc)

            # Determine which pages to process
            if pages is None:
                pages_to_process = list(range(total_pages))
            else:
                pages_to_process = [p for p in pages if 0 <= p < total_pages]

            all_output_files = []
            all_analyses = []
            strategies_used = set()

            for page_num in pages_to_process:
                page = doc[page_num]

                # Analyze page
                analysis = self.analyze_page(page)

                # Apply overrides
                if force_strategy:
                    analysis.recommended_strategy = force_strategy
                if force_dpi:
                    analysis.recommended_base_dpi = force_dpi

                all_analyses.append(analysis)
                strategies_used.add(analysis.recommended_strategy)

                # Render page
                prefix = f"{file_path.stem}_p{page_num + 1:02d}"
                page_files = self.render_page(page, analysis, output_path, prefix)
                all_output_files.extend(page_files)

            doc.close()

            # Determine overall strategy used
            if len(strategies_used) == 1:
                strategy = strategies_used.pop()
            elif ProcessingStrategy.ADAPTIVE_TILED in strategies_used:
                strategy = ProcessingStrategy.ADAPTIVE_TILED
            elif ProcessingStrategy.TILED in strategies_used:
                strategy = ProcessingStrategy.TILED
            else:
                strategy = ProcessingStrategy.ENHANCED

            # Calculate totals
            total_tiles = len(all_output_files)
            estimated_tokens = self._estimate_tokens(all_output_files)

            return ProcessingResult(
                original_path=str(file_path),
                page_count=len(pages_to_process),
                output_files=all_output_files,
                page_analyses=all_analyses,
                strategy_used=strategy,
                total_tiles=total_tiles,
                estimated_tokens=estimated_tokens,
                success=True,
                metadata={
                    "output_directory": str(output_path),
                    "output_format": self.output_format,
                    "tile_overlap_percent": self.tile_overlap_percent,
                },
            )

        except Exception as e:
            return ProcessingResult(
                original_path=str(file_path),
                page_count=0,
                output_files=[],
                page_analyses=[],
                strategy_used=ProcessingStrategy.DIRECT,
                total_tiles=0,
                estimated_tokens=0,
                success=False,
                error_message=str(e),
            )

    def process_region(
        self,
        file_path: Union[str, Path],
        page_number: int,
        region: Tuple[float, float, float, float],
        output_dir: Optional[Union[str, Path]] = None,
        dpi: Optional[int] = None,
        zoom_factor: float = 1.0,
    ) -> ProcessingResult:
        """
        Process a specific region of a page at high resolution.

        Useful for zooming into specific details like schedules,
        dimension clusters, or complex junctions.

        Args:
            file_path: Path to the PDF
            page_number: Page number (0-indexed)
            region: Crop rectangle (x0, y0, x1, y1) in points
            output_dir: Output directory
            dpi: Rendering DPI (default: auto-detected)
            zoom_factor: Additional zoom multiplier (1.0 = no extra zoom)

        Returns:
            ProcessingResult with single zoomed image
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return ProcessingResult(
                original_path=str(file_path),
                page_count=0,
                output_files=[],
                page_analyses=[],
                strategy_used=ProcessingStrategy.ENHANCED,
                total_tiles=0,
                estimated_tokens=0,
                success=False,
                error_message=f"File not found: {file_path}",
            )

        # Setup output
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = Path(tempfile.mkdtemp(prefix="pdf_region_"))
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            doc = self.fitz.open(str(file_path))

            if page_number >= len(doc):
                doc.close()
                return ProcessingResult(
                    original_path=str(file_path),
                    page_count=0,
                    output_files=[],
                    page_analyses=[],
                    strategy_used=ProcessingStrategy.ENHANCED,
                    total_tiles=0,
                    estimated_tokens=0,
                    success=False,
                    error_message=f"Page {page_number} does not exist",
                )

            page = doc[page_number]

            # Create clip rectangle
            x0, y0, x1, y1 = region
            clip = self.fitz.Rect(x0, y0, x1, y1)

            # Determine DPI
            if dpi is None:
                # Analyze the region to determine appropriate DPI
                analysis = self.analyze_page(page)
                dpi = min(self.max_dpi, int(analysis.recommended_base_dpi * 1.3))

            # Apply zoom factor
            effective_dpi = min(self.max_dpi, int(dpi * zoom_factor))

            # Render
            mat = self.fitz.Matrix(effective_dpi / 72, effective_dpi / 72)
            pix = page.get_pixmap(matrix=mat, clip=clip)

            ext = "jpg" if self.output_format == "jpg" else "png"
            output_file = (
                output_path / f"{file_path.stem}_p{page_number + 1}_region.{ext}"
            )

            if ext == "jpg":
                pix.save(str(output_file), jpg_quality=self.jpeg_quality)
            else:
                pix.save(str(output_file))

            doc.close()

            return ProcessingResult(
                original_path=str(file_path),
                page_count=1,
                output_files=[str(output_file)],
                page_analyses=[],
                strategy_used=ProcessingStrategy.ENHANCED,
                total_tiles=1,
                estimated_tokens=self._estimate_tokens([str(output_file)]),
                success=True,
                metadata={
                    "region": region,
                    "effective_dpi": effective_dpi,
                    "zoom_factor": zoom_factor,
                },
            )

        except Exception as e:
            return ProcessingResult(
                original_path=str(file_path),
                page_count=0,
                output_files=[],
                page_analyses=[],
                strategy_used=ProcessingStrategy.ENHANCED,
                total_tiles=0,
                estimated_tokens=0,
                success=False,
                error_message=str(e),
            )


def quick_process(
    file_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    high_density: bool = False,
) -> ProcessingResult:
    """
    Convenience function for quick processing with sensible defaults.

    Args:
        file_path: PDF to process
        output_dir: Output directory (default: temp)
        high_density: Set True for known high-density drawings

    Returns:
        ProcessingResult
    """
    processor = AdaptivePDFProcessor(
        default_dpi=200 if high_density else 150, output_format="png"
    )
    return processor.process_for_vision(file_path, output_dir)


# CLI interface
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Process architectural PDFs for vision API extraction"
    )
    parser.add_argument("pdf_file", help="PDF file to process")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("-d", "--dpi", type=int, help="Force specific DPI")
    parser.add_argument(
        "--high-density", action="store_true", help="Optimize for high-density drawings"
    )
    parser.add_argument(
        "--format", choices=["png", "jpg"], default="png", help="Output format"
    )
    parser.add_argument(
        "--analyze-only", action="store_true", help="Only analyze, don't render"
    )

    args = parser.parse_args()

    processor = AdaptivePDFProcessor(
        default_dpi=200 if args.high_density else 150, output_format=args.format
    )

    print(f"\nAnalyzing: {args.pdf_file}")

    if args.analyze_only:
        # Just analyze
        import fitz

        doc = fitz.open(args.pdf_file)
        for i, page in enumerate(doc):
            analysis = processor.analyze_page(page)
            print(f"\nPage {i + 1}:")
            print(f"  Size: {analysis.width_pts:.0f} x {analysis.height_pts:.0f} pts")
            print(f"  Text blocks: {analysis.total_text_blocks}")
            print(f"  Drawing elements: {analysis.total_drawings}")
            print(f"  Density: {analysis.density_level.value}")
            print(f"  Detected scale: {analysis.detected_scale or 'Unknown'}")
            print(f"  Recommended strategy: {analysis.recommended_strategy.value}")
            print(f"  Recommended DPI: {analysis.recommended_base_dpi}")
        doc.close()
    else:
        # Full processing
        result = processor.process_for_vision(
            args.pdf_file, output_dir=args.output, force_dpi=args.dpi
        )

        print(f"\n{result}")

        if result.success:
            print(f"\nOutput files:")
            for f in result.output_files:
                size_kb = Path(f).stat().st_size / 1024
                print(f"  {Path(f).name} ({size_kb:.1f} KB)")

            print(f"\nPage analyses:")
            for a in result.page_analyses:
                print(
                    f"  Page {a.page_number + 1}: {a.density_level.value}, "
                    f"scale={a.detected_scale or '?'}, "
                    f"strategy={a.recommended_strategy.value}"
                )
