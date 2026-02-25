# Lab Data Normalization Tool

## Overview

The `normalize_lab_data_tool` standardizes lab parameters extracted from medical reports by:
1. **Parameter Name Standardization** - Maps variations to canonical names
2. **Unit Conversion** - Converts values to standard units
3. **Reference Range Alignment** - Provides standard reference ranges

## Architecture

### Components

```
tools/src/document_data_extraction_tools/
├── normalize_lab_data_tool.py      # Main tool entry point
├── lab_data_normalizer.py          # Core normalization logic
└── README_NORMALIZE_LAB_DATA.md    # This file

models/
├── lab_parameter.py                # Input parameter schema
├── normalized_parameter.py         # Output parameter schema
├── normalization_result.py         # Result schema
└── database_connection.py          # DB connection manager
```

### Database Tables

#### Existing Tables (Used)
- `health_parameters` - Source of raw lab data (READ + UPDATE)
- `normalized_parameters` - Stores normalized results (INSERT)
- `normalization_audit_logs` - Audit trail of operations (INSERT)

#### New Tables (Required)
- `parameter_name_mappings` - Name variation → canonical name mappings
- `unit_conversion_rules` - Unit conversion factors
- `standard_reference_ranges` - Standard reference ranges

## Installation

### 1. Database Setup

Run the normalization tables script:

```bash
# If using Docker
docker exec -i medical-health-review-db psql -U postgres -d medical_health_review < init-scripts/02-normalization-tables.sql

# If using local PostgreSQL
psql -U postgres -d medical_health_review -f init-scripts/02-normalization-tables.sql
```

### 2. Python Dependencies

Install required packages:

```bash
pip install psycopg2-binary pydantic
```

### 3. Environment Variables

Ensure these are set in your `.env` file:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=medical_health_review
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

## Usage

### Single Parameter Normalization

```python
from tools.src.document_data_extraction_tools.normalize_lab_data_tool import normalize_lab_data

result = normalize_lab_data(
    parameter_id="550e8400-e29b-41d4-a716-446655440000",
    user_id="USER-123ABC",
    parameter_name="Blood Glucose",
    value=117.0,
    unit="mg/dL"
)

if result['success']:
    print(f"Normalized value: {result['normalized_parameter']['normalized_value']}")
    print(f"Standard unit: {result['normalized_parameter']['standard_unit']}")
else:
    print(f"Errors: {result['errors']}")
```

### Batch Normalization

```python
from tools.src.document_data_extraction_tools.normalize_lab_data_tool import normalize_batch

parameters = [
    {
        "parameter_id": "uuid-1",
        "user_id": "USER-123",
        "parameter_name": "Blood Glucose",
        "value": 117.0,
        "unit": "mg/dL"
    },
    {
        "parameter_id": "uuid-2",
        "user_id": "USER-123",
        "parameter_name": "HbA1c",
        "value": 6.5,
        "unit": "%"
    }
]

batch_result = normalize_batch(parameters)
print(f"Successful: {batch_result['successful']}/{batch_result['total']}")
```

## Normalization Workflow

```
1. READ health_parameters (WHERE normalization_status = 'pending')
   ↓
2. LOOKUP parameter_name_mappings (get canonical name)
   → LOG to normalization_audit_logs (operation: 'name_mapping')
   ↓
3. LOOKUP unit_conversion_rules (get conversion factor)
   → LOG to normalization_audit_logs (operation: 'unit_conversion')
   ↓
4. LOOKUP standard_reference_ranges (get standard range)
   → LOG to normalization_audit_logs (operation: 'range_alignment')
   ↓
5. INSERT to normalized_parameters (final result)
   ↓
6. UPDATE health_parameters (SET normalization_status = 'normalized')
```

## Result Schema

```python
{
    "success": bool,                    # Whether normalization succeeded
    "normalized_parameter": {           # Normalized data (if successful)
        "normalized_parameter_id": str,
        "original_parameter_id": str,
        "user_id": str,
        "canonical_name": str,
        "original_value": float,
        "original_unit": str,
        "normalized_value": float,
        "standard_unit": str,
        "conversion_factor": float,
        "reference_range_min": float,
        "reference_range_max": float,
        "normalization_confidence": float
    },
    "operations_logged": int,           # Number of audit log entries
    "errors": [str],                    # Error messages
    "warnings": [str],                  # Warning messages
    "flagged_for_review": bool          # Requires human review
}
```

## Confidence Scoring

The tool calculates an overall confidence score (0-1) based on:
- **Name mapping confidence** - How certain the canonical name mapping is
- **Unit conversion confidence** - How certain the unit conversion is
- **Reference range confidence** - How certain the reference range is

**Overall confidence = (name_conf + unit_conf + range_conf) / 3**

Parameters with confidence < 0.7 are automatically flagged for human review.

## Error Handling

### Flagged for Review

Parameters are flagged when:
- No canonical name mapping found
- No unit conversion rule found
- Overall confidence < 0.7

Flagged parameters:
- Have `normalization_status = 'flagged'` in `health_parameters`
- Are logged in `normalization_audit_logs` with `status = 'flagged'`
- Return `flagged_for_review = True` in result

### Failed Operations

Failed operations:
- Are logged with `status = 'failed'` and `failure_reason`
- Do not create records in `normalized_parameters`
- Return `success = False` with error details

## Sample Data

The schema includes sample data for testing:

### Supported Parameters
- Glucose (Blood Glucose, Blood Sugar, FBS, etc.)
- HbA1c (Hemoglobin A1C, Glycated Hemoglobin, etc.)
- Total Cholesterol
- HDL Cholesterol
- LDL Cholesterol
- Triglycerides

### Supported Unit Conversions
- Glucose: mg/dL → mmol/L (factor: 0.0555)
- HbA1c: mmol/mol → % (factor: 0.0915)
- Cholesterol: mg/dL → mmol/L (factor: 0.0259)
- Triglycerides: mg/dL → mmol/L (factor: 0.0113)

## Testing

Run the tool directly to test:

```bash
cd agentic-medical-health-review
python tools/src/document_data_extraction_tools/normalize_lab_data_tool.py
```

This will run a test normalization and display results.

## Adding New Parameters

### 1. Add Name Mappings

```sql
INSERT INTO parameter_name_mappings (variant_name, canonical_name, confidence_score)
VALUES ('Vitamin D', 'vitamin_d', 1.0);
```

### 2. Add Unit Conversions

```sql
INSERT INTO unit_conversion_rules (canonical_parameter_name, source_unit, target_unit, conversion_factor)
VALUES ('vitamin_d', 'ng/mL', 'nmol/L', 2.496);
```

### 3. Add Reference Ranges

```sql
INSERT INTO standard_reference_ranges (canonical_parameter_name, standard_unit, range_min, range_max, source)
VALUES ('vitamin_d', 'nmol/L', 50.0, 125.0, 'Endocrine Society Guidelines');
```

## Audit Trail

All operations are logged to `normalization_audit_logs`:

```sql
SELECT 
    operation,
    status,
    original_name,
    canonical_name,
    original_value,
    original_unit,
    normalized_value,
    standard_unit,
    conversion_factor,
    failure_reason,
    timestamp
FROM normalization_audit_logs
WHERE parameter_id = 'your-parameter-id'
ORDER BY timestamp;
```

## Integration with Other Tools

This tool is designed to work with:
- **lab_report_parser_tool** - Provides raw extracted data
- **mismatch_detection_tool** - Uses normalized data for comparisons
- **trend_computation_tool** - Uses normalized data for trend analysis
- **risk_assessment_tool** - Uses normalized data for risk scoring

## Troubleshooting

### Connection Errors
- Verify PostgreSQL is running
- Check `.env` file has correct credentials
- Ensure database `medical_health_review` exists

### Missing Mappings
- Check `parameter_name_mappings` table for the parameter name
- Add new mappings if needed
- Review audit logs for flagged operations

### Low Confidence Scores
- Review the confidence scores in reference tables
- Update mappings with higher confidence
- Add more specific mappings for variations

## Future Enhancements

- Age and gender-specific reference ranges
- Multi-language parameter name support
- Automatic learning from human reviews
- Batch processing optimization
- Real-time normalization API endpoint
