"""
UFH BOQ to QSPlus Export Script
================================
Parses the consolidated BOQ markdown and exports to QSPlus-compatible Excel format.

Author: Claude AI
Date: 2026-01-04
"""

import sys
import re
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from Reference.QSPlus_Export_Module import BOQItem, QSPlusExporter


def parse_boq_markdown(md_file: str) -> list:
    """
    Parse BOQ items from markdown file.

    Returns list of BOQItem objects.
    """
    items = []

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Track current section and subsection
    current_bill = ""
    current_section = ""
    current_subsection = ""

    # Split by lines
    lines = content.split('\n')

    # Patterns
    bill_pattern = re.compile(r'^#\s+BILL(?:\s+NO\.?\s*)?\s*[-:]?\s*(\d+)?\s*[-–—]?\s*(.+)$', re.IGNORECASE)
    section_pattern = re.compile(r'^##\s+([\d.]+)\s+(.+)$')
    subsection_pattern = re.compile(r'^##\s+([A-Z]+\.?\d*)\s+(.+)$')

    # Table row pattern - matches item rows
    # Format: | Item | Description | Unit | Qty | or | Item | Description | Amount |
    table_row_pattern = re.compile(r'^\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')

    in_table = False
    table_headers = []

    for i, line in enumerate(lines):
        line = line.strip()

        # Check for bill header (# BILL NO. X - NAME)
        bill_match = bill_pattern.match(line)
        if bill_match:
            bill_num = bill_match.group(1) or ""
            bill_name = bill_match.group(2).strip()
            current_bill = f"BILL {bill_num} - {bill_name}" if bill_num else bill_name
            current_section = current_bill
            current_subsection = ""
            in_table = False
            continue

        # Check for section header (## X.X NAME)
        section_match = section_pattern.match(line)
        if section_match:
            sec_num = section_match.group(1)
            sec_name = section_match.group(2).strip()
            current_subsection = f"{sec_num} {sec_name}"
            in_table = False
            continue

        # Check for alternate section header (## XX.X NAME)
        alt_section = re.match(r'^##\s+([A-Z]+[.\d]*)\s+(.+)$', line)
        if alt_section:
            sec_num = alt_section.group(1)
            sec_name = alt_section.group(2).strip()
            current_subsection = f"{sec_num} {sec_name}"
            in_table = False
            continue

        # Check for table header row
        if '|' in line and ('Item' in line or 'Description' in line):
            # This is likely a header row
            parts = [p.strip() for p in line.split('|') if p.strip()]
            table_headers = parts
            in_table = True
            continue

        # Skip separator rows
        if line.startswith('|') and set(line.replace('|', '').replace('-', '').replace(':', '').strip()) == set():
            continue
        if '---' in line and '|' in line:
            continue

        # Parse data rows
        if in_table and line.startswith('|') and not line.startswith('|-'):
            parts = [p.strip() for p in line.split('|')]
            # Remove empty parts at start/end
            parts = [p for p in parts if p]

            if len(parts) >= 3:
                item_col = parts[0] if len(parts) > 0 else ""
                desc_col = parts[1] if len(parts) > 1 else ""

                # Skip summary/total rows
                if item_col.startswith('**') or 'Total' in item_col or item_col == '':
                    continue

                # Skip header-like rows
                if item_col.lower() in ['item', 'item no', 'item no.']:
                    continue

                # Determine format based on headers/content
                unit = ""
                quantity = 0.0
                rate = 0.0
                amount = 0.0

                # Standard BOQ format: Item | Description | Unit | Qty
                if len(parts) >= 4:
                    unit_col = parts[2] if len(parts) > 2 else ""
                    qty_col = parts[3] if len(parts) > 3 else ""

                    # Check if this is standard format or P.Sum format
                    if unit_col in ['m2', 'm3', 'm', 'No', 't', 'kg', 'L', 'Item', 'P.Sum']:
                        unit = unit_col
                        # Parse quantity
                        try:
                            qty_str = qty_col.replace(',', '').replace('R', '').strip()
                            quantity = float(qty_str)
                        except (ValueError, AttributeError):
                            quantity = 0.0
                    elif unit_col.startswith('R') or unit_col.replace(',', '').replace('.', '').isdigit():
                        # This might be Amount (R) column for Provisional Sums
                        unit = "P.Sum"
                        try:
                            amt_str = unit_col.replace(',', '').replace('R', '').strip()
                            amount = float(amt_str)
                            quantity = 1
                        except:
                            amount = 0.0

                # Skip if no valid item number pattern
                if not re.match(r'^[A-Z]*[.\d]+', item_col) and not item_col.startswith('PS'):
                    continue

                # Create BOQItem
                item = BOQItem(
                    item_number=item_col,
                    section=current_section,
                    subsection=current_subsection,
                    description=desc_col,
                    unit=unit,
                    quantity=quantity,
                    rate=rate,
                    amount=amount,
                    measurement_rule="ASAQS SSM7 / DQRules"
                )
                items.append(item)

    return items


def main():
    """Main export function"""

    # File paths
    base_dir = Path(__file__).parent
    md_file = base_dir / "UFH_CONSOLIDATED_BOQ_DRAFT.md"
    output_dir = base_dir / "QSPlus_Export"
    output_dir.mkdir(exist_ok=True)

    print(f"Parsing BOQ from: {md_file}")

    # Parse BOQ items
    items = parse_boq_markdown(str(md_file))
    print(f"Extracted {len(items)} BOQ items")

    # Create exporter
    exporter = QSPlusExporter(
        project_name="UFH Alice Campus - Finance Offices Conversion",
        project_number="UFH-FINANCE-2026"
    )
    exporter.add_items(items)

    # Export to Excel (primary format for QSPlus)
    excel_file = output_dir / "UFH_BOQ_QSPlus.xlsx"
    try:
        result = exporter.export_to_excel(str(excel_file), include_calculations=True)
        print(f"[OK] Excel export created: {result}")
    except ImportError as e:
        print(f"[ERROR] Excel export failed (openpyxl not installed): {e}")
        print("  Installing openpyxl...")

    # Export to CSV as backup
    csv_file = output_dir / "UFH_BOQ_QSPlus.csv"
    result = exporter.export_to_csv(str(csv_file), include_calculations=True)
    print(f"[OK] CSV export created: {result}")

    # Export to JSON for reference
    json_file = output_dir / "UFH_BOQ_QSPlus.json"
    result = exporter.export_to_json(str(json_file), include_calculations=True)
    print(f"[OK] JSON export created: {result}")

    # Print summary
    print("\n" + "="*60)
    print("EXPORT SUMMARY")
    print("="*60)
    print(f"Total items exported: {len(items)}")

    # Count by section
    sections = {}
    for item in items:
        sec = item.section
        sections[sec] = sections.get(sec, 0) + 1

    print("\nItems by section:")
    for sec, count in sections.items():
        print(f"  - {sec}: {count} items")

    print("\n" + "="*60)
    print("Files created:")
    print(f"  1. {excel_file}")
    print(f"  2. {csv_file}")
    print(f"  3. {json_file}")
    print("="*60)


if __name__ == "__main__":
    main()
