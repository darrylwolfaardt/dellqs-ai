-- =============================================================================
-- QS AGENT DATABASE SCHEMA
-- Based on ASAQS 7th Edition (2015) Standard System of Measuring Building Work
-- For South African Quantity Surveying Projects
-- =============================================================================

-- =============================================================================
-- SECTION 1: MEASUREMENT STANDARDS AND REFERENCE DATA
-- =============================================================================

-- Measurement Standards (ASAQS, NRM1, SMM7, etc.)
CREATE TABLE measurement_standards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    version VARCHAR(50),
    effective_date DATE,
    region VARCHAR(100),  -- 'South Africa', 'UK', 'Africa', etc.
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO measurement_standards (code, name, version, region, description) VALUES
('ASAQS7', 'Standard System of Measuring Building Work', '7th Edition 2015', 'South Africa', 'Primary SA standard for building measurement'),
('AAQS2015', 'Standard Method of Measuring Building Work for Africa', '1st Edition 2015', 'Africa', 'Pan-African standard based on ASAQS'),
('NRM1', 'New Rules of Measurement - Order of Cost Estimating', 'NRM1 2nd Ed', 'UK', 'RICS cost estimating standard'),
('NRM2', 'New Rules of Measurement - Detailed Measurement', 'NRM2 2nd Ed', 'UK', 'RICS detailed measurement for BQ'),
('SMM7', 'Standard Method of Measurement', '7th Edition', 'UK', 'Traditional UK measurement standard');

-- =============================================================================
-- SECTION 2: TRADE SECTIONS (TOP LEVEL - 21 ASAQS TRADE CATEGORIES)
-- =============================================================================

CREATE TABLE trade_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    standard_id UUID REFERENCES measurement_standards(id),
    code CHAR(1) NOT NULL,  -- A, B, C, D, etc.
    name VARCHAR(200) NOT NULL,
    description TEXT,
    measurement_order INT,  -- Order within BOQ (mass, volume, area, length, number)
    sort_order INT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(standard_id, code)
);

-- ASAQS 7th Edition Trade Sections from Model Preambles
INSERT INTO trade_sections (standard_id, code, name, sort_order, description)
SELECT id, code, name, sort_order, description FROM measurement_standards 
CROSS JOIN (VALUES
    ('A', 'General', 1, 'General preambles, abbreviations, materials and workmanship standards'),
    ('B', 'Alterations', 2, 'Taking down, removing, and alteration work to existing structures'),
    ('C', 'Earthworks', 3, 'Demolitions, excavations, filling, soil insecticides'),
    ('D', 'Concrete, Formwork and Reinforcement', 4, 'In-situ concrete work per SANS 1200G'),
    ('E', 'Precast Concrete', 5, 'Precast concrete elements, terrazzo finishes'),
    ('F', 'Masonry', 6, 'Brickwork, blockwork, mortar, face brickwork'),
    ('G', 'Waterproofing', 7, 'DPC, tanking, roof waterproofing'),
    ('H', 'Roof Coverings etc', 8, 'Tiles, sheeting, flashings, insulation'),
    ('I', 'Carpentry and Joinery', 9, 'Structural timber, doors, frames, joinery'),
    ('J', 'Ceilings, Partitions and Access Flooring', 10, 'Suspended ceilings, dry partitions'),
    ('K', 'Floor Coverings, Wall Linings, etc', 11, 'Vinyl, carpet, timber flooring'),
    ('L', 'Ironmongery', 12, 'Locks, hinges, door furniture'),
    ('M', 'Structural Steelwork', 13, 'Per SANS 1200H/HA'),
    ('N', 'Metalwork', 14, 'Steel, aluminium windows, doors, balustrades'),
    ('O', 'Plastering', 15, 'Screeds, renders, granolithic, terrazzo'),
    ('P', 'Tiling', 16, 'Wall and floor tiling'),
    ('Q', 'Plumbing and Drainage', 17, 'Pipes, sanitary fittings, drainage'),
    ('R', 'Glazing', 18, 'Glass, mirrors, putty'),
    ('S', 'Paintwork', 19, 'Primers, undercoats, finishing coats'),
    ('T', 'Paperhanging', 20, 'Wallpaper application'),
    ('U', 'External Works', 21, 'Landscaping, roadwork, fencing')
) AS t(code, name, sort_order, description)
WHERE measurement_standards.code = 'ASAQS7';

