"""
PDF Splitter Module for DELLQS-AI
===================================

This module provides functionality to split large PDF files into smaller parts
to avoid API size limit errors (HTTP 413 - Request Too Large).

Use Case:
- When Claude Code's Read tool returns a 413 error for large PDFs
- Split the PDF into smaller chunks that can be processed individually

Dependencies:
- PyMuPDF (fitz): pip install PyMuPDF

Author: DELLQS-AI
Date: 2025-12-13
Version: 1.0
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass


# Default size limit - approximately 500KB for safe API usage
# The actual limit is higher, but this provides a safety margin
DEFAULT_MAX_SIZE_KB = 500
DEFAULT_MAX_PAGES = 5


@dataclass
class SplitResult:
    """Result of a PDF split operation."""
    original_path: str
    original_size_kb: float
    original_page_count: int
    split_files: List[str]
    split_count: int
    success: bool
    error_message: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return (
                f"Split '{Path(self.original_path).name}' "
                f"({self.original_size_kb:.1f}KB, {self.original_page_count} pages) "
                f"into {self.split_count} parts"
            )
        return f"Failed to split '{self.original_path}': {self.error_message}"


def _ensure_fitz():
    """Import and return fitz (PyMuPDF)."""
    try:
        import fitz
        return fitz
    except ImportError:
        raise ImportError(
            "PyMuPDF is required for PDF splitting. Install with: pip install PyMuPDF"
        )


def get_pdf_info(file_path: Union[str, Path]) -> Tuple[float, int]:
    """
    Get PDF file size and page count.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple of (size_in_kb, page_count)
    """
    fitz = _ensure_fitz()
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    size_kb = file_path.stat().st_size / 1024

    doc = fitz.open(str(file_path))
    page_count = len(doc)
    doc.close()

    return size_kb, page_count


def is_pdf_too_large(
    file_path: Union[str, Path],
    max_size_kb: float = DEFAULT_MAX_SIZE_KB
) -> bool:
    """
    Check if a PDF file exceeds the size limit.

    Args:
        file_path: Path to the PDF file
        max_size_kb: Maximum size in kilobytes (default: 500KB)

    Returns:
        True if the file is too large, False otherwise
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return False

    size_kb = file_path.stat().st_size / 1024
    return size_kb > max_size_kb


def split_pdf_by_pages(
    file_path: Union[str, Path],
    pages_per_split: int = DEFAULT_MAX_PAGES,
    output_dir: Optional[Union[str, Path]] = None,
    output_prefix: Optional[str] = None
) -> SplitResult:
    """
    Split a PDF into multiple files with a fixed number of pages each.

    Args:
        file_path: Path to the PDF file to split
        pages_per_split: Maximum pages per output file (default: 5)
        output_dir: Directory for output files (default: same as input)
        output_prefix: Prefix for output files (default: original filename)

    Returns:
        SplitResult with details of the operation
    """
    fitz = _ensure_fitz()
    file_path = Path(file_path)

    if not file_path.exists():
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=0,
            original_page_count=0,
            split_files=[],
            split_count=0,
            success=False,
            error_message=f"File not found: {file_path}"
        )

    # Setup output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = file_path.parent
    output_path.mkdir(parents=True, exist_ok=True)

    # Setup output prefix
    if not output_prefix:
        output_prefix = file_path.stem

    try:
        # Get original file info
        size_kb = file_path.stat().st_size / 1024

        # Open the PDF
        doc = fitz.open(str(file_path))
        total_pages = len(doc)

        # If already small enough, no split needed
        if total_pages <= pages_per_split:
            doc.close()
            return SplitResult(
                original_path=str(file_path),
                original_size_kb=size_kb,
                original_page_count=total_pages,
                split_files=[str(file_path)],
                split_count=1,
                success=True
            )

        split_files = []
        part_number = 1

        # Split into chunks
        for start_page in range(0, total_pages, pages_per_split):
            end_page = min(start_page + pages_per_split - 1, total_pages - 1)

            # Create new document with selected pages
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)

            # Generate output filename
            output_filename = f"{output_prefix}_part{part_number:02d}.pdf"
            output_file = output_path / output_filename

            # Save the split file
            new_doc.save(str(output_file))
            new_doc.close()

            split_files.append(str(output_file))
            part_number += 1

        doc.close()

        return SplitResult(
            original_path=str(file_path),
            original_size_kb=size_kb,
            original_page_count=total_pages,
            split_files=split_files,
            split_count=len(split_files),
            success=True
        )

    except Exception as e:
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=0,
            original_page_count=0,
            split_files=[],
            split_count=0,
            success=False,
            error_message=str(e)
        )


