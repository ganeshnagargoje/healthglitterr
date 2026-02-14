# Phase 1: Single Agent \+ Multiple Tools 

## Week 1: Build the Specification file for each stage 
1) Orchestrator: Draft agent workflow \+ states   
2) Tool Eng 1: Tool Design \+ Schema   
3) Tool Eng 2: Tool Design \+ Schema   
4) Prompt Engineer: System prompt \+ tool calling prompt \+ constraints   
5) QA/DEmo:10 test prompts \+ 2 full conversational script (satisfactory \+ failure) 

## Week 1 Deliverables 
— Medical Report Trend + Holistic Health Review (Multi-Agent) 
### What we froze this week
1) Use case structured spec (Goal, boundaries, user types, conversations)
2) Agent workflow state machine + Mermaid diagram
3) Tool list + JSON schemas (extract_entities, compare_documents, compute_adjusted_total)
4) Tool fixtures (sample inputs/outputs)
5) Prompts (system, tool-use, safety policy)
6) Test scripts + prompts + evaluation rubric 
### Assumptions (Week 1)
- Tolerance baseline: 2% (user-confirmed)
- Escalation threshold: INR 50,000
- Agent does NOT execute payments or send emails automatically.

## How the 5 members collaborate (Week 1 in practice) 
### Daily sync (15 min) 
- Member 1 checks: “Do tool schemas cover the state machine needs?” 
- Member 2 and 3 : "Design the tool and schemas" 
- Member 4 checks: “Do prompts match the schemas/fields?” 
- Member 5 checks: “Can we run the conversation scripts using only these fields?” 

### Integration checkpoint (end of Week 1) 
Run through happy_path.md and ensure every step maps to: 
- ca state 
- a tool schema 
- a prompt rule 
- a policy gate