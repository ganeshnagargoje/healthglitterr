# Lab Report Parser - End-to-End Testing Guide

## 🎯 Overview

This testing suite provides **end-to-end extraction** of lab test data from PDF files and images. The pipeline uses:

1. **PaddleOCR** - Extracts text from PDF/images
2. **LLM (GPT-4o-mini)** - Intelligently parses text into structured JSON
3. **Structured Output** - Returns test name, value, unit, and reference range

## 🚀 Quick Start

### End-to-End Test with Real PDF

```bash
# Navigate to test directory
cd agentic-medical-health-review/tests/tools/document_data_extraction_tools

# Test with LLM extraction (recommended - more robust)
python test_real_file.py ../../test_data/sample_reports/lab_report1_page_1.pdf --llm --save

# Test with regex extraction (faster, less accurate)
python test_real_file.py path/to/your/lab_report.pdf --save

# Get raw OCR text only
python test_real_file.py path/to/your/lab_report.pdf --format text
```

### Test LLM Extraction Only (No OCR)

```bash
# Test LLM extraction with sample text (bypasses OCR)
python test_with_sample_text.py
```

### Prerequisites

1. **Python 3.8-3.12**
2. **OpenAI API Key** (for LLM extraction)
   - Get your key from: https://platform.openai.com/api-keys
   - Set in `.env` file: `OPENAI_API_KEY=your-key-here`
3. **PaddleOCR** (for OCR text extraction)
   - Install: `pip install paddleocr`
4. **Poppler** (for PDF processing)
   - **Windows:** Download from https://github.com/oschwartz10612/poppler-windows/releases/ and add to PATH
   - **Linux:** `sudo apt-get install poppler-utils`
   - **Mac:** `brew install poppler`

### Setup .env File

Create a `.env` file in `agentic-medical-health-review/` directory:

```bash
# .env file
OPENAI_API_KEY=your-openai-api-key-here
```

Or use the provided `.env.example` as a template.

---

## 📁 Files in This Directory

### Test Scripts
- **`test_real_file.py`** ⭐ **Main end-to-end test** - PDF/Image → OCR → LLM → JSON
- **`test_with_sample_text.py`** - Test LLM extraction only (bypasses OCR)
- **`test_env.py`** - Verify environment setup (API keys, dependencies)

### Documentation
- **`README.md`** - This file

---

## 📖 Usage Examples

### Example 1: End-to-End Test with LLM (Recommended)
```bash
# Extract structured data using LLM (most accurate)
python test_real_file.py ../../test_data/sample_reports/lab_report1_page_1.pdf --llm --save
```

**Output:**
```
✓ Extraction complete!
Status: success
Tests found: 12
Raw text length: 1289 characters

Extracted Lab Tests:
1. Haemoglobin: 8.7 g/dL (13.5 - 18.0)
2. PCV/Hematocrit: 25.6% (42 - 52)
...
💾 Saved to: lab_report1_page_1_extracted.json
```

### Example 2: Test with Regex Extraction (Faster)
```bash
# Extract using regex patterns (faster but less robust)
python test_real_file.py path/to/report.pdf --save
```

### Example 3: Get Raw OCR Text Only
```bash
# Extract raw text without structuring
python test_real_file.py report.pdf --format text
```

### Example 4: Test LLM Extraction Without OCR
```bash
# Test LLM extraction with sample text (useful for debugging)
python test_with_sample_text.py
```

### Example 5: Verify Environment Setup
```bash
# Check if API keys and dependencies are configured
python test_env.py
```
### Example 6: Use in Your Code
```python
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tools" / "src" / "document_data_extraction_tools"))

from lab_report_parser import extract_structured_lab_data

# Extract with LLM (recommended)
result = extract_structured_lab_data("path/to/report.pdf", use_llm=True)

# Or extract with regex (faster)
result = extract_structured_lab_data("path/to/report.pdf", use_llm=False)

# Access results
print(f"Status: {result['metadata']['extraction_status']}")
print(f"Method: {result['metadata']['extraction_method']}")
print(f"Tests found: {result['metadata']['total_tests_found']}")

for test in result['tests']:
    print(f"{test['test_name']}: {test['test_value']} {test['unit']} ({test['reference_range']})")
```

