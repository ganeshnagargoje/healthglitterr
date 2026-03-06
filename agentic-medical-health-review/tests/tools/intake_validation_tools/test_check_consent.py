"""
Test suite for the Consent Validation Tool.
"""

import pytest
from tools.src.intake_validation_tools.check_consent import validate_consent

class TestCheckConsent:
    """Test cases for validate_consent function"""
    
    def test_consent_approved_variations(self):
        """Test variations of 'Yes' that should be approved"""
        variations = ["Yes", "YES", "yes", "YeS", " Yes ", "  YES  "]
        for val in variations:
            result = validate_consent(val)
            assert result['is_valid'] is True
            assert result['status'] == "Approved"
            assert result['error'] is None
            
    def test_consent_rejected(self):
        """Test variations of 'No' that should be rejected"""
        variations = ["No", "NO", "no", " nO ", "  no  "]
        for val in variations:
            result = validate_consent(val)
            assert result['is_valid'] is False
            assert result['status'] == "Rejected"
            assert "NOT given consent" in result['error']
            
    def test_consent_invalid_input(self):
        """Test invalid strings and types"""
        invalid_inputs = ["Maybe", "I don't know", "True", "1", ""]
        for val in invalid_inputs:
            result = validate_consent(val)
            assert result['is_valid'] is False
            assert "must be 'Yes' or 'No'" in result['error']
            
    def test_consent_missing(self):
        """Test None as input"""
        result = validate_consent(None)
        assert result['is_valid'] is False
        assert "required" in result['error']
