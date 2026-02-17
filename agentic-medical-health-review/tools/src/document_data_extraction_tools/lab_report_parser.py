"""
Lab Report Parser

Provides OCR text extraction from medical lab reports in PDF or image format.
"""

import os
import numpy as np
from PIL import Image

# Disable PIR to avoid PaddlePaddle compatibility issues
os.environ['PADDLE_PIR_ENABLED'] = '0'

from paddleocr import PaddleOCR

# Handle both relative and absolute imports
try:
    from .file_validator import FileValidator
except ImportError:
    from file_validator import FileValidator


class LabReportParser:
    """Singleton wrapper around PaddleOCR with lazy initialization."""
    
    _instance = None
    
    def __init__(self):
        """Private constructor - use get_instance() instead."""
        self._ocr = None
        self._initialized = False
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of OCREngine.
        
        Returns:
            OCREngine: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _initialize_engine(self):
        """
        Initialize the PaddleOCR engine with minimal configuration.
        Only initializes once per instance.
        """
        if not self._initialized:
            # Use absolute minimal configuration - only lang parameter
            self._ocr = PaddleOCR(lang='en')
            self._initialized = True
    
    def extract_text_from_file(self, file_path):
        """
        Extract text from a PDF or image file.
        
        Args:
            file_path: Path to PDF or image file (str or Path)
            
        Returns:
            str: Extracted text from all pages/images
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        file_path_str = str(file_path)
        
        # Validate file existence using FileValidator
        is_valid, error_msg = FileValidator.validate_file(file_path_str)
        if not is_valid:
            raise FileNotFoundError(error_msg)
        
        # Determine file type using FileValidator
        file_type = FileValidator.get_file_type(file_path_str)
        
        if file_type == "pdf":
            return self._extract_from_pdf(file_path_str)
        elif file_type == "image":
            return self._extract_from_image(file_path_str)
        else:
            raise ValueError(f"Unsupported file format: {file_path_str}")
    
    def _extract_from_pdf(self, pdf_path):
        """
        Extract text from all pages of a PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            str: Extracted text from all pages
        """
        try:
            import pdf2image
        except ImportError:
            raise ImportError(
                "pdf2image is required for PDF processing. "
                "Install with: pip install pdf2image"
            )
        
        try:
            # Convert PDF pages to images with higher DPI for better OCR
            print(f"🔄 Converting PDF to images...")
            print(f"   File: {pdf_path}")
            
            images = pdf2image.convert_from_path(
                pdf_path, 
                dpi=300,  # High DPI for better text recognition
                fmt='png'  # PNG format for better quality
            )
            
            print(f"✓ Converted {len(images)} page(s)")
            
            if not images:
                print("⚠ Warning: No pages found in PDF")
                return ""
            
            # Extract text from each page
            all_text = []
            for page_num, image in enumerate(images, 1):
                print(f"📄 Processing page {page_num}/{len(images)}...")
                print(f"   Image size: {image.size[0]}x{image.size[1]} pixels")
                
                # Extract text from this page
                text = self.extract_text(image)
                
                print(f"   Extracted: {len(text)} characters")
                
                if text.strip():
                    all_text.append(f"--- Page {page_num} ---\n{text}")
                else:
                    print(f"   ⚠ No text found on page {page_num}")
            
            result = "\n\n".join(all_text)
            print(f"✓ Total extracted: {len(result)} characters from {len(all_text)} page(s)")
            
            if not result.strip():
                print("\n⚠ WARNING: No text was extracted from any page")
                print("   Possible reasons:")
                print("   - PDF contains only images without text")
                print("   - Text is too small or low quality")
                print("   - PDF is encrypted or protected")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error during PDF processing: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    def _extract_from_image(self, image_path):
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            str: Extracted text
        """
        image = Image.open(image_path)
        return self.extract_text(image)
    
    def extract_text(self, image):
        """
        Extract text from a single image.
        
        Args:
            image: PIL.Image object or numpy array
            
        Returns:
            str: Extracted text with preserved spatial ordering
        """
        # Ensure engine is initialized
        if not self._initialized:
            print("   Initializing OCR engine (first time only)...")
            self._initialize_engine()
            print("   ✓ OCR engine ready")
        
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Run OCR - remove cls parameter as it's not supported in newer versions
        print(f"   Running OCR on image shape: {image.shape}")
        results = self._ocr.ocr(image)
        
        # Handle empty results
        if not results or not results[0]:
            print("   ⚠ OCR returned no results")
            return ""
        
        # Get the first result (for single image)
        result = results[0]
        
        # Check if we have text regions
        if not result:
            print("   ⚠ No text regions found")
            return ""
        
        print(f"   Found {len(result)} text regions")
        
        # Extract and organize text regions
        # Format: [[bbox, (text, confidence)], ...]
        text_regions = []
        for item in result:
            if len(item) >= 2:
                bbox = item[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text_info = item[1]
                text = text_info[0] if isinstance(text_info, tuple) else text_info
                
                # Calculate positions
                y_coords = [bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]]
                y_pos = sum(y_coords) / len(y_coords)
                x_coords = [bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]]
                x_pos = sum(x_coords) / len(x_coords)
                
                text_regions.append((y_pos, x_pos, text))
        
        return self._organize_text_regions_simple(text_regions)
    
    def _organize_text_regions(self, ocr_text):
        """
        Organize OCR text regions by spatial position.
        
        Args:
            ocr_text: List of OCR results with bbox and text
            
        Returns:
            str: Organized text with proper line breaks
        """
        text_regions = []
        
        for item in ocr_text:
            bbox = item['bbox']  # [x1, y1, x2, y2, x3, y3, x4, y4]
            text = item['text']
            
            # Calculate vertical position (average y-coordinate)
            y_coords = [bbox[1], bbox[3], bbox[5], bbox[7]]
            y_pos = sum(y_coords) / len(y_coords)
            
            # Calculate horizontal position (average x-coordinate)
            x_coords = [bbox[0], bbox[2], bbox[4], bbox[6]]
            x_pos = sum(x_coords) / len(x_coords)
            
            text_regions.append((y_pos, x_pos, text))
        
        # Sort by vertical position (top to bottom), then horizontal (left to right)
        text_regions.sort(key=lambda region: (region[0], region[1]))
        
        # Group by lines and concatenate
        lines = []
        current_line = []
        current_y = None
        y_threshold = 10  # Pixels threshold for same line
        
        for y_pos, x_pos, text in text_regions:
            if current_y is None or abs(y_pos - current_y) < y_threshold:
                current_line.append(text)
                if current_y is None:
                    current_y = y_pos
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [text]
                current_y = y_pos
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def _organize_text_regions_simple(self, text_regions):
        """
        Organize text regions (simple version for tuple format).
        
        Args:
            text_regions: List of (y_pos, x_pos, text) tuples
            
        Returns:
            str: Organized text with proper line breaks
        """
        # Sort by vertical position (top to bottom), then horizontal (left to right)
        text_regions.sort(key=lambda region: (region[0], region[1]))
        
        # Group by lines and concatenate
        lines = []
        current_line = []
        current_y = None
        y_threshold = 10  # Pixels threshold for same line
        
        for y_pos, x_pos, text in text_regions:
            if current_y is None or abs(y_pos - current_y) < y_threshold:
                current_line.append(text)
                if current_y is None:
                    current_y = y_pos
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [text]
                current_y = y_pos
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)


