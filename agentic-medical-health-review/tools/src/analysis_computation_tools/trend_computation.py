"""
Trend Computation Tool

Computes trends across multiple lab reports or device data points by analyzing
temporal patterns in normalized parameter values.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from models.normalized_parameter import NormalizedParameter


class TrendType:
    """Trend classification types"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    INSUFFICIENT_DATA = "insufficient_data"


class TrendDataPoint:
    """Data point for trend analysis"""
    def __init__(self, value: float, timestamp: datetime, parameter_id: str):
        self.value = value
        self.timestamp = timestamp
        self.parameter_id = parameter_id


def compute_trend(
    data_points: List[Dict[str, Any]],
    canonical_name: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Compute trend across multiple data points for a specific parameter
    
    Args:
        data_points: List of dicts containing:
            - value: float (normalized value)
            - timestamp: datetime or ISO string
            - parameter_id: str (optional, for tracking)
        canonical_name: Name of the parameter being analyzed
        user_id: User ID
    
    Returns:
        Dict containing:
            - trend_type: Type of trend (increasing, decreasing, stable, insufficient_data)
            - confidence_score: Confidence in trend detection (0-1)
            - data_point_count: Number of data points analyzed
            - value_change: Absolute change from first to last value
            - percentage_change: Percentage change from first to last value
            - average_value: Mean value across all data points
            - canonical_name: Parameter name
            - user_id: User ID
            - time_span_days: Number of days between first and last measurement
    """
    result = {
        "trend_type": TrendType.INSUFFICIENT_DATA,
        "confidence_score": 0.0,
        "data_point_count": len(data_points),
        "value_change": None,
        "percentage_change": None,
        "average_value": None,
        "canonical_name": canonical_name,
        "user_id": user_id,
        "time_span_days": None
    }
    
    # Validate minimum data points
    if len(data_points) < 2:
        return result
    
    # Sort data points by timestamp
    sorted_points = sorted(data_points, key=lambda x: _parse_timestamp(x['timestamp']))
    
    # Extract values and timestamps
    values = [point['value'] for point in sorted_points]
    timestamps = [_parse_timestamp(point['timestamp']) for point in sorted_points]
    
    # Calculate basic statistics
    first_value = values[0]
    last_value = values[-1]
    value_change = last_value - first_value
    percentage_change = (value_change / first_value * 100) if first_value != 0 else 0
    average_value = sum(values) / len(values)
    
    # Calculate time span
    time_span = timestamps[-1] - timestamps[0]
    time_span_days = time_span.days + (time_span.seconds / 86400)
    
    # Determine trend type using linear regression slope
    slope = _calculate_slope(values, timestamps)
    trend_type, confidence = _classify_trend(slope, values, percentage_change)
    
    result.update({
        "trend_type": trend_type,
        "confidence_score": confidence,
        "value_change": value_change,
        "percentage_change": percentage_change,
        "average_value": average_value,
        "time_span_days": time_span_days
    })
    
    return result


def _parse_timestamp(timestamp: Any) -> datetime:
    """Parse timestamp from various formats"""
    if isinstance(timestamp, datetime):
        return timestamp
    elif isinstance(timestamp, str):
        # Try ISO format
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            # Try common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
                try:
                    return datetime.strptime(timestamp, fmt)
                except:
                    continue
    raise ValueError(f"Could not parse timestamp: {timestamp}")


def _calculate_slope(values: List[float], timestamps: List[datetime]) -> float:
    """
    Calculate slope using simple linear regression
    
    Returns slope in units per day
    """
    n = len(values)
    if n < 2:
        return 0.0
    
    # Convert timestamps to days since first measurement
    time_days = [(t - timestamps[0]).total_seconds() / 86400 for t in timestamps]
    
    # Calculate means
    mean_time = sum(time_days) / n
    mean_value = sum(values) / n
    
    # Calculate slope using least squares
    numerator = sum((time_days[i] - mean_time) * (values[i] - mean_value) for i in range(n))
    denominator = sum((time_days[i] - mean_time) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0.0
    
    slope = numerator / denominator
    return slope


def _classify_trend(slope: float, values: List[float], percentage_change: float) -> tuple:
    """
    Classify trend type and calculate confidence score
    
    Returns:
        Tuple of (trend_type, confidence_score)
    """
    # Calculate variability (coefficient of variation)
    mean_value = sum(values) / len(values)
    std_dev = _calculate_std_dev(values, mean_value)
    cv = (std_dev / mean_value) if mean_value != 0 else 0
    
    # Base confidence on consistency (lower variability = higher confidence)
    base_confidence = max(0.0, 1.0 - cv)
    
    # Adjust confidence based on number of data points
    data_point_factor = min(1.0, len(values) / 5.0)  # Max confidence at 5+ points
    confidence = base_confidence * data_point_factor
    
    # Classify trend based on percentage change and slope
    abs_percentage_change = abs(percentage_change)
    
    if abs_percentage_change < 5.0:
        # Less than 5% change is considered stable
        return TrendType.STABLE, confidence
    elif slope > 0:
        return TrendType.INCREASING, confidence
    elif slope < 0:
        return TrendType.DECREASING, confidence
    else:
        return TrendType.STABLE, confidence


def _calculate_std_dev(values: List[float], mean: float) -> float:
    """Calculate standard deviation"""
    if len(values) < 2:
        return 0.0
    
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5


def compute_trends_batch(
    parameters_data: Dict[str, List[Dict[str, Any]]],
    user_id: str
) -> Dict[str, Any]:
    """
    Compute trends for multiple parameters in batch
    
    Args:
        parameters_data: Dict mapping canonical_name to list of data points
            Example: {
                "glucose_fasting": [
                    {"value": 5.0, "timestamp": "2024-01-01", "parameter_id": "id1"},
                    {"value": 5.5, "timestamp": "2024-02-01", "parameter_id": "id2"}
                ],
                "cholesterol_total": [...]
            }
        user_id: User ID
    
    Returns:
        Dict containing:
            - total_parameters: Number of parameters analyzed
            - trends_computed: Number of trends successfully computed
            - insufficient_data: Number of parameters with insufficient data
            - results: Dict mapping canonical_name to trend result
    """
    batch_result = {
        "total_parameters": len(parameters_data),
        "trends_computed": 0,
        "insufficient_data": 0,
        "results": {}
    }
    
    for canonical_name, data_points in parameters_data.items():
        trend_result = compute_trend(data_points, canonical_name, user_id)
        batch_result["results"][canonical_name] = trend_result
        
        if trend_result["trend_type"] == TrendType.INSUFFICIENT_DATA:
            batch_result["insufficient_data"] += 1
        else:
            batch_result["trends_computed"] += 1
    
    return batch_result


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("TREND COMPUTATION TOOL - TEST")
    print("=" * 80)
    
    # Test increasing trend
    test_data = [
        {"value": 5.0, "timestamp": "2024-01-01", "parameter_id": "id1"},
        {"value": 5.5, "timestamp": "2024-02-01", "parameter_id": "id2"},
        {"value": 6.0, "timestamp": "2024-03-01", "parameter_id": "id3"},
        {"value": 6.5, "timestamp": "2024-04-01", "parameter_id": "id4"}
    ]
    
    result = compute_trend(test_data, "glucose_fasting", "USER-123")
    
    print("\nTrend Analysis Result:")
    print(f"Trend Type: {result['trend_type']}")
    print(f"Confidence Score: {result['confidence_score']:.2f}")
    print(f"Data Points: {result['data_point_count']}")
    print(f"Value Change: {result['value_change']:.2f}")
    print(f"Percentage Change: {result['percentage_change']:.2f}%")
    print(f"Average Value: {result['average_value']:.2f}")
    print(f"Time Span: {result['time_span_days']:.1f} days")
    
    print("\n" + "=" * 80)
