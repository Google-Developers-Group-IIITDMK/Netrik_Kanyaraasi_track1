# Track 2 — AI HR Agent Steering File

## 1. Objective

Implement a complete AI HR Agent that fulfills all required Track 2 functionalities while strictly preserving:
- Class interfaces
- Output format
- Evaluation schema

The system must appear production-ready and modular.

## 2. Required Functional Modules

The implementation must fully support:
- Resume Screening
- Interview Scheduling
- Questionnaire Generation
- Pipeline Management
- Leave Management
- Escalation Handling

All must return results in the official evaluation format.

## 3. Non-Negotiable Constraints

- Do NOT modify abstract interfaces.
- Do NOT modify export_results() format.
- Ensure deterministic behavior unless LLM explicitly used.
- Ranking must be explainable.
- Scheduling must handle slot availability.
- Leave management must enforce policy strictly.
- Escalation must categorize priority.

## 4. Resume Screening Strategy

Ranking logic should include:
- Required skill overlap
- Preferred skill bonus
- Experience normalization
- Optional semantic similarity
- Final weighted score

Avoid basic keyword-only matching.

## 5. Interview Scheduling Strategy

Minimum viable:
- Assign first available slot
- Mark slot unavailable
- Update pipeline state

If possible:
- Avoid conflicts
- Track scheduled interviews

## 6. Questionnaire Generation Strategy

Must generate structured list:
- Technical
- Behavioral (STAR format)
- Situational
- Role-specific

Output must be JSON structured.

## 7. Leave Management

Already implemented. Ensure policy violations are clear and human-readable.

## 8. Escalation Handling

Keyword-based categorization:
- High
- Medium
- Low

Return tuple as specified.

## 9. Architecture Principles

- Separation of concerns
- No hidden global state
- Extendable for LLM integration (Bedrock ready)
- Modular logic
- Hackathon-ready but scalable

## 10. Differentiation Goal

This must not look like a partial implementation. All abstract methods must be implemented.

The final output must fully populate:
- resume_screening
- scheduling
- questionnaire
- pipeline
- leave_management
- escalations