-- =============================================================================
-- SECTION 3: NRM1 GROUP ELEMENTS (FOR UK PROJECTS AND ELEMENTAL ANALYSIS)
-- =============================================================================

CREATE TABLE nrm_group_elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(10) NOT NULL,  -- 0, 1, 2, 3, etc.
    name VARCHAR(200) NOT NULL,
    description TEXT,
    sort_order INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO nrm_group_elements (code, name, sort_order) VALUES
('0', 'Facilitating Works', 0),
('1', 'Substructure', 1),
('2', 'Superstructure', 2),
('3', 'Internal Finishes', 3),
('4', 'Fittings, Furnishings and Equipment', 4),
('5', 'Services', 5),
('6', 'Prefabricated Buildings and Building Units', 6),
('7', 'Work to Existing Buildings', 7),
('8', 'External Works', 8);

-- NRM1 Elements (Sub-level)
CREATE TABLE nrm_elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_element_id UUID REFERENCES nrm_group_elements(id),
    code VARCHAR(10) NOT NULL,  -- 1.1, 2.1, 2.2, etc.
    name VARCHAR(200) NOT NULL,
    description TEXT,
    sort_order INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample NRM1 Elements
INSERT INTO nrm_elements (group_element_id, code, name, sort_order)
SELECT ge.id, e.code, e.name, e.sort_order
FROM nrm_group_elements ge
JOIN (VALUES
    -- Substructure elements
    ('1', '1.1', 'Substructure', 1),
    -- Superstructure elements  
    ('2', '2.1', 'Frame', 1),
    ('2', '2.2', 'Upper Floors', 2),
    ('2', '2.3', 'Roof', 3),
    ('2', '2.4', 'Stairs and Ramps', 4),
    ('2', '2.5', 'External Walls', 5),
    ('2', '2.6', 'Windows and External Doors', 6),
    ('2', '2.7', 'Internal Walls and Partitions', 7),
    ('2', '2.8', 'Internal Doors', 8),
    -- Internal Finishes
    ('3', '3.1', 'Wall Finishes', 1),
    ('3', '3.2', 'Floor Finishes', 2),
    ('3', '3.3', 'Ceiling Finishes', 3),
    -- Services
    ('5', '5.1', 'Sanitary Installations', 1),
    ('5', '5.2', 'Services Equipment', 2),
    ('5', '5.3', 'Disposal Installations', 3),
    ('5', '5.4', 'Water Installations', 4),
    ('5', '5.5', 'Heat Source', 5),
    ('5', '5.6', 'Space Heating and Air Conditioning', 6),
    ('5', '5.7', 'Ventilation', 7),
    ('5', '5.8', 'Electrical Installations', 8),
    ('5', '5.9', 'Fuel Installations', 9),
    ('5', '5.10', 'Lift and Conveyor Installations', 10),
    ('5', '5.11', 'Fire and Lightning Protection', 11),
    ('5', '5.12', 'Communication, Security and Control Systems', 12),
    ('5', '5.13', 'Specialist Installations', 13),
    ('5', '5.14', 'Builders Work in Connection with Services', 14),
    -- External Works
    ('8', '8.1', 'Site Preparation Works', 1),
    ('8', '8.2', 'Roads, Paths and Pavings', 2),
    ('8', '8.3', 'Soft Landscaping, Planting and Irrigation', 3),
    ('8', '8.4', 'Fencing, Railings and Walls', 4),
    ('8', '8.5', 'External Fixtures', 5),
    ('8', '8.6', 'External Drainage', 6),
    ('8', '8.7', 'External Services', 7),
    ('8', '8.8', 'Minor Building Works and Ancillary Buildings', 8)
) AS e(group_code, code, name, sort_order)
ON ge.code = e.group_code;

-- =============================================================================
-- SECTION 4: TRADE SUB-SECTIONS (ASAQS CLAUSE LEVEL)
-- =============================================================================

