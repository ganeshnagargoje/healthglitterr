# Agentic Medical Health Review

## Room No: 9 — Medical Report Trend \+ Holistic Health Review (Multi-Agent)** 

**Problem Context (100 words)**   
People receive lab/medical reports as PDFs with many parameters over time. Manually tracking trends (diabetes, liver, kidney, thyroid, etc.) is difficult; patients miss early warnings. Reports are reviewed episodically, not longitudinally. Lack of personalized, multi-language interpretation creates confusion and delayed action. 

**One Primary Goal**   
The agent’s goal is to **analyze reports, detect trends, and produce holistic guidance**, subject to **medical safety constraints \+ report validity \+ user consent**, while optimizing for **early risk detection and understandable summaries**. 

**Scope and Boundaries** 
* Allowed: extract parameters, trend charts, risk flags, medication interaction reminders (non-prescriptive), lifestyle suggestions, regional language summary.   
* Stop/ask human: high-risk findings, medication changes, diagnosis.   
* Out of scope: prescribing/altering treatment. 

**User Types**   
Patient, Caregiver, Doctor (review), Lab admin. 

**Formal Conversation Samples** 
1. User uploads reports → Agent: “HbA1c rising 3 cycles—risk flag; book doctor?”   
2. User: “Explain in Hindi/Tamil.” → Agent provides translated summary \+ next-step checklist. 

## Team :
| Role  | Primary Owner Name  | Assistants  |
| :---- | :---- | :---- |
| **Agent Orchestrator (Core)** | Pradeep C R | Ganesh Nagargoje |
| **Tool Engineer A** | Ganesh Nagargoje | Pradeep C R |
| **Tool Engineer B** | Amulya  | Satheesh, Ganesh Nagargoje |
| **Prompt Engineer** | Sanchit Mehra | Amulya, Ganesh Nagargoje |
| **QA/Eval and Demo Engineer** | Satheesh  | Pradeep C R, Ganesh Nagargoje |

## Team Roles:  
1. **Agent Orchestrator (Core) Own the agent loop**:   
    Perceive \-\> Plan \-\> Act \-\> Validate \-\> HITL    
2. **Tool Engineer:**  
   (2 members for group with 5 members)   
   Build "self-defined tools" (local Python functions \+ JSON Schema) Tool Testing    
3. **Prompt Engineer:**  
    Design system prompts, tool calling prompt templates, constraints, refusal/safety rules, output formats    
4. **QA/Eval and Demo Engineer:**   
5. Creates conversational scripts, test cases, failure scenarios, metrics and a complete demo walkthrough 

**Online Design Document Link (Google Docs)**:
https://docs.google.com/document/d/1DYZvd7UyfHRj-pgG0AL0EKyqFKcVfioU3mnuJLsqkyE/edit?tab=t.dvklxtdrs3cj