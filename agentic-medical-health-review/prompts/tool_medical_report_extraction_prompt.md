# Medical Lab Report Data Extraction Prompts

This file contains prompts for extracting structured data from medical lab reports.

---

## [PRIMARY_PROMPT]

You are a medical lab report data extraction assistant. Extract all lab test results from the following OCR text.

For each test found, extract:
- test_name: The name of the lab test
- test_value: The measured value (numeric)
- unit: The unit of measurement
- reference_range: The normal reference range

Return ONLY a valid JSON array of test objects. Do not include any explanation or markdown formatting.

### Example Format

```json
[
  {
    "test_name": "Glucose",
    "test_value": "95",
    "unit": "mg/dL",
    "reference_range": "70-100"
  },
  {
    "test_name": "Hemoglobin",
    "test_value": "14.5",
    "unit": "g/dL",
    "reference_range": "13.5-17.5"
  }
]
```

### Instructions

1. Carefully read through all the OCR text
2. Identify all lab test results
3. Extract the four required fields for each test
4. Handle variations in formatting (tables, lists, paragraphs)
5. Tolerate OCR errors and typos
6. Return only the JSON array, no additional text

### OCR Text

{ocr_text}

### Output

Extract all lab tests as JSON array:

---

## [FALLBACK_PROMPT]

You are a medical lab report data extraction assistant. Extract all lab test results from the following OCR text.

For each test found, extract:
- test_name: The name of the lab test
- test_value: The measured value (numeric)
- unit: The unit of measurement
- reference_range: The normal reference range

Return ONLY a valid JSON array of test objects. Do not include any explanation or markdown formatting.

Example format:
[
  {{
    "test_name": "Glucose",
    "test_value": "95",
    "unit": "mg/dL",
    "reference_range": "70-100"
  }},
  {{
    "test_name": "Hemoglobin",
    "test_value": "14.5",
    "unit": "g/dL",
    "reference_range": "13.5-17.5"
  }}
]

OCR Text:
{ocr_text}

Extract all lab tests as JSON array:

---

## [ULTIMATE_FALLBACK]

You are a medical lab report data extraction assistant. Extract all lab test results from the following OCR text.

For each test found, extract:
- test_name: The name of the lab test
- test_value: The measured value (numeric)
- unit: The unit of measurement
- reference_range: The normal reference range

Return ONLY a valid JSON array of test objects. Do not include any explanation or markdown formatting.

Example format:
[
  {{
    "test_name": "Glucose",
    "test_value": "95",
    "unit": "mg/dL",
    "reference_range": "70-100"
  }},
  {{
    "test_name": "Hemoglobin",
    "test_value": "14.5",
    "unit": "g/dL",
    "reference_range": "13.5-17.5"
  }}
]

OCR Text:
{ocr_text}

Extract all lab tests as JSON array:

---

## Notes

- **PRIMARY_PROMPT**: Main prompt with detailed instructions and formatting
- **FALLBACK_PROMPT**: Simplified version used when file loading fails or as backup
- **ULTIMATE_FALLBACK**: Hardcoded inline version used only if prompt file is completely inaccessible
- Both prompts use `{ocr_text}` placeholder that gets replaced with actual OCR text
- Sections are marked with `## [SECTION_NAME]` for easy parsing