# Convenience function for quick usage
def extract_text_from_lab_report(file_path):
    """
    Extract text from a lab report file (PDF or image).
    
    Args:
        file_path: Path to the lab report file
        
    Returns:
        str: Extracted text
    """
    parser = LabReportParser.get_instance()
    return parser.extract_text_from_file(file_path)


def extract_structured_lab_data(file_path, llm=None, model_name="gpt-4o-mini"):
    """
    Extract structured lab data from a lab report file using LLM.
    
    Args:
        file_path: Path to the lab report file
        llm: Optional pre-configured LLM instance (LangChain compatible)
        model_name: Model name to use if llm is not provided (default: gpt-4o-mini)
        
    Returns:
        dict: Structured lab data with format:
        {
            "raw_text": str,
            "tests": [
                {
                    "test_name": str,
                    "test_value": str,
                    "unit": str,
                    "reference_range": str
                }
            ],
            "metadata": {
                "file_path": str,
                "extraction_status": str,
                "total_tests_found": int,
                "extraction_method": "llm",
                "model": str
            }
        }
    """
    parser = LabReportParser.get_instance()
    raw_text = ""
    
    try:
        # Extract raw text using OCR
        raw_text = parser.extract_text_from_file(file_path)
        
        # Use LLM-based extraction
        try:
            from .llm_structured_extractor import extract_with_llm
        except ImportError:
            from llm_structured_extractor import extract_with_llm
        
        return extract_with_llm(raw_text, str(file_path), llm=llm, model_name=model_name)
        
    except Exception as e:
        # Preserve raw_text even if extraction fails
        return {
            "raw_text": raw_text,
            "tests": [],
            "metadata": {
                "file_path": str(file_path),
                "extraction_status": "error",
                "error_message": str(e),
                "total_tests_found": 0,
                "extraction_method": "llm"
            }
        }
