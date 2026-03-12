"""
Mismatch Detection Tool

Detects deviations from reference ranges by comparing test values against
their normalized reference ranges.
"""

from typing import Dict, Any, List, Optional
from models.normalized_parameter import NormalizedParameter


class MismatchType:
    """Mismatch classification types"""
    ABOVE_RANGE = "above_range"
    BELOW_RANGE = "below_range"
    WITHIN_RANGE = "within_range"
    NO_REFERENCE = "no_reference"


def detect_mismatch(normalized_param: NormalizedParameter) -> Dict[str, Any]:
    """
    Detect if a normalized parameter deviates from its reference range
    
    Args:
        normalized_param: NormalizedParameter object with normalized value and reference range
    
    Returns:
        Dict containing:
            - has_mismatch: bool indicating if value is outside reference range
            - mismatch_type: Type of mismatch (above_range, below_range, within_range, no_reference)
            - deviation_percentage: Percentage deviation from range (if applicable)
            - severity: Severity level (none, mild, moderate, severe)
            - normalized_parameter_id: ID of the parameter
            - canonical_name: Name of the parameter
            - normalized_value: The measured value
            - reference_range_min: Minimum reference value
            - reference_range_max: Maximum reference value
    """
    result = {
        "has_mismatch": False,
        "mismatch_type": MismatchType.NO_REFERENCE,
        "deviation_percentage": None,
        "severity": "none",
        "normalized_parameter_id": normalized_param.normalized_parameter_id,
        "canonical_name": normalized_param.canonical_name,
        "normalized_value": normalized_param.normalized_value,
        "reference_range_min": normalized_param.reference_range_min,
        "reference_range_max": normalized_param.reference_range_max
    }
    
    # Check if reference range is available
    if normalized_param.reference_range_min is None and normalized_param.reference_range_max is None:
        result["mismatch_type"] = MismatchType.NO_REFERENCE
        return result
    
    value = normalized_param.normalized_value
    min_ref = normalized_param.reference_range_min
    max_ref = normalized_param.reference_range_max
    
    # Handle cases where only one bound is available
    if min_ref is not None and max_ref is not None:
        # Both bounds available
        if value < min_ref:
            result["has_mismatch"] = True
            result["mismatch_type"] = MismatchType.BELOW_RANGE
            result["deviation_percentage"] = ((min_ref - value) / min_ref) * 100
            result["severity"] = _calculate_severity(result["deviation_percentage"])
        elif value > max_ref:
            result["has_mismatch"] = True
            result["mismatch_type"] = MismatchType.ABOVE_RANGE
            result["deviation_percentage"] = ((value - max_ref) / max_ref) * 100
            result["severity"] = _calculate_severity(result["deviation_percentage"])
        else:
            result["mismatch_type"] = MismatchType.WITHIN_RANGE
    
    elif min_ref is not None:
        # Only minimum bound available
        if value < min_ref:
            result["has_mismatch"] = True
            result["mismatch_type"] = MismatchType.BELOW_RANGE
            result["deviation_percentage"] = ((min_ref - value) / min_ref) * 100
            result["severity"] = _calculate_severity(result["deviation_percentage"])
        else:
            result["mismatch_type"] = MismatchType.WITHIN_RANGE
    
    elif max_ref is not None:
        # Only maximum bound available
        if value > max_ref:
            result["has_mismatch"] = True
            result["mismatch_type"] = MismatchType.ABOVE_RANGE
            result["deviation_percentage"] = ((value - max_ref) / max_ref) * 100
            result["severity"] = _calculate_severity(result["deviation_percentage"])
        else:
            result["mismatch_type"] = MismatchType.WITHIN_RANGE
    
    return result


def _calculate_severity(deviation_percentage: float) -> str:
    """
    Calculate severity level based on deviation percentage
    
    Args:
        deviation_percentage: Percentage deviation from reference range
    
    Returns:
        Severity level: mild, moderate, or severe
    """
    abs_deviation = abs(deviation_percentage)
    
    if abs_deviation < 10:
        return "mild"
    elif abs_deviation < 25:
        return "moderate"
    else:
        return "severe"


def detect_mismatches_batch(normalized_params: List[NormalizedParameter]) -> Dict[str, Any]:
    """
    Detect mismatches for multiple normalized parameters
    
    Args:
        normalized_params: List of NormalizedParameter objects
    
    Returns:
        Dict containing:
            - total: Total parameters analyzed
            - mismatches_found: Number of parameters with mismatches
            - within_range: Number of parameters within range
            - no_reference: Number of parameters without reference ranges
            - results: List of individual mismatch detection results
    """
    batch_result = {
        "total": len(normalized_params),
        "mismatches_found": 0,
        "within_range": 0,
        "no_reference": 0,
        "results": []
    }
    
    for param in normalized_params:
        result = detect_mismatch(param)
        batch_result["results"].append(result)
        
        if result["has_mismatch"]:
            batch_result["mismatches_found"] += 1
        elif result["mismatch_type"] == MismatchType.WITHIN_RANGE:
            batch_result["within_range"] += 1
        elif result["mismatch_type"] == MismatchType.NO_REFERENCE:
            batch_result["no_reference"] += 1
    
    return batch_result


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("MISMATCH DETECTION TOOL - TEST")
    print("=" * 80)
    
    # Create test normalized parameter
    test_param = NormalizedParameter(
        normalized_parameter_id="test-123",
        original_parameter_id="orig-456",
        user_id="USER-789",
        canonical_name="glucose",
        original_value=117.0,
        original_unit="mg/dL",
        normalized_value=6.5,
        standard_unit="mmol/L",
        conversion_factor=0.0555,
        reference_range_min=3.9,
        reference_range_max=6.1,
        normalization_confidence=0.95
    )
    
    result = detect_mismatch(test_param)
    
    print("\nMismatch Detection Result:")
    print(f"Has Mismatch: {result['has_mismatch']}")
    print(f"Mismatch Type: {result['mismatch_type']}")
    print(f"Deviation: {result['deviation_percentage']:.2f}%" if result['deviation_percentage'] else "N/A")
    print(f"Severity: {result['severity']}")
    print(f"Parameter: {result['canonical_name']}")
    print(f"Value: {result['normalized_value']} (Range: {result['reference_range_min']}-{result['reference_range_max']})")
    
    print("\n" + "=" * 80)
