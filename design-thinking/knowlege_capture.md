This is where the real work happens. A well-structured knowledge capture process will determine the quality of everything downstream. Let me build you a comprehensive framework.

## Knowledge Capture Framework for QS Domain Expert

### Guiding Principles

Before diving into templates, these principles should govern every capture session:

1. **Capture the why, not just the what** - Understanding reasoning allows the agent to handle novel situations
2. **Record exceptions as carefully as rules** - Edge cases reveal expert judgment
3. **Preserve uncertainty** - When he says "it depends" that's valuable information about decision boundaries
4. **Use real examples** - Abstract rules anchored to actual projects are more accurate
5. **Capture in his language first** - Formalise later; don't lose nuance in translation

---

## Knowledge Taxonomy

Different types of knowledge serve different agents:

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE TYPES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DECLARATIVE (Facts)          PROCEDURAL (How-to)               │
│  ├─ Standards & codes         ├─ Measurement sequences          │
│  ├─ Rate databases            ├─ Calculation methods            │
│  ├─ Material properties       ├─ Drawing reading protocols      │
│  ├─ Regional factors          ├─ Quality check routines         │
│  └─ Terminology               └─ Document workflows             │
│                                                                  │
│  HEURISTIC (Rules of thumb)   CONTEXTUAL (Judgment)             │
│  ├─ Quick estimates           ├─ When to apply contingency      │
│  ├─ Sanity checks             ├─ How to handle ambiguity        │
│  ├─ Warning signs             ├─ Client communication choices   │
│  └─ Shortcuts                 └─ Risk assessment                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation Capture

### Session 1.1: Professional Context & Standards

**Duration:** 2-3 hours
**Purpose:** Establish the baseline standards and his relationship to them
**Consuming agents:** All agents (foundational context)

**Interview Guide:**

```markdown
## Professional Foundation Interview

### Standards & Frameworks

1. Which measurement standard do you primarily use?
   - SA Standard System of Measurement?
   - Which edition/version?
   - How strictly do you adhere vs adapt?

2. For UK projects, what standard applies?
   - NRM1 (cost planning) / NRM2 (detailed measurement)?
   - Key differences you navigate between SA and UK?

3. Are there other standards you reference?
   - JBCC documentation?
   - SANS specifications?
   - Industry body guidelines?

### Regional Practice

4. How does SA practice differ from international practice?
   - Terminology differences?
   - Measurement convention differences?
   - Contractual framework differences?

5. Within SA, do you adjust for regions?
   - Gauteng vs Western Cape vs KZN?
   - Urban vs rural considerations?

6. For UK projects, what adaptations do you make?
   - Beyond the measurement standard itself?
   - Procurement route differences?
   - Documentation expectations?

### Personal Evolution

7. Over 45 years, what has changed most significantly?
   - Methods that are now obsolete?
   - New requirements that didn't exist?
   - Technology impacts?

8. What would you teach a graduate that they won't learn in university?
```

**Capture Template:**

```markdown
# Standards Foundation Document

## Primary Standard
- Name: 
- Version/Edition:
- Key sections referenced most:
- Known limitations or gaps:

## Secondary Standards
| Standard | When Used | Key Differences from Primary |
|----------|-----------|------------------------------|
|          |           |                              |

## Regional Variations
| Region | Adjustments Required | Rationale |
|--------|---------------------|-----------|
|        |                     |           |

## Terminology Map
| SA Term | UK Equivalent | Notes |
|---------|---------------|-------|
|         |               |       |

## Historical Context
- Methods no longer used:
- Why they changed:
- Lessons that still apply:
```

---

### Session 1.2: Project Type Classification

**Duration:** 2 hours
**Purpose:** Understand how project type affects approach
**Consuming agents:** Orchestrator, Measurement, Cost Estimation

**Interview Guide:**

```markdown
## Project Classification Interview

### Project Types Handled

1. What project types do you work on?
   - Residential (houses, apartments, estates)
   - Commercial (offices, retail)
   - Industrial (warehouses, factories)
   - Institutional (schools, hospitals)
   - Infrastructure (roads, services)
   - Refurbishment vs new build

2. For each type, what fundamentally changes in your approach?
   - Measurement emphasis?
   - Typical specification complexity?
   - Cost drivers?
   - Risk factors?

3. Which types are most/least straightforward? Why?

### Classification Signals

4. When you receive new drawings, how do you quickly classify?
   - What do you look for first?
   - What tells you this will be complex vs simple?

5. What information do you need before starting any project?
   - Minimum documentation set?
   - Critical client clarifications?

### Workflow Variations

6. Does your workflow change by project type?
   - Different measurement sequences?
   - Different output formats?
   - Different level of detail?
```

