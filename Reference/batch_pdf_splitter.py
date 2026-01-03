"""
Batch PDF Splitter for Architectural Drawings
==============================================

Scans a project folder for large PDFs and splits them into manageable chunks.
Handles large single-page architectural drawings by rendering to images.

Usage:
    python batch_pdf_splitter.py <project_folder> [options]

Options:
    --max-size, -s    Split PDFs larger than this (MB), default: 5
    --max-pages, -p   Max pages per split file, default: 10
    --render          Render pages to images (for vision processing)
    --dpi             DPI for rendered images, default: 150
    --split-all       Split every page into separate file
    --target-size     Target size per output file (MB), default: 2

Output Structure:
    project_folder/
    ├── split_pdfs/
    │   ├── LargeDocument1/
    │   │   ├── LargeDocument1_page_001.pdf (or .png if --render)
    │   │   ├── LargeDocument1_page_002.pdf
    │   │   └── ...
    │   └── split_manifest.json
    └── original PDFs (unchanged)

Dependencies:
    pip install PyMuPDF --break-system-packages
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from datetime import datetime


@dataclass
class SplitFileInfo:
    """Information about a single split/rendered file."""

    filename: str
    path: str
    page_start: int  # 1-indexed
    page_end: int  # 1-indexed
    size_kb: float
    file_type: str  # "pdf" or "png" or "jpg"


@dataclass
class SplitPdfResult:
    """Result of splitting a single PDF."""

    original_file: str
    original_filename: str
    original_size_kb: float
    original_page_count: int
    output_folder: str
    split_files: List[SplitFileInfo] = field(default_factory=list)
    split_count: int = 0
    success: bool = True
    error: Optional[str] = None
    method: str = "split"  # "split", "render", "copy"


@dataclass
class BatchSplitManifest:
    """Manifest of all split operations."""

    project_folder: str
    processed_at: str
    settings: Dict
    total_pdfs_found: int
    total_pdfs_processed: int
    total_output_files: int
    pdfs: List[SplitPdfResult] = field(default_factory=list)


def _ensure_fitz():
    """Import PyMuPDF."""
    try:
        import fitz

        return fitz
    except ImportError:
        raise ImportError(
            "PyMuPDF required: pip install PyMuPDF --break-system-packages"
        )


def get_pdf_info(pdf_path: Path) -> Tuple[int, float, List[Tuple[float, float]]]:
    """
    Get PDF page count, file size, and per-page dimensions.

    Returns:
        (page_count, size_kb, [(width, height), ...])
    """
    fitz = _ensure_fitz()
    doc = fitz.open(str(pdf_path))
    page_count = len(doc)
    size_kb = pdf_path.stat().st_size / 1024

    dimensions = []
    for page in doc:
        rect = page.rect
        dimensions.append((rect.width, rect.height))

    doc.close()
    return page_count, size_kb, dimensions


def find_large_pdfs(
    folder: str, min_size_mb: float = 5.0, recursive: bool = True
) -> List[Path]:
    """
    Find all PDF files larger than the specified size.
    """
    folder = Path(folder)
    min_size_bytes = min_size_mb * 1024 * 1024

    pattern = "**/*.pdf" if recursive else "*.pdf"
    large_pdfs = []

    for pdf_path in folder.glob(pattern):
        # Skip files in split_pdfs output folder
        if "split_pdfs" in pdf_path.parts:
            continue

        if pdf_path.stat().st_size >= min_size_bytes:
            large_pdfs.append(pdf_path)

    return sorted(large_pdfs)


def render_page_to_image(
    doc, page_num: int, output_path: Path, dpi: int = 150, image_format: str = "png"
) -> float:
    """
    Render a single PDF page to an image.

    Returns:
        Size of output file in KB
    """
    fitz = _ensure_fitz()

    page = doc[page_num]

    # Calculate zoom for desired DPI
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    # Render to pixmap
    pix = page.get_pixmap(matrix=mat)

    # Save image
    if image_format.lower() in ["jpg", "jpeg"]:
        pix.save(str(output_path), jpg_quality=90)
    else:
        pix.save(str(output_path))

    return output_path.stat().st_size / 1024


def split_pdf_to_pages(
    pdf_path: Path,
    output_folder: Path,
    max_pages: int = 1,
    render_images: bool = False,
    dpi: int = 150,
    image_format: str = "png",
    target_size_kb: float = 2048,
) -> SplitPdfResult:
    """
    Split a PDF into individual pages or small chunks.

    For large architectural drawings, renders to images when:
    - render_images=True, OR
    - A single page PDF exceeds target_size_kb

    Args:
        pdf_path: Path to the PDF file
        output_folder: Folder to save split files
        max_pages: Maximum pages per split file (1 = individual pages)
        render_images: Force render all pages to images
        dpi: DPI for image rendering
        image_format: "png" or "jpg"
        target_size_kb: If single-page PDF exceeds this, render to image

    Returns:
        SplitPdfResult with details of the operation
    """
    fitz = _ensure_fitz()

    result = SplitPdfResult(
        original_file=str(pdf_path),
        original_filename=pdf_path.name,
        original_size_kb=pdf_path.stat().st_size / 1024,
        original_page_count=0,
        output_folder=str(output_folder),
    )

    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        result.original_page_count = total_pages

        # Create output folder
        output_folder.mkdir(parents=True, exist_ok=True)

        stem = pdf_path.stem
        split_files = []

        # Determine if we should render to images
        should_render = render_images

        # For single-page large PDFs, render to image
        if total_pages == 1 and result.original_size_kb > target_size_kb:
            should_render = True
            result.method = "render"
        elif render_images:
            result.method = "render"
        else:
            result.method = "split"

        if should_render:
            # Render each page to image
            ext = "jpg" if image_format.lower() in ["jpg", "jpeg"] else "png"

            for page_num in range(total_pages):
                output_filename = f"{stem}_page_{page_num + 1:03d}.{ext}"
                output_path = output_folder / output_filename

                size_kb = render_page_to_image(
                    doc, page_num, output_path, dpi, image_format
                )

                split_info = SplitFileInfo(
                    filename=output_filename,
                    path=str(output_path),
                    page_start=page_num + 1,
                    page_end=page_num + 1,
                    size_kb=round(size_kb, 2),
                    file_type=ext,
                )
                split_files.append(split_info)
        else:
            # Split into PDF chunks
            num_splits = (total_pages + max_pages - 1) // max_pages

            for split_idx in range(num_splits):
                start_page = split_idx * max_pages
                end_page = min(start_page + max_pages, total_pages)

                # Create new document with selected pages
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)

                # Generate output filename
                if max_pages == 1:
                    output_filename = f"{stem}_page_{start_page + 1:03d}.pdf"
                elif num_splits == 1:
                    output_filename = f"{stem}.pdf"
                else:
                    output_filename = (
                        f"{stem}_pages_{start_page + 1:03d}-{end_page:03d}.pdf"
                    )

                output_path = output_folder / output_filename
                new_doc.save(str(output_path))
                new_doc.close()

                split_info = SplitFileInfo(
                    filename=output_filename,
                    path=str(output_path),
                    page_start=start_page + 1,
                    page_end=end_page,
                    size_kb=round(output_path.stat().st_size / 1024, 2),
                    file_type="pdf",
                )
                split_files.append(split_info)

        doc.close()

        result.split_files = split_files
        result.split_count = len(split_files)
        result.success = True

    except Exception as e:
        result.success = False
        result.error = str(e)

    return result


def process_project_folder(
    project_folder: str,
    max_size_mb: float = 5.0,
    max_pages: int = 1,
    render_images: bool = False,
    dpi: int = 150,
    image_format: str = "png",
    target_size_mb: float = 2.0,
    recursive: bool = True,
    split_all_pages: bool = True,
) -> BatchSplitManifest:
    """
    Process all large PDFs in a project folder.

    Args:
        project_folder: Root folder to process
        max_size_mb: Process PDFs larger than this (in MB)
        max_pages: Maximum pages per split file (1 = individual pages)
        render_images: Render all pages to images
        dpi: DPI for image rendering
        image_format: "png" or "jpg" for images
        target_size_mb: Target max size per output file
        recursive: Search subdirectories for PDFs
        split_all_pages: Split every page into separate file

    Returns:
        BatchSplitManifest with all results
    """
    project_folder = Path(project_folder)
    output_base = project_folder / "split_pdfs"

    # Find large PDFs
    print(f"Scanning {project_folder} for PDFs > {max_size_mb} MB...")
    large_pdfs = find_large_pdfs(project_folder, max_size_mb, recursive)
    print(f"Found {len(large_pdfs)} large PDF(s)\n")

    if not large_pdfs:
        print("No PDFs found matching criteria.")

    # Settings for manifest
    settings = {
        "max_size_mb": max_size_mb,
        "max_pages_per_split": max_pages,
        "render_images": render_images,
        "dpi": dpi,
        "image_format": image_format,
        "target_size_mb": target_size_mb,
        "split_all_pages": split_all_pages,
    }

    # Initialize manifest
    manifest = BatchSplitManifest(
        project_folder=str(project_folder),
        processed_at=datetime.now().isoformat(),
        settings=settings,
        total_pdfs_found=len(large_pdfs),
        total_pdfs_processed=0,
        total_output_files=0,
    )

    # Process each PDF
    for pdf_path in large_pdfs:
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"Processing: {pdf_path.name}")
        print(f"  Size: {size_mb:.2f} MB")

        # Get page info
        try:
            page_count, _, dimensions = get_pdf_info(pdf_path)
            print(f"  Pages: {page_count}")

            # Check if pages are landscape (likely drawings)
            landscape_pages = sum(1 for w, h in dimensions if w > h)
            if landscape_pages > 0:
                print(f"  Landscape pages: {landscape_pages} (likely drawings)")
        except Exception as e:
            print(f"  Error reading PDF: {e}")
            continue

        # Create output folder named after the PDF
        pdf_output_folder = output_base / pdf_path.stem

        # Determine pages per split
        pages_per_split = 1 if split_all_pages else max_pages

        result = split_pdf_to_pages(
            pdf_path,
            pdf_output_folder,
            max_pages=pages_per_split,
            render_images=render_images,
            dpi=dpi,
            image_format=image_format,
            target_size_kb=target_size_mb * 1024,
        )

        if result.success:
            print(f"  Method: {result.method}")
            print(
                f"  Output: {result.split_count} file(s) in {pdf_output_folder.name}/"
            )

            # Show file sizes
            total_output_size = sum(sf.size_kb for sf in result.split_files)
            avg_size = (
                total_output_size / result.split_count if result.split_count > 0 else 0
            )
            print(f"  Avg file size: {avg_size:.1f} KB")

            manifest.total_pdfs_processed += 1
            manifest.total_output_files += result.split_count
        else:
            print(f"  ERROR: {result.error}")

        manifest.pdfs.append(result)
        print()

    # Save manifests (both formats)
    output_base.mkdir(parents=True, exist_ok=True)

    # Compact JSON
    json_path = output_base / "split_manifest.json"
    save_manifest_json(json_path, manifest.pdfs, settings)

    # Readable Markdown
    md_path = output_base / "split_manifest.md"
    save_manifest_markdown(md_path, manifest.pdfs, settings)

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"PDFs found:      {manifest.total_pdfs_found}")
    print(f"PDFs processed:  {manifest.total_pdfs_processed}")
    print(f"Output files:    {manifest.total_output_files}")
    print(f"Manifest:        {md_path}")

    return manifest


def build_pdf_entry(pdf_result: SplitPdfResult, compact: bool = True) -> Dict:
    """Build a PDF entry dict, optionally compact."""
    if compact:
        # Streamlined: just filename -> list of output files
        return {
            "source": pdf_result.original_filename,
            "pages": pdf_result.original_page_count,
            "method": pdf_result.method,
            "files": [sf.filename for sf in pdf_result.split_files],
        }
    else:
        return {
            "original_file": pdf_result.original_file,
            "original_filename": pdf_result.original_filename,
            "original_size_kb": round(pdf_result.original_size_kb, 2),
            "original_page_count": pdf_result.original_page_count,
            "output_folder": pdf_result.output_folder,
            "method": pdf_result.method,
            "split_count": pdf_result.split_count,
            "success": pdf_result.success,
            "error": pdf_result.error,
            "split_files": [
                {
                    "filename": sf.filename,
                    "path": sf.path,
                    "page_start": sf.page_start,
                    "page_end": sf.page_end,
                    "size_kb": sf.size_kb,
                    "file_type": sf.file_type,
                }
                for sf in pdf_result.split_files
            ],
        }


def save_manifest_json(
    manifest_path: Path, results: List[SplitPdfResult], settings: Dict
):
    """Save compact JSON manifest."""
    manifest = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "pdfs": [build_pdf_entry(r) for r in results if r.success],
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def save_manifest_markdown(
    manifest_path: Path, results: List[SplitPdfResult], settings: Dict
):
    """Save markdown manifest - clean and readable."""
    lines = [
        "# Split PDFs",
        f"",
        f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
    ]

    for r in results:
        if not r.success:
            lines.append(f"## ❌ {r.original_filename}")
            lines.append(f"Error: {r.error}")
            lines.append("")
            continue

        lines.append(f"## {r.original_filename}")
        lines.append(f"")
        lines.append(f"- **Pages:** {r.original_page_count}")
        lines.append(f"- **Size:** {r.original_size_kb / 1024:.1f} MB")
        lines.append(f"- **Method:** {r.method}")
        lines.append(f"- **Output:** `{Path(r.output_folder).name}/`")
        lines.append(f"")
        lines.append("| File | Pages | Size |")
        lines.append("|------|-------|------|")

        for sf in r.split_files:
            pages = (
                f"{sf.page_start}"
                if sf.page_start == sf.page_end
                else f"{sf.page_start}-{sf.page_end}"
            )
            lines.append(f"| {sf.filename} | {pages} | {sf.size_kb:.0f} KB |")

        lines.append("")

    with open(manifest_path, "w") as f:
        f.write("\n".join(lines))


def update_manifest(
    manifest_path: Path,
    pdf_result: SplitPdfResult,
    settings: Dict,
    use_markdown: bool = True,
) -> None:
    """
    Update or create manifest with a single PDF result.
    """
    output_base = manifest_path.parent
    output_base.mkdir(parents=True, exist_ok=True)

    # For single file updates, we maintain both formats
    json_path = output_base / "split_manifest.json"
    md_path = output_base / "split_manifest.md"

    # Load existing JSON to get previous entries
    existing_pdfs = []
    if json_path.exists():
        with open(json_path, "r") as f:
            existing = json.load(f)
            # We need to track which PDFs we've already processed
            existing_pdfs = existing.get("pdfs", [])

    # Check if this PDF already exists
    found_idx = None
    for i, pdf in enumerate(existing_pdfs):
        if pdf.get("source") == pdf_result.original_filename:
            found_idx = i
            break

    new_entry = build_pdf_entry(pdf_result)

    if found_idx is not None:
        existing_pdfs[found_idx] = new_entry
        print(f"  Updated existing entry")
    else:
        existing_pdfs.append(new_entry)
        print(f"  Added new entry")

    # Save compact JSON
    manifest = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "pdfs": existing_pdfs,
    }
    with open(json_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Also save markdown version
    # For this we need full SplitPdfResult objects, so just save the current one
    # In practice, we'd need to track all results - for now, append to existing md
    if md_path.exists():
        with open(md_path, "r") as f:
            content = f.read()

        # Check if this PDF section already exists
        section_header = f"## {pdf_result.original_filename}"
        if section_header in content:
            # Replace the section - find start and next ##
            start = content.find(section_header)
            next_section = content.find("\n## ", start + 1)
            if next_section == -1:
                content = content[:start]
            else:
                content = content[:start] + content[next_section + 1 :]
    else:
        content = "# Split PDFs\n\n"

    # Add/update the entry
    lines = [
        f"## {pdf_result.original_filename}",
        f"",
        f"- **Pages:** {pdf_result.original_page_count}",
        f"- **Size:** {pdf_result.original_size_kb / 1024:.1f} MB",
        f"- **Method:** {pdf_result.method}",
        f"- **Output:** `{Path(pdf_result.output_folder).name}/`",
        f"",
        "| File | Pages | Size |",
        "|------|-------|------|",
    ]

    for sf in pdf_result.split_files:
        pages = (
            f"{sf.page_start}"
            if sf.page_start == sf.page_end
            else f"{sf.page_start}-{sf.page_end}"
        )
        lines.append(f"| {sf.filename} | {pages} | {sf.size_kb:.0f} KB |")

    lines.append("")

    # Update timestamp in header
    if "Updated:" in content:
        import re

        content = re.sub(
            r"Updated:.*\n",
            f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
            content,
        )
    else:
        content = (
            f"# Split PDFs\n\nUpdated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        )

    content += "\n".join(lines)

    with open(md_path, "w") as f:
        f.write(content)

    print(f"  Manifest: {md_path.name}")


def process_single_file(
    pdf_path: str,
    output_base: Optional[str] = None,
    max_pages: int = 1,
    render_images: bool = False,
    dpi: int = 150,
    image_format: str = "png",
    target_size_mb: float = 2.0,
    split_all_pages: bool = True,
) -> SplitPdfResult:
    """
    Process a single PDF file and update the manifest.

    Args:
        pdf_path: Path to the PDF file
        output_base: Base output directory (default: same folder as PDF/split_pdfs)
        max_pages: Maximum pages per split file
        render_images: Render pages to images
        dpi: DPI for image rendering
        image_format: "png" or "jpg"
        target_size_mb: Target max size per output
        split_all_pages: Split every page into separate file

    Returns:
        SplitPdfResult with processing details
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        return None

    if not pdf_path.suffix.lower() == ".pdf":
        print(f"Error: Not a PDF file: {pdf_path}")
        return None

    # Determine output location
    if output_base:
        output_base = Path(output_base)
    else:
        output_base = pdf_path.parent / "split_pdfs"

    pdf_output_folder = output_base / pdf_path.stem

    # Settings
    settings = {
        "max_size_mb": None,  # N/A for single file
        "max_pages_per_split": max_pages,
        "render_images": render_images,
        "dpi": dpi,
        "image_format": image_format,
        "target_size_mb": target_size_mb,
        "split_all_pages": split_all_pages,
    }

    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"Processing: {pdf_path.name}")
    print(f"  Size: {size_mb:.2f} MB")

    # Get page info
    try:
        page_count, _, dimensions = get_pdf_info(pdf_path)
        print(f"  Pages: {page_count}")

        landscape_pages = sum(1 for w, h in dimensions if w > h)
        if landscape_pages > 0:
            print(f"  Landscape pages: {landscape_pages} (likely drawings)")
    except Exception as e:
        print(f"  Error reading PDF: {e}")
        return None

    # Process the PDF
    pages_per_split = 1 if split_all_pages else max_pages

    result = split_pdf_to_pages(
        pdf_path,
        pdf_output_folder,
        max_pages=pages_per_split,
        render_images=render_images,
        dpi=dpi,
        image_format=image_format,
        target_size_kb=target_size_mb * 1024,
    )

    if result.success:
        print(f"  Method: {result.method}")
        print(f"  Output: {result.split_count} file(s) in {pdf_output_folder.name}/")

        total_output_size = sum(sf.size_kb for sf in result.split_files)
        avg_size = (
            total_output_size / result.split_count if result.split_count > 0 else 0
        )
        print(f"  Avg file size: {avg_size:.1f} KB")

        # Update manifest
        manifest_path = output_base / "split_manifest.json"
        update_manifest(manifest_path, result, settings)
    else:
        print(f"  ERROR: {result.error}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Split large PDFs (especially architectural drawings) in a project folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split all large PDFs into individual pages
  python batch_pdf_splitter.py /path/to/project

  # Process a SINGLE PDF file (updates manifest)
  python batch_pdf_splitter.py /path/to/drawing.pdf

  # Single file with custom output location
  python batch_pdf_splitter.py /path/to/drawing.pdf --output /project/split_pdfs

  # Render drawings to PNG images for vision processing
  python batch_pdf_splitter.py /path/to/project --render --dpi 200

  # Process smaller files (> 2MB) with custom settings
  python batch_pdf_splitter.py /path/to/project -s 2 --render --dpi 150

  # Split into 5-page chunks instead of individual pages
  python batch_pdf_splitter.py /path/to/project --max-pages 5 --no-split-all

Output:
  project_folder/
  └── split_pdfs/
      ├── DrawingSet1/
      │   ├── DrawingSet1_page_001.png (if --render)
      │   ├── DrawingSet1_page_002.png
      │   └── ...
      ├── DrawingSet2/
      │   └── ...
      └── split_manifest.json
        """,
    )

    parser.add_argument(
        "input_path", help="Project folder to scan, OR a single PDF file to process"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory for split files (default: input_path/split_pdfs)",
    )
    parser.add_argument(
        "--max-size",
        "-s",
        type=float,
        default=5.0,
        help="Process PDFs larger than this size in MB (default: 5, ignored for single file)",
    )
    parser.add_argument(
        "--max-pages",
        "-p",
        type=int,
        default=10,
        help="Max pages per split file when not splitting all (default: 10)",
    )
    parser.add_argument(
        "--render",
        "-r",
        action="store_true",
        help="Render pages to images (PNG/JPG) for vision processing",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="DPI for rendered images (default: 150, use 200 for detail)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["png", "jpg"],
        default="png",
        help="Image format when rendering (default: png)",
    )
    parser.add_argument(
        "--target-size",
        "-t",
        type=float,
        default=2.0,
        help="Target max size per output in MB (default: 2)",
    )
    parser.add_argument(
        "--no-split-all",
        action="store_true",
        help="Don't split every page - use --max-pages chunks instead",
    )
    parser.add_argument(
        "--no-recursive", action="store_true", help="Don't search subdirectories"
    )

    args = parser.parse_args()

    input_path = Path(args.input_path)

    if not input_path.exists():
        print(f"Error: Path not found: {input_path}")
        sys.exit(1)

    # Detect if input is a single file or a folder
    if input_path.is_file():
        # Single file mode
        if input_path.suffix.lower() != ".pdf":
            print(f"Error: Not a PDF file: {input_path}")
            sys.exit(1)

        print("=" * 60)
        print("SINGLE FILE MODE")
        print("=" * 60)

        result = process_single_file(
            str(input_path),
            output_base=args.output,
            max_pages=args.max_pages,
            render_images=args.render,
            dpi=args.dpi,
            image_format=args.format,
            target_size_mb=args.target_size,
            split_all_pages=not args.no_split_all,
        )

        if result and result.success:
            print("\n" + "=" * 60)
            print("SUCCESS")
            print("=" * 60)
        else:
            sys.exit(1)
    else:
        # Folder mode
        process_project_folder(
            str(input_path),
            max_size_mb=args.max_size,
            max_pages=args.max_pages,
            render_images=args.render,
            dpi=args.dpi,
            image_format=args.format,
            target_size_mb=args.target_size,
            recursive=not args.no_recursive,
            split_all_pages=not args.no_split_all,
        )


if __name__ == "__main__":
    main()
