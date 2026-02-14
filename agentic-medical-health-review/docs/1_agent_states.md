# Orchestrator: Agent workflow + States 
## A) Workflow:
**Input (User → Agent)** : User message ( Name + Age + Gender +Height + Weight + physical /mental activities + language + food habits )  + Lab reports (PDF or images or any other format) + approval / consent 
**Minimal required fields**:
- user_id  (name , age , gender , height + weight, language ) 
- test_eval_id 
- lab reports  (pdf or image or any other format)  
**Internal processing** : 
- user_id   (string and number)
- test_eval_id (number) 
- reference_value
- test_value
- mismatches w.r.t reference (array)
- Computed (lab report trend w.r.t measured parameters )
- risk_assessment (parameters v/s health risk )
- language_id (number)
- medication (string)
- device_id (number)
- device_data (array)
- consent_id
- activities_id
- food_habit_id
**Output (Agent → User)** :
Required Output Format
1) User info
    - user_id   (string and number)
    - test_eval_id (number) 
    -consent_id
2) Key Findings 
    - mismatch summary 
    - computed results / trends  
3) Health trend and Risk assessment
    - health trend
    - risk assessment details based on parameters
4) Medication and interaction
    - suggested medications
    - needs approval from doctor
5) Holistic  health review 
    - lifestyle changes 
    - diet  changes
    - overall reports

## B) States with State Diagram
stateDiagram-v2
	[*] --> Receive_Input
 	Receive_Input : User submits data\n(User info + Lab reports + Consent)
 	Receive_Input --> Validate_Input
 	Validate_Input : Check minimal required fields\n(user_id, test_eval_id, lab reports)
 	Validate_Input --> Reject_Input : Missing / Invalid data
	Reject_Input --> [*]
 	Validate_Input --> Store_Input : Valid data
 	Store_Input : Store raw user data & lab reports
 	Store_Input --> Extract_Lab_Data
 	Extract_Lab_Data : Parse PDFs / Images Extract test values
 	Extract_Lab_Data --> Map_Reference_Values
 	Map_Reference_Values : Map test values with reference ranges
 	Map_Reference_Values --> Detect_Mismatches
 	Detect_Mismatches : Identify mismatches (test vs reference)
 	Detect_Mismatches --> Compute_Trends
 	Compute_Trends : Analyze lab trends (historical / parameter-based)
 	Compute_Trends --> Risk_Assessment
 	Risk_Assessment : Assess health risks based on parameters
 	Risk_Assessment --> Medication_Recommendation
 	Medication_Recommendation : Suggest medications Flag doctor approval required
 	Medication_Recommendation --> Holistic_Review
 	Holistic_Review : Lifestyle & diet analysis (activity + food habits)
 	Holistic_Review --> Generate_Report
 	Generate_Report : Compile final response (User info + findings + risks)
 	Generate_Report --> Deliver_Output
 	Deliver_Output : Send structured report\nto user
 	Deliver_Output --> [*]

## C) State Flow Explanation (Quick)
**Input Phase**
- Receive_Input → collects user details, lab reports, and consent
- Validate_Input → ensures minimal required fields exist
**Processing Phase**
- Extract_Lab_Data → parses PDFs/images
- Map_Reference_Values → aligns tests with normal ranges
- Detect_Mismatches → finds abnormal values
- Compute_Trends → trend analysis over parameters
- Risk_Assessment → maps values to health risks
- Decision & Advisory Phase
- Medication_Recommendation → suggests meds (doctor approval flagged)
- Holistic_Review → lifestyle + diet insights
**Output Phase**
- Generate_Report → structured output as specified
- Deliver_Output → sent to user
