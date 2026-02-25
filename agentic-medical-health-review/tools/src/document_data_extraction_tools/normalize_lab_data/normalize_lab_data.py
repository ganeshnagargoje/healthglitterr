"""
Lab Data Normalization Tool

Normalizes extracted lab parameters by:
1. Standardizing parameter names to canonical forms
2. Converting units to standard units
3. Aligning reference ranges to standard units

This tool integrates with PostgreSQL database to:
- Read normalization rules from reference tables
- Write normalized data to normalized_parameters table
- Log all operations to normalization_audit_logs table
- Update health_parameters status
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any, Optional
import uuid
from models.database_connection import DatabaseConnection
from lab_data_normalizer import LabDataNormalizer


def normalize_lab_data(
    parameter_id: str,
    user_id: str,
    parameter_name: str,
    value: float,
    unit: Optional[str] = None,
    reference_range: Optional[str] = None
) -> Dict[str, Any]:
    """
    Normalize a single lab parameter
    
    This function performs a complete normalization workflow:
    1. Maps parameter name to canonical form
    2. Converts value to standard unit
    3. Aligns reference range to standard unit
    4. Saves normalized data to database
    5. Logs all operations for audit trail
    
    Args:
        parameter_id: UUID of the health parameter (from health_parameters table)
        user_id: User ID
        parameter_name: Original parameter name from lab report
        value: Measured value
        unit: Original unit (optional)
        reference_range: Original reference range string (optional, not currently used)
    
    Returns:
        Dict containing:
            - success: bool indicating if normalization succeeded
            - normalized_parameter: Dict with normalized data if successful
            - operations_logged: Number of operations logged to audit trail
            - errors: List of error messages
            - warnings: List of warning messages
            - flagged_for_review: bool indicating if human review needed
    
    Example:
        >>> result = normalize_lab_data(
        ...     parameter_id="550e8400-e29b-41d4-a716-446655440000",
        ...     user_id="USER-123ABC",
        ...     parameter_name="Blood Glucose",
        ...     value=117.0,
        ...     unit="mg/dL"
        ... )
        >>> print(result['success'])
        True
        >>> print(result['normalized_parameter']['normalized_value'])
        6.4935
    """
    result = {
        "success": False,
        "normalized_parameter": None,
        "operations_logged": 0,
        "errors": [],
        "warnings": [],
        "flagged_for_review": False
    }
    
    try:
        with DatabaseConnection() as db:
            normalizer = LabDataNormalizer(db)
            
            # Step 1: Normalize parameter name
            canonical_name, name_confidence = normalizer.normalize_parameter_name(
                parameter_name, parameter_id
            )
            
            if not canonical_name:
                result["errors"].append(f"Could not map parameter name: {parameter_name}")
                result["flagged_for_review"] = True
                normalizer.save_audit_logs()
                result["operations_logged"] = len(normalizer.operations_log)
                
                # Update health_parameters status to 'flagged'
                db.cursor.execute("""
                    UPDATE health_parameters
                    SET normalization_status = 'flagged'
                    WHERE parameter_id = %s
                """, (parameter_id,))
                
                return result
            
            # Step 2: Convert unit
            normalized_value, standard_unit, conversion_factor, unit_confidence = normalizer.convert_unit(
                value, unit, canonical_name, parameter_id
            )
            
            if normalized_value is None:
                result["errors"].append(f"Could not convert unit: {unit}")
                result["flagged_for_review"] = True
                normalizer.save_audit_logs()
                result["operations_logged"] = len(normalizer.operations_log)
                
                # Update health_parameters status to 'flagged'
                db.cursor.execute("""
                    UPDATE health_parameters
                    SET normalization_status = 'flagged'
                    WHERE parameter_id = %s
                """, (parameter_id,))
                
                return result
            
            # Step 3: Align reference range
            range_min, range_max, range_confidence = normalizer.align_reference_range(
                canonical_name, standard_unit, parameter_id
            )
            
            if range_min is None and range_max is None:
                result["warnings"].append(f"No reference range available for {canonical_name}")
            
            # Calculate overall confidence (average of all three operations)
            overall_confidence = (name_confidence + unit_confidence + range_confidence) / 3.0
            
            # Step 4: Save normalized parameter to normalized_parameters table
            normalized_param_id = str(uuid.uuid4())
            
            db.cursor.execute("""
                INSERT INTO normalized_parameters (
                    normalized_parameter_id, original_parameter_id, user_id,
                    canonical_name, original_value, original_unit,
                    normalized_value, standard_unit, conversion_factor,
                    reference_range_min, reference_range_max, normalization_confidence
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                normalized_param_id, parameter_id, user_id,
                canonical_name, value, unit,
                normalized_value, standard_unit, conversion_factor,
                range_min, range_max, overall_confidence
            ))
            
            # Step 5: Update health_parameters status to 'normalized'
            db.cursor.execute("""
                UPDATE health_parameters
                SET normalization_status = 'normalized'
                WHERE parameter_id = %s
            """, (parameter_id,))
            
            # Step 6: Save audit logs to normalization_audit_logs table
            normalizer.save_audit_logs()
            
            # Build success result
            result["success"] = True
            result["normalized_parameter"] = {
                "normalized_parameter_id": normalized_param_id,
                "original_parameter_id": parameter_id,
                "user_id": user_id,
                "canonical_name": canonical_name,
                "original_value": value,
                "original_unit": unit,
                "normalized_value": normalized_value,
                "standard_unit": standard_unit,
                "conversion_factor": conversion_factor,
                "reference_range_min": range_min,
                "reference_range_max": range_max,
                "normalization_confidence": overall_confidence
            }
            result["operations_logged"] = len(normalizer.operations_log)
            
            # Flag for review if confidence is low
            if overall_confidence < 0.7:
                result["flagged_for_review"] = True
                result["warnings"].append(f"Low confidence score: {overall_confidence:.2f}")
            
    except Exception as e:
        result["errors"].append(f"Unexpected error: {str(e)}")
        result["flagged_for_review"] = True
    
    return result