CREATE TABLE trade_sub_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_section_id UUID REFERENCES trade_sections(id),
    code VARCHAR(20) NOT NULL,  -- C.1, C.2, C.3, etc.
    name VARCHAR(200) NOT NULL,
    description TEXT,
    measurement_rules TEXT,  -- How to measure this category
    coverage_rules TEXT,     -- What's deemed included
    sort_order INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample sub-sections for key trades
-- Earthworks (Trade C)
INSERT INTO trade_sub_sections (trade_section_id, code, name, sort_order, measurement_rules)
SELECT ts.id, ss.code, ss.name, ss.sort_order, ss.rules
FROM trade_sections ts
CROSS JOIN (VALUES
    ('C.1', 'Demolitions', 1, 'Nature and extent given as rough guide. Demolish to 150mm below ground.'),
    ('C.2', 'Soil Insecticides', 2, 'Per SANS 10124'),
    ('C.3', 'Filling etc', 3, 'Layers not exceeding 300mm, compacted to 90% Mod AASHTO'),
    ('C.4', 'Excavations', 4, 'Classified as hard rock, soft rock, or earth. Net voids measured.')
) AS ss(code, name, sort_order, rules)
WHERE ts.code = 'C';

-- Concrete (Trade D)
INSERT INTO trade_sub_sections (trade_section_id, code, name, sort_order, description)
SELECT ts.id, ss.code, ss.name, ss.sort_order, ss.desc
FROM trade_sections ts
CROSS JOIN (VALUES
    ('D.1', 'Specification for Concrete Work', 1, 'Per SANS 1200G with Project Specification'),
    ('D.2', 'Aggregates of Low Density', 2, 'Per SANS 794'),
    ('D.3', 'Hollow Blocks and Beams', 3, 'Block beams, planks - no broken components'),
    ('D.4', 'Supervision', 4, 'Foreman requirements for concrete work'),
    ('D.5', 'General Concrete Items', 5, 'Construction joints, surface beds, formwork')
) AS ss(code, name, sort_order, desc)
WHERE ts.code = 'D';

-- Masonry (Trade F)
INSERT INTO trade_sub_sections (trade_section_id, code, name, sort_order, description)
SELECT ts.id, ss.code, ss.name, ss.sort_order, ss.desc
FROM trade_sections ts
CROSS JOIN (VALUES
    ('F.1', 'Materials and Workmanship Standards', 1, 'SANS references for masonry materials'),
    ('F.2', 'Sand', 2, 'Washed and screened through 2.4mm mesh'),
    ('F.3', 'Burnt Clay Bricks', 3, '222x106x73mm nominal, common or facing'),
    ('F.4', 'Concrete Bricks', 4, '8 MPa minimum compressive strength'),
    ('F.5', 'Quarry Tiles etc', 5, 'Even shape, size, colour, free from defects'),
    ('F.6', 'Wire Ties', 6, 'Galvanized steel, single or butterfly type'),
    ('F.7', 'Brickwork Reinforcement', 7, '2.8mm main wires, 2.5mm cross wires at 300mm'),
    ('F.8', 'Mortar', 8, 'Class I, II, or III per strength requirements'),
    ('F.9', 'Compo Mortar', 9, 'Class III with lime content of 80 litres'),
    ('F.10', 'Brickwork', 10, 'Stretcher or English bond, Class II mortar'),
    ('F.11', 'Blockwork', 11, 'Stretcher bond, shell bedding for hollow blocks'),
    ('F.12', 'Centres and Turning Pieces', 12, 'Left 14 days minimum'),
    ('F.13', 'Face Brickwork', 13, 'True and fair face, perpends aligned'),
    ('F.14', 'Pavings, Sills, Copings', 14, 'Class I mortar, slightly keyed joints')
) AS ss(code, name, sort_order, desc)
WHERE ts.code = 'F';

-- =============================================================================
-- SECTION 5: BOQ ITEM TEMPLATES (REUSABLE MEASUREMENT ITEMS)
-- =============================================================================

CREATE TABLE units_of_measurement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    category VARCHAR(50)  -- mass, volume, area, length, number
);

INSERT INTO units_of_measurement (code, name, category) VALUES
('m³', 'Cubic Metres', 'volume'),
('m²', 'Square Metres', 'area'),
('m', 'Linear Metres', 'length'),
('kg', 'Kilograms', 'mass'),
('t', 'Tonnes', 'mass'),
('No', 'Number', 'number'),
('Item', 'Item', 'number'),
('Prov Sum', 'Provisional Sum', 'number'),
('PC Sum', 'Prime Cost Sum', 'number');

CREATE TABLE boq_item_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_sub_section_id UUID REFERENCES trade_sub_sections(id),
    nrm_element_id UUID REFERENCES nrm_elements(id),
    item_code VARCHAR(50),
    short_description VARCHAR(200) NOT NULL,
    full_description TEXT,
    unit_id UUID REFERENCES units_of_measurement(id),
    
    -- Measurement classification (ASAQS ordering: mass, volume, area, length, number)
    measurement_category VARCHAR(20),  -- mass, volume, area, length, number
    
    -- Typical specification references
    sans_reference VARCHAR(100),  -- e.g., 'SANS 1200G', 'SANS 227'
    
    -- Classification flags
    is_provisional BOOLEAN DEFAULT false,
    is_prime_cost BOOLEAN DEFAULT false,
    requires_drawing_reference BOOLEAN DEFAULT false,
    
    -- Default pricing hints (optional)
    typical_rate_range_low DECIMAL(12,2),
    typical_rate_range_high DECIMAL(12,2),
    rate_currency CHAR(3) DEFAULT 'ZAR',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample BOQ items for Earthworks
INSERT INTO boq_item_templates (trade_sub_section_id, item_code, short_description, full_description, unit_id, measurement_category)
SELECT 
    tss.id,
    t.item_code,
    t.short_desc,
    t.full_desc,
    u.id,
    t.category
FROM trade_sub_sections tss
CROSS JOIN (VALUES
    ('C.4', 'C.4.1', 'Excavation in earth', 'Bulk excavation in earth not exceeding 2m deep', 'm³', 'volume'),
    ('C.4', 'C.4.2', 'Excavation in soft rock', 'Bulk excavation in soft rock not exceeding 2m deep', 'm³', 'volume'),
    ('C.4', 'C.4.3', 'Excavation in hard rock', 'Bulk excavation in hard rock not exceeding 2m deep', 'm³', 'volume'),
    ('C.4', 'C.4.4', 'Trench excavation', 'Trench excavation in earth not exceeding 1.5m deep', 'm³', 'volume'),
    ('C.3', 'C.3.1', 'Filling imported', 'Filling with imported material compacted to 90% Mod AASHTO', 'm³', 'volume'),
    ('C.3', 'C.3.2', 'Filling selected', 'Filling with selected excavated material', 'm³', 'volume'),
    ('C.3', 'C.3.3', 'Hardcore filling', 'Hardcore filling 25-75mm graded stone', 'm³', 'volume')
) AS t(sub_code, item_code, short_desc, full_desc, unit_code, category)
JOIN units_of_measurement u ON u.code = t.unit_code
WHERE tss.code = t.sub_code;

-- Sample BOQ items for Concrete
INSERT INTO boq_item_templates (trade_sub_section_id, item_code, short_description, full_description, unit_id, measurement_category, sans_reference)
SELECT 
    tss.id,
    t.item_code,
    t.short_desc,
    t.full_desc,
    u.id,
    t.category,
    t.sans_ref
