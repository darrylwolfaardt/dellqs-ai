# UFH Roofing Measurement Comparison Report

**Date:** 2026-01-07
**Purpose:** Compare original fixed-DPI extraction vs adaptive high-resolution extraction

---

## Processing Comparison

| Aspect | Original | Adaptive |
|--------|----------|----------|
| DPI | 150 (fixed) | 350 (adaptive) |
| Images per drawing | 1 | 9 (3x3 grid) |
| Tile overlap | N/A | 12% |
| Density detected | N/A | Very High / High |
| Scale detected | Manual | Auto (1:100) |
| Total tokens | ~3,000 | ~130,000 |

---

## Critical Finding: Roof Covering Type Error

### Original Measurement (INCORRECT)
```
Klip-Lok Concealed fix roof sheeting
0.58mm Galvanised steel coil
Colour: Safari-boy
```

### Adaptive Finding (FROM DRAWINGS)
```
BMI Coverland 420 x 330mm Elite roof tile
Concrete tile (not metal)
Colour: Slate Grey
```

**Impact:** This is a fundamental specification error that affects:
- Material costs (tiles vs steel significantly different)
- Substructure requirements (heavier dead load)
- Installation trades (tiler vs sheeter)
- Batten spacing and fixing

**Root Cause:** Original image resolution likely made annotation text unreadable, leading to assumption-based measurement.

---

## Quantitative Comparison

| Item | Original | Adaptive | Delta | % Change |
|------|----------|----------|-------|----------|
| **Roof Covering** | | | | |
| Type | Klip-Lok steel | BMI tiles | **WRONG TYPE** | - |
| Pitch assumed | 15° | 17° | +2° | - |
| Pitch factor | 1.08 | 1.046 | -0.034 | -3.1% |
| Area (on slope) | 285 m² | 295 m² | +10 | +3.5% |
| **Flashings** | | | | |
| Total | 106 m | 140 m | +34 | +32% |
| **Rainwater Goods** | | | | |
| Gutters | 44 m | 54 m | +10 | +23% |
| Gutter outlets | 4 No | 6 No | +2 | +50% |
| RWDP | 13 m | 21 m | +8 | +62% |
| RW shoes | 4 No | 6 No | +2 | +50% |
| Valley gutters | 8 m | 10 m | +2 | +25% |
| **Waterproofing** | | | | |
| Membrane | 38 m² | 35 m² | -3 | -8% |
| Upstands | 24 m | 20 m | -4 | -17% |
| **Insulation** | | | | |
| Area | 265 m² | 282 m² | +17 | +6% |

---

## Readability Improvements

### Annotations Now Readable
The adaptive processing captured these specifications that were unclear/missed originally:

1. **Gutter specification:**
   > "Aluminium seamless gutter, overall size 125 x 125 x 0.5mm thick coated internally and externally with ColourTech G4"

2. **Roof tile specification:**
   > "BMI Coverland 420 x 330mm Elite roof tile - installed as per strict Manufacturer's specifications. Colour - Slate Grey"

3. **Insulation specification:**
   > "135mm Think Pink insulation blanket to be placed on ceiling"

4. **Structure note:**
   > "NEW ROOF STRUCTURE: Roof truss, Purlins, bracing sized and spaced as per Structural Engineer's details"

### Grid Dimensions Captured
All grid spacings now measured:
- 01-02: 2,285mm
- 02-03: 11,180mm
- 03-04: 4,150mm
- 04-05: 3,600mm
- 05-06: 3,600mm
- 06-07: 3,600mm
- 07-08: 1,200mm

### Level Data Captured
- T.O.F: 530,970
- U.F.F.L 01: 531,650
- Wall Plate Height: 535,105

---

## RWDP Location Accuracy

### Original (4 locations assumed)
- Grid 05-F
- Grid 08-E1
- Additional (estimate): 2

### Adaptive (6 locations identified)
- Grid A near 01/02 (visible on plan)
- Grid F1 x 2 locations (annotated)
- Grid A near 08 (annotated)
- Clerestory locations x 2

---

## Conclusion

### Adaptive Processing Benefits Demonstrated

1. **Specification Accuracy** - Critical error in roof covering type identified
2. **Quantity Accuracy** - Rainwater goods increased 23-62% based on visible annotations
3. **Dimension Verification** - Grid spacings captured and verifiable
4. **Assumption Reduction** - Pitch factor corrected from 1.08 to 1.046

### Recommendation

The adaptive PDF processing should be standard for all architectural drawings, particularly:
- Dense drawings (schedules, complex plans)
- Drawings with small annotation text
- Drawings at 1:100 scale or smaller

---

## Files Generated

| File | Purpose |
|------|---------|
| `UFH_Roofing_085_086.md` | Original measurement (baseline) |
| `UFH_Roofing_085_086_REVIEW.md` | Template for Ron's verification |
| `UFH_Roofing_085_086_ADAPTIVE.md` | New extraction with adaptive processing |
| `UFH_Roofing_COMPARISON.md` | This comparison report |

---

## Next Steps

1. **Ron to review** both original and adaptive measurements against drawings
2. **Confirm roof specification** with Architect (tiles vs steel)
3. **If adaptive proves more accurate**, apply to remaining trades:
   - Concrete (structural drawings - likely HIGH density)
   - Glazing (fenestration details - likely HIGH density)
   - External Works (paving layouts)

---

*Report generated: 2026-01-07*
*Adaptive processing: Reference/adaptive_pdf_processor.py*
