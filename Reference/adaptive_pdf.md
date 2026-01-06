Two modules ready for your QS application:
## adaptive_pdf_processor.py - Core processing engine:

[adaptive_pdf_processor.py]('./adaptive_pdf_processor.py)

Analyzes page density (text blocks, drawing elements, text sizes)
Detects scale from annotations (1:50, 1:100, etc.)
Automatically selects strategy: direct render, enhanced DPI, or intelligent tiling
Adaptive DPI per region for variable-density drawings
Configurable tile overlap (default 12%) to avoid cutting elements

## opus_vision_optimizer.py - High-level API interface:
[opus_vision_optimizer.py]('./opus_vision_optimizer.py)
Batches images optimally for Opus (respects token/image limits)
Generates context-aware prompts for each batch
Handles tile continuity ("this is tile r2c1 of a 3×3 grid...")
Multiple extraction modes: full takeoff, dimensions only, schedule extract, verification
Returns ImageBatch objects with .get_api_content() ready for Claude API

## Quick usage:
pythonfrom opus_vision_optimizer import OpusVisionOptimizer, ExtractionMode

optimizer = OpusVisionOptimizer(default_dpi=180)
prep = optimizer.prepare_for_extraction(
    "complex_plan.pdf",
    mode=ExtractionMode.FULL_TAKEOFF
)

for batch in prep.batches:
    # batch.get_api_content() → ready for Claude API
    # batch.context_prompt includes tile position, scale, extraction instructions
    pass
For dense regions (schedules, dimension clusters):
pythonprep = optimizer.prepare_region(
    "drawing.pdf",
    page_number=0,
    region=(100, 200, 400, 500),  # points
    zoom_factor=2.0,
    mode=ExtractionMode.SCHEDULE_EXTRACT
)
Dependencies: pip install PyMuPDF pillow