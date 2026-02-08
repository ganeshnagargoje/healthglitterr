**Members**: 
1. Sanchit Mehara 
2. Ganesh Nagargoje 
3. Satheeshkumar Rajasekaran 
4. Pradeep CR   
5. Amulya Kumar     

**Room No: 9 — Medical Report Trend + Holistic Health Review (Multi-Agent)** 

**Problem Context (100 words)** 
People receive lab/medical reports as PDFs with many parameters over time. Manually tracking trends (diabetes, liver, kidney, thyroid, etc.) is difficult; patients miss early warnings. Reports are reviewed episodically, not longitudinally. Lack of personalized, multi-language interpretation creates confusion and delayed action. 

**One Primary Goal** 
The agent’s goal is to analyze reports, detect trends, and produce holistic guidance, subject to medical safety constraints + report validity + user consent, while optimizing for early risk detection and understandable summaries. 

**Scope and Boundaries** 

Allowed: extract parameters, trend charts, risk flags, medication interaction reminders (non-prescriptive), lifestyle suggestions, regional language summary. 

Stop/ask human: high-risk findings, medication changes, diagnosis. 

**Out of scope**: prescribing/altering treatment. 

**User Types** 
Patient, Caregiver, Doctor (review), Lab admin. 

**Formal Conversation Samples** 

User uploads reports → Agent: “HbA1c rising 3 cycles—risk flag; book doctor?” 

User: “Explain in Hindi/Tamil.” → Agent provides translated summary + next-step checklist. 

----------- 

agentic-invoice-dispute/
├── docs/
│   ├── agent_states.md          # State definitions & transitions
│   ├── agent_io_contract.md     # Input/output contracts per state
│   ├── state_diagram.mmd        # Mermaid state diagram
│   └── README_week1.md          # Design notes & early milestones
│
├── tools/
│   ├── specs/
│   │   ├── extract_entities.schema.json
│   │   ├── compare_documents.schema.json
│   │   └── compute_adjusted_total.schema.json
│   │
│   └── fixtures/
│       ├── extract_entities_case*.json
│       ├── mismatch_samples.json
│
├── prompts/
│   ├── system_prompt.md         # Global agent role & constraints
│   ├── tool_use_prompt.md       # Rules for tool invocation
│   └── safety_policy.md         # Financial & hallucination guardrails
│
├── tests/
│   ├── conversations/
│   │   ├── happy_path.md
│   │   └── escalation_path.md
│   ├── test_prompts.md
│   └── eval_rubric.md
│
└── README.md
