"""
Test LabReportParser with Real Files

Use this script to test OCR extraction on your own lab report files.
Outputs structured JSON format matching lab_report_extraction.spec.json
"""

import sys
from pathlib import Path
import argparse
import json

# Add the tools/src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tools" / "src" / "document_data_extraction_tools" / "lab_report_parser"))

from lab_report_parser import LabReportParser, extract_text_from_lab_report, extract_structured_lab_data
from file_validator import FileValidator


def test_real_file(file_path, save_output=False, output_format='json'):
    """
    Test OCR extraction on a real file.
    
    Args:
        file_path: Path to the file to test
        save_output: If True, saves extracted data to a file
        output_format: 'json' for structured output, 'text' for raw text
    """
    print("\n" + "="*70)
    print("Testing LabReportParser with Real File")
    print("="*70)
    
    # Step 1: Validate file
    print(f"\n📄 File: {file_path}")
    
    is_valid, error = FileValidator.validate_file(file_path)
    if not is_valid:
        print(f"❌ Error: {error}")
        return
    
    print("✓ File exists")
    
    # Step 2: Check file type
    file_type = FileValidator.get_file_type(file_path)
    print(f"✓ File type: {file_type}")
    
    if file_type == "unsupported":
        print("❌ Unsupported file format")
        print("   Supported formats: PDF, PNG, JPG, JPEG, BMP, TIFF, TIF")
        return
    
    # Step 3: Extract data
    print("\n🔍 Extracting data...")
    print("   (This may take 10-15 seconds on first run)")
    print("   Using LLM for structured extraction")
    
    try:
        if output_format == 'json':
            # Extract structured data using LLM
            result = extract_structured_lab_data(file_path)
            
            print("✓ Extraction complete!")
            
            # Display raw extracted text first
            print("\n" + "="*70)
            print("Raw Extracted Text (OCR Output)")
            print("="*70)
            if result['raw_text'].strip():
                print(result['raw_text'])
            else:
                print("(No text extracted)")
            print("="*70)
            
            # Display structured results
            print("\n" + "="*70)
            print("Extraction Results (Structured JSON)")
            print("="*70)
            print(f"Status: {result['metadata']['extraction_status']}")
            print(f"Extraction method: {result['metadata'].get('extraction_method', 'llm')}")
            if 'model' in result['metadata']:
                print(f"Model: {result['metadata']['model']}")
            print(f"Tests found: {result['metadata']['total_tests_found']}")
            print(f"Raw text length: {len(result['raw_text'])} characters")
            
            if result['tests']:
                print("\n" + "-"*70)
                print("Extracted Lab Tests:")
                print("-"*70)
                for i, test in enumerate(result['tests'], 1):
                    print(f"\nTest {i}:")
                    print(f"  Name: {test['test_name']}")
                    print(f"  Value: {test['test_value']}")
                    print(f"  Unit: {test['unit']}")
                    print(f"  Reference Range: {test['reference_range']}")
            else:
                print("\n⚠ No structured test data found")
                print("   Showing raw extracted text instead:")
                print("\n" + "-"*70)
                print(result['raw_text'][:500])  # Show first 500 chars
                if len(result['raw_text']) > 500:
                    print("...")
                print("-"*70)
            
            # Save to JSON file if requested
            if save_output:
                output_file = Path(file_path).stem + "_extracted.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Saved to: {output_file}")
                
        else:  # text format
            # Extract raw text only
            text = extract_text_from_lab_report(file_path)
            
            print("✓ Extraction complete!")
            
            # Display results
            print("\n" + "="*70)
            print("Extraction Results (Raw Text)")
            print("="*70)
            print(f"Characters extracted: {len(text)}")
            print(f"Lines: {len(text.splitlines())}")
            print(f"Words (approx): {len(text.split())}")
            
            if text.strip():
                print("\n" + "-"*70)
                print("Extracted Text:")
                print("-"*70)
                print(text)
                print("-"*70)
                
                # Save to file if requested
                if save_output:
                    output_file = Path(file_path).stem + "_extracted.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"\n💾 Saved to: {output_file}")
            else:
                print("\n⚠ Warning: No text was extracted")
                print("   Possible reasons:")
                print("   - Image has no text")
                print("   - Text is too small or unclear")
                print("   - Low contrast between text and background")
                print("   - Image quality is poor")
            
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Test LabReportParser with your own files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract structured JSON with LLM
  python test_real_file.py my_lab_report.pdf
  
  # Extract and save to JSON file
  python test_real_file.py my_lab_report.jpg --save
  
  # Extract raw text only
  python test_real_file.py report.pdf --format text
  
  # Full path with spaces
  python test_real_file.py "C:/path/to/report.pdf" --save

Supported formats:
  - PDF files (.pdf)
  - Images (.png, .jpg, .jpeg, .bmp, .tiff, .tif)

Output formats:
  - json: Structured data with test_name, test_value, unit, reference_range (uses LLM)
  - text: Raw extracted text
        """
    )
    
    parser.add_argument(
        'file_path',
        help='Path to the lab report file (PDF or image)'
    )
    
    parser.add_argument(
        '--save', '-s',
        action='store_true',
        help='Save extracted data to a file (.json or .txt depending on format)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'text'],
        default='json',
        help='Output format: json (structured with LLM) or text (raw). Default: json'
    )
    
    args = parser.parse_args()
    
    # Test the file
    test_real_file(args.file_path, args.save, args.format)


if __name__ == "__main__":
    # Check if file path was provided as argument
    if len(sys.argv) > 1:
        main()
    else:
        # Interactive mode
        print("\n" + "="*70)
        print("Test LabReportParser with Real Files")
        print("="*70)
        print("\nThis script will extract data from your lab report files.")
        print("\nSupported formats:")
        print("  - PDF files (.pdf)")
        print("  - Images (.png, .jpg, .jpeg, .bmp, .tiff, .tif)")
        
        print("\n" + "-"*70)
        file_path = input("\nEnter the path to your file: ").strip().strip('"').strip("'")
        
        if not file_path:
            print("❌ No file path provided")
            sys.exit(1)
        
        format_choice = input("Output format (json/text) [json]: ").strip().lower() or 'json'
        if format_choice not in ['json', 'text']:
            format_choice = 'json'
        
        save_choice = input("Save extracted data to file? (y/n): ").strip().lower()
        save_output = save_choice in ['y', 'yes']
        
        test_real_file(file_path, save_output, format_choice)
