# How to Use health_input_validator_standalone as an Agent Tool

## Quick Summary

You have a **standalone Python validator** that takes health input and returns validation results. Here's how to use it in your agent:

---

## 🎯 The Simplest Approach (Recommended)

### Step 1: Import the validator
```python
from health_input_validator_standalone import validate_health_input
```

### Step 2: Use it in your agent
```python
# When your agent needs to validate health input:
result = validate_health_input(
    name="Joe Smith",
    age=42,
    gender="Male",
    height_cm=172,
    weight_kg=86,
    consent_id="CONSENT-2026-001"
)

# Check the result
if result['is_valid']:
    validated_data = result['validated_data']
    # Continue processing
else:
    errors = result['errors']
    # Handle validation errors
```

### Step 3: That's it! ✓
No LLM required. No Langchain required. Just pure Python.

---

## How It Works

```
Your Agent
    ↓
    calls: validate_health_input(name, age, gender, height_cm, weight_kg, consent_id...)
    ↓
    Returns: {
        "is_valid": True/False,
        "validated_data": {...sanitized data...},
        "errors": {...validation errors...},
        "warnings": [...messages...]
    }
    ↓
Your Agent continues
```

---

## 3 Ways to Use It

### Way 1: Direct Function Call (Simplest)
```python
from health_input_validator_standalone import validate_health_input

# Just call it like a normal function
result = validate_health_input(
    name="John Doe",
    age=35,
    gender="Male",
    height_cm=180,
    weight_kg=75,
    consent_id="CONSENT-123"
)

print(result['is_valid'])  # True or False
print(result['validated_data'])  # Cleaned data
print(result['errors'])  # Any errors
print(result['warnings'])  # Any warnings
```

**Best for:** Simple, direct validation without Langchain

---

### Way 2: Langchain Tool Wrapper (With Langchain)
If you have Langchain installed (`pip install langchain-core`):

```python
from langchain_core.tools import Tool
from health_input_validator_standalone import validate_health_input

# Create a Langchain tool
validator_tool = Tool.from_function(
    func=validate_health_input,
    name="validate_health_input",
    description="Validates patient health input (name, age, gender, height, weight, consent)"
)

# Add to your agent's tools list
tools = [validator_tool, other_tools...]

# Your Langchain agent will now have access to this tool
# It will call it automatically when needed
```

**Best for:** If you're using Langchain agents

---

### Way 3: Wrap with @tool Decorator (With Langchain)
```python
from langchain_core.tools import tool
from health_input_validator_standalone import validate_health_input

@tool
def validate_patient_health(
    name: str,
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    consent_id: str = None,
):
    """Validates patient health data"""
    return validate_health_input(
        name=name,
        age=age,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        consent_id=consent_id
    )

# Now use validate_patient_health in your agent
tools = [validate_patient_health, other_tools...]
```

**Best for:** Creating custom tool with additional logic

---

## Input Parameters

| Parameter | Type | Required | Range/Rules |
|-----------|------|----------|-------------|
| `name` | string | ✓ | 1-100 chars |
| `age` | integer | ✓ | 0-150 |
| `gender` | string | ✓ | Male/Female/Other |
| `height_cm` | float | ✓ | > 0 |
| `weight_kg` | float | ✓ | > 0 |
| `consent_id` | string | ✗ | ≤100 chars |
| `iso_language_id` | integer | ✗ | > 0 |
| `language_desc` | string | ✗ | any |
| `test_eval_id` | integer | ✗ | ≥ 0 |

---

## Output Format

### When Valid ✓
```python
{
    "is_valid": True,
    "validated_data": {
        "user_id": {
            "name": "Joe Smith",
            "age": 42,
            "gender": "Male",
            "height_cm": 172.0,
            "weight_kg": 86.0
        },
        "consent_id": "CONSENT-2026-001"
    },
    "errors": {},
    "warnings": []
}
```

### When Invalid ✗
```python
{
    "is_valid": False,
    "validated_data": None,
    "errors": {
        "age": "Age cannot exceed 150 years",
        "gender": "Gender must be one of: Male, Female, Other"
    },
    "warnings": []
}
```

### When Valid But Missing Consent ⚠️
```python
{
    "is_valid": True,
    "validated_data": {
        "user_id": {...},
        # Note: no consent_id here
    },
    "errors": {},
    "warnings": [
        "consent_id is not provided. User will need explicit consent before data processing."
    ]
}
```

---

## Real-World Examples

### Example 1: Patient Registration Flow
```python
from health_input_validator_standalone import validate_health_input

def register_patient(form_data):
    # Validate the input
    result = validate_health_input(
        name=form_data['name'],
        age=form_data['age'],
        gender=form_data['gender'],
        height_cm=form_data['height_cm'],
        weight_kg=form_data['weight_kg'],
        consent_id=form_data.get('consent_id')
    )
    
    # Handle result
    if result['is_valid']:
        # Store in database
        store_patient(result['validated_data'])
        return {"status": "success", "message": "Patient registered"}
    else:
        # Show errors to user
        return {"status": "error", "errors": result['errors']}
```

### Example 2: Multi-Patient Processing
```python
from health_input_validator_standalone import validate_health_input

patients_list = [
    {"name": "Patient 1", "age": 42, "gender": "Male", ...},
    {"name": "Patient 2", "age": 38, "gender": "Female", ...},
    # ...more patients
]

validated_patients = []
rejected_patients = []

for patient in patients_list:
    result = validate_health_input(**patient)
    
    if result['is_valid']:
        validated_patients.append(result['validated_data'])
    else:
        rejected_patients.append({
            "patient": patient,
            "errors": result['errors']
        })

print(f"Valid: {len(validated_patients)}")
print(f"Rejected: {len(rejected_patients)}")
```

### Example 3: Agent Processing Pipeline
```python
def agent_health_handler(user_input):
    # Step 1: Parse input from user/API
    patient_data = parse_user_input(user_input)
    
    # Step 2: Validate using standalone tool
    validation_result = validate_health_input(**patient_data)
    
    if not validation_result['is_valid']:
        return {
            "action": "ask_for_correction",
            "errors": validation_result['errors']
        }
    
    # Step 3: Check consent
    if validation_result['warnings']:
        return {
            "action": "ask_for_consent",
            "message": validation_result['warnings'][0]
        }
    
    # Step 4: Proceed with validated data
    return {
        "action": "proceed_to_next_step",
        "data": validation_result['validated_data']
    }
```

---

## Key Points

### ✓ What the Tool Does
- Takes patient demographic info
- Validates against health_input_contract schema
- Returns clean, validated data
- Flags missing consent
- Reports all errors

### ✗ What the Tool Does NOT Do
- Doesn't talk to LLM (no API calls)
- Doesn't store data (no database)
- Doesn't process lab reports (separate tool)
- Doesn't make decisions (just validates)

### 🎯 It's Just a Validator
Think of it as a **gatekeeper**:
```
Raw Input → [VALIDATOR] → Validated JSON or Errors
```

No external dependencies. No LLM. Just pure Python validation.

---

## Testing

Run these to see the validator in action:

```bash
# Run the standalone validator directly
python health_input_validator_standalone.py

# See all integration examples
python agent_integration_guide.py

# Test with fixture files
python test_health_input_validator_standalone.py
```

---

## Integration Checklist

- [ ] Copy the 3 files to your tools directory
- [ ] Import `validate_health_input` from `health_input_validator_standalone`
- [ ] Call it in your agent when you need to validate health input
- [ ] Check `result['is_valid']` to decide next steps
- [ ] Use `result['validated_data']` for downstream processing
- [ ] Handle `result['errors']` and `result['warnings']`

---

## File Structure

```
tools/
├── health_input_validator_standalone.py  ← The validator (USE THIS!)
├── agent_integration_guide.py            ← Integration examples
├── test_health_input_validator_standalone.py  ← Tests
├── HEALTH_INPUT_VALIDATOR_README.md      ← Full API docs
└── QUICKSTART.md                         ← Quick reference
```

---

## Summary

**Your standalone validator is production-ready!**

- ✓ No external dependencies
- ✓ Works standalone without LLM
- ✓ Easy to integrate into your agent
- ✓ Clean JSON input/output
- ✓ Comprehensive error handling

**Just import it and call it like a normal Python function!**

```python
from health_input_validator_standalone import validate_health_input

result = validate_health_input(name, age, gender, height_cm, weight_kg, consent_id)
```

That's all you need! 🚀
