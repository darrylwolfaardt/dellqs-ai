"""
Script to split all PDF files > 2MB in UFHARE project into subfolders.
"""
import sys
import json
sys.path.insert(0, r'C:\Users\darryl\source\repos\dellqs-ai')

from pathlib import Path
from Reference.PDF_Splitter_Module import handle_large_pdf, get_pdf_info

def main():
    base = Path(r'C:\Users\darryl\source\repos\dellqs-ai\Projects\UFHARE')
    large_pdfs = []

    # Find all PDFs > 2MB
    for pdf in base.rglob('*.pdf'):
        size_mb = pdf.stat().st_size / (1024 * 1024)
        if size_mb > 2:
            large_pdfs.append((pdf, size_mb))

    large_pdfs.sort(key=lambda x: -x[1])

    print(f'Processing {len(large_pdfs)} PDF files > 2MB...\n')

    results = []

    for pdf_path, size_mb in large_pdfs:
        # Create subfolder with same name as file (without extension)
        subfolder = pdf_path.parent / pdf_path.stem
        subfolder.mkdir(exist_ok=True)

        print(f'Splitting: {pdf_path.name} ({size_mb:.2f} MB)')
        print(f'  Output: {subfolder.relative_to(base)}')

        # Use handle_large_pdf to split the file
        result = handle_large_pdf(
            file_path=pdf_path,
            output_dir=subfolder,
            max_size_kb=500  # 500KB per part
        )

        if result.success:
            print(f'  Result: {result.split_count} parts created')
            for i, f in enumerate(result.split_files, 1):
                part_size = Path(f).stat().st_size / 1024
                print(f'    Part {i}: {Path(f).name} ({part_size:.1f} KB)')
            results.append({
                'original': str(pdf_path.relative_to(base)),
                'subfolder': str(subfolder.relative_to(base)),
                'parts': [str(Path(p).name) for p in result.split_files],
                'success': True
            })
        else:
            print(f'  ERROR: {result.error_message}')
            results.append({
                'original': str(pdf_path.relative_to(base)),
                'subfolder': str(subfolder.relative_to(base)),
                'error': result.error_message,
                'success': False
            })
        print()

    print(f'\n=== SUMMARY ===')
    print(f'Total files processed: {len(large_pdfs)}')
    print(f'Successful: {sum(1 for r in results if r["success"])}')
    print(f'Failed: {sum(1 for r in results if not r["success"])}')

    # Save results to JSON for later use
    results_file = base / 'split_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nResults saved to: {results_file}')

if __name__ == '__main__':
    main()
