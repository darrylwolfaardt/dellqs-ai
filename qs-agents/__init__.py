"""
QS Agents - Quantity Surveying AI Agent Framework.

This package provides AI-powered agents for quantity surveying tasks:
- Intake Analyst: Document reception, classification, and completeness checking
- Measure Agent: Quantity take-off from drawings
- Cost Agent: Pricing and rate application
- QA Agent: Quality assurance and validation
- Output Agent: Report generation

Usage:
    from qs_agents.agents import IntakeAnalyst

    analyst = IntakeAnalyst(config)
    result = await analyst.analyze("./drawings/")
"""

__version__ = "1.0.0"
__author__ = "Dell QS"

from .agents import IntakeAnalyst, IntakeResult
from .tools import (
    PDFParser,
    DrawingClassifier,
    MetadataExtractor,
    Geocoder,
)

__all__ = [
    # Agents
    "IntakeAnalyst",
    "IntakeResult",
    # Tools
    "PDFParser",
    "DrawingClassifier",
    "MetadataExtractor",
    "Geocoder",
]
