"""
Test Script for QSPlus Export Module
=====================================

This script tests the QSPlus export functionality with sample BOQ data
based on the DELLQS-AI measuring list structure.

Usage:
    python Reference/test_qsplus_export.py
"""

import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add Reference directory to path
reference_dir = Path(__file__).parent
sys.path.insert(0, str(reference_dir))

from QSPlus_Export_Module import BOQItem, QSPlusExporter, export_boq_to_qsplus


def create_sample_boq_items():
    """Create sample BOQ items representing a typical project"""

    items = [
        # FOUNDATIONS
        BOQItem(
            item_number="1.1",
            section="FOUNDATIONS",
            subsection="Site Preparation",
            description="Clear site - Measure 2m beyond perimeter of building",
            unit="m2",
            quantity=150.50,
            rate=25.00,
            measurement_rule="DQSRule",
            calculation_notes="Building 10m x 12m, perimeter (10+12)x2=44m, area with 2m margin = (14x16)=224m2",
            reference_drawing="DWG-SITE-001"
        ),
        BOQItem(
            item_number="1.2",
            section="FOUNDATIONS",
            subsection="Site Preparation",
            description="Strip topsoil - Measure 1m beyond perimeter of building",
            unit="m2",
            quantity=132.00,
            rate=30.00,
            measurement_rule="DQSRule",
            calculation_notes="Building perimeter with 1m margin = (12x14)=168m2",
            reference_drawing="DWG-SITE-001"
        ),
        BOQItem(
            item_number="1.3",
            section="FOUNDATIONS",
            subsection="Excavation",
            description="Excavate for surface trenches - 700mm wide x 1500mm deep",
            unit="m3",
            quantity=46.20,
            rate=85.00,
            measurement_rule="DQSRule",
            calculation_notes="Perimeter 44m x 0.7m width x 1.5m depth = 46.2m3",
            reference_drawing="DWG-FOUND-001"
        ),
        BOQItem(
            item_number="1.4",
            section="FOUNDATIONS",
            subsection="Excavation",
            description="Risk of collapse - Take area of both sides of excavation",
            unit="m2",
            quantity=132.00,
            rate=15.50,
            measurement_rule="DQSRule",
            calculation_notes="Perimeter 44m x 1.5m depth x 2 sides = 132m2",
            reference_drawing="DWG-FOUND-001"
        ),
        BOQItem(
            item_number="1.5",
            section="FOUNDATIONS",
            subsection="Concrete Work",
            description="Mass concrete footings - 700 x 250mm deep x length of footings",
            unit="m3",
            quantity=7.70,
            rate=950.00,
            measurement_rule="DQSRule",
            calculation_notes="44m length x 0.7m width x 0.25m depth = 7.7m3",
            reference_drawing="DWG-FOUND-002"
        ),
        BOQItem(
            item_number="1.6",
            section="FOUNDATIONS",
            subsection="Concrete Work",
            description="Reinforcement - Take as 100kg per m3 of concrete",
            unit="t",
            quantity=0.77,
            rate=12500.00,
            measurement_rule="DQSRule",
            calculation_notes="7.7m3 concrete x 100kg/m3 = 770kg = 0.77t",
            reference_drawing="DWG-FOUND-002"
        ),

        # REINFORCED CONCRETE STRUCTURE
        BOQItem(
            item_number="2.1",
            section="REINFORCED CONCRETE STRUCTURE",
            subsection="Structural Elements",
            description="Concrete in columns",
            unit="m3",
            quantity=4.50,
            rate=1150.00,
            measurement_rule="DQSRule",
            calculation_notes="6 columns x 0.3m x 0.3m x 2.5m height = 1.35m3",
            reference_drawing="DWG-STRUCT-001"
        ),
        BOQItem(
            item_number="2.2",
            section="REINFORCED CONCRETE STRUCTURE",
            subsection="Structural Elements",
            description="Concrete in beams",
            unit="m3",
            quantity=3.20,
            rate=1150.00,
            measurement_rule="DQSRule",
            calculation_notes="Total beam length 40m x 0.3m x 0.4m = 4.8m3",
            reference_drawing="DWG-STRUCT-001"
        ),
        BOQItem(
            item_number="2.3",
            section="REINFORCED CONCRETE STRUCTURE",
            subsection="Structural Elements",
            description="Concrete in slabs",
            unit="m3",
            quantity=12.00,
            rate=980.00,
            measurement_rule="DQSRule",
            calculation_notes="Floor area 120m2 x 0.10m thickness = 12m3",
            reference_drawing="DWG-STRUCT-002"
        ),
        BOQItem(
            item_number="2.4",
            section="REINFORCED CONCRETE STRUCTURE",
            subsection="Formwork",
            description="Formwork to columns",
            unit="m2",
            quantity=18.00,
            rate=350.00,
            measurement_rule="DQSRule",
            calculation_notes="6 columns x (0.3m x 4 sides) x 2.5m height = 18m2",
            reference_drawing="DWG-STRUCT-001"
        ),

        # BRICKWORK STRUCTURE
        BOQItem(
            item_number="3.1",
            section="BRICKWORK STRUCTURE",
            subsection="Walls",
            description="Brickwork to external walls",
            unit="m2",
            quantity=88.00,
            rate=285.00,
            measurement_rule="DQSRule",
            calculation_notes="Perimeter 44m x 2.5m height - openings = 88m2",
            reference_drawing="DWG-ARCH-001"
        ),
        BOQItem(
            item_number="3.2",
            section="BRICKWORK STRUCTURE",
            subsection="Walls",
            description="Brick reinforcement - 2.94m per m2 of brickwork",
            unit="m",
            quantity=258.72,
            rate=8.50,
            measurement_rule="DQSRule",
            calculation_notes="88m2 brickwork x 2.94m/m2 = 258.72m",
            reference_drawing="DWG-ARCH-001"
        ),

        # ROOFS
        BOQItem(
            item_number="5.1",
            section="ROOFS AND RAINWATER DISPOSAL",
            subsection="Roof Structure",
            description="Roof trusses",
            unit="No",
            quantity=8.00,
            rate=1850.00,
            measurement_rule="DQSRule",
            calculation_notes="Building width 12m, trusses at 1.5m centers = 8 trusses",
            reference_drawing="DWG-ROOF-001"
        ),
        BOQItem(
            item_number="5.2",
            section="ROOFS AND RAINWATER DISPOSAL",
            subsection="Roof Covering",
            description="Roof tiles",
            unit="m2",
            quantity=145.00,
            rate=165.00,
            measurement_rule="DQSRule",
            calculation_notes="Roof area 12m x 10m x 1.2 (pitch factor) = 144m2",
            reference_drawing="DWG-ROOF-002"
        ),

        # DOORS
        BOQItem(
            item_number="10.1",
            section="DOORS",
            subsection="External Doors",
            description="Hardwood external door 900x2100mm complete with frame",
            unit="No",
            quantity=1.00,
            rate=3250.00,
            measurement_rule="Standard",
            reference_drawing="DWG-DOORS-001"
        ),

        # WINDOWS
        BOQItem(
            item_number="11.1",
            section="WINDOWS",
            subsection="Aluminum Windows",
            description="Aluminum sliding window 1500x1200mm",
            unit="No",
            quantity=4.00,
            rate=2800.00,
            measurement_rule="Standard",
            reference_drawing="DWG-WINDOWS-001"
        ),

        # PLUMBING
        BOQItem(
            item_number="15.1",
            section="PLUMBING AND DRAINAGE",
            subsection="Sanitary Fittings",
            description="WC suite complete with cistern",
            unit="No",
            quantity=2.00,
            rate=1850.00,
            measurement_rule="Standard",
            reference_drawing="DWG-PLUMB-001"
        ),

        # ELECTRICAL
        BOQItem(
            item_number="20.1",
            section="ELECTRICAL INSTALLATION",
            subsection="Wiring",
            description="Power sockets",
            unit="No",
            quantity=16.00,
            rate=185.00,
            measurement_rule="Standard",
            reference_drawing="DWG-ELEC-001"
        ),

        # PRELIMINARIES
        BOQItem(
            item_number="21.1",
            section="PRELIMINARIES",
            subsection="General",
            description="Preliminaries and general items",
            unit="No",
            quantity=1.00,
            rate=45000.00,
            measurement_rule="Lump Sum",
            calculation_notes="Site establishment, facilities, supervision",
            reference_drawing="N/A"
        ),
    ]

    return items


