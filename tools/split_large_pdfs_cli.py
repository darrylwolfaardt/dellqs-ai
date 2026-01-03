#!/usr/bin/env python
"""
Command-line tool to split large PDF files into smaller parts.

Usage:
    python split_large_pdfs_cli.py <directory> [options]

Examples:
    # Split all PDFs > 2MB in a directory
    python split_large_pdfs_cli.py "Projects/UFHARE"

    # Split PDFs > 5MB with 1MB max part size
    python split_large_pdfs_cli.py "Projects/UFHARE" --threshold 5 --max-size 1000

    # Dry run to see what would be split
    python split_large_pdfs_cli.py "Projects/UFHARE" --dry-run
"""
import sys
import json
import argparse
from pathlib import Path

# Add the project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Reference.PDF_Splitter_Module import handle_large_pdf, get_pdf_info


def find_large_pdfs(directory: Path, threshold_mb: float) -> list:
    """Find all PDFs larger than threshold in directory."""
    large_pdfs = []

    for pdf in directory.rglob('*.pdf'):
        try:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            if size_mb > threshold_mb:
                large_pdfs.append((pdf, size_mb))
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not access {pdf}: {e}")

    # Sort by size descending
    large_pdfs.sort(key=lambda x: -x[1])
    return large_pdfs


def split_pdf(pdf_path: Path, output_dir: Path, max_size_kb: int, verbose: bool = True) -> dict:
    """Split a single PDF file."""
    result = handle_large_pdf(
        file_path=pdf_path,
        output_dir=output_dir,
        max_size_kb=max_size_kb
    )

    if result.success:
        parts_info = []
        for f in result.split_files:
            part_path = Path(f)
            part_size = part_path.stat().st_size / 1024
            parts_info.append({
                'name': part_path.name,
                'size_kb': round(part_size, 1)
            })

        return {
            'original': str(pdf_path),
            'output_dir': str(output_dir),
            'parts': parts_info,
            'split_count': result.split_count,
            'success': True
        }
    else:
        return {
            'original': str(pdf_path),
            'output_dir': str(output_dir),
            'error': result.error_message,
            'success': False
        }


def main():
    parser = argparse.ArgumentParser(
        description='Split large PDF files into smaller parts.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Projects/UFHARE"
      Split all PDFs > 2MB in the directory

  %(prog)s "Projects/UFHARE" --threshold 5 --max-size 1000
      Split PDFs > 5MB into 1MB parts

  %(prog)s "Projects/UFHARE" --dry-run
      Show what would be split without doing it

  %(prog)s "Projects/UFHARE" --single "path/to/file.pdf"
      Split only a specific PDF file
        """
    )

    parser.add_argument(
        'directory',
        type=str,
        help='Directory to search for PDF files (relative to project root or absolute)'
    )

    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=2.0,
        help='Size threshold in MB (default: 2.0)'
    )

    parser.add_argument(
        '-m', '--max-size',
        type=int,
        default=500,
        help='Maximum size per split part in KB (default: 500)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default=None,
        help='Output directory for all splits (default: subfolder next to each PDF)'
    )

    parser.add_argument(
        '-s', '--single',
        type=str,
        default=None,
        help='Split a single PDF file instead of scanning directory'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be split without actually splitting'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output'
    )

    parser.add_argument(
        '--json',
        type=str,
        default=None,
        help='Save results to JSON file'
    )

    args = parser.parse_args()

    # Resolve directory
    directory = Path(args.directory)
    if not directory.is_absolute():
        directory = PROJECT_ROOT / directory

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    # Handle single file mode
    if args.single:
        single_path = Path(args.single)
        if not single_path.is_absolute():
            single_path = directory / single_path

        if not single_path.exists():
            print(f"Error: File not found: {single_path}")
            sys.exit(1)

        size_mb = single_path.stat().st_size / (1024 * 1024)
        large_pdfs = [(single_path, size_mb)]
    else:
        # Find all large PDFs
        large_pdfs = find_large_pdfs(directory, args.threshold)

    if not large_pdfs:
        print(f"No PDF files > {args.threshold}MB found in {directory}")
        sys.exit(0)

    # Display what will be processed
    if not args.quiet:
        print(f"\n{'='*60}")
        print(f"PDF Splitter - Found {len(large_pdfs)} file(s) to process")
        print(f"{'='*60}")
        print(f"Directory: {directory}")
        print(f"Threshold: {args.threshold} MB")
        print(f"Max part size: {args.max_size} KB")
        print(f"{'='*60}\n")

        for pdf_path, size_mb in large_pdfs:
            rel_path = pdf_path.relative_to(directory) if pdf_path.is_relative_to(directory) else pdf_path
            print(f"  {rel_path} ({size_mb:.2f} MB)")
        print()

    if args.dry_run:
        print("Dry run complete. No files were modified.")
        sys.exit(0)

    # Process each PDF
    results = []
    success_count = 0
    fail_count = 0

    for pdf_path, size_mb in large_pdfs:
        # Determine output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
            if not output_dir.is_absolute():
                output_dir = directory / output_dir
            output_dir = output_dir / pdf_path.stem
        else:
            output_dir = pdf_path.parent / pdf_path.stem

        output_dir.mkdir(parents=True, exist_ok=True)

        if not args.quiet:
            rel_path = pdf_path.relative_to(directory) if pdf_path.is_relative_to(directory) else pdf_path
            print(f"Splitting: {rel_path} ({size_mb:.2f} MB)")
            print(f"  Output: {output_dir}")

        result = split_pdf(pdf_path, output_dir, args.max_size)
        results.append(result)

        if result['success']:
            success_count += 1
            if not args.quiet:
                print(f"  Created {result['split_count']} parts:")
                for part in result['parts']:
                    print(f"    - {part['name']} ({part['size_kb']} KB)")
        else:
            fail_count += 1
            if not args.quiet:
                print(f"  ERROR: {result['error']}")

        if not args.quiet:
            print()

    # Summary
    if not args.quiet:
        print(f"{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Total processed: {len(large_pdfs)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {fail_count}")

    # Save JSON results if requested
    if args.json:
        json_path = Path(args.json)
        if not json_path.is_absolute():
            json_path = directory / json_path

        with open(json_path, 'w') as f:
            json.dump({
                'directory': str(directory),
                'threshold_mb': args.threshold,
                'max_size_kb': args.max_size,
                'results': results
            }, f, indent=2)

        if not args.quiet:
            print(f"\nResults saved to: {json_path}")

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == '__main__':
    main()
