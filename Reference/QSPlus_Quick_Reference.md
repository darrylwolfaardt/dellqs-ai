# QSPlus Export - Quick Reference Card

## Installation

```bash
# Required for Excel export only
pip install openpyxl
```

## Basic Usage

```python
from Reference.QSPlus_Export_Module import BOQItem, export_boq_to_qsplus

# Create BOQ items
items = [
    BOQItem(
        item_number="1.1",
        section="FOUNDATIONS",
        description="Clear site - 2m beyond perimeter",
        unit="m2",
        quantity=150.5,
        rate=25.00
    )
]

# Export to QSPlus Excel format
excel_file = export_boq_to_qsplus(
    items=items,
    output_path="outputs/Project_BOQ.xlsx",
    project_name="My Project",
    project_number="PROJ-001",
    format="excel"
)
```

## Supported Formats

| Format | File Extension | Best For |
|--------|----------------|----------|
| Excel  | `.xlsx` | QSPlus import (recommended) |
| CSV    | `.csv` | Simple import, backup |
| XML    | `.xml` | System integration |
| JSON   | `.json` | Web/API applications |

## BOQItem Fields

### Required
- `item_number` - Item ID (e.g., "1.1")
- `description` - Item description
- `unit` - Unit (m2, m3, m, No, t, tonnes)

### Optional
- `quantity` - Measured quantity (default: 0.0)
- `rate` - Unit rate (default: 0.0)
- `amount` - Total (auto-calculated)
- `section` - Major section
- `subsection` - Minor section
- `calculation_notes` - How calculated
- `reference_drawing` - Drawing ref
- `measurement_rule` - Rule applied

## Common Units

- **m2** - Square meters (areas)
- **m3** - Cubic meters (volumes)
- **m** - Linear meters (lengths)
- **No** - Number (count items)
- **t** or **tonnes** - Tonnes (heavy materials)

## Quick Export Function

```python
# One-line export
output = export_boq_to_qsplus(
    items=my_items,
    output_path="outputs/BOQ.xlsx",
    project_name="Project Name",
    project_number="PROJ-001",
    format="excel",              # or "csv", "xml", "json"
    include_calculations=True    # or False for clean output
)
```

## Testing

```bash
# Run test script
python Reference/test_qsplus_export.py
```

## Output Location

All exports go to: `outputs/` directory

## File Naming Convention

Recommended format:
```
outputs/ProjectName_BOQ_QSPlus_2025-12-06.xlsx
outputs/ProjectNumber_Final_BOQ.csv
```

## Import into QSPlus

1. Export with `include_calculations=False` for clean import
2. Open QSPlus software
3. File → Import → Bill of Quantities
4. Select exported Excel file
5. Map columns if prompted
6. Verify totals

## Troubleshooting

**Excel export fails:**
```bash
pip install openpyxl
```

**CSV works but Excel doesn't:**
Use CSV format instead - fully compatible with QSPlus

## Documentation

- Full Guide: `Reference/QSPlus_Export_Guide.md`
- Module Code: `Reference/QSPlus_Export_Module.py`
- Task Template: `Reference/QS-Task-Template.md`
- Test Script: `Reference/test_qsplus_export.py`

---

**Version:** 1.0
**Updated:** 2025-12-06
