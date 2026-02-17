"""
Health Input Validator Tool for Langchain Framework

This tool validates health input data including USER_ID and CONSENT_ID
against the health_input_contract.spec.json schema.
Lab reports are handled by a separate tool.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import json
import os
from datetime import datetime


class UserIDSchema(BaseModel):
    """Schema for USER_ID field validation"""
    name: str = Field(..., description="Patient's full name")
    age: int = Field(..., ge=0, le=150, description="Patient's age in years")
    gender: str = Field(..., description="Patient's gender (Male/Female/Other)")
    height_cm: float = Field(..., gt=0, description="Patient's height in centimeters")
    weight_kg: float = Field(..., gt=0, description="Patient's weight in kilograms")
    iso_language_id: Optional[int] = Field(None, description="ISO language code")
    language_desc: Optional[str] = Field(None, description="Language description")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        if len(v) > 100:
            raise ValueError("Name cannot exceed 100 characters")
        return v.strip()

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        valid_genders = {'Male', 'Female', 'Other', 'male', 'female', 'other'}
        if v not in valid_genders:
            raise ValueError(f"Gender must be one of {valid_genders}")
        return v.capitalize()


class HealthInputValidationRequest(BaseModel):
    """Schema for health input validation request"""
    user_id: Dict[str, Any] = Field(..., description="User identification and demographics")
    consent_id: Optional[str] = Field(None, description="Consent identifier for data processing")
    test_eval_id: Optional[int] = Field(None, description="Test evaluation identifier")

    @field_validator('consent_id')
    @classmethod
    def validate_consent_id(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Consent ID cannot be an empty string")
        if v is not None and len(v) > 100:
            raise ValueError("Consent ID cannot exceed 100 characters")
        return v


class ValidationResult(BaseModel):
    """Schema for validation result"""
    is_valid: bool
    validated_data: Optional[Dict[str, Any]] = None
    errors: Dict[str, str] = {}
    warnings: list = []

#@tool
def validate_health_input(
    name: str,
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    consent_id: Optional[str] = None,
    iso_language_id: Optional[int] = None,
    language_desc: Optional[str] = None,
    test_eval_id: Optional[int] = None,
    user_consent: str = None,
) -> Dict[str, Any]:
    """
    Validates health input data for USER_ID and CONSENT_ID fields.
    
    This tool validates patient demographics (USER_ID) and consent information
    against the health input contract schema. Lab reports are handled separately.
    
    Args:
        name: Patient's full name
        age: Patient's age in years (0-150)
        gender: Patient's gender (Male/Female/Other)
        height_cm: Patient's height in centimeters
        weight_kg: Patient's weight in kilograms
        consent_id: Optional consent identifier for data processing
        iso_language_id: Optional ISO language code
        language_desc: Optional language description
        test_eval_id: Optional test evaluation identifier
        user_consent: User's explicit consent for data processing (Yes/No) - MANDATORY
    
    Returns:
        Dict containing:
            - is_valid: bool indicating if validation passed
            - validated_data: Validated input data if successful
            - errors: Dict of validation errors if any
            - warnings: List of validation warnings
    
    Raises:
        ValueError: If required fields are missing or invalid
    """
    
    result = {
        "is_valid": False,
        "validated_data": None,
        "errors": {},
        "warnings": []
    }
    
    try:
        # Validate USER_ID fields
        user_id_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
        }
        
        if iso_language_id is not None:
            user_id_data["iso_language_id"] = iso_language_id
        if language_desc is not None:
            user_id_data["language_desc"] = language_desc
        
        # Create and validate user_id
        validated_user_id = UserIDSchema(**user_id_data)
        
        # Validate CONSENT_ID if provided
        if consent_id is None:
            result["warnings"].append("consent_id is not provided. User will need explicit consent.")
        else:
            if not isinstance(consent_id, str):
                result["errors"]["consent_id"] = "Consent ID must be a string"
                return result
            if len(consent_id.strip()) == 0:
                result["errors"]["consent_id"] = "Consent ID cannot be empty"
                return result
        
        # Validate user consent (Yes/No)
        if user_consent is None:
            result["errors"]["user_consent"] = "Explicit user consent is required (Yes/No)"
            return result
        
        user_consent_normalized = user_consent.strip().lower()
        if user_consent_normalized not in ['yes', 'no']:
            result["errors"]["user_consent"] = "User consent must be 'Yes' or 'No'"
            return result
        
        if user_consent_normalized == 'no':
            result["errors"]["user_consent"] = "User has NOT given consent. Cannot proceed with data processing."
            return result
        
        # Build validated data
        validated_data = {
            "user_id": {
                "name": validated_user_id.name,
                "age": validated_user_id.age,
                "gender": validated_user_id.gender,
                "height_cm": validated_user_id.height_cm,
                "weight_kg": validated_user_id.weight_kg,
            }
        }
        
        if validated_user_id.iso_language_id:
            validated_data["user_id"]["iso_language_id"] = validated_user_id.iso_language_id
        if validated_user_id.language_desc:
            validated_data["user_id"]["language_desc"] = validated_user_id.language_desc
        
        if consent_id:
            validated_data["consent_id"] = consent_id.strip()
        
        # Add user consent status
        validated_data["user_consent"] = user_consent_normalized.capitalize()
        
        if test_eval_id is not None:
            validated_data["test_eval_id"] = test_eval_id
        
        result["is_valid"] = True
        result["validated_data"] = validated_data
        
    except ValueError as e:
        error_str = str(e)
        if "name" in error_str.lower():
            result["errors"]["name"] = error_str
        elif "age" in error_str.lower():
            result["errors"]["age"] = error_str
        elif "gender" in error_str.lower():
            result["errors"]["gender"] = error_str
        elif "height" in error_str.lower():
            result["errors"]["height_cm"] = error_str
        elif "weight" in error_str.lower():
            result["errors"]["weight_kg"] = error_str
        else:
            result["errors"]["validation"] = error_str
    
    except Exception as e:
        result["errors"]["unexpected_error"] = f"Unexpected validation error: {str(e)}"
    
    return result


def collect_patient_input() -> Dict[str, Any]:
    """
    Collect patient health input from user interactively.
    
    Returns:
        Dictionary containing all patient input data
    """
    print("\n" + "=" * 80)
    print("PATIENT HEALTH INPUT FORM")
    print("=" * 80)
    print("\nPlease provide the following information:\n")
    
    # Collect USER_ID information (required)
    print("--- USER IDENTIFICATION ---")
    name = input("1. Patient Full Name: ").strip()
    
    while True:
        try:
            age = int(input("2. Patient Age (0-150): "))
            break
        except ValueError:
            print("   ✗ Please enter a valid number for age")
    
    while True:
        gender = input("3. Gender (Male/Female/Other): ").strip()
        if gender.lower() in ['male', 'female', 'other']:
            break
        else:
            print("   ✗ Please enter: Male, Female, or Other")
    
    while True:
        try:
            height_cm = float(input("4. Height (cm): "))
            break
        except ValueError:
            print("   ✗ Please enter a valid number for height")
    
    while True:
        try:
            weight_kg = float(input("5. Weight (kg): "))
            break
        except ValueError:
            print("   ✗ Please enter a valid number for weight")
    
    # Collect optional language information
    print("\n--- OPTIONAL LANGUAGE INFORMATION ---")
    iso_language_id_input = input("6. ISO Language ID (optional, press Enter to skip): ").strip()
    iso_language_id = int(iso_language_id_input) if iso_language_id_input else None
    
    language_desc = input("7. Language Description (optional, press Enter to skip): ").strip()
    language_desc = language_desc if language_desc else None
    
    # Collect CONSENT_ID
    print("\n--- CONSENT INFORMATION ---")
    consent_id = input("8. Consent ID (optional, press Enter to skip): ").strip()
    consent_id = consent_id if consent_id else None
    
    # Collect test evaluation ID
    test_eval_id_input = input("9. Test Evaluation ID (optional, press Enter to skip): ").strip()
    test_eval_id = int(test_eval_id_input) if test_eval_id_input else None
    
    # Collect MANDATORY user consent
    print("\n--- MANDATORY USER CONSENT ---")
    print("⚠️  This is a REQUIRED field")
    while True:
        user_consent = input("10. Do you give consent to process your health data? (Yes/No): ").strip()
        if user_consent.lower() in ['yes', 'no']:
            break
        else:
            print("    ✗ Please enter: Yes or No")
    
    # Return collected data
    user_input = {
        "name": name,
        "age": age,
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "iso_language_id": iso_language_id,
        "language_desc": language_desc,
        "consent_id": consent_id,
        "test_eval_id": test_eval_id,
        "user_consent": user_consent
    }
    
    return user_input


def display_input_summary(user_input: Dict[str, Any]) -> None:
    """Display collected input for user review"""
    print("\n" + "=" * 80)
    print("INPUT SUMMARY - PLEASE REVIEW")
    print("=" * 80)
    print("\nPatient Information:")
    print(f"  Name:               {user_input['name']}")
    print(f"  Age:                {user_input['age']} years")
    print(f"  Gender:             {user_input['gender']}")
    print(f"  Height:             {user_input['height_cm']} cm")
    print(f"  Weight:             {user_input['weight_kg']} kg")
    
    if user_input['iso_language_id']:
        print(f"  ISO Language ID:    {user_input['iso_language_id']}")
    if user_input['language_desc']:
        print(f"  Language:           {user_input['language_desc']}")
    if user_input['consent_id']:
        print(f"  Consent ID:         {user_input['consent_id']}")
    if user_input['test_eval_id']:
        print(f"  Test Eval ID:       {user_input['test_eval_id']}")
    print(f"  User Consent:        {user_input['user_consent']}")


def save_validation_to_json(result: Dict[str, Any], patient_name: str = None) -> str:
    """
    Save validated patient data to JSON file.
    
    Args:
        result: Validation result dictionary
        patient_name: Patient name for filename (optional)
    
    Returns:
        Path to saved JSON file
    """
    if not result['is_valid']:
        print("\n⚠️  Cannot save invalid data. Please fix validation errors first.")
        return None
    
    # Create output directory if it doesn't exist
    output_dir = "patient_data_exports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_name = patient_name.replace(" ", "_") if patient_name else "patient"
    filename = f"patient_health_input_{sanitized_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Add metadata to the export
    export_data = {
        "metadata": {
            "export_timestamp": datetime.now().isoformat(),
            "validator_version": "1.0",
            "data_type": "patient_health_input"
        },
        "validation_status": {
            "is_valid": result['is_valid'],
            "errors": result['errors'],
            "warnings": result['warnings']
        },
        "data": result['validated_data']
    }
    
    # Save to JSON file
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    return filepath


def display_validation_result(result: Dict[str, Any]) -> None:
    """Display validation result in a user-friendly format"""
    print("\n" + "=" * 80)
    print("VALIDATION RESULT")
    print("=" * 80)
    
    if result['is_valid']:
        print("\n✅ VALIDATION PASSED - Data is valid and ready for processing")
        print("\nValidated Data:")
        print(json.dumps(result['validated_data'], indent=2))
    else:
        print("\n❌ VALIDATION FAILED - Please correct the following errors:")
        print("\nErrors:")
        for field, error in result['errors'].items():
            print(f"  • {field}: {error}")
    
    if result['warnings']:
        print("\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"  • {warning}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        # Collect patient input interactively
        user_input = collect_patient_input()
        
        # Display what was collected for review
        display_input_summary(user_input)
        
        # Validate the collected input
        result = validate_health_input(
            name=user_input['name'],
            age=user_input['age'],
            gender=user_input['gender'],
            height_cm=user_input['height_cm'],
            weight_kg=user_input['weight_kg'],
            consent_id=user_input.get('consent_id'),
            iso_language_id=user_input.get('iso_language_id'),
            language_desc=user_input.get('language_desc'),
            test_eval_id=user_input.get('test_eval_id'),
            user_consent=user_input['user_consent']
        )
        
        # Display validation result
        display_validation_result(result)
        
        # Save to JSON if validation passed
        if result['is_valid']:
            json_filepath = save_validation_to_json(result, patient_name=user_input['name'])
            print("\n" + "=" * 80)
            print("DATA EXPORTED")
            print("=" * 80)
            print(f"✅ Patient data saved to: {json_filepath}")
            print("\nThis file can now be used by other agent tools for further processing.")
            print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
