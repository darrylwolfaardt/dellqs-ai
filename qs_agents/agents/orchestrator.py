"""
Orchestrator Agent Implementation.

The Orchestrator is the entry point for all QS projects. It:
1. Receives project briefs and documents
2. Classifies the project type
3. Determines the appropriate workflow
4. Coordinates specialist agents
5. Tracks project status and escalates when needed

Principles:
- Classify before delegate
- Never let ambiguous scope proceed without clarification
- Track all active projects and their status
- Escalate novel situations rather than guess
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Callable, Awaitable

from .intake_analyst import IntakeAnalyst, IntakeResult
from .measure import MeasureAgent, MeasureResult

logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Types of QS projects."""
    NEW_BUILD_RESIDENTIAL = "new_build_residential"
    NEW_BUILD_COMMERCIAL = "new_build_commercial"
    REFURBISHMENT = "refurbishment"
    TENDER_REVIEW = "tender_review"
    VARIATION_ASSESSMENT = "variation_assessment"
    UNKNOWN = "unknown"


class AutonomyLevel(Enum):
    """Autonomy levels for agent operations."""
    LEVEL_1_SUGGEST = "level_1_suggest"      # Agent suggests, human decides
    LEVEL_2_CONFIRM = "level_2_confirm"      # Agent acts, human confirms before external output
    LEVEL_3_NOTIFY = "level_3_notify"        # Agent acts autonomously, notifies human


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"
    FAILED = "failed"
    ON_HOLD = "on_hold"