**Capture Template:**

```markdown
# Project Type Classification Matrix

## Type: [e.g., Residential - Single Dwelling]

### Characteristics
- Typical size range:
- Typical complexity:
- Typical duration:
- Common procurement route:

### Measurement Approach
- Primary elements:
- Typical sequence:
- Level of detail required:
- Common shortcuts appropriate:

### Cost Drivers
- Major cost elements (ranked):
- Typical cost range (per m²):
- High variability items:
- Common exclusions:

### Risk Factors
- Typical contingency %:
- Common problem areas:
- Red flags to watch for:

### Documentation Requirements
- Minimum drawings needed:
- Specification requirements:
- Typical deliverables:

### Workflow Variations
- Steps unique to this type:
- Steps that can be abbreviated:
```

---

## Phase 2: Process Capture (By Agent Role)

### Session 2.1: Document Receipt & Classification

**Duration:** 1.5 hours
**Purpose:** Capture intake and document handling logic
**Consuming agents:** Intake Agent, Document Controller

**Interview Guide:**

```markdown
## Document Handling Interview

### Initial Receipt

1. When you receive project documents, what's your first action?
   - How do you organise them?
   - What naming conventions do you use?
   - How do you track what you've received?

2. How do you identify what type of drawing you're looking at?
   - Title block conventions?
   - Drawing number patterns?
   - Visual identification?

3. What's the minimum document set needed to start?
   - Can you proceed with partial information?
   - What triggers a "stop and request more" decision?

### Classification Logic

4. Walk me through classifying a typical document set:
   [Use actual example project]

5. How do you handle revisions?
   - How do you identify a revision?
   - What do you do with superseded documents?
   - How do you track revision impact on measurements?

### Quality Assessment

6. How do you assess drawing quality?
   - What makes a drawing "good" vs "problematic"?
   - Common architect mistakes you catch?
   - When do you send drawings back vs work with what you have?

7. How do you handle inconsistencies between documents?
   - Specifications vs drawings conflicts?
   - Drawing-to-drawing conflicts?
```

**Capture Template:**

```markdown
# Document Classification Rules

## Drawing Type Identification

| Drawing Type | Number Pattern | Visual Indicators | Title Block Clues |
|--------------|----------------|-------------------|-------------------|
| Floor Plan   |                |                   |                   |
| Elevation    |                |                   |                   |
| Section      |                |                   |                   |
| Detail       |                |                   |                   |
| Site Plan    |                |                   |                   |

## Minimum Document Sets

| Project Type | Required Drawings | Required Specs | Can Proceed Without |
|--------------|-------------------|----------------|---------------------|
|              |                   |                |                     |

## Revision Handling Protocol

1. Identification method:
2. Superseded document action:
3. Re-measurement trigger criteria:
4. Revision tracking format:

## Quality Assessment Criteria

### Acceptable Quality
- [ ] Criterion 1
- [ ] Criterion 2

### Problematic Indicators
- Warning sign 1 → Action
- Warning sign 2 → Action

## Conflict Resolution Rules

| Conflict Type | Resolution Rule | Escalation Trigger |
|---------------|-----------------|-------------------|
| Spec vs Drawing |               |                   |
| Drawing vs Drawing |            |                   |
| Dimension mismatch |            |                   |
```

---

### Session 2.2: Drawing Interpretation

**Duration:** 3-4 hours (multiple sessions recommended)
**Purpose:** Capture how he reads and extracts information from drawings
**Consuming agents:** Drawing Interpreter

**Method:** Screen share or in-person with actual drawings. Record the session.

**Interview Guide:**

```markdown
## Drawing Interpretation Interview

### Reading Protocol

1. When you open a floor plan, where do your eyes go first?
   - What are you establishing?
   - What sequence do you follow?

2. How do you verify scale?
   - What known dimensions do you check against?
   - What do you do if scale seems wrong?

3. How do you handle drawings without dimensions?
   - Can you scale off drawings?
   - When is this acceptable vs not?

### Element Identification

4. Let's go through this drawing together. Talk me through:
   - How you identify each wall type
   - How you distinguish structural vs partition
   - How you identify openings
   - How you read finishes

5. What annotations do you rely on most?
   - Room names/numbers?
   - Specification references?
   - Material notations?

6. What do you infer vs what must be explicit?
   - Standard assumptions you make?
   - When do you query the architect?

### Cross-Referencing

7. How do you move between drawings?
   - Plan to elevation to section?
   - What are you validating at each step?

8. How do you reconcile different information sources?
   - Drawing vs specification priority?
   - When drawings disagree?

### Common Patterns

9. What patterns repeat across most projects?
   - Standard construction details you recognise?
   - Common specification clauses?

10. What are the gotchas?
    - Things that look standard but aren't?
    - Common architect errors?
```

