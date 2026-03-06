"""
Pytest configuration for automatic JSON report formatting.
Intercepts pytest-json-report to rewrite the raw output into a clean,
human-readable schema that matches the custom validation tool report.
"""
import os
import re
from datetime import datetime
from pathlib import Path


def pytest_json_modifyreport(json_report):
    """
    Hook called by pytest-json-report before saving the JSON to disk.
    Allows us to completely restructure the output dictionary.
    """
    
    # Calculate totals
    passed = json_report.get("summary", {}).get("passed", 0)
    failed = json_report.get("summary", {}).get("failed", 0)
    total = passed + failed
    pass_rate = f"{(passed / total * 100):.1f}%" if total else "N/A"
    overall_status = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    # Build the custom clear array of test cases
    test_cases = []
    
    for test in json_report.get("tests", []):
        nodeid = test.get("nodeid", "")
        outcome = test.get("outcome", "unknown").upper()
        
        # Determine PASS/FAIL (pytest uses 'passed', 'failed', 'skipped', etc.)
        status = "PASS" if outcome == "PASSED" else ("FAIL" if outcome == "FAILED" else outcome)

        # Extract Class Name (Category) and Test Name
        parts = nodeid.split("::")
        category = parts[-2].replace("TestValidateHealthInput", "") if len(parts) >= 3 else "Unknown"
        
        # Try to parse docstring from metadata (if available) or format test name
        test_name = parts[-1]
        description = test_name.replace("test_", "").replace("_", " ").capitalize()

        test_cases.append({
            "id": test_name,
            "category": category,
            "description": description,
            "status": status,
            "duration_sec": round(test.get("setup", {}).get("duration", 0) + test.get("call", {}).get("duration", 0), 4)
        })

    # ── Completely overwrite the dictionary passed by pytest ──
    json_report.clear()
    
    json_report["report_metadata"] = {
        "generated_at": datetime.now().isoformat(),
        "tool": "test_validate_input.py",
        "total_cases": total,
        "passed": passed,
        "failed": failed,
    }
    
    json_report["summary"] = {
        "pass_rate": pass_rate,
        "overall_status": overall_status,
    }
    
    json_report["test_cases"] = test_cases
