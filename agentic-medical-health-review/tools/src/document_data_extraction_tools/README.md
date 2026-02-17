# Document Data Extraction Tools

OCR-based text extraction from medical lab reports in PDF and image formats.

## Components

### 1. FileValidator
Validates file existence and format support before processing.

**Supported Formats:**
- PDF: `.pdf`
- Images: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.tif`

**Methods:**
- `validate_file(file_path)` - Check if file exists
- `get_file_type(file_path)` - Identify file type (pdf/image/unsupported)

### 2. LabReportParser
Singleton wrapper around PaddleOCR for text extraction with spatial ordering.

**Features:**
- Lazy initialization of OCR engine
- PDF multi-page support
- Image format support
- Preserves spatial text ordering (top-to-bottom, left-to-right)
- Automatic line grouping

**Methods:**
- `get_instance()` - Get singleton instance
- `extract_text_from_file(file_path)` - Extract from PDF or image file
- `extract_text(image)` - Extract from PIL Image or numpy array

## Installation

```bash
# Install required packages
pip install paddleocr pillow pdf2image

# For PDF support on Windows, install poppler
pip install poppler-utils
```

## Usage Examples

### Basic Usage

```python
from lab_report_parser import extract_text_from_lab_report

# Extract from PDF
text = extract_text_from_lab_report("lab_report.pdf")
print(text)

# Extract from image
text = extract_text_from_lab_report("lab_report.jpg")
print(text)
```

### Using Singleton Instance

```python
from lab_report_parser import LabReportParser

parser = LabReportParser.get_instance()
text = parser.extract_text_from_file("report.pdf")
```

### With File Validation

```python
from file_validator import FileValidator
from lab_report_parser import LabReportParser

# Validate first
is_valid, error = FileValidator.validate_file("report.pdf")
if is_valid:
    file_type = FileValidator.get_file_type("report.pdf")
    print(f"File type: {file_type}")
    
    # Extract text
    parser = LabReportParser.get_instance()
    text = parser.extract_text_from_file("report.pdf")
else:
    print(f"Error: {error}")
```

### Batch Processing

```python
from lab_report_parser import LabReportParser

files = ["report1.pdf", "report2.jpg", "report3.png"]
parser = LabReportParser.get_instance()

for file_path in files:
    try:
        text = parser.extract_text_from_file(file_path)
        print(f"Processed {file_path}: {len(text)} chars")
    except Exception as e:
        print(f"Failed {file_path}: {e}")
```

### Extract from PIL Image

```python
from PIL import Image
from lab_report_parser import LabReportParser

image = Image.open("report.jpg")
parser = LabReportParser.get_instance()
text = parser.extract_text(image)
```

## Error Handling

The parser raises specific exceptions:

- `FileNotFoundError` - File doesn't exist
- `ValueError` - Unsupported file format
- `ImportError` - Missing pdf2image for PDF processing

```python
try:
    text = extract_text_from_lab_report("report.pdf")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Unsupported format: {e}")
except ImportError as e:
    print(f"Missing dependency: {e}")
```

## Configuration

The OCR engine is configured for medical documents:

- `use_textline_orientation=True` - Detect text orientation
- `lang='en'` - English language
- `device='cpu'` - CPU processing
- `enable_mkldnn=False` - Compatibility mode
- `text_det_thresh=0.3` - Detection threshold
- `text_det_box_thresh=0.5` - Box threshold

## Testing

Run the integration test:

```bash
cd agentic-medical-health-review/tests/tools/document_data_extraction_tools
python test_integration.py
```

Run the usage examples:

```bash
cd agentic-medical-health-review/tests/tools/document_data_extraction_tools
python example_usage.py
```

## Architecture

```
FileValidator (validates file)
       ↓
LabReportParser (extracts text)
       ↓
PaddleOCR (OCR engine)
```

## Notes

- The parser uses a singleton pattern for efficient resource usage
- OCR engine is lazily initialized on first use
- PDF files are converted to images page-by-page
- Text regions are spatially ordered for natural reading flow
- Multi-page PDFs include page markers in output
