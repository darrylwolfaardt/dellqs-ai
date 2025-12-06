# QSPlus Export Module - User Guide

## Overview

The QSPlus Export Module provides comprehensive functionality to export Bill of Quantities (BOQ) data from DELLQS-AI in formats compatible with QSPlus estimating software and other industry-standard BOQ applications.

**File Location:** `Reference/QSPlus_Export_Module.py`
**Version:** 1.0
**Date:** 2025-12-06

---

## Supported Export Formats

| Format | Extension | Description | Best For |
|--------|-----------|-------------|----------|
| **Excel** | .xlsx | Fully formatted spreadsheet with styling | QSPlus import, professional reports |
| **CSV** | .csv | Simple comma-separated values | Data exchange, simple imports |
| **XML** | .xml | Structured XML document | System integration, data backup |
| **JSON** | .json | JavaScript Object Notation | API integration, web applications |

---

## Installation Requirements

### Required Python Packages

```bash
# Core requirement for Excel export
pip install openpyxl

# The module uses these standard library modules (no installation needed):
# - csv
# - json
# - xml.etree.ElementTree
# - xml.dom.minidom
# - datetime
# - pathlib
# - typing
```

---

## Quick Start

### Basic Usage Example

```python
from Reference.QSPlus_Export_Module import BOQItem, QSPlusExporter

# Create BOQ items
items = [
    BOQItem(
        item_number="1.1",
        section="FOUNDATIONS",
        subsection="Site Preparation",
        description="Clear site - 2m beyond perimeter",
        unit="m2",
        quantity=150.5,
        rate=25.00,
        measurement_rule="DQSRule"
    )
]

# Create exporter
exporter = QSPlusExporter(
    project_name="New Office Building",
    project_number="PROJ-2025-001"
)

# Add items
exporter.add_items(items)

# Export to Excel (recommended for QSPlus)
excel_file = exporter.export_to_excel("outputs/BOQ_QSPlus.xlsx")
print(f"BOQ exported to: {excel_file}")
```

---

## Detailed Usage

### Creating BOQ Items

The `BOQItem` class represents a single line item in the Bill of Quantities.

#### BOQItem Parameters

```python
BOQItem(
    item_number: str,        # Item identifier (e.g., "1.1", "2.3.1")
    description: str,        # Item description
    unit: str,              # Unit of measurement (m2, m3, m, No, t, tonnes)
    quantity: float,        # Measured quantity
    rate: float,            # Unit rate/price
    amount: float,          # Total amount (auto-calculated if not provided)
    section: str,           # Major section (e.g., "FOUNDATIONS")
    subsection: str,        # Minor section (e.g., "Site Preparation")
    calculation_notes: str, # How quantity was calculated
    reference_drawing: str, # Drawing reference number
    measurement_rule: str   # Rule applied (DQSRule, DBRule, etc.)
)
```

#### Example: Creating Different Item Types

```python
# Foundation excavation item
excavation = BOQItem(
    item_number="1.3",
    section="FOUNDATIONS",
    subsection="Excavation",
    description="Excavate for surface trenches - 700mm wide x 1500mm deep",
    unit="m3",
    quantity=15.4,
    rate=85.00,
    measurement_rule="DQSRule",
    calculation_notes="Perimeter 44m x 0.7m width x 1.5m depth",
    reference_drawing="DWG-001"
)

# Concrete work item
concrete = BOQItem(
    item_number="2.1",
    section="REINFORCED CONCRETE STRUCTURE",
    subsection="Structural Elements",
    description="Concrete in columns",
    unit="m3",
    quantity=12.5,
    rate=950.00,
    measurement_rule="DQSRule"
)

# Finishing item
plastering = BOQItem(
    item_number="8.1",
    section="INTERNAL WALL FINISHES",
    description="Plaster to walls",
    unit="m2",
    quantity=245.0,
    rate=125.00
)
```

### Using the QSPlusExporter Class

#### Initialize Exporter

```python
exporter = QSPlusExporter(
    project_name="Residential Complex Phase 2",
    project_number="RC-PHASE2-2025"
)
```

#### Add Items

```python
# Add single item
exporter.add_item(excavation)

# Add multiple items
exporter.add_items([concrete, plastering])

# Clear all items
exporter.clear_items()
```

#### Export to Different Formats

```python
# Export to Excel (recommended for QSPlus)
excel_path = exporter.export_to_excel(
    output_path="outputs/BOQ_Final.xlsx",
    include_calculations=True  # Include calculation notes and rules
)

# Export to CSV (simple format)
csv_path = exporter.export_to_csv(
    output_path="outputs/BOQ_Simple.csv",
    include_calculations=False  # Exclude calculation details
)

# Export to XML (structured data)
xml_path = exporter.export_to_xml(
    output_path="outputs/BOQ_Data.xml",
    include_calculations=True
)

# Export to JSON (web/API friendly)
json_path = exporter.export_to_json(
    output_path="outputs/BOQ_Data.json",
    include_calculations=True
)
```

