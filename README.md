**Members**: 
1. Sanchit Mehara 
2. Ganesh Nagargoje 
3. Satheeshkumar Rajasekaran 
4. Pradeep CR   
5. Amulya Kumar     

**Problem Context (100 words):**      

**Agentic AI System for Diabetic Care & Risk Prevention:**
Today, diabetic care is largely manual and fragmented. Patients collect lab reports and glucometer readings from multiple sources, often in paper or PDF form, and doctors review them during brief, infrequent consultations. Analysis is mostly limited to checking individual values against normal ranges, with little systematic trend or risk prediction. Secondary complications such as kidney disease, heart conditions, or vision problems are usually identified only after symptoms appear or during annual screenings. Lifestyle guidance is generic and not personalized, making care reactive rather than preventive and increasing the risk of delayed intervention and poorer long-term health outcomes. 

**One Primary Goal:**
The agent’s goal is to continuously analyze diabetic patients’ medical reports, lab results, and glucose data to identify early risks of secondary complications and generate personalized health insights, subject to clinical guidelines, data availability, and ethical and regulatory constraints, while optimizing for early risk detection, patient safety, explainability, and long-term health and well-being. 

**Scope and Boundaries**   
**Scope:** 
The system focuses on analyzing diabetes-related medical data, including lab reports, medical records, and glucometer readings, to identify early risks of secondary complications such as kidney disease, cardiovascular conditions, and vision impairment. It provides personalized, explainable health insights and holistic lifestyle recommendations covering diet, activity, sleep, and preventive care, along with continuous monitoring and alerts for abnormal trends. 

**Boundaries:** 
The system does not replace doctors or provide medical diagnoses or emergency care. It does not prescribe or modify medications and operates strictly as a decision-support and wellness guidance tool. All insights are based on available data and standard clinical guidelines, with final medical decisions remaining with qualified healthcare professionals. 

**User Types**
Who interacts with the agent? 
Primary Users: Diabetic patients who regularly undergo lab testing and/or record blood glucose levels using a glucometer device. 
Secondary Users (Optional): Caregivers or family members who support the patient in monitoring health data and follow-up actions. 

**How does the interaction begin?**
The interaction begins when a patient uploads medical or lab reports (PDF/images) or connects/records glucose readings from a glucometer device. 
Users may also initiate interaction by asking questions about their reports, recent glucose trends, or overall health status through a conversational interface.

----------- 
**Formal conversation Samples** 
**Conversation 1: Lab Report Analysis & Kidney Risk Identification**
User (Patient): 
I have uploaded my latest blood and urine lab reports. Can you analyze them? 
Agent: 
I’ve reviewed your reports. Your HbA1c is 8.2%, which indicates suboptimal glucose control. Additionally, your urine microalbumin level is higher than normal over the last two tests. 
User: 
What does that mean for my health? 
Agent: 
Persistent elevated microalbumin levels can indicate an increased risk of early kidney disease in diabetic patients. Based on your data, your kidney risk is currently moderate. 
User: 
What should I do to improve this? 
Agent: 
I recommend tighter glucose control, reducing daily salt intake, maintaining proper hydration, and engaging in at least 30 minutes of moderate physical activity five days a week. It would also be advisable to consult your physician about periodic kidney function monitoring. 
Goal Achieved: 
Early kidney disease risk identified, and actionable, personalized health guidance provided. 

----------- 

**Conversation 2: Glucometer Trend Analysis & Cardiovascular Risk Awareness**
User (Patient): 
I’ve been recording my glucometer readings daily for the last three months. Can you check if everything looks, okay? 
Agent: 
I’ve analyzed your glucose trends. Your fasting glucose levels show frequent morning spikes, and your HbA1c trend has been gradually increasing. 
User: 
Does this put me at risk for other problems? 
Agent: 
Yes. Long-term elevated glucose levels combined with your recent lipid profile increase your risk of cardiovascular complications. Your current heart health risk is assessed as moderate. 
User: 
How can I reduce this risk? 
Agent: 
You can lower your risk by incorporating low–glycemic index foods, increasing aerobic exercise, improving sleep consistency, and managing stress levels. I also recommend discussing cholesterol management with your doctor during your next visit. 
Goal Achieved: 
Continuous glucose data analyzed, cardiovascular risk highlighted, and holistic lifestyle recommendations delivered. 

----------- 

**Hybrid Multi Agent Systems:**
Agent 1: Medical Report Intelligence Agent 
Lab report analysis and Glucometer reading analysis 
Agent 2: Health Trend & Risk Forecasting Agent:  
Key vitals analysis related to Diabetics, and identify if user is prone to Heart risk, Liver, Kidneys, Thyroid, Other vitals    
Agent 3: Medication & Interaction Agent: 
Diagnostic conclusions and suggestions to review with doctor.    
Agent 4: Holistic health review and suggestions:  
Overall health style suggestions, diet suggestions, Physical and mental fitness related suggestions    
Agent 5: Multi language support: 
Review results and translate them into any regional language provided by user.    
Agent 6: Integrate with health wearable device/App:  
Track the fitness goal, reminder for medication, reminder for lab visit, reminder for doctor consultation.

----------- 
