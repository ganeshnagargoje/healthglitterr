"""
Consent Validation Tool

This tool validates user's explicit consent for health data processing.
It returns a failure and stops the process if consent is not granted.
"""

from typing import Optional, Dict, Any
import json
import argparse
import sys

def validate_consent(user_consent: Optional[str]) -> Dict[str, Any]:
    """
    Validates user's explicit consent for data processing.
    
    Args:
        user_consent: User's explicit consent (Yes/No)
    
    Returns:
        Dict containing:
            - is_valid: bool indicating if consent was granted
            - status: "Approved" or "Rejected"
            - error: Error message if rejected or invalid
    """
    result = {
        "is_valid": False,
        "status": "Rejected",
        "error": None
    }
    
    if user_consent is None:
        result["error"] = "Explicit user consent is required (Yes/No)"
        return result
    
    user_consent_normalized = str(user_consent).strip().lower()
    
    if user_consent_normalized not in ['yes', 'no']:
        result["error"] = "User consent must be 'Yes' or 'No'"
        return result
    
    if user_consent_normalized == 'no':
        result["error"] = "User has NOT given consent. Cannot proceed with data processing."
        return result
    
    # Consent is valid and "Yes"
    result["is_valid"] = True
    result["status"] = "Approved"
    return result

def collect_consent_interactive() -> str:
    """Collect consent via interactive prompt."""
    print("\n" + "=" * 80)
    print("MANDATORY USER CONSENT")
    print("=" * 80)
    print("⚠️  This is a REQUIRED field for data processing.")
    
    while True:
        consent = input("Do you give consent to process your health data? (Yes/No): ").strip()
        if consent.lower() in ['yes', 'no']:
            return consent
        else:
            print("    ✗ Please enter: Yes or No")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consent Validator")
    parser.add_argument("--consent", type=str, help="Consent value (Yes/No)")
    parser.add_argument("--json", type=str, help="JSON input containing 'user_consent'")
    args = parser.parse_args()

    try:
        consent_val = None
        
        if args.consent:
            consent_val = args.consent
            print(f"\n[*] Validating consent from CLI argument: {consent_val}")
        elif args.json:
            try:
                data = json.loads(args.json)
                consent_val = data.get('user_consent')
                print("\n[*] Validating consent from JSON input.")
            except json.JSONDecodeError:
                print("❌ Error: Invalid JSON provided.")
                sys.exit(1)
        else:
            consent_val = collect_consent_interactive()
            
        result = validate_consent(consent_val)
        
        print("\n" + "=" * 80)
        print("CONSENT VALIDATION RESULT")
        print("=" * 80)
        
        if result['is_valid']:
            print(f"\n✅ CONSENT GRANTED")
            print(f"   Status: {result['status']}")
        else:
            print(f"\n❌ CONSENT REJECTED")
            print(f"   Error: {result['error']}")
            # Standard behavior: Exit with error code if consent is denied
            sys.exit(1)
            
        print("\n" + "=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
