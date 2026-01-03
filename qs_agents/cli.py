#!/usr/bin/env python3
"""
QS Agents CLI - Command line interface for running QS agents.

Usage:
    python -m qs_agents.cli start <input_path> [options]  # Start new project via orchestrator
    python -m qs_agents.cli intake <input_path> [options]  # Run intake only

Examples:
    python -m qs_agents.cli start ./drawings/ --project-id ABC123 --type new_build_commercial
    python -m qs_agents.cli intake ./drawings/project.pdf
    python -m qs_agents.cli continue ABC123 --decision proceed
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_logging(level: str = "INFO"):
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


async def run_intake(args):
    """Run the intake analyst agent."""
    from qs_agents.agents import IntakeAnalyst

    config = {
        "output_dir": args.output,
        "project_type": args.type,
    }

    # Vision provider configuration
    # Default: uses Claude Code CLI (authenticated session, no API key needed)
    # Optional: set ANTHROPIC_API_KEY or OPENAI_API_KEY for direct API access
    if os.environ.get("ANTHROPIC_API_KEY"):
        config["anthropic_api_key"] = os.environ["ANTHROPIC_API_KEY"]
        config["vision_provider"] = "anthropic"
    elif os.environ.get("OPENAI_API_KEY"):
        config["openai_api_key"] = os.environ["OPENAI_API_KEY"]
        config["vision_provider"] = "openai"
    else:
        # Use Claude Code CLI by default (no API key required)
        config["vision_provider"] = "claude"

    if os.environ.get("GOOGLE_API_KEY"):
        config["google_api_key"] = os.environ["GOOGLE_API_KEY"]

    analyst = IntakeAnalyst(config)

    print(f"\n{'=' * 60}")
    print("QS INTAKE ANALYST")
    print(f"{'=' * 60}")
    print(f"Input: {args.input}")
    print(f"Project Type: {args.type}")
    print(f"Output Directory: {args.output}")
    print(f"{'=' * 60}\n")

    result = await analyst.analyze(args.input, args.project_id)

    # Print summary
    print(f"\n{'=' * 60}")
    print("INTAKE ANALYSIS COMPLETE")
    print(f"{'=' * 60}")
    print(f"Project ID: {result.project_id}")
    print(f"Processing Time: {result.processing_time_ms:.0f}ms")
    print()

    # Manifest summary
    print("DOCUMENTS RECEIVED:")
    print(f"  - Total documents: {len(result.manifest.documents)}")
    print(f"  - Total pages: {result.manifest.total_pages}")
    print(f"  - Total drawings: {result.manifest.total_drawings}")
    print()

    # Metadata summary
    if result.manifest.metadata:
        m = result.manifest.metadata
        print("PROJECT METADATA:")
        if m.project_name:
            print(f"  - Project: {m.project_name}")
        if m.project_number:
            print(f"  - Reference: {m.project_number}")
        if m.architect:
            print(f"  - Architect: {m.architect}")
        if m.location and m.location.postcode:
            print(f"  - Location: {m.location.postcode}")
        print()

    # Completeness summary
    c = result.completeness
    print("COMPLETENESS ASSESSMENT:")
    print(f"  - Status: {c.status.upper()}")
    print(f"  - Completeness: {c.overall_completeness_pct:.0f}%")
    print(f"  - Recommendation: {c.proceed_recommendation.upper()}")
    if c.hold_reasons:
        print("  - Reasons:")
        for reason in c.hold_reasons:
            print(f"      • {reason}")
    print()

    # Drawing types found
    if c.drawing_types_present:
        print("DRAWING TYPES IDENTIFIED:")
        for dt in c.drawing_types_present:
            print(f"  ✓ {dt.value.replace('_', ' ').title()}")
        print()

    # Missing items
    if c.missing_items:
        critical = [m for m in c.missing_items if m.severity == "critical"]
        important = [m for m in c.missing_items if m.severity == "important"]

        if critical:
            print("CRITICAL MISSING ITEMS:")
            for item in critical:
                print(f"  ✗ {item.description}")
            print()

        if important:
            print("IMPORTANT MISSING ITEMS:")
            for item in important:
                print(f"  ⚠ {item.description}")
            print()

    # Measurement scope summary
    s = result.measurement_scope
    high = len([m for m in s.measurable_elements if m.confidence == "high"])
    med = len([m for m in s.measurable_elements if m.confidence == "medium"])
    low = len([m for m in s.measurable_elements if m.confidence == "low"])

    print("MEASUREMENT SCOPE:")
    print(f"  - Measurable elements: {len(s.measurable_elements)}")
    print(f"      High confidence: {high}")
    print(f"      Medium confidence: {med}")
    print(f"      Low confidence: {low}")
    print(f"  - Cannot be measured: {len(s.unmeasurable_elements)}")
    print()

    # Warnings
    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings[:5]:  # Show first 5
            print(f"  ⚠ {warning}")
        if len(result.warnings) > 5:
            print(f"  ... and {len(result.warnings) - 5} more")
        print()

    # Output files
    output_dir = Path(args.output) / result.project_id
    print("OUTPUT FILES:")
    print(f"  - {output_dir / 'project_manifest.json'}")
    print(f"  - {output_dir / 'completeness_report.md'}")
    print(f"  - {output_dir / 'measurement_scope.md'}")
    print(f"{'=' * 60}\n")

    return 0 if c.proceed_recommendation != "hold" else 1


async def run_start(args):
    """Start a new project via the orchestrator."""
    from qs_agents.agents import Orchestrator

    config = {
        "output_dir": args.output,
    }

    # Vision provider configuration
    if os.environ.get("ANTHROPIC_API_KEY"):
        config["anthropic_api_key"] = os.environ["ANTHROPIC_API_KEY"]
        config["vision_provider"] = "anthropic"
    elif os.environ.get("OPENAI_API_KEY"):
        config["openai_api_key"] = os.environ["OPENAI_API_KEY"]
        config["vision_provider"] = "openai"
    else:
        config["vision_provider"] = "claude"

    if os.environ.get("GOOGLE_API_KEY"):
        config["google_api_key"] = os.environ["GOOGLE_API_KEY"]

    orchestrator = Orchestrator(config)

    print(f"\n{'=' * 60}")
    print("QS ORCHESTRATOR - PROJECT START")
    print(f"{'=' * 60}")
    print(f"Input: {args.input}")
    if args.type:
        print(f"Project Type: {args.type}")
    print(f"Output Directory: {args.output}")
    print(f"{'=' * 60}\n")

    result = await orchestrator.start_project(
        input_path=args.input,
        project_id=args.project_id,
        project_type=args.type,
        brief_text=args.brief,
    )

    # Print summary
    print(f"\n{'=' * 60}")
    print("PROJECT INITIALIZED")
    print(f"{'=' * 60}")
    print(f"Project ID: {result.project_id}")
    print(f"Project Type: {result.project_type.value}")
    print(f"Status: {result.status.value.upper()}")
    print(f"Processing Time: {result.processing_time_ms:.0f}ms")
    print()

    # Workflow info
    workflow = orchestrator.get_workflow(result.project_type)
    print("WORKFLOW:")
    print(f"  Agents: {' → '.join(workflow.agents)}")
    print(f"  Autonomy: {workflow.autonomy.value}")
    print()

    # Agent status
    print("AGENT STATUS:")
    for agent in result.agents_run:
        print(f"  ✓ {agent} - completed")
    for agent in result.agents_pending:
        print(f"  ○ {agent} - pending")
    print()

    # Intake summary if available
    if result.intake_result:
        ir = result.intake_result
        print("INTAKE SUMMARY:")
        print(f"  Documents: {len(ir.manifest.documents)}")
        print(f"  Pages: {ir.manifest.total_pages}")
        print(f"  Drawings: {ir.manifest.total_drawings}")
        print(f"  Completeness: {ir.completeness.overall_completeness_pct:.0f}%")
        print(f"  Recommendation: {ir.completeness.proceed_recommendation.upper()}")
        print()

    # Escalations
    if result.escalations:
        print("ESCALATIONS:")
        for esc in result.escalations:
            print(f"  ⚠ {esc['type'].upper()}: {esc['message']}")
            if esc.get('details'):
                for detail in esc['details']:
                    print(f"      - {detail}")
        print()

    # Human decisions required
    if result.human_decisions_required:
        print("DECISIONS REQUIRED:")
        for dec in result.human_decisions_required:
            print(f"  ? {dec['message']}")
            if dec.get('options'):
                print(f"    Options: {', '.join(dec['options'])}")
        print()
        print("To continue, run:")
        print(f"  python -m qs_agents.cli continue {result.project_id} --decision <option>")
        print()

    # Warnings
    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings[:5]:
            print(f"  ⚠ {warning}")
        if len(result.warnings) > 5:
            print(f"  ... and {len(result.warnings) - 5} more")
        print()

    # Errors
    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  ✗ {error}")
        print()

    # Output location
    print(f"Project Directory: {args.output}/{result.project_id}/")
    print(f"{'=' * 60}\n")

    return 0 if result.status.value not in ["failed", "on_hold"] else 1


async def run_continue(args):
    """Continue an existing project."""
    from qs_agents.agents import Orchestrator

    config = {
        "output_dir": args.output,
    }

    orchestrator = Orchestrator(config)

    print(f"\n{'=' * 60}")
    print("QS ORCHESTRATOR - CONTINUE PROJECT")
    print(f"{'=' * 60}")
    print(f"Project ID: {args.project_id}")
    print(f"Decision: {args.decision}")
    print(f"{'=' * 60}\n")

    result = await orchestrator.continue_project(
        project_id=args.project_id,
        human_decision=args.decision,
    )

    # Print summary
    print(f"\n{'=' * 60}")
    print("PROJECT STATUS UPDATE")
    print(f"{'=' * 60}")
    print(f"Project ID: {result.project_id}")
    print(f"Status: {result.status.value.upper()}")
    print(f"Workflow Complete: {'Yes' if result.workflow_completed else 'No'}")
    print()

    # Agent status
    print("AGENT STATUS:")
    for agent in result.agents_run:
        print(f"  ✓ {agent} - completed")
    for agent in result.agents_pending:
        print(f"  ○ {agent} - pending")
    print()

    # Human decisions required
    if result.human_decisions_required:
        print("DECISIONS REQUIRED:")
        for dec in result.human_decisions_required:
            print(f"  ? {dec['message']}")
        print()

    # Warnings
    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")
        print()

    print(f"{'=' * 60}\n")

    return 0 if result.status.value != "failed" else 1


async def run_cost(args):
    """Run the cost agent standalone."""
    from pathlib import Path
    import json
    from qs_agents.agents import CostAgent, MeasureResult, MeasurementStandard
    from qs_agents.agents.measure import ElementGroup, QuantityItem, ElementCategory, UnitOfMeasure

    config = {
        "output_dir": args.output,
        "region": args.region,
        "project_stage": args.stage,
        "project_type": args.type,
    }

    agent = CostAgent(config)

    print(f"\n{'=' * 60}")
    print("QS COST AGENT")
    print(f"{'=' * 60}")
    print(f"Project ID: {args.project_id}")
    print(f"Measure Directory: {args.measure_dir}")
    print(f"Region: {args.region}")
    print(f"Project Stage: {args.stage}")
    print(f"Output Directory: {args.output}")
    print(f"{'=' * 60}\n")

    # Load measure results
    measure_dir = Path(args.measure_dir)
    quantities_path = measure_dir / "quantities.json"

    if not quantities_path.exists():
        print(f"ERROR: Quantities not found at {quantities_path}")
        print("Run measure first: python -m qs_agents.cli measure <project_id> <intake_dir>")
        return 1

    with open(quantities_path) as f:
        quantities_data = json.load(f)

    # Convert to MeasureResult object
    # Parse element groups
    element_groups = []
    for g in quantities_data.get("element_groups", []):
        try:
            category = ElementCategory(g.get("category", "superstructure"))
        except ValueError:
            category = ElementCategory.SUPERSTRUCTURE

        items = []
        for item_data in g.get("items", []):
            try:
                unit = UnitOfMeasure(item_data.get("unit", "item"))
            except ValueError:
                unit = UnitOfMeasure.ITEM

            item = QuantityItem(
                item_id=item_data.get("item_id", ""),
                element_ref=item_data.get("element_ref", ""),
                description=item_data.get("description", ""),
                quantity=float(item_data.get("quantity", 0)),
                unit=unit,
                nrm_reference=item_data.get("nrm_reference"),
                source_drawing=item_data.get("source_drawing"),
                source_page=item_data.get("source_page"),
                measurement_method=item_data.get("measurement_method", ""),
                calculation=item_data.get("calculation"),
                confidence=float(item_data.get("confidence", 0.5)),
                assumptions=item_data.get("assumptions", []),
                notes=item_data.get("notes", []),
            )
            items.append(item)

        group = ElementGroup(
            category=category,
            element_code=g.get("element_code", ""),
            element_name=g.get("element_name", ""),
            items=items,
        )
        element_groups.append(group)

    try:
        standard = MeasurementStandard(quantities_data.get("measurement_standard", "sa_standard"))
    except ValueError:
        standard = MeasurementStandard.SA_STANDARD

    measure_result = MeasureResult(
        project_id=quantities_data.get("project_id", args.project_id),
        measurement_standard=standard,
        element_groups=element_groups,
        clarifications=[],  # Not needed for pricing
        confidence_scores=[],
        processing_time_ms=0,
        drawings_analyzed=quantities_data.get("summary", {}).get("drawings_analyzed", 0),
        total_items=quantities_data.get("summary", {}).get("total_items", 0),
        assumptions_made=quantities_data.get("assumptions_made", []),
        exclusions=quantities_data.get("exclusions", []),
    )

    if not measure_result.element_groups:
        print("ERROR: No element groups found in quantities")
        return 1

    total_items = sum(len(g.items) for g in measure_result.element_groups)
    print(f"Found {total_items} quantity items in {len(measure_result.element_groups)} element groups")
    print()

    # Run pricing
    result = await agent.price(
        project_id=args.project_id,
        measure_result=measure_result,
        gifa=args.gifa,
    )

    # Print summary
    print(f"\n{'=' * 60}")
    print("COST PRICING COMPLETE")
    print(f"{'=' * 60}")
    print(f"Project ID: {result.project_id}")
    print(f"Region: {result.region.value.replace('_', ' ').title()}")
    print(f"Project Stage: {result.project_stage.value.title()}")
    print(f"Processing Time: {result.processing_time_ms:.0f}ms")
    print()

    # Cost summary
    s = result.summary
    print("COST SUMMARY:")
    print(f"  Base Building Cost:    {result.currency} {s.base_building_cost:>15,.2f}")
    print(f"  External Works:        {result.currency} {s.external_works:>15,.2f}")
    print(f"  Preliminaries:         {result.currency} {s.preliminaries:>15,.2f}")
    print(f"  Contingencies:         {result.currency} {s.contingencies:>15,.2f}")
    print(f"  Professional Fees:     {result.currency} {s.professional_fees:>15,.2f}")
    print(f"  ----------------------------------------")
    print(f"  Subtotal (excl VAT):   {result.currency} {s.subtotal_excl_vat:>15,.2f}")
    print(f"  VAT @ 15%:             {result.currency} {s.vat_amount:>15,.2f}")
    print(f"  ========================================")
    print(f"  TOTAL (incl VAT):      {result.currency} {s.total_incl_vat:>15,.2f}")
    print()

    if s.cost_per_sqm and s.gifa:
        print(f"  GIFA:                  {s.gifa:,.2f} m²")
        print(f"  Cost per m²:           {result.currency} {s.cost_per_sqm:,.2f}")
        print()

    # Statistics
    print("STATISTICS:")
    print(f"  - Items priced: {result.items_priced}")
    print(f"  - Items unpriced: {result.items_unpriced}")
    print(f"  - Element groups: {len(result.element_groups)}")
    print(f"  - Risks identified: {len(result.risks)}")
    print()

    # Risks
    if result.risks:
        high_risks = [r for r in result.risks if r.impact == "high"]
        if high_risks:
            print("HIGH IMPACT RISKS:")
            for r in high_risks[:3]:
                print(f"  ⚠ {r.description}")
            if len(high_risks) > 3:
                print(f"    ... and {len(high_risks) - 3} more")
            print()

    # Warnings
    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings[:5]:
            print(f"  ⚠ {warning}")
        if len(result.warnings) > 5:
            print(f"    ... and {len(result.warnings) - 5} more")
        print()

    # Errors
    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  ✗ {error.get('message', str(error))}")
        print()

    # Output files
    output_dir = Path(args.output)
    print("OUTPUT FILES:")
    print(f"  - {output_dir / 'priced_boq.json'}")
    print(f"  - {output_dir / 'priced_boq.xlsx'} (if openpyxl installed)")
    print(f"  - {output_dir / 'cost_summary.md'}")
    print(f"  - {output_dir / 'pricing_assumptions.md'}")
    print(f"  - {output_dir / 'cost_risk_register.md'}")
    print(f"{'=' * 60}\n")

    return 0 if not result.errors else 1


async def run_measure(args):
    """Run the measure agent standalone."""
    from pathlib import Path
    import json
    from qs_agents.agents import MeasureAgent
    from qs_agents.tools.common import DrawingInfo, DrawingType, MeasurementScope

    config = {
        "output_dir": args.output,
        "measurement_standard": args.standard,
    }

    # Vision provider configuration
    if os.environ.get("ANTHROPIC_API_KEY"):
        config["anthropic_api_key"] = os.environ["ANTHROPIC_API_KEY"]
        config["vision_provider"] = "anthropic"
    elif os.environ.get("OPENAI_API_KEY"):
        config["openai_api_key"] = os.environ["OPENAI_API_KEY"]
        config["vision_provider"] = "openai"
    else:
        config["vision_provider"] = "claude"

    agent = MeasureAgent(config)

    print(f"\n{'=' * 60}")
    print("QS MEASURE AGENT")
    print(f"{'=' * 60}")
    print(f"Project ID: {args.project_id}")
    print(f"Intake Directory: {args.intake_dir}")
    print(f"Measurement Standard: {args.standard}")
    print(f"Output Directory: {args.output}")
    print(f"{'=' * 60}\n")

    # Load intake results
    intake_dir = Path(args.intake_dir)
    manifest_path = intake_dir / "project_manifest.json"

    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}")
        print("Run intake first: python -m qs_agents.cli intake <drawings>")
        return 1

    with open(manifest_path) as f:
        manifest_data = json.load(f)

    # Convert manifest drawings to DrawingInfo objects
    drawings = []
    for doc in manifest_data.get("documents", []):
        for d in doc.get("drawings", []):
            try:
                drawing_type = DrawingType(d.get("drawing_type", "unknown"))
            except ValueError:
                drawing_type = DrawingType.UNKNOWN

            drawing = DrawingInfo(
                file_path=d.get("file_path", ""),
                page_number=d.get("page_number", 1),
                drawing_type=drawing_type,
                drawing_number=d.get("drawing_number"),
                drawing_title=d.get("drawing_title"),
                scale=d.get("scale"),
                dimensions_present=d.get("dimensions_present", False),
                annotations_present=d.get("annotations_present", False),
                confidence=d.get("confidence", 0.5),
            )
            # Try to set image path
            source_file = Path(drawing.file_path).stem
            image_path = intake_dir / "images" / f"{source_file}_page_{drawing.page_number}.png"
            if image_path.exists():
                drawing.image_path = str(image_path)
            drawings.append(drawing)

    if not drawings:
        print("ERROR: No drawings found in manifest")
        return 1

    print(f"Found {len(drawings)} drawings from intake")
    print()

    # Run measurement
    result = await agent.measure(
        project_id=args.project_id,
        drawings=drawings,
        intake_output_dir=intake_dir,
    )

    # Print summary
    print(f"\n{'=' * 60}")
    print("MEASUREMENT EXTRACTION COMPLETE")
    print(f"{'=' * 60}")
    print(f"Project ID: {result.project_id}")
    print(f"Measurement Standard: {result.measurement_standard.value.upper()}")
    print(f"Processing Time: {result.processing_time_ms:.0f}ms")
    print()

    print("SUMMARY:")
    print(f"  - Drawings Analyzed: {result.drawings_analyzed}")
    print(f"  - Total Items Measured: {result.total_items}")
    print(f"  - Element Groups: {len(result.element_groups)}")
    print(f"  - Clarifications Needed: {len(result.clarifications)}")
    print()

    # Element groups
    if result.element_groups:
        print("ELEMENT GROUPS:")
        for group in result.element_groups:
            print(f"  {group.element_code} {group.element_name}: {len(group.items)} items")
        print()

    # Confidence scores
    if result.confidence_scores:
        print("CONFIDENCE SCORES:")
        for score in result.confidence_scores:
            print(f"  {score.category}: {score.overall_confidence:.0%}")
            if score.limiting_factors:
                for factor in score.limiting_factors[:2]:
                    print(f"      - {factor}")
        print()

    # Clarifications
    if result.clarifications:
        high_priority = [c for c in result.clarifications if c.priority == "high"]
        if high_priority:
            print("HIGH PRIORITY CLARIFICATIONS:")
            for c in high_priority[:3]:
                print(f"  ? {c.question}")
            if len(high_priority) > 3:
                print(f"    ... and {len(high_priority) - 3} more")
            print()

    # Assumptions
    if result.assumptions_made:
        print("ASSUMPTIONS MADE:")
        for assumption in result.assumptions_made[:5]:
            print(f"  - {assumption}")
        if len(result.assumptions_made) > 5:
            print(f"    ... and {len(result.assumptions_made) - 5} more")
        print()

    # Exclusions
    if result.exclusions:
        print("EXCLUSIONS:")
        for exclusion in result.exclusions[:5]:
            print(f"  - {exclusion}")
        print()

    # Warnings
    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings[:5]:
            print(f"  ⚠ {warning}")
        if len(result.warnings) > 5:
            print(f"    ... and {len(result.warnings) - 5} more")
        print()

    # Errors
    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  ✗ {error.get('message', str(error))}")
        print()

    # Output files
    output_dir = Path(args.output)
    print("OUTPUT FILES:")
    print(f"  - {output_dir / 'quantities.json'}")
    print(f"  - {output_dir / 'take_off_notes.md'}")
    print(f"  - {output_dir / 'clarifications.md'}")
    print(f"  - {output_dir / 'measurement_confidence.json'}")
    print(f"{'=' * 60}\n")

    return 0 if not result.errors else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="QS Agents CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start command (orchestrator)
    start_parser = subparsers.add_parser(
        "start",
        help="Start a new project via the orchestrator",
    )
    start_parser.add_argument(
        "input",
        help="Path to PDF file or directory containing PDFs",
    )
    start_parser.add_argument(
        "--project-id",
        dest="project_id",
        help="Project identifier (auto-generated if not provided)",
    )
    start_parser.add_argument(
        "--output", "-o",
        default="./projects",
        help="Base output directory for projects",
    )
    start_parser.add_argument(
        "--type", "-t",
        default=None,
        choices=[
            "new_build_residential",
            "new_build_commercial",
            "refurbishment",
            "tender_review",
            "variation_assessment",
        ],
        help="Project type (auto-detected if not provided)",
    )
    start_parser.add_argument(
        "--brief", "-b",
        default=None,
        help="Brief text for project classification",
    )

    # Continue command
    continue_parser = subparsers.add_parser(
        "continue",
        help="Continue an existing project",
    )
    continue_parser.add_argument(
        "project_id",
        help="Project identifier to continue",
    )
    continue_parser.add_argument(
        "--decision", "-d",
        required=True,
        choices=["proceed", "cancel", "modify_workflow"],
        help="Decision for continuing the project",
    )
    continue_parser.add_argument(
        "--output", "-o",
        default="./projects",
        help="Base output directory for projects",
    )

    # Intake command (standalone)
    intake_parser = subparsers.add_parser(
        "intake",
        help="Run intake analysis only (standalone, no orchestrator)",
    )
    intake_parser.add_argument(
        "input",
        help="Path to PDF file or directory containing PDFs",
    )
    intake_parser.add_argument(
        "--project-id",
        dest="project_id",
        help="Project identifier (auto-generated if not provided)",
    )
    intake_parser.add_argument(
        "--output", "-o",
        default="./intake_output",
        help="Output directory for results",
    )
    intake_parser.add_argument(
        "--type", "-t",
        default="new_build_commercial",
        choices=[
            "new_build_residential",
            "new_build_commercial",
            "refurbishment",
            "tender_review",
            "variation_assessment",
            "default",
        ],
        help="Project type for completeness checking",
    )

    # Measure command (standalone)
    measure_parser = subparsers.add_parser(
        "measure",
        help="Run measurement extraction (requires intake to be complete)",
    )
    measure_parser.add_argument(
        "project_id",
        help="Project identifier",
    )
    measure_parser.add_argument(
        "intake_dir",
        help="Path to intake output directory containing project_manifest.json",
    )
    measure_parser.add_argument(
        "--output", "-o",
        default="./measure_output",
        help="Output directory for measurement results",
    )
    measure_parser.add_argument(
        "--standard", "-s",
        default="sa_standard",
        choices=["sa_standard", "nrm1", "nrm2"],
        help="Measurement standard to apply",
    )

    # Cost command (standalone)
    cost_parser = subparsers.add_parser(
        "cost",
        help="Run cost pricing (requires measure to be complete)",
    )
    cost_parser.add_argument(
        "project_id",
        help="Project identifier",
    )
    cost_parser.add_argument(
        "measure_dir",
        help="Path to measure output directory containing quantities.json",
    )
    cost_parser.add_argument(
        "--output", "-o",
        default="./cost_output",
        help="Output directory for cost results",
    )
    cost_parser.add_argument(
        "--region", "-r",
        default="gauteng",
        choices=[
            "gauteng", "western_cape", "kwazulu_natal", "eastern_cape",
            "free_state", "limpopo", "mpumalanga", "north_west", "northern_cape", "uk",
        ],
        help="Region for rate adjustment",
    )
    cost_parser.add_argument(
        "--stage",
        default="concept",
        choices=["feasibility", "concept", "developed", "technical", "tender"],
        help="Project stage for pricing detail level",
    )
    cost_parser.add_argument(
        "--type", "-t",
        default="new_build_standard",
        choices=[
            "new_build_standard", "new_build_complex", "refurbishment",
            "heritage", "tender_review", "variation",
        ],
        help="Project type for contingency calculation",
    )
    cost_parser.add_argument(
        "--gifa",
        type=float,
        default=None,
        help="Gross Internal Floor Area (m²) for cost per m² calculation",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(args.log_level)

    if args.command == "start":
        return asyncio.run(run_start(args))
    elif args.command == "continue":
        return asyncio.run(run_continue(args))
    elif args.command == "intake":
        return asyncio.run(run_intake(args))
    elif args.command == "measure":
        return asyncio.run(run_measure(args))
    elif args.command == "cost":
        return asyncio.run(run_cost(args))

    return 0


if __name__ == "__main__":
    sys.exit(main())