---

## Convenience Function

For quick, one-line exports:

```python
from Reference.QSPlus_Export_Module import export_boq_to_qsplus

output_file = export_boq_to_qsplus(
    items=my_boq_items,
    output_path="outputs/Final_BOQ.xlsx",
    project_name="Shopping Mall Construction",
    project_number="SM-2025-03",
    format="excel",  # or "csv", "xml", "json"
    include_calculations=True
)
```

---

## Export Format Specifications

### Excel (.xlsx) Format

**Features:**
- Professional formatting with colored headers
- Section headers with highlighting
- Automatic column width adjustment
- Number formatting for quantities and amounts
- Frozen header row for easy scrolling
- Summary total at bottom

**Column Structure (with calculations):**
1. Item No.
2. Section
3. Subsection
4. Description
5. Unit
6. Quantity
7. Rate
8. Amount
9. Calculation Notes
10. Reference
11. Rule

**Styling:**
- **Header:** Dark blue background, white text, bold
- **Sections:** Light blue background, bold text
- **Data:** Bordered cells, right-aligned numbers
- **Numbers:** Formatted as #,##0.00

### CSV Format

**Structure:**
```
Project: [Project Name]
Project Number: [Project Number]
Date: [Creation Date]
Software: DELLQS-AI

Item Number,Section,Subsection,Description,Unit,Quantity,Rate,Amount,...
1.1,FOUNDATIONS,Site Preparation,Clear site,m2,150.50,25.00,3762.50,...
...

TOTAL,,,,,,,15234.75
```

### XML Format

**Structure:**
```xml
<?xml version="1.0" ?>
<BillOfQuantities>
  <ProjectInformation>
    <ProjectName>...</ProjectName>
    <ProjectNumber>...</ProjectNumber>
    <CreatedDate>...</CreatedDate>
  </ProjectInformation>
  <Items>
    <Item>
      <ItemNumber>1.1</ItemNumber>
      <Description>...</Description>
      <Quantity>150.5</Quantity>
      ...
    </Item>
  </Items>
  <Summary>
    <TotalItems>45</TotalItems>
    <TotalAmount>15234.75</TotalAmount>
  </Summary>
</BillOfQuantities>
```

### JSON Format

**Structure:**
```json
{
  "project_information": {
    "project_name": "...",
    "project_number": "...",
    "created_date": "2025-12-06 10:30:00"
  },
  "items": [
    {
      "Item Number": "1.1",
      "Description": "...",
      "Quantity": 150.5,
      "Rate": 25.0,
      "Amount": 3762.5
    }
  ],
  "summary": {
    "total_items": 45,
    "total_amount": 15234.75
  }
}
```

---

## Integration with DELLQS-AI Workflow

### Automated Export After Task Completion

The QSPlus export should be automatically triggered after completing any BOQ calculation task:

```python
# Example integration in task completion workflow
def complete_boq_task(task_items, project_info):
    # 1. Perform BOQ calculations
    calculated_items = perform_calculations(task_items)

    # 2. Create BOQ items
    boq_items = []
    for item in calculated_items:
        boq_item = BOQItem(
            item_number=item['number'],
            section=item['section'],
            description=item['description'],
            unit=item['unit'],
            quantity=item['quantity'],
            rate=item.get('rate', 0.0),
            calculation_notes=item.get('calc_notes', ''),
            measurement_rule=item.get('rule', '')
        )
        boq_items.append(boq_item)

    # 3. Export to QSPlus format
    output_path = f"outputs/{project_info['name']}_BOQ_QSPlus.xlsx"
    excel_file = export_boq_to_qsplus(
        items=boq_items,
        output_path=output_path,
        project_name=project_info['name'],
        project_number=project_info['number'],
        format="excel",
        include_calculations=True
    )

    # 4. Also export CSV for backup
    csv_file = export_boq_to_qsplus(
        items=boq_items,
        output_path=output_path.replace('.xlsx', '.csv'),
        project_name=project_info['name'],
        project_number=project_info['number'],
        format="csv",
        include_calculations=True
    )

    return excel_file, csv_file
```

---

## Best Practices

### 1. File Naming Convention

Use descriptive, standardized file names:

```python
# Good naming
"ProjectName_BOQ_QSPlus_2025-12-06.xlsx"
"PROJ-001_Final_BOQ.xlsx"
"Shopping_Mall_Phase1_BOQ.csv"

# Avoid
"output.xlsx"
"boq.csv"
"final.xlsx"
```

### 2. Include Calculations for Internal Use

