"""
Export Adaptive BOQ to QSPlus Format
====================================

Converts the adaptive BOQ markdown to QSPlus-compatible CSV and XLSX formats.

Usage:
    python export_adaptive_to_qsplus.py
"""

import sys
from pathlib import Path

# Add Reference folder to path for QSPlus module
# Path: Claude Measurements -> MEASUREMENT UFHare -> 1 Pre-Tender -> UFHARE -> Projects -> dellqs-ai
ref_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "Reference"
sys.path.insert(0, str(ref_path))

from QSPlus_Export_Module import BOQItem, QSPlusExporter

# Define all BOQ items from the Adaptive extraction
def get_adaptive_boq_items():
    """Return all BOQ items from the adaptive extraction."""

    items = []

    # ============================================================
    # BILL 4 - EARTHWORKS
    # ============================================================
    items.extend([
        BOQItem("4.1.1", "Clear site of vegetation, grass and weeds", "m2", 250.0,
                section="BILL 4 - EARTHWORKS", subsection="4.1 SITE CLEARANCE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.2.1", "Excavation to reduce levels for surface bed formation, maximum depth not exceeding 2.00m, in earth", "m3", 65.0,
                section="BILL 4 - EARTHWORKS", subsection="4.2 EXCAVATION",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="Verified from adaptive structural drawings +4"),
        BOQItem("4.2.2", "Excavation for strip foundations 600mm wide x 700mm deep, maximum depth not exceeding 2.00m, in earth", "m3", 48.0,
                section="BILL 4 - EARTHWORKS", subsection="4.2 EXCAVATION",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="Verified from foundation layout +3"),
        BOQItem("4.2.3", "Excavation to reduce levels for external paving layerworks, maximum depth not exceeding 500mm, in earth", "m3", 34.0,
                section="BILL 4 - EARTHWORKS", subsection="4.2 EXCAVATION",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.3.1", "Disposal of excavated material off site, including loading and carting away", "m3", 147.0,
                section="BILL 4 - EARTHWORKS", subsection="4.3 DISPOSAL",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="Increased from 140 to 147"),
        BOQItem("4.4.1", "Filling to make up levels under surface beds with approved crushed stone or G5 material, compacted in layers not exceeding 150mm, average thickness 150mm", "m3", 30.0,
                section="BILL 4 - EARTHWORKS", subsection="4.4 FILLING - INTERNAL",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.4.2", "Sand blinding over hardcore filling, 50mm thick, levelled and compacted to receive DPM", "m2", 198.0,
                section="BILL 4 - EARTHWORKS", subsection="4.4 FILLING - INTERNAL",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="Verified from surface bed layout +12"),
        BOQItem("4.5.1", "150mm thick G7 filling compacted to 93% Mod AASHTO density (heavy duty paving areas only)", "m3", 4.0,
                section="BILL 4 - EARTHWORKS", subsection="4.5 FILLING - EXTERNAL PAVING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.5.2", "150mm thick G5 crusher run sub-base compacted to 98% Mod AASHTO density", "m3", 19.0,
                section="BILL 4 - EARTHWORKS", subsection="4.5 FILLING - EXTERNAL PAVING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.5.3", "25mm thick sand bedding to paving, levelled and screeded", "m2", 128.0,
                section="BILL 4 - EARTHWORKS", subsection="4.5 FILLING - EXTERNAL PAVING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.6.1", "Compaction of formation to receive filling under surface beds", "m2", 198.0,
                section="BILL 4 - EARTHWORKS", subsection="4.6 COMPACTION",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.6.2", "Compaction of insitu subgrade to 90% Mod AASHTO for external paving", "m2", 128.0,
                section="BILL 4 - EARTHWORKS", subsection="4.6 COMPACTION",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.7.1", "Keep excavations free of water during construction including pumping, temporary drainage and all associated works", "Item", 1.0,
                section="BILL 4 - EARTHWORKS", subsection="4.7 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("4.7.2", "Provisional Sum for dewatering if extensive pumping required", "P.Sum", 15000.0,
                section="BILL 4 - EARTHWORKS", subsection="4.7 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT
    # ============================================================
    items.extend([
        BOQItem("7.1.1", "Blinding concrete, 15MPa/19mm, 50mm thick under foundations", "m3", 4.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.1 CONCRETE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.1.2", "Reinforced concrete, 25MPa/26mm, in strip foundations 600mm wide x 700mm deep", "m3", 48.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.1 CONCRETE",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="Verified +3 from structural drawings"),
        BOQItem("7.1.3", "Reinforced concrete, 25MPa/19mm, in ring beams RB1 (350x450mm) to SANS 1200 G", "m3", 12.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.1 CONCRETE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.1.4", "Reinforced concrete, 25MPa/19mm, in ring beams RB2 (250x250mm) to SANS 1200 G", "m3", 3.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.1 CONCRETE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.1.5", "Reinforced concrete, 30MPa/19mm, in surface beds 125mm thick, power floated finish", "m3", 25.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.1 CONCRETE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.1.6", "Reinforced concrete, 25MPa/19mm, in columns to SANS 1200 G as per Structural Engineer's details", "m3", 2.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.1 CONCRETE",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="NEW - identified from adaptive sections"),
        BOQItem("7.1.7", "Reinforced concrete, 25MPa/19mm, in canopy slab and beam (Provisional)", "m3", 1.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.1 CONCRETE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.2.1", "Formwork, rough, to sides of strip foundations", "m2", 160.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.2 FORMWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.2.2", "Formwork, smooth (Class F2), to sides and soffits of ring beams", "m2", 122.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.2 FORMWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.2.3", "Formwork, smooth, to edges of surface beds 125mm deep", "m", 115.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.2 FORMWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.2.4", "Formwork, smooth, to columns", "m2", 18.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.2 FORMWORK",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="NEW - for new column concrete"),
        BOQItem("7.2.5", "Formwork, smooth, to canopy slab and beam (Provisional)", "m2", 8.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.2 FORMWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.3.1", "High tensile reinforcement to BS4449, including cutting, bending, fixing with spacers and tying wire", "t", 5.8,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.3 REINFORCEMENT",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+0.5t for columns"),
        BOQItem("7.3.2", "Welded steel fabric reinforcement Ref 193, including laps", "m2", 198.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.3 REINFORCEMENT",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.4.1", "Concrete test cubes including laboratory testing", "No", 65.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.4 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.4.2", "Isolation joints, 10mm wide, to perimeter of surface beds and around columns", "m", 130.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.4 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("7.4.3", "Sawcut joints to surface beds, 3mm wide", "m", 85.0,
                section="BILL 7 - CONCRETE, FORMWORK & REINFORCEMENT", subsection="7.4 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # BILL 10 - MASONRY
    # ============================================================
    items.extend([
        BOQItem("10.1.1", "Corobrik Breeze Block walling, 14MPa, 230mm thick, in cement mortar Class II, to external walls", "m2", 38.0,
                section="BILL 10 - MASONRY", subsection="10.1 BLOCKWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("10.1.2", "Concrete block walling, 7MPa, 230mm thick, in cement mortar Class II, to internal walls", "m2", 82.0,
                section="BILL 10 - MASONRY", subsection="10.1 BLOCKWORK",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="Verified from ground plan +6"),
        BOQItem("10.2.1", "Extra over blockwork for fair face finish (Platinum Satin)", "m2", 38.0,
                section="BILL 10 - MASONRY", subsection="10.2 FAIR FACE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("10.3.1", "Filling to underside of ring beams with blockwork", "m2", 24.0,
                section="BILL 10 - MASONRY", subsection="10.3 BEAM FILLING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("10.4.1", "Malthoid DPC, 230mm wide, under walls", "m", 62.0,
                section="BILL 10 - MASONRY", subsection="10.4 DAMP PROOF COURSE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("10.5.1", "Fabricated steel lintels, various sizes, over openings", "No", 38.0,
                section="BILL 10 - MASONRY", subsection="10.5 LINTELS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("10.6.1", "Brickforce reinforcement, 75mm wide, in every alternate course to loadbearing blockwork", "m", 480.0,
                section="BILL 10 - MASONRY", subsection="10.6 BRICKFORCE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("10.6.2", "Brickforce reinforcement, 75mm wide, in every fourth course to non-loadbearing blockwork", "m", 320.0,
                section="BILL 10 - MASONRY", subsection="10.6 BRICKFORCE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("10.7.1", "Gyproc drywall partitions, 110mm thick, double sided with insulation, complete with all framing, angles and jointing", "m2", 82.0,
                section="BILL 10 - MASONRY", subsection="10.7 DRYWALL PARTITIONS",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # WATERPROOFING
    # ============================================================
    items.extend([
        BOQItem("W.1.1", "250 micron polyethylene DPM to SANS 952-1985 Type C, lapped 150mm at joints, under surface beds", "m2", 198.0,
                section="WATERPROOFING", subsection="W.1 DAMP PROOF MEMBRANE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("W.2.1", "Torch-on waterproofing membrane to ablution floors, turned up at edges 100mm", "m2", 28.0,
                section="WATERPROOFING", subsection="W.2 WET AREA WATERPROOFING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("W.2.2", "Waterproof membrane/coating to ablution walls to 1800mm height", "m2", 68.0,
                section="WATERPROOFING", subsection="W.2 WET AREA WATERPROOFING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("W.3.1", "Waterproof seal to floor/wall junctions in wet areas", "m", 38.0,
                section="WATERPROOFING", subsection="W.3 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("W.3.2", "Waterproof seal around floor wastes and pipe penetrations", "No", 14.0,
                section="WATERPROOFING", subsection="W.3 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # ROOFING - CORRECTED SPECIFICATION
    # ============================================================
    items.extend([
        BOQItem("R.1.1", "BMI Coverland 420 x 330mm Elite concrete roof tiles, Colour Slate Grey, installed as per strict Manufacturer's specifications including all clips, fixings and underlays, on timber battens", "m2", 295.0,
                section="ROOFING", subsection="R.1 ROOF COVERING",
                measurement_rule="ASAQS SSM7 / DQRules",
                calculation_notes="CORRECTED from Klip-Lok steel - BMI tiles verified from adaptive extraction"),
        BOQItem("R.2.1", "BMI Coverland 420 x 200mm Elite ridge tiles, Colour Slate Grey, installed as per Manufacturer's specifications", "m", 32.0,
                section="ROOFING", subsection="R.2 FLASHINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("R.2.2", "Lead flashing 300mm girth to abutments", "m", 45.0,
                section="ROOFING", subsection="R.2 FLASHINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("R.2.3", "Lead flashing stepped to gable ends", "m", 28.0,
                section="ROOFING", subsection="R.2 FLASHINGS",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="NEW - from adaptive"),
        BOQItem("R.2.4", "Valley flashing including valley trough", "m", 12.0,
                section="ROOFING", subsection="R.2 FLASHINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("R.2.5", "Hip tiles, BMI Coverland Elite, Slate Grey", "m", 23.0,
                section="ROOFING", subsection="R.2 FLASHINGS",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="NEW - from adaptive"),
        BOQItem("R.3.1", "Aluminium seamless gutter 125 x 125 x 0.9mm thick, ColourTech G4 coating, including dual-purpose brackets at 600mm centres", "m", 54.0,
                section="ROOFING", subsection="R.3 RAINWATER GOODS",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+10m verified from adaptive"),
        BOQItem("R.3.2", "Extra over for gutter mitred angles", "No", 6.0,
                section="ROOFING", subsection="R.3 RAINWATER GOODS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("R.3.3", "Extra over for gutter stop ends, riveted", "No", 6.0,
                section="ROOFING", subsection="R.3 RAINWATER GOODS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("R.3.4", "Extra over for gutter outlets", "No", 6.0,
                section="ROOFING", subsection="R.3 RAINWATER GOODS",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+2 verified from roof plan"),
        BOQItem("R.3.5", "Aluminium rainwater downpipes 80mm diameter, including brackets, bends and connections", "m", 21.0,
                section="ROOFING", subsection="R.3 RAINWATER GOODS",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+8m verified from sections"),
        BOQItem("R.3.6", "Aluminium rainwater shoes", "No", 6.0,
                section="ROOFING", subsection="R.3 RAINWATER GOODS",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+2 for additional downpipes"),
        BOQItem("R.3.7", "Aluminium valley gutter to BMI specifications", "m", 10.0,
                section="ROOFING", subsection="R.3 RAINWATER GOODS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("R.4.1", "Torch-on waterproofing membrane to flat roof areas (clerestory), 2-layer system including primer", "m2", 35.0,
                section="ROOFING", subsection="R.4 ROOF WATERPROOFING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("R.4.2", "Extra over for upstands and kerbs", "m", 20.0,
                section="ROOFING", subsection="R.4 ROOF WATERPROOFING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("R.5.1", "135mm Think Pink Aerolite glass fibre insulation blanket to roof, laid over ceiling", "m2", 282.0,
                section="ROOFING", subsection="R.5 INSULATION",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+17 from accurate ceiling area"),
        BOQItem("R.6.1", "P.Sum for roof timber structure (trusses, purlins, battens, bracing) as per Structural Engineer's details - INCREASED FOR CONCRETE TILE LOAD", "P.Sum", 180000.0,
                section="ROOFING", subsection="R.6 PROVISIONAL SUM",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="Increased from R150k for heavier tile load"),
    ])

    # ============================================================
    # CARPENTRY & JOINERY
    # ============================================================
    items.extend([
        BOQItem("CJ.1.1", "Timber flush door D01, 900x2100mm, complete with hardwood frame and ironmongery (3 hinges, lever handles, mortice lock, stop)", "No", 9.0,
                section="CARPENTRY & JOINERY", subsection="CJ.1 DOORS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.1.2", "Timber flush door D02, 800x2100mm, complete with hardwood frame and ironmongery", "No", 2.0,
                section="CARPENTRY & JOINERY", subsection="CJ.1 DOORS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.1.3", "Timber flush door D03, 700x2100mm (WC type), with indicator lock and ironmongery", "No", 7.0,
                section="CARPENTRY & JOINERY", subsection="CJ.1 DOORS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.1.4", "Steel security door D04, 900x2100mm, to strong rooms, complete with heavy duty frame, multi-point locking system", "No", 2.0,
                section="CARPENTRY & JOINERY", subsection="CJ.1 DOORS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.1.5", "Timber flush door D05, 820x2100mm, complete with hardwood frame and ironmongery", "No", 1.0,
                section="CARPENTRY & JOINERY", subsection="CJ.1 DOORS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.1.6", "Timber flush door D06, 750x2100mm, complete with hardwood frame and ironmongery", "No", 2.0,
                section="CARPENTRY & JOINERY", subsection="CJ.1 DOORS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.1.7", "Timber door D07, 900x2400mm, full height", "No", 1.0,
                section="CARPENTRY & JOINERY", subsection="CJ.1 DOORS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.1.8", "Timber door D08, 800x2100mm", "No", 1.0,
                section="CARPENTRY & JOINERY", subsection="CJ.1 DOORS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.2.1", "Steel security gate G01, 1200x2100mm, complete with frame, heavy duty hinges, gate lock, drop bolts", "No", 1.0,
                section="CARPENTRY & JOINERY", subsection="CJ.2 GATES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.2.2", "Steel security gate G02, 900x2100mm, complete as before", "No", 1.0,
                section="CARPENTRY & JOINERY", subsection="CJ.2 GATES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.3.1", "Security desk unit JT01, complete as drawing A-(74)6001, Melawood carcass, MDF doors, EeziQuartz countertop, including all fittings, locks and finishes", "No", 1.0,
                section="CARPENTRY & JOINERY", subsection="CJ.3 BUILT-IN JOINERY",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.3.2", "Kitchenette unit JT02, complete as drawing A-(74)6002, Melawood carcass, MDF doors and drawers, EeziQuartz countertop and splashback, including all fittings (excluding sink and mixer)", "No", 1.0,
                section="CARPENTRY & JOINERY", subsection="CJ.3 BUILT-IN JOINERY",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.4.1", "Capco Gamma Base Reveal 75 skirting (Type 01), concealed fixed with bonding agent", "m", 210.0,
                section="CARPENTRY & JOINERY", subsection="CJ.4 SKIRTINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.4.2", "Capco Gamma Flat Skirting 76 (Type 02), concealed fixed with bonding agent", "m", 98.0,
                section="CARPENTRY & JOINERY", subsection="CJ.4 SKIRTINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.4.3", "Extra over for internal corners", "No", 52.0,
                section="CARPENTRY & JOINERY", subsection="CJ.4 SKIRTINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.4.4", "Extra over for external corners", "No", 14.0,
                section="CARPENTRY & JOINERY", subsection="CJ.4 SKIRTINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CJ.4.5", "Extra over for stop ends", "No", 40.0,
                section="CARPENTRY & JOINERY", subsection="CJ.4 SKIRTINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # CEILINGS
    # ============================================================
    items.extend([
        BOQItem("CE.1.1", "600 x 600 x 15mm mineral fiber acoustic ceiling tiles (Ce.01) on 24mm exposed aluminium T-bar suspension grid system, including all hangers, main runners, cross tees, wall angles and accessories, fixed at 2700mm AFFL - general areas", "m2", 252.0,
                section="CEILINGS", subsection="CE.1 SUSPENDED CEILINGS",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+13 verified"),
        BOQItem("CE.1.2", "600 x 600 x 15mm vinyl faced moisture resistant ceiling tiles (Ce.02) on concealed aluminium suspension grid, complete as before - wet areas", "m2", 38.0,
                section="CEILINGS", subsection="CE.1 SUSPENDED CEILINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CE.2.1", "Gypsum plasterboard bulkhead 400mm wide x 300mm drop (Type 01) on light steel framing, jointed and finished ready for painting - perimeter", "m", 72.0,
                section="CEILINGS", subsection="CE.2 BULKHEADS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CE.2.2", "Gypsum plasterboard bulkhead 600mm wide x 400mm drop (Type 02) on light steel framing, complete as before - over ring beams", "m", 48.0,
                section="CEILINGS", subsection="CE.2 BULKHEADS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CE.2.3", "Gypsum plasterboard bulkhead 300mm wide x 200mm drop (Type 03) on light steel framing, complete as before - internal partitions", "m", 38.0,
                section="CEILINGS", subsection="CE.2 BULKHEADS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CE.2.4", "12.5mm gypsum plasterboard to soffits of bulkheads including jointing and finishing", "m2", 70.0,
                section="CEILINGS", subsection="CE.2 BULKHEADS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CE.3.1", "600 x 600mm hinged metal access panel in suspended ceiling including frame and trim", "No", 8.0,
                section="CEILINGS", subsection="CE.3 ACCESS PANELS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CE.3.2", "450 x 450mm plastic hinged access panel in suspended ceiling including frame and trim", "No", 4.0,
                section="CEILINGS", subsection="CE.3 ACCESS PANELS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("CE.4.1", "20mm shadow line detail at wall/ceiling junction formed in suspended ceiling grid system", "m", 285.0,
                section="CEILINGS", subsection="CE.4 SHADOW LINES",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # FLOOR COVERINGS
    # ============================================================
    items.extend([
        BOQItem("FL.1.1", "600 x 600 x 10mm glazed porcelain floor tiles (Fl.01), fixed with tile adhesive, 3mm grouted joints, colour to architect's selection - general areas", "m2", 365.0,
                section="FLOOR COVERINGS", subsection="FL.1 FLOOR TILES",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+15 verified from floor finishes layout"),
        BOQItem("FL.1.2", "300 x 300 x 9mm anti-slip ceramic floor tiles (Fl.02), fixed with tile adhesive, 3mm grouted joints - wet areas", "m2", 32.0,
                section="FLOOR COVERINGS", subsection="FL.1 FLOOR TILES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("FL.2.1", "Prepare surface bed to receive floor tiles including grinding and priming", "m2", 397.0,
                section="FLOOR COVERINGS", subsection="FL.2 FLOOR PREPARATION",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("FL.3.1", "100mm high coved ceramic tile skirting to match floor tiles (Type 01)", "m", 102.0,
                section="FLOOR COVERINGS", subsection="FL.3 TILE SKIRTINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("FL.3.2", "100mm high straight ceramic tile skirting (Type 02)", "m", 132.0,
                section="FLOOR COVERINGS", subsection="FL.3 TILE SKIRTINGS",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # WALL FINISHES & PAINTING
    # ============================================================
    items.extend([
        BOQItem("WF.1.1", "15mm thick cement plaster (1:4) wood float finish to new blockwork walls internally including dubbing out, rounded internal angles and preparing for painting", "m2", 205.0,
                section="WALL FINISHES & PAINTING", subsection="WF.1 PLASTERING",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="+17 verified"),
        BOQItem("WF.1.2", "Hack off defective plaster and make good to existing walls including dubbing out, feathering edges and preparing for painting", "m2", 42.0,
                section="WALL FINISHES & PAINTING", subsection="WF.1 PLASTERING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("WF.1.3", "15mm thick cement plaster to exposed faces of ring beams including rounded arrises and preparing for painting", "m2", 48.0,
                section="WALL FINISHES & PAINTING", subsection="WF.1 PLASTERING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("WF.2.1", "300 x 600 x 9mm glazed ceramic wall tiles to SANS 1285, fixed with TAL Professional tile adhesive, grouted with TAL Fine Epoxy grout in 3mm joints, colour to architect's selection - ablution walls full height to 2100mm AFFL", "m2", 102.0,
                section="WALL FINISHES & PAINTING", subsection="WF.2 WALL TILING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("WF.2.2", "Ditto but 600mm high splashback to kitchenette", "m2", 3.0,
                section="WALL FINISHES & PAINTING", subsection="WF.2 WALL TILING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("WF.2.3", "Aluminium straight edge trim to exposed tile edges including bedding in adhesive", "m", 38.0,
                section="WALL FINISHES & PAINTING", subsection="WF.2 WALL TILING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("WF.3.1", "Prepare, apply 1 coat DULUX Trade Alkali Resistant Primer (full coat) and 2 coats DULUX Trade 100 Low Sheen to new plastered/drywalled walls internally (WF01), colour to architect's selection", "m2", 285.0,
                section="WALL FINISHES & PAINTING", subsection="WF.3 PAINTING - WALLS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("WF.3.2", "Prepare, apply 1 coat DULUX Trade Alkali Resistant Primer (patching) and 2 coats DULUX Trade 100 Low Sheen to existing plastered walls internally (WF02), colour to architect's selection", "m2", 145.0,
                section="WALL FINISHES & PAINTING", subsection="WF.3 PAINTING - WALLS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("WF.4.1", "Prepare, apply 1 coat primer and 2 coats DULUX Trade 100 Low Sheen to gypsum plasterboard bulkhead soffits", "m2", 70.0,
                section="WALL FINISHES & PAINTING", subsection="WF.4 PAINTING - CEILINGS/BULKHEADS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("WF.4.2", "Prepare, apply 1 coat primer and 2 coats DULUX Trade 100 Low Sheen to gypsum plasterboard bulkhead sides", "m2", 56.0,
                section="WALL FINISHES & PAINTING", subsection="WF.4 PAINTING - CEILINGS/BULKHEADS",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # GLAZING
    # ============================================================
    items.extend([
        BOQItem("GL.1.1", "Aluminium window type W01, 600 x 2805mm, side hung, H-SYSTEM flush glazing or equal, 60-80um powder coated finish, complete with friction stays, handles, weatherstripping, 6.38mm clear laminated safety glass", "No", 3.0,
                section="GLAZING", subsection="GL.1 ALUMINIUM WINDOWS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.1.2", "Aluminium window type W02, 350 x 900mm, side hung opening, complete as before", "No", 12.0,
                section="GLAZING", subsection="GL.1 ALUMINIUM WINDOWS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.1.3", "Aluminium window type W03, 900 x 1200mm, top hung opening, complete as before", "No", 5.0,
                section="GLAZING", subsection="GL.1 ALUMINIUM WINDOWS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.1.4", "Aluminium window type W04, 1200 x 1500mm, side hung opening, complete as before", "No", 2.0,
                section="GLAZING", subsection="GL.1 ALUMINIUM WINDOWS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.1.5", "Aluminium window type W05, 1500 x 1200mm, top hung opening, complete as before", "No", 2.0,
                section="GLAZING", subsection="GL.1 ALUMINIUM WINDOWS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.1.6", "Aluminium window type W06, 600 x 600mm, fixed glazing, complete as before", "No", 8.0,
                section="GLAZING", subsection="GL.1 ALUMINIUM WINDOWS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.1", "Aluminium shopfront type SF01, 1275 x 400mm, fixed glazing, complete with 10.38mm laminated safety glass", "No", 2.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.2", "Aluminium shopfront type SF02, 2400 x 2400mm, fixed glazing with transom, complete as before", "No", 1.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.3", "Aluminium shopfront type SF03, 1800 x 2400mm, single door with sidelight, including door closer, floor spring, handles", "No", 2.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.4", "Aluminium shopfront type SF04, 2400 x 2400mm, double doors with sidelights, including closers, floor springs, handles, panic hardware", "No", 1.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.5", "Aluminium shopfront type SF05, 1200 x 2400mm, fixed full height glazing", "No", 5.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.6", "Aluminium shopfront type SF06, 3000 x 1200mm, counter screen with transaction opening", "No", 1.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.7", "Aluminium shopfront type SF07, 1500 x 2100mm, fixed glazing", "No", 2.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.8", "Aluminium shopfront type SF08, 900 x 2400mm, fixed full height glazing", "No", 4.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.2.9", "Aluminium shopfront type SF09, 3600 x 2400mm, entrance screen with single door", "No", 1.0,
                section="GLAZING", subsection="GL.2 ALUMINIUM SHOPFRONTS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.3.1", "Approved polysulphide sealant to perimeter of aluminium frames", "m", 285.0,
                section="GLAZING", subsection="GL.3 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.3.2", "Safety manifestation to glass doors and floor-to-ceiling panels to SANS 10400 requirements", "m2", 38.0,
                section="GLAZING", subsection="GL.3 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("GL.4.1", "PC Sum for specialist glazing works if glass specification varies", "P.Sum", 50000.0,
                section="GLAZING", subsection="GL.4 PC SUM",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # METALWORK
    # ============================================================
    items.extend([
        BOQItem("MW.1.1", "Aluminium security gate type G01, 1200 x 2100mm high, powder coated finish, complete with frame, infill panels, heavy duty hinges (3 No.), gate lock, drop bolts, fixed in prepared opening", "No", 1.0,
                section="METALWORK", subsection="MW.1 GATES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("MW.1.2", "Aluminium security gate type G02, 900 x 2100mm high, complete as before", "No", 1.0,
                section="METALWORK", subsection="MW.1 GATES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("MW.2.1", "100 x 100 x 3mm RHS steel post, 2700mm long, hot dip galvanized and powder coated, including base plate, holding down bolts and grouting - shopfront supports", "No", 4.0,
                section="METALWORK", subsection="MW.2 STRUCTURAL STEEL",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("MW.3.1", "Precast concrete bollard 150mm dia x 900mm high above ground, including 300mm embedment in 300 x 300 x 400mm concrete base grade 25/19, natural finish or painted", "No", 9.0,
                section="METALWORK", subsection="MW.3 BOLLARDS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("MW.4.1", "Galvanized steel frame anchors for aluminium door and window frames", "No", 204.0,
                section="METALWORK", subsection="MW.4 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("MW.4.2", "Heavy duty cast iron manhole cover 600 x 600mm, grade A15, including frame bedded in mortar", "No", 2.0,
                section="METALWORK", subsection="MW.4 SUNDRIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # PLUMBING & DRAINAGE
    # ============================================================
    items.extend([
        BOQItem("PL.1.1", "Close coupled WC suite comprising vitreous china pan, dual flush cistern (6/3L), seat and cover, complete with flush pipe, soil connector, fixing bolts, all white", "No", 2.0,
                section="PLUMBING & DRAINAGE", subsection="PL.1 WC SUITES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.1.2", "Wall hung WC pan vitreous china with concealed cistern, seat and cover, support frame, flush plate, complete with connections, all white", "No", 5.0,
                section="PLUMBING & DRAINAGE", subsection="PL.1 WC SUITES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.1.3", "Doc M WC suite 480mm high pan, close coupled cistern, seat and cover, complete with grab rails, all white", "No", 2.0,
                section="PLUMBING & DRAINAGE", subsection="PL.1 WC SUITES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.2.1", "Wall hung urinal vitreous china with concealed auto-flush system, waste outlet, including spreader and trap, all white", "No", 2.0,
                section="PLUMBING & DRAINAGE", subsection="PL.2 URINALS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.3.1", "Wall hung wash hand basin 500mm vitreous china with pillar mixer tap, bottle trap, waste, brackets, all white/chrome", "No", 2.0,
                section="PLUMBING & DRAINAGE", subsection="PL.3 WASH HAND BASINS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.3.2", "Vanity counter-mounted wash hand basin 450mm vitreous china with deck mixer tap, bottle trap, waste, all white/chrome", "No", 5.0,
                section="PLUMBING & DRAINAGE", subsection="PL.3 WASH HAND BASINS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.3.3", "Doc M accessible wash hand basin with lever taps (150mm handles), bottle trap, waste, support brackets, all white/chrome", "No", 2.0,
                section="PLUMBING & DRAINAGE", subsection="PL.3 WASH HAND BASINS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.4.1", "Single bowl stainless steel sink 450x400mm with mixer tap and swivel spout, strainer waste, bottle trap, complete with clips", "No", 1.0,
                section="PLUMBING & DRAINAGE", subsection="PL.4 SINKS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.5.1", "25mm HDPE Class 10 pipe including fittings, clips, sleeves through walls", "m", 48.0,
                section="PLUMBING & DRAINAGE", subsection="PL.5 COLD WATER PIPEWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.5.2", "22mm copper Class 0 pipe including fittings, clips, sleeves", "m", 38.0,
                section="PLUMBING & DRAINAGE", subsection="PL.5 COLD WATER PIPEWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.5.3", "15mm copper Class 0 pipe including fittings, clips, sleeves", "m", 65.0,
                section="PLUMBING & DRAINAGE", subsection="PL.5 COLD WATER PIPEWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.6.1", "22mm copper Class 0 pipe including fittings, clips, insulation", "m", 28.0,
                section="PLUMBING & DRAINAGE", subsection="PL.6 HOT WATER PIPEWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.6.2", "15mm copper Class 0 pipe including fittings, clips, insulation", "m", 45.0,
                section="PLUMBING & DRAINAGE", subsection="PL.6 HOT WATER PIPEWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.7.1", "110mm uPVC waste pipe including fittings, clips", "m", 28.0,
                section="PLUMBING & DRAINAGE", subsection="PL.7 WASTE & VENT PIPES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.7.2", "50mm uPVC waste pipe including fittings, clips", "m", 38.0,
                section="PLUMBING & DRAINAGE", subsection="PL.7 WASTE & VENT PIPES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.7.3", "40mm uPVC waste pipe including fittings, clips", "m", 18.0,
                section="PLUMBING & DRAINAGE", subsection="PL.7 WASTE & VENT PIPES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.7.4", "110mm uPVC vent pipe through roof including flashing", "m", 10.0,
                section="PLUMBING & DRAINAGE", subsection="PL.7 WASTE & VENT PIPES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.7.5", "50mm uPVC vent pipe including fittings", "m", 14.0,
                section="PLUMBING & DRAINAGE", subsection="PL.7 WASTE & VENT PIPES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.8.1", "25mm gate valve", "No", 1.0,
                section="PLUMBING & DRAINAGE", subsection="PL.8 VALVES & EQUIPMENT",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.8.2", "22mm ball valve", "No", 5.0,
                section="PLUMBING & DRAINAGE", subsection="PL.8 VALVES & EQUIPMENT",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.8.3", "15mm angle service valve", "No", 22.0,
                section="PLUMBING & DRAINAGE", subsection="PL.8 VALVES & EQUIPMENT",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.8.4", "25mm non-return valve", "No", 1.0,
                section="PLUMBING & DRAINAGE", subsection="PL.8 VALVES & EQUIPMENT",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.8.5", "150L electric geyser horizontal with thermostat, drip tray and connections", "No", 1.0,
                section="PLUMBING & DRAINAGE", subsection="PL.8 VALVES & EQUIPMENT",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.8.6", "Expansion vessel 8L", "No", 1.0,
                section="PLUMBING & DRAINAGE", subsection="PL.8 VALVES & EQUIPMENT",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.9.1", "110mm uPVC below ground drain pipe in trench including bedding", "m", 48.0,
                section="PLUMBING & DRAINAGE", subsection="PL.9 BELOW GROUND DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.9.2", "160mm uPVC below ground drain pipe in trench including bedding", "m", 18.0,
                section="PLUMBING & DRAINAGE", subsection="PL.9 BELOW GROUND DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.9.3", "Precast concrete inspection chamber 600x450 including cover", "No", 4.0,
                section="PLUMBING & DRAINAGE", subsection="PL.9 BELOW GROUND DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.9.4", "110mm rodding eye including cover", "No", 5.0,
                section="PLUMBING & DRAINAGE", subsection="PL.9 BELOW GROUND DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.9.5", "110mm gully complete with grating", "No", 3.0,
                section="PLUMBING & DRAINAGE", subsection="PL.9 BELOW GROUND DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.9.6", "50L grease trap complete with cover", "No", 1.0,
                section="PLUMBING & DRAINAGE", subsection="PL.9 BELOW GROUND DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.10.1", "Toilet roll holder stainless steel", "No", 9.0,
                section="PLUMBING & DRAINAGE", subsection="PL.10 ACCESSORIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.10.2", "Toilet brush holder stainless steel", "No", 9.0,
                section="PLUMBING & DRAINAGE", subsection="PL.10 ACCESSORIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.10.3", "Grab rail 600mm stainless steel", "No", 6.0,
                section="PLUMBING & DRAINAGE", subsection="PL.10 ACCESSORIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.10.4", "Mirror 600x450mm with polished edges", "No", 9.0,
                section="PLUMBING & DRAINAGE", subsection="PL.10 ACCESSORIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.10.5", "Soap dispenser stainless steel", "No", 9.0,
                section="PLUMBING & DRAINAGE", subsection="PL.10 ACCESSORIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.10.6", "Paper towel dispenser stainless steel", "No", 7.0,
                section="PLUMBING & DRAINAGE", subsection="PL.10 ACCESSORIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.10.7", "Sanitary bin stainless steel", "No", 6.0,
                section="PLUMBING & DRAINAGE", subsection="PL.10 ACCESSORIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PL.10.8", "Bib tap chrome with hose union", "No", 2.0,
                section="PLUMBING & DRAINAGE", subsection="PL.10 ACCESSORIES",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    # ============================================================
    # EXTERNAL WORKS
    # ============================================================
    items.extend([
        BOQItem("EW.1.1", "Strip topsoil average 150mm deep, stockpile on site for reuse", "m2", 150.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.1 SITE CLEARANCE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.1.2", "Break up and remove existing concrete hardstanding average 100mm thick, cart away and dispose off site", "m2", 85.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.1 SITE CLEARANCE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.1.3", "Clear site of vegetation, grass and weeds", "m2", 150.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.1 SITE CLEARANCE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.2.1", "60mm thick Bosun Smooth Ethnic interlocking concrete pavers, charcoal colour, laid on sand bedding in herringbone pattern, joints filled with sand, vibrated and compacted (light duty)", "m2", 108.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.2 PAVING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.2.2", "80mm thick Bosun Smooth Ethnic interlocking concrete pavers, charcoal colour, complete as before (heavy duty)", "m2", 26.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.2 PAVING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.2.3", "Cutting pavers to curves, angles and at edges", "m", 85.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.2 PAVING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.3.1", "Precast concrete kerb 200 x 100mm on and including 100mm thick concrete haunching grade 15/19, mortar jointed", "m", 70.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.3 EDGING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.3.2", "Paving edge restraint including pegs", "m", 18.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.3 EDGING",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.4.1", "100mm wide ACO channel drain including grating, bedded in concrete", "m", 14.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.4 SURFACE DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.4.2", "100mm gully with grating, connection to drain", "No", 3.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.4 SURFACE DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.4.3", "110mm uPVC stormwater drain in trench including bedding", "m", 10.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.4 SURFACE DRAINAGE",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("EW.5.1", "Concrete ramp 1:12 gradient including non-slip finish, handrails both sides", "m2", 12.0,
                section="BILL 22 - EXTERNAL WORKS", subsection="EW.5 RAMP",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="NEW - from Section 4"),
    ])

    # ============================================================
    # PROVISIONAL SUMS
    # ============================================================
    items.extend([
        BOQItem("PS.1.1", "PC Sum for landscaping works to external areas including planting, irrigation and establishment maintenance, all to landscape architect's specification when issued", "P.Sum", 100000.0,
                section="BILL 23 - PROVISIONAL SUMS & PC ITEMS", subsection="PS.1 PRIME COST SUMS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PS.1.2", "PC Sum for boundary treatment/fencing allowance as may be directed", "P.Sum", 50000.0,
                section="BILL 23 - PROVISIONAL SUMS & PC ITEMS", subsection="PS.1 PRIME COST SUMS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PS.1.3", "PC Sum for specialist glazing works if glass specification varies from measured", "P.Sum", 50000.0,
                section="BILL 23 - PROVISIONAL SUMS & PC ITEMS", subsection="PS.1 PRIME COST SUMS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PS.1.4", "PC Sum for roof timber structure including trusses, purlins, bracing and installation - INCREASED FOR CONCRETE TILE LOAD", "P.Sum", 180000.0,
                section="BILL 23 - PROVISIONAL SUMS & PC ITEMS", subsection="PS.1 PRIME COST SUMS",
                measurement_rule="ASAQS SSM7 / DQRules", calculation_notes="Increased from R150k for heavier BMI tile load"),
        BOQItem("PS.2.4", "Provisional sum for dewatering if extensive pumping required", "P.Sum", 15000.0,
                section="BILL 23 - PROVISIONAL SUMS & PC ITEMS", subsection="PS.2 PROVISIONAL SUMS",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PS.3.1", "Provisional sum for daywork - labour", "P.Sum", 25000.0,
                section="BILL 23 - PROVISIONAL SUMS & PC ITEMS", subsection="PS.3 DAYWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PS.3.2", "Provisional sum for daywork - plant and equipment", "P.Sum", 10000.0,
                section="BILL 23 - PROVISIONAL SUMS & PC ITEMS", subsection="PS.3 DAYWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
        BOQItem("PS.3.3", "Provisional sum for daywork - materials", "P.Sum", 15000.0,
                section="BILL 23 - PROVISIONAL SUMS & PC ITEMS", subsection="PS.3 DAYWORK",
                measurement_rule="ASAQS SSM7 / DQRules"),
    ])

    return items


def main():
    """Export adaptive BOQ to QSPlus formats."""

    # Setup paths
    output_dir = Path(__file__).parent / "QSPlus_Export_Adaptive"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create exporter
    exporter = QSPlusExporter(
        project_name="UFH Alice Campus - Finance Offices Conversion (ADAPTIVE)",
        project_number="UFH-FINANCE-2026-ADAPTIVE"
    )

    # Get all BOQ items
    items = get_adaptive_boq_items()
    exporter.add_items(items)

    print("=" * 60)
    print("UFH Adaptive BOQ - QSPlus Export")
    print("=" * 60)
    print(f"Total items: {len(items)}")

    # Export to CSV
    csv_path = output_dir / "UFH_BOQ_ADAPTIVE_QSPlus.csv"
    exporter.export_to_csv(str(csv_path))
    print(f"CSV exported: {csv_path}")

    # Export to Excel
    xlsx_path = output_dir / "UFH_BOQ_ADAPTIVE_QSPlus.xlsx"
    try:
        exporter.export_to_excel(str(xlsx_path))
        print(f"Excel exported: {xlsx_path}")
    except ImportError as e:
        print(f"Excel export skipped (openpyxl not installed): {e}")

    # Export to JSON
    json_path = output_dir / "UFH_BOQ_ADAPTIVE_QSPlus.json"
    exporter.export_to_json(str(json_path))
    print(f"JSON exported: {json_path}")

    print("\nExport complete!")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
