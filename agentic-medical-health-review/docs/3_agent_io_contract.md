# Tools Design + Schema i/o contract

## 1) Input Contract Spec
**Purpose**: What the agent is allowed to accept from the user.
**Prevents**:
- Partial data
- Silent assumptions
- Unsafe defaults
**Must Define**:
- Required vs optional fields
- Data types
- Minimal viable input
**health_input_contract.spec.json**
{
  "spec_type": "input_contract",
  "required_fields": [
    "user_id",
    "test_eval_id",
    "lab_reports",
    "consent_id"
  ],
  "user_id_schema": {
    "name": "string",
    "age": "number",
    "gender": "string",
    "height_cm": "number",
    "weight_kg": "number",
    "iso_language_code": "number",
    "language_desc": "string"
  },
  "lab_reports_schema": {
    "format": "pdf | image | other",
    "uri": "string"
  }
}


## 2) Consent & Compliance Spec
**Purpose**: 
- Hard-stop medical processing without explicit consent.
- This spec is non-negotiable in healthcare.
**Must Define**:
- When processing is blocked
- Allowed actions before consent
- Audit requirements
**health_consent_policy.spec.json**
{
  "spec_type": "consent_policy",
  "consent_required": true,
  "blocking_behavior": {
    "on_missing_consent": "STOP_PROCESSING"
  },
  "allowed_actions_without_consent": [
    "request_consent",
    "store_metadata"
  ],
  "audit_required": true
}

## 3) Lab Report Extraction Spec
**Purpose**: 
- Controls how raw PDFs/images become structured data.
**Prevents**:
- Hallucinated lab values
- Incorrect units
- Missing reference ranges
**Must Define**:
- Extractable parameters
- Required fields per parameter
**lab_report_extraction.spec.json**
{
  "spec_type": "extraction",
  "required_fields_per_test": [
    "test_name",
    "test_value",
    "unit",
    "reference_range"
  ],
  "allowed_units_validation": true,
  "unknown_test_handling": "FLAG"
}

## 4) Trend Computation Spec
**Purpose**: 
- Defines how trends are calculated, not guessed.
**Must Define**:
- Minimum data points
- Trend logic
- Confidence levels
**health_trend_computation.spec.json**
{
  "spec_type": "trend_computation",
  "minimum_reports_required": 2,
  "trend_types": [
    "increasing",
    "decreasing",
    "stable"
  ],
  "confidence_required": true
}

## 5) Risk Assessment Policy Spec
**Purpose**: 
- Maps lab parameters → health risks
- WITHOUT diagnosing.
- This is where many agents accidentally cross legal lines.
**Must Define**:
- Allowed risk labels
- Forbidden language
- Parameter-to-risk mapping
**health_risk_assessment.spec.json**
{ 
  "spec_type": "risk_assessment",
  "allowed_risk_levels": [
    "Low",
    "Moderate",
    "High"
  ],
  "forbidden_outputs": [
    "diagnosis",
    "disease_confirmation"
  ],
  "risk_mapping_requires_reference_range": true
}

## 6) Medication Safety Spec
**Purpose**: 
- Ensures no autonomous prescribing.
**Must Define**:
- What “suggestion” means
- Doctor approval enforcement
- Interaction warnings
**medication_safety.spec.json**
{
  "spec_type": "medication_policy",
  "can_prescribe": false,
  "can_suggest": true,
  "doctor_approval_required": true,
  "interaction_check_required": true
}

## 7) Localization & Language Spec
**Purpose**:
- Ensures output matches user language and avoids medical ambiguity.
**Must Define**:
- Language fallback
- Translation boundaries
**language_localization.spec.json**
{
  "spec_type": "localization",
  "supported_languages": [“mr”, “en”, “hn”],
  "fallback_language": en,
  "medical_terms_translation": "controlled"
}
**Reference**:
- https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes

## 8) Output Contract Spec
**Purpose**: 
- Locks the shape of the final answer.
**Prevents**:
- Missing sections
- Free-form unsafe advice
**health_output_contract.spec.json**
{
  "spec_type": "output_contract",
  "required_sections": [
    "user_info",
    "key_findings",
    "health_trend_and_risk",
    "medication_and_interaction",
    "holistic_health_review"
  ],
  "ordering_required": true
}

## 9) Failure & State Transition Spec
**Purpose**: 
- Defines what state the agent enters on failure.
- Critical for agentic workflows.
**agent_state_transition.spec.json**
{
  "spec_type": "state_machine",
  "states": [
    "INTAKE",
    "CONSENT_REQUIRED",
    "ANALYSIS",
    "REVIEW_REQUIRED",
    "COMPLETED"
  ],
  "error_transitions": {
    "MISSING_CONSENT": "CONSENT_REQUIRED",
    "INVALID_INPUT": "INTAKE"
  }
}

## 10) Audit & Traceability Spec
**Purpose**: 
- Compliance, debugging, and trust.
**health_audit.spec.json**
{
  "spec_type": "audit",
  "log_required": true,
  "fields": [
    "timestamp",
    "spec_version",
    "decision_summary"
  ]
}