```python
# For internal review and audit trail
exporter.export_to_excel(
    "internal/BOQ_WithCalculations.xlsx",
    include_calculations=True  # Keep all calculation details
)

# For client/QSPlus import (cleaner)
exporter.export_to_excel(
    "client/BOQ_Final.xlsx",
    include_calculations=False  # Remove calculation notes
)
```

### 3. Version Control

```python
from datetime import datetime

# Add timestamp to filename
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"BOQ_{project_number}_{timestamp}.xlsx"
```

### 4. Error Handling

```python
try:
    output_file = exporter.export_to_excel(output_path)
    print(f"✓ BOQ exported successfully: {output_file}")
except Exception as e:
    print(f"✗ Export failed: {str(e)}")
    # Fallback to CSV if Excel fails
    output_file = exporter.export_to_csv(output_path.replace('.xlsx', '.csv'))
```

---

## Common Units of Measurement

| Unit | Description | Typical Use |
|------|-------------|-------------|
| **m2** | Square meters | Areas, surfaces, finishes |
| **m3** | Cubic meters | Volumes, excavation, concrete |
| **m** | Linear meters | Lengths, pipes, beams |
| **No** | Number | Count items, fixtures |
| **t** or **tonnes** | Tonnes | Heavy materials, reinforcement |
| **kg** | Kilograms | Light materials |
| **L** | Liters | Liquids, paints |

---

## Importing into QSPlus

### Step-by-Step Import Process

1. **Prepare the Export**
   ```python
   exporter.export_to_excel("QSPlus_Import.xlsx", include_calculations=False)
   ```

2. **Open QSPlus Software**
   - Launch QSPlus estimating software
   - Create new project or open existing

3. **Import the File**
   - Navigate to: File → Import → Bill of Quantities
   - Select the exported Excel file
   - Map columns if prompted:
     - Item Number → Item No.
     - Description → Description
     - Unit → Unit
     - Quantity → Qty
     - Rate → Rate
     - Amount → Amount

4. **Verify Import**
   - Check total items count
   - Verify total amount matches
   - Review section structure

5. **Apply Rates** (if not included in export)
   - Use QSPlus rate library
   - Apply project-specific rates

---

## Troubleshooting

### Issue: Excel Export Fails

**Solution:**
```bash
pip install openpyxl
# or upgrade
pip install --upgrade openpyxl
```

### Issue: Special Characters Not Displaying

**Solution:**
All exports use UTF-8 encoding. Ensure your viewing software supports UTF-8.

### Issue: Calculations Column Too Wide

**Solution:**
Adjust column width in the module or in Excel after export:
```python
# In QSPlus_Export_Module.py, line ~225
col_widths = [10, 20, 20, 50, 10, 12, 12, 15, 30, 15, 15]  # Reduce from 40 to 30
```

### Issue: QSPlus Can't Read File

**Solutions:**
1. Try CSV format instead of Excel
2. Ensure file is not open in another program
3. Check file permissions
4. Remove special characters from file path

---

## Advanced Usage

### Custom Formatting

Modify the export module to add custom formatting:

```python
# Example: Add custom column
class CustomBOQItem(BOQItem):
    def __init__(self, *args, contractor_notes="", **kwargs):
        super().__init__(*args, **kwargs)
        self.contractor_notes = contractor_notes

    def to_dict(self):
        data = super().to_dict()
        data['Contractor Notes'] = self.contractor_notes
        return data
```

### Batch Export

Export multiple projects:

```python
projects = [
    {'name': 'Project A', 'number': 'PA-001', 'items': items_a},
    {'name': 'Project B', 'number': 'PB-002', 'items': items_b},
]

for project in projects:
    export_boq_to_qsplus(
        items=project['items'],
        output_path=f"batch_exports/{project['number']}_BOQ.xlsx",
        project_name=project['name'],
        project_number=project['number'],
        format="excel"
    )
```

### Filter by Section

Export only specific sections:

```python
# Filter items
foundation_items = [item for item in all_items if item.section == "FOUNDATIONS"]

# Export filtered items
export_boq_to_qsplus(
    items=foundation_items,
    output_path="BOQ_Foundations_Only.xlsx",
    project_name="Project Name - Foundations",
    format="excel"
)
```

---

## Support and Updates

**Documentation Location:** `Reference/QSPlus_Export_Guide.md`
**Module Location:** `Reference/QSPlus_Export_Module.py`
**Version:** 1.0
**Last Updated:** 2025-12-06

For updates or issues, refer to the DELLQS-AI project documentation.

---

## Summary Checklist

- [ ] Install required packages (`pip install openpyxl`)
- [ ] Import the module in your task scripts
- [ ] Create BOQItem objects with complete data
- [ ] Initialize QSPlusExporter with project details
- [ ] Add all BOQ items to exporter
- [ ] Export to desired format (Excel recommended)
- [ ] Verify output file is created
- [ ] Import into QSPlus software
- [ ] Verify data integrity in QSPlus

---

**End of Guide**
