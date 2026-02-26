"""
Pytest configuration and fixtures for document data extraction tools tests
"""

import pytest
from pathlib import Path


@pytest.fixture
def pdf_path():
    """
    Fixture providing the path to a sample PDF for testing
    """
    # Path relative to the test file location
    test_dir = Path(__file__).parent
    sample_pdf = test_dir / "../../test_data/sample_reports/lab_report1_page_1.pdf"
    
    # Resolve to absolute path
    pdf_file = sample_pdf.resolve()
    
    if not pdf_file.exists():
        pytest.skip(f"Sample PDF not found at {pdf_file}")
    
    return str(pdf_file)


@pytest.fixture
def file_path(pdf_path):
    """
    Alias fixture for file_path (used by test_real_file.py)
    """
    return pdf_path


@pytest.fixture
def sample_reports_dir():
    """
    Fixture providing the path to the sample reports directory
    """
    test_dir = Path(__file__).parent
    reports_dir = test_dir / "../../test_data/sample_reports"
    
    reports_path = reports_dir.resolve()
    
    if not reports_path.exists():
        pytest.skip(f"Sample reports directory not found at {reports_path}")
    
    return str(reports_path)
