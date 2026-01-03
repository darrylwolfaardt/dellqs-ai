"""Data schemas for QS Agent tools."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import json


class DrawingType(Enum):
    """Classification of architectural/engineering drawings."""
    FLOOR_PLAN = "floor_plan"
    SITE_PLAN = "site_plan"
    ELEVATION = "elevation"
    SECTION = "section"
    DETAIL = "detail"
    SCHEDULE = "schedule"
    SPECIFICATION = "specification"
    ROOF_PLAN = "roof_plan"
    REFLECTED_CEILING = "reflected_ceiling"
    STRUCTURAL = "structural"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    LANDSCAPE = "landscape"
    DEMOLITION = "demolition"
    COVER_SHEET = "cover_sheet"
    LEGEND = "legend"
    UNKNOWN = "unknown"


class DocumentStatus(Enum):
    """Status of a document in the package."""
    PRESENT = "present"
    MISSING = "missing"
    INCOMPLETE = "incomplete"
    SUPERSEDED = "superseded"


@dataclass
class DrawingInfo:
    """Information extracted from a single drawing."""
    file_path: str
    page_number: int
    drawing_type: DrawingType
    drawing_number: Optional[str] = None
    drawing_title: Optional[str] = None
    revision: Optional[str] = None
    revision_date: Optional[datetime] = None
    scale: Optional[str] = None
    dimensions_present: bool = False
    annotations_present: bool = False
    confidence: float = 0.0  # Classification confidence 0-1
    extracted_text: Optional[str] = None
    image_path: Optional[str] = None  # Path to extracted image for vision processing
    measurement_potential: list[str] = field(default_factory=list)  # What can be measured
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "page_number": self.page_number,
            "drawing_type": self.drawing_type.value,
            "drawing_number": self.drawing_number,
            "drawing_title": self.drawing_title,
            "revision": self.revision,
            "revision_date": self.revision_date.isoformat() if self.revision_date else None,
            "scale": self.scale,
            "dimensions_present": self.dimensions_present,
            "annotations_present": self.annotations_present,
            "confidence": self.confidence,
            "measurement_potential": self.measurement_potential,
            "notes": self.notes,
        }


@dataclass
class LocationInfo:
    """Geographic location information."""
    address: Optional[str] = None
    postcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    local_authority: Optional[str] = None
    region: Optional[str] = None
    country: str = "UK"
    what3words: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "address": self.address,
            "postcode": self.postcode,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "local_authority": self.local_authority,
            "region": self.region,
            "country": self.country,
            "what3words": self.what3words,
        }


@dataclass
class ProjectMetadata:
    """Extracted project metadata."""
    project_name: Optional[str] = None
    project_number: Optional[str] = None
    client_name: Optional[str] = None
    architect: Optional[str] = None
    architect_reference: Optional[str] = None
    structural_engineer: Optional[str] = None
    location: Optional[LocationInfo] = None
    issue_date: Optional[datetime] = None
    stage: Optional[str] = None  # RIBA stage or equivalent
    building_type: Optional[str] = None
    gross_internal_area_m2: Optional[float] = None
    storeys: Optional[int] = None
    procurement_route: Optional[str] = None
    contract_type: Optional[str] = None
    raw_extracted_fields: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "project_number": self.project_number,
            "client_name": self.client_name,
            "architect": self.architect,
            "architect_reference": self.architect_reference,
            "structural_engineer": self.structural_engineer,
            "location": self.location.to_dict() if self.location else None,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "stage": self.stage,
            "building_type": self.building_type,
            "gross_internal_area_m2": self.gross_internal_area_m2,
            "storeys": self.storeys,
            "procurement_route": self.procurement_route,
            "contract_type": self.contract_type,
            "raw_extracted_fields": self.raw_extracted_fields,
        }


@dataclass
class DocumentEntry:
    """Entry in the document manifest."""
    file_name: str
    file_path: str
    file_type: str
    file_size_bytes: int
    page_count: int
    drawings: list[DrawingInfo] = field(default_factory=list)
    status: DocumentStatus = DocumentStatus.PRESENT
    hash_md5: Optional[str] = None
    received_date: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size_bytes": self.file_size_bytes,
            "page_count": self.page_count,
            "drawings": [d.to_dict() for d in self.drawings],
            "status": self.status.value,
            "hash_md5": self.hash_md5,
            "received_date": self.received_date.isoformat(),
        }


@dataclass
class DocumentManifest:
    """Complete manifest of received documents - project_manifest.json output."""
    project_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    source_directory: Optional[str] = None
    documents: list[DocumentEntry] = field(default_factory=list)
    metadata: Optional[ProjectMetadata] = None
    total_pages: int = 0
    total_drawings: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
            "source_directory": self.source_directory,
            "documents": [d.to_dict() for d in self.documents],
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "total_pages": self.total_pages,
            "total_drawings": self.total_drawings,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


@dataclass
class MissingItem:
    """An item identified as missing from the document package."""
    item_type: str  # e.g., "drawing", "specification", "schedule"
    description: str
    severity: str  # "critical", "important", "minor"
    impact: str  # How this affects measurement/costing
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_type": self.item_type,
            "description": self.description,
            "severity": self.severity,
            "impact": self.impact,
            "recommendation": self.recommendation,
        }


@dataclass
class CompletenessReport:
    """Report on document package completeness - completeness_report.md output."""
    project_id: str
    assessment_date: datetime = field(default_factory=datetime.utcnow)
    overall_completeness_pct: float = 0.0
    status: str = "incomplete"  # "complete", "incomplete", "critical_gaps"

    # What we have
    drawing_types_present: list[DrawingType] = field(default_factory=list)
    specifications_present: bool = False
    schedules_present: bool = False

    # What's missing
    missing_items: list[MissingItem] = field(default_factory=list)

    # Warnings and notes
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    # Recommendation
    proceed_recommendation: str = "hold"  # "proceed", "proceed_with_caution", "hold"
    hold_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "assessment_date": self.assessment_date.isoformat(),
            "overall_completeness_pct": self.overall_completeness_pct,
            "status": self.status,
            "drawing_types_present": [dt.value for dt in self.drawing_types_present],
            "specifications_present": self.specifications_present,
            "schedules_present": self.schedules_present,
            "missing_items": [m.to_dict() for m in self.missing_items],
            "warnings": self.warnings,
            "notes": self.notes,
            "proceed_recommendation": self.proceed_recommendation,
            "hold_reasons": self.hold_reasons,
        }

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            f"# Completeness Report",
            f"",
            f"**Project ID:** {self.project_id}",
            f"**Assessment Date:** {self.assessment_date.strftime('%Y-%m-%d %H:%M')}",
            f"**Overall Completeness:** {self.overall_completeness_pct:.0f}%",
            f"**Status:** {self.status.replace('_', ' ').title()}",
            f"",
            f"## Recommendation",
            f"",
            f"**{self.proceed_recommendation.replace('_', ' ').title()}**",
            f"",
        ]

        if self.hold_reasons:
            lines.append("### Reasons")
            for reason in self.hold_reasons:
                lines.append(f"- {reason}")
            lines.append("")

        lines.extend([
            f"## Documents Received",
            f"",
            f"### Drawing Types Present",
        ])

        if self.drawing_types_present:
            for dt in self.drawing_types_present:
                lines.append(f"- ✓ {dt.value.replace('_', ' ').title()}")
        else:
            lines.append("- None identified")

        lines.extend([
            f"",
            f"- Specifications: {'✓ Present' if self.specifications_present else '✗ Missing'}",
            f"- Schedules: {'✓ Present' if self.schedules_present else '✗ Missing'}",
            f"",
        ])

        if self.missing_items:
            lines.extend([
                f"## Missing Items",
                f"",
            ])

            critical = [m for m in self.missing_items if m.severity == "critical"]
            important = [m for m in self.missing_items if m.severity == "important"]
            minor = [m for m in self.missing_items if m.severity == "minor"]

            if critical:
                lines.append("### Critical (Blocks Measurement)")
                for item in critical:
                    lines.extend([
                        f"",
                        f"**{item.description}**",
                        f"- Impact: {item.impact}",
                        f"- Recommendation: {item.recommendation}",
                    ])
                lines.append("")

            if important:
                lines.append("### Important (Affects Accuracy)")
                for item in important:
                    lines.extend([
                        f"",
                        f"**{item.description}**",
                        f"- Impact: {item.impact}",
                        f"- Recommendation: {item.recommendation}",
                    ])
                lines.append("")

            if minor:
                lines.append("### Minor (Nice to Have)")
                for item in minor:
                    lines.append(f"- {item.description}")
                lines.append("")

        if self.warnings:
            lines.extend([
                f"## Warnings",
                f"",
            ])
            for warning in self.warnings:
                lines.append(f"⚠️ {warning}")
            lines.append("")

        if self.notes:
            lines.extend([
                f"## Notes",
                f"",
            ])
            for note in self.notes:
                lines.append(f"- {note}")

        return "\n".join(lines)


@dataclass
class MeasurableElement:
    """An element that can be measured from available drawings."""
    element_type: str  # e.g., "floor_area", "wall_length", "door_schedule"
    nrm_reference: Optional[str] = None  # NRM1/NRM2 reference
    source_drawings: list[str] = field(default_factory=list)
    confidence: str = "medium"  # "high", "medium", "low"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "element_type": self.element_type,
            "nrm_reference": self.nrm_reference,
            "source_drawings": self.source_drawings,
            "confidence": self.confidence,
            "notes": self.notes,
        }


@dataclass
class MeasurementScope:
    """Scope of what can be measured - measurement_scope.md output."""
    project_id: str
    assessment_date: datetime = field(default_factory=datetime.utcnow)

    # Elements that can be measured
    measurable_elements: list[MeasurableElement] = field(default_factory=list)

    # Elements that cannot be measured (and why)
    unmeasurable_elements: list[dict[str, str]] = field(default_factory=list)

    # Summary
    coverage_summary: str = ""
    recommended_assumptions: list[str] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "assessment_date": self.assessment_date.isoformat(),
            "measurable_elements": [m.to_dict() for m in self.measurable_elements],
            "unmeasurable_elements": self.unmeasurable_elements,
            "coverage_summary": self.coverage_summary,
            "recommended_assumptions": self.recommended_assumptions,
            "exclusions": self.exclusions,
        }

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            f"# Measurement Scope",
            f"",
            f"**Project ID:** {self.project_id}",
            f"**Assessment Date:** {self.assessment_date.strftime('%Y-%m-%d %H:%M')}",
            f"",
            f"## Summary",
            f"",
            f"{self.coverage_summary}",
            f"",
            f"## Measurable Elements",
            f"",
        ]

        if self.measurable_elements:
            # Group by confidence
            high = [m for m in self.measurable_elements if m.confidence == "high"]
            medium = [m for m in self.measurable_elements if m.confidence == "medium"]
            low = [m for m in self.measurable_elements if m.confidence == "low"]

            if high:
                lines.append("### High Confidence")
                lines.append("| Element | NRM Ref | Source Drawings |")
                lines.append("|---------|---------|-----------------|")
                for elem in high:
                    sources = ", ".join(elem.source_drawings[:3])
                    if len(elem.source_drawings) > 3:
                        sources += f" (+{len(elem.source_drawings)-3} more)"
                    lines.append(f"| {elem.element_type} | {elem.nrm_reference or '-'} | {sources} |")
                lines.append("")

            if medium:
                lines.append("### Medium Confidence")
                lines.append("| Element | NRM Ref | Notes |")
                lines.append("|---------|---------|-------|")
                for elem in medium:
                    notes = "; ".join(elem.notes) if elem.notes else "-"
                    lines.append(f"| {elem.element_type} | {elem.nrm_reference or '-'} | {notes} |")
                lines.append("")

            if low:
                lines.append("### Low Confidence (Requires Assumptions)")
                for elem in low:
                    lines.append(f"- **{elem.element_type}**")
                    for note in elem.notes:
                        lines.append(f"  - {note}")
                lines.append("")
        else:
            lines.append("*No elements identified for measurement*")
            lines.append("")

        if self.unmeasurable_elements:
            lines.extend([
                f"## Cannot Be Measured",
                f"",
            ])
            for item in self.unmeasurable_elements:
                lines.append(f"- **{item.get('element', 'Unknown')}**: {item.get('reason', 'No reason given')}")
            lines.append("")

        if self.recommended_assumptions:
            lines.extend([
                f"## Recommended Assumptions",
                f"",
            ])
            for assumption in self.recommended_assumptions:
                lines.append(f"- {assumption}")
            lines.append("")

        if self.exclusions:
            lines.extend([
                f"## Exclusions",
                f"",
            ])
            for exclusion in self.exclusions:
                lines.append(f"- {exclusion}")

        return "\n".join(lines)