FROM trade_sub_sections tss
CROSS JOIN (VALUES
    ('D.5', 'D.5.1', 'Blinding concrete', '25MPa/19mm concrete blinding not exceeding 75mm thick', 'm³', 'volume', 'SANS 1200G'),
    ('D.5', 'D.5.2', 'Strip foundations', '25MPa/19mm concrete in strip foundations', 'm³', 'volume', 'SANS 1200G'),
    ('D.5', 'D.5.3', 'Pad foundations', '30MPa/19mm concrete in pad foundations', 'm³', 'volume', 'SANS 1200G'),
    ('D.5', 'D.5.4', 'Surface beds', '25MPa/19mm concrete surface beds 100mm thick', 'm²', 'area', 'SANS 1200G'),
    ('D.5', 'D.5.5', 'Suspended slabs', '30MPa/19mm concrete in suspended slabs', 'm³', 'volume', 'SANS 1200G'),
    ('D.5', 'D.5.6', 'Columns', '30MPa/19mm concrete in columns', 'm³', 'volume', 'SANS 1200G'),
    ('D.5', 'D.5.7', 'Beams', '30MPa/19mm concrete in beams', 'm³', 'volume', 'SANS 1200G'),
    ('D.5', 'D.5.8', 'Formwork rough', 'Formwork to sides of foundations', 'm²', 'area', NULL),
    ('D.5', 'D.5.9', 'Formwork smooth', 'Formwork to soffits of slabs', 'm²', 'area', NULL),
    ('D.5', 'D.5.10', 'Reinforcement Y10', 'High tensile reinforcement Y10', 't', 'mass', NULL),
    ('D.5', 'D.5.11', 'Reinforcement Y12', 'High tensile reinforcement Y12', 't', 'mass', NULL),
    ('D.5', 'D.5.12', 'Reinforcement Y16', 'High tensile reinforcement Y16', 't', 'mass', NULL),
    ('D.5', 'D.5.13', 'Mesh Ref 193', 'Welded steel fabric reinforcement Ref 193', 'm²', 'area', 'SANS 1024')
) AS t(sub_code, item_code, short_desc, full_desc, unit_code, category, sans_ref)
JOIN units_of_measurement u ON u.code = t.unit_code
WHERE tss.code = t.sub_code;

-- Sample BOQ items for Masonry
INSERT INTO boq_item_templates (trade_sub_section_id, item_code, short_description, full_description, unit_id, measurement_category, sans_reference)
SELECT 
    tss.id,
    t.item_code,
    t.short_desc,
    t.full_desc,
    u.id,
    t.category,
    t.sans_ref
FROM trade_sub_sections tss
CROSS JOIN (VALUES
    ('F.10', 'F.10.1', 'Half brick walls', 'Half brick walls in common bricks in Class II mortar', 'm²', 'area', 'SANS 227'),
    ('F.10', 'F.10.2', 'One brick walls', 'One brick walls in common bricks in Class II mortar', 'm²', 'area', 'SANS 227'),
    ('F.10', 'F.10.3', 'Hollow walls', 'Hollow walls two half brick skins with 50mm cavity', 'm²', 'area', 'SANS 227'),
    ('F.13', 'F.13.1', 'Face brickwork NFP', 'Face brickwork in NFP facing bricks extra over', 'm²', 'area', 'SANS 227'),
    ('F.13', 'F.13.2', 'Face brickwork FBS', 'Face brickwork in FBS facing bricks extra over', 'm²', 'area', 'SANS 227'),
    ('F.11', 'F.11.1', 'Blockwork 140mm', '140mm hollow concrete blockwork in Class II mortar', 'm²', 'area', 'SANS 1215'),
    ('F.11', 'F.11.2', 'Blockwork 190mm', '190mm hollow concrete blockwork in Class II mortar', 'm²', 'area', 'SANS 1215'),
    ('F.11', 'F.11.3', 'Blockwork 90mm', '90mm solid concrete blockwork in Class II mortar', 'm²', 'area', 'SANS 1215')
) AS t(sub_code, item_code, short_desc, full_desc, unit_code, category, sans_ref)
JOIN units_of_measurement u ON u.code = t.unit_code
WHERE tss.code = t.sub_code;

-- =============================================================================
-- SECTION 6: PROJECT-LEVEL TABLES
-- =============================================================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_number VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    client_name VARCHAR(200),
    site_address TEXT,
    
    -- Project classification
    building_type VARCHAR(100),  -- Residential, Commercial, Industrial, etc.
    contract_type VARCHAR(50),   -- JBCC, NEC, FIDIC, etc.
    
    -- Key metrics
    gross_floor_area_m2 DECIMAL(12,2),
    number_of_storeys INT,
    
    -- Standards
    measurement_standard_id UUID REFERENCES measurement_standards(id),
    
    -- Status and dates
    status VARCHAR(50) DEFAULT 'draft',
    tender_date DATE,
    contract_date DATE,
    completion_date DATE,
    
    -- Currency
    currency CHAR(3) DEFAULT 'ZAR',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bills within a project (can have multiple)
CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    bill_number INT NOT NULL,
    name VARCHAR(200) NOT NULL,  -- 'Bill No. 1 - Preliminaries', etc.
    description TEXT,
    sort_order INT,
    
    -- Totals (calculated)
    subtotal DECIMAL(15,2) DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(project_id, bill_number)
);

