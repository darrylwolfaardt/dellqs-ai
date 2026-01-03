"""
Mixed-Content PDF Processing Pipeline
======================================

Handles PDFs with:
- Initial text/specification section (portrait, extractable text)
- Architectural drawing section (landscape, needs vision processing)

Designed for QS workflow integration.

Dependencies:
    pip install PyMuPDF pdfplumber --break-system-packages
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any
from enum import Enum
import json

# Add QS skill path if available
sys.path.insert(0, "/mnt/skills/user/qs-measurement")


class PageType(Enum):
    TEXT = "text"
    DRAWING = "drawing"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class Orientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE = "square"


@dataclass
class PageInfo:
    """Information about a single PDF page."""

    page_num: int  # 0-indexed
    width: float
    height: float
    orientation: Orientation
    page_type: PageType
    text_density: float  # chars per sq inch
    has_images: bool
    rotation: int  # degrees

    @property
    def is_drawing(self) -> bool:
        return self.page_type == PageType.DRAWING or (
            self.orientation == Orientation.LANDSCAPE and self.text_density < 50
        )


@dataclass
class DocumentSegment:
    """A segment of the document (text section or drawings section)."""

    segment_type: str  # "text" or "drawings"
    start_page: int
    end_page: int
    page_count: int
    pages: List[PageInfo] = field(default_factory=list)
    extracted_content: Optional[Any] = None
    output_files: List[str] = field(default_factory=list)


@dataclass
class DocumentAnalysis:
    """Complete analysis of a mixed-content PDF."""

    file_path: str
    total_pages: int
    file_size_kb: float
    segments: List[DocumentSegment] = field(default_factory=list)
    transition_page: Optional[int] = None  # Where text ends and drawings begin
    pages: List[PageInfo] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Document: {Path(self.file_path).name}",
            f"Total pages: {self.total_pages} ({self.file_size_kb:.1f} KB)",
            f"Transition at page: {self.transition_page}",
            "",
            "Segments:",
        ]
        for seg in self.segments:
            lines.append(
                f"  - {seg.segment_type.upper()}: pages {seg.start_page + 1}-{seg.end_page + 1} ({seg.page_count} pages)"
            )
        return "\n".join(lines)


def _ensure_fitz():
    """Import PyMuPDF."""
    try:
        import fitz

        return fitz
    except ImportError:
        raise ImportError(
            "PyMuPDF required: pip install PyMuPDF --break-system-packages"
        )


def _ensure_pdfplumber():
    """Import pdfplumber."""
    try:
        import pdfplumber

        return pdfplumber
    except ImportError:
        raise ImportError(
            "pdfplumber required: pip install pdfplumber --break-system-packages"
        )


def analyze_page(fitz_page, page_num: int) -> PageInfo:
    """
    Analyze a single page to determine its type and characteristics.
    """
    rect = fitz_page.rect
    width = rect.width
    height = rect.height
    rotation = fitz_page.rotation

    # Determine orientation (accounting for rotation)
    effective_width = width if rotation in [0, 180] else height
    effective_height = height if rotation in [0, 180] else width

    if abs(effective_width - effective_height) < 10:
        orientation = Orientation.SQUARE
    elif effective_width > effective_height:
        orientation = Orientation.LANDSCAPE
    else:
        orientation = Orientation.PORTRAIT

    # Extract text and calculate density
    text = fitz_page.get_text()
    text_len = len(text.strip())
    area_sq_inch = (width / 72) * (height / 72)
    text_density = text_len / area_sq_inch if area_sq_inch > 0 else 0

    # Check for images
    image_list = fitz_page.get_images(full=True)
    has_images = len(image_list) > 0

    # Determine page type based on heuristics
    if text_density > 200:
        page_type = PageType.TEXT
    elif text_density < 30 and (has_images or orientation == Orientation.LANDSCAPE):
        page_type = PageType.DRAWING
    elif text_density < 100 and orientation == Orientation.LANDSCAPE:
        page_type = PageType.DRAWING
    elif has_images and text_density < 150:
        page_type = PageType.MIXED
    else:
        page_type = PageType.TEXT if text_density > 50 else PageType.UNKNOWN

    return PageInfo(
        page_num=page_num,
        width=width,
        height=height,
        orientation=orientation,
        page_type=page_type,
        text_density=text_density,
        has_images=has_images,
        rotation=rotation,
    )


def analyze_document(file_path: str) -> DocumentAnalysis:
    """
    Analyze a PDF to identify text vs drawing sections.

    Returns DocumentAnalysis with segment information.
    """
    fitz = _ensure_fitz()
    file_path = Path(file_path)

    doc = fitz.open(str(file_path))
    total_pages = len(doc)
    file_size_kb = file_path.stat().st_size / 1024

    # Analyze each page
    pages = []
    for i in range(total_pages):
        page_info = analyze_page(doc[i], i)
        pages.append(page_info)

    doc.close()

    # Find transition point (where drawings begin)
    transition_page = None
    for i, page in enumerate(pages):
        if page.is_drawing:
            # Check if this is the start of a drawing section
            # (not just a single figure in text)
            remaining_drawings = sum(1 for p in pages[i:] if p.is_drawing)
            remaining_total = len(pages) - i
            if remaining_drawings >= remaining_total * 0.7:  # 70%+ are drawings
                transition_page = i
                break

    # Build segments
    segments = []
    if transition_page is not None and transition_page > 0:
        # Text section
        segments.append(
            DocumentSegment(
                segment_type="text",
                start_page=0,
                end_page=transition_page - 1,
                page_count=transition_page,
                pages=pages[:transition_page],
            )
        )
        # Drawing section
        segments.append(
            DocumentSegment(
                segment_type="drawings",
                start_page=transition_page,
                end_page=total_pages - 1,
                page_count=total_pages - transition_page,
                pages=pages[transition_page:],
            )
        )
    elif transition_page == 0:
        # All drawings
        segments.append(
            DocumentSegment(
                segment_type="drawings",
                start_page=0,
                end_page=total_pages - 1,
                page_count=total_pages,
                pages=pages,
            )
        )
    else:
        # All text (no drawings found)
        segments.append(
            DocumentSegment(
                segment_type="text",
                start_page=0,
                end_page=total_pages - 1,
                page_count=total_pages,
                pages=pages,
            )
        )

    return DocumentAnalysis(
        file_path=str(file_path),
        total_pages=total_pages,
        file_size_kb=file_size_kb,
        segments=segments,
        transition_page=transition_page,
        pages=pages,
    )


def extract_text_section(
    file_path: str, start_page: int, end_page: int, output_dir: str
) -> Dict[str, Any]:
    """
    Extract text and tables from the text section of the PDF.

    Uses pdfplumber for better table extraction.
    """
    pdfplumber = _ensure_pdfplumber()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {"pages": [], "tables": [], "full_text": "", "output_files": []}

    with pdfplumber.open(file_path) as pdf:
        for page_num in range(start_page, end_page + 1):
            page = pdf.pages[page_num]

            # Extract text
            text = page.extract_text() or ""
            result["pages"].append({"page_num": page_num + 1, "text": text})
            result["full_text"] += f"\n\n--- Page {page_num + 1} ---\n\n{text}"

            # Extract tables
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                if table:
                    result["tables"].append(
                        {
                            "page_num": page_num + 1,
                            "table_idx": table_idx,
                            "data": table,
                        }
                    )

    # Save extracted text
    text_file = output_dir / "extracted_text.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(result["full_text"])
    result["output_files"].append(str(text_file))

    # Save tables as JSON
    if result["tables"]:
        tables_file = output_dir / "extracted_tables.json"
        with open(tables_file, "w", encoding="utf-8") as f:
            json.dump(result["tables"], f, indent=2)
        result["output_files"].append(str(tables_file))

    return result


def render_drawings_to_images(
    file_path: str,
    start_page: int,
    end_page: int,
    output_dir: str,
    dpi: int = 200,
    image_format: str = "png",
) -> List[str]:
    """
    Render drawing pages to high-resolution images for vision processing.

    Args:
        file_path: Path to PDF
        start_page: First drawing page (0-indexed)
        end_page: Last drawing page (0-indexed)
        output_dir: Directory for output images
        dpi: Resolution (200 is good balance of quality/size for A1/A0 drawings)
        image_format: "png" or "jpg"

    Returns:
        List of output image file paths
    """
    fitz = _ensure_fitz()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(file_path)
    output_files = []

    # Calculate zoom matrix for desired DPI
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(start_page, end_page + 1):
        page = doc[page_num]

        # Render page to pixmap
        pix = page.get_pixmap(matrix=mat)

        # Generate output filename
        ext = "jpg" if image_format.lower() in ["jpg", "jpeg"] else "png"
        output_file = output_dir / f"drawing_page_{page_num + 1:03d}.{ext}"

        # Save image
        if ext == "jpg":
            pix.save(str(output_file), jpg_quality=90)
        else:
            pix.save(str(output_file))

        output_files.append(str(output_file))
        print(f"  Rendered page {page_num + 1} -> {output_file.name}")

    doc.close()
    return output_files


def process_mixed_pdf(
    file_path: str, output_dir: str, drawing_dpi: int = 200, image_format: str = "png"
) -> DocumentAnalysis:
    """
    Complete pipeline to process a mixed-content PDF.

    1. Analyzes document to find text vs drawing sections
    2. Extracts text and tables from text section
    3. Renders drawings to images for vision processing

    Args:
        file_path: Path to input PDF
        output_dir: Base output directory
        drawing_dpi: DPI for rendering drawings (200 recommended for A1/A0)
        image_format: "png" or "jpg" for drawings

    Returns:
        DocumentAnalysis with all extracted content and file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing: {file_path}")

    # Step 1: Analyze document
    analysis = analyze_document(file_path)
    print(analysis.summary())
    print()

    # Step 2: Process each segment
    for segment in analysis.segments:
        if segment.segment_type == "text":
            print(
                f"Extracting text from pages {segment.start_page + 1}-{segment.end_page + 1}..."
            )
            text_output_dir = output_dir / "text_section"
            extracted = extract_text_section(
                file_path, segment.start_page, segment.end_page, str(text_output_dir)
            )
            segment.extracted_content = extracted
            segment.output_files = extracted["output_files"]
            print(f"  Saved: {[Path(f).name for f in segment.output_files]}")

        elif segment.segment_type == "drawings":
            print(
                f"Rendering drawings from pages {segment.start_page + 1}-{segment.end_page + 1}..."
            )
            drawings_output_dir = output_dir / "drawings"
            image_files = render_drawings_to_images(
                file_path,
                segment.start_page,
                segment.end_page,
                str(drawings_output_dir),
                dpi=drawing_dpi,
                image_format=image_format,
            )
            segment.output_files = image_files
            print(f"  Rendered {len(image_files)} drawing images")

    # Save analysis summary
    summary_file = output_dir / "document_analysis.json"
    summary_data = {
        "file_path": analysis.file_path,
        "total_pages": analysis.total_pages,
        "file_size_kb": analysis.file_size_kb,
        "transition_page": analysis.transition_page,
        "segments": [
            {
                "type": seg.segment_type,
                "pages": f"{seg.start_page + 1}-{seg.end_page + 1}",
                "count": seg.page_count,
                "output_files": seg.output_files,
            }
            for seg in analysis.segments
        ],
        "page_details": [
            {
                "page": p.page_num + 1,
                "orientation": p.orientation.value,
                "type": p.page_type.value,
                "text_density": round(p.text_density, 1),
            }
            for p in analysis.pages
        ],
    }
    with open(summary_file, "w") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\nAnalysis saved to: {summary_file}")
    return analysis


