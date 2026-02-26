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
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tools" / "src" / "document_data_extraction_tools" / "normalize_lab_data"))

import pytest
from normalize_lab_data import normalize_lab_data, normalize_batch
import uuid
from models.database_connection import DatabaseConnection


@pytest.fixture(scope="module")
def test_user_id():
    """Create a test user and return the user_id"""
    with DatabaseConnection() as db:
        user_id = str(uuid.uuid4())
        db.cursor.execute("""
            INSERT INTO users (user_id, email, role, consent_status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET user_id = EXCLUDED.user_id
            RETURNING user_id
        """, (user_id, f'test_{user_id}@example.com', 'patient', True))
        result = db.cursor.fetchone()
        return result['user_id'] if result else user_id


@pytest.fixture
def create_health_parameter(test_user_id):
    """Factory fixture to create health parameters in the database"""
    created_params = []
    
    def _create_parameter(parameter_name, value, unit):
        with DatabaseConnection() as db:
            parameter_id = str(uuid.uuid4())
            db.cursor.execute("""
                INSERT INTO health_parameters (
                    parameter_id, user_id, parameter_name, value, unit,
                    timestamp, source, normalization_status
                ) VALUES (%s, %s, %s, %s, %s, NOW(), 'report', 'pending')
                RETURNING parameter_id
            """, (parameter_id, test_user_id, parameter_name, value, unit))
            created_params.append(parameter_id)
            return parameter_id
    
    yield _create_parameter
    
    # Cleanup after tests
    with DatabaseConnection() as db:
        for param_id in created_params:
            # Delete in correct order due to foreign key constraints
            db.cursor.execute("DELETE FROM normalized_parameters WHERE original_parameter_id = %s", (param_id,))
            db.cursor.execute("DELETE FROM normalization_audit_logs WHERE parameter_id = %s", (param_id,))
            db.cursor.execute("DELETE FROM health_parameters WHERE parameter_id = %s", (param_id,))