def split_pdf_by_size(
    file_path: Union[str, Path],
    max_size_kb: float = DEFAULT_MAX_SIZE_KB,
    output_dir: Optional[Union[str, Path]] = None,
    output_prefix: Optional[str] = None
) -> SplitResult:
    """
    Split a PDF into multiple files, each under the specified size limit.

    Uses a binary search approach to find the optimal number of pages per split.

    Args:
        file_path: Path to the PDF file to split
        max_size_kb: Maximum size per output file in KB (default: 500KB)
        output_dir: Directory for output files (default: same as input)
        output_prefix: Prefix for output files (default: original filename)

    Returns:
        SplitResult with details of the operation
    """
    fitz = _ensure_fitz()
    file_path = Path(file_path)

    if not file_path.exists():
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=0,
            original_page_count=0,
            split_files=[],
            split_count=0,
            success=False,
            error_message=f"File not found: {file_path}"
        )

    # Setup output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = file_path.parent
    output_path.mkdir(parents=True, exist_ok=True)

    # Setup output prefix
    if not output_prefix:
        output_prefix = file_path.stem

    try:
        # Get original file info
        original_size_kb = file_path.stat().st_size / 1024

        # If already under limit, no split needed
        if original_size_kb <= max_size_kb:
            doc = fitz.open(str(file_path))
            page_count = len(doc)
            doc.close()
            return SplitResult(
                original_path=str(file_path),
                original_size_kb=original_size_kb,
                original_page_count=page_count,
                split_files=[str(file_path)],
                split_count=1,
                success=True
            )

        # Open the PDF
        doc = fitz.open(str(file_path))
        total_pages = len(doc)

        # Estimate pages per chunk based on average page size
        avg_page_size = original_size_kb / total_pages
        estimated_pages = max(1, int(max_size_kb / avg_page_size * 0.8))  # 80% margin

        split_files = []
        part_number = 1
        current_page = 0

        while current_page < total_pages:
            # Start with estimated pages, adjust if needed
            pages_to_include = min(estimated_pages, total_pages - current_page)

            # Binary search for optimal page count
            while pages_to_include > 0:
                # Create test document
                test_doc = fitz.open()
                test_doc.insert_pdf(
                    doc,
                    from_page=current_page,
                    to_page=current_page + pages_to_include - 1
                )

                # Check size by saving to temp file
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp_path = tmp.name

                test_doc.save(tmp_path)
                test_doc.close()

                test_size_kb = os.path.getsize(tmp_path) / 1024
                os.unlink(tmp_path)

                if test_size_kb <= max_size_kb:
                    break

                # Reduce pages and try again
                pages_to_include = max(1, pages_to_include // 2)

            # Create the actual split file
            new_doc = fitz.open()
            new_doc.insert_pdf(
                doc,
                from_page=current_page,
                to_page=current_page + pages_to_include - 1
            )

            output_filename = f"{output_prefix}_part{part_number:02d}.pdf"
            output_file = output_path / output_filename

            new_doc.save(str(output_file))
            new_doc.close()

            split_files.append(str(output_file))
            current_page += pages_to_include
            part_number += 1

        doc.close()

        return SplitResult(
            original_path=str(file_path),
            original_size_kb=original_size_kb,
            original_page_count=total_pages,
            split_files=split_files,
            split_count=len(split_files),
            success=True
        )

    except Exception as e:
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=0,
            original_page_count=0,
            split_files=[],
            split_count=0,
            success=False,
            error_message=str(e)
        )


