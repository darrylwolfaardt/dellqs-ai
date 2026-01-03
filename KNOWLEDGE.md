# QS Agents Knowledge Base

> Reference information for implementing remaining agents and tools

---

## 1. Measurement Standards

### SA Standard System of Measurement
- Default for South African projects
- Element-based measurement approach

### UK NRM (New Rules of Measurement)
- **NRM1**: Order of cost estimating and cost planning
- **NRM2**: Detailed measurement for building works

### Element Hierarchy (from measure.agent.yaml)
1. **Substructure** - foundations, basement
2. **Superstructure** - frame, upper floors, roof
3. **External Envelope** - walls, windows, doors
4. **Internal Finishes** - walls, floors, ceilings
5. **Services** - mechanical, electrical, plumbing
6. **External Works** - drainage, landscaping, parking

---

## 2. Drawing Type → Measurement Mapping

From `IntakeAnalyst.MEASUREMENT_POTENTIAL`:

| Drawing Type | Measurable Elements |
|--------------|---------------------|
| FLOOR_PLAN | GIFA, NIA, room areas, wall lengths, doors, windows, partitions |
| SITE_PLAN | Site area, building footprint, hard/soft landscaping, boundaries, parking |
| ELEVATION | External wall areas, window/door areas, cladding, building height |
| SECTION | Floor-to-floor heights, construction depths, foundation depths, stairs |
| ROOF_PLAN | Roof area, perimeter, rainwater goods, rooflights |
| REFLECTED_CEILING | Ceiling areas, grid, light fittings, access panels |
| SCHEDULE | Door/window quantities, finish schedule, room data |
| STRUCTURAL | Foundation types, beam sizes, column positions, slab thickness |
| DETAIL | Construction build-ups, material specifications |

---

## 3. Cost Agent Parameters

### Regional Adjustment Factors (from cost.agent.yaml)
| Region | Factor |
|--------|--------|
| Gauteng (baseline) | 1.00 |
| Western Cape | 1.05 |
| KwaZulu-Natal | 0.98 |
| Eastern Cape | 0.95 |
| UK Projects | GBP→ZAR conversion |

### Contingency Rules
| Project Type | Contingency |
|--------------|-------------|
| New build standard | 5-8% |
| New build complex | 8-12% |
| Refurbishment | 15-20% |
| Heritage | 20-30% |

### Preliminaries (by project size)
| Size | Preliminaries |
|------|---------------|
| Small (<R10m) | 8-12% |
| Medium (R10m-R50m) | 10-15% |
| Large (>R50m) | 12-18% |

---

## 4. Workflow Definitions

From `Orchestrator.WORKFLOWS`:

```python
NEW_BUILD_RESIDENTIAL:
  agents: [intake, measure, cost, output]
  autonomy: level_2_confirm

NEW_BUILD_COMMERCIAL:
  agents: [intake, context_enricher, measure, cost, qa, output]
  autonomy: level_2_confirm

REFURBISHMENT:
  agents: [intake, context_enricher, measure, cost, qa, output]
  autonomy: level_1_suggest  # Higher risk

TENDER_REVIEW:
  agents: [intake, cost, qa, output]
  autonomy: level_2_confirm

VARIATION_ASSESSMENT:
  agents: [intake, measure, cost, output]
  autonomy: level_3_notify  # Fast track
```

---

## 5. Project Type Classification Keywords

From `Orchestrator.PROJECT_TYPE_KEYWORDS`:

- **new_build_residential**: residential, house, dwelling, apartment, flat, home, housing, villa, cottage, bungalow
- **new_build_commercial**: commercial, office, retail, warehouse, industrial, factory, hotel, hospital, school, university, shopping, mall, mixed-use
- **refurbishment**: refurbishment, refurb, renovation, alteration, conversion, fit-out, fitout, remodel, upgrade, modernisation, retrofit
- **tender_review**: tender, bid, pricing, review, check, audit, verification, assessment
- **variation_assessment**: variation, change order, VO, variation order, amendment, modification, revised, addendum

---

## 6. Output File Conventions

### Intake Phase (`01-intake/`)
- `project_manifest.json` - Document inventory
- `completeness_report.md` - Gap analysis
- `measurement_scope.md` - What can be measured

### Measure Phase (`02-measure/`)
- `quantities.json` - Structured quantity data
- `take_off_notes.md` - Methodology and assumptions
- `clarifications.md` - Questions for architects
- `measurement_confidence.json` - Per-element confidence

### Cost Phase (`03-cost/`)
- `priced_boq.xlsx` - Bill of quantities with rates
- `cost_summary.md` - High-level breakdown
- `pricing_assumptions.md` - Rate sources
- `cost_risk_register.md` - Risk analysis

### QA Phase (`04-qa/`)
- Validation reports
- Error/warning logs

### Output Phase (`05-output/`)
- Final deliverables (XLSX, PDF, DOCX)

### Project State (`_project/`)
- `state.json` - Workflow checkpoint
- `flags.json` - Items needing review
- `audit-log.json` - Processing history

