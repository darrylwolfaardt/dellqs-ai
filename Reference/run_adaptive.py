"""Simple wrapper to run adaptive PDF processing without Unicode issues."""
import sys
import json
from pathlib import Path
from adaptive_pdf_processor import AdaptivePDFProcessor

def process_pdf(pdf_path, output_dir):
    """Process a PDF and save analysis."""
    processor = AdaptivePDFProcessor(
        default_dpi=200,
        max_dpi=350,
        tile_overlap_percent=12.0,
        output_format="png"
    )

    result = processor.process_for_vision(pdf_path, output_dir=output_dir)

    # Save analysis as JSON
    if result.success:
        analysis_data = {
            "source": str(pdf_path),
            "page_count": result.page_count,
            "strategy": result.strategy_used.value,
            "total_tiles": result.total_tiles,
            "estimated_tokens": result.estimated_tokens,
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

        analysis_path = Path(output_dir) / "analysis.json"
        with open(analysis_path, "w") as f:
            json.dump(analysis_data, f, indent=2)

        print(f"SUCCESS: {len(result.output_files)} files created")
        for f in result.output_files:
            print(f"  - {Path(f).name}")
    else:
        print(f"FAILED: {result.error_message}")

    return result.success

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_adaptive.py <pdf_path> <output_dir>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    success = process_pdf(pdf_path, output_dir)
    sys.exit(0 if success else 1)
