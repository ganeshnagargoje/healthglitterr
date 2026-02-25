-- Additional tables for lab data normalization
-- This script adds reference tables needed by normalize_lab_data_tool

-- Parameter name mappings table
-- Maps various parameter name variations to canonical standardized names
CREATE TABLE parameter_name_mappings (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    variant_name VARCHAR(255) NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    confidence_score DECIMAL(3, 2) DEFAULT 1.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(variant_name, canonical_name)
);

-- Unit conversion rules table
-- Stores conversion factors between different units for each parameter
CREATE TABLE unit_conversion_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_parameter_name VARCHAR(255) NOT NULL,
    source_unit VARCHAR(50) NOT NULL,
    target_unit VARCHAR(50) NOT NULL,
    conversion_factor DECIMAL(15, 10) NOT NULL,
    confidence_score DECIMAL(3, 2) DEFAULT 1.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(canonical_parameter_name, source_unit, target_unit)
);

-- Standard reference ranges table
-- Stores canonical reference ranges for each parameter
-- Supports age and gender-specific ranges
CREATE TABLE standard_reference_ranges (
    range_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_parameter_name VARCHAR(255) NOT NULL,
    standard_unit VARCHAR(50) NOT NULL,
    range_min DECIMAL(10, 4),
    range_max DECIMAL(10, 4),
    age_min INT,
    age_max INT,
    gender VARCHAR(20),
    confidence_score DECIMAL(3, 2) DEFAULT 1.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_parameter_name_mappings_variant ON parameter_name_mappings(variant_name);
CREATE INDEX idx_parameter_name_mappings_canonical ON parameter_name_mappings(canonical_name);
CREATE INDEX idx_unit_conversion_rules_parameter ON unit_conversion_rules(canonical_parameter_name);
CREATE INDEX idx_unit_conversion_rules_source_unit ON unit_conversion_rules(source_unit);
CREATE INDEX idx_standard_reference_ranges_parameter ON standard_reference_ranges(canonical_parameter_name);

-- Create triggers for updated_at
CREATE TRIGGER update_parameter_name_mappings_updated_at
    BEFORE UPDATE ON parameter_name_mappings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_unit_conversion_rules_updated_at
    BEFORE UPDATE ON unit_conversion_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_standard_reference_ranges_updated_at
    BEFORE UPDATE ON standard_reference_ranges
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

-- Parameter name mappings
-- Glucose/Blood Sugar variations
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('Blood Glucose', 'glucose_fasting', 1.0),
('Blood Sugar', 'glucose_fasting', 0.95),
('Fasting Glucose', 'glucose_fasting', 1.0),
('Fasting Blood Sugar', 'glucose_fasting', 0.95),
('FBS', 'glucose_fasting', 0.90),
('Glucose', 'glucose_fasting', 0.85);

-- HbA1c variations
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('HbA1c', 'hemoglobin_a1c', 1.0),
('Hemoglobin A1C', 'hemoglobin_a1c', 1.0),
('Glycated Hemoglobin', 'hemoglobin_a1c', 0.95),
('A1C', 'hemoglobin_a1c', 0.90),
('Glycohemoglobin', 'hemoglobin_a1c', 0.90);

-- Cholesterol variations
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('Total Cholesterol', 'cholesterol_total', 1.0),
('Cholesterol', 'cholesterol_total', 0.90),
('Serum Cholesterol', 'cholesterol_total', 0.95);

-- HDL variations
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('HDL Cholesterol', 'cholesterol_hdl', 1.0),
('HDL', 'cholesterol_hdl', 0.95),
('High Density Lipoprotein', 'cholesterol_hdl', 0.90);

-- LDL variations
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('LDL Cholesterol', 'cholesterol_ldl', 1.0),
('LDL', 'cholesterol_ldl', 0.95),
('Low Density Lipoprotein', 'cholesterol_ldl', 0.90);

-- Triglycerides variations
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('Triglycerides', 'triglycerides', 1.0),
('TG', 'triglycerides', 0.90),
('Serum Triglycerides', 'triglycerides', 0.95);

-- Unit conversion rules
-- Glucose conversions
INSERT INTO unit_conversion_rules (canonical_parameter_name, source_unit, target_unit, conversion_factor, confidence_score) VALUES
('glucose_fasting', 'mg/dL', 'mmol/L', 0.0555, 1.0),
('glucose_fasting', 'mmol/L', 'mmol/L', 1.0, 1.0);

-- HbA1c conversions
INSERT INTO unit_conversion_rules (canonical_parameter_name, source_unit, target_unit, conversion_factor, confidence_score) VALUES
('hemoglobin_a1c', '%', '%', 1.0, 1.0),
('hemoglobin_a1c', 'mmol/mol', '%', 0.0915, 0.95);

-- Cholesterol conversions (Total, HDL, LDL)
INSERT INTO unit_conversion_rules (canonical_parameter_name, source_unit, target_unit, conversion_factor, confidence_score) VALUES
('cholesterol_total', 'mg/dL', 'mmol/L', 0.0259, 1.0),
('cholesterol_total', 'mmol/L', 'mmol/L', 1.0, 1.0),
('cholesterol_hdl', 'mg/dL', 'mmol/L', 0.0259, 1.0),
('cholesterol_hdl', 'mmol/L', 'mmol/L', 1.0, 1.0),
('cholesterol_ldl', 'mg/dL', 'mmol/L', 0.0259, 1.0),
('cholesterol_ldl', 'mmol/L', 'mmol/L', 1.0, 1.0);

-- Triglycerides conversions
INSERT INTO unit_conversion_rules (canonical_parameter_name, source_unit, target_unit, conversion_factor, confidence_score) VALUES
('triglycerides', 'mg/dL', 'mmol/L', 0.0113, 1.0),
('triglycerides', 'mmol/L', 'mmol/L', 1.0, 1.0);

-- Standard reference ranges
-- Glucose (fasting)
INSERT INTO standard_reference_ranges (canonical_parameter_name, standard_unit, range_min, range_max, confidence_score, source) VALUES
('glucose_fasting', 'mmol/L', 3.9, 5.6, 1.0, 'ADA Guidelines 2024');

-- HbA1c
INSERT INTO standard_reference_ranges (canonical_parameter_name, standard_unit, range_min, range_max, confidence_score, source) VALUES
('hemoglobin_a1c', '%', 4.0, 5.6, 1.0, 'ADA Guidelines 2024');

-- Total Cholesterol
INSERT INTO standard_reference_ranges (canonical_parameter_name, standard_unit, range_min, range_max, confidence_score, source) VALUES
('cholesterol_total', 'mmol/L', 0.0, 5.2, 1.0, 'NCEP ATP III Guidelines');

-- HDL Cholesterol
INSERT INTO standard_reference_ranges (canonical_parameter_name, standard_unit, range_min, range_max, confidence_score, source) VALUES
('cholesterol_hdl', 'mmol/L', 1.0, 999.0, 1.0, 'NCEP ATP III Guidelines');

-- LDL Cholesterol
INSERT INTO standard_reference_ranges (canonical_parameter_name, standard_unit, range_min, range_max, confidence_score, source) VALUES
('cholesterol_ldl', 'mmol/L', 0.0, 3.4, 1.0, 'NCEP ATP III Guidelines');

-- Triglycerides
INSERT INTO standard_reference_ranges (canonical_parameter_name, standard_unit, range_min, range_max, confidence_score, source) VALUES
('triglycerides', 'mmol/L', 0.0, 1.7, 1.0, 'NCEP ATP III Guidelines');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE parameter_name_mappings IS 'Maps various lab parameter name variations to canonical standardized names';
COMMENT ON TABLE unit_conversion_rules IS 'Stores unit conversion factors for normalizing lab values to standard units';
COMMENT ON TABLE standard_reference_ranges IS 'Canonical reference ranges for lab parameters in standard units';

COMMENT ON COLUMN parameter_name_mappings.variant_name IS 'Original parameter name as it appears in lab reports';
COMMENT ON COLUMN parameter_name_mappings.canonical_name IS 'Standardized parameter name used throughout the system';
COMMENT ON COLUMN parameter_name_mappings.confidence_score IS 'Confidence in this mapping (0-1), lower scores may require review';

COMMENT ON COLUMN unit_conversion_rules.source_unit IS 'Original unit from lab report';
COMMENT ON COLUMN unit_conversion_rules.target_unit IS 'Standard unit to convert to';
COMMENT ON COLUMN unit_conversion_rules.conversion_factor IS 'Multiply source value by this to get target value';

COMMENT ON COLUMN standard_reference_ranges.age_min IS 'Minimum age for this range (NULL = no minimum)';
COMMENT ON COLUMN standard_reference_ranges.age_max IS 'Maximum age for this range (NULL = no maximum)';
COMMENT ON COLUMN standard_reference_ranges.gender IS 'Gender for this range (NULL = applies to all)';
