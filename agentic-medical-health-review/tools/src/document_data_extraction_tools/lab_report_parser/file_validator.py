"""
PaddleOCR Text Extraction Tool

This module provides text extraction functionality from medical documents
in PDF and image formats using PaddleOCR.
"""

import os
from typing import Tuple


class FileValidator:
    """Validates file existence and format support for OCR processing."""
    
    SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
    SUPPORTED_PDF_EXTENSIONS = {'.pdf'}
    
    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate if a file exists and is accessible.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if file exists, False otherwise
            - error_message: Empty string if valid, error description if invalid
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        return True, ""
    
    @staticmethod
    def get_file_type(file_path: str) -> str:
        """
        Identify file type based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            "pdf" for PDF files
            "image" for supported image formats
            "unsupported" for unsupported formats
        """
        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()
        
        if ext_lower in FileValidator.SUPPORTED_PDF_EXTENSIONS:
            return "pdf"
        elif ext_lower in FileValidator.SUPPORTED_IMAGE_EXTENSIONS:
            return "image"
        else:
            return "unsupported"