**Capture Template:**

```markdown
# Drawing Interpretation Protocol

## Reading Sequence

### Floor Plans
1. First look:
2. Second pass:
3. Detail extraction:
4. Verification checks:

### Elevations
1. First look:
2. Key information extracted:
3. Cross-reference with plans:

### Sections
1. Primary purpose:
2. Key information extracted:
3. What this reveals that plans don't:

## Element Identification Rules

### Walls
| Visual Pattern | Interpretation | Confidence | Verify Via |
|----------------|----------------|------------|------------|
| Thick solid line | External wall |            | Section    |
| Thin solid line | Internal partition |       | Spec       |
| Hatched        | Material-specific |         |            |

### Openings
| Symbol/Pattern | Interpretation | Measurement Rule |
|----------------|----------------|------------------|
|                |                |                  |

### Finishes
| Notation Pattern | Meaning | Source for Spec |
|------------------|---------|-----------------|
|                  |         |                 |

## Scale Verification

Reference dimensions for checking:
- Standard door width:
- Standard ceiling height:
- Standard brick course:
- Other:

## Standard Assumptions

| When You See | You Assume | Unless |
|--------------|------------|--------|
|              |            |        |

## Query Triggers

| Situation | Action | Query Wording |
|-----------|--------|---------------|
| Ambiguous dimension |        |               |
| Missing information |         |               |
| Apparent error |              |               |
```

---

### Session 2.3: Measurement Rules & Adaptations

**Duration:** 4-6 hours (multiple sessions essential)
**Purpose:** Core domain knowledge - measurement methodology
**Consuming agents:** Measurement Agent

**This is the most critical capture session. Take your time.**

**Interview Guide:**

```markdown
## Measurement Rules Interview

### General Principles

1. What are your fundamental measurement principles?
   - Measure twice philosophy?
   - Rounding conventions?
   - Unit preferences?

2. How do you decide what level of detail to measure?
   - Factors that increase detail?
   - When is approximate acceptable?

### Element-by-Element Deep Dive

For each major element, capture:
- Measurement unit
- What to include/exclude
- Deduction rules
- SA adaptations
- UK variations
- Common mistakes

3. Let's go through each building element:

**Substructure**
- Excavation measurement rules
- Foundation measurement
- Floor slab measurement
- DPM/DPC treatment

**Superstructure - Frame**
- Concrete frame measurement
- Steel frame measurement
- Timber frame measurement

**Superstructure - Walls**
- External wall measurement
- Internal wall measurement
- Openings treatment
- Lintels, arches, special features

**Superstructure - Roof**
- Roof structure measurement
- Roof covering measurement
- Rainwater goods

**Finishes**
- Floor finishes
- Wall finishes
- Ceiling finishes
- Painting & decorating

**Services (measured vs provisional)**
- Electrical approach
- Plumbing approach
- HVAC approach
- When to measure vs PC/Provisional

**External Works**
- Paving measurement
- Drainage measurement
- Landscaping treatment

### Your Adaptations

4. For each element, where does your practice differ from the standard?
   - What adaptation?
   - Why did you develop this?
   - When does it apply?

5. What shortcuts do you use that a graduate wouldn't know?
```

**Capture Template (one per element):**

```markdown
# Measurement Rules: [ELEMENT NAME]

## Standard Rule (SA SMM)
- Unit of measurement:
- Description format:
- Include:
- Exclude:

## Deduction Rules
| Feature | Deduct If | Don't Deduct If |
|---------|-----------|-----------------|
|         |           |                 |

## Waste/Cutting Allowance
- Standard allowance:
- Adjust upward when:
- Adjust downward when:

## SA Adaptation
- Adaptation description:
- Rationale:
- When to apply:
- When NOT to apply:

## UK Variation (NRM)
- Different unit?
- Different inclusions?
- Different grouping?

## Calculation Method
```
[Actual formula or step-by-step]
Example:
Wall area = (length × height) - openings > 0.5m²
```

## Common Errors
- Error 1: Description → Correct approach
- Error 2: Description → Correct approach

## Quality Check
- Reasonable range per m²:
- Red flag if outside:

## Example Calculation
[Worked example from real project]
```

