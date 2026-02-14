# COMPLETE TOOL LIST FOR HEALTH AGENT
## 1️⃣ Intake & Validation Tools
**1. validate_input_tool**
**Purpose**
- Validate incoming user payload against input_contract
**Responsibilities**
- Required fields present
- Data types correct
- Lab report format supported
**Failure triggers**
- INVALID_INPUT 
- Missing mandatory fields

**2. check_consent_tool**
**Purpose**
- Enforce consent & compliance policy
**Responsibilities**
- Verify consent_id
- Check consent validity / expiry (if applicable)
**Outputs**
- CONSENT_VALID
- CONSENT_MISSING
- CONSENT_DENIED

## 2️⃣ Document & Data Extraction Tools
**3. lab_report_parser_tool**
**Purpose**
- Parse PDFs / images into structured lab data
**Responsibilities**
- OCR (if image) 
- **Extract:**
    - test_name
    - test_value
    - unit
    - reference_range
**Hard rules**
- No hallucinated values
- Flag unknown tests

**4. normalize_lab_data_tool**
**Purpose**
- Normalize extracted values
**Responsibilities**
- Unit standardization
- Reference range alignment
- Parameter naming consistency

## 3️⃣ Analysis & Computation Tools
**5. mismatch_detection_tool**
**Purpose**
- Detect deviations from reference ranges
**Responsibilities**
- Compare test_value vs reference_range
- Generate mismatch objects

**6. trend_computation_tool**
**Purpose**
- Compute trends across multiple reports or device data
**Responsibilities**
- Increasing / Decreasing / Stable
- Confidence score calculation
**Constraints**
- Requires ≥ 2 data points

**7. risk_assessment_tool**
**Purpose**
- Map lab parameters to risk levels (not diagnosis)
**Responsibilities**
- Assign Low / Moderate / High risk
- Explain why risk exists
**Forbidden**
- Disease confirmation
- Diagnostic language

## 4️⃣ Medication & Safety Tools
**8. medication_suggestion_tool**
**Purpose**
- Suggest non-prescriptive medication options
**Responsibilities**
- Only suggest (never prescribe)
- Default to lifestyle-first approach
**Triggers**
- Escalates to HITL(Human-in-the-loop) if medication mentioned

**9. drug_interaction_check_tool**
**Purpose**
- Check for potential interactions
**Responsibilities**
- Validate against known interaction rules 
- Raise warning flags

**10. doctor_approval_gate_tool (Human-in-the-Loop)**
**Purpose**
- Enforce manual approval
**Responsibilities**
- Pause workflow
- Accept approve / reject signal
**States**
- REVIEW_REQUIRED

## 5️⃣ Holistic Health Tools
**11. lifestyle_recommendation_tool**
**Purpose**
- Suggest activity & behavior changes
**Inputs**
- Risk level
- Activity data
- Age & BMI

**12. diet_recommendation_tool**
**Purpose**
- Suggest diet changes
**Inputs**
- Lab mismatches
- Food habits
- Cultural context

## 6️⃣ Localization & Presentation Tools
**3. localization_tool**
**Purpose**
- Localize output to user language
**Responsibilities**
- Controlled medical vocabulary
- Safe translation

**14. output_formatter_tool**
**Purpose**
- Enforce output contract & ordering
**Responsibilities**
- No missing sections
- No free-form unsafe text

## 7️⃣ State, Audit & Governance Tools
**15. state_transition_tool**
**Purpose**
- Move agent between states
**States**
- INTAKE
- CONSENT_REQUIRED
- ANALYSIS
- REVIEW_REQUIRED
- COMPLETED
-  FAILED

**16. audit_logger_tool**
**Purpose**
- Compliance & traceability
**Logs**
- Timestamp
- Spec version
- Decisions
- State transitions

## 8️⃣ Error & Safety Tools
**17. failure_handler_tool**
**Purpose**
- Handle hard failures safely
**Responsibilities**
- User-safe messaging
- No partial medical insight leakage