def normalize_batch(parameters: list) -> Dict[str, Any]:
    """
    Normalize multiple lab parameters in batch
    
    Args:
        parameters: List of dicts, each containing:
            - parameter_id, user_id, parameter_name, value, unit (optional)
    
    Returns:
        Dict containing:
            - total: Total parameters processed
            - successful: Number of successful normalizations
            - failed: Number of failed normalizations
            - flagged: Number flagged for review
            - results: List of individual results
    """
    batch_result = {
        "total": len(parameters),
        "successful": 0,
        "failed": 0,
        "flagged": 0,
        "results": []
    }
    
    for param in parameters:
        result = normalize_lab_data(
            parameter_id=param['parameter_id'],
            user_id=param['user_id'],
            parameter_name=param['parameter_name'],
            value=param['value'],
            unit=param.get('unit'),
            reference_range=param.get('reference_range')
        )
        
        batch_result["results"].append(result)
        
        if result['success']:
            batch_result["successful"] += 1
        else:
            batch_result["failed"] += 1
        
        if result['flagged_for_review']:
            batch_result["flagged"] += 1
    
    return batch_result


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("LAB DATA NORMALIZATION TOOL - TEST")
    print("=" * 80)
    
    # Test single parameter normalization
    test_result = normalize_lab_data(
        parameter_id="550e8400-e29b-41d4-a716-446655440000",
        user_id="USER-123ABC",
        parameter_name="Blood Glucose",
        value=117.0,
        unit="mg/dL"
    )
    
    print("\nNormalization Result:")
    print(f"Success: {test_result['success']}")
    print(f"Operations Logged: {test_result['operations_logged']}")
    print(f"Flagged for Review: {test_result['flagged_for_review']}")
    
    if test_result['normalized_parameter']:
        print("\nNormalized Parameter:")
        for key, val in test_result['normalized_parameter'].items():
            print(f"  {key}: {val}")
    
    if test_result['errors']:
        print("\nErrors:")
        for error in test_result['errors']:
            print(f"  - {error}")
    
    if test_result['warnings']:
        print("\nWarnings:")
        for warning in test_result['warnings']:
            print(f"  - {warning}")
    
    print("\n" + "=" * 80)
