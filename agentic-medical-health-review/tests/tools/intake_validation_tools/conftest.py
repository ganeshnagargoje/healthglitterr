"""
Pytest configuration for automatic JSON report formatting
"""
import json
import os
import glob
from pathlib import Path


# Store the test directory
TEST_DIR = Path(__file__).parent


def pytest_sessionfinish(session, exitstatus):
    """
    Hook to automatically format any JSON report files after tests finish.
    This ensures all test_report*.json files are properly indented and readable.
    """
    # Find any test_report*.json files in the test directory
    # Pattern for test_report*.json, test_auto_format.json, etc.
    report_pattern = str(TEST_DIR / "test_*.json")
    report_files = glob.glob(report_pattern)
    
    for report_file in report_files:
        if os.path.exists(report_file):
            try:
                # Read the JSON (minified or not)
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Write it back with proper indentation (2 spaces)
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"\n[OK] JSON report formatted: {os.path.basename(report_file)}")
            except Exception as e:
                print(f"[WARNING] Could not format '{os.path.basename(report_file)}': {e}")
