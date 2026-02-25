"""
Test normalize_lab_data_tool with real database data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from tools.src.document_data_extraction_tools.normalize_lab_data.normalize_lab_data import normalize_lab_data
from models.database_connection import DatabaseConnection


def test_with_real_data():
    """Test normalization with actual database records"""
    
    # Get a test parameter from database
    with DatabaseConnection() as db:
        db.cursor.execute("""
            SELECT parameter_id, user_id, parameter_name, value, unit
            FROM health_parameters
            WHERE normalization_status = 'pending'
            LIMIT 1
        """)
        
        param = db.cursor.fetchone()
        
        if not param:
            print("No pending parameters found. Run setup_test_data.py first.")
            return
        
        print(f"Testing with parameter:")
        print(f"  ID: {param['parameter_id']}")
        print(f"  Name: {param['parameter_name']}")
        print(f"  Value: {param['value']} {param['unit']}")
        print()
        
        # Normalize the parameter
        result = normalize_lab_data(
            parameter_id=param['parameter_id'],
            user_id=param['user_id'],
            parameter_name=param['parameter_name'],
            value=float(param['value']),
            unit=param['unit']
        )
        
        print("=" * 80)
        print("NORMALIZATION RESULT")
        print("=" * 80)
        print(f"Success: {result['success']}")
        print(f"Operations Logged: {result['operations_logged']}")
        print(f"Flagged for Review: {result['flagged_for_review']}")
        
        if result['normalized_parameter']:
            print("\nNormalized Parameter:")
            for key, val in result['normalized_parameter'].items():
                print(f"  {key}: {val}")
        
        if result['errors']:
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print("\nWarnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        print("=" * 80)


if __name__ == "__main__":
    test_with_real_data()
