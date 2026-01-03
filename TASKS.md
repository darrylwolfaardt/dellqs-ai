# QS Agents Implementation Tasks

> Last Updated: 2025-12-10 (Cost Agent Complete)
> Status: In Progress

## Overview

Multi-agent Quantity Surveying automation framework. The system processes architectural documents and automates QS workflows through specialized agents.

## Completed Tasks

### ✅ Priority 1: Orchestrator Agent
- **File**: `qs_agents/agents/orchestrator.py` (~800 lines)
- **Status**: Complete
- **Features**:
  - Project classification (keyword-based with confidence scoring)
  - Workflow routing for 5 project types
  - Autonomy levels (level_1_suggest, level_2_confirm, level_3_notify)
  - Project state persistence (`_project/state.json`)
  - Intake integration and escalation handling
  - Measure agent integration
  - CLI commands: `start`, `continue`

### ✅ Priority 2: Measure Agent
- **File**: `qs_agents/agents/measure.py` (~800 lines)
- **Status**: Complete
- **Features**:
  - Vision-based quantity extraction from drawings
  - Support for SA Standard System and UK NRM standards
  - Structured quantity data with NRM element hierarchy
  - Clarification tracking for ambiguous items
  - Full audit trail with take-off notes
  - Confidence scoring per measurement category
  - CLI command: `measure`
- **Outputs**:
  - `quantities.json` - Structured quantity data by element
  - `take_off_notes.md` - Methodology, assumptions, summary
  - `clarifications.md` - Questions for architect/engineer
  - `measurement_confidence.json` - Per-element confidence scores

### ✅ Priority 3: Cost Agent
- **File**: `qs_agents/agents/cost.py` (~900 lines)
- **Status**: Complete
- **Features**:
  - Rate application from internal rate database
  - Regional adjustment factors (9 SA regions + UK)
  - Project stage-aware pricing (feasibility → tender)
  - Contingency calculation by project type
  - Preliminaries calculation by project size
  - Professional fees allowances
  - VAT calculation (15% default)
  - Cost risk identification
  - XLSX export (with openpyxl)
  - CLI command: `cost`
- **Outputs**:
  - `priced_boq.json` / `priced_boq.xlsx` - Full priced BOQ
  - `cost_summary.md` - High-level cost breakdown
  - `pricing_assumptions.md` - Rate sources and adjustments
  - `cost_risk_register.md` - Risk analysis with cost impacts

### ✅ Previously Complete (Before This Session)
- **IntakeAnalyst Agent** (`qs_agents/agents/intake_analyst.py`) - 699 lines
- **PDFParser Tool** (`qs_agents/tools/pdf_parser/parser.py`) - 429 lines
- **DrawingClassifier Tool** (`qs_agents/tools/drawing_classifier/classifier.py`) - 516 lines
- **MetadataExtractor Tool** (`qs_agents/tools/metadata_extractor/extractor.py`) - 501 lines
- **Geocoder Tool** (`qs_agents/tools/geocoder/geocoder.py`) - 453 lines
- **Data Schemas** (`qs_agents/tools/common/schemas.py`) - 480 lines
- **BaseTool** (`qs_agents/tools/common/base.py`) - 117 lines
- **CLI** (`qs_agents/cli.py`) - ~800 lines

---

## Pending Tasks

### 🔲 Priority 4: QA Agent (MEDIUM)
- **Spec**: `qs_agents/core/qa.agent.yaml`
- **Purpose**: Validate arithmetic, reasonableness, completeness before delivery
- **Checks**: Sums, extensions, cost/m² ratios, historical comparison

### 🔲 Priority 5: Output Agent (MEDIUM)
- **Spec**: `qs_agents/core/output.agent.yaml`
- **Purpose**: Generate final deliverables (BOQ, estimates, tender docs)
- **Formats**: XLSX, PDF, DOCX

### 🔲 Priority 6: Document Router Tool (LOW)
- **Purpose**: Route documents to correct folders based on classification
- **Referenced in**: intake-analyst.agent.yaml

### 🔲 Priority 7: Spec Parser Tool (MEDIUM)
- **Purpose**: Parse specification documents for material/workmanship requirements

### 🔲 Priority 8: Brief Analyzer Tool (MEDIUM)
- **Purpose**: Extract requirements from project briefs

### 🔲 Priority 9: State Manager Tool (LOW)
- **Purpose**: Workflow checkpoint and state management
- **Note**: Basic state persistence already in Orchestrator

### 🔲 Priority 10: Context Enricher Agent (MEDIUM)
- **Spec**: `qs_agents/core/context-enricher.agent.yaml` (pending status)
- **Purpose**: Cross-agent context sharing, enrichment

### 🔲 Priority 11: Knowledge Base Structure (LOW)
- **Path**: `qs_agents/knowledge/`
- **Structure**: measurement-rules/, rates/, regulations/, benchmarks/

### 🔲 Priority 12: Unit Tests (MEDIUM)
- **Path**: `tests/`
- **Coverage**: All tools and agents

### 🔲 Priority 13: Integration Tests (MEDIUM)
- **Purpose**: Full workflow testing end-to-end

### 🔲 Priority 14: Rate Database (MEDIUM)
- **Purpose**: Seed data for SA/UK rates, materials, labour

---

## Quick Start

```bash
# Install package
python -m pip install -e .

# Start a new project
python -m qs_agents.cli start ./drawings/ --type new_build_commercial

# Continue a project
python -m qs_agents.cli continue PROJECT_ID --decision proceed

# Run intake only
python -m qs_agents.cli intake ./drawings/

# Run measure (after intake)
python -m qs_agents.cli measure PROJECT_ID ./intake_output/ --standard sa_standard

# Run cost (after measure)
python -m qs_agents.cli cost PROJECT_ID ./measure_output/ --region gauteng --stage concept
```

---

## Architecture Notes

- **Async throughout**: All tools/agents use `asyncio`
- **Vision providers**: Claude CLI (default), Anthropic API, OpenAI API
- **Directory renamed**: `qs-agents` → `qs_agents` for Python compatibility
- **Package install**: `pyproject.toml` created, install with `pip install -e .`
