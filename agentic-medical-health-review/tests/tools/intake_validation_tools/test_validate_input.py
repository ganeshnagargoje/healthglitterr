"""
Health Input Validator Tool for Langchain Framework

This tool validates health input data including USER_ID and CONSENT_ID
against the health_input_contract.spec.json schema.
Lab reports are handled by a separate tool.
"""

from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator
import json
import os
from datetime import datetime
import uuid
import pytest


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


def load_user_registry() -> Dict[str, Any]:
    """
    Load user registry from JSON file.
    
    Returns:
        Dictionary mapping user_id to patient info
    """
    registry_path = "user_registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            return json.load(f)
    return {}


def save_user_registry(registry: Dict[str, Any]) -> None:
    """
    Save user registry to JSON file.
    
    Args:
        registry: User registry dictionary
    """
    with open("user_registry.json", 'w') as f:
        json.dump(registry, f, indent=2)


def check_existing_patient(name: str, age: int, gender: str) -> Optional[str]:
    """
    Check if patient already exists in registry.
    Uses exact match on name, age, and gender.
    
    Args:
        name: Patient name
        age: Patient age
        gender: Patient gender
    
    Returns:
        User ID if patient exists, None otherwise
    """
    registry = load_user_registry()
    
    for user_id, patient_info in registry.items():
        if (patient_info['name'].lower() == name.lower() and
            patient_info['age'] == age and
            patient_info['gender'].lower() == gender.lower()):
            return user_id
    
    return None


def generate_user_id() -> str:
    """
    Generate a unique User ID using UUID.
    
    Returns:
        Unique User ID string (format: USER-<uuid>)
    """
    return f"USER-{uuid.uuid4().hex[:12].upper()}"


def register_patient(user_id: str, name: str, age: int, gender: str, is_new: bool = True) -> None:
    """
    Register patient in user registry.
    
    Args:
        user_id: Unique user ID
        name: Patient name
        age: Patient age
        gender: Patient gender
        is_new: Whether this is a new patient registration
    """
    registry = load_user_registry()
    
    if user_id not in registry:
        registry[user_id] = {
            "name": name,
            "age": age,
            "gender": gender,
            "created_at": datetime.now().isoformat(),
            "records_count": 0
        }
    
    # Update records count
    registry[user_id]['records_count'] = registry[user_id].get('records_count', 0) + 1
    registry[user_id]['last_updated'] = datetime.now().isoformat()
    
    save_user_registry(registry)


