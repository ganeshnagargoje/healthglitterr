"""
Tests for Lab Data Normalization Tool

Tests the normalize_lab_data_tool functionality including:
- Parameter name normalization
- Unit conversion
- Reference range alignment
- Error handling
- Batch processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

import pytest
from tools.src.document_data_extraction_tools.normlize_lab_data.normalize_lab_data import normalize_lab_data, normalize_batch
import uuid


class TestNormalizeLabData:
    """Test suite for normalize_lab_data function"""
    
    def test_successful_glucose_normalization(self):
        """Test successful normalization of glucose from mg/dL to mmol/L"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Blood Glucose",
            value=117.0,
            unit="mg/dL"
        )
        
        assert result['success'] == True
        assert result['normalized_parameter'] is not None
        assert result['normalized_parameter']['canonical_name'] == 'glucose_fasting'
        assert result['normalized_parameter']['standard_unit'] == 'mmol/L'
        assert abs(result['normalized_parameter']['normalized_value'] - 6.4935) < 0.01
        assert result['operations_logged'] == 3  # name_mapping, unit_conversion, range_alignment
    
    def test_successful_hba1c_normalization(self):
        """Test successful normalization of HbA1c (already in standard unit)"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="HbA1c",
            value=6.5,
            unit="%"
        )
        
        assert result['success'] == True
        assert result['normalized_parameter']['canonical_name'] == 'hemoglobin_a1c'
        assert result['normalized_parameter']['standard_unit'] == '%'
        assert result['normalized_parameter']['normalized_value'] == 6.5
        assert result['normalized_parameter']['conversion_factor'] == 1.0
    
    def test_unknown_parameter_name(self):
        """Test handling of unknown parameter name"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Unknown Test Parameter",
            value=100.0,
            unit="mg/dL"
        )
        
        assert result['success'] == False
        assert result['flagged_for_review'] == True
        assert len(result['errors']) > 0
        assert 'Could not map parameter name' in result['errors'][0]
    
    def test_unknown_unit(self):
        """Test handling of unknown unit"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Blood Glucose",
            value=100.0,
            unit="unknown_unit"
        )
        
        assert result['success'] == False
        assert result['flagged_for_review'] == True
        assert len(result['errors']) > 0
        assert 'Could not convert unit' in result['errors'][0]
    
    def test_missing_unit(self):
        """Test handling of missing unit (should flag but may succeed)"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Blood Glucose",
            value=100.0,
            unit=None
        )
        
        # Should be flagged for review due to missing unit
        assert result['flagged_for_review'] == True or result['success'] == False
    
    def test_cholesterol_conversion(self):
        """Test cholesterol conversion from mg/dL to mmol/L"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Total Cholesterol",
            value=200.0,
            unit="mg/dL"
        )
        
        assert result['success'] == True
        assert result['normalized_parameter']['canonical_name'] == 'cholesterol_total'
        assert result['normalized_parameter']['standard_unit'] == 'mmol/L'
        assert abs(result['normalized_parameter']['normalized_value'] - 5.18) < 0.01
    
    def test_confidence_scoring(self):
        """Test that confidence scores are calculated correctly"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Blood Glucose",
            value=117.0,
            unit="mg/dL"
        )
        
        assert result['success'] == True
        confidence = result['normalized_parameter']['normalization_confidence']
        assert 0.0 <= confidence <= 1.0
        
        # High confidence parameters should not be flagged
        if confidence >= 0.7:
            assert result['flagged_for_review'] == False
    
    def test_low_confidence_flagging(self):
        """Test that low confidence results are flagged for review"""
        # Use a parameter name with lower confidence score
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Glucose",  # Lower confidence mapping
            value=100.0,
            unit="mg/dL"
        )
        
        if result['success']:
            confidence = result['normalized_parameter']['normalization_confidence']
            if confidence < 0.7:
                assert result['flagged_for_review'] == True
                assert any('Low confidence' in w for w in result['warnings'])


class TestNormalizeBatch:
    """Test suite for normalize_batch function"""
    
    def test_batch_normalization_success(self):
        """Test batch normalization with multiple parameters"""
        parameters = [
            {
                "parameter_id": str(uuid.uuid4()),
                "user_id": "TEST-USER-001",
                "parameter_name": "Blood Glucose",
                "value": 117.0,
                "unit": "mg/dL"
            },
            {
                "parameter_id": str(uuid.uuid4()),
                "user_id": "TEST-USER-001",
                "parameter_name": "HbA1c",
                "value": 6.5,
                "unit": "%"
            },
            {
                "parameter_id": str(uuid.uuid4()),
                "user_id": "TEST-USER-001",
                "parameter_name": "Total Cholesterol",
                "value": 200.0,
                "unit": "mg/dL"
            }
        ]
        
        batch_result = normalize_batch(parameters)
        
        assert batch_result['total'] == 3
        assert batch_result['successful'] >= 0
        assert batch_result['failed'] >= 0
        assert batch_result['successful'] + batch_result['failed'] == 3
        assert len(batch_result['results']) == 3
    
    def test_batch_with_mixed_results(self):
        """Test batch normalization with both successful and failed items"""
        parameters = [
            {
                "parameter_id": str(uuid.uuid4()),
                "user_id": "TEST-USER-001",
                "parameter_name": "Blood Glucose",
                "value": 117.0,
                "unit": "mg/dL"
            },
            {
                "parameter_id": str(uuid.uuid4()),
                "user_id": "TEST-USER-001",
                "parameter_name": "Unknown Parameter",
                "value": 100.0,
                "unit": "mg/dL"
            }
        ]
        
        batch_result = normalize_batch(parameters)
        
        assert batch_result['total'] == 2
        assert batch_result['successful'] >= 1  # At least glucose should succeed
        assert batch_result['failed'] >= 1      # Unknown parameter should fail


class TestReferenceRanges:
    """Test suite for reference range alignment"""
    
    def test_reference_range_included(self):
        """Test that reference ranges are included in normalized output"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Blood Glucose",
            value=117.0,
            unit="mg/dL"
        )
        
        if result['success']:
            assert result['normalized_parameter']['reference_range_min'] is not None
            assert result['normalized_parameter']['reference_range_max'] is not None
            assert result['normalized_parameter']['reference_range_min'] < result['normalized_parameter']['reference_range_max']
    
    def test_missing_reference_range_warning(self):
        """Test that missing reference ranges generate warnings"""
        # This test assumes there might be parameters without reference ranges
        # Adjust based on your sample data
        pass


class TestAuditLogging:
    """Test suite for audit logging functionality"""
    
    def test_operations_logged_count(self):
        """Test that all operations are logged"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Blood Glucose",
            value=117.0,
            unit="mg/dL"
        )
        
        # Should log: name_mapping, unit_conversion, range_alignment
        assert result['operations_logged'] >= 3
    
    def test_failed_operations_logged(self):
        """Test that failed operations are also logged"""
        result = normalize_lab_data(
            parameter_id=str(uuid.uuid4()),
            user_id="TEST-USER-001",
            parameter_name="Unknown Parameter",
            value=100.0,
            unit="mg/dL"
        )
        
        # Even failed operations should be logged
        assert result['operations_logged'] >= 1


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
