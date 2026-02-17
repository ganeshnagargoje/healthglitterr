# Installation Guide

This guide will help you set up the development environment for the Medical Health Review system.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment tool (venv)

## Installation Steps

### 1. Create Virtual Environment

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv .venv
.venv\Scripts\activate.bat

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**IMPORTANT**: The installation may show some dependency conflict warnings. These are expected and can be safely ignored:

```
WARNING: paddleocr 2.7.0.3 requires PyMuPDF<1.21.0, but you have pymupdf 1.27.1
```

This conflict does NOT affect functionality because we use `pdf2image` for PDF processing, not PyMuPDF.

### 3. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

### 4. Verify Installation

Run the end-to-end test to verify everything is working:

```bash
cd agentic-medical-health-review/tests/tools/document_data_extraction_tools
python test_real_file.py
```

Expected output:
- OCR extraction of text from PDF
- Structured JSON output with lab test results
- Success message

## Critical Version Requirements

### NumPy Version
- **MUST use numpy==1.26.4**
- NumPy 2.x has breaking ABI changes incompatible with OpenCV and PaddlePaddle
- Do NOT upgrade to NumPy 2.x

### OpenCV Version
- **MUST use opencv-python==4.6.0.66**
- PaddleOCR requires OpenCV <=4.6.0.66
- Do NOT install opencv-python-headless (requires NumPy 2.x)

### PaddleOCR and PaddlePaddle
- **MUST use paddleocr==2.7.0.3 and paddlepaddle==2.6.2**
- These versions are tested and working together
- Newer versions may have compatibility issues

## Troubleshooting

### Issue: NumPy ABI Error
```
RuntimeError: module compiled against ABI version 0x1000009 but this version of numpy is 0x2000000
```

**Solution**: Downgrade NumPy to 1.26.4
```bash
pip install numpy==1.26.4
```

### Issue: OpenCV Import Error
```
ImportError: numpy.core.multiarray failed to import
```

**Solution**: Ensure you have the correct OpenCV and NumPy versions
```bash
pip install opencv-python==4.6.0.66 opencv-contrib-python==4.6.0.66 numpy==1.26.4
```

### Issue: PaddlePaddle PIR Error
```
Error: PIR mode is not supported
```

**Solution**: This is already handled in the code with:
```python
os.environ['PADDLE_PIR_ENABLED'] = '0'
```

### Issue: Missing PaddleOCR Dependencies

If you see errors about missing dependencies (attrdict, beautifulsoup4, etc.), they should be installed automatically from requirements.txt. If not, install them manually:

```bash
pip install attrdict beautifulsoup4 cython fire imgaug lxml openpyxl pdf2docx premailer python-docx scikit-image
```

## System Requirements

### Windows
- Tested on Windows 10/11
- PowerShell or CMD
- No Visual Studio required (using pre-built wheels)

### Linux/Mac
- Should work with standard Python installation
- May need additional system libraries for pdf2image (poppler-utils)

## Additional Notes

- The system uses GPT-4o-mini for LLM extraction (~$0.001 per report)
- PaddleOCR runs locally and does not require internet connection
- First run may download PaddleOCR models (~100MB)
