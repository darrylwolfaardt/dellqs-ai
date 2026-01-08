"""
Batch Adaptive PDF Processor for UFH Project BOQ Rebuild
=========================================================

Processes all key architectural and structural drawings using adaptive
PDF processing for high-quality measurement extraction.

Usage:
    python batch_adaptive_process.py
"""

import sys
import json
from pathlib import Path

# Add reference folder to path
sys.path.insert(0, str(Path(__file__).parent))

from adaptive_pdf_processor import AdaptivePDFProcessor

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
UFHARE_ROOT = PROJECT_ROOT / "Projects" / "UFHARE" / "1 Pre-Tender"
ARCH_DRAWINGS = UFHARE_ROOT / "ALL DRAWINGS SPECS" / "Architectural Drawings"
STRUCT_DRAWINGS = UFHARE_ROOT / "ALL DRAWINGS SPECS" / "Structural Drawings"
OUTPUT_ROOT = PROJECT_ROOT / "Projects" / "UFHARE" / "split_pdfs_adaptive"

# Key drawings organized by trade relevance
DRAWINGS_TO_PROCESS = {
    # Main architectural plans
    "ground_plan": {
        "pdf": ARCH_DRAWINGS / "A-(11)1000-Ground Storey Plan-(4).pdf",
        "trades": ["masonry", "partitions", "doors", "glazing", "floor_finishes", "wall_finishes", "plumbing"]
    },
    "roof_plan": {
        "pdf": ARCH_DRAWINGS / "A-(11)1001-Roof Plan-(4).pdf",
        "trades": ["roofing", "rainwater", "insulation"]
    },
    "clerestory_plan": {
        "pdf": ARCH_DRAWINGS / "A-(11)1002-Clerestory Plan Level-(3).pdf",
        "trades": ["roofing", "glazing", "structure"]
    },
    "general_arrangement": {
        "pdf": ARCH_DRAWINGS / "A-(11)1003-General Arrangement Layout-(4).pdf",
        "trades": ["all"]
    },
    "sections": {
        "pdf": ARCH_DRAWINGS / "A-(12)2000-Sections-(4).pdf",
        "trades": ["concrete", "masonry", "roofing", "structure"]
    },
    "elevations": {
        "pdf": ARCH_DRAWINGS / "A-(13)3000-Elevations-(4).pdf",
        "trades": ["external_finishes", "roofing", "glazing"]
    },
    "ceiling_plan": {
        "pdf": ARCH_DRAWINGS / "A-(14)1000-Ceiling Plan-(3).pdf",
        "trades": ["ceilings", "bulkheads"]
    },
    "ground_ceiling": {
        "pdf": ARCH_DRAWINGS / "A-(14)1003-GROUND STOREY CEILING PLAN (1).pdf",
        "trades": ["ceilings", "bulkheads"]
    },
    # Fenestration
    "fenestration_key": {
        "pdf": ARCH_DRAWINGS / "A-(30)1001-Fenestration Key Plan-(2).pdf",
        "trades": ["glazing", "doors"]
    },
    "fenestration_clerestory": {
        "pdf": ARCH_DRAWINGS / "A-(30)1002-Fenestration Key Plan_Clerestory-(2).pdf",
        "trades": ["glazing"]
    },
    # Finishes layouts
    "wall_finishes": {
        "pdf": ARCH_DRAWINGS / "A-(51)1001-Wall Finishes Layout(1).pdf",
        "trades": ["wall_finishes", "plastering", "painting", "tiling"]
    },
    "floor_finishes": {
        "pdf": ARCH_DRAWINGS / "A-(52)1001-Floor Finishes Layout(1).pdf",
        "trades": ["floor_finishes", "tiling"]
    },
    "skirtings": {
        "pdf": ARCH_DRAWINGS / "A-(52)1002-Skirtings(1).pdf",
        "trades": ["carpentry", "skirtings"]
    },
    # Ablution details
    "ablution_details": {
        "pdf": ARCH_DRAWINGS / "A-(50)6001-Ablution Details-(1).pdf",
        "trades": ["plumbing", "tiling", "waterproofing"]
    },
    # Joinery
    "joinery_key": {
        "pdf": ARCH_DRAWINGS / "A-(74)1000-Fixed Furniture and Fittings Key Plan(1).pdf",
        "trades": ["carpentry", "joinery"]
    },
    "security_desk": {
        "pdf": ARCH_DRAWINGS / "A-(74)6001-JT01 - Security Desk(1).pdf",
        "trades": ["joinery"]
    },
    "kitchenette": {
        "pdf": ARCH_DRAWINGS / "A-(74)6002-JT02 - Kitchenette(1).pdf",
        "trades": ["joinery", "plumbing"]
    },
    # External works
    "paving_layout": {
        "pdf": ARCH_DRAWINGS / "New Paving Layout.pdf",
        "trades": ["external_works", "paving"]
    },
    # Demolitions
    "demolition_plan": {
        "pdf": ARCH_DRAWINGS / "A-(01)1002-Demolition Plan(3).pdf",
        "trades": ["demolitions"]
    },
    # Structural drawings
    "foundation_layout": {
        "pdf": STRUCT_DRAWINGS / "S-01-25055-20-001-Rev E-Foundation Layout.pdf",
        "trades": ["earthworks", "concrete", "formwork", "reinforcement"]
    },
    "surface_bed": {
        "pdf": STRUCT_DRAWINGS / "S-01-25055-20-002-Rev E-Surface Bed Layout.pdf",
        "trades": ["concrete", "formwork", "reinforcement"]
    },
    "ring_beam": {
        "pdf": STRUCT_DRAWINGS / "S-01-25055-20-003-Rev E-Ring Beam Layout.pdf",
        "trades": ["concrete", "formwork", "reinforcement"]
    },
    "structural_sections": {
        "pdf": STRUCT_DRAWINGS / "S-01-25055-20-004-Rev D-Sections.pdf",
        "trades": ["concrete", "structure"]
    },
}

