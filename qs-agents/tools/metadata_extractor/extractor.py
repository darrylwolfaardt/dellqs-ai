"""Metadata Extractor for extracting project information from documents."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..common.base import BaseTool, ToolResult, ToolStatus, ToolError
from ..common.schemas import ProjectMetadata, LocationInfo


@dataclass
class ExtractionResult:
    """Result of metadata extraction."""
    metadata: ProjectMetadata
    extraction_sources: list[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_text_used: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "extraction_sources": self.extraction_sources,
            "confidence": self.confidence,
        }


class MetadataExtractor(BaseTool):
    """
    Tool for extracting project metadata from document text.

    Uses pattern matching and optional LLM enhancement to extract:
    - Project name and number
    - Client and architect information
    - Location details
    - Dates and revisions
    - Building type and scale
    """

    # Common patterns for metadata extraction
    PATTERNS = {
        "project_name": [
            r"(?:project|scheme|development)[\s:]+([A-Za-z0-9\s\-&,.']+?)(?:\n|$|revision|drawing)",
            r"(?:project title|site)[\s:]+([A-Za-z0-9\s\-&,.']+?)(?:\n|$)",
        ],
        "project_number": [
            r"(?:project|job|ref)[\s\.]*(?:no|number|ref)?[\s:\.]*([A-Z0-9\-/]+)",
            r"(?:^|\s)([A-Z]{2,4}[\-/][0-9]{3,6})(?:\s|$)",
        ],
        "client": [
            r"(?:client|employer|for)[\s:]+([A-Za-z0-9\s\-&,.']+?)(?:\n|$|project)",
        ],
        "architect": [
            r"(?:architect|designed by|drawn by)[\s:]+([A-Za-z0-9\s\-&,.']+?)(?:\n|$)",
            r"(?:^|\n)([A-Za-z\s]+(?:architects?|associates|partnership|llp))(?:\n|$)",
        ],
        "structural_engineer": [
            r"(?:structural|engineer|structures)[\s:]+([A-Za-z0-9\s\-&,.']+?)(?:\n|$)",
        ],
        "postcode": [
            r"([A-Z]{1,2}[0-9][0-9A-Z]?\s*[0-9][A-Z]{2})",  # UK postcode
        ],
        "scale": [
            r"scale[\s:]*([0-9]+\s*:\s*[0-9]+)",
            r"@\s*([0-9]+\s*:\s*[0-9]+)",
            r"(?:^|\s)(1\s*:\s*(?:50|100|200|250|500|1000|1250|2500))(?:\s|$)",
        ],
        "date": [
            r"(?:date|issued|drawn)[\s:]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})",
            r"(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})",
            r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})",
        ],
        "revision": [
            r"(?:rev|revision)[\s:\.]*([A-Z0-9]+)",
            r"(?:^|\s)rev[\s\.]*([A-Z])(?:\s|$)",
        ],
        "stage": [
            r"(?:riba\s+)?stage[\s:]*([0-9])",
            r"(concept|developed design|technical design|construction)",
            r"(planning|tender|construction)",
        ],
        "gia": [
            r"(?:gia|gross internal area|floor area)[\s:]*([0-9,]+(?:\.[0-9]+)?)\s*(?:m2|sqm|m²)",
        ],
        "storeys": [
            r"([0-9]+)\s*(?:storey|story|floor)s?",
            r"(?:^|\s)(basement|ground|\+[0-9]+)(?:\s|$)",
        ],
    }

    # RIBA stage mappings
    RIBA_STAGES = {
        "0": "Strategic Definition",
        "1": "Preparation and Brief",
        "2": "Concept Design",
        "3": "Developed Design",
        "4": "Technical Design",
        "5": "Construction",
        "6": "Handover and Close Out",
        "7": "In Use",
        "concept": "2",
        "developed design": "3",
        "technical design": "4",
        "construction": "5",
        "planning": "3",
        "tender": "4",
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(config)
        self.use_llm_enhancement = config.get("use_llm", False) if config else False
        self.llm_provider = config.get("llm_provider", "anthropic") if config else "anthropic"
        self.llm_model = config.get("llm_model", "claude-3-haiku-20240307") if config else "claude-3-haiku-20240307"

    @property
    def name(self) -> str:
        return "metadata_extractor"

    @property
    def description(self) -> str:
        return "Extracts project metadata (name, client, location, dates) from document text"

    def _extract_pattern(
        self,
        text: str,
        patterns: list[str],
        flags: int = re.IGNORECASE | re.MULTILINE,
    ) -> Optional[str]:
        """Try multiple patterns and return first match."""
        for pattern in patterns:
            match = re.search(pattern, text, flags)
            if match:
                return match.group(1).strip()
        return None

    def _extract_all_matches(
        self,
        text: str,
        patterns: list[str],
        flags: int = re.IGNORECASE | re.MULTILINE,
    ) -> list[str]:
        """Extract all matches from multiple patterns."""
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags):
                value = match.group(1).strip()
                if value and value not in matches:
                    matches.append(value)
        return matches

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats."""
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m/%y",
            "%d-%m-%y",
            "%d %B %Y",
            "%d %b %Y",
            "%B %Y",
            "%b %Y",
        ]

        date_str = date_str.strip()

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def _normalize_stage(self, stage_str: str) -> Optional[str]:
        """Normalize RIBA stage to standard format."""
        stage_str = stage_str.lower().strip()

        if stage_str in self.RIBA_STAGES:
            stage_num = self.RIBA_STAGES[stage_str]
            if stage_num.isdigit():
                return f"RIBA Stage {stage_num}"
            return stage_str

        if stage_str.isdigit() and stage_str in self.RIBA_STAGES:
            return f"RIBA Stage {stage_str}"

        return stage_str.title()

    def _count_storeys(self, text: str) -> Optional[int]:
        """Count number of storeys from text."""
        # Look for explicit count
        match = re.search(r"(\d+)\s*(?:storey|story|floor)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Count floor references
        floors = set()
        floor_patterns = [
            (r"basement", -1),
            (r"ground\s*floor", 0),
            (r"first\s*floor", 1),
            (r"second\s*floor", 2),
            (r"third\s*floor", 3),
            (r"fourth\s*floor", 4),
            (r"fifth\s*floor", 5),
            (r"\+(\d+)", lambda m: int(m.group(1))),
        ]

        for pattern, value in floor_patterns:
            if callable(value):
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    floors.add(value(match))
            elif re.search(pattern, text, re.IGNORECASE):
                floors.add(value)

        if floors:
            return max(floors) - min(floors) + 1

        return None

    def _extract_location(self, text: str) -> LocationInfo:
        """Extract location information from text."""
        location = LocationInfo()

        # Extract postcode
        postcode = self._extract_pattern(text, self.PATTERNS["postcode"])
        if postcode:
            location.postcode = postcode.upper().replace("  ", " ")

        # Try to extract address (lines before postcode)
        if postcode:
            # Find text around postcode
            pattern = r"([A-Za-z0-9\s,\-'\.]+(?:\n[A-Za-z0-9\s,\-'\.]+)*)\s*" + re.escape(postcode)
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                address_lines = match.group(1).strip().split("\n")
                # Clean and join address
                address = ", ".join(line.strip() for line in address_lines if line.strip())
                if address:
                    location.address = f"{address}, {postcode}"

        return location

    def _calculate_confidence(self, metadata: ProjectMetadata) -> float:
        """Calculate extraction confidence based on fields populated."""
        weights = {
            "project_name": 0.20,
            "project_number": 0.10,
            "client_name": 0.10,
            "architect": 0.10,
            "location": 0.15,
            "issue_date": 0.10,
            "stage": 0.05,
            "building_type": 0.10,
            "gross_internal_area_m2": 0.05,
            "storeys": 0.05,
        }

        score = 0.0

        if metadata.project_name:
            score += weights["project_name"]
        if metadata.project_number:
            score += weights["project_number"]
        if metadata.client_name:
            score += weights["client_name"]
        if metadata.architect:
            score += weights["architect"]
        if metadata.location and (metadata.location.postcode or metadata.location.address):
            score += weights["location"]
        if metadata.issue_date:
            score += weights["issue_date"]
        if metadata.stage:
            score += weights["stage"]
        if metadata.building_type:
            score += weights["building_type"]
        if metadata.gross_internal_area_m2:
            score += weights["gross_internal_area_m2"]
        if metadata.storeys:
            score += weights["storeys"]

        return score

    async def execute(
        self,
        text: str,
        source_description: Optional[str] = None,
    ) -> ToolResult[ExtractionResult]:
        """
        Extract metadata from text.

        Args:
            text: Text to extract metadata from
            source_description: Description of text source for tracking

        Returns:
            ToolResult containing ExtractionResult
        """
        import time
        start_time = time.time()

        if not text or not text.strip():
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "EMPTY_INPUT",
                    "No text provided for extraction",
                    recoverable=False,
                )],
            )

        warnings: list[str] = []
        raw_fields: dict[str, str] = {}

        # Extract fields using patterns
        project_name = self._extract_pattern(text, self.PATTERNS["project_name"])
        if project_name:
            raw_fields["project_name"] = project_name

        project_number = self._extract_pattern(text, self.PATTERNS["project_number"])
        if project_number:
            raw_fields["project_number"] = project_number

        client = self._extract_pattern(text, self.PATTERNS["client"])
        if client:
            raw_fields["client"] = client

        architect = self._extract_pattern(text, self.PATTERNS["architect"])
        if architect:
            raw_fields["architect"] = architect

        structural = self._extract_pattern(text, self.PATTERNS["structural_engineer"])
        if structural:
            raw_fields["structural_engineer"] = structural

        # Extract and parse date
        date_str = self._extract_pattern(text, self.PATTERNS["date"])
        issue_date = None
        if date_str:
            raw_fields["date"] = date_str
            issue_date = self._parse_date(date_str)
            if not issue_date:
                warnings.append(f"Could not parse date: {date_str}")

        # Extract stage
        stage_str = self._extract_pattern(text, self.PATTERNS["stage"])
        stage = None
        if stage_str:
            raw_fields["stage"] = stage_str
            stage = self._normalize_stage(stage_str)

        # Extract GIA
        gia_str = self._extract_pattern(text, self.PATTERNS["gia"])
        gia = None
        if gia_str:
            raw_fields["gia"] = gia_str
            try:
                gia = float(gia_str.replace(",", ""))
            except ValueError:
                warnings.append(f"Could not parse GIA: {gia_str}")

        # Extract storeys
        storeys = self._count_storeys(text)
        if storeys:
            raw_fields["storeys"] = str(storeys)

        # Extract location
        location = self._extract_location(text)
        if location.postcode:
            raw_fields["postcode"] = location.postcode

        # Build metadata object
        metadata = ProjectMetadata(
            project_name=project_name,
            project_number=project_number,
            client_name=client,
            architect=architect,
            structural_engineer=structural,
            location=location if location.postcode or location.address else None,
            issue_date=issue_date,
            stage=stage,
            gross_internal_area_m2=gia,
            storeys=storeys,
            raw_extracted_fields=raw_fields,
        )

        # Calculate confidence
        confidence = self._calculate_confidence(metadata)

        result = ExtractionResult(
            metadata=metadata,
            extraction_sources=[source_description] if source_description else [],
            confidence=confidence,
            raw_text_used=text[:500] if len(text) > 500 else text,
        )

        execution_time = (time.time() - start_time) * 1000

        # Determine status
        if confidence < 0.2:
            status = ToolStatus.PARTIAL
            warnings.append("Low extraction confidence - limited metadata found")
        else:
            status = ToolStatus.SUCCESS

        return ToolResult(
            status=status,
            data=result,
            warnings=warnings,
            execution_time_ms=execution_time,
        )

    async def extract_from_pages(
        self,
        pages: list[dict[str, Any]],
    ) -> ToolResult[ExtractionResult]:
        """
        Extract metadata from multiple page texts, merging results.

        Args:
            pages: List of dicts with 'text' and optionally 'page_number'

        Returns:
            ToolResult containing merged ExtractionResult
        """
        import time
        start_time = time.time()

        if not pages:
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "EMPTY_INPUT",
                    "No pages provided",
                    recoverable=False,
                )],
            )

        # Combine text from all pages
        combined_text = "\n\n".join(
            p.get("text", "") for p in pages if p.get("text")
        )

        # Also try to find metadata in first few pages (title blocks)
        priority_text = "\n\n".join(
            p.get("text", "") for p in pages[:3] if p.get("text")
        )

        # Extract from priority pages first
        result = await self.execute(
            priority_text,
            source_description="First 3 pages (title blocks)",
        )

        # If low confidence, try full document
        if result.success and result.data and result.data.confidence < 0.5:
            full_result = await self.execute(
                combined_text,
                source_description="Full document",
            )

            if full_result.success and full_result.data:
                # Merge results, preferring priority extraction for key fields
                priority_meta = result.data.metadata
                full_meta = full_result.data.metadata

                # Use priority values if available, else fall back to full
                merged = ProjectMetadata(
                    project_name=priority_meta.project_name or full_meta.project_name,
                    project_number=priority_meta.project_number or full_meta.project_number,
                    client_name=priority_meta.client_name or full_meta.client_name,
                    architect=priority_meta.architect or full_meta.architect,
                    structural_engineer=priority_meta.structural_engineer or full_meta.structural_engineer,
                    location=priority_meta.location or full_meta.location,
                    issue_date=priority_meta.issue_date or full_meta.issue_date,
                    stage=priority_meta.stage or full_meta.stage,
                    building_type=priority_meta.building_type or full_meta.building_type,
                    gross_internal_area_m2=priority_meta.gross_internal_area_m2 or full_meta.gross_internal_area_m2,
                    storeys=priority_meta.storeys or full_meta.storeys,
                    raw_extracted_fields={
                        **full_meta.raw_extracted_fields,
                        **priority_meta.raw_extracted_fields,
                    },
                )

                confidence = self._calculate_confidence(merged)

                result = ToolResult(
                    status=ToolStatus.SUCCESS if confidence >= 0.2 else ToolStatus.PARTIAL,
                    data=ExtractionResult(
                        metadata=merged,
                        extraction_sources=["First 3 pages", "Full document"],
                        confidence=confidence,
                    ),
                    warnings=result.warnings + full_result.warnings,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

        return result
