"""
Intake Analyst Agent Implementation.

The Intake Analyst is the first agent in the QS pipeline. It:
1. Receives architectural drawing packages
2. Validates completeness
3. Extracts metadata
4. Identifies what's present/missing
5. Produces outputs for downstream agents

Outputs:
- project_manifest.json: What we received
- completeness_report.md: What's missing
- measurement_scope.md: What can be measured from available info
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..tools import (
    PDFParser,
    PDFParserResult,
    DrawingClassifier,
    ClassificationResult,
    MetadataExtractor,
    ExtractionResult,
    Geocoder,
    GeocodingResult,
)
from ..tools.common import (
    ToolResult,
    ToolStatus,
    DrawingType,
    DrawingInfo,
    ProjectMetadata,
    LocationInfo,
    DocumentManifest,
    DocumentEntry,
    CompletenessReport,
    MeasurementScope,
    MissingItem,
    MeasurableElement,
)

logger = logging.getLogger(__name__)


@dataclass
class IntakeResult:
    """Complete result of intake analysis."""
    project_id: str
    manifest: DocumentManifest
    completeness: CompletenessReport
    measurement_scope: MeasurementScope
    processing_time_ms: float
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "manifest": self.manifest.to_dict(),
            "completeness": self.completeness.to_dict(),
            "measurement_scope": self.measurement_scope.to_dict(),
            "processing_time_ms": self.processing_time_ms,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class IntakeAnalyst:
    """
    Intake Analyst Agent - First eyes on every project.

    Scans drawing packages, identifies document types, extracts metadata,
    and flags gaps that will impede measurement.

    Principles:
    - Catalogue before analyse
    - Flag missing information explicitly, never assume
    - Extract: project name, location, architect, revision dates, scale
    - Identify drawing types and their measurement implications
    """

    # Required drawing types for different project types
    REQUIRED_DRAWINGS = {
        "new_build_residential": [
            DrawingType.SITE_PLAN,
            DrawingType.FLOOR_PLAN,
            DrawingType.ELEVATION,
            DrawingType.SECTION,
        ],
        "new_build_commercial": [
            DrawingType.SITE_PLAN,
            DrawingType.FLOOR_PLAN,
            DrawingType.ELEVATION,
            DrawingType.SECTION,
            DrawingType.ROOF_PLAN,
        ],
        "refurbishment": [
            DrawingType.FLOOR_PLAN,
            DrawingType.DEMOLITION,
        ],
        "default": [
            DrawingType.FLOOR_PLAN,
        ],
    }

    # What can be measured from each drawing type
    MEASUREMENT_POTENTIAL = {
        DrawingType.FLOOR_PLAN: [
            "Gross Internal Floor Area (GIFA)",
            "Net Internal Area (NIA)",
            "Room areas",
            "Wall lengths (internal)",
            "Door positions and counts",
            "Window positions",
            "Partition lengths",
        ],
        DrawingType.SITE_PLAN: [
            "Site area",
            "Building footprint",
            "Hard landscaping areas",
            "Soft landscaping areas",
            "Boundary lengths",
            "Parking spaces",
            "Access road lengths",
        ],
        DrawingType.ELEVATION: [
            "External wall areas",
            "Window areas and counts",
            "Door areas and counts",
            "Cladding areas",
            "Building height",
        ],
        DrawingType.SECTION: [
            "Floor-to-floor heights",
            "Floor construction depths",
            "Roof construction depth",
            "Foundation depths",
            "Stair flights",
        ],
        DrawingType.ROOF_PLAN: [
            "Roof area",
            "Roof perimeter",
            "Rainwater goods",
            "Rooflights",
        ],
        DrawingType.REFLECTED_CEILING: [
            "Ceiling areas",
            "Ceiling grid",
            "Light fittings count",
            "Access panels",
        ],
        DrawingType.SCHEDULE: [
            "Door schedule quantities",
            "Window schedule quantities",
            "Finish schedule",
            "Room data",
        ],
        DrawingType.STRUCTURAL: [
            "Foundation types/sizes",
            "Beam sizes",
            "Column positions",
            "Slab thicknesses",
        ],
        DrawingType.DETAIL: [
            "Construction build-ups",
            "Material specifications",
        ],
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the Intake Analyst.

        Args:
            config: Configuration dict with optional keys:
                - output_dir: Directory for output files
                - vision_provider: "claude" (default), "anthropic", or "openai"
                - vision_model: Model name for classification (used with anthropic/openai)
                - anthropic_api_key: API key for Anthropic (optional, falls back to claude CLI)
                - openai_api_key: API key for OpenAI
                - google_api_key: API key for Google Geocoding
                - project_type: Expected project type for completeness check

        Note:
            By default, uses Claude Code CLI for vision classification. This leverages
            the authenticated Claude Code session and doesn't require API keys.
            Set vision_provider to "anthropic" or "openai" with corresponding API key
            to use direct API access instead.
        """
        self.config = config or {}
        self.output_dir = Path(config.get("output_dir", "./intake_output")) if config else Path("./intake_output")
        self.project_type = config.get("project_type", "default") if config else "default"

        # Initialize tools
        self.pdf_parser = PDFParser({
            "output_dir": str(self.output_dir / "images"),
            "extract_images": True,
            "image_dpi": 150,
        })

        # Vision config - default to 'claude' (CLI) which uses authenticated session
        vision_config = {
            "provider": config.get("vision_provider", "claude") if config else "claude",
            "model": config.get("vision_model", "claude-sonnet-4-20250514") if config else "claude-sonnet-4-20250514",
        }
        # Only set API key if explicitly provided (for direct API access)
        if config and config.get("anthropic_api_key"):
            vision_config["provider"] = "anthropic"
            vision_config["api_key"] = config["anthropic_api_key"]
        elif config and config.get("openai_api_key"):
            vision_config["provider"] = "openai"
            vision_config["api_key"] = config["openai_api_key"]
        self.classifier = DrawingClassifier(vision_config)

        self.metadata_extractor = MetadataExtractor()

        geocoder_config = {}
        if config and config.get("google_api_key"):
            geocoder_config["provider"] = "google"
            geocoder_config["google_api_key"] = config["google_api_key"]
        self.geocoder = Geocoder(geocoder_config)

        self.logger = logging.getLogger(self.__class__.__name__)

    async def analyze(
        self,
        input_path: str | Path,
        project_id: Optional[str] = None,
    ) -> IntakeResult:
        """
        Analyze a document package or single file.

        Args:
            input_path: Path to PDF file or directory containing PDFs
            project_id: Optional project identifier (generated if not provided)

        Returns:
            IntakeResult with manifest, completeness report, and measurement scope
        """
        import time
        start_time = time.time()

        input_path = Path(input_path)
        project_id = project_id or str(uuid.uuid4())[:8].upper()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        errors: list[dict[str, Any]] = []
        warnings: list[str] = []

        # Step 1: Parse PDFs
        self.logger.info(f"[{project_id}] Starting intake analysis for: {input_path}")

        if input_path.is_file():
            pdf_result = await self.pdf_parser.execute(input_path, self.output_dir / "images")
            pdf_results = [pdf_result.data] if pdf_result.success and pdf_result.data else []
            if pdf_result.errors:
                errors.extend([e.to_dict() for e in pdf_result.errors])
            warnings.extend(pdf_result.warnings)
        else:
            batch_result = await self.pdf_parser.parse_directory(input_path, self.output_dir / "images")
            pdf_results = batch_result.data if batch_result.success and batch_result.data else []
            if batch_result.errors:
                errors.extend([e.to_dict() for e in batch_result.errors])
            warnings.extend(batch_result.warnings)

        if not pdf_results:
            # Return minimal result if no PDFs processed
            empty_manifest = DocumentManifest(
                project_id=project_id,
                source_directory=str(input_path),
            )
            return IntakeResult(
                project_id=project_id,
                manifest=empty_manifest,
                completeness=self._create_empty_completeness(project_id),
                measurement_scope=self._create_empty_scope(project_id),
                processing_time_ms=(time.time() - start_time) * 1000,
                errors=errors,
                warnings=warnings + ["No PDF documents processed"],
            )

        # Step 2: Extract metadata from text
        self.logger.info(f"[{project_id}] Extracting metadata from {len(pdf_results)} documents")

        all_pages = []
        for pdf in pdf_results:
            for page in pdf.pages:
                all_pages.append({
                    "text": page.text,
                    "page_number": page.page_number,
                    "source": pdf.file_name,
                })

        metadata_result = await self.metadata_extractor.extract_from_pages(all_pages)
        project_metadata = metadata_result.data.metadata if metadata_result.success and metadata_result.data else ProjectMetadata()
        warnings.extend(metadata_result.warnings)

        # Step 3: Enrich location with geocoding
        if project_metadata.location and project_metadata.location.postcode:
            self.logger.info(f"[{project_id}] Geocoding location: {project_metadata.location.postcode}")
            geo_result = await self.geocoder.enrich_location(project_metadata.location)
            if geo_result.success and geo_result.data:
                project_metadata.location = geo_result.data
            warnings.extend(geo_result.warnings)

        # Step 4: Classify drawings using vision
        self.logger.info(f"[{project_id}] Classifying drawings")

        all_drawings: list[DrawingInfo] = []
        document_entries: list[DocumentEntry] = []

        for pdf in pdf_results:
            doc_entry = pdf.to_document_entry()
            doc_drawings: list[DrawingInfo] = []

            # Get image paths for classification
            image_paths = [
                p.extracted_image_path
                for p in pdf.pages
                if p.extracted_image_path
            ]

            if image_paths:
                classify_result = await self.classifier.classify_batch(
                    image_paths,
                    source_file=pdf.file_path,
                )

                if classify_result.success and classify_result.data:
                    for i, classification in enumerate(classify_result.data):
                        drawing_info = classification.to_drawing_info(
                            file_path=pdf.file_path,
                            page_number=i + 1,
                        )
                        # Add image path
                        if i < len(image_paths):
                            drawing_info.image_path = image_paths[i]
                        # Add measurement potential based on type
                        if drawing_info.drawing_type in self.MEASUREMENT_POTENTIAL:
                            drawing_info.measurement_potential = self.MEASUREMENT_POTENTIAL[drawing_info.drawing_type]

                        doc_drawings.append(drawing_info)
                        all_drawings.append(drawing_info)

                warnings.extend(classify_result.warnings)
            else:
                warnings.append(f"No images extracted from {pdf.file_name}")

            doc_entry.drawings = doc_drawings
            document_entries.append(doc_entry)

        # Step 5: Build manifest
        manifest = DocumentManifest(
            project_id=project_id,
            source_directory=str(input_path),
            documents=document_entries,
            metadata=project_metadata,
            total_pages=sum(d.page_count for d in document_entries),
            total_drawings=len(all_drawings),
        )

        # Step 6: Assess completeness
        completeness = self._assess_completeness(project_id, all_drawings, project_metadata)

        # Step 7: Determine measurement scope
        measurement_scope = self._determine_scope(project_id, all_drawings)

        # Step 8: Save outputs
        await self._save_outputs(project_id, manifest, completeness, measurement_scope)

        processing_time = (time.time() - start_time) * 1000
        self.logger.info(f"[{project_id}] Intake analysis complete in {processing_time:.0f}ms")

        return IntakeResult(
            project_id=project_id,
            manifest=manifest,
            completeness=completeness,
            measurement_scope=measurement_scope,
            processing_time_ms=processing_time,
            errors=errors,
            warnings=warnings,
        )

    def _assess_completeness(
        self,
        project_id: str,
        drawings: list[DrawingInfo],
        metadata: ProjectMetadata,
    ) -> CompletenessReport:
        """Assess document package completeness."""
        report = CompletenessReport(project_id=project_id)

        # What drawing types do we have?
        present_types = set(d.drawing_type for d in drawings if d.drawing_type != DrawingType.UNKNOWN)
        report.drawing_types_present = list(present_types)

        # Check for schedules and specifications
        report.schedules_present = DrawingType.SCHEDULE in present_types
        report.specifications_present = DrawingType.SPECIFICATION in present_types

        # What's required for this project type?
        required = set(self.REQUIRED_DRAWINGS.get(self.project_type, self.REQUIRED_DRAWINGS["default"]))

        # What's missing?
        missing_types = required - present_types

        for missing_type in missing_types:
            severity = "critical" if missing_type in {DrawingType.FLOOR_PLAN, DrawingType.SITE_PLAN} else "important"

            impact = self._get_missing_impact(missing_type)

            report.missing_items.append(MissingItem(
                item_type="drawing",
                description=f"{missing_type.value.replace('_', ' ').title()} drawing",
                severity=severity,
                impact=impact,
                recommendation=f"Request {missing_type.value.replace('_', ' ')} from architect",
            ))

        # Check metadata completeness
        if not metadata.project_name:
            report.missing_items.append(MissingItem(
                item_type="metadata",
                description="Project name not identified",
                severity="minor",
                impact="Project identification may be unclear",
                recommendation="Confirm project name with client",
            ))

        if not metadata.location or not metadata.location.postcode:
            report.missing_items.append(MissingItem(
                item_type="metadata",
                description="Site location/postcode not identified",
                severity="important",
                impact="Cannot determine regional pricing factors",
                recommendation="Request site address from client",
            ))

        # Check drawing quality
        low_confidence = [d for d in drawings if d.confidence < 0.5]
        if low_confidence:
            report.warnings.append(
                f"{len(low_confidence)} drawings have low classification confidence - manual review recommended"
            )

        no_dimensions = [d for d in drawings if not d.dimensions_present and d.drawing_type in {
            DrawingType.FLOOR_PLAN, DrawingType.ELEVATION, DrawingType.SECTION
        }]
        if no_dimensions:
            report.warnings.append(
                f"{len(no_dimensions)} key drawings appear to lack dimensions"
            )

        # Calculate completeness percentage
        total_checks = len(required) + 3  # required drawings + metadata checks
        passed_checks = len(required - missing_types)
        if metadata.project_name:
            passed_checks += 1
        if metadata.location and metadata.location.postcode:
            passed_checks += 1
        if metadata.architect:
            passed_checks += 1

        report.overall_completeness_pct = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        # Determine status and recommendation
        critical_missing = [m for m in report.missing_items if m.severity == "critical"]

        if critical_missing:
            report.status = "critical_gaps"
            report.proceed_recommendation = "hold"
            report.hold_reasons = [m.description for m in critical_missing]
        elif report.overall_completeness_pct >= 80:
            report.status = "complete"
            report.proceed_recommendation = "proceed"
        else:
            report.status = "incomplete"
            report.proceed_recommendation = "proceed_with_caution"
            report.hold_reasons = [
                f"Completeness at {report.overall_completeness_pct:.0f}% - some assumptions may be required"
            ]

        return report

    def _get_missing_impact(self, drawing_type: DrawingType) -> str:
        """Get impact description for missing drawing type."""
        impacts = {
            DrawingType.FLOOR_PLAN: "Cannot measure floor areas, partitions, doors, or internal elements",
            DrawingType.SITE_PLAN: "Cannot measure external works, site area, or verify building position",
            DrawingType.ELEVATION: "Cannot measure external wall areas, windows, or cladding",
            DrawingType.SECTION: "Cannot verify floor-to-floor heights or construction build-ups",
            DrawingType.ROOF_PLAN: "Cannot measure roof area or rainwater goods",
            DrawingType.DEMOLITION: "Cannot identify extent of demolition works for refurbishment",
            DrawingType.SCHEDULE: "Must count elements manually from drawings",
            DrawingType.STRUCTURAL: "Cannot verify foundation type or structural frame",
        }
        return impacts.get(drawing_type, "May affect measurement accuracy")

    def _determine_scope(
        self,
        project_id: str,
        drawings: list[DrawingInfo],
    ) -> MeasurementScope:
        """Determine what can be measured from available drawings."""
        scope = MeasurementScope(project_id=project_id)

        # Group drawings by type
        by_type: dict[DrawingType, list[DrawingInfo]] = {}
        for d in drawings:
            if d.drawing_type not in by_type:
                by_type[d.drawing_type] = []
            by_type[d.drawing_type].append(d)

        # Build measurable elements based on available drawings
        for drawing_type, type_drawings in by_type.items():
            if drawing_type == DrawingType.UNKNOWN:
                continue

            potential = self.MEASUREMENT_POTENTIAL.get(drawing_type, [])
            if not potential:
                continue

            # Determine confidence based on drawing quality
            avg_confidence = sum(d.confidence for d in type_drawings) / len(type_drawings)
            has_dimensions = any(d.dimensions_present for d in type_drawings)

            if avg_confidence >= 0.8 and has_dimensions:
                confidence = "high"
            elif avg_confidence >= 0.5 or has_dimensions:
                confidence = "medium"
            else:
                confidence = "low"

            source_drawings = [
                f"{d.drawing_number or 'Page ' + str(d.page_number)}"
                for d in type_drawings
            ]

            notes = []
            if not has_dimensions:
                notes.append("No dimension annotations detected - may need to scale from drawing")
            if avg_confidence < 0.7:
                notes.append("Drawing classification confidence is moderate")

            for element in potential:
                # Map to NRM reference where possible
                nrm_ref = self._get_nrm_reference(element)

                scope.measurable_elements.append(MeasurableElement(
                    element_type=element,
                    nrm_reference=nrm_ref,
                    source_drawings=source_drawings,
                    confidence=confidence,
                    notes=notes,
                ))

        # Identify what cannot be measured
        all_potential = set()
        for potentials in self.MEASUREMENT_POTENTIAL.values():
            all_potential.update(potentials)

        measurable = set(m.element_type for m in scope.measurable_elements)
        unmeasurable = all_potential - measurable

        for element in unmeasurable:
            required_type = None
            for dt, potentials in self.MEASUREMENT_POTENTIAL.items():
                if element in potentials:
                    required_type = dt
                    break

            scope.unmeasurable_elements.append({
                "element": element,
                "reason": f"No {required_type.value.replace('_', ' ') if required_type else 'suitable'} drawing available",
            })

        # Build summary
        high_conf = len([m for m in scope.measurable_elements if m.confidence == "high"])
        med_conf = len([m for m in scope.measurable_elements if m.confidence == "medium"])
        low_conf = len([m for m in scope.measurable_elements if m.confidence == "low"])

        scope.coverage_summary = (
            f"From {len(drawings)} drawings, {len(scope.measurable_elements)} element types can be measured: "
            f"{high_conf} high confidence, {med_conf} medium confidence, {low_conf} low confidence. "
            f"{len(scope.unmeasurable_elements)} element types cannot be measured from available information."
        )

        # Add standard assumptions
        if DrawingType.SECTION not in by_type:
            scope.recommended_assumptions.append(
                "Floor-to-floor height: Assume 3.0m for commercial, 2.7m for residential unless stated"
            )
        if DrawingType.STRUCTURAL not in by_type:
            scope.recommended_assumptions.append(
                "Foundation type: Assume strip foundations for loadbearing masonry, pad foundations for framed buildings"
            )

        return scope

    def _get_nrm_reference(self, element: str) -> Optional[str]:
        """Map measurement element to NRM1/NRM2 reference."""
        # Simplified mapping - would be more comprehensive in production
        nrm_map = {
            "Gross Internal Floor Area (GIFA)": "NRM1 2.6",
            "Net Internal Area (NIA)": "NRM1 2.7",
            "External wall areas": "NRM1 2.5.1",
            "Roof area": "NRM1 2.5.2",
            "Site area": "NRM1 2.1",
            "Window areas and counts": "NRM2 L10/L20",
            "Door areas and counts": "NRM2 L20",
            "Ceiling areas": "NRM2 K10/K40",
            "Floor construction depths": "NRM1 2.4.3",
        }
        return nrm_map.get(element)

    async def _save_outputs(
        self,
        project_id: str,
        manifest: DocumentManifest,
        completeness: CompletenessReport,
        scope: MeasurementScope,
    ) -> None:
        """Save output files."""
        project_dir = self.output_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save manifest as JSON
        manifest_path = project_dir / "project_manifest.json"
        with open(manifest_path, "w") as f:
            f.write(manifest.to_json(indent=2))
        self.logger.info(f"Saved: {manifest_path}")

        # Save completeness report as Markdown
        completeness_path = project_dir / "completeness_report.md"
        with open(completeness_path, "w") as f:
            f.write(completeness.to_markdown())
        self.logger.info(f"Saved: {completeness_path}")

        # Save measurement scope as Markdown
        scope_path = project_dir / "measurement_scope.md"
        with open(scope_path, "w") as f:
            f.write(scope.to_markdown())
        self.logger.info(f"Saved: {scope_path}")

    def _create_empty_completeness(self, project_id: str) -> CompletenessReport:
        """Create empty completeness report."""
        report = CompletenessReport(project_id=project_id)
        report.status = "critical_gaps"
        report.proceed_recommendation = "hold"
        report.hold_reasons = ["No documents processed"]
        return report

    def _create_empty_scope(self, project_id: str) -> MeasurementScope:
        """Create empty measurement scope."""
        scope = MeasurementScope(project_id=project_id)
        scope.coverage_summary = "No drawings available for measurement"
        return scope


async def run_intake(
    input_path: str,
    project_id: Optional[str] = None,
    output_dir: str = "./intake_output",
    project_type: str = "default",
    **kwargs,
) -> IntakeResult:
    """
    Convenience function to run intake analysis.

    Args:
        input_path: Path to PDF file or directory
        project_id: Optional project identifier
        output_dir: Output directory for results
        project_type: Project type for completeness checking
        **kwargs: Additional config options

    Returns:
        IntakeResult
    """
    config = {
        "output_dir": output_dir,
        "project_type": project_type,
        **kwargs,
    }

    analyst = IntakeAnalyst(config)
    return await analyst.analyze(input_path, project_id)
