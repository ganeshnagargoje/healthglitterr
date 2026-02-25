-- Additional Parameter Name Mappings for Common Lab Tests
-- Run this to add more parameter mappings to the database

-- Hemoglobin variations
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('Haemoglobin', 'hemoglobin', 1.0),
('Hemoglobin', 'hemoglobin', 1.0),
('Hb', 'hemoglobin', 0.95),
('HGB', 'hemoglobin', 0.95)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- PCV / Hematocrit
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('PCV (Packed Cell Volume)/Hematocrit', 'hematocrit', 1.0),
('Hematocrit', 'hematocrit', 1.0),
('PCV', 'hematocrit', 0.95),
('Packed Cell Volume', 'hematocrit', 0.95),
('HCT', 'hematocrit', 0.90)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- RBC Count
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('RBC Count', 'rbc_count', 1.0),
('Red Blood Cell Count', 'rbc_count', 1.0),
('RBC', 'rbc_count', 0.95),
('Erythrocyte Count', 'rbc_count', 0.90)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- MCH
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('MCH (Mean Corpuscular Hemoglobin)', 'mch', 1.0),
('MCH', 'mch', 1.0),
('Mean Corpuscular Hemoglobin', 'mch', 1.0)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- Eosinophils
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('Eosinophils %', 'eosinophils_percent', 1.0),
('Eosinophils', 'eosinophils_percent', 0.95),
('EOS %', 'eosinophils_percent', 0.90)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- Absolute Eosinophil Count
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('Absolute Eosinophil Count', 'eosinophils_absolute', 1.0),
('AEC', 'eosinophils_absolute', 0.95)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- Platelet Count
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('Platelet Count', 'platelet_count', 1.0),
('Platelets', 'platelet_count', 0.95),
('PLT', 'platelet_count', 0.90)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- MPV (Mean Platelet Volume)
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('MPV', 'mpv', 1.0),
('Mean Platelet Volume', 'mpv', 1.0)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- PCT (Plateletcrit)
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('PCT', 'plateletcrit', 1.0),
('Plateletcrit', 'plateletcrit', 1.0)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- ESR
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('ESR (Erythrocyte Sedimentation Rate)', 'esr', 1.0),
('ESR', 'esr', 1.0),
('Erythrocyte Sedimentation Rate', 'esr', 1.0),
('Sed Rate', 'esr', 0.90)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- GFR
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('GFR Study', 'gfr', 1.0),
('GFR', 'gfr', 1.0),
('Glomerular Filtration Rate', 'gfr', 1.0),
('eGFR', 'gfr', 0.95)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- Glycosylated Haemoglobin (already exists but add this variation)
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score) VALUES
('Glycosylated Haemoglobin (HbA1c)', 'hemoglobin_a1c', 1.0),
('Glycosylated Haemoglobin', 'hemoglobin_a1c', 1.0)
ON CONFLICT (variant_name, canonical_name) DO NOTHING;

-- Unit conversion rules for new parameters
INSERT INTO unit_conversion_rules (canonical_parameter_name, source_unit, target_unit, conversion_factor, confidence_score) VALUES
('hemoglobin', 'g/dL', 'g/dL', 1.0, 1.0),
('hemoglobin', 'g/L', 'g/dL', 0.1, 1.0),
('hematocrit', '%', '%', 1.0, 1.0),
('rbc_count', 'mill/cu.mm', 'mill/cu.mm', 1.0, 1.0),
('rbc_count', '10^6/μL', 'mill/cu.mm', 1.0, 1.0),
('mch', 'pg', 'pg', 1.0, 1.0),
('eosinophils_percent', '%', '%', 1.0, 1.0),
('eosinophils_absolute', '10^3/ L', '10^3/μL', 1.0, 1.0),
('eosinophils_absolute', '10^3/μL', '10^3/μL', 1.0, 1.0),
('platelet_count', '10^3/ L', '10^3/μL', 1.0, 1.0),
('platelet_count', '10^3/μL', '10^3/μL', 1.0, 1.0),
('mpv', 'fL', 'fL', 1.0, 1.0),
('plateletcrit', '%', '%', 1.0, 1.0),
('esr', 'mm/hr', 'mm/hr', 1.0, 1.0),
('gfr', 'mL/min/1.7 sq.m', 'mL/min/1.73m²', 1.0, 1.0),
('gfr', 'mL/min/1.73m²', 'mL/min/1.73m²', 1.0, 1.0)
ON CONFLICT (canonical_parameter_name, source_unit, target_unit) DO NOTHING;

-- Standard reference ranges for new parameters
INSERT INTO standard_reference_ranges (canonical_parameter_name, standard_unit, range_min, range_max, gender, confidence_score, source) VALUES
('hemoglobin', 'g/dL', 13.5, 18.0, 'Male', 1.0, 'WHO Guidelines'),
('hemoglobin', 'g/dL', 12.0, 16.0, 'Female', 1.0, 'WHO Guidelines'),
('hematocrit', '%', 42.0, 52.0, 'Male', 1.0, 'Clinical Reference'),
('hematocrit', '%', 37.0, 47.0, 'Female', 1.0, 'Clinical Reference'),
('rbc_count', 'mill/cu.mm', 4.7, 6.0, 'Male', 1.0, 'Clinical Reference'),
('rbc_count', 'mill/cu.mm', 4.2, 5.4, 'Female', 1.0, 'Clinical Reference'),
('mch', 'pg', 27.0, 32.0, NULL, 1.0, 'Clinical Reference'),
('eosinophils_percent', '%', 1.0, 6.0, NULL, 1.0, 'Clinical Reference'),
('eosinophils_absolute', '10^3/μL', 0.04, 0.44, NULL, 1.0, 'Clinical Reference'),
('platelet_count', '10^3/μL', 150.0, 450.0, NULL, 1.0, 'Clinical Reference'),
('mpv', 'fL', 7.9, 13.7, NULL, 1.0, 'Clinical Reference'),
('plateletcrit', '%', 0.18, 0.28, NULL, 1.0, 'Clinical Reference'),
('esr', 'mm/hr', 0.0, 15.0, 'Male', 1.0, 'Clinical Reference'),
('esr', 'mm/hr', 0.0, 20.0, 'Female', 1.0, 'Clinical Reference'),
('gfr', 'mL/min/1.73m²', 90.0, 999.0, NULL, 1.0, 'KDIGO Guidelines')
ON CONFLICT DO NOTHING;

-- Display summary
SELECT 'Parameter mappings added successfully!' as status;
SELECT COUNT(*) as total_mappings FROM parameter_name_mappings;
SELECT COUNT(*) as total_conversion_rules FROM unit_conversion_rules;
SELECT COUNT(*) as total_reference_ranges FROM standard_reference_ranges;
