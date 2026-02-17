#!/usr/bin/env python3
"""
Test extraction with sample OCR text (bypassing PaddleOCR issues)

This demonstrates the LLM extraction working with realistic lab report text.
"""

import sys
import json
from pathlib import Path

# Add the tools/src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tools" / "src" / "document_data_extraction_tools"))

from llm_structured_extractor import extract_with_llm

# Realistic sample OCR text from a lab report
sample_text = """
MEDICAL LABORATORY REPORT

Patient: John Doe
DOB: 01/15/1980
Date Collected: 2024-02-15
Report Date: 2024-02-16

COMPLETE BLOOD COUNT (CBC)

Test Name                Result      Unit        Reference Range
------------------------------------------------------------------------
Hemoglobin              14.5        g/dL        13.5-17.5
Hematocrit              42.0        %           38.0-50.0
RBC Count               4.8         M/uL        4.5-5.5
WBC Count               7.2         K/uL        4.5-11.0
Platelet Count          250         K/uL        150-400

CHEMISTRY PANEL

Glucose                 95          mg/dL       70-100
BUN                     18          mg/dL       7-20
Creatinine              1.0         mg/dL       0.7-1.3
Sodium                  140         mmol/L      136-145
Potassium               4.2         mmol/L      3.5-5.0
Chloride                102         mmol/L      98-107

LIPID PANEL

Cholesterol, Total      185         mg/dL       <200
HDL Cholesterol         55          mg/dL       >40
LDL Cholesterol         110         mg/dL       <130
Triglycerides           100         mg/dL       <150

All results are within normal limits.

Reviewed by: Dr. Smith, MD
"""

def main():
    print("="*80)
    print("Lab Report Extraction Test - LLM Method")
    print("="*80)
    
    print("\n📄 Sample OCR Text (simulating PDF extraction):")
    print("-"*80)
    print(sample_text[:500] + "..." if len(sample_text) > 500 else sample_text)
    print("-"*80)
    
    print("\n🤖 Extracting structured data with LLM (gpt-4o-mini)...")
    print("   This may take 5-10 seconds...")
    
    try:
        # Extract using LLM
        result = extract_with_llm(
            raw_text=sample_text,
            file_path="sample_lab_report.txt",
            model_name="gpt-4o-mini"
        )
        
        print("✓ Extraction complete!")
        
        # Display raw text
        print("\n" + "="*80)
        print("Raw Extracted Text (OCR Output)")
        print("="*80)
        print(sample_text)
        print("="*80)
        
        # Display results
        print("\n" + "="*80)
        print("Extraction Results (Structured JSON)")
        print("="*80)
        print(f"Status: {result['metadata']['extraction_status']}")
        print(f"Extraction method: {result['metadata'].get('extraction_method', 'llm')}")
        print(f"Model: {result['metadata'].get('model', 'N/A')}")
        print(f"Tests found: {result['metadata']['total_tests_found']}")
        print(f"Raw text length: {len(result['raw_text'])} characters")
        
        if result['tests']:
            print("\n" + "-"*80)
            print("Extracted Lab Tests:")
            print("-"*80)
            for i, test in enumerate(result['tests'], 1):
                print(f"\n{i}. {test['test_name']}")
                print(f"   Value: {test['test_value']}")
                print(f"   Unit: {test['unit']}")
                print(f"   Reference Range: {test['reference_range']}")
            
            # Save to JSON file
            output_file = "sample_lab_report_extracted.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved to: {output_file}")
            
            print("\n" + "="*80)
            print("✅ SUCCESS!")
            print("="*80)
            print(f"\nExtracted {len(result['tests'])} lab tests successfully.")
            print("The LLM-based extraction is working correctly!")
            
            return True
        else:
            print("\n⚠ No tests extracted")
            if 'error_message' in result['metadata']:
                print(f"   Error: {result['metadata']['error_message']}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