def get_drawings_for_vision(analysis: DocumentAnalysis) -> List[Tuple[int, str]]:
    """
    Get list of (page_number, image_path) tuples for vision processing.

    Use this to iterate through drawings for QS extraction.
    """
    drawings = []
    for segment in analysis.segments:
        if segment.segment_type == "drawings":
            for i, output_file in enumerate(segment.output_files):
                page_num = segment.start_page + i + 1
                drawings.append((page_num, output_file))
    return drawings


# =============================================================================
# QS Workflow Integration
# =============================================================================


def process_for_qs_extraction(
    file_path: str, project_dir: str, drawing_dpi: int = 200
) -> Dict[str, Any]:
    """
    Process PDF for QS quantity extraction workflow.

    This function integrates with the QS measurement skill:
    1. Analyzes and segments the PDF
    2. Extracts specs/text for reference
    3. Prepares drawings as images for vision extraction

    Args:
        file_path: Path to the architectural PDF
        project_dir: QS project directory
        drawing_dpi: Resolution for drawings (200 for detail, 150 for speed)

    Returns:
        Dictionary with paths and metadata for QS workflow
    """
    project_dir = Path(project_dir)

    # Create output structure
    output_dir = project_dir / "pdf_processing"

    # Process the PDF
    analysis = process_mixed_pdf(
        file_path, str(output_dir), drawing_dpi=drawing_dpi, image_format="png"
    )

    # Prepare result for QS workflow
    result = {
        "source_pdf": str(file_path),
        "project_dir": str(project_dir),
        "specs_text_file": None,
        "specs_tables_file": None,
        "drawing_images": [],
        "transition_page": analysis.transition_page,
        "total_pages": analysis.total_pages,
    }

    for segment in analysis.segments:
        if segment.segment_type == "text":
            for f in segment.output_files:
                if f.endswith(".txt"):
                    result["specs_text_file"] = f
                elif f.endswith(".json"):
                    result["specs_tables_file"] = f
        elif segment.segment_type == "drawings":
            result["drawing_images"] = [
                {"page": analysis.transition_page + i + 1, "image_path": img_path}
                for i, img_path in enumerate(segment.output_files)
            ]

    # Save workflow metadata
    workflow_file = project_dir / "pdf_workflow.json"
    with open(workflow_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n{'=' * 60}")
    print("QS Workflow Ready")
    print(f"{'=' * 60}")
    print(f"Specs text: {result['specs_text_file']}")
    print(f"Drawing images: {len(result['drawing_images'])} prepared")
    print(f"Workflow file: {workflow_file}")

    return result


# =============================================================================
# CLI Usage
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_processing_pipeline.py <pdf_file> [output_dir] [dpi]")
        print("\nExamples:")
        print("  python pdf_processing_pipeline.py document.pdf")
        print("  python pdf_processing_pipeline.py document.pdf ./output 200")
        print("\nFor QS workflow:")
        print("  python pdf_processing_pipeline.py document.pdf --qs ./qs_project")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Check for QS mode
    if "--qs" in sys.argv:
        qs_idx = sys.argv.index("--qs")
        project_dir = (
            sys.argv[qs_idx + 1] if qs_idx + 1 < len(sys.argv) else "./qs_project"
        )
        result = process_for_qs_extraction(pdf_path, project_dir)
    else:
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "./pdf_output"
        dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 200
        analysis = process_mixed_pdf(pdf_path, output_dir, drawing_dpi=dpi)

        # Show drawing files ready for vision
        drawings = get_drawings_for_vision(analysis)
        if drawings:
            print("\nDrawings ready for vision extraction:")
            for page_num, img_path in drawings:
                print(f"  Page {page_num}: {img_path}")
