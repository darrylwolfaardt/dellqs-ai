"""PDF Parser implementation for extracting content from architectural drawings."""

import hashlib
import io
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..common.base import BaseTool, ToolResult, ToolStatus, ToolError
from ..common.schemas import DocumentEntry, DocumentStatus


@dataclass
class PageContent:
    """Content extracted from a single PDF page."""
    page_number: int
    text: str
    has_images: bool
    image_count: int
    width_pts: float
    height_pts: float
    rotation: int
    extracted_image_path: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_number": self.page_number,
            "text": self.text,
            "has_images": self.has_images,
            "image_count": self.image_count,
            "width_pts": self.width_pts,
            "height_pts": self.height_pts,
            "rotation": self.rotation,
            "extracted_image_path": self.extracted_image_path,
        }


@dataclass
class PDFParserResult:
    """Result of parsing a PDF file."""
    file_path: str
    file_name: str
    file_size_bytes: int
    hash_md5: str
    page_count: int
    pages: list[PageContent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    is_scanned: bool = False
    has_text_layer: bool = True
    extraction_quality: str = "good"  # "good", "partial", "poor"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "hash_md5": self.hash_md5,
            "page_count": self.page_count,
            "pages": [p.to_dict() for p in self.pages],
            "metadata": self.metadata,
            "is_scanned": self.is_scanned,
            "has_text_layer": self.has_text_layer,
            "extraction_quality": self.extraction_quality,
        }

    def to_document_entry(self) -> DocumentEntry:
        """Convert to DocumentEntry for manifest."""
        return DocumentEntry(
            file_name=self.file_name,
            file_path=self.file_path,
            file_type="application/pdf",
            file_size_bytes=self.file_size_bytes,
            page_count=self.page_count,
            status=DocumentStatus.PRESENT,
            hash_md5=self.hash_md5,
        )