-- Sections within bills
CREATE TABLE bill_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bill_id UUID REFERENCES bills(id) ON DELETE CASCADE,
    trade_section_id UUID REFERENCES trade_sections(id),
    
    section_number VARCHAR(20),
    name VARCHAR(200),
    preamble_notes TEXT,  -- Project-specific preamble additions
    
    sort_order INT,
    subtotal DECIMAL(15,2) DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- SECTION 7: BOQ LINE ITEMS (THE ACTUAL MEASURED QUANTITIES)
-- =============================================================================

CREATE TABLE boq_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bill_section_id UUID REFERENCES bill_sections(id) ON DELETE CASCADE,
    template_id UUID REFERENCES boq_item_templates(id),  -- Link to template if used
    
    -- Item identification
    item_number VARCHAR(20),
    
    -- Description (can override template)
    short_description VARCHAR(200) NOT NULL,
    full_description TEXT,
    
    -- Drawing references
    drawing_reference VARCHAR(100),
    location_reference VARCHAR(200),  -- 'Ground Floor', 'Block A', etc.
    
    -- Measurement
    unit_id UUID REFERENCES units_of_measurement(id),
    quantity DECIMAL(15,4),
    
    -- Pricing
    rate DECIMAL(15,4),
    amount DECIMAL(15,2) GENERATED ALWAYS AS (quantity * rate) STORED,
    
    -- Classification
    is_provisional BOOLEAN DEFAULT false,
    is_prime_cost BOOLEAN DEFAULT false,
    
    -- Sorting
    sort_order INT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- SECTION 8: DIMENSION RECORDS (TAKING OFF)
-- =============================================================================

CREATE TABLE dimension_sheets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    
    sheet_number INT,
    name VARCHAR(200),
    drawing_reference VARCHAR(100),
    measured_by VARCHAR(100),
    checked_by VARCHAR(100),
    date_measured DATE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE dimension_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dimension_sheet_id UUID REFERENCES dimension_sheets(id) ON DELETE CASCADE,
    boq_item_id UUID REFERENCES boq_items(id),
    
    -- Traditional taking off format
    timesing INT DEFAULT 1,  -- Number of times (multiplier)
    length DECIMAL(12,4),
    width DECIMAL(12,4),
    height_depth DECIMAL(12,4),
    
    -- Calculated quantity
    calculated_quantity DECIMAL(15,4),
    
    -- Notes and references
    description TEXT,
    location VARCHAR(200),
    drawing_detail VARCHAR(100),
    
    -- Is this a deduction?
    is_deduction BOOLEAN DEFAULT false,
    
    sort_order INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- SECTION 9: CROSS-REFERENCE MAPPING (TRADE TO NRM ELEMENTS)
-- =============================================================================

-- Maps ASAQS trades to NRM1 elements for elemental cost analysis
CREATE TABLE trade_element_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_section_id UUID REFERENCES trade_sections(id),
    trade_sub_section_id UUID REFERENCES trade_sub_sections(id),
    nrm_element_id UUID REFERENCES nrm_elements(id),
    mapping_notes TEXT,
    percentage_allocation DECIMAL(5,2) DEFAULT 100.00,  -- For items spanning multiple elements
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- SECTION 10: COST DATABASE (HISTORICAL RATES)
-- =============================================================================