def split_pdf_single_pages(
    file_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    output_prefix: Optional[str] = None
) -> SplitResult:
    """
    Split a PDF into individual single-page files.

    Useful for architectural drawings where each page is a separate drawing.

    Args:
        file_path: Path to the PDF file to split
        output_dir: Directory for output files (default: same as input)
        output_prefix: Prefix for output files (default: original filename)

    Returns:
        SplitResult with details of the operation
    """
    return split_pdf_by_pages(
        file_path=file_path,
        pages_per_split=1,
        output_dir=output_dir,
        output_prefix=output_prefix
    )


def split_for_api(
    file_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    max_size_kb: float = DEFAULT_MAX_SIZE_KB
) -> SplitResult:
    """
    Split a PDF to ensure each part can be processed by the API.

    This is the recommended function to use when handling 413 errors.
    It automatically determines the best split strategy.

    Args:
        file_path: Path to the PDF file
        output_dir: Directory for output files (default: creates temp dir)
        max_size_kb: Maximum size per file in KB (default: 500KB)

    Returns:
        SplitResult with list of files to process

    Example:
        # When you get a 413 error:
        result = split_for_api("large_drawing.pdf")
        if result.success:
            for part_file in result.split_files:
                # Process each part with the API
                content = read_pdf(part_file)
    """
    file_path = Path(file_path)

    # Use temp directory if no output specified
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="qs_pdf_split_"))

    # First check if split is needed
    if not is_pdf_too_large(file_path, max_size_kb):
        size_kb, page_count = get_pdf_info(file_path)
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=size_kb,
            original_page_count=page_count,
            split_files=[str(file_path)],
            split_count=1,
            success=True
        )

    # Split by size for best results
    return split_pdf_by_size(
        file_path=file_path,
        max_size_kb=max_size_kb,
        output_dir=output_dir
    )


def cleanup_split_files(split_result: SplitResult) -> None:
    """
    Clean up temporary split files after processing.

    Args:
        split_result: The result from a split operation
    """
    for file_path in split_result.split_files:
        path = Path(file_path)
        # Only delete if it's in a temp directory
        if 'qs_pdf_split_' in str(path.parent):
            try:
                path.unlink()
            except OSError:
                pass

    # Try to remove the temp directory if empty
    if split_result.split_files:
        parent = Path(split_result.split_files[0]).parent
        if 'qs_pdf_split_' in str(parent):
            try:
                parent.rmdir()
            except OSError:
                pass


def render_pdf_to_image(
    file_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    dpi: int = 150,
    image_format: str = "png"
) -> SplitResult:
    """
    Render PDF pages to images for API processing.

    This is useful for single-page PDFs that are too large - instead of
    splitting, we render to an image which the API can process.

    Args:
        file_path: Path to the PDF file
        output_dir: Directory for output images (default: creates temp dir)
        dpi: Resolution in dots per inch (default: 150, lower = smaller file)
        image_format: Output format - 'png' or 'jpg' (jpg is smaller)

    Returns:
        SplitResult with list of image files
    """
    fitz = _ensure_fitz()
    file_path = Path(file_path)

    if not file_path.exists():
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=0,
            original_page_count=0,
            split_files=[],
            split_count=0,
            success=False,
            error_message=f"File not found: {file_path}"
        )

    # Setup output directory
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="qs_pdf_render_"))
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        original_size_kb = file_path.stat().st_size / 1024

        doc = fitz.open(str(file_path))
        total_pages = len(doc)

        output_files = []
        mat = fitz.Matrix(dpi / 72, dpi / 72)

        for page_num in range(total_pages):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=mat)

            ext = "jpg" if image_format.lower() in ["jpg", "jpeg"] else "png"
            output_filename = f"{file_path.stem}_page{page_num + 1:02d}.{ext}"
            output_file = output_dir / output_filename

            if ext == "jpg":
                pix.save(str(output_file), jpg_quality=85)
            else:
                pix.save(str(output_file))

            output_files.append(str(output_file))

        doc.close()

        return SplitResult(
            original_path=str(file_path),
            original_size_kb=original_size_kb,
            original_page_count=total_pages,
            split_files=output_files,
            split_count=len(output_files),
            success=True
        )

    except Exception as e:
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=0,
            original_page_count=0,
            split_files=[],
            split_count=0,
            success=False,
            error_message=str(e)
        )


def handle_large_pdf(
    file_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    max_size_kb: float = DEFAULT_MAX_SIZE_KB,
    render_dpi: int = 150,
    image_format: str = "png"
) -> SplitResult:
    """
    Smart handler for large PDFs - the main function to use for 413 errors.

    Automatically chooses the best strategy:
    - Multi-page PDFs: Split by size
    - Single-page PDFs: Render to image
    - Already small: Return original

    Args:
        file_path: Path to the PDF file
        output_dir: Directory for output files (default: creates temp dir)
        max_size_kb: Maximum size per file in KB (default: 500KB)
        render_dpi: DPI for image rendering (default: 150)
        image_format: Image format for rendering - 'png' or 'jpg'

    Returns:
        SplitResult with list of files to process

    Example:
        # When you get a 413 error:
        result = handle_large_pdf("large_drawing.pdf")
        if result.success:
            for part_file in result.split_files:
                # Process each part with the API
                content = read_file(part_file)
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=0,
            original_page_count=0,
            split_files=[],
            split_count=0,
            success=False,
            error_message=f"File not found: {file_path}"
        )

    # Check if split is needed
    if not is_pdf_too_large(file_path, max_size_kb):
        size_kb, page_count = get_pdf_info(file_path)
        return SplitResult(
            original_path=str(file_path),
            original_size_kb=size_kb,
            original_page_count=page_count,
            split_files=[str(file_path)],
            split_count=1,
            success=True
        )

    # Get page count
    size_kb, page_count = get_pdf_info(file_path)

    # Use temp directory if no output specified
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="qs_pdf_handle_"))

    # Single-page large PDFs: render to image
    if page_count == 1:
        return render_pdf_to_image(
            file_path=file_path,
            output_dir=output_dir,
            dpi=render_dpi,
            image_format=image_format
        )

    # Multi-page: split by size
    return split_pdf_by_size(
        file_path=file_path,
        max_size_kb=max_size_kb,
        output_dir=output_dir
    )


# Example usage and testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python PDF_Splitter_Module.py <pdf_file> [max_size_kb]")
        print("\nExample:")
        print("  python PDF_Splitter_Module.py large_drawing.pdf 500")
        sys.exit(1)

    pdf_path = sys.argv[1]
    max_size = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_SIZE_KB

    print(f"\nAnalyzing: {pdf_path}")

    try:
        size_kb, pages = get_pdf_info(pdf_path)
        print(f"  Size: {size_kb:.1f} KB")
        print(f"  Pages: {pages}")
        print(f"  Max allowed: {max_size} KB")

        if is_pdf_too_large(pdf_path, max_size):
            print(f"\n  File exceeds {max_size}KB limit - splitting...")
            result = split_for_api(pdf_path, max_size_kb=max_size)
            print(f"  {result}")

            if result.success:
                print("\n  Split files:")
                for i, f in enumerate(result.split_files, 1):
                    split_size = Path(f).stat().st_size / 1024
                    print(f"    {i}. {Path(f).name} ({split_size:.1f} KB)")
        else:
            print(f"\n  File is under {max_size}KB - no split needed")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