---

## 7. Autonomy Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| level_1_suggest | Agent suggests, human decides | Refurbishment (high risk) |
| level_2_confirm | Agent acts, human confirms before output | Standard projects |
| level_3_notify | Agent acts autonomously, notifies human | Variations (fast track) |

---

## 8. Key Data Classes

Located in `qs_agents/tools/common/schemas.py`:

- `DrawingType` - Enum of 17 drawing types
- `DrawingInfo` - Single drawing metadata
- `ProjectMetadata` - Project information
- `LocationInfo` - Geographic location
- `DocumentManifest` - Complete document inventory
- `CompletenessReport` - Gap analysis
- `MeasurementScope` - Measurement capability
- `MeasurableElement` - Single measurable item

---

## 9. Vision Provider Configuration

Default: Claude Code CLI (uses authenticated session)

```python
# In config:
vision_provider: "claude"      # Default - uses CLI
vision_provider: "anthropic"   # Requires ANTHROPIC_API_KEY
vision_provider: "openai"      # Requires OPENAI_API_KEY
```

---

## 10. Standards Keeper Sources (Background Agent)

From `qs_agents/background/standards-keeper.agent.yaml`:

- **Measurement Standards**: RICS, SACQSP, NRM (weekly)
- **Material Prices**: BuildSmart indices, StatsSA PPI, supplier lists (monthly)
- **Labour Rates**: Bargaining council agreements, industry surveys (quarterly)
- **Regulatory Changes**: Government gazette, SANS standards, municipal bylaws (weekly)

---

## 11. NRM Reference Mappings

Partial mapping from `IntakeAnalyst._get_nrm_reference()`:

| Element | NRM Reference |
|---------|---------------|
| Gross Internal Floor Area (GIFA) | NRM1 2.6 |
| Net Internal Area (NIA) | NRM1 2.7 |
| External wall areas | NRM1 2.5.1 |
| Roof area | NRM1 2.5.2 |
| Site area | NRM1 2.1 |
| Window areas and counts | NRM2 L10/L20 |
| Door areas and counts | NRM2 L20 |
| Ceiling areas | NRM2 K10/K40 |
| Floor construction depths | NRM1 2.4.3 |

---

## 12. Measure Agent Implementation

### Overview
- **File**: `qs_agents/agents/measure.py` (~800 lines)
- **Status**: Complete
- **Features**:
  - Vision-based quantity extraction from drawings
  - Support for SA Standard System and UK NRM standards
  - Structured quantity data with element hierarchy
  - Clarification tracking for ambiguous items
  - Full audit trail with take-off notes

### Key Classes

```python
# Result types
MeasureResult         # Complete measurement result
QuantityItem          # Single measured quantity
ElementGroup          # Group of quantities by element category
ClarificationItem     # Item requiring design team clarification
MeasurementConfidence # Confidence scoring per category

# Enums
MeasurementStandard   # sa_standard, nrm1, nrm2
ElementCategory       # substructure, superstructure, etc.
UnitOfMeasure        # m², m³, m, nr, kg, item
```

### Drawing Type → Measurement Mapping

| Drawing Type | Extracts |
|--------------|----------|
| FLOOR_PLAN | GIFA, NIA, room areas, walls, doors, windows |
| SITE_PLAN | Site area, footprint, paving, landscaping, parking |
| ELEVATION | External walls, windows, doors, cladding, height |
| SECTION | Floor-to-floor heights, construction depths, stairs |
| ROOF_PLAN | Roof area, perimeter, ridge/hip lengths, outlets |
| REFLECTED_CEILING | Ceiling areas, light fittings, access panels |
| STRUCTURAL | Foundations, columns, beams, slabs |

### NRM Element Codes

| Code | Category |
|------|----------|
| 1.x | Substructure |
| 2.x | Superstructure |
| 3.x | Internal Finishes |
| 5.x | Services |
| 8.x | External Works |

### CLI Usage

```bash
# Run measure standalone (after intake)
python -m qs_agents.cli measure PROJECT_ID ./intake_output/ -o ./measure_output/

# With NRM2 standard
python -m qs_agents.cli measure PROJECT_ID ./intake_output/ --standard nrm2
```

### Outputs
- `quantities.json` - Structured quantity data by element
- `take_off_notes.md` - Methodology, assumptions, summary
- `clarifications.md` - Questions for architect/engineer
- `measurement_confidence.json` - Per-element confidence scores

---

## 13. Implementation Patterns

### Agent Pattern (from IntakeAnalyst/MeasureAgent)
```python
@dataclass
class AgentResult:
    project_id: str
    # ... result fields
    processing_time_ms: float
    errors: list[dict]
    warnings: list[str]

class Agent:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def analyze(self, input_path, project_id=None) -> AgentResult:
        # Main entry point
        pass
```

### Tool Pattern (from BaseTool)
```python
class MyTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "What this tool does"

    async def execute(self, *args, **kwargs) -> ToolResult[T]:
        # Implementation
        pass
```

