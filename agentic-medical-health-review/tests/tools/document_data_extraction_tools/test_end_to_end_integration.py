"""
End-to-End Integration Test

This test demonstrates the complete workflow:
1. Extract lab data from PDF using lab_report_parser
2. Normalize the extracted data using normalize_lab_data
3. Display the complete results
"""

import sys
import os
from pathlib import Path
import uuid

# Add paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tools" / "src" / "document_data_extraction_tools" / "lab_report_parser"))
sys.path.insert(0, str(project_root / "tools" / "src" / "document_data_extraction_tools" / "normalize_lab_data"))

from lab_report_parser import extract_structured_lab_data
from normalize_lab_data import normalize_lab_data
from models.database_connection import DatabaseConnection


def create_health_parameter(user_id, test_data):
    """
    Create a health_parameter record in the database
    
    Args:
        user_id: UUID of the user
        test_data: Dict with test_name, test_value, unit
    
    Returns:
        parameter_id: UUID of created parameter
    """
    with DatabaseConnection() as db:
        parameter_id = str(uuid.uuid4())
        
        # Parse the test value (remove any non-numeric characters except decimal point)
        try:
            value = float(''.join(c for c in str(test_data['test_value']) if c.isdigit() or c == '.'))
        except:
            value = 0.0
        
        db.cursor.execute("""
            INSERT INTO health_parameters (
                parameter_id, user_id, parameter_name, value, unit,
                timestamp, source, normalization_status
            ) VALUES (%s, %s, %s, %s, %s, NOW(), 'report', 'pending')
            RETURNING parameter_id
        """, (parameter_id, user_id, test_data['test_name'], value, test_data['unit']))
        
        return parameter_id


def test_end_to_end_integration(pdf_path):
    """
    Complete end-to-end test of lab report processing
    
    Args:
        pdf_path: Path to the lab report PDF file
    """
    print("=" * 80)
    print("END-TO-END INTEGRATION TEST")
    print("Lab Report Parser → Normalize Lab Data")
    print("=" * 80)
    
    # Step 1: Extract data from lab report
    print("\n📄 STEP 1: Extract Lab Data from PDF")
    print("-" * 80)
    print(f"File: {pdf_path}")
    
    try:
        report_data = extract_structured_lab_data(pdf_path)
        
        print(f"✓ Extraction Status: {report_data['metadata']['extraction_status']}")
        print(f"✓ Tests Found: {report_data['metadata']['total_tests_found']}")
        print(f"✓ Raw Text Length: {len(report_data['raw_text'])} characters")
        
        if not report_data['tests']:
            print("\n⚠ No structured test data found. Cannot proceed with normalization.")
            return
        
        print(f"\n✓ Extracted {len(report_data['tests'])} lab tests:")
        for i, test in enumerate(report_data['tests'], 1):
            print(f"  {i}. {test['test_name']}: {test['test_value']} {test['unit']}")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Get or create test user
    print("\n👤 STEP 2: Setup Test User")
    print("-" * 80)
    
    with DatabaseConnection() as db:
        # Check if test user exists
        db.cursor.execute("""
            SELECT user_id FROM users WHERE email = %s
        """, ('test@example.com',))
        
        result = db.cursor.fetchone()
        if result:
            user_id = result['user_id']
            print(f"✓ Using existing test user: {user_id}")
        else:
            # Create test user
            user_id = str(uuid.uuid4())
            db.cursor.execute("""
                INSERT INTO users (user_id, email, role, consent_status)
                VALUES (%s, %s, %s, %s)
            """, (user_id, 'test@example.com', 'patient', True))
            print(f"✓ Created new test user: {user_id}")
    
    # Step 3: Normalize each extracted test
    print("\n🔄 STEP 3: Normalize Extracted Lab Data")
    print("-" * 80)
    
    results = []
    
    for i, test in enumerate(report_data['tests'], 1):
        print(f"\n[{i}/{len(report_data['tests'])}] Processing: {test['test_name']}")
        print(f"     Original: {test['test_value']} {test['unit']}")
        
        try:
            # Create health parameter record
            parameter_id = create_health_parameter(user_id, test)
            print(f"     ✓ Created parameter record: {parameter_id}")
            
            # Parse value
            try:
                value = float(''.join(c for c in str(test['test_value']) if c.isdigit() or c == '.'))
            except:
                print(f"     ⚠ Could not parse value: {test['test_value']}")
                continue
            
            # Normalize the parameter
            result = normalize_lab_data(
                parameter_id=parameter_id,
                user_id=user_id,
                parameter_name=test['test_name'],
                value=value,
                unit=test['unit']
            )
            
            results.append({
                'original': test,
                'normalization': result
            })
            
            if result['success']:
                norm = result['normalized_parameter']
                print(f"     ✓ Normalized: {norm['normalized_value']} {norm['standard_unit']}")
                print(f"     ✓ Canonical Name: {norm['canonical_name']}")
                print(f"     ✓ Confidence: {norm['normalization_confidence']:.2f}")
                if norm['reference_range_min'] and norm['reference_range_max']:
                    print(f"     ✓ Reference Range: {norm['reference_range_min']} - {norm['reference_range_max']} {norm['standard_unit']}")
            else:
                print(f"     ❌ Normalization failed: {result['errors']}")
                if result['flagged_for_review']:
                    print(f"     ⚠ Flagged for human review")
        
        except Exception as e:
            print(f"     ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Step 4: Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['normalization']['success'])
    failed = len(results) - successful
    flagged = sum(1 for r in results if r['normalization']['flagged_for_review'])
    
    print(f"\nTotal Tests Processed: {len(results)}")
    print(f"✓ Successfully Normalized: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⚠ Flagged for Review: {flagged}")
    
    # Detailed results table
    if results:
        print("\n" + "-" * 80)
        print("DETAILED RESULTS")
        print("-" * 80)
        print(f"{'Test Name':<30} {'Original':<20} {'Normalized':<20} {'Status':<10}")
        print("-" * 80)
        
        for r in results:
            test = r['original']
            norm_result = r['normalization']
            
            original_str = f"{test['test_value']} {test['unit']}"
            
            if norm_result['success']:
                norm = norm_result['normalized_parameter']
                normalized_str = f"{norm['normalized_value']:.2f} {norm['standard_unit']}"
                status = "✓ OK" if not norm_result['flagged_for_review'] else "⚠ Review"
            else:
                normalized_str = "Failed"
                status = "❌ Error"
            
            print(f"{test['test_name']:<30} {original_str:<20} {normalized_str:<20} {status:<10}")
        
        print("-" * 80)
    
    print("\n✅ End-to-End Integration Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    # Default test file
    default_pdf = "tests/test_data/sample_reports/lab_report1_page_1.pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = default_pdf
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found: {pdf_path}")
        print(f"\nUsage: python {sys.argv[0]} <path_to_pdf>")
        print(f"Example: python {sys.argv[0]} {default_pdf}")
        sys.exit(1)
    
    test_end_to_end_integration(pdf_path)
