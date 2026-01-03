"""Drawing Classifier using vision models to identify architectural drawing types."""

import base64
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..common.base import BaseTool, ToolResult, ToolStatus, ToolError
from ..common.schemas import DrawingType, DrawingInfo


CLASSIFICATION_PROMPT = """You are an expert architectural drawing analyst. Analyze this drawing image and provide a detailed classification.

Identify the following:

1. **Drawing Type** - Classify as one of:
   - floor_plan: Shows layout of rooms, walls, doors, windows from above
   - site_plan: Shows building footprint on land, boundaries, access
   - elevation: Shows vertical face of building exterior
   - section: Shows cut-through view of building
   - detail: Shows enlarged view of specific construction element
   - schedule: Table/list of items (doors, windows, finishes)
   - specification: Written specifications or notes
   - roof_plan: Shows roof layout from above
   - reflected_ceiling: Shows ceiling layout looking up
   - structural: Shows structural elements (beams, columns, foundations)
   - mechanical: Shows HVAC systems
   - electrical: Shows electrical systems
   - plumbing: Shows plumbing systems
   - landscape: Shows external landscaping
   - demolition: Shows elements to be removed
   - cover_sheet: Title page or project information
   - legend: Key/legend for symbols
   - unknown: Cannot determine

2. **Drawing Number** - Extract any drawing reference number visible

3. **Drawing Title** - Extract the title if visible

4. **Revision** - Extract revision letter/number if visible

5. **Scale** - Extract scale notation (e.g., "1:100", "1:50")

6. **Dimensions Present** - Are dimension annotations visible? (true/false)

7. **Annotations Present** - Are text annotations/notes visible? (true/false)

8. **Confidence** - How confident are you in this classification? (0.0 to 1.0)

9. **Measurement Potential** - What quantities could be measured from this drawing?
   Examples: "floor areas", "wall lengths", "door counts", "window sizes"

10. **Notes** - Any relevant observations about the drawing quality or content

Respond in JSON format:
```json
{
  "drawing_type": "floor_plan",
  "drawing_number": "A-101",
  "drawing_title": "Ground Floor Plan",
  "revision": "C",
  "scale": "1:100",
  "dimensions_present": true,
  "annotations_present": true,
  "confidence": 0.95,
  "measurement_potential": ["floor areas", "room dimensions", "door positions", "wall lengths"],
  "notes": ["Clear dimension strings", "North arrow present", "Good print quality"]
}
```"""


@dataclass
class ClassificationResult:
    """Result of classifying a single drawing."""
    drawing_type: DrawingType
    drawing_number: Optional[str] = None
    drawing_title: Optional[str] = None
    revision: Optional[str] = None
    scale: Optional[str] = None
    dimensions_present: bool = False
    annotations_present: bool = False
    confidence: float = 0.0
    measurement_potential: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    raw_response: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "drawing_type": self.drawing_type.value,
            "drawing_number": self.drawing_number,
            "drawing_title": self.drawing_title,
            "revision": self.revision,
            "scale": self.scale,
            "dimensions_present": self.dimensions_present,
            "annotations_present": self.annotations_present,
            "confidence": self.confidence,
            "measurement_potential": self.measurement_potential,
            "notes": self.notes,
        }

    def to_drawing_info(self, file_path: str, page_number: int) -> DrawingInfo:
        """Convert to DrawingInfo schema."""
        return DrawingInfo(
            file_path=file_path,
            page_number=page_number,
            drawing_type=self.drawing_type,
            drawing_number=self.drawing_number,
            drawing_title=self.drawing_title,
            revision=self.revision,
            scale=self.scale,
            dimensions_present=self.dimensions_present,
            annotations_present=self.annotations_present,
            confidence=self.confidence,
            measurement_potential=self.measurement_potential,
            notes=self.notes,
        )


