Thinking about this from the agent's perspective - it needs predictable paths, clear separation between inputs/working/outputs, and support for the checkpoint system.
/projects
  /{project-id}-{project-name}
    │
    ├── /01-intake
    │   ├── /drawings              # Raw PDFs from client
    │   │   ├── /architectural
    │   │   ├── /structural
    │   │   ├── /services
    │   │   └── /schedules
    │   ├── /specifications        # Material specs, standards
    │   ├── /site-info             # Survey data, geotech reports if provided
    │   └── /brief                 # Scope, client requirements, RFQ docs
    │
    ├── /02-analysis
    │   ├── /drawings-extracted    # Structured data from drawing analysis
    │   ├── /geological            # Risk assessment outputs
    │   ├── /regulatory            # Zoning, heritage, compliance checks
    │   ├── /climate               # Material validation against conditions
    │   ├── /supply-chain          # Availability, lead times
    │   └── /services              # Infrastructure assessment
    │
    ├── /03-measurement
    │   ├── /takeoffs              # Element quantities by category
    │   ├── /pricing               # Applied rates, supplier quotes
    │   └── /validation            # Sanity checks, anomaly flags
    │
    ├── /04-deliverables
    │   ├── /boq                   # Bills of quantities (xlsx, pdf, json)
    │   ├── /estimates             # Cost estimates, budgets
    │   ├── /reports               # Risk summaries, advisory reports
    │   └── /archive               # Final versions, version history
    │
    ├── /05-correspondence
    │   ├── /rfi                   # Requests for information
    │   ├── /clarifications        # Q&A with architect/client
    │   └── /variations            # Change orders, amendments
    │
    └── /_project
        ├── manifest.json          # Project metadata, input inventory
        ├── state.json             # Current checkpoint, resume data
        ├── flags.json             # Items requiring review
        └── audit-log.json         # Processing history, decisions made
Key Design Decisions
Numbered prefixes - Forces logical ordering in file browsers, makes the workflow stages explicit.
Intake is read-only after init - Agent never modifies client-provided files. Everything derived goes into analysis or measurement.
Separation of analysis layers - Each value-add service gets its own space. Makes it modular - can run geological without supply chain if needed.
_project folder - Underscore prefix keeps it at top/bottom (depending on sort), clearly meta/system files not deliverables.
Deliverables has archive subfolder - Supports versioning without cluttering the main output space.
Correspondence folder - Often overlooked but critical for audit trail. RFIs and clarifications directly impact quantities.
Variations separate - These are post-initial-BOQ amendments and need their own workflow branch.

[manifest.json](./manifest.json)

Key Design Decisions
Project identification - Supports both internal ID and client reference. Building type enables sensible defaults and sanity checking later.
Location block - Structured for geocoding API calls. The coordinates, confidence score, and source give the geological/regulatory agents what they need to query external data.
Standards section - Explicit about measurement system, currency, and regional adaptations. This drives which rule sets the measurement agent applies.
Value-add services - Each service is a toggleable module with its own status tracking. The intake agent can enable defaults based on location (e.g., auto-enable geological for Gauteng addresses).
Drawings inventory - Detailed per-file metadata including revision, date, scale, and extraction status. The notes field captures agent observations like revision mismatches. The extracted boolean tracks workflow progress.
Gaps and flags - Three severity levels (critical/warning/info) with structured tracking. Each flag has a code for reference in RFIs and reports. This is what surfaces to the user for review decisions.
Workflow block - Checkpoint history with timestamps, next steps queue, and explicit blocking/user-input dependencies. This is what enables the resume capability.
Audit trail - Version history and change log for every modification. Essential for professional accountability.
Want me to draft the state.json schema next - the checkpoint/resume mechanism - or the flags.json that would hold the detailed review items?