"""
Tests for Mismatch Detection Tool

Tests the mismatch_detection_tool functionality including:
- Detection of values above reference range
- Detection of values below reference range
- Detection of values within reference range
- Handling of missing reference ranges
- Severity classification
- Batch processing
- Edge cases
"""

import sys
import os
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tools" / "src" / "analysus_computation_tools"))

import pytest
from mismatch_detection import (
    detect_mismatch,
    detect_mismatches_batch,
    MismatchType,
    _calculate_severity
)
from models.normalized_parameter import NormalizedParameter


class TestDetectMismatch:
    """Test suite for detect_mismatch function"""
    
    def test_value_above_range(self):
        """Test detection of value above reference range"""
        param = NormalizedParameter(
            normalized_parameter_id="test-001",
            original_parameter_id="orig-001",
            user_id="USER-001",
            canonical_name="glucose_fasting",
            original_value=150.0,
            original_unit="mg/dL",
            normalized_value=8.3,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.ABOVE_RANGE
        assert result['deviation_percentage'] is not None
        assert result['deviation_percentage'] > 0
        assert result['severity'] in ['mild', 'moderate', 'severe']
        assert result['canonical_name'] == 'glucose_fasting'
    
    def test_value_below_range(self):
        """Test detection of value below reference range"""
        param = NormalizedParameter(
            normalized_parameter_id="test-002",
            original_parameter_id="orig-002",
            user_id="USER-002",
            canonical_name="glucose_fasting",
            original_value=60.0,
            original_unit="mg/dL",
            normalized_value=3.3,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.BELOW_RANGE
        assert result['deviation_percentage'] is not None
        assert result['deviation_percentage'] > 0
        assert result['severity'] in ['mild', 'moderate', 'severe']
    
    def test_value_within_range(self):
        """Test detection of value within reference range"""
        param = NormalizedParameter(
            normalized_parameter_id="test-003",
            original_parameter_id="orig-003",
            user_id="USER-003",
            canonical_name="glucose_fasting",
            original_value=90.0,
            original_unit="mg/dL",
            normalized_value=5.0,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == False
        assert result['mismatch_type'] == MismatchType.WITHIN_RANGE
        assert result['deviation_percentage'] is None
        assert result['severity'] == 'none'
    
    def test_value_at_lower_boundary(self):
        """Test value exactly at lower boundary (should be within range)"""
        param = NormalizedParameter(
            normalized_parameter_id="test-004",
            original_parameter_id="orig-004",
            user_id="USER-004",
            canonical_name="glucose_fasting",
            original_value=70.2,
            original_unit="mg/dL",
            normalized_value=3.9,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == False
        assert result['mismatch_type'] == MismatchType.WITHIN_RANGE
    
    def test_value_at_upper_boundary(self):
        """Test value exactly at upper boundary (should be within range)"""
        param = NormalizedParameter(
            normalized_parameter_id="test-005",
            original_parameter_id="orig-005",
            user_id="USER-005",
            canonical_name="glucose_fasting",
            original_value=109.9,
            original_unit="mg/dL",
            normalized_value=6.1,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == False
        assert result['mismatch_type'] == MismatchType.WITHIN_RANGE
    
    def test_no_reference_range(self):
        """Test handling of parameter without reference range"""
        param = NormalizedParameter(
            normalized_parameter_id="test-006",
            original_parameter_id="orig-006",
            user_id="USER-006",
            canonical_name="custom_parameter",
            original_value=100.0,
            original_unit="mg/dL",
            normalized_value=5.5,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=None,
            reference_range_max=None,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == False
        assert result['mismatch_type'] == MismatchType.NO_REFERENCE
        assert result['deviation_percentage'] is None
        assert result['severity'] == 'none'
    
    def test_only_min_reference_value_below(self):
        """Test with only minimum reference value, value below"""
        param = NormalizedParameter(
            normalized_parameter_id="test-007",
            original_parameter_id="orig-007",
            user_id="USER-007",
            canonical_name="hemoglobin",
            original_value=10.0,
            original_unit="g/dL",
            normalized_value=10.0,
            standard_unit="g/dL",
            conversion_factor=1.0,
            reference_range_min=12.0,
            reference_range_max=None,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.BELOW_RANGE
        assert result['deviation_percentage'] is not None
    
    def test_only_min_reference_value_above(self):
        """Test with only minimum reference value, value above"""
        param = NormalizedParameter(
            normalized_parameter_id="test-008",
            original_parameter_id="orig-008",
            user_id="USER-008",
            canonical_name="hemoglobin",
            original_value=14.0,
            original_unit="g/dL",
            normalized_value=14.0,
            standard_unit="g/dL",
            conversion_factor=1.0,
            reference_range_min=12.0,
            reference_range_max=None,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == False
        assert result['mismatch_type'] == MismatchType.WITHIN_RANGE
    
    def test_only_max_reference_value_above(self):
        """Test with only maximum reference value, value above"""
        param = NormalizedParameter(
            normalized_parameter_id="test-009",
            original_parameter_id="orig-009",
            user_id="USER-009",
            canonical_name="cholesterol_total",
            original_value=250.0,
            original_unit="mg/dL",
            normalized_value=6.5,
            standard_unit="mmol/L",
            conversion_factor=0.026,
            reference_range_min=None,
            reference_range_max=5.2,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.ABOVE_RANGE
        assert result['deviation_percentage'] is not None
    
    def test_only_max_reference_value_below(self):
        """Test with only maximum reference value, value below"""
        param = NormalizedParameter(
            normalized_parameter_id="test-010",
            original_parameter_id="orig-010",
            user_id="USER-010",
            canonical_name="cholesterol_total",
            original_value=150.0,
            original_unit="mg/dL",
            normalized_value=3.9,
            standard_unit="mmol/L",
            conversion_factor=0.026,
            reference_range_min=None,
            reference_range_max=5.2,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == False
        assert result['mismatch_type'] == MismatchType.WITHIN_RANGE


class TestSeverityCalculation:
    """Test suite for severity calculation"""
    
    def test_mild_severity(self):
        """Test mild severity (< 10% deviation)"""
        assert _calculate_severity(5.0) == "mild"
        assert _calculate_severity(9.9) == "mild"
        assert _calculate_severity(-5.0) == "mild"
        assert _calculate_severity(-9.9) == "mild"
    
    def test_moderate_severity(self):
        """Test moderate severity (10-25% deviation)"""
        assert _calculate_severity(10.0) == "moderate"
        assert _calculate_severity(15.0) == "moderate"
        assert _calculate_severity(24.9) == "moderate"
        assert _calculate_severity(-10.0) == "moderate"
        assert _calculate_severity(-24.9) == "moderate"
    
    def test_severe_severity(self):
        """Test severe severity (>= 25% deviation)"""
        assert _calculate_severity(25.0) == "severe"
        assert _calculate_severity(50.0) == "severe"
        assert _calculate_severity(100.0) == "severe"
        assert _calculate_severity(-25.0) == "severe"
        assert _calculate_severity(-100.0) == "severe"
    
    def test_zero_deviation(self):
        """Test zero deviation"""
        assert _calculate_severity(0.0) == "mild"


class TestDeviationPercentage:
    """Test suite for deviation percentage calculation"""
    
    def test_above_range_deviation(self):
        """Test deviation calculation for value above range"""
        param = NormalizedParameter(
            normalized_parameter_id="test-011",
            original_parameter_id="orig-011",
            user_id="USER-011",
            canonical_name="glucose_fasting",
            original_value=150.0,
            original_unit="mg/dL",
            normalized_value=7.5,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.0,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        # Deviation = ((7.5 - 6.0) / 6.0) * 100 = 25%
        assert result['deviation_percentage'] is not None
        assert abs(result['deviation_percentage'] - 25.0) < 0.1
    
    def test_below_range_deviation(self):
        """Test deviation calculation for value below range"""
        param = NormalizedParameter(
            normalized_parameter_id="test-012",
            original_parameter_id="orig-012",
            user_id="USER-012",
            canonical_name="glucose_fasting",
            original_value=60.0,
            original_unit="mg/dL",
            normalized_value=3.0,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=4.0,
            reference_range_max=6.0,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        # Deviation = ((4.0 - 3.0) / 4.0) * 100 = 25%
        assert result['deviation_percentage'] is not None
        assert abs(result['deviation_percentage'] - 25.0) < 0.1


class TestBatchDetection:
    """Test suite for batch mismatch detection"""
    
    def test_batch_all_within_range(self):
        """Test batch detection with all values within range"""
        params = [
            NormalizedParameter(
                normalized_parameter_id=f"test-{i}",
                original_parameter_id=f"orig-{i}",
                user_id=f"USER-{i}",
                canonical_name="glucose_fasting",
                original_value=90.0,
                original_unit="mg/dL",
                normalized_value=5.0,
                standard_unit="mmol/L",
                conversion_factor=0.0555,
                reference_range_min=3.9,
                reference_range_max=6.1,
                normalization_confidence=0.95
            )
            for i in range(3)
        ]
        
        result = detect_mismatches_batch(params)
        
        assert result['total'] == 3
        assert result['mismatches_found'] == 0
        assert result['within_range'] == 3
        assert result['no_reference'] == 0
        assert len(result['results']) == 3
    
    def test_batch_all_mismatches(self):
        """Test batch detection with all values outside range"""
        params = [
            NormalizedParameter(
                normalized_parameter_id=f"test-{i}",
                original_parameter_id=f"orig-{i}",
                user_id=f"USER-{i}",
                canonical_name="glucose_fasting",
                original_value=150.0,
                original_unit="mg/dL",
                normalized_value=8.3,
                standard_unit="mmol/L",
                conversion_factor=0.0555,
                reference_range_min=3.9,
                reference_range_max=6.1,
                normalization_confidence=0.95
            )
            for i in range(3)
        ]
        
        result = detect_mismatches_batch(params)
        
        assert result['total'] == 3
        assert result['mismatches_found'] == 3
        assert result['within_range'] == 0
        assert len(result['results']) == 3
    
    def test_batch_mixed_results(self):
        """Test batch detection with mixed results"""
        params = [
            # Within range
            NormalizedParameter(
                normalized_parameter_id="test-1",
                original_parameter_id="orig-1",
                user_id="USER-1",
                canonical_name="glucose_fasting",
                original_value=90.0,
                original_unit="mg/dL",
                normalized_value=5.0,
                standard_unit="mmol/L",
                conversion_factor=0.0555,
                reference_range_min=3.9,
                reference_range_max=6.1,
                normalization_confidence=0.95
            ),
            # Above range
            NormalizedParameter(
                normalized_parameter_id="test-2",
                original_parameter_id="orig-2",
                user_id="USER-2",
                canonical_name="glucose_fasting",
                original_value=150.0,
                original_unit="mg/dL",
                normalized_value=8.3,
                standard_unit="mmol/L",
                conversion_factor=0.0555,
                reference_range_min=3.9,
                reference_range_max=6.1,
                normalization_confidence=0.95
            ),
            # No reference
            NormalizedParameter(
                normalized_parameter_id="test-3",
                original_parameter_id="orig-3",
                user_id="USER-3",
                canonical_name="custom_param",
                original_value=100.0,
                original_unit="mg/dL",
                normalized_value=5.5,
                standard_unit="mmol/L",
                conversion_factor=0.0555,
                reference_range_min=None,
                reference_range_max=None,
                normalization_confidence=0.95
            )
        ]
        
        result = detect_mismatches_batch(params)
        
        assert result['total'] == 3
        assert result['mismatches_found'] == 1
        assert result['within_range'] == 1
        assert result['no_reference'] == 1
    
    def test_batch_empty_list(self):
        """Test batch detection with empty list"""
        result = detect_mismatches_batch([])
        
        assert result['total'] == 0
        assert result['mismatches_found'] == 0
        assert result['within_range'] == 0
        assert result['no_reference'] == 0
        assert len(result['results']) == 0


class TestEdgeCases:
    """Test suite for edge cases"""
    
    def test_very_high_value(self):
        """Test with extremely high value"""
        param = NormalizedParameter(
            normalized_parameter_id="test-edge-1",
            original_parameter_id="orig-edge-1",
            user_id="USER-EDGE-1",
            canonical_name="glucose_fasting",
            original_value=500.0,
            original_unit="mg/dL",
            normalized_value=27.75,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.ABOVE_RANGE
        assert result['severity'] == 'severe'
    
    def test_very_low_value(self):
        """Test with extremely low value"""
        param = NormalizedParameter(
            normalized_parameter_id="test-edge-2",
            original_parameter_id="orig-edge-2",
            user_id="USER-EDGE-2",
            canonical_name="glucose_fasting",
            original_value=20.0,
            original_unit="mg/dL",
            normalized_value=1.1,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.BELOW_RANGE
        assert result['severity'] == 'severe'
    
    def test_zero_value(self):
        """Test with zero value"""
        param = NormalizedParameter(
            normalized_parameter_id="test-edge-3",
            original_parameter_id="orig-edge-3",
            user_id="USER-EDGE-3",
            canonical_name="glucose_fasting",
            original_value=0.0,
            original_unit="mg/dL",
            normalized_value=0.0,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.BELOW_RANGE
    
    def test_negative_value(self):
        """Test with negative value (should be below range)"""
        param = NormalizedParameter(
            normalized_parameter_id="test-edge-4",
            original_parameter_id="orig-edge-4",
            user_id="USER-EDGE-4",
            canonical_name="glucose_fasting",
            original_value=-5.0,
            original_unit="mg/dL",
            normalized_value=-0.28,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.1,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.BELOW_RANGE


class TestRealWorldScenarios:
    """Test suite for real-world medical scenarios"""
    
    def test_prediabetic_glucose(self):
        """Test glucose level in prediabetic range"""
        param = NormalizedParameter(
            normalized_parameter_id="test-real-1",
            original_parameter_id="orig-real-1",
            user_id="USER-REAL-1",
            canonical_name="glucose_fasting",
            original_value=110.0,
            original_unit="mg/dL",
            normalized_value=6.1,
            standard_unit="mmol/L",
            conversion_factor=0.0555,
            reference_range_min=3.9,
            reference_range_max=6.0,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.ABOVE_RANGE
        assert result['severity'] == 'mild'
    
    def test_high_cholesterol(self):
        """Test high cholesterol level"""
        param = NormalizedParameter(
            normalized_parameter_id="test-real-2",
            original_parameter_id="orig-real-2",
            user_id="USER-REAL-2",
            canonical_name="cholesterol_total",
            original_value=240.0,
            original_unit="mg/dL",
            normalized_value=6.2,
            standard_unit="mmol/L",
            conversion_factor=0.026,
            reference_range_min=0.0,
            reference_range_max=5.2,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.ABOVE_RANGE
    
    def test_low_hemoglobin_anemia(self):
        """Test low hemoglobin indicating possible anemia"""
        param = NormalizedParameter(
            normalized_parameter_id="test-real-3",
            original_parameter_id="orig-real-3",
            user_id="USER-REAL-3",
            canonical_name="hemoglobin",
            original_value=10.5,
            original_unit="g/dL",
            normalized_value=10.5,
            standard_unit="g/dL",
            conversion_factor=1.0,
            reference_range_min=12.0,
            reference_range_max=16.0,
            normalization_confidence=0.95
        )
        
        result = detect_mismatch(param)
        
        assert result['has_mismatch'] == True
        assert result['mismatch_type'] == MismatchType.BELOW_RANGE
        assert result['severity'] in ['mild', 'moderate']


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
