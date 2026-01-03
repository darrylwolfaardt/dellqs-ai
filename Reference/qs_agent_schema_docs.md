# QS Agent Database Schema Documentation

## Overview

This database schema is designed for a Quantity Surveying (QS) AI Agent that automates Bill of Quantities (BOQ) production from architectural drawings. It's based primarily on the **ASAQS 7th Edition (2015)** Standard System of Measuring Building Work, with mappings to NRM1 for UK project compatibility.

## ASAQS 7th Edition Trade Structure

The ASAQS 7th Edition defines **21 trade sections** (not 41 as previously suggested). Here's the complete hierarchy:

### Trade Sections (from Model Preambles for Trades 2008)

| Code | Trade Name | Key Coverage |
|------|------------|--------------|
| A | General | Abbreviations, materials standards, workmanship |
| B | Alterations | Taking down, removals, making good |
| C | Earthworks | Demolitions, excavations, filling, soil treatment |
| D | Concrete, Formwork and Reinforcement | In-situ concrete per SANS 1200G |
| E | Precast Concrete | Precast elements, terrazzo finishes |
| F | Masonry | Brickwork, blockwork, mortar classes |
| G | Waterproofing | DPC, tanking, membrane systems |
| H | Roof Coverings etc | Tiles, sheeting, flashings |
| I | Carpentry and Joinery | Timber, doors, frames, trusses |
| J | Ceilings, Partitions and Access Flooring | Suspended systems, dry walls |
| K | Floor Coverings, Wall Linings, etc | Vinyl, carpet, timber flooring |
| L | Ironmongery | Locks, hinges, door furniture |
| M | Structural Steelwork | Per SANS 1200H/HA |
| N | Metalwork | Windows, doors, balustrades |
| O | Plastering | Screeds, renders, granolithic, terrazzo |
| P | Tiling | Wall and floor tiles |
| Q | Plumbing and Drainage | Pipes, fittings, sanitary ware |
| R | Glazing | Glass, mirrors, putty |
| S | Paintwork | Primers, undercoats, finishes |
| T | Paperhanging | Wallpaper |
| U | External Works | Landscaping, roads, fencing |

### Measurement Order (ASAQS Rule 4.3)

Within each trade section, items are arranged by:
1. **Mass** (tonnes, kg)
2. **Volume** (m³)
3. **Area** (m²)
4. **Length** (m)
5. **Number** (No, Item)

Items within each category are ordered by approximate value (cheapest first).

## Database Schema Hierarchy

```
measurement_standards
    └── trade_sections (21 ASAQS trades)
        └── trade_sub_sections (clauses like C.1, C.2)
            └── boq_item_templates (reusable standard items)
                └── boq_items (actual measured quantities in projects)

nrm_group_elements (0-8)
    └── nrm_elements (1.1, 2.1, 2.2, etc.)

projects
    └── bills (Bill No. 1, 2, etc.)
        └── bill_sections (trade sections within bills)
            └── boq_items

dimension_sheets
    └── dimension_items (traditional taking off)

source_documents
    └── document_extractions (AI-extracted elements)
```

## Key SANS/SABS References (from Model Preambles)

### Masonry (Trade F)
- SANS 227 - Burnt clay masonry units
- SANS 1215 - Concrete masonry units
- SANS 523 - Limes for building
- SANS 1090 - Fine aggregates for mortar
- SANS 10249 - Masonry walling

### Concrete (Trade D)
- SANS 1200G - Concrete work specification
- SANS 794 - Low density aggregates
- SANS 1024 - Welded steel fabric reinforcement

### Metalwork (Trade N)
- SANS 727 - Steel windows and doors
- SANS 121 - Hot-dip galvanized coatings
- SANS 1129 - Steel door frames
- SANS 999 - Anodized aluminium coatings

### Plumbing (Trade Q)
- SANS 10252 - Water supply and drainage
- SANS 791 - PVC-U sewer pipes
- SANS 967 - PVC-U soil, waste and vent pipes
- SANS 497 - Glazed ceramic sanitary ware

## Mortar Classes (ASAQS Table F.8)

| Class | Min Strength (MPa) | Common Cement | Masonry Cement |
|-------|-------------------|---------------|----------------|
| I | 10 | 1:4 | 1:3 |
| II | 5 | 1:6 | 1:5 |
| III | 1.5 | 1:9 | 1:6 |

## Concrete Mix Classifications (ASAQS Table D.5.5.1.6)

| Class | Est. Strength (MPa) | Max Aggregate (mm) | Cement:Sand:Stone |
|-------|---------------------|-------------------|-------------------|
| A | 7 | 37.5 | 1:4:8 |
| B | 15 | 19 | 1:3:5 |
| C | 20 | 19 | 1:2.5:3.5 |

## Agent Integration Points

### 1. Document Processing Flow
```
source_documents (upload PDF/DWG)
    → AI extraction → document_extractions
    → Template matching → boq_item_templates
    → Quantity assignment → boq_items
    → QS verification → dimension_items (if needed)
```

### 2. Key Queries for Agent

**Find matching template for extracted element:**
```sql
SELECT * FROM boq_item_templates
WHERE to_tsvector('english', short_description || ' ' || full_description) 
      @@ plainto_tsquery('english', 'half brick wall');
```

**Get trade section for element type:**
```sql
SELECT ts.code, ts.name, tss.code, tss.name
FROM trade_sections ts
JOIN trade_sub_sections tss ON tss.trade_section_id = ts.id
WHERE ts.code = 'F';  -- Masonry
```

**Calculate bill totals:**
```sql
SELECT b.bill_number, b.name, SUM(bi.amount) as total
FROM bills b
JOIN bill_sections bs ON bs.bill_id = b.id
JOIN boq_items bi ON bi.bill_section_id = bs.id
WHERE b.project_id = :project_id
GROUP BY b.id, b.bill_number, b.name;
```

### 3. NRM1 Elemental Mapping

The schema includes `trade_element_mapping` to convert trade-based BOQs to elemental cost analysis:

| ASAQS Trade | Typical NRM1 Element |
|-------------|---------------------|
| C Earthworks | 1.1 Substructure |
| D Concrete | 1.1, 2.1, 2.2, 2.3 |
| F Masonry | 2.5, 2.7 |
| I Carpentry | 2.3, 2.4, 2.8 |
| Q Plumbing | 5.1-5.4 |
| S Paintwork | 3.1, 3.2, 3.3 |

## South African Context Notes

1. **JBCC Contract** - Most common building contract form
2. **Primary currency** - ZAR (South African Rand)
3. **Regional variations** - Rates vary significantly between Gauteng, Western Cape, KZN
4. **Labour-intensive requirements** - Some government projects require EPWP compliance
5. **BEE considerations** - May affect subcontractor selection

## Extension Points for BMAD Module

1. **Specialist agents can query:**
   - `boq_item_templates` for standard descriptions
   - `cost_rates` for budget estimates
   - `trade_sub_sections` for measurement rules

2. **Document extraction agent outputs to:**
   - `document_extractions` table
   - Links to `suggested_template_id`

3. **Measurement agent uses:**
   - `dimension_items` for detailed taking off
   - `boq_items` for final quantities

4. **Review/QA agent checks:**
   - Verification flags in `document_extractions`
   - Completeness of `bill_sections`