---

## 14. Measurement Prompt Engineering

The MeasureAgent uses structured prompts for vision-based quantity extraction:

```python
MEASUREMENT_PROMPT = """
You are an expert Quantity Surveyor analyzing architectural drawings...

**Drawing Information:**
- Drawing Type: {drawing_type}
- Drawing Number: {drawing_number}
- Scale: {scale}

**Elements to Measure:**
{elements_to_measure}

For each measurable element, extract:
1. Description - Clear description
2. Quantity - Numeric value (no rounding)
3. Unit - m², m³, m, nr, kg, item
4. Calculation - Show working
5. Confidence - 0.0 to 1.0
6. Assumptions - List any made
7. Notes - Observations
...
"""
```

Key principles:
- Never round during extraction (precision preserved)
- Flag ambiguity with both interpretations
- Document all assumptions explicitly
- Track source drawing and calculation method

---

## 15. Cost Agent Implementation

### Overview
- **File**: `qs_agents/agents/cost.py` (~900 lines)
- **Status**: Complete
- **Features**:
  - Rate application from internal rate database
  - Regional adjustment factors (9 SA regions + UK)
  - Project stage-aware pricing (feasibility → tender)
  - Contingency calculation by project type
  - Preliminaries calculation by project size
  - Professional fees allowances
  - VAT calculation
  - Cost risk identification
  - XLSX export (requires openpyxl)

### Key Classes

```python
# Result types
CostResult          # Complete pricing result
PricedItem          # Single priced quantity
ElementCostGroup    # Group of priced items by element
CostAllowance       # Allowance/addition to base cost
CostRisk            # Risk item with cost impact
CostSummary         # High-level cost breakdown

# Enums
ProjectStage        # feasibility, concept, developed, technical, tender
Region              # gauteng, western_cape, kwazulu_natal, etc.
RiskLevel           # low, medium, high, very_high
```

### Regional Adjustment Factors

| Region | Factor |
|--------|--------|
| Gauteng (baseline) | 1.00 |
| Western Cape | 1.05 |
| KwaZulu-Natal | 0.98 |
| Eastern Cape | 0.95 |
| Free State | 0.92 |
| Limpopo | 0.90 |
| Mpumalanga | 0.93 |
| North West | 0.91 |
| Northern Cape | 0.88 |
| UK | 1.00 (separate rates) |

### Contingency Ranges by Project Type

| Project Type | Contingency |
|--------------|-------------|
| New build standard | 5-8% |
| New build complex | 8-12% |
| Refurbishment | 15-20% |
| Heritage | 20-30% |
| Tender review | 3-5% |
| Variation | 5-10% |

### Preliminaries by Project Size

| Size | Preliminaries |
|------|---------------|
| Small (<R10m) | 8-12% |
| Medium (R10m-R50m) | 10-15% |
| Large (>R50m) | 12-18% |

### Base Rate Categories

| Code | Category | Default Rate | Unit |
|------|----------|--------------|------|
| 1.1 | Standard foundations | R850 | m² |
| 2.1 | Structural frame | R1,800 | m² |
| 2.2 | Upper floor construction | R1,200 | m² |
| 2.3 | Roof construction | R950 | m² |
| 2.5 | External walls | R1,800 | m² |
| 2.6 | Windows/external doors | R3,500 | m² |
| 2.7 | Internal walls | R650 | m² |
| 2.8 | Internal doors | R4,500 | nr |
| 3.1 | Wall finishes | R280 | m² |
| 3.2 | Floor finishes | R450 | m² |
| 3.3 | Ceiling finishes | R320 | m² |
| 5.8 | Electrical installations | R280 | m² |
| 8.2 | Roads/paths/pavings | R450 | m² |

### CLI Usage

```bash
# Run cost standalone (after measure)
python -m qs_agents.cli cost PROJECT_ID ./measure_output/ -o ./cost_output/

# With regional adjustment
python -m qs_agents.cli cost PROJECT_ID ./measure_output/ --region western_cape

# With project stage
python -m qs_agents.cli cost PROJECT_ID ./measure_output/ --stage tender

# With GIFA for cost/m² calculation
python -m qs_agents.cli cost PROJECT_ID ./measure_output/ --gifa 2500

# Full options
python -m qs_agents.cli cost PROJECT_ID ./measure_output/ \
    --region gauteng \
    --stage concept \
    --type new_build_commercial \
    --gifa 2500 \
    -o ./cost_output/
```

### Outputs
- `priced_boq.json` - Full priced BOQ data
- `priced_boq.xlsx` - Excel workbook with Summary and BOQ sheets
- `cost_summary.md` - High-level cost breakdown
- `pricing_assumptions.md` - Rate sources and adjustment logic
- `cost_risk_register.md` - Identified risks with cost impacts

### Risk Categories Identified

1. **Measurement Uncertainty** - Items with low confidence scores
2. **Design Uncertainty** - Outstanding clarifications
3. **Market Risk** - Material price volatility
4. **Scope Risk** - Potential scope changes
