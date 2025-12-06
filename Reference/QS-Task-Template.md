# Quantity Surveyor Documentation Task Template

This template outlines the standard sequence of tasks for completing quantity surveyor documentation for new building construction projects. Tasks are organized by construction phase and follow the DELLQS-AI measuring list structure.

## Task Execution Guidelines

- Complete tasks in sequential order within each section
- Apply measurement rules (DQSRule/DBRule) as specified
- Record quantities with appropriate units (m2, m3, m, No, t, tonnes)
- Verify calculations against architectural drawings
- Document all assumptions and deviations

### Reference Folder Usage (CRITICAL)

**ALWAYS** rely on the `Reference/` folder for:
- **Export Tools**: Use `Reference/QSPlus_Export_Module.py` for all BOQ exports
- **Export Formats**: Follow `Reference/QSPlus_Export_Guide.md` for correct formatting
- **Measurement Standards**: Apply measurement rules from Reference documentation
- **Templates**: Use standard templates and structures provided in Reference folder
- **Never create custom export functions** - use the provided Python export module

### Output Directory Structure

**MANDATORY**: All BOQ output files must be saved to:
- Location: `[ProjectFolder]/Final Bills of Quantities/`
- The folder `Final Bills of Quantities` must be created if it does not exist
- Use project-relative paths, not absolute paths
- Include date stamps in filenames: `[ProjectName]_BOQ_QSPlus_[YYYYMMDD].xlsx`

---

## 1. FOUNDATIONS

### Site Preparation
- [ ] **Clear site** - Measure 2m beyond perimeter of building (m2)
- [ ] **Strip topsoil** - Measure 1m beyond perimeter of building (m2)
- [ ] **Excavate for surface trenches, holes** - Take strip footing excavation 700mm wide x 1500mm deep (m3)
- [ ] **Risk of collapse** - Take area of both sides of excavation (m2)
- [ ] **Compaction** - Area of bottom of excavation for surface trenches (m2)
- [ ] **Soil poisoning to trench excavations** - Measure bottom area + area of both sides of excavation (m2)

### Material Management
- [ ] **Backfilling** - Take volume of excavation less (volume of brickwork in foundations and volume of concrete in foundations) (m3)
- [ ] **Cart away** - Volume of excavated material (m3)

### Testing
- [ ] **Compaction tests** - Area of bottom of excavation (No)
- [ ] **Soil material tests** - Take as one per 10m of footing excavation (No)

### Concrete Work
- [ ] **Mass concrete footings** - Measure 700 x 250mm deep x length of footings (m3)
- [ ] **Reinforced concrete bases, ground beams** (m3)
- [ ] **Formwork to sides of ground beams, bases** (m2)
- [ ] **Reinforcement** - Take as 100kg per m3 of concrete (t)

### Brickwork
- [ ] **Brickwork in foundations** - Take as one brick wall, measure as depth of excavation - 250mm thick concrete + 100mm thick surface bed (m2)
- [ ] **Brickforce** - Take as 2.94m per m2 of brickwork (m)
- [ ] **Extra over ordinary brickwork for facings in foundations** (m2)

---

## 2. REINFORCED CONCRETE STRUCTURE

### Structural Elements
- [ ] **Columns** (m3)
- [ ] **Beams** (m3)
- [ ] **Slabs** (m3)
- [ ] **Formwork** - Take as both sides of excavation (m2)
- [ ] **Reinforcement** - Take as 100kg/m3 of concrete (tonnes)

### Floor Finishes
- [ ] **Powerfloat** - Measure top area of floor (m2)
- [ ] **Broomswept finish to concrete** - Measure top area of floor (m2)

---

## 3. BRICKWORK STRUCTURE

- [ ] **DPC Dampproof course** - Length of trench excavation x 200mm wide (m2)
- [ ] **Brickwork to walls** (m2)
- [ ] **Brick reinforcement** - Taken as 2.94m per m2 of brickwork (m2)
- [ ] **Airbricks** (No)
- [ ] **Extra over ordinary brickwork for facings** - Measure surface of brickwork over walls and halfway into reveals (m2)
- [ ] **Hoop iron ties, truss ties** - 2 per timber roof truss (No)

---

## 4. SURFACE BED CONSTRUCTION

### Base Preparation
- [ ] **Filling beneath floors** - Measure over area of building (m3)
- [ ] **Compaction** (m2)
- [ ] **Soil poisoning beneath surface beds** (m2)
- [ ] **50mm Thick Sandbed** (m2)
- [ ] **Dampproof membrane** (m2)

### Concrete Work
- [ ] **Concrete in surface beds** - Floor area x 0.10m (m3)
- [ ] **Formwork to edges not exceeding 300mm high** - Taken at doorways only (m)
- [ ] **Reinforcing mesh to surface beds** - Area of floor (m2)
- [ ] **Sawcuts** (m)
- [ ] **Movement joints** (m)

