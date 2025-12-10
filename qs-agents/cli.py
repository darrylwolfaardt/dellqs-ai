#!/usr/bin/env python3
"""
QS Agents CLI - Command line interface for running QS agents.

Usage:
    python -m qs_agents.cli intake <input_path> [options]

Examples:
    python -m qs_agents.cli intake ./drawings/project.pdf
    python -m qs_agents.cli intake ./drawings/ --project-id ABC123 --type new_build_commercial
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

    # Intake command
    intake_parser = subparsers.add_parser(
        "intake",
        help="Run intake analysis on documents",
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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(args.log_level)

    if args.command == "intake":
        return asyncio.run(run_intake(args))

    return 0


if __name__ == "__main__":
    sys.exit(main())
