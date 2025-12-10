"""QS Agent Tools Package.

This package provides the tooling infrastructure for QS agents:
- pdf_parser: Parse PDF documents and extract content
- drawing_classifier: Classify architectural drawings using vision AI
- metadata_extractor: Extract project metadata from documents
- geocoder: Geocode addresses and postcodes
"""

from .common import (
    BaseTool,
    ToolResult,
    ToolError,
    DrawingType,
    DrawingInfo,
    ProjectMetadata,
    DocumentManifest,
    CompletenessReport,
    MeasurementScope,
)
from .pdf_parser import PDFParser, PDFParserResult
from .drawing_classifier import DrawingClassifier, ClassificationResult
from .metadata_extractor import MetadataExtractor, ExtractionResult
from .geocoder import Geocoder, GeocodingResult

__all__ = [
    # Base
    "BaseTool",
    "ToolResult",
    "ToolError",
    # Schemas
    "DrawingType",
    "DrawingInfo",
    "ProjectMetadata",
    "DocumentManifest",
    "CompletenessReport",
    "MeasurementScope",
    # Tools
    "PDFParser",
    "PDFParserResult",
    "DrawingClassifier",
    "ClassificationResult",
    "MetadataExtractor",
    "ExtractionResult",
    "Geocoder",
    "GeocodingResult",
]