### Surface Finishes
- [ ] **Float top surfaces, to falls and patterns** - Area of floor (m2)
- [ ] **Powerfloat** - Area of floor (m2)

---

## 5. ROOFS AND RAINWATER DISPOSAL

### Roof Structure
- [ ] **Wallplates** (m)
- [ ] **Tie downs** (No)
- [ ] **Trusses** (No)
- [ ] **Cross bracing** - Measure as Width of building x 3 (m)
- [ ] **Longitudinal bracing** - Times length of building x 1.4 for raking length (m)
- [ ] **Purlins** (m)
- [ ] **Dakseal** (m2)
- [ ] **Battens** (m2)
- [ ] **Tilting fillet** (m)
- [ ] **Hurricane clips** - One per intersection of truss and purlin (No)
- [ ] **Roof tiles** (m2)

### Rainwater System
- [ ] **Gutters** (m)
- [ ] **Outlets** - One outlet per downpipe (No)
- [ ] **Angles** - Take one per 90 degree corner (No)
- [ ] **Stopped ends** (No)
- [ ] **Downpipes** (m)
- [ ] **Eaves projections** - One per downpipe (No)
- [ ] **Bends** - Two per downpipe (No)
- [ ] **Shoes** - One per downpipe (No)
- [ ] **Precast rainwater channel** - One per downpipe (m)

---

## 6. EXTERNAL FINISHES

- [ ] **Extra over ordinary brickwork for facings** (m2)
- [ ] **Beamfilling**
- [ ] **Plaster** (m2)
- [ ] **Paint to walls** (m2)

---

## 7. INTERNAL FLOOR FINISHES

- [ ] **Grano** (m2)
- [ ] **Screed** (m2)
- [ ] **Carpet** (m2)
- [ ] **Tiles** (m2)
- [ ] **Skirtings** (m)
- [ ] **Varnish on skirtings not exceeding 300mm girth** (m)

---

## 8. INTERNAL WALL FINISHES

- [ ] **Plaster** (m2)
- [ ] **Airbricks** - One per room (No)
- [ ] **Paint on walls** (m2)
- [ ] **Tiling** (m2)
- [ ] **Dado** (m2)

---

## 9. CEILINGS

- [ ] **Brandering** (m2)
- [ ] **Insulation** (m2)
- [ ] **Ceiling boarding** (m2)
- [ ] **Suspended ceilings** (m2)
- [ ] **Plaster** (m2)
- [ ] **Paint on ceilings** (m2)
- [ ] **Cornices** (m)

---

## 10. DOORS

### Door Installation
- [ ] **Frame** (No)
- [ ] **Door** (No)
- [ ] **Glass to fanlight, sidelight** (m2)
- [ ] **Beading to glass** (m)
- [ ] **Paint on door** (m2)
- [ ] **Paint on frame** (m2)
- [ ] **Ironmongery** (No)
- [ ] **Architrave** (m)
- [ ] **Silicone seal around frame** (m)

### Door Adjustments
- [ ] **Lintel** (m)
- [ ] **Brickforce above lintels**
- [ ] **Deduct brick walls** (m2)
- [ ] **Deduct brick reinforcement** (m)
- [ ] **Close cavities all around** (m)
- [ ] **Deduct external plaster** (m2)
- [ ] **Deduct external finish to walls** (m2)
- [ ] **Deduct internal plaster** (m2)
- [ ] **Deduct internal finish to walls** (m2)
- [ ] **External cill** (m)
- [ ] **Internal cill** (m)
- [ ] **External facings/plaster to reveals** (m2)
- [ ] **External finish to reveals** (m2)
- [ ] **Internal finish to reveals** (m2)
- [ ] **Deduct Tiling to walls** (m2)
- [ ] **Tile reveals** (m)
- [ ] **Trim to tiling edges** (m)
- [ ] **Screed at threshold** (m2)
- [ ] **Brass/alum trim at threshold** (m)

---

## 11. WINDOWS

### Window Installation
- [ ] **Window** (No)
- [ ] **Glazing** (m2)
- [ ] **Beads** (m)
- [ ] **Paint on window** (m2)
- [ ] **Silicone seal around window** (m)

### Window Adjustments
- [ ] **Lintel** (m)
- [ ] **Brickforce over lintels**
- [ ] **Deduct brick walls** (m2)
- [ ] **Deduct brick reinforcement**
- [ ] **Close cavities all around** (m)
- [ ] **Deduct external plaster** (m2)
- [ ] **Deduct external finish to walls** (m2)
- [ ] **Deduct internal plaster** (m2)
- [ ] **Deduct internal finish to walls** (m2)
- [ ] **External cill** (m)
- [ ] **Internal cill** (m)
- [ ] **DPC beneath cill** (m2)
- [ ] **External facings/plaster to reveals** (m2)
- [ ] **External finish to reveals** (m2)
- [ ] **Internal finish to reveals** (m2)
- [ ] **Deduct Tiling to walls** (m2)
- [ ] **Tile reveals** (m)
- [ ] **Trim to tiling edges** (m)