CREATE TABLE cost_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES boq_item_templates(id),
    
    -- Source
    source_type VARCHAR(50),  -- 'tender', 'budget', 'published'
    source_reference VARCHAR(200),
    source_date DATE,
    
    -- Location and scope
    region VARCHAR(100),  -- 'Gauteng', 'Western Cape', etc.
    project_type VARCHAR(100),
    
    -- Rate data
    rate DECIMAL(15,4),
    currency CHAR(3) DEFAULT 'ZAR',
    
    -- Validity
    valid_from DATE,
    valid_to DATE,
    
    -- Adjustments
    base_date DATE,
    cpi_index DECIMAL(8,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- SECTION 11: DOCUMENT PROCESSING (FOR AI AGENT)
-- =============================================================================

CREATE TABLE source_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    
    document_type VARCHAR(50),  -- 'architectural_drawing', 'structural_drawing', 'specification', etc.
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_hash VARCHAR(64),  -- For deduplication
    
    -- Processing status
    processing_status VARCHAR(50) DEFAULT 'pending',
    processed_at TIMESTAMPTZ,
    
    -- Extracted metadata
    drawing_number VARCHAR(100),
    revision VARCHAR(20),
    scale VARCHAR(20),
    date_on_drawing DATE,
    
    -- AI extraction results
    extraction_confidence DECIMAL(5,4),
    extraction_notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Elements extracted from documents by AI
CREATE TABLE document_extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES source_documents(id) ON DELETE CASCADE,
    
    -- What was identified
    element_type VARCHAR(100),  -- 'wall', 'door', 'window', 'floor_area', etc.
    element_description TEXT,
    
    -- Location in document
    page_number INT,
    bounding_box JSONB,  -- {x, y, width, height}
    
    -- Measurements extracted
    measurement_type VARCHAR(50),  -- 'length', 'area', 'count'
    measurement_value DECIMAL(15,4),
    measurement_unit VARCHAR(20),
    
    -- Mapping to BOQ
    suggested_template_id UUID REFERENCES boq_item_templates(id),
    mapping_confidence DECIMAL(5,4),
    
    -- Verification
    is_verified BOOLEAN DEFAULT false,
    verified_by VARCHAR(100),
    verified_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- SECTION 12: USEFUL VIEWS
-- =============================================================================

-- Complete BOQ view with all details
CREATE VIEW vw_complete_boq AS
SELECT 
    p.id AS project_id,
    p.name AS project_name,
    p.project_number,
    b.bill_number,
    b.name AS bill_name,
    bs.section_number,
    ts.code AS trade_code,
    ts.name AS trade_name,
    bi.item_number,
    bi.short_description,
    bi.full_description,
    bi.drawing_reference,
    bi.location_reference,
    u.code AS unit,
    bi.quantity,
    bi.rate,
    bi.amount,
    bi.is_provisional,
    bi.is_prime_cost
FROM projects p
JOIN bills b ON b.project_id = p.id
JOIN bill_sections bs ON bs.bill_id = b.id
JOIN trade_sections ts ON ts.id = bs.trade_section_id
JOIN boq_items bi ON bi.bill_section_id = bs.id
LEFT JOIN units_of_measurement u ON u.id = bi.unit_id
ORDER BY p.name, b.bill_number, bs.sort_order, bi.sort_order;

-- Trade summary by project
CREATE VIEW vw_trade_summary AS
SELECT 
    p.id AS project_id,
    p.name AS project_name,
    ts.code AS trade_code,
    ts.name AS trade_name,
    COUNT(bi.id) AS item_count,
    SUM(bi.amount) AS trade_total
FROM projects p
JOIN bills b ON b.project_id = p.id
JOIN bill_sections bs ON bs.bill_id = b.id
JOIN trade_sections ts ON ts.id = bs.trade_section_id
JOIN boq_items bi ON bi.bill_section_id = bs.id
GROUP BY p.id, p.name, ts.code, ts.name
ORDER BY p.name, ts.code;

-- =============================================================================
-- SECTION 13: INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX idx_trade_sections_standard ON trade_sections(standard_id);
CREATE INDEX idx_trade_sub_sections_trade ON trade_sub_sections(trade_section_id);
CREATE INDEX idx_boq_templates_sub_section ON boq_item_templates(trade_sub_section_id);
CREATE INDEX idx_boq_items_section ON boq_items(bill_section_id);
CREATE INDEX idx_boq_items_template ON boq_items(template_id);
CREATE INDEX idx_dimension_items_sheet ON dimension_items(dimension_sheet_id);
CREATE INDEX idx_dimension_items_boq ON dimension_items(boq_item_id);
CREATE INDEX idx_cost_rates_template ON cost_rates(template_id);
CREATE INDEX idx_document_extractions_doc ON document_extractions(document_id);

-- Full text search on descriptions
CREATE INDEX idx_boq_templates_desc_fts ON boq_item_templates USING gin(to_tsvector('english', short_description || ' ' || COALESCE(full_description, '')));
CREATE INDEX idx_boq_items_desc_fts ON boq_items USING gin(to_tsvector('english', short_description || ' ' || COALESCE(full_description, '')));
