"""
UFH Finance Office Conversion - BOQ Generator
Based on DQRules and QS-Task-Template measurements
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from Reference.QSPlus_Export_Module import BOQItem, QSPlusExporter

# Project Details
project_name = 'UFH - Alice Campus Finance Office Conversion'
project_number = 'P20002-00'

# Create exporter
exporter = QSPlusExporter(project_name, project_number)

items = []

# ============================================================
# 1. ALTERATIONS & DEMOLITIONS
# ============================================================

items.append(BOQItem(
    item_number='1.1',
    section='ALTERATIONS',
    subsection='Removals',
    description='Remove existing internal brick walls including making good',
    unit='m2',
    quantity=85.0,
    rate=0.00,
    calculation_notes='Estimated internal walls: 28m length x 3.0m height',
    reference_drawing='A-(01)1002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='1.2',
    section='ALTERATIONS',
    subsection='Removals',
    description='Remove existing floor finishes',
    unit='m2',
    quantity=398.0,
    rate=0.00,
    calculation_notes='Full internal floor area',
    reference_drawing='A-(01)1002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='1.3',
    section='ALTERATIONS',
    subsection='Removals',
    description='Remove existing ceiling finishes',
    unit='m2',
    quantity=398.0,
    rate=0.00,
    calculation_notes='Full internal ceiling area',
    reference_drawing='A-(01)1002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='1.4',
    section='ALTERATIONS',
    subsection='Removals',
    description='Remove existing doors and frames',
    unit='No',
    quantity=12.0,
    rate=0.00,
    calculation_notes='Existing doors to be removed',
    reference_drawing='A-(01)1002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='1.5',
    section='ALTERATIONS',
    subsection='Removals',
    description='Remove existing sanitary fittings including disconnection',
    unit='No',
    quantity=8.0,
    rate=0.00,
    calculation_notes='WCs, WHBs to be removed',
    reference_drawing='A-(01)1002',
    measurement_rule='DQRule'
))

# ============================================================
# 2. FOUNDATIONS
# ============================================================

items.append(BOQItem(
    item_number='2.1',
    section='FOUNDATIONS',
    subsection='Excavations',
    description='Excavate for surface trenches 450mm wide x 600mm deep',
    unit='m3',
    quantity=17.55,
    rate=0.00,
    calculation_notes='65m new walls x 0.45m wide x 0.60m deep',
    reference_drawing='S-01-25055-20-001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='2.2',
    section='FOUNDATIONS',
    subsection='Excavations',
    description='Risk of collapse to sides of excavations <=1.5m deep',
    unit='m2',
    quantity=78.0,
    rate=0.00,
    calculation_notes='65m x 0.6m depth x 2 sides',
    reference_drawing='S-01-25055-20-001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='2.3',
    section='FOUNDATIONS',
    subsection='Concrete',
    description='Mass concrete 25MPa in strip footings 450 x 200mm',
    unit='m3',
    quantity=5.85,
    rate=0.00,
    calculation_notes='65m x 0.45m x 0.20m',
    reference_drawing='S-01-25055-20-001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='2.4',
    section='FOUNDATIONS',
    subsection='Brickwork',
    description='Brickwork in foundations one brick wall',
    unit='m2',
    quantity=26.0,
    rate=0.00,
    calculation_notes='65m x 0.4m height',
    reference_drawing='S-01-25055-20-001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='2.5',
    section='FOUNDATIONS',
    subsection='Filling',
    description='Backfilling to trenches with selected material',
    unit='m3',
    quantity=8.78,
    rate=0.00,
    calculation_notes='Excavation less concrete and brickwork',
    reference_drawing='S-01-25055-20-001',
    measurement_rule='DQRule'
))

# ============================================================
# 3. SURFACE BEDS
# ============================================================

items.append(BOQItem(
    item_number='3.1',
    section='SURFACE BEDS',
    subsection='Filling',
    description='Filling beneath floors compacted in 150mm layers',
    unit='m3',
    quantity=18.0,
    rate=0.00,
    calculation_notes='120m2 x 0.15m thick',
    reference_drawing='S-01-25055-20-002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='3.2',
    section='SURFACE BEDS',
    subsection='Filling',
    description='Compaction to filling',
    unit='m2',
    quantity=120.0,
    rate=0.00,
    calculation_notes='Area of new surface beds',
    reference_drawing='S-01-25055-20-002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='3.3',
    section='SURFACE BEDS',
    subsection='DPM',
    description='250 micron plastic dampproof membrane',
    unit='m2',
    quantity=120.0,
    rate=0.00,
    calculation_notes='Under new surface beds',
    reference_drawing='S-01-25055-20-002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='3.4',
    section='SURFACE BEDS',
    subsection='Concrete',
    description='Concrete 25MPa in surface beds 100mm thick',
    unit='m3',
    quantity=12.0,
    rate=0.00,
    calculation_notes='120m2 x 0.10m',
    reference_drawing='S-01-25055-20-002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='3.5',
    section='SURFACE BEDS',
    subsection='Reinforcement',
    description='Ref 193 fabric reinforcement in surface beds',
    unit='m2',
    quantity=120.0,
    rate=0.00,
    calculation_notes='Area of new surface beds',
    reference_drawing='S-01-25055-20-002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='3.6',
    section='SURFACE BEDS',
    subsection='Surface Treatment',
    description='Power float finish to surface beds',
    unit='m2',
    quantity=120.0,
    rate=0.00,
    calculation_notes='Top surface of new beds',
    reference_drawing='S-01-25055-20-002',
    measurement_rule='DQRule'
))

# ============================================================
# 4. BRICKWORK STRUCTURE
# ============================================================

items.append(BOQItem(
    item_number='4.1',
    section='BRICKWORK',
    subsection='DPC',
    description='Dampproof course 230mm wide under walls',
    unit='m2',
    quantity=14.95,
    rate=0.00,
    calculation_notes='65m length x 0.23m wide',
    reference_drawing='S-01-25055-20-003',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='4.2',
    section='BRICKWORK',
    subsection='Walls',
    description='Half-brick walls in stock bricks',
    unit='m2',
    quantity=195.0,
    rate=0.00,
    calculation_notes='65m x 3.0m height',
    reference_drawing='A-(11)1000',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='4.3',
    section='BRICKWORK',
    subsection='Reinforcement',
    description='Brick reinforcement (brickforce) to walls',
    unit='m',
    quantity=573.3,
    rate=0.00,
    calculation_notes='195m2 x 2.94m per m2',
    reference_drawing='A-(11)1000',
    measurement_rule='DQRule'
))

# ============================================================
# 5. WALL FINISHES
# ============================================================

items.append(BOQItem(
    item_number='5.1',
    section='WALL FINISHES',
    subsection='Plaster',
    description='12mm Cement plaster to walls',
    unit='m2',
    quantity=620.0,
    rate=0.00,
    calculation_notes='New walls 390m2 + existing 280m2 - openings 50m2',
    reference_drawing='A-(51)1001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='5.2',
    section='WALL FINISHES',
    subsection='Paint',
    description='One coat primer and two coats PVA paint to walls',
    unit='m2',
    quantity=580.0,
    rate=0.00,
    calculation_notes='Plastered walls less tiled areas',
    reference_drawing='A-(51)1001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='5.3',
    section='WALL FINISHES',
    subsection='Tiling',
    description='Ceramic wall tiles to ablutions full height',
    unit='m2',
    quantity=85.0,
    rate=0.00,
    calculation_notes='WC areas perimeter x 2.4m height',
    reference_drawing='A-(51)1001',
    measurement_rule='DQRule'
))

# ============================================================
# 6. FLOOR FINISHES
# ============================================================

items.append(BOQItem(
    item_number='6.1',
    section='FLOOR FINISHES',
    subsection='Screed',
    description='40mm Cement screed to floors',
    unit='m2',
    quantity=368.0,
    rate=0.00,
    calculation_notes='398m2 total - 30m2 veranda',
    reference_drawing='A-(52)1001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='6.2',
    section='FLOOR FINISHES',
    subsection='Tiles',
    description='Ceramic floor tiles including adhesive bedding',
    unit='m2',
    quantity=188.0,
    rate=0.00,
    calculation_notes='Offices, passages, ablutions',
    reference_drawing='A-(52)1001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='6.3',
    section='FLOOR FINISHES',
    subsection='Carpet',
    description='Carpet tiles to consulting and waiting areas',
    unit='m2',
    quantity=154.0,
    rate=0.00,
    calculation_notes='Student Consulting 64m2 + Waiting 90m2',
    reference_drawing='A-(52)1001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='6.4',
    section='FLOOR FINISHES',
    subsection='Skirtings',
    description='75mm Ceramic tile skirting',
    unit='m',
    quantity=320.0,
    rate=0.00,
    calculation_notes='Perimeter of tiled areas',
    reference_drawing='A-(52)1002',
    measurement_rule='DQRule'
))

# ============================================================
# 7. CEILING FINISHES
# ============================================================

items.append(BOQItem(
    item_number='7.1',
    section='CEILINGS',
    subsection='Suspended Ceiling',
    description='600x600mm Suspended ceiling tiles on exposed grid',
    unit='m2',
    quantity=368.0,
    rate=0.00,
    calculation_notes='Internal ceiling area',
    reference_drawing='A-(14)1000',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='7.2',
    section='CEILINGS',
    subsection='Paint',
    description='One coat primer and two coats PVA paint to ceilings',
    unit='m2',
    quantity=368.0,
    rate=0.00,
    calculation_notes='Internal ceiling area',
    reference_drawing='A-(14)1000',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='7.3',
    section='CEILINGS',
    subsection='Bulkheads',
    description='Gypsum board bulkheads including framing',
    unit='m',
    quantity=45.0,
    rate=0.00,
    calculation_notes='Bulkheads at service areas',
    reference_drawing='A-(14)1000',
    measurement_rule='DQRule'
))

# ============================================================
# 8. DOORS
# ============================================================

doors = [
    ('D01', 'Custom Aluminium glazed door 1800x2350mm', 2),
    ('D02', 'Custom Aluminium glazed door', 1),
    ('D03', 'Custom Aluminium glazed door', 1),
    ('D04', 'Custom Aluminium glazed door', 1),
    ('D05', 'Custom Aluminium glazed door', 1),
    ('D06', 'Custom Aluminium glazed door', 1),
    ('D07', 'Custom Aluminium glazed door', 1),
    ('D08', 'Custom Aluminium glazed door', 1),
    ('G01', 'Steel security gate', 1),
    ('G02', 'Steel security gate', 1),
]

for i, (mark, desc, qty) in enumerate(doors, start=1):
    items.append(BOQItem(
        item_number=f'8.{i}',
        section='DOORS',
        subsection='Supply and Install',
        description=f'{desc} Type {mark} complete with frame and hardware',
        unit='No',
        quantity=float(qty),
        rate=0.00,
        calculation_notes=f'As per fenestration schedule {mark}',
        reference_drawing=f'A-(31)500{i}',
        measurement_rule='DQRule'
    ))

items.append(BOQItem(
    item_number='8.11',
    section='DOORS',
    subsection='Lintels',
    description='Precast concrete lintels over door openings',
    unit='m',
    quantity=22.0,
    rate=0.00,
    calculation_notes='11 door openings x 2.0m average',
    reference_drawing='A-(11)1000',
    measurement_rule='DQRule'
))

# ============================================================
# 9. WINDOWS & SHOPFRONTS
# ============================================================

items.append(BOQItem(
    item_number='9.1',
    section='WINDOWS',
    subsection='Supply and Install',
    description='Custom Aluminium glazed window W01 600x2805mm high',
    unit='No',
    quantity=6.0,
    rate=0.00,
    calculation_notes='Type W01 as per schedule',
    reference_drawing='A-(35)5001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='9.2',
    section='WINDOWS',
    subsection='Supply and Install',
    description='Custom Aluminium glazed windows W02-W06 various sizes',
    unit='No',
    quantity=12.0,
    rate=0.00,
    calculation_notes='Types W02-W06 as per schedule',
    reference_drawing='A-(35)5002-5006',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='9.3',
    section='WINDOWS',
    subsection='Shopfronts',
    description='Custom Aluminium glazed shopfront SF01-SF09',
    unit='No',
    quantity=9.0,
    rate=0.00,
    calculation_notes='Types SF01-SF09 as per schedule',
    reference_drawing='A-(32)5001-5009',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='9.4',
    section='WINDOWS',
    subsection='Lintels',
    description='Precast concrete lintels over window/shopfront openings',
    unit='m',
    quantity=35.0,
    rate=0.00,
    calculation_notes='Window and shopfront openings',
    reference_drawing='A-(11)1000',
    measurement_rule='DQRule'
))

# ============================================================
# 10. JOINERY & FITTINGS
# ============================================================

items.append(BOQItem(
    item_number='10.1',
    section='JOINERY',
    subsection='Fixed Furniture',
    description='Security desk JT01 complete',
    unit='No',
    quantity=1.0,
    rate=0.00,
    calculation_notes='As per joinery schedule',
    reference_drawing='A-(74)6001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='10.2',
    section='JOINERY',
    subsection='Fixed Furniture',
    description='Kitchenette unit JT02 complete',
    unit='No',
    quantity=1.0,
    rate=0.00,
    calculation_notes='As per joinery schedule',
    reference_drawing='A-(74)6002',
    measurement_rule='DQRule'
))

# ============================================================
# 11. PLUMBING
# ============================================================

items.append(BOQItem(
    item_number='11.1',
    section='PLUMBING',
    subsection='Sanitary Fittings',
    description='WC suite complete with seat, cistern and connections',
    unit='No',
    quantity=6.0,
    rate=0.00,
    calculation_notes='Male 2 + Female 2 + UA 1 + Staff 1',
    reference_drawing='A-(50)6001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='11.2',
    section='PLUMBING',
    subsection='Sanitary Fittings',
    description='Wash hand basin complete with taps and trap',
    unit='No',
    quantity=6.0,
    rate=0.00,
    calculation_notes='As per ablution layout',
    reference_drawing='A-(50)6001',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='11.3',
    section='PLUMBING',
    subsection='Sanitary Fittings',
    description='Stainless steel sink unit to kitchenette',
    unit='No',
    quantity=1.0,
    rate=0.00,
    calculation_notes='Kitchenette area',
    reference_drawing='A-(74)6002',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='11.4',
    section='PLUMBING',
    subsection='Pipework',
    description='Sanitary plumbing installation complete (provisional)',
    unit='Item',
    quantity=1.0,
    rate=0.00,
    calculation_notes='Provisional sum',
    reference_drawing='A-(50)6001',
    measurement_rule='DQRule'
))

# ============================================================
# 12. ELECTRICAL
# ============================================================

items.append(BOQItem(
    item_number='12.1',
    section='ELECTRICAL',
    subsection='Installation',
    description='Electrical installation complete (provisional)',
    unit='Item',
    quantity=1.0,
    rate=0.00,
    calculation_notes='Provisional sum',
    reference_drawing='Electrical',
    measurement_rule='DQRule'
))

# ============================================================
# 13. EXTERNAL WORKS
# ============================================================

items.append(BOQItem(
    item_number='13.1',
    section='EXTERNAL WORKS',
    subsection='Paving',
    description='Interlocking concrete block paving',
    unit='m2',
    quantity=90.0,
    rate=0.00,
    calculation_notes='Student outside waiting area',
    reference_drawing='A-(11)1000',
    measurement_rule='DQRule'
))

items.append(BOQItem(
    item_number='13.2',
    section='EXTERNAL WORKS',
    subsection='Paving',
    description='Paving layerworks 150mm thick compacted',
    unit='m2',
    quantity=90.0,
    rate=0.00,
    calculation_notes='Under paving',
    reference_drawing='Paving',
    measurement_rule='DQRule'
))

# ============================================================
# EXPORT
# ============================================================

exporter.add_items(items)

# Create output directory
output_dir = os.path.join(os.path.dirname(__file__), 'Final Bills of Quantities')
os.makedirs(output_dir, exist_ok=True)

date_stamp = datetime.now().strftime('%Y%m%d')

# Export to Excel
excel_file = exporter.export_to_excel(
    os.path.join(output_dir, f'UFH_Finance_Office_BOQ_QSPlus_{date_stamp}.xlsx'),
    include_calculations=True
)
print(f'Excel BOQ exported: {excel_file}')

# Export to CSV
csv_file = exporter.export_to_csv(
    os.path.join(output_dir, f'UFH_Finance_Office_BOQ_Backup_{date_stamp}.csv'),
    include_calculations=True
)
print(f'CSV backup exported: {csv_file}')

# Print summary
print(f'\nBOQ SUMMARY')
print(f'===========')
print(f'Project: {project_name}')
print(f'Project No: {project_number}')
print(f'Total items: {len(items)}')

from collections import Counter
sections = Counter(item.section for item in items)
print(f'\nItems by section:')
for section, count in sorted(sections.items()):
    print(f'  {section}: {count} items')