---

### Session 2.4: Cost Estimation & Rates

**Duration:** 3-4 hours
**Purpose:** Rate application, adjustments, and estimation judgment
**Consuming agents:** Cost Estimation Agent

**Interview Guide:**

```markdown
## Cost Estimation Interview

### Rate Sources

1. Where do you get your rates from?
   - Published sources?
   - Own database?
   - Recent tender feedback?
   - Supplier quotations?

2. How current do rates need to be?
   - How do you update your database?
   - How do you handle rate escalation?

### Rate Application

3. When applying rates to quantities, what's your process?
   - Direct matches vs interpolation?
   - How do you handle unusual items?
   - When do you get quotations vs estimate?

4. What adjustments do you apply to base rates?
   - Location factors?
   - Project size factors?
   - Access/complexity factors?
   - Market conditions?

### Regional Factors

5. Talk me through SA regional adjustments:
   - Gauteng as baseline?
   - Percentage adjustments for other regions?
   - What drives these differences?

6. For UK projects:
   - How do you source UK rates?
   - Exchange rate handling?
   - Methodology differences that affect cost?

### Preliminaries & Contingency

7. How do you calculate preliminaries?
   - Percentage method vs itemised?
   - Factors that increase/decrease?
   - Typical ranges by project type?

8. How do you set contingency?
   - Base percentage?
   - What increases it?
   - What decreases it?
   - Client communication about contingency?

### Estimation Shortcuts

9. For quick budget estimates, what rules of thumb do you use?
   - Cost per m² by building type?
   - Elemental ratios?
   - Quick sanity checks?

10. When has a "shortcut estimate" led you astray? What did you learn?
```

**Capture Template:**

```markdown
# Cost Estimation Parameters

## Rate Database Structure

### Rate Categories
| Category | Subcategories | Update Frequency | Primary Source |
|----------|---------------|------------------|----------------|
|          |               |                  |                |

### Rate Record Format
```json
{
  "item_code": "",
  "description": "",
  "unit": "",
  "base_rate": 0.00,
  "region": "GAU",
  "effective_date": "2024-01",
  "source": "",
  "notes": ""
}
```

## Regional Adjustment Factors

### South Africa (Base: Gauteng = 1.00)
| Region | Factor | Notes |
|--------|--------|-------|
| Gauteng | 1.00 | Baseline |
| Western Cape | | |
| KZN Coastal | | |
| KZN Inland | | |
| Eastern Cape | | |
| Rural/Remote | | |

### UK Regions
| Region | Factor | Notes |
|--------|--------|-------|
| London | | |
| South East | | |
| Midlands | | |
| North | | |

## Project Adjustment Factors

| Factor | Adjustment Range | Trigger Conditions |
|--------|------------------|-------------------|
| Project size | | |
| Access difficulty | | |
| Programme pressure | | |
| Quality specification | | |
| Market conditions | | |

## Preliminaries Calculation

### Percentage Method
| Project Type | Typical % | Range | Factors Increasing |
|--------------|-----------|-------|-------------------|
|              |           |       |                   |

### Key Preliminaries Items
1. Item: Typical cost/calculation method
2. Item: Typical cost/calculation method

## Contingency Framework

| Risk Level | Base % | Conditions |
|------------|--------|------------|
| Low | | |
| Medium | | |
| High | | |

### Contingency Adjusters
| Factor | Adjustment | Rationale |
|--------|------------|-----------|
| Incomplete drawings | +X% | |
| Difficult ground | +X% | |
| Proven contractor | -X% | |

## Quick Estimate Benchmarks

### Cost per m² (GFA) - Current Rates
| Building Type | Low | Medium | High | Notes |
|---------------|-----|--------|------|-------|
| Residential - basic | | | | |
| Residential - high end | | | | |
| Office - shell | | | | |
| Office - fitted | | | | |
| Retail | | | | |
| Industrial | | | | |

### Elemental Ratios (% of total)
| Element | Typical % | Range |
|---------|-----------|-------|
| Substructure | | |
| Superstructure | | |
| Finishes | | |
| Services | | |
| External | | |
| Prelims | | |
| Contingency | | |
```

---

### Session 2.5: Quality Assurance & Validation