---

## 🔄 Extraction Pipeline

### Full Pipeline (PDF → JSON)

```
┌─────────────┐
│  PDF File   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  pdf2image      │  Convert PDF to images
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  PaddleOCR      │  Extract text from images
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Raw OCR Text   │  "Glucose: 95 mg/dL (70-100)..."
└──────┬──────────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ LLM Extract  │  │ Regex Extract│  │  Raw Text    │
│ (--llm flag) │  │  (default)   │  │ (--format    │
│              │  │              │  │   text)      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────┐
│         Structured JSON Output              │
│  {                                          │
│    "tests": [                               │
│      {                                      │
│        "test_name": "Glucose",              │
│        "test_value": "95",                  │
│        "unit": "mg/dL",                     │
│        "reference_range": "70-100"          │
│      }                                      │
│    ]                                        │
│  }                                          │
└─────────────────────────────────────────────┘
```

### Extraction Methods

**1. LLM Extraction (--llm flag)**
- Uses GPT-4o-mini via OpenAI API
- Most accurate and robust
- Handles varied formats and layouts
- Cost: ~$0.001 per report
- Requires: OPENAI_API_KEY in .env

**2. Regex Extraction (default)**
- Uses pattern matching
- Faster and free
- Less robust with varied formats
- Good for standardized reports

**3. Raw Text (--format text)**
- Returns OCR text only
- No structuring
- Useful for debugging OCR quality

---

## 📊 Output Format

The structured JSON output matches `lab_report_extraction.spec.json`:

```json
{
  "raw_text": "--- Page 1 ---\nmedall\nLABORATORY REPORT...",
  "tests": [
    {
      "test_name": "Haemoglobin",
      "test_value": "8.7",
      "unit": "g/dL",
      "reference_range": "13.5 - 18.0"
    },
    {
      "test_name": "Glucose",
      "test_value": "95",
      "unit": "mg/dL",
      "reference_range": "70-100"
    }
  ],
  "metadata": {
    "file_path": "../../test_data/sample_reports/lab_report1_page_1.pdf",
    "extraction_status": "success",
    "extraction_method": "llm",
    "model": "gpt-4o-mini",
    "total_tests_found": 12
  }
}
```

### Metadata Fields

- **extraction_status**: `success`, `no_tests_found`, `error`, `no_text`
- **extraction_method**: `llm`, `regex`, or `regex_fallback`
- **model**: LLM model used (only for LLM extraction)
- **total_tests_found**: Number of tests extracted
- **error_message**: Error details (only if status is `error`)

---

## ✅ Test Results

### Real PDF Test (lab_report1_page_1.pdf)

**Input:** Medical lab report PDF (1 page)

**Pipeline:**
1. ✅ PDF → Image conversion (2481x3508 pixels)
2. ✅ OCR extraction (1289 characters, 97 text regions)
3. ✅ LLM structuring (12 lab tests extracted)

**Extracted Tests:**
1. Haemoglobin: 8.7 g/dL (13.5 - 18.0)
2. PCV/Hematocrit: 25.6% (42 - 52)
3. RBC Count: 3.3 mill/cu.mm (4.7 - 6.0)
4. MCH: 26.7 pg (27 - 32)
5. Eosinophils: 0.1% (01 - 06)
6. Absolute Eosinophil Count: 0.04 10^3/L (0.04 - 0.44)
7. Platelet Count: 471 10^3/L (150 - 450)
8. MPV: 7.1 fL (7.9 - 13.7)
9. PCT: 0.33% (0.18 - 0.28)
10. ESR: 30 mm/hr (0 - 15)
11. GFR Study: 24.7 mL/min/1.7 sq.m (>= 90)
12. HbA1c: 6.4% (4.5 - 5.6)

**Performance:**
- OCR time: ~4 seconds
- LLM extraction: ~5 seconds
- Total: ~10 seconds
- Cost: ~$0.001

---

## ✅ Current Status