class DrawingClassifier(BaseTool):
    """
    Tool for classifying architectural drawings using vision models.

    Uses Claude Code CLI for vision classification, leveraging the authenticated
    Claude Code session rather than requiring separate API keys.

    Falls back to direct Anthropic/OpenAI API if configured with api_key.
    """

    SUPPORTED_PROVIDERS = ["claude", "anthropic", "openai"]

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(config)
        self.provider = config.get("provider", "claude") if config else "claude"
        self.model = config.get("model", "claude-sonnet-4-20250514") if config else "claude-sonnet-4-20250514"
        self.api_key = config.get("api_key") if config else None
        self._client = None

        # If no API key provided and provider is anthropic, default to claude (CLI)
        if self.provider == "anthropic" and not self.api_key:
            self.provider = "claude"

    @property
    def name(self) -> str:
        return "drawing_classifier"

    @property
    def description(self) -> str:
        return "Classifies architectural drawings using vision AI to identify drawing types and extract metadata"

    async def health_check(self) -> bool:
        """Check if the vision API is accessible."""
        if self.provider == "claude":
            # Check if claude CLI is available
            try:
                result = subprocess.run(
                    ["claude", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                self.logger.warning("claude CLI not found or not accessible")
                return False
        elif self.provider == "anthropic":
            try:
                import anthropic
                return True
            except ImportError:
                self.logger.warning("anthropic package not installed")
                return False
        elif self.provider == "openai":
            try:
                import openai
                return True
            except ImportError:
                self.logger.warning("openai package not installed")
                return False
        return False

    def _get_client(self):
        """Get or create the API client."""
        if self._client is not None:
            return self._client

        if self.provider == "anthropic":
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == "openai":
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)

        return self._client

    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        """Encode image to base64 and determine media type."""
        suffix = image_path.suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_types.get(suffix, "image/png")

        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        return image_data, media_type

    def _parse_response(self, response_text: str) -> ClassificationResult:
        """Parse the model response into a ClassificationResult."""
        # Try to extract JSON from response
        json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Return unknown classification
                return ClassificationResult(
                    drawing_type=DrawingType.UNKNOWN,
                    confidence=0.0,
                    notes=["Failed to parse model response"],
                    raw_response=response_text,
                )

        try:
            data = json.loads(json_str)

            # Map drawing type string to enum
            drawing_type_str = data.get("drawing_type", "unknown").lower()
            try:
                drawing_type = DrawingType(drawing_type_str)
            except ValueError:
                drawing_type = DrawingType.UNKNOWN

            return ClassificationResult(
                drawing_type=drawing_type,
                drawing_number=data.get("drawing_number"),
                drawing_title=data.get("drawing_title"),
                revision=data.get("revision"),
                scale=data.get("scale"),
                dimensions_present=data.get("dimensions_present", False),
                annotations_present=data.get("annotations_present", False),
                confidence=float(data.get("confidence", 0.5)),
                measurement_potential=data.get("measurement_potential", []),
                notes=data.get("notes", []),
                raw_response=response_text,
            )

        except json.JSONDecodeError as e:
            return ClassificationResult(
                drawing_type=DrawingType.UNKNOWN,
                confidence=0.0,
                notes=[f"JSON parse error: {e}"],
                raw_response=response_text,
            )

    async def _classify_with_claude(self, image_path: Path) -> str:
        """Classify using Claude Code CLI.

        Uses the authenticated Claude Code session to analyze images,
        avoiding the need for separate API keys.
        """
        # Build the prompt with the image path
        prompt = f"""Please analyze this architectural drawing image at: {image_path}

{CLASSIFICATION_PROMPT}"""

        try:
            # Use claude CLI with the image
            # The --print flag outputs only the response without interactive elements
            result = subprocess.run(
                [
                    "claude",
                    "--print",
                    "--allowedTools", "Read",  # Allow reading the image file
                    "-p", prompt,
                    str(image_path),
                ],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for vision analysis
                cwd=str(image_path.parent),
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude CLI failed: {result.stderr}")

            return result.stdout

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude CLI timed out during image classification")
        except FileNotFoundError:
            raise RuntimeError("Claude CLI not found. Ensure 'claude' is installed and in PATH.")

    async def _classify_with_anthropic(self, image_path: Path) -> str:
        """Classify using Anthropic Claude Vision API directly."""
        import anthropic

        client = self._get_client()
        image_data, media_type = self._encode_image(image_path)

        message = client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": CLASSIFICATION_PROMPT,
                        },
                    ],
                }
            ],
        )

        return message.content[0].text

    async def _classify_with_openai(self, image_path: Path) -> str:
        """Classify using OpenAI GPT-4 Vision."""
        client = self._get_client()
        image_data, media_type = self._encode_image(image_path)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": CLASSIFICATION_PROMPT,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=1024,
        )

        return response.choices[0].message.content

    async def execute(
        self,
        image_path: str | Path,
        source_file: Optional[str] = None,
        page_number: int = 1,
    ) -> ToolResult[ClassificationResult]:
        """
        Classify a single drawing image.

        Args:
            image_path: Path to the drawing image
            source_file: Original source file path (for tracking)
            page_number: Page number in source document

        Returns:
            ToolResult containing ClassificationResult
        """
        import time
        start_time = time.time()

        image_path = Path(image_path)

        # Validate input
        if not image_path.exists():
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "FILE_NOT_FOUND",
                    f"Image not found: {image_path}",
                    recoverable=False,
                )],
            )

        valid_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
        if image_path.suffix.lower() not in valid_extensions:
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "INVALID_FORMAT",
                    f"Unsupported image format: {image_path.suffix}",
                    recoverable=False,
                )],
            )

        try:
            # Call appropriate provider
            if self.provider == "claude":
                response_text = await self._classify_with_claude(image_path)
            elif self.provider == "anthropic":
                response_text = await self._classify_with_anthropic(image_path)
            elif self.provider == "openai":
                response_text = await self._classify_with_openai(image_path)
            else:
                return ToolResult(
                    status=ToolStatus.FAILED,
                    errors=[self._create_error(
                        "INVALID_PROVIDER",
                        f"Unsupported provider: {self.provider}",
                        recoverable=False,
                    )],
                )

            # Parse response
            result = self._parse_response(response_text)

            execution_time = (time.time() - start_time) * 1000

            # Determine status based on confidence
            if result.drawing_type == DrawingType.UNKNOWN:
                status = ToolStatus.PARTIAL
                warnings = ["Could not confidently classify drawing"]
            elif result.confidence < 0.5:
                status = ToolStatus.PARTIAL
                warnings = [f"Low confidence classification: {result.confidence:.2f}"]
            else:
                status = ToolStatus.SUCCESS
                warnings = []

            return ToolResult(
                status=status,
                data=result,
                warnings=warnings,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            self.logger.error(f"Classification failed for {image_path}: {e}")
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "CLASSIFICATION_ERROR",
                    f"Failed to classify drawing: {str(e)}",
                    recoverable=True,
                    details={"exception": str(type(e).__name__)},
                )],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def classify_batch(
        self,
        image_paths: list[str | Path],
        source_file: Optional[str] = None,
    ) -> ToolResult[list[ClassificationResult]]:
        """
        Classify multiple drawing images.

        Args:
            image_paths: List of paths to drawing images
            source_file: Original source file path

        Returns:
            ToolResult containing list of ClassificationResult
        """
        import time
        start_time = time.time()

        results: list[ClassificationResult] = []
        errors: list[ToolError] = []
        warnings: list[str] = []

        for i, image_path in enumerate(image_paths):
            result = await self.execute(
                image_path,
                source_file=source_file,
                page_number=i + 1,
            )

            if result.success and result.data:
                results.append(result.data)
            else:
                errors.extend(result.errors)
                # Add placeholder for failed classification
                results.append(ClassificationResult(
                    drawing_type=DrawingType.UNKNOWN,
                    confidence=0.0,
                    notes=["Classification failed"],
                ))

            warnings.extend(result.warnings)

        execution_time = (time.time() - start_time) * 1000

        return ToolResult(
            status=ToolStatus.SUCCESS if not errors else ToolStatus.PARTIAL,
            data=results,
            errors=errors,
            warnings=warnings,
            execution_time_ms=execution_time,
        )