**Duration:** 2 hours
**Purpose:** Capture checking and validation logic
**Consuming agents:** QA Agent

**Interview Guide:**

```markdown
## Quality Assurance Interview

### Self-Checking Process

1. Before issuing any document, what do you check?
   - Calculation verification?
   - Completeness check?
   - Presentation review?

2. What are your "sanity checks"?
   - Benchmark comparisons?
   - Ratio checks?
   - Common sense tests?

3. What mistakes have you caught in your own work? How?

### Review Process

4. When reviewing others' work, what do you look for?
   - Red flags?
   - Common graduate errors?
   - Structural problems vs minor errors?

5. What's your threshold for "good enough" vs "needs rework"?

### Benchmarks

6. What benchmarks do you use to validate estimates?
   - Source of benchmarks?
   - How tight should the match be?
   - What variation triggers investigation?

7. Can you give me your current benchmarks?
   - By building type
   - By element
   - By trade

### Error Patterns

8. What are the most common errors you see?
   - In measurement?
   - In rate application?
   - In documentation?

9. What errors are critical vs tolerable?
```

**Capture Template:**

```markdown
# Quality Assurance Protocol

## Pre-Issue Checklist

### Calculation Verification
- [ ] Check item 1
- [ ] Check item 2
- [ ] Check item 3

### Completeness Check
- [ ] All elements included?
- [ ] All items priced?
- [ ] Preliminaries included?
- [ ] Contingency applied?

### Presentation Review
- [ ] Formatting correct?
- [ ] Descriptions clear?
- [ ] Totals correct?
- [ ] Client-ready?

## Benchmark Validation

### Cost per m² Tolerances
| Building Type | Expected | Acceptable Range | Investigate If |
|---------------|----------|------------------|----------------|
|               |          | ±X%              | Outside ±Y%    |

### Elemental Ratio Tolerances
| Element | Expected % | Acceptable Range | Investigate If |
|---------|------------|------------------|----------------|
|         |            |                  |                |

### Trade Ratio Checks
| Trade | Typical % of Element | Flag If |
|-------|---------------------|---------|
|       |                     |         |

## Error Classification

### Critical Errors (Must Fix)
1. Error type → Why critical
2. Error type → Why critical

### Significant Errors (Should Fix)
1. Error type → Impact
2. Error type → Impact

### Minor Errors (Fix If Time)
1. Error type → Acceptable threshold
2. Error type → Acceptable threshold

## Common Error Patterns

| Error | How to Detect | How to Prevent |
|-------|---------------|----------------|
|       |               |                |
```

---

## Phase 3: Output Capture

### Session 3.1: Deliverable Templates & Formats

**Duration:** 2-3 hours
**Purpose:** Capture exact output requirements
**Consuming agents:** BoQ Production, Reporting

**Interview Guide:**

```markdown
## Deliverables Interview

### Bills of Quantities

1. Show me your BoQ templates:
   - What format (Excel structure)?
   - What columns are essential?
   - How do you organise sections?

2. Do you have different formats for:
   - Preliminary estimates?
   - Tender documents?
   - Contract BoQs?

3. What preambles and preliminaries text do you use?
   - Standard clauses?
   - Project-specific modifications?

### Reports

4. What reports do you produce regularly?
   - Format and structure?
   - Key sections?
   - Client preferences?

5. Show me examples of:
   - Cost report
   - Variation assessment
   - Progress valuation
   - Final account summary

### Communication

6. How do you typically communicate findings?
   - Query format?
   - Recommendation format?
   - Risk communication?
```

**Capture:** Collect actual template files, not just descriptions. These become the basis for output generation.

---

## Phase 4: Scenario-Based Capture

### Session 4.1: Edge Cases & Judgment Calls

**Duration:** 2-3 hours
**Purpose:** Capture decision-making in non-standard situations
**Consuming agents:** All agents (exception handling)

**Interview Guide:**