def save_validation_to_json(result: Dict[str, Any], patient_data: Dict[str, Any]) -> Tuple[str, str, bool]:
    """
    Save validated patient data to JSON file with unique User ID.
    Checks for existing patients and reuses User ID if found.
    Creates timestamped history records under each User ID.
    
    Args:
        result: Validation result dictionary
        patient_data: Patient information dict with name, age, gender
    
    Returns:
        Tuple of (filepath, user_id, is_new_patient)
    """
    if not result['is_valid']:
        print("\n⚠️  Cannot save invalid data. Please fix validation errors first.")
        return None, None, None
    
    name = patient_data['name']
    age = patient_data['age']
    gender = patient_data['gender']
    
    # Check if patient already exists
    existing_user_id = check_existing_patient(name, age, gender)
    
    if existing_user_id:
        user_id = existing_user_id
        is_new_patient = False
    else:
        user_id = generate_user_id()
        is_new_patient = True
    
    # Register/update patient in registry
    register_patient(user_id, name, age, gender, is_new_patient)
    
    # Create user-specific directory
    output_dir = os.path.join("patient_data_exports", user_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate timestamped record filename (UNIQUE: USER_ID + TIMESTAMP)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]  # Include milliseconds for uniqueness
    filename = f"record_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Add User ID and timestamp metadata to the export
    export_data = {
        "user_id": user_id,
        "is_new_patient": is_new_patient,
        "metadata": {
            "export_timestamp": datetime.now().isoformat(),
            "validator_version": "2.0",
            "data_type": "patient_health_input",
            "record_unique_id": f"{user_id}_{timestamp}"
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
    
    return filepath, user_id, is_new_patient


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


# ============================================================================
# PYTEST TEST CASES
# ============================================================================

class TestValidateHealthInputBasic:
    """Test basic validation scenarios"""
    
    def test_valid_input_all_fields(self):
        """Test validation with all required and optional fields"""
        result = validate_health_input(
            name="John Doe",
            age=35,
            gender="Male",
            height_cm=180.5,
            weight_kg=75.0,
            consent_id="CONSENT-123",
            iso_language_id=1,
            language_desc="English",
            test_eval_id=1,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data'] is not None
        assert len(result['errors']) == 0
        assert result['validated_data']['user_id']['name'] == "John Doe"
        assert result['validated_data']['user_id']['age'] == 35
        assert result['validated_data']['consent_id'] == "CONSENT-123"
        assert result['validated_data']['test_eval_id'] == 1
        assert result['validated_data']['user_consent'] == "Yes"
    
    def test_valid_input_minimal_required_only(self):
        """Test validation with only required fields"""
        result = validate_health_input(
            name="Jane Smith",
            age=28,
            gender="Female",
            height_cm=165.0,
            weight_kg=60.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data'] is not None
        assert len(result['errors']) == 0
        assert "consent_id" not in result['validated_data']
        assert "iso_language_id" not in result['validated_data']['user_id']
        # Should have warning about missing consent_id
        assert any("consent_id" in w for w in result['warnings'])
    
    def test_valid_input_with_optional_consent_id(self):
        """Test validation with optional consent_id"""
        result = validate_health_input(
            name="Robert Johnson",
            age=45,
            gender="Male",
            height_cm=175.0,
            weight_kg=85.0,
            consent_id="CONSENT-456",
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data']['consent_id'] == "CONSENT-456"


class TestValidateHealthInputName:
    """Test name field validation"""
    
    def test_valid_names(self):
        """Test various valid name formats"""
        valid_names = [
            "John Doe",
            "Maria Garcia",
            "Dr. Jane Smith",
            "A",  # Single character
            "José María García",  # Special characters
        ]
        
        for name in valid_names:
            result = validate_health_input(
                name=name,
                age=30,
                gender="Male",
                height_cm=170.0,
                weight_kg=70.0,
                user_consent="Yes"
            )
            assert result['is_valid'] is True, f"Name '{name}' should be valid"
    
    def test_invalid_empty_name(self):
        """Test validation fails with empty name"""
        result = validate_health_input(
            name="",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "name" in result['errors']
        assert "empty" in result['errors']['name'].lower()
    
    def test_invalid_whitespace_only_name(self):
        """Test validation fails with whitespace-only name"""
        result = validate_health_input(
            name="   ",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "name" in result['errors']
    
    def test_invalid_name_too_long(self):
        """Test validation fails with name exceeding 100 characters"""
        long_name = "A" * 101
        result = validate_health_input(
            name=long_name,
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "name" in result['errors']
        assert "exceed" in result['errors']['name'].lower()


class TestValidateHealthInputAge:
    """Test age field validation"""
    
    def test_valid_ages(self):
        """Test various valid age values"""
        valid_ages = [0, 1, 18, 35, 65, 100, 150]
        
        for age in valid_ages:
            result = validate_health_input(
                name="John Doe",
                age=age,
                gender="Male",
                height_cm=170.0,
                weight_kg=70.0,
                user_consent="Yes"
            )
            assert result['is_valid'] is True, f"Age {age} should be valid"
    
    def test_invalid_negative_age(self):
        """Test validation fails with negative age"""
        result = validate_health_input(
            name="John Doe",
            age=-5,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "age" in result['errors']
    
    def test_invalid_age_exceeds_150(self):
        """Test validation fails with age exceeding 150"""
        result = validate_health_input(
            name="John Doe",
            age=151,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "age" in result['errors']


class TestValidateHealthInputGender:
    """Test gender field validation"""
    
    def test_valid_genders(self):
        """Test valid gender values (case insensitive)"""
        valid_genders = ["Male", "Female", "Other", "male", "female", "other", "MALE", "FEMALE"]
        
        for gender in valid_genders:
            result = validate_health_input(
                name="John Doe",
                age=30,
                gender=gender,
                height_cm=170.0,
                weight_kg=70.0,
                user_consent="Yes"
            )
            assert result['is_valid'] is True, f"Gender '{gender}' should be valid"
            # Verify normalization
            assert result['validated_data']['user_id']['gender'] in ["Male", "Female", "Other"]
    
    def test_invalid_gender(self):
        """Test validation fails with invalid gender"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Unknown",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "gender" in result['errors']


class TestValidateHealthInputHeight:
    """Test height field validation"""
    
    def test_valid_heights(self):
        """Test various valid height values"""
        valid_heights = [50.0, 120.5, 170.0, 200.0, 220.0]
        
        for height in valid_heights:
            result = validate_health_input(
                name="John Doe",
                age=30,
                gender="Male",
                height_cm=height,
                weight_kg=70.0,
                user_consent="Yes"
            )
            assert result['is_valid'] is True, f"Height {height} should be valid"
    
    def test_invalid_height_zero(self):
        """Test validation fails with zero height"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "height_cm" in result['errors']
    
    def test_invalid_height_negative(self):
        """Test validation fails with negative height"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=-170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "height_cm" in result['errors']


class TestValidateHealthInputWeight:
    """Test weight field validation"""
    
    def test_valid_weights(self):
        """Test various valid weight values"""
        valid_weights = [2.5, 50.0, 70.0, 100.0, 150.0]
        
        for weight in valid_weights:
            result = validate_health_input(
                name="John Doe",
                age=30,
                gender="Male",
                height_cm=170.0,
                weight_kg=weight,
                user_consent="Yes"
            )
            assert result['is_valid'] is True, f"Weight {weight} should be valid"
    
    def test_invalid_weight_zero(self):
        """Test validation fails with zero weight"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "weight_kg" in result['errors']
    
    def test_invalid_weight_negative(self):
        """Test validation fails with negative weight"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=-70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "weight_kg" in result['errors']


class TestValidateHealthInputConsent:
    """Test consent field validation"""
    
    def test_consent_yes_variations(self):
        """Test consent acceptance with various formats"""
        variations = ["Yes", "YES", "yes", "YeS", " Yes ", "  YES  "]
        
        for consent in variations:
            result = validate_health_input(
                name="John Doe",
                age=30,
                gender="Male",
                height_cm=170.0,
                weight_kg=70.0,
                user_consent=consent
            )
            assert result['is_valid'] is True, f"Consent '{consent}' should be valid"
            assert result['validated_data']['user_consent'] == "Yes"
    
    def test_consent_no_rejection(self):
        """Test consent rejection"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="No"
        )
        
        assert result['is_valid'] is False
        assert "user_consent" in result['errors']
        assert "NOT given consent" in result['errors']['user_consent']
    
    def test_consent_missing(self):
        """Test validation fails when consent is missing"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent=None
        )
        
        assert result['is_valid'] is False
        assert "user_consent" in result['errors']
        assert "required" in result['errors']['user_consent'].lower()
    
    def test_consent_invalid_value(self):
        """Test validation fails with invalid consent value"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Maybe"
        )
        
        assert result['is_valid'] is False
        assert "user_consent" in result['errors']
        assert "Yes" in result['errors']['user_consent'] or "No" in result['errors']['user_consent']


class TestValidateHealthInputConsentID:
    """Test consent_id field validation"""
    
    def test_valid_consent_id(self):
        """Test with valid consent_id"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            consent_id="CONSENT-12345",
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data']['consent_id'] == "CONSENT-12345"
    
    def test_consent_id_optional(self):
        """Test that consent_id is optional but generates warning"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            consent_id=None,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert "consent_id" not in result['validated_data']
        assert len(result['warnings']) > 0
        assert any("consent_id" in w for w in result['warnings'])
    
    def test_consent_id_empty_string(self):
        """Test validation fails with empty consent_id"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            consent_id="",
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "consent_id" in result['errors']
    
    def test_consent_id_whitespace_only(self):
        """Test validation fails with whitespace-only consent_id"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            consent_id="   ",
            user_consent="Yes"
        )
        
        assert result['is_valid'] is False
        assert "consent_id" in result['errors']


class TestValidateHealthInputOptionalFields:
    """Test optional fields"""
    
    def test_iso_language_id_valid(self):
        """Test with valid ISO language ID"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            iso_language_id=1,
            language_desc="English",
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data']['user_id']['iso_language_id'] == 1
        assert result['validated_data']['user_id']['language_desc'] == "English"
    
    def test_test_eval_id_valid(self):
        """Test with valid test evaluation ID"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            test_eval_id=99,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data']['test_eval_id'] == 99
    
    def test_all_optional_fields(self):
        """Test with all optional fields provided"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            consent_id="CONSENT-123",
            iso_language_id=2,
            language_desc="Spanish",
            test_eval_id=5,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data']['consent_id'] == "CONSENT-123"
        assert result['validated_data']['user_id']['iso_language_id'] == 2
        assert result['validated_data']['user_id']['language_desc'] == "Spanish"
        assert result['validated_data']['test_eval_id'] == 5


class TestValidateHealthInputEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_max_age_boundary(self):
        """Test with maximum allowed age"""
        result = validate_health_input(
            name="John Doe",
            age=150,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data']['user_id']['age'] == 150
    
    def test_zero_age(self):
        """Test with age zero (newborn)"""
        result = validate_health_input(
            name="Baby",
            age=0,
            gender="Male",
            height_cm=50.0,
            weight_kg=3.5,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data']['user_id']['age'] == 0
    
    def test_decimal_values_for_biometrics(self):
        """Test decimal values for height and weight"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.75,
            weight_kg=70.25,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert result['validated_data']['user_id']['height_cm'] == 170.75
        assert result['validated_data']['user_id']['weight_kg'] == 70.25
    
    def test_name_with_special_characters(self):
        """Test name with special characters"""
        result = validate_health_input(
            name="José María O'Neill-García",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert result['is_valid'] is True
        assert "José" in result['validated_data']['user_id']['name']


class TestValidateHealthInputMultipleErrors:
    """Test scenarios with multiple validation errors"""
    
    def test_multiple_errors(self):
        """Test validation with multiple errors"""
        result = validate_health_input(
            name="",  # Invalid: empty
            age=200,  # Invalid: exceeds 150
            gender="Unknown",  # Invalid
            height_cm=-170.0,  # Invalid: negative
            weight_kg=0,  # Invalid: zero
            user_consent="Maybe"  # Invalid
        )
        
        assert result['is_valid'] is False
        assert len(result['errors']) > 0
    
    def test_mixed_valid_invalid(self):
        """Test with some valid and some invalid fields"""
        result = validate_health_input(
            name="John Doe",  # Valid
            age=200,  # Invalid
            gender="Male",  # Valid
            height_cm=170.0,  # Valid
            weight_kg=70.0,  # Valid
            user_consent="Yes"  # Valid
        )
        
        assert result['is_valid'] is False
        assert "age" in result['errors']


class TestValidateHealthInputResponseStructure:
    """Test response structure and format"""
    
    def test_response_structure_on_success(self):
        """Test that successful response has correct structure"""
        result = validate_health_input(
            name="John Doe",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "validated_data" in result
        assert "errors" in result
        assert "warnings" in result
        assert isinstance(result['is_valid'], bool)
        assert isinstance(result['errors'], dict)
        assert isinstance(result['warnings'], list)
    
    def test_response_structure_on_failure(self):
        """Test that failed response has correct structure"""
        result = validate_health_input(
            name="",
            age=30,
            gender="Male",
            height_cm=170.0,
            weight_kg=70.0,
            user_consent="Yes"
        )
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert result['is_valid'] is False
        assert isinstance(result['errors'], dict)
        assert len(result['errors']) > 0



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
            json_filepath, user_id, is_new = save_validation_to_json(result, {
                'name': user_input['name'],
                'age': user_input['age'],
                'gender': user_input['gender']
            })
            
            print("\n" + "=" * 80)
            print("DATA EXPORTED & REGISTERED")
            print("=" * 80)
            
            if is_new:
                print(f"\n✅ NEW PATIENT REGISTERED")
                print(f"   User ID: {user_id}")
                print(f"   Patient: {user_input['name']} (Age: {user_input['age']}, Gender: {user_input['gender']})")
            else:
                print(f"\n✅ EXISTING PATIENT FOUND")
                print(f"   User ID: {user_id}")
                print(f"   New record added to patient history")
            
            print(f"\n📁 Record saved to: {json_filepath}")
            print(f"   History Location: patient_data_exports/{user_id}/")
            print("\nThis record has been added to the patient's permanent history.")
            print("All records are uniquely identified by USER_ID + TIMESTAMP.")
            print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