---

## 12. PLAIN OPENINGS

### Plain Opening
- [ ] **Plain opening**

### Plain Opening Adjustments
- [ ] **Lintel** (m)
- [ ] **Brickforce over lintels**
- [ ] **Deduct brick walls** (m2)
- [ ] **Deduct brick reinforcement** (m)
- [ ] **Close cavities all around** (m)
- [ ] **Deduct external plaster** (m2)
- [ ] **Deduct external finish to walls** (m2)
- [ ] **Deduct internal plaster** (m2)
- [ ] **Deduct internal finish to walls** (m2)
- [ ] **External facings/plaster to reveals** (m2)
- [ ] **External finish to reveals** (m2)
- [ ] **Internal finish to reveals** (m2)

---

## 13. JOINERY FITTINGS

- [ ] **Joinery** (No)

---

## 14. SUNDRIES

- [ ] **Mirrors** (No)
- [ ] **Toilet roll holders** (No)
- [ ] **Stainless steel grab rails** (No)

---

## 15. PLUMBING AND DRAINAGE

### Water Supply

#### 5000 Litre Water Tank
- [ ] **Tank** (No)
- [ ] **Tank Stand** (No)

#### Connect water supply from bottom of tank
- [ ] **Class 10 HDPE** (m)
- [ ] **40mm HDPE male nipple** (No)
- [ ] **1 1/2" plastic open/close valve** (No)
- [ ] **40 x 1 1/2" male adaptor** (No)
- [ ] **40mm or other size HDPE pipe** (No)

#### Connect tap only
- [ ] **40mm nipple to tank** (No)
- [ ] **1" plastic open/close valve** (No)
- [ ] **25mm x 1" male adapter** (No)
- [ ] **22mm Copper Class 1 Pipe** (No)
- [ ] **20mm Heavy duty brass hose bibtap** (No)

#### Tank overflow
- [ ] **40mm Nylon Elbow male** (No)
- [ ] **Push on HDPE light duty pipe** (m)

### Sanitary Fittings
- [ ] **WC**
- [ ] **Wash hand basin**
- [ ] **Bath**
- [ ] **Shower**
- [ ] **Urinal**
- [ ] **Sink**

### Sanitary Plumbing
- [ ] **Sanitary plumbing work**

### Soil Drainage
- [ ] **Soil drainage work**

---

## 16. FIRE SERVICES

### Fire Extinguishers
- [ ] **4.5Kg DCP (dry chemical powder) SABS fire extinguisher**
- [ ] **9Kg DCP (dry chemical powder) (Safequip Code M30) SABS fire extinguisher**

### Backing Boards
- [ ] **Backing board Saligna 450mm long for 4.5kg extinguisher**
- [ ] **600mm Long for 9kg extinguisher**

### Fire Hose Reels
- [ ] **Step down to 38mm galvanised piping**
- [ ] **38x25mm Reducer**
- [ ] **25mm galvanised pipe and fittings**

#### Fire hose reel SABS certified
- [ ] **30m Hose to SANS1086**
- [ ] **Wall mounting bracket**
- [ ] **Hose guide**
- [ ] **Durable nozzle**
- [ ] **Stopcock**
- [ ] **Instantaneous adapter (includes male and female fittings)**
- [ ] **Double door hose reel cabinet, size 850x250x850mm, with closed back**

### Fire Hydrant
- [ ] **HDPE to 80mm galvanised pipe adaptor**
- [ ] **80mm Diameter galvanised pipe**
- [ ] **80mm Tamper proof hydrant valve with handwheel**
- [ ] **Woodlands WHS-80 Right Angle Valve and Single Lug Outlet**
- [ ] **Concrete hydrant**

---

## 17. SUNDRY METAL WORK ITEMS

- [ ] **Balustrades** (m)

---

## 18. EXTERNAL WORKS

- [ ] **Hoardings** (m)
- [ ] **Platforms** (m3)
- [ ] **Fencing and gates** (m)
- [ ] **Roads** (m2)
- [ ] **Paving** (m2)
- [ ] **Aprons** (m2)
- [ ] **Stormwater drainage** (m)
- [ ] **Water supply reticulation** (m)
- [ ] **Fire supply reticulation** (m)
- [ ] **Soil drainage reticulation** (m)

---

## 19. BUILDERS WORK TO SPECIALIST INSTALLATIONS

- [ ] **Chasing for electrical conduits** (m)
- [ ] **Building in distribution board** (No)
- [ ] **50mm Sleeves through walls** (No)
- [ ] **100mm Sleeves through walls** (No)