class TestNormalizeLabData:
    """Test suite for normalize_lab_data function"""
    
    def test_successful_glucose_normalization(self, test_user_id, create_health_parameter):
        """Test successful normalization of glucose from mg/dL to mmol/L"""
        parameter_id = create_health_parameter("Blood Glucose", 117.0, "mg/dL")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
            parameter_name="Blood Glucose",
            value=117.0,
            unit="mg/dL"
        )
        
        assert result['success'] == True
        assert result['normalized_parameter'] is not None
        assert result['normalized_parameter']['canonical_name'] == 'glucose_fasting'
        assert result['normalized_parameter']['standard_unit'] == 'mmol/L'
        assert abs(result['normalized_parameter']['normalized_value'] - 6.4935) < 0.01
        assert result['operations_logged'] >= 3  # name_mapping, unit_conversion, range_alignment
    
    def test_successful_hba1c_normalization(self, test_user_id, create_health_parameter):
        """Test successful normalization of HbA1c (already in standard unit)"""
        parameter_id = create_health_parameter("HbA1c", 6.5, "%")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
            parameter_name="HbA1c",
            value=6.5,
            unit="%"
        )
        
        assert result['success'] == True
        assert result['normalized_parameter']['canonical_name'] == 'hemoglobin_a1c'
        assert result['normalized_parameter']['standard_unit'] == '%'
        assert result['normalized_parameter']['normalized_value'] == 6.5
        assert result['normalized_parameter']['conversion_factor'] == 1.0
    
    def test_unknown_parameter_name(self, test_user_id, create_health_parameter):
        """Test handling of unknown parameter name"""
        parameter_id = create_health_parameter("Unknown Test Parameter", 100.0, "mg/dL")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
            parameter_name="Unknown Test Parameter",
            value=100.0,
            unit="mg/dL"
        )
        
        assert result['success'] == False
        assert result['flagged_for_review'] == True
        assert len(result['errors']) > 0
        assert 'Could not map parameter name' in result['errors'][0]
    
    def test_unknown_unit(self, test_user_id, create_health_parameter):
        """Test handling of unknown unit"""
        parameter_id = create_health_parameter("Blood Glucose", 100.0, "unknown_unit")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
            parameter_name="Blood Glucose",
            value=100.0,
            unit="unknown_unit"
        )
        
        assert result['success'] == False
        assert result['flagged_for_review'] == True
        assert len(result['errors']) > 0
        assert 'Could not convert unit' in result['errors'][0]
    
    def test_missing_unit(self, test_user_id, create_health_parameter):
        """Test handling of missing unit (should flag but may succeed)"""
        parameter_id = create_health_parameter("Blood Glucose", 100.0, None)
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
            parameter_name="Blood Glucose",
            value=100.0,
            unit=None
        )
        
        # Should be flagged for review due to missing unit
        assert result['flagged_for_review'] == True or result['success'] == False
    
    def test_cholesterol_conversion(self, test_user_id, create_health_parameter):
        """Test cholesterol conversion from mg/dL to mmol/L"""
        parameter_id = create_health_parameter("Total Cholesterol", 200.0, "mg/dL")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
            parameter_name="Total Cholesterol",
            value=200.0,
            unit="mg/dL"
        )
        
        assert result['success'] == True
        assert result['normalized_parameter']['canonical_name'] == 'cholesterol_total'
        assert result['normalized_parameter']['standard_unit'] == 'mmol/L'
        assert abs(result['normalized_parameter']['normalized_value'] - 5.18) < 0.01
    
    def test_confidence_scoring(self, test_user_id, create_health_parameter):
        """Test that confidence scores are calculated correctly"""
        parameter_id = create_health_parameter("Blood Glucose", 117.0, "mg/dL")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
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
    
    def test_low_confidence_flagging(self, test_user_id, create_health_parameter):
        """Test that low confidence results are flagged for review"""
        parameter_id = create_health_parameter("Glucose", 100.0, "mg/dL")
        
        # Use a parameter name with lower confidence score
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
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
    
    def test_batch_normalization_success(self, test_user_id, create_health_parameter):
        """Test batch normalization with multiple parameters"""
        param1_id = create_health_parameter("Blood Glucose", 117.0, "mg/dL")
        param2_id = create_health_parameter("HbA1c", 6.5, "%")
        param3_id = create_health_parameter("Total Cholesterol", 200.0, "mg/dL")
        
        parameters = [
            {
                "parameter_id": param1_id,
                "user_id": test_user_id,
                "parameter_name": "Blood Glucose",
                "value": 117.0,
                "unit": "mg/dL"
            },
            {
                "parameter_id": param2_id,
                "user_id": test_user_id,
                "parameter_name": "HbA1c",
                "value": 6.5,
                "unit": "%"
            },
            {
                "parameter_id": param3_id,
                "user_id": test_user_id,
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
    
    def test_batch_with_mixed_results(self, test_user_id, create_health_parameter):
        """Test batch normalization with both successful and failed items"""
        param1_id = create_health_parameter("Blood Glucose", 117.0, "mg/dL")
        param2_id = create_health_parameter("Unknown Parameter", 100.0, "mg/dL")
        
        parameters = [
            {
                "parameter_id": param1_id,
                "user_id": test_user_id,
                "parameter_name": "Blood Glucose",
                "value": 117.0,
                "unit": "mg/dL"
            },
            {
                "parameter_id": param2_id,
                "user_id": test_user_id,
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
    
    def test_reference_range_included(self, test_user_id, create_health_parameter):
        """Test that reference ranges are included in normalized output"""
        parameter_id = create_health_parameter("Blood Glucose", 117.0, "mg/dL")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
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
    
    def test_operations_logged_count(self, test_user_id, create_health_parameter):
        """Test that all operations are logged"""
        parameter_id = create_health_parameter("Blood Glucose", 117.0, "mg/dL")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
            parameter_name="Blood Glucose",
            value=117.0,
            unit="mg/dL"
        )
        
        # Should log: name_mapping, unit_conversion, range_alignment
        assert result['operations_logged'] >= 3
    
    def test_failed_operations_logged(self, test_user_id, create_health_parameter):
        """Test that failed operations are also logged"""
        parameter_id = create_health_parameter("Unknown Parameter", 100.0, "mg/dL")
        
        result = normalize_lab_data(
            parameter_id=parameter_id,
            user_id=test_user_id,
            parameter_name="Unknown Parameter",
            value=100.0,
            unit="mg/dL"
        )
        
        # Even failed operations should be logged
        assert result['operations_logged'] >= 1


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
