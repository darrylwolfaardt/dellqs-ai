"""
QS Agents - Quantity Surveying AI Agent Framework.

This package provides AI-powered agents for quantity surveying tasks:
- Orchestrator: Project routing and workflow coordination
- Intake Analyst: Document reception, classification, and completeness checking
- Measure Agent: Quantity take-off from drawings
- Cost Agent: Pricing and rate application
- QA Agent: Quality assurance and validation
- Output Agent: Report generation

Usage:
    from qs_agents.agents import Orchestrator, IntakeAnalyst

    orchestrator = Orchestrator(config)
    result = await orchestrator.start_project("./drawings/")
"""

__version__ = "1.0.0"
__author__ = "Dell QS"

from .agents import (
    IntakeAnalyst,
    IntakeResult,
    Orchestrator,
    OrchestratorResult,
    ProjectType,
    ProjectState,
    WorkflowStatus,
    AutonomyLevel,
    WorkflowDefinition,
)
from .tools import (
    PDFParser,
    DrawingClassifier,
    MetadataExtractor,
    Geocoder,
)

__all__ = [
    # Orchestrator
    "Orchestrator",
    "OrchestratorResult",
    "ProjectType",
    "ProjectState",
    "WorkflowStatus",
    "AutonomyLevel",
    "WorkflowDefinition",
    # Intake Agent
    "IntakeAnalyst",
    "IntakeResult",
    # Tools
    "PDFParser",
    "DrawingClassifier",
    "MetadataExtractor",
    "Geocoder",
]