class PDFParser(BaseTool):
    """
    Tool for parsing PDF documents and extracting text, images, and metadata.

    Uses PyMuPDF (fitz) for PDF processing and optionally pdf2image for
    high-quality image extraction for vision model processing.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(config)
        self.output_dir = config.get("output_dir") if config else None
        self.extract_images = config.get("extract_images", True) if config else True
        self.image_dpi = config.get("image_dpi", 150) if config else 150
        self.image_format = config.get("image_format", "png") if config else "png"
        self._fitz = None
        self._pdf2image = None

    @property
    def name(self) -> str:
        return "pdf_parser"

    @property
    def description(self) -> str:
        return "Parses PDF documents to extract text, images, and metadata from architectural drawings"

    async def health_check(self) -> bool:
        """Check if required libraries are available."""
        try:
            import fitz
            self._fitz = fitz
            return True
        except ImportError:
            self.logger.warning("PyMuPDF (fitz) not installed. Run: pip install PyMuPDF")
            return False

    def _ensure_fitz(self):
        """Ensure fitz is imported."""
        if self._fitz is None:
            try:
                import fitz
                self._fitz = fitz
            except ImportError:
                raise ImportError(
                    "PyMuPDF is required for PDF parsing. Install with: pip install PyMuPDF"
                )
        return self._fitz

    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _extract_page_image(
        self,
        page,
        page_number: int,
        output_dir: Path,
        file_stem: str,
    ) -> Optional[str]:
        """Extract a page as an image for vision processing."""
        fitz = self._ensure_fitz()
        try:
            # Render page to image
            mat = fitz.Matrix(self.image_dpi / 72, self.image_dpi / 72)
            pix = page.get_pixmap(matrix=mat)

            # Save image
            image_filename = f"{file_stem}_page_{page_number:03d}.{self.image_format}"
            image_path = output_dir / image_filename
            pix.save(str(image_path))

            return str(image_path)
        except Exception as e:
            self.logger.warning(f"Failed to extract image for page {page_number}: {e}")
            return None

    def _detect_if_scanned(self, pages: list[PageContent]) -> tuple[bool, bool]:
        """
        Detect if the PDF is a scanned document.

        Returns:
            Tuple of (is_scanned, has_text_layer)
        """
        if not pages:
            return False, False

        # Check if pages have meaningful text
        total_text = sum(len(p.text.strip()) for p in pages)
        total_images = sum(p.image_count for p in pages)

        # Heuristic: if average text per page is very low but images exist
        avg_text_per_page = total_text / len(pages) if pages else 0

        if avg_text_per_page < 50 and total_images > 0:
            # Likely a scanned document
            return True, avg_text_per_page > 10

        return False, total_text > 0

    async def execute(
        self,
        file_path: str | Path,
        output_dir: Optional[str | Path] = None,
        extract_images: Optional[bool] = None,
    ) -> ToolResult[PDFParserResult]:
        """
        Parse a PDF file and extract content.

        Args:
            file_path: Path to the PDF file
            output_dir: Directory to save extracted images (optional)
            extract_images: Override config setting for image extraction

        Returns:
            ToolResult containing PDFParserResult
        """
        import time
        start_time = time.time()

        errors: list[ToolError] = []
        warnings: list[str] = []

        file_path = Path(file_path)

        # Validate input
        if not file_path.exists():
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "FILE_NOT_FOUND",
                    f"File not found: {file_path}",
                    recoverable=False,
                )],
            )

        if file_path.suffix.lower() != ".pdf":
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "INVALID_FILE_TYPE",
                    f"Expected PDF file, got: {file_path.suffix}",
                    recoverable=False,
                )],
            )

        # Setup output directory
        should_extract = extract_images if extract_images is not None else self.extract_images
        if output_dir:
            output_path = Path(output_dir)
        elif self.output_dir:
            output_path = Path(self.output_dir)
        else:
            output_path = Path(tempfile.mkdtemp(prefix="qs_pdf_"))

        output_path.mkdir(parents=True, exist_ok=True)

        fitz = self._ensure_fitz()

        try:
            # Calculate file hash
            file_hash = self._calculate_md5(file_path)
            file_size = file_path.stat().st_size

            # Open and parse PDF
            doc = fitz.open(str(file_path))

            # Extract document metadata
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", ""),
                "keywords": doc.metadata.get("keywords", ""),
            }

            pages: list[PageContent] = []

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Extract text
                text = page.get_text()

                # Count images
                image_list = page.get_images(full=True)
                image_count = len(image_list)

                # Get page dimensions
                rect = page.rect

                # Extract page as image if requested
                image_path = None
                if should_extract:
                    image_path = self._extract_page_image(
                        page,
                        page_num + 1,
                        output_path,
                        file_path.stem,
                    )

                page_content = PageContent(
                    page_number=page_num + 1,
                    text=text,
                    has_images=image_count > 0,
                    image_count=image_count,
                    width_pts=rect.width,
                    height_pts=rect.height,
                    rotation=page.rotation,
                    extracted_image_path=image_path,
                )
                pages.append(page_content)

            doc.close()

            # Detect if scanned
            is_scanned, has_text = self._detect_if_scanned(pages)

            # Determine extraction quality
            if is_scanned and not has_text:
                extraction_quality = "poor"
                warnings.append(
                    "PDF appears to be scanned without OCR. Text extraction limited."
                )
            elif is_scanned:
                extraction_quality = "partial"
                warnings.append(
                    "PDF appears to be scanned with OCR. Text extraction may be imperfect."
                )
            else:
                extraction_quality = "good"

            result = PDFParserResult(
                file_path=str(file_path),
                file_name=file_path.name,
                file_size_bytes=file_size,
                hash_md5=file_hash,
                page_count=len(pages),
                pages=pages,
                metadata=metadata,
                is_scanned=is_scanned,
                has_text_layer=has_text,
                extraction_quality=extraction_quality,
            )

            execution_time = (time.time() - start_time) * 1000

            return ToolResult(
                status=ToolStatus.SUCCESS if not warnings else ToolStatus.PARTIAL,
                data=result,
                warnings=warnings,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            self.logger.error(f"Failed to parse PDF {file_path}: {e}")
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "PARSE_ERROR",
                    f"Failed to parse PDF: {str(e)}",
                    recoverable=False,
                    details={"exception": str(type(e).__name__)},
                )],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def parse_directory(
        self,
        directory: str | Path,
        output_dir: Optional[str | Path] = None,
        recursive: bool = True,
    ) -> ToolResult[list[PDFParserResult]]:
        """
        Parse all PDF files in a directory.

        Args:
            directory: Directory to scan for PDFs
            output_dir: Directory to save extracted images
            recursive: Whether to scan subdirectories

        Returns:
            ToolResult containing list of PDFParserResult
        """
        import time
        start_time = time.time()

        directory = Path(directory)

        if not directory.exists():
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "DIR_NOT_FOUND",
                    f"Directory not found: {directory}",
                    recoverable=False,
                )],
            )

        # Find all PDFs
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(directory.glob(pattern))

        if not pdf_files:
            return ToolResult(
                status=ToolStatus.PARTIAL,
                data=[],
                warnings=["No PDF files found in directory"],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        results: list[PDFParserResult] = []
        errors: list[ToolError] = []
        warnings: list[str] = []

        for pdf_file in pdf_files:
            result = await self.execute(pdf_file, output_dir)

            if result.success and result.data:
                results.append(result.data)
            else:
                errors.extend(result.errors)

            warnings.extend(result.warnings)

        execution_time = (time.time() - start_time) * 1000

        if not results:
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=errors,
                warnings=warnings,
                execution_time_ms=execution_time,
            )

        return ToolResult(
            status=ToolStatus.SUCCESS if not errors else ToolStatus.PARTIAL,
            data=results,
            errors=errors,
            warnings=warnings,
            execution_time_ms=execution_time,
        )
