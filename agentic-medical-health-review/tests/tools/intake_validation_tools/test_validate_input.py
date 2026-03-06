"""
Test suite for the Health Input Validator Tool.
Imports the validation logic from the tools package and tests
all edge cases, boundary conditions, and invalid inputs.
"""

import pytest
from tools.src.intake_validation_tools.validate_input import validate_health_input as _validate_health_input

def validate_health_input(**kwargs):
    """
    Wrapper to allow the existing 37 kwarg-based test cases to test the new
    dictionary-based `user_input` signature expected by the Langchain Agent.
    """
    return _validate_health_input(kwargs)

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
            test_eval_id=1
        )
        
        assert result['is_valid'] is True
        assert result['validated_data'] is not None
        assert len(result['errors']) == 0
        assert result['validated_data']['user_id']['name'] == "John Doe"
        assert result['validated_data']['user_id']['age'] == 35
        assert result['validated_data']['consent_id'] == "CONSENT-123"
        assert result['validated_data']['test_eval_id'] == 1
    
    def test_valid_input_minimal_required_only(self):
        """Test validation with only required fields"""
        result = validate_health_input(
            name="Jane Smith",
            age=28,
            gender="Female",
            height_cm=165.0,
            weight_kg=60.0
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
            consent_id="CONSENT-456"
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

        )
        
        assert result['is_valid'] is False
        assert "age" in result['errors']


class TestValidateHealthInputGender:
    """Test gender field validation"""
    
    def test_valid_genders(self):
        """Test valid gender values (case insensitive)"""
        valid_genders = ["Male", "Female", "Other", "male", "female", "other"]
        
        for gender in valid_genders:
            result = validate_health_input(
                name="John Doe",
                age=30,
                gender=gender,
                height_cm=170.0,
                weight_kg=70.0,
    
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
