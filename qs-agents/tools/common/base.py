"""Base classes for QS Agent tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Generic, TypeVar, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ToolStatus(Enum):
    """Status of a tool execution."""
    SUCCESS = "success"
    PARTIAL = "partial"  # Some results, but with warnings
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ToolError:
    """Represents an error encountered during tool execution."""
    code: str
    message: str
    recoverable: bool = True
    details: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "recoverable": self.recoverable,
            "details": self.details,
        }


@dataclass
class ToolResult(Generic[T]):
    """Generic result wrapper for tool outputs."""
    status: ToolStatus
    data: Optional[T] = None
    errors: list[ToolError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def success(self) -> bool:
        return self.status in (ToolStatus.SUCCESS, ToolStatus.PARTIAL)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "data": self.data if not hasattr(self.data, "to_dict") else self.data.to_dict(),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseTool(ABC):
    """Abstract base class for all QS Agent tools."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of tool capability."""
        pass

    @property
    def version(self) -> str:
        """Tool version."""
        return "1.0.0"

    @abstractmethod
    async def execute(self, *args, **kwargs) -> ToolResult:
        """Execute the tool's primary function."""
        pass

    async def validate_input(self, *args, **kwargs) -> list[ToolError]:
        """Validate inputs before execution. Override in subclasses."""
        return []

    async def health_check(self) -> bool:
        """Check if the tool is operational. Override for tools with dependencies."""
        return True

    def _create_error(
        self,
        code: str,
        message: str,
        recoverable: bool = True,
        details: Optional[dict] = None,
    ) -> ToolError:
        """Helper to create consistent error objects."""
        return ToolError(
            code=f"{self.name.upper()}_{code}",
            message=message,
            recoverable=recoverable,
            details=details,
        )