def process_all_drawings():
    """Process all key drawings with adaptive extraction."""
    processor = AdaptivePDFProcessor(
        default_dpi=200,
        max_dpi=350,
        tile_overlap_percent=12.0,
        output_format="png"
    )

    results = {}
    total_tokens = 0
    total_tiles = 0

    print("=" * 60)
    print("UFH Adaptive PDF Processing - Full BOQ Rebuild")
    print("=" * 60)

    for name, config in DRAWINGS_TO_PROCESS.items():
        pdf_path = config["pdf"]

        if not pdf_path.exists():
            print(f"\n[SKIP] {name}: File not found - {pdf_path.name}")
            continue

        output_dir = OUTPUT_ROOT / pdf_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)

        # Check if already processed
        analysis_file = output_dir / "analysis.json"
        if analysis_file.exists():
            with open(analysis_file) as f:
                existing = json.load(f)
            print(f"\n[EXISTS] {name}: {existing['total_tiles']} tiles, ~{existing['estimated_tokens']:,} tokens")
            results[name] = existing
            total_tokens += existing['estimated_tokens']
            total_tiles += existing['total_tiles']
            continue

        print(f"\n[PROCESSING] {name}: {pdf_path.name}")
        print(f"  Trades: {', '.join(config['trades'])}")

        try:
            result = processor.process_for_vision(str(pdf_path), output_dir=str(output_dir))

            if result.success:
                analysis_data = {
                    "source": str(pdf_path),
                    "drawing_name": name,
                    "page_count": result.page_count,
                    "strategy": result.strategy_used.value,
                    "total_tiles": result.total_tiles,
                    "estimated_tokens": result.estimated_tokens,
                    "trades": config["trades"],
                    "output_files": result.output_files,
                    "pages": []
                }

                for pa in result.page_analyses:
                    analysis_data["pages"].append({
                        "page": pa.page_number + 1,
                        "width_pts": pa.width_pts,
                        "height_pts": pa.height_pts,
                        "text_blocks": pa.total_text_blocks,
                        "drawings": pa.total_drawings,
                        "density": pa.density_level.value,
                        "detected_scale": pa.detected_scale,
                        "strategy": pa.recommended_strategy.value,
                        "recommended_dpi": pa.recommended_base_dpi
                    })

                with open(analysis_file, "w") as f:
                    json.dump(analysis_data, f, indent=2)

                print(f"  SUCCESS: {result.total_tiles} tiles, ~{result.estimated_tokens:,} tokens")
                print(f"  Strategy: {result.strategy_used.value}")
                for pa in result.page_analyses:
                    print(f"  Page {pa.page_number + 1}: {pa.density_level.value} density, scale {pa.detected_scale or 'not detected'}")

                results[name] = analysis_data
                total_tokens += result.estimated_tokens
                total_tiles += result.total_tiles
            else:
                print(f"  FAILED: {result.error_message}")

        except Exception as e:
            print(f"  ERROR: {str(e)}")

    # Summary
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Drawings processed: {len(results)}")
    print(f"Total tiles: {total_tiles}")
    print(f"Estimated tokens: {total_tokens:,}")
    print(f"Output directory: {OUTPUT_ROOT}")

    # Save master index
    index_file = OUTPUT_ROOT / "processing_index.json"
    with open(index_file, "w") as f:
        json.dump({
            "project": "UFH Alice Campus Finance Offices",
            "processed_date": "2026-01-08",
            "total_drawings": len(results),
            "total_tiles": total_tiles,
            "total_estimated_tokens": total_tokens,
            "drawings": results
        }, f, indent=2)

    print(f"\nIndex saved: {index_file}")

    return results

if __name__ == "__main__":
    process_all_drawings()
