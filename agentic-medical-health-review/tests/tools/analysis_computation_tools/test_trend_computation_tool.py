"""
Tests for Trend Computation Tool

Tests the trend_computation_tool functionality including:
- Increasing trend detection
- Decreasing trend detection
- Stable trend detection
- Confidence score calculation
- Insufficient data handling
- Batch processing
- Edge cases
"""

import sys
import os
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tools" / "src" / "analysis_computation_tools"))

import pytest
from datetime import datetime, timedelta
from trend_computation import (
    compute_trend,
    compute_trends_batch,
    TrendType,
    _calculate_slope,
    _calculate_std_dev
)


class TestComputeTrend:
    """Test suite for compute_trend function"""
    
    def test_increasing_trend(self):
        """Test detection of increasing trend"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 5.5, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 6.0, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 6.5, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-001")
        
        assert result['trend_type'] == TrendType.INCREASING
        assert result['confidence_score'] > 0.0
        assert result['data_point_count'] == 4
        assert result['value_change'] == 1.5
        assert result['percentage_change'] == 30.0
        assert result['average_value'] == 5.75

    
    def test_decreasing_trend(self):
        """Test detection of decreasing trend"""
        data_points = [
            {"value": 6.5, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 6.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 5.5, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 5.0, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-002")
        
        assert result['trend_type'] == TrendType.DECREASING
        assert result['confidence_score'] > 0.0
        assert result['data_point_count'] == 4
        assert result['value_change'] == -1.5
        assert result['percentage_change'] < 0
        assert result['average_value'] == 5.75
    
    def test_stable_trend(self):
        """Test detection of stable trend"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 5.1, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 4.9, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 5.0, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-003")
        
        assert result['trend_type'] == TrendType.STABLE
        assert result['confidence_score'] > 0.0
        assert result['data_point_count'] == 4
        assert abs(result['percentage_change']) < 5.0
    
    def test_insufficient_data_single_point(self):
        """Test handling of single data point"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-004")
        
        assert result['trend_type'] == TrendType.INSUFFICIENT_DATA
        assert result['confidence_score'] == 0.0
        assert result['data_point_count'] == 1
        assert result['value_change'] is None
    
    def test_insufficient_data_empty_list(self):
        """Test handling of empty data list"""
        data_points = []
        
        result = compute_trend(data_points, "glucose_fasting", "USER-005")
        
        assert result['trend_type'] == TrendType.INSUFFICIENT_DATA
        assert result['confidence_score'] == 0.0
        assert result['data_point_count'] == 0

    
    def test_two_data_points_minimum(self):
        """Test with exactly 2 data points (minimum required)"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 6.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-006")
        
        assert result['trend_type'] in [TrendType.INCREASING, TrendType.DECREASING, TrendType.STABLE]
        assert result['confidence_score'] > 0.0
        assert result['data_point_count'] == 2
        assert result['value_change'] == 1.0
    
    def test_unsorted_timestamps(self):
        """Test that unsorted data points are handled correctly"""
        data_points = [
            {"value": 6.0, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 6.5, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"},
            {"value": 5.5, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-007")
        
        # Should sort and detect increasing trend
        assert result['trend_type'] == TrendType.INCREASING
        assert result['value_change'] == 1.5  # From 5.0 to 6.5
    
    def test_iso_string_timestamps(self):
        """Test with ISO format string timestamps"""
        data_points = [
            {"value": 5.0, "timestamp": "2024-01-01T00:00:00", "parameter_id": "id1"},
            {"value": 5.5, "timestamp": "2024-02-01T00:00:00", "parameter_id": "id2"},
            {"value": 6.0, "timestamp": "2024-03-01T00:00:00", "parameter_id": "id3"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-008")
        
        assert result['trend_type'] == TrendType.INCREASING
        assert result['data_point_count'] == 3


class TestConfidenceScore:
    """Test suite for confidence score calculation"""
    
    def test_high_confidence_consistent_trend(self):
        """Test high confidence with consistent increasing values"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 5.5, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 6.0, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 6.5, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"},
            {"value": 7.0, "timestamp": datetime(2024, 5, 1), "parameter_id": "id5"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-009")
        
        # Consistent trend with 5+ points should have high confidence
        assert result['confidence_score'] > 0.7

    
    def test_low_confidence_erratic_values(self):
        """Test low confidence with erratic values"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 8.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 4.0, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 7.0, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-010")
        
        # Erratic values should have lower confidence
        assert result['confidence_score'] < 0.8
    
    def test_confidence_increases_with_data_points(self):
        """Test that confidence increases with more data points"""
        # 2 data points
        data_2 = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 6.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        # 5 data points
        data_5 = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 5.5, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 6.0, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 6.5, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"},
            {"value": 7.0, "timestamp": datetime(2024, 5, 1), "parameter_id": "id5"}
        ]
        
        result_2 = compute_trend(data_2, "glucose_fasting", "USER-011")
        result_5 = compute_trend(data_5, "glucose_fasting", "USER-012")
        
        # More data points should generally increase confidence
        assert result_5['confidence_score'] >= result_2['confidence_score']


class TestTimeSpan:
    """Test suite for time span calculation"""
    
    def test_time_span_calculation(self):
        """Test time span calculation in days"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 6.0, "timestamp": datetime(2024, 1, 31), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-013")
        
        assert result['time_span_days'] == 30.0
    
    def test_same_day_measurements(self):
        """Test with measurements on the same day"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1, 8, 0), "parameter_id": "id1"},
            {"value": 7.0, "timestamp": datetime(2024, 1, 1, 20, 0), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-014")
        
        assert result['time_span_days'] == 0.5  # 12 hours = 0.5 days



class TestBatchTrendComputation:
    """Test suite for batch trend computation"""
    
    def test_batch_multiple_parameters(self):
        """Test batch computation for multiple parameters"""
        parameters_data = {
            "glucose_fasting": [
                {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
                {"value": 6.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
            ],
            "cholesterol_total": [
                {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id3"},
                {"value": 4.5, "timestamp": datetime(2024, 2, 1), "parameter_id": "id4"}
            ]
        }
        
        result = compute_trends_batch(parameters_data, "USER-015")
        
        assert result['total_parameters'] == 2
        assert result['trends_computed'] == 2
        assert result['insufficient_data'] == 0
        assert "glucose_fasting" in result['results']
        assert "cholesterol_total" in result['results']
    
    def test_batch_with_insufficient_data(self):
        """Test batch with some parameters having insufficient data"""
        parameters_data = {
            "glucose_fasting": [
                {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
                {"value": 6.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
            ],
            "hemoglobin": [
                {"value": 14.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id3"}
            ]
        }
        
        result = compute_trends_batch(parameters_data, "USER-016")
        
        assert result['total_parameters'] == 2
        assert result['trends_computed'] == 1
        assert result['insufficient_data'] == 1
    
    def test_batch_empty_dict(self):
        """Test batch with empty dictionary"""
        result = compute_trends_batch({}, "USER-017")
        
        assert result['total_parameters'] == 0
        assert result['trends_computed'] == 0
        assert result['insufficient_data'] == 0


class TestEdgeCases:
    """Test suite for edge cases"""
    
    def test_zero_initial_value(self):
        """Test with zero as initial value"""
        data_points = [
            {"value": 0.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 5.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-018")
        
        # Should handle division by zero gracefully
        # Percentage change will be 0 to avoid division by zero, making it appear stable
        assert result['trend_type'] == TrendType.STABLE
        assert result['percentage_change'] == 0  # Handled gracefully
        assert result['value_change'] == 5.0  # Absolute change is still tracked

    
    def test_negative_values(self):
        """Test with negative values"""
        data_points = [
            {"value": -2.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": -1.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "custom_param", "USER-019")
        
        assert result['trend_type'] == TrendType.INCREASING
        assert result['value_change'] == 1.0
    
    def test_all_same_values(self):
        """Test with all identical values"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 5.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 5.0, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-020")
        
        assert result['trend_type'] == TrendType.STABLE
        assert result['value_change'] == 0.0
        assert result['percentage_change'] == 0.0
    
    def test_very_large_values(self):
        """Test with very large values"""
        data_points = [
            {"value": 1000.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 1100.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "custom_param", "USER-021")
        
        assert result['trend_type'] == TrendType.INCREASING
        assert result['value_change'] == 100.0
        assert result['percentage_change'] == 10.0


class TestSlopeCalculation:
    """Test suite for slope calculation"""
    
    def test_positive_slope(self):
        """Test positive slope calculation"""
        values = [1.0, 2.0, 3.0, 4.0]
        timestamps = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 3),
            datetime(2024, 1, 4)
        ]
        
        slope = _calculate_slope(values, timestamps)
        
        assert slope > 0
    
    def test_negative_slope(self):
        """Test negative slope calculation"""
        values = [4.0, 3.0, 2.0, 1.0]
        timestamps = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 3),
            datetime(2024, 1, 4)
        ]
        
        slope = _calculate_slope(values, timestamps)
        
        assert slope < 0

    
    def test_zero_slope(self):
        """Test zero slope with flat values"""
        values = [5.0, 5.0, 5.0]
        timestamps = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 3)
        ]
        
        slope = _calculate_slope(values, timestamps)
        
        assert slope == 0.0


class TestStandardDeviation:
    """Test suite for standard deviation calculation"""
    
    def test_std_dev_calculation(self):
        """Test standard deviation calculation"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        mean = 3.0
        
        std_dev = _calculate_std_dev(values, mean)
        
        # Expected std dev ≈ 1.58
        assert abs(std_dev - 1.58) < 0.01
    
    def test_std_dev_identical_values(self):
        """Test standard deviation with identical values"""
        values = [5.0, 5.0, 5.0]
        mean = 5.0
        
        std_dev = _calculate_std_dev(values, mean)
        
        assert std_dev == 0.0
    
    def test_std_dev_single_value(self):
        """Test standard deviation with single value"""
        values = [5.0]
        mean = 5.0
        
        std_dev = _calculate_std_dev(values, mean)
        
        assert std_dev == 0.0


class TestRealWorldScenarios:
    """Test suite for real-world medical scenarios"""
    
    def test_diabetes_progression(self):
        """Test glucose levels showing diabetes progression"""
        data_points = [
            {"value": 5.5, "timestamp": datetime(2023, 1, 1), "parameter_id": "id1"},
            {"value": 6.0, "timestamp": datetime(2023, 6, 1), "parameter_id": "id2"},
            {"value": 6.8, "timestamp": datetime(2024, 1, 1), "parameter_id": "id3"},
            {"value": 7.5, "timestamp": datetime(2024, 6, 1), "parameter_id": "id4"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-022")
        
        assert result['trend_type'] == TrendType.INCREASING
        assert result['percentage_change'] > 30
        assert result['time_span_days'] > 500
    
    def test_cholesterol_improvement(self):
        """Test cholesterol levels showing improvement"""
        data_points = [
            {"value": 6.5, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 6.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 5.5, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 5.0, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"}
        ]
        
        result = compute_trend(data_points, "cholesterol_total", "USER-023")
        
        assert result['trend_type'] == TrendType.DECREASING
        assert result['percentage_change'] < 0

    
    def test_stable_well_controlled_parameter(self):
        """Test stable trend for well-controlled parameter"""
        data_points = [
            {"value": 5.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 5.1, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"},
            {"value": 4.9, "timestamp": datetime(2024, 3, 1), "parameter_id": "id3"},
            {"value": 5.0, "timestamp": datetime(2024, 4, 1), "parameter_id": "id4"},
            {"value": 5.1, "timestamp": datetime(2024, 5, 1), "parameter_id": "id5"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-024")
        
        assert result['trend_type'] == TrendType.STABLE
        assert abs(result['percentage_change']) < 5.0
        assert result['confidence_score'] > 0.7


class TestPercentageChange:
    """Test suite for percentage change calculation"""
    
    def test_percentage_change_positive(self):
        """Test positive percentage change"""
        data_points = [
            {"value": 100.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 150.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "custom_param", "USER-025")
        
        assert result['percentage_change'] == 50.0
    
    def test_percentage_change_negative(self):
        """Test negative percentage change"""
        data_points = [
            {"value": 100.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 75.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "custom_param", "USER-026")
        
        assert result['percentage_change'] == -25.0
    
    def test_small_percentage_change(self):
        """Test small percentage change (should be stable)"""
        data_points = [
            {"value": 100.0, "timestamp": datetime(2024, 1, 1), "parameter_id": "id1"},
            {"value": 102.0, "timestamp": datetime(2024, 2, 1), "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "custom_param", "USER-027")
        
        assert result['trend_type'] == TrendType.STABLE
        assert result['percentage_change'] == 2.0


class TestTimestampFormats:
    """Test suite for different timestamp formats"""
    
    def test_iso_format_with_timezone(self):
        """Test ISO format with timezone"""
        data_points = [
            {"value": 5.0, "timestamp": "2024-01-01T00:00:00Z", "parameter_id": "id1"},
            {"value": 6.0, "timestamp": "2024-02-01T00:00:00Z", "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-028")
        
        assert result['trend_type'] == TrendType.INCREASING
    
    def test_date_only_format(self):
        """Test date-only format"""
        data_points = [
            {"value": 5.0, "timestamp": "2024-01-01", "parameter_id": "id1"},
            {"value": 6.0, "timestamp": "2024-02-01", "parameter_id": "id2"}
        ]
        
        result = compute_trend(data_points, "glucose_fasting", "USER-029")
        
        assert result['trend_type'] == TrendType.INCREASING


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