class AgentStatus(Enum):
    """Status of individual agent execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentExecution:
    """Tracks execution of a single agent in the workflow."""
    agent_name: str
    status: AgentStatus = AgentStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


@dataclass
class WorkflowDefinition:
    """Defines a workflow for a project type."""
    project_type: ProjectType
    agents: list[str]
    autonomy: AutonomyLevel
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_type": self.project_type.value,
            "agents": self.agents,
            "autonomy": self.autonomy.value,
            "description": self.description,
        }


@dataclass
class ProjectState:
    """Tracks the state of a project through the workflow."""
    project_id: str
    project_type: ProjectType
    workflow: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_agent_index: int = 0
    agent_executions: list[AgentExecution] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Data passed between agents
    intake_result: Optional[IntakeResult] = None
    measure_result: Optional[Any] = None
    cost_result: Optional[Any] = None
    qa_result: Optional[Any] = None
    output_result: Optional[Any] = None

    # Flags and escalations
    escalations: list[dict[str, Any]] = field(default_factory=list)
    human_decisions_required: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_type": self.project_type.value,
            "workflow": self.workflow.to_dict(),
            "status": self.status.value,
            "current_agent_index": self.current_agent_index,
            "agent_executions": [e.to_dict() for e in self.agent_executions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "escalations": self.escalations,
            "human_decisions_required": self.human_decisions_required,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class OrchestratorResult:
    """Result of orchestrator execution."""
    project_id: str
    project_type: ProjectType
    status: WorkflowStatus
    workflow_completed: bool
    agents_run: list[str]
    agents_pending: list[str]
    intake_result: Optional[IntakeResult] = None
    escalations: list[dict[str, Any]] = field(default_factory=list)
    human_decisions_required: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    processing_time_ms: float = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_type": self.project_type.value,
            "status": self.status.value,
            "workflow_completed": self.workflow_completed,
            "agents_run": self.agents_run,
            "agents_pending": self.agents_pending,
            "escalations": self.escalations,
            "human_decisions_required": self.human_decisions_required,
            "errors": self.errors,
            "warnings": self.warnings,
            "processing_time_ms": self.processing_time_ms,
        }


class Orchestrator:
    """
    Orchestrator Agent - Senior Partner coordinating all QS work.

    The Orchestrator is responsible for:
    1. Classifying incoming projects
    2. Selecting the appropriate workflow
    3. Coordinating specialist agents
    4. Tracking project status
    5. Escalating when needed

    Principles:
    - Classify before delegate
    - Never let ambiguous scope proceed without clarification
    - Track all active projects and their status
    - Escalate novel situations rather than guess
    """

    # Workflow definitions for each project type
    WORKFLOWS: dict[ProjectType, WorkflowDefinition] = {
        ProjectType.NEW_BUILD_RESIDENTIAL: WorkflowDefinition(
            project_type=ProjectType.NEW_BUILD_RESIDENTIAL,
            agents=["intake", "measure", "cost", "output"],
            autonomy=AutonomyLevel.LEVEL_2_CONFIRM,
            description="Standard new build residential workflow",
        ),
        ProjectType.NEW_BUILD_COMMERCIAL: WorkflowDefinition(
            project_type=ProjectType.NEW_BUILD_COMMERCIAL,
            agents=["intake", "context_enricher", "measure", "cost", "qa", "output"],
            autonomy=AutonomyLevel.LEVEL_2_CONFIRM,
            description="Commercial new build with QA gate",
        ),
        ProjectType.REFURBISHMENT: WorkflowDefinition(
            project_type=ProjectType.REFURBISHMENT,
            agents=["intake", "context_enricher", "measure", "cost", "qa", "output"],
            autonomy=AutonomyLevel.LEVEL_1_SUGGEST,  # Higher risk, more unknowns
            description="Refurbishment with additional oversight",
        ),
        ProjectType.TENDER_REVIEW: WorkflowDefinition(
            project_type=ProjectType.TENDER_REVIEW,
            agents=["intake", "cost", "qa", "output"],
            autonomy=AutonomyLevel.LEVEL_2_CONFIRM,
            description="Tender review - skip measurement",
        ),
        ProjectType.VARIATION_ASSESSMENT: WorkflowDefinition(
            project_type=ProjectType.VARIATION_ASSESSMENT,
            agents=["intake", "measure", "cost", "output"],
            autonomy=AutonomyLevel.LEVEL_3_NOTIFY,  # Usually quick turnaround
            description="Variation assessment - fast track",
        ),
    }

    # Keywords for project type classification
    PROJECT_TYPE_KEYWORDS = {
        ProjectType.NEW_BUILD_RESIDENTIAL: [
            "residential", "house", "dwelling", "apartment", "flat",
            "home", "housing", "villa", "cottage", "bungalow",
        ],
        ProjectType.NEW_BUILD_COMMERCIAL: [
            "commercial", "office", "retail", "warehouse", "industrial",
            "factory", "hotel", "hospital", "school", "university",
            "shopping", "mall", "mixed-use", "mixed use",
        ],
        ProjectType.REFURBISHMENT: [
            "refurbishment", "refurb", "renovation", "alteration",
            "conversion", "fit-out", "fitout", "fit out", "remodel",
            "upgrade", "modernisation", "modernization", "retrofit",
        ],
        ProjectType.TENDER_REVIEW: [
            "tender", "bid", "pricing", "review", "check", "audit",
            "verification", "assessment",
        ],
        ProjectType.VARIATION_ASSESSMENT: [
            "variation", "change order", "VO", "variation order",
            "amendment", "modification", "revised", "addendum",
        ],
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the Orchestrator.

        Args:
            config: Configuration dict with optional keys:
                - output_dir: Base directory for project outputs
                - auto_classify: Whether to auto-classify project type (default: True)
                - default_project_type: Default type if classification fails
                - vision_provider: Vision provider for intake agent
                - anthropic_api_key: API key for Anthropic
                - openai_api_key: API key for OpenAI
                - google_api_key: API key for Google Geocoding
        """
        self.config = config or {}
        self.output_dir = Path(config.get("output_dir", "./projects")) if config else Path("./projects")
        self.auto_classify = config.get("auto_classify", True) if config else True
        self.default_project_type = ProjectType(
            config.get("default_project_type", "new_build_commercial")
        ) if config else ProjectType.NEW_BUILD_COMMERCIAL

        # Active projects being tracked
        self.active_projects: dict[str, ProjectState] = {}

        self.logger = logging.getLogger(self.__class__.__name__)

    def classify_project_type(
        self,
        brief_text: Optional[str] = None,
        file_names: Optional[list[str]] = None,
        explicit_type: Optional[str] = None,
    ) -> tuple[ProjectType, float, str]:
        """
        Classify the project type based on available information.

        Args:
            brief_text: Text from project brief or description
            file_names: Names of files in the package
            explicit_type: Explicitly specified project type

        Returns:
            Tuple of (ProjectType, confidence score, reasoning)
        """
        # If explicit type provided, use it
        if explicit_type:
            try:
                project_type = ProjectType(explicit_type)
                return project_type, 1.0, f"Explicitly specified as {explicit_type}"
            except ValueError:
                self.logger.warning(f"Unknown explicit type: {explicit_type}, will classify")

        # Score each project type based on keyword matches
        scores: dict[ProjectType, int] = {pt: 0 for pt in ProjectType if pt != ProjectType.UNKNOWN}

        # Combine all text for analysis
        all_text = ""
        if brief_text:
            all_text += brief_text.lower() + " "
        if file_names:
            all_text += " ".join(file_names).lower()

        if not all_text.strip():
            return self.default_project_type, 0.3, "No text to classify, using default"

        # Count keyword matches
        for project_type, keywords in self.PROJECT_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in all_text:
                    scores[project_type] += 1

        # Find highest scoring type
        max_score = max(scores.values())

        if max_score == 0:
            return self.default_project_type, 0.4, "No keywords matched, using default"

        # Get all types with max score (handle ties)
        top_types = [pt for pt, score in scores.items() if score == max_score]

        if len(top_types) == 1:
            confidence = min(0.5 + (max_score * 0.1), 0.95)
            return top_types[0], confidence, f"Matched {max_score} keywords for {top_types[0].value}"

        # Tie-breaker: prefer new_build_commercial as safest default
        if ProjectType.NEW_BUILD_COMMERCIAL in top_types:
            return ProjectType.NEW_BUILD_COMMERCIAL, 0.5, f"Tie between {[t.value for t in top_types]}, defaulting to commercial"

        return top_types[0], 0.5, f"Tie between {[t.value for t in top_types]}, selected first match"

    def get_workflow(self, project_type: ProjectType) -> WorkflowDefinition:
        """Get the workflow definition for a project type."""
        return self.WORKFLOWS.get(project_type, self.WORKFLOWS[ProjectType.NEW_BUILD_COMMERCIAL])

    async def start_project(
        self,
        input_path: str | Path,
        project_id: Optional[str] = None,
        project_type: Optional[str] = None,
        brief_text: Optional[str] = None,
    ) -> OrchestratorResult:
        """
        Start a new project through the QS workflow.

        This is the main entry point. It will:
        1. Classify the project type (or use explicit type)
        2. Select the appropriate workflow
        3. Run the intake agent
        4. Determine next steps based on intake results

        Args:
            input_path: Path to documents (PDF file or directory)
            project_id: Optional project identifier
            project_type: Optional explicit project type
            brief_text: Optional text from project brief for classification

        Returns:
            OrchestratorResult with status and any required decisions
        """
        import time
        start_time = time.time()

        input_path = Path(input_path)
        project_id = project_id or str(uuid.uuid4())[:8].upper()

        errors: list[str] = []
        warnings: list[str] = []

        self.logger.info(f"[{project_id}] Starting project: {input_path}")

        # Step 1: Classify project type
        file_names = None
        if input_path.is_dir():
            file_names = [f.name for f in input_path.glob("*.pdf")]
        elif input_path.is_file():
            file_names = [input_path.name]

        classified_type, confidence, reasoning = self.classify_project_type(
            brief_text=brief_text,
            file_names=file_names,
            explicit_type=project_type,
        )

        self.logger.info(f"[{project_id}] Classified as {classified_type.value} (confidence: {confidence:.0%})")
        self.logger.info(f"[{project_id}] Reasoning: {reasoning}")

        if confidence < 0.6:
            warnings.append(f"Project type classification confidence is low ({confidence:.0%}): {reasoning}")

        # Step 2: Get workflow
        workflow = self.get_workflow(classified_type)
        self.logger.info(f"[{project_id}] Workflow: {' → '.join(workflow.agents)}")

        # Step 3: Initialize project state
        state = ProjectState(
            project_id=project_id,
            project_type=classified_type,
            workflow=workflow,
            status=WorkflowStatus.IN_PROGRESS,
        )

        # Initialize agent executions
        for agent_name in workflow.agents:
            state.agent_executions.append(AgentExecution(agent_name=agent_name))

        self.active_projects[project_id] = state

        # Step 4: Create project directory structure
        project_dir = self.output_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create standard subdirectories
        for subdir in ["01-intake", "02-measure", "03-cost", "04-qa", "05-output", "_project"]:
            (project_dir / subdir).mkdir(exist_ok=True)

        # Step 5: Run intake agent
        intake_execution = state.agent_executions[0]
        intake_execution.status = AgentStatus.RUNNING
        intake_execution.started_at = datetime.now()

        try:
            intake_config = {
                "output_dir": str(project_dir / "01-intake"),
                "project_type": classified_type.value,
            }

            # Pass through vision and API key config
            for key in ["vision_provider", "anthropic_api_key", "openai_api_key", "google_api_key"]:
                if self.config.get(key):
                    intake_config[key] = self.config[key]

            intake_agent = IntakeAnalyst(intake_config)
            intake_result = await intake_agent.analyze(input_path, project_id)

            intake_execution.status = AgentStatus.COMPLETED
            intake_execution.completed_at = datetime.now()
            intake_execution.result = intake_result
            state.intake_result = intake_result

            warnings.extend(intake_result.warnings)

            self.logger.info(f"[{project_id}] Intake complete: {intake_result.completeness.status}")

        except Exception as e:
            intake_execution.status = AgentStatus.FAILED
            intake_execution.completed_at = datetime.now()
            intake_execution.error = str(e)
            errors.append(f"Intake failed: {str(e)}")
            self.logger.error(f"[{project_id}] Intake failed: {e}")

            state.status = WorkflowStatus.FAILED
            state.updated_at = datetime.now()

            return OrchestratorResult(
                project_id=project_id,
                project_type=classified_type,
                status=WorkflowStatus.FAILED,
                workflow_completed=False,
                agents_run=["intake"],
                agents_pending=workflow.agents[1:],
                errors=errors,
                warnings=warnings,
                processing_time_ms=(time.time() - start_time) * 1000,
            )

        # Step 6: Evaluate intake results and determine next steps
        state.current_agent_index = 1
        human_decisions: list[dict[str, Any]] = []
        escalations: list[dict[str, Any]] = []

        # Check if we need to hold for critical gaps
        if intake_result.completeness.proceed_recommendation == "hold":
            state.status = WorkflowStatus.ON_HOLD

            escalations.append({
                "type": "critical_gaps",
                "message": "Project has critical gaps that must be resolved before proceeding",
                "details": intake_result.completeness.hold_reasons,
                "action_required": "Obtain missing documents or confirm acceptable assumptions",
            })

            self.logger.warning(f"[{project_id}] Project on hold due to critical gaps")

        # Check if human decision needed based on autonomy level
        elif workflow.autonomy == AutonomyLevel.LEVEL_1_SUGGEST:
            # Always require human confirmation for level 1
            state.status = WorkflowStatus.AWAITING_INPUT

            human_decisions.append({
                "type": "proceed_confirmation",
                "message": f"Please confirm workflow should proceed for {classified_type.value} project",
                "options": ["proceed", "modify_workflow", "cancel"],
                "context": {
                    "completeness": intake_result.completeness.overall_completeness_pct,
                    "status": intake_result.completeness.status,
                    "missing_items": len(intake_result.completeness.missing_items),
                },
            })

            self.logger.info(f"[{project_id}] Awaiting human confirmation (autonomy: level_1_suggest)")

        elif intake_result.completeness.proceed_recommendation == "proceed_with_caution":
            # For level 2, flag caution items but can proceed
            if workflow.autonomy == AutonomyLevel.LEVEL_2_CONFIRM:
                human_decisions.append({
                    "type": "acknowledge_cautions",
                    "message": "Proceeding with cautions - please review before final output",
                    "cautions": intake_result.completeness.hold_reasons,
                })

        state.escalations = escalations
        state.human_decisions_required = human_decisions
        state.updated_at = datetime.now()

        # Save project state
        await self._save_project_state(state)

        processing_time = (time.time() - start_time) * 1000
        self.logger.info(f"[{project_id}] Orchestration complete in {processing_time:.0f}ms")

        return OrchestratorResult(
            project_id=project_id,
            project_type=classified_type,
            status=state.status,
            workflow_completed=state.status == WorkflowStatus.COMPLETED,
            agents_run=["intake"],
            agents_pending=workflow.agents[1:],
            intake_result=intake_result,
            escalations=escalations,
            human_decisions_required=human_decisions,
            errors=errors,
            warnings=warnings,
            processing_time_ms=processing_time,
        )

    async def continue_project(
        self,
        project_id: str,
        human_decision: Optional[str] = None,
        additional_documents: Optional[list[str]] = None,
    ) -> OrchestratorResult:
        """
        Continue a project that was awaiting input or on hold.

        Args:
            project_id: The project identifier
            human_decision: Decision from human (e.g., "proceed", "cancel")
            additional_documents: Paths to additional documents to process

        Returns:
            OrchestratorResult with updated status
        """
        import time
        start_time = time.time()

        if project_id not in self.active_projects:
            # Try to load from disk
            state = await self._load_project_state(project_id)
            if not state:
                return OrchestratorResult(
                    project_id=project_id,
                    project_type=ProjectType.UNKNOWN,
                    status=WorkflowStatus.FAILED,
                    workflow_completed=False,
                    agents_run=[],
                    agents_pending=[],
                    errors=[f"Project {project_id} not found"],
                    processing_time_ms=(time.time() - start_time) * 1000,
                )
            self.active_projects[project_id] = state
        else:
            state = self.active_projects[project_id]

        errors: list[str] = []
        warnings: list[str] = []

        # Handle human decision
        if human_decision:
            if human_decision == "cancel":
                state.status = WorkflowStatus.FAILED
                state.updated_at = datetime.now()
                await self._save_project_state(state)

                return OrchestratorResult(
                    project_id=project_id,
                    project_type=state.project_type,
                    status=WorkflowStatus.FAILED,
                    workflow_completed=False,
                    agents_run=[e.agent_name for e in state.agent_executions if e.status == AgentStatus.COMPLETED],
                    agents_pending=[e.agent_name for e in state.agent_executions if e.status == AgentStatus.PENDING],
                    errors=["Project cancelled by user"],
                    processing_time_ms=(time.time() - start_time) * 1000,
                )

            elif human_decision == "proceed":
                state.status = WorkflowStatus.IN_PROGRESS
                state.human_decisions_required = []
                state.escalations = []
                self.logger.info(f"[{project_id}] Human decision: proceed")

        # TODO: Process additional documents if provided
        if additional_documents:
            warnings.append("Additional document processing not yet implemented")

        # Continue with next agents in workflow
        pending_agents = [e.agent_name for e in state.agent_executions if e.status == AgentStatus.PENDING]

        # Run the next pending agent if available
        if pending_agents and state.status == WorkflowStatus.IN_PROGRESS:
            next_agent = pending_agents[0]

            if next_agent == "measure":
                # Run measure agent
                measure_result = await self._run_measure_agent(state, errors, warnings)
                if measure_result:
                    state.measure_result = measure_result

                    # Check for high priority clarifications
                    high_priority_clars = [c for c in measure_result.clarifications if c.priority == "high"]
                    if high_priority_clars and state.workflow.autonomy != AutonomyLevel.LEVEL_3_NOTIFY:
                        state.status = WorkflowStatus.AWAITING_INPUT
                        state.human_decisions_required.append({
                            "type": "clarifications_required",
                            "message": f"{len(high_priority_clars)} high-priority clarifications need review",
                            "options": ["proceed_with_assumptions", "hold_for_clarification"],
                        })

            elif next_agent in ["context_enricher", "cost", "qa", "output"]:
                # These agents are not yet implemented
                warnings.append(f"Agent '{next_agent}' not yet implemented - skipping")
                for exec in state.agent_executions:
                    if exec.agent_name == next_agent:
                        exec.status = AgentStatus.SKIPPED
                        break

            # Update pending agents list
            pending_agents = [e.agent_name for e in state.agent_executions if e.status == AgentStatus.PENDING]

        if not pending_agents:
            state.status = WorkflowStatus.COMPLETED
        elif state.status != WorkflowStatus.AWAITING_INPUT:
            # Still have pending agents but none that we can run now
            not_implemented = [a for a in pending_agents if a not in ["intake", "measure"]]
            if not_implemented:
                warnings.append(f"Remaining agents not yet implemented: {', '.join(not_implemented)}")
                state.status = WorkflowStatus.AWAITING_INPUT
                state.human_decisions_required.append({
                    "type": "agents_not_implemented",
                    "message": f"The following agents are not yet implemented: {', '.join(not_implemented)}",
                    "options": ["wait", "complete_manually"],
                })

        state.updated_at = datetime.now()
        await self._save_project_state(state)

        return OrchestratorResult(
            project_id=project_id,
            project_type=state.project_type,
            status=state.status,
            workflow_completed=state.status == WorkflowStatus.COMPLETED,
            agents_run=[e.agent_name for e in state.agent_executions if e.status == AgentStatus.COMPLETED],
            agents_pending=pending_agents,
            intake_result=state.intake_result,
            escalations=state.escalations,
            human_decisions_required=state.human_decisions_required,
            errors=errors,
            warnings=warnings,
            processing_time_ms=(time.time() - start_time) * 1000,
        )

    def get_project_status(self, project_id: str) -> Optional[ProjectState]:
        """Get the current status of a project."""
        return self.active_projects.get(project_id)

    def list_active_projects(self) -> list[dict[str, Any]]:
        """List all active projects."""
        return [
            {
                "project_id": state.project_id,
                "project_type": state.project_type.value,
                "status": state.status.value,
                "current_agent": state.workflow.agents[state.current_agent_index] if state.current_agent_index < len(state.workflow.agents) else "complete",
                "created_at": state.created_at.isoformat(),
                "updated_at": state.updated_at.isoformat(),
            }
            for state in self.active_projects.values()
        ]

    async def _run_measure_agent(
        self,
        state: ProjectState,
        errors: list[str],
        warnings: list[str],
    ) -> Optional[MeasureResult]:
        """Run the measure agent as part of the workflow."""
        project_id = state.project_id

        # Find the measure execution entry
        measure_exec = None
        for exec in state.agent_executions:
            if exec.agent_name == "measure":
                measure_exec = exec
                break

        if not measure_exec:
            errors.append("Measure agent not in workflow")
            return None

        if not state.intake_result:
            errors.append("Cannot run measure - intake not complete")
            return None

        measure_exec.status = AgentStatus.RUNNING
        measure_exec.started_at = datetime.now()

        try:
            # Get drawings from intake result
            all_drawings = []
            for doc in state.intake_result.manifest.documents:
                all_drawings.extend(doc.drawings)

            if not all_drawings:
                warnings.append("No drawings available for measurement")
                measure_exec.status = AgentStatus.SKIPPED
                measure_exec.completed_at = datetime.now()
                return None

            # Configure measure agent
            measure_config = {
                "output_dir": str(self.output_dir / project_id / "02-measure"),
            }

            # Determine measurement standard based on project location
            if state.intake_result.manifest.metadata and state.intake_result.manifest.metadata.location:
                location = state.intake_result.manifest.metadata.location
                if location.country and location.country.upper() in ["UK", "GB"]:
                    measure_config["measurement_standard"] = "nrm2"
                    measure_config["region"] = "uk"
                else:
                    measure_config["measurement_standard"] = "sa_standard"
                    measure_config["region"] = "za"

            # Pass through vision config
            for key in ["vision_provider", "anthropic_api_key", "openai_api_key"]:
                if self.config.get(key):
                    measure_config[key] = self.config[key]

            measure_agent = MeasureAgent(measure_config)

            # Get intake output directory for images
            intake_output_dir = self.output_dir / project_id / "01-intake"

            result = await measure_agent.measure(
                project_id=project_id,
                drawings=all_drawings,
                measurement_scope=state.intake_result.measurement_scope,
                intake_output_dir=intake_output_dir,
            )

            measure_exec.status = AgentStatus.COMPLETED
            measure_exec.completed_at = datetime.now()
            measure_exec.result = result

            warnings.extend(result.warnings)
            if result.errors:
                for err in result.errors:
                    errors.append(err.get("message", str(err)))

            self.logger.info(f"[{project_id}] Measure complete: {result.total_items} items extracted")

            return result

        except Exception as e:
            measure_exec.status = AgentStatus.FAILED
            measure_exec.completed_at = datetime.now()
            measure_exec.error = str(e)
            errors.append(f"Measure failed: {str(e)}")
            self.logger.error(f"[{project_id}] Measure failed: {e}")
            return None

    async def _save_project_state(self, state: ProjectState) -> None:
        """Save project state to disk."""
        project_dir = self.output_dir / state.project_id / "_project"
        project_dir.mkdir(parents=True, exist_ok=True)

        state_path = project_dir / "state.json"
        with open(state_path, "w") as f:
            f.write(state.to_json(indent=2))

        self.logger.debug(f"Saved project state: {state_path}")

    async def _load_project_state(self, project_id: str) -> Optional[ProjectState]:
        """Load project state from disk."""
        state_path = self.output_dir / project_id / "_project" / "state.json"

        if not state_path.exists():
            return None

        try:
            with open(state_path, "r") as f:
                data = json.load(f)

            # Reconstruct ProjectState from JSON
            # Note: This is a simplified reconstruction - intake_result would need special handling
            workflow = WorkflowDefinition(
                project_type=ProjectType(data["workflow"]["project_type"]),
                agents=data["workflow"]["agents"],
                autonomy=AutonomyLevel(data["workflow"]["autonomy"]),
            )

            state = ProjectState(
                project_id=data["project_id"],
                project_type=ProjectType(data["project_type"]),
                workflow=workflow,
                status=WorkflowStatus(data["status"]),
                current_agent_index=data["current_agent_index"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                escalations=data.get("escalations", []),
                human_decisions_required=data.get("human_decisions_required", []),
            )

            # Reconstruct agent executions
            for exec_data in data.get("agent_executions", []):
                execution = AgentExecution(
                    agent_name=exec_data["agent_name"],
                    status=AgentStatus(exec_data["status"]),
                    error=exec_data.get("error"),
                )
                if exec_data.get("started_at"):
                    execution.started_at = datetime.fromisoformat(exec_data["started_at"])
                if exec_data.get("completed_at"):
                    execution.completed_at = datetime.fromisoformat(exec_data["completed_at"])
                state.agent_executions.append(execution)

            return state

        except Exception as e:
            self.logger.error(f"Failed to load project state: {e}")
            return None


async def run_orchestrator(
    input_path: str,
    project_id: Optional[str] = None,
    project_type: Optional[str] = None,
    output_dir: str = "./projects",
    brief_text: Optional[str] = None,
    **kwargs,
) -> OrchestratorResult:
    """
    Convenience function to run the orchestrator.

    Args:
        input_path: Path to documents
        project_id: Optional project identifier
        project_type: Optional explicit project type
        output_dir: Base directory for outputs
        brief_text: Optional brief text for classification
        **kwargs: Additional config options

    Returns:
        OrchestratorResult
    """
    config = {
        "output_dir": output_dir,
        **kwargs,
    }

    orchestrator = Orchestrator(config)
    return await orchestrator.start_project(
        input_path=input_path,
        project_id=project_id,
        project_type=project_type,
        brief_text=brief_text,
    )
