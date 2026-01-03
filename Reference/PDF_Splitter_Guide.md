# PDF Splitter Module Guide

## Purpose

Handle large PDF files that cause **HTTP 413 (Request Too Large)** errors when using Claude Code's `Read` tool.

## When to Use

When you see this error:
```
● Read(path/to/drawing.pdf)
  ⎿  Read PDF (787.6KB)
  ⎿  API Error: 413
     {"error":{"type":"request_too_large","message":"Request exceeds the maximum size"}}
```

## Quick Usage

### Command Line
```bash
python Reference/PDF_Splitter_Module.py "Projects/path/to/large.pdf" 500
```

### In Python/Claude Code (Recommended)
```python
from Reference.PDF_Splitter_Module import handle_large_pdf, cleanup_split_files

# Smart handler - automatically chooses best strategy
result = handle_large_pdf("path/to/large_drawing.pdf")

if result.success:
    # Process each file (PDF parts or rendered images)
    for part_file in result.split_files:
        # Read and process each part
        pass

    # Optional: cleanup temp files when done
    cleanup_split_files(result)
```

## Available Functions

| Function | Description |
|----------|-------------|
| `handle_large_pdf(file_path)` | **Recommended** - Smart handler that chooses best strategy |
| `split_for_api(file_path)` | Auto-splits multi-page PDFs for API compatibility |
| `render_pdf_to_image(file_path, dpi, format)` | Render PDF to images (for single-page large PDFs) |
| `split_pdf_by_size(file_path, max_size_kb)` | Split to stay under size limit |
| `split_pdf_by_pages(file_path, pages_per_split)` | Split by page count |
| `split_pdf_single_pages(file_path)` | One page per file |
| `is_pdf_too_large(file_path)` | Check if handling is needed |
| `get_pdf_info(file_path)` | Get size (KB) and page count |
| `cleanup_split_files(result)` | Remove temp files |

## Smart Strategy

`handle_large_pdf()` automatically chooses the best approach:

| Scenario | Strategy |
|----------|----------|
| PDF is under size limit | Return original file |
| Multi-page large PDF | Split into smaller PDFs |
| Single-page large PDF | Render to image (PNG/JPG) |

## Default Limits

- **Max Size**: 500 KB per file
- **Default DPI**: 150 (for image rendering)
- **Max Pages**: 5 pages per split (when using page-based split)

## Workflow for 413 Errors

1. **Detect**: Read tool returns 413 error
2. **Handle**: Use `handle_large_pdf()` to process
3. **Process**: Read each output file individually
4. **Combine**: Aggregate results from all parts
5. **Cleanup**: Remove temporary files

## Examples

### Multi-page PDF (split into parts)
```
Split 'Multi-Page-Plans.pdf' (1.2MB, 8 pages) into 3 parts

Split files:
  1. Multi-Page-Plans_part01.pdf (298.4 KB)
  2. Multi-Page-Plans_part02.pdf (412.1 KB)
  3. Multi-Page-Plans_part03.pdf (477.1 KB)
```

### Single-page large PDF (rendered to image)
```
Rendered 'A-(14)1000-Ceiling Plan(2).pdf' (787.6KB, 1 page) to image

Output files:
  1. A-(14)1000-Ceiling Plan(2)_page01.png (1.2 MB)
```

### Using JPEG for smaller images
```python
result = handle_large_pdf("drawing.pdf", image_format="jpg", render_dpi=100)
# Smaller file size due to JPEG compression and lower DPI
```

## Dependencies

- PyMuPDF: `pip install PyMuPDF`