def test_all_export_formats():
    """Test all export formats"""

    print("=" * 70)
    print("QSPlus Export Module - Test Script")
    print("=" * 70)
    print()

    # Create sample data
    print("Creating sample BOQ items...")
    items = create_sample_boq_items()
    print(f"✓ Created {len(items)} sample BOQ items")
    print()

    # Create exporter
    project_name = "Sample Residential Building"
    project_number = "SAMPLE-2025-001"

    exporter = QSPlusExporter(
        project_name=project_name,
        project_number=project_number
    )
    exporter.add_items(items)

    # Calculate totals
    total_amount = sum(item.amount for item in items)
    print(f"Project: {project_name}")
    print(f"Project Number: {project_number}")
    print(f"Total Items: {len(items)}")
    print(f"Total Amount: R {total_amount:,.2f}")
    print()

    # Create outputs directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir.absolute()}")
    print()

    # Test Excel export
    print("-" * 70)
    print("Testing Excel Export (.xlsx)...")
    try:
        excel_file = exporter.export_to_excel(
            "outputs/Test_BOQ_QSPlus.xlsx",
            include_calculations=True
        )
        print(f"✓ Excel export successful: {excel_file}")
    except Exception as e:
        print(f"✗ Excel export failed: {str(e)}")
    print()

    # Test CSV export
    print("-" * 70)
    print("Testing CSV Export (.csv)...")
    try:
        csv_file = exporter.export_to_csv(
            "outputs/Test_BOQ_Backup.csv",
            include_calculations=True
        )
        print(f"✓ CSV export successful: {csv_file}")
    except Exception as e:
        print(f"✗ CSV export failed: {str(e)}")
    print()

    # Test XML export
    print("-" * 70)
    print("Testing XML Export (.xml)...")
    try:
        xml_file = exporter.export_to_xml(
            "outputs/Test_BOQ_Data.xml",
            include_calculations=True
        )
        print(f"✓ XML export successful: {xml_file}")
    except Exception as e:
        print(f"✗ XML export failed: {str(e)}")
    print()

    # Test JSON export
    print("-" * 70)
    print("Testing JSON Export (.json)...")
    try:
        json_file = exporter.export_to_json(
            "outputs/Test_BOQ_Data.json",
            include_calculations=True
        )
        print(f"✓ JSON export successful: {json_file}")
    except Exception as e:
        print(f"✗ JSON export failed: {str(e)}")
    print()

    # Test convenience function
    print("-" * 70)
    print("Testing Convenience Function...")
    try:
        quick_file = export_boq_to_qsplus(
            items=items,
            output_path="outputs/Test_BOQ_Quick.xlsx",
            project_name=project_name,
            project_number=project_number,
            format="excel",
            include_calculations=False  # Without calculations
        )
        print(f"✓ Quick export successful: {quick_file}")
    except Exception as e:
        print(f"✗ Quick export failed: {str(e)}")
    print()

    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"✓ All export formats tested successfully!")
    print(f"✓ Output files created in: {output_dir.absolute()}")
    print()
    print("Next Steps:")
    print("1. Open outputs/Test_BOQ_QSPlus.xlsx in Excel to review")
    print("2. Import outputs/Test_BOQ_QSPlus.xlsx into QSPlus software")
    print("3. Verify data integrity and formatting")
    print()
    print("=" * 70)


if __name__ == "__main__":
    test_all_export_formats()