---

## 20. ELECTRICAL INSTALLATION

- [ ] **Conduits** (m)
- [ ] **Wiring** (m)
- [ ] **Power sockets** (No)
- [ ] **Light switches** (No)
- [ ] **Light fittings** (No)
- [ ] **Distribution board** (No)
- [ ] **Breakers** (No)
- [ ] **Cable from power supply pole to dist board** (m)

---

## 21. PRELIMINARIES

- [ ] **Preliminaries** (No)

---

## 22. HEALTH AND SAFETY

### Stage 1 - Design
- [ ] **Baseline Risk Assessment by H&S Agent**
- [ ] **Risk Register set up right at design start**

### Costs of H&S
- [ ] **Type of building - risks**
- [ ] **Client insurance for construction method**
- [ ] **Liability Insurance for design team incl QS**

---

## Notes for AI Agents

### Measurement Rules Reference
- **DQSRule** = Dell Quantity Surveyor Rule (specific to this measuring methodology)
- **DBRule** = Dell Builder Rule (construction-specific measurement approach)

### Common Measurement Principles
1. Always measure from architectural drawings
2. Apply deductions (Ddt) for openings, voids, and overlaps
3. Calculate reinforcement as specified ratios (e.g., 100kg/m3 for concrete)
4. Include waste factors as per project specifications
5. Verify all calculations before finalizing

### Output Format
When completing this template, provide:
- Item description
- Quantity calculated
- Unit of measurement
- Calculation method/formula used
- Reference to drawing number and detail

### Required Output Files
After completing any BOQ task, the following files MUST be generated:

**IMPORTANT**: All output files must be saved to the project-relative folder `Final Bills of Quantities/`. Create this folder if it does not exist.

1. **QSPlus Excel Export** (Primary)
   - Format: Excel (.xlsx)
   - Include: All calculations, measurement rules, and references
   - Location: `[ProjectFolder]/Final Bills of Quantities/[ProjectName]_BOQ_QSPlus_[Date].xlsx`
   - Purpose: Import into QSPlus estimating software

2. **CSV Backup Export** (Secondary)
   - Format: CSV (.csv)
   - Include: Full calculation details
   - Location: `[ProjectFolder]/Final Bills of Quantities/[ProjectName]_BOQ_Backup_[Date].csv`
   - Purpose: Data backup and alternative import format

3. **Summary Report** (Optional)
   - Format: Markdown or PDF
   - Include: Project summary, totals, key assumptions
   - Location: `[ProjectFolder]/Final Bills of Quantities/[ProjectName]_Summary_[Date].md`

### Export Workflow
**ALWAYS** use the tools and formats provided in the `Reference/` folder:

1. **QSPlus Export Module**: `Reference/QSPlus_Export_Module.py`
2. **Export Guide**: `Reference/QSPlus_Export_Guide.md`
3. **Standard Formats**: All templates and measurement rules in `Reference/`

Use the QSPlus Export Module as follows:

```python
import os
from datetime import datetime
from Reference.QSPlus_Export_Module import BOQItem, export_boq_to_qsplus

# Define output directory (project-relative)
output_dir = "Final Bills of Quantities"
os.makedirs(output_dir, exist_ok=True)

# Generate timestamp for files
date_stamp = datetime.now().strftime("%Y%m%d")

# After completing BOQ calculations, create BOQ items
boq_items = [
    BOQItem(
        item_number="1.1",
        section="FOUNDATIONS",
        description="...",
        unit="m2",
        quantity=calculated_qty,
        rate=unit_rate,
        calculation_notes="...",
        measurement_rule="DQSRule"
    ),
    # ... more items
]

# Export to QSPlus Excel format
excel_file = export_boq_to_qsplus(
    items=boq_items,
    output_path=f"{output_dir}/{project_name}_BOQ_QSPlus_{date_stamp}.xlsx",
    project_name=project_name,
    project_number=project_number,
    format="excel",
    include_calculations=True
)

# Export CSV backup
csv_file = export_boq_to_qsplus(
    items=boq_items,
    output_path=f"{output_dir}/{project_name}_BOQ_Backup_{date_stamp}.csv",
    project_name=project_name,
    project_number=project_number,
    format="csv",
    include_calculations=True
)
```

**IMPORTANT REMINDER**: Always consult `Reference/QSPlus_Export_Guide.md` for detailed usage instructions and ensure all Reference folder tools are used as documented.

---

**Document Version:** 1.2
**Source:** Measuring List - Ron.csv
**Last Updated:** 2025-12-06
**Changes in v1.2:**
- Added mandatory Reference folder usage guidelines
- Updated output directory to "Final Bills of Quantities" (project-relative)
- Enhanced export workflow with folder creation and date stamping
- Clarified that agents must use Reference/QSPlus_Export_Module.py for all exports