```markdown
## Scenarios Interview

Present each scenario, capture response and reasoning:

### Incomplete Information Scenarios

1. "You receive drawings but no specification. What do you do?"

2. "The drawings show a feature but dimensions are missing. 
    How do you proceed?"

3. "You're asked for an estimate but only have sketch drawings. 
    What's your approach?"

### Conflict Scenarios

4. "The structural drawings show different dimensions than 
    the architectural. How do you resolve?"

5. "The specification calls for a material that doesn't match 
    the drawings. What do you do?"

6. "Client's budget expectation is significantly below your 
    estimate. How do you handle this?"

### Time Pressure Scenarios

7. "You need to produce an estimate in 2 hours. What do you 
    prioritise? What do you skip?"

8. "A tender closes tomorrow and you've just received revised 
    drawings. What's your process?"

### Unusual Project Scenarios

9. "You're asked to measure a type of building you've never 
    done before. How do you approach it?"

10. "The project is in a country you haven't worked in. 
     What do you need to find out?"

### Error Discovery Scenarios

11. "After issuing a BoQ, you discover a significant error. 
     What do you do?"

12. "During construction, measured quantities prove to be 
     significantly different from BoQ. How do you handle?"
```

**Capture Template:**

```markdown
# Decision Scenario: [SCENARIO NAME]

## Situation
[Description]

## Decision Factors
- Factor 1: Weight/importance
- Factor 2: Weight/importance

## Decision Tree
```
IF [condition] THEN [action]
ELSE IF [condition] THEN [action]
ELSE [default action]
```

## Rationale
[Why this approach]

## Risks of Wrong Decision
[What could go wrong]

## Real Example
[Actual instance where this occurred]
```

---

## Knowledge Validation Framework

After capture, validate with him:

### Validation Session Structure

```markdown
## Knowledge Validation Checklist

### Accuracy Review
Present captured rules back to him:
- "I've documented that for brickwork you [X]. Is that correct?"
- "Your adaptation for [Y] says [Z]. Is that accurate?"

### Completeness Check
- "What have I missed?"
- "What other situations should I know about?"
- "Are there exceptions to these rules?"

### Edge Case Testing
Present hypothetical scenarios:
- "If [unusual situation], what would you do?"
- "Does this rule apply when [edge condition]?"

### Priority Confirmation
- "Which of these rules are most critical?"
- "Which can flex? Which are absolute?"
```

---

## Capture Session Schedule

Suggested sequence over 2-3 weeks:

| Week | Session | Duration | Focus |
|------|---------|----------|-------|
| 1 | 1.1 | 2-3 hrs | Standards foundation |
| 1 | 1.2 | 2 hrs | Project classification |
| 1 | 2.1 | 1.5 hrs | Document handling |
| 2 | 2.2 | 3-4 hrs | Drawing interpretation |
| 2 | 2.3a | 2 hrs | Measurement rules (Part 1) |
| 2 | 2.3b | 2 hrs | Measurement rules (Part 2) |
| 2 | 2.3c | 2 hrs | Measurement rules (Part 3) |
| 3 | 2.4 | 3-4 hrs | Cost estimation |
| 3 | 2.5 | 2 hrs | Quality assurance |
| 3 | 3.1 | 2-3 hrs | Templates & outputs |
| 3 | 4.1 | 2-3 hrs | Edge cases |
| 3 | Val | 2 hrs | Validation review |

---

## Output: Knowledge Base Structure

After capture, organise into this structure for agent consumption:

```
/knowledge-base/
  /standards/
    sa-smm-reference.md
    uk-nrm-reference.md
    terminology-mapping.md
  
  /measurement-rules/
    /substructure/
      excavation.md
      foundations.md
      ground-floor.md
    /superstructure/
      walls-external.md
      walls-internal.md
      structural-frame.md
      roof-structure.md
      roof-covering.md
    /finishes/
      floor-finishes.md
      wall-finishes.md
      ceiling-finishes.md
      painting.md
    /services/
      electrical-approach.md
      plumbing-approach.md
      hvac-approach.md
    /external/
      paving.md
      drainage.md
      landscaping.md
  
  /adaptations/
    sa-specific/
      [adaptation files]
    uk-specific/
      [adaptation files]
    expert-shortcuts/
      [efficiency rules]
  
  /cost-data/
    rate-database.json
    regional-factors.json
    preliminaries-rules.md
    contingency-framework.md
    benchmarks.json
  
  /quality/
    qa-checklist.md
    benchmarks-validation.md
    error-patterns.md
  
  /templates/
    boq-preliminary.xlsx
    boq-tender.xlsx
    cost-report.docx
    [etc.]
  
  /scenarios/
    incomplete-information.md
    conflicts.md
    time-pressure.md
    unusual-projects.md
  
  /project-types/
    residential-single.md
    residential-multi.md
    commercial-office.md
    [etc.]
```

---

Shall I now create detailed persona definitions for each agent that will consume this knowledge, or would you prefer to start with the interview sessions and refine the framework based on what emerges?