### Working Features
- ✅ PDF to image conversion
- ✅ OCR text extraction with PaddleOCR
- ✅ LLM-based structured extraction (GPT-4o-mini)
- ✅ Regex-based extraction (fallback)
- ✅ File validation (PDF and image formats)
- ✅ Structured JSON output matching spec
- ✅ Raw text preservation even on errors
- ✅ Direct OpenAI API integration (avoids PyTorch DLL issues)

### Known Limitations

1. **OCR Quality Dependent**
   - Extraction quality depends on PDF/image quality
   - Low-resolution images may have poor OCR results
   - Recommendation: Use 300 DPI for best results

2. **LLM API Required**
   - LLM extraction requires OpenAI API key
   - Falls back to regex if API unavailable
   - Cost: ~$0.001 per report (very affordable)

3. **First Run Slower**
   - PaddleOCR downloads models on first run (~100MB)
   - Subsequent runs are much faster

---

## 🔧 Troubleshooting

### Issue 1: No API Key Error

**Error:**
```
openai.OpenAIError: The api_key client option must be set
```

**Solution:**
1. Create `.env` file in `agentic-medical-health-review/` directory
2. Add: `OPENAI_API_KEY=your-key-here`
3. Get key from: https://platform.openai.com/api-keys

### Issue 2: No Text Extracted

**Symptoms:**
```
Raw text length: 0 characters
Tests found: 0
```

**Solutions:**
1. Check PDF quality - try with a clear, high-resolution PDF
2. Verify Poppler is installed: `where pdftoppm` (Windows) or `which pdftoppm` (Linux/Mac)
3. Test with a simple image first
4. Check if PDF is encrypted or password-protected

### Issue 3: PaddleOCR Installation Issues

**Error:**
```
ModuleNotFoundError: No module named 'paddle'
```

**Solution:**
```bash
pip install paddlepaddle paddleocr
```

### Issue 4: Poppler Not Found

**Error:**
```
PDFInfoNotInstalledError: Unable to get page count. Is poppler installed and in PATH?
```

**Solution:**
- **Windows:** Download from https://github.com/oschwartz10612/poppler-windows/releases/
  - Extract and add `bin` folder to PATH
- **Linux:** `sudo apt-get install poppler-utils`
- **Mac:** `brew install poppler`

### Quick Environment Check

```bash
# Verify all dependencies
python test_env.py
```

This will check:
- ✅ OpenAI API key configured
- ✅ PaddleOCR installed
- ✅ Poppler installed
- ✅ Python version compatible

---

## 🎯 Supported Formats

### Input Files
- PDF files (`.pdf`) - Single or multi-page
- Images (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.tif`)

### Text Patterns Recognized

The LLM extraction handles various formats automatically. Regex extraction recognizes:

**Pattern 1:** `Test Name: Value Unit (Range)`
```
Glucose: 95 mg/dL (70-100)
```

**Pattern 2:** `Test Name Value Unit Range`
```
Glucose 95 mg/dL 70-100
```

**Pattern 3:** `Test Name | Value | Unit | Range` (table format)
```
Glucose | 95 | mg/dL | 70-100
```

---

## 📞 Support

If you encounter issues:

1. ✅ Run `python test_env.py` to verify setup
2. ✅ Check `.env` file has OPENAI_API_KEY
3. ✅ Test with `test_with_sample_text.py` to isolate LLM issues
4. ✅ Test with a simple, clear image first
5. ✅ Share full error traceback and environment details

---

## 🔗 Related Files

- **Source Code:**
  - `../../../tools/src/document_data_extraction_tools/lab_report_parser.py` - Main parser
  - `../../../tools/src/document_data_extraction_tools/llm_structured_extractor.py` - LLM extraction
  - `../../../tools/src/document_data_extraction_tools/file_validator.py` - File validation
- **Configuration:**
  - `../../../.env` - API keys and configuration
  - `../../../prompts/tool_medical_report_extraction_prompt.md` - LLM prompts
- **Test Data:**
  - `../../test_data/sample_reports/lab_report1_page_1.pdf` - Sample PDF for testing
