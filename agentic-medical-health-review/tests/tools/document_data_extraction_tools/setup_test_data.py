"""
Setup test data for normalize_lab_data tests

This script creates test users and health parameters in the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

import uuid
from models.database_connection import DatabaseConnection


def setup_test_data():
    """Create test users and health parameters"""
    
    with DatabaseConnection() as db:
        # Create test user
        test_user_id = str(uuid.uuid4())
        
        try:
            db.cursor.execute("""
                INSERT INTO users (user_id, email, role, consent_status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING user_id
            """, (test_user_id, 'test@example.com', 'patient', True))
            
            result = db.cursor.fetchone()
            if result:
                test_user_id = result['user_id']
            else:
                # User already exists, get the ID
                db.cursor.execute("""
                    SELECT user_id FROM users WHERE email = %s
                """, ('test@example.com',))
                test_user_id = db.cursor.fetchone()['user_id']
            
            print(f"Test user ID: {test_user_id}")
            
            # Create test health parameters
            test_params = [
                {
                    'parameter_name': 'Blood Glucose',
                    'value': 117.0,
                    'unit': 'mg/dL'
                },
                {
                    'parameter_name': 'HbA1c',
                    'value': 6.5,
                    'unit': '%'
                },
                {
                    'parameter_name': 'Total Cholesterol',
                    'value': 200.0,
                    'unit': 'mg/dL'
                }
            ]
            
            param_ids = []
            for param in test_params:
                param_id = str(uuid.uuid4())
                db.cursor.execute("""
                    INSERT INTO health_parameters (
                        parameter_id, user_id, parameter_name, value, unit,
                        timestamp, source, normalization_status
                    ) VALUES (%s, %s, %s, %s, %s, NOW(), 'report', 'pending')
                    RETURNING parameter_id
                """, (param_id, test_user_id, param['parameter_name'], 
                      param['value'], param['unit']))
                
                param_ids.append(param_id)
                print(f"Created parameter: {param['parameter_name']} (ID: {param_id})")
            
            return test_user_id, param_ids
            
        except Exception as e:
            print(f"Error setting up test data: {e}")
            raise


if __name__ == "__main__":
    print("Setting up test data...")
    user_id, param_ids = setup_test_data()
    print(f"\nTest data created successfully!")
    print(f"User ID: {user_id}")
    print(f"Parameter IDs: {param_ids}")
