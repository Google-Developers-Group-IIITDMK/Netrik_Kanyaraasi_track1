# Requirements Document

## Introduction

This document specifies the requirements for completing the AI HR Agent hackathon project to meet all NETRIK Hackathon 2026 evaluation criteria. The system currently has basic resume parsing and ranking functionality (40% complete). This specification covers the missing 60% of functionality including interview question generation, conflict-aware scheduling, leave management policy compliance, pipeline state validation, and query escalation logic.

The completed system will be a comprehensive HR automation agent capable of screening candidates, generating interview questions, scheduling interviews without conflicts, managing leave requests according to policy rules, and escalating complex queries appropriately.

## Glossary

- **HR_Agent**: The main orchestration class that coordinates all HR automation functionality
- **Interview_Question_Generator**: Component responsible for generating role-specific interview questions using LLM
- **Interview_Scheduler**: Component that assigns candidates to available interview slots while preventing conflicts
- **Leave_Manager**: Component that evaluates leave requests against policy rules and employee balances
- **Pipeline_State_Validator**: Component that enforces valid state transitions in the candidate pipeline
- **Query_Escalator**: Component that determines when HR queries require human intervention
- **Candidate**: Data structure representing a job applicant with resume, skills, and pipeline status
- **InterviewSlot**: Data structure representing an available time slot with interviewer assignment
- **LeaveRequest**: Data structure representing an employee's request for time off
- **LeavePolicy**: Data structure defining rules for leave types (quota, notice period, max consecutive days)
- **PipelineStatus**: Enumeration of valid candidate states (applied, screened, interview_scheduled, interviewed, offer_extended, offer_accepted, hired, rejected)
- **MRR**: Mean Reciprocal Rank - metric for evaluating ranking quality (1/rank of first relevant result)

## Requirements

### Requirement 1: Generate Role-Specific Interview Questions

**User Story:** As an HR manager, I want the system to automatically generate relevant interview questions for each candidate based on their role and skills, so that I can conduct effective interviews without manual question preparation.

#### Acceptance Criteria

1. WHEN a candidate is shortlisted for interview, THE Interview_Question_Generator SHALL generate between 5 and 10 role-specific questions
2. THE Interview_Question_Generator SHALL include questions covering technical skills, behavioral scenarios, and experience validation
3. WHEN generating questions, THE Interview_Question_Generator SHALL reference the candidate's matched skills and missing skills from their explanation
4. THE Interview_Question_Generator SHALL include at least one question addressing each missing required skill
5. WHEN the job description includes preferred skills, THE Interview_Question_Generator SHALL generate at least one question about preferred skills the candidate possesses
6. THE Interview_Question_Generator SHALL format each question with a question type label (technical, behavioral, or experience)
7. WHEN AWS Bedrock is available, THE Interview_Question_Generator SHALL use an LLM to generate contextual questions
8. IF AWS Bedrock is unavailable, THEN THE Interview_Question_Generator SHALL use template-based question generation as fallback
9. THE Interview_Question_Generator SHALL store generated questions in the candidate's data structure
10. THE Interview_Question_Generator SHALL complete question generation within 5 seconds per candidate

### Requirement 2: Schedule Interviews Without Conflicts

**User Story:** As an HR coordinator, I want the system to automatically assign candidates to available interview slots without double-booking interviewers, so that I can efficiently manage the interview calendar.

#### Acceptance Criteria

1. WHEN scheduling interviews for shortlisted candidates, THE Interview_Scheduler SHALL assign each candidate to exactly one available InterviewSlot
2. THE Interview_Scheduler SHALL mark assigned slots as unavailable (is_available = False)
3. THE Interview_Scheduler SHALL prevent assigning multiple candidates to the same slot
4. WHEN an interviewer has multiple slots, THE Interview_Scheduler SHALL distribute candidates across different interviewers when possible
5. IF insufficient slots exist for all candidates, THEN THE Interview_Scheduler SHALL schedule as many as possible and return a list of unscheduled candidates
6. THE Interview_Scheduler SHALL validate that slot start_time is before end_time
7. THE Interview_Scheduler SHALL validate that slot start_time is in the future relative to current time
8. WHEN a candidate is assigned to a slot, THE Interview_Scheduler SHALL store the slot_id and interviewer_id in the candidate's data
9. THE Interview_Scheduler SHALL update the candidate's status to "interview_scheduled" only after successful slot assignment
10. THE Interview_Scheduler SHALL return a scheduling report containing assigned slots, unscheduled candidates, and conflict count (should be 0)

### Requirement 3: Validate Leave Requests Against Policy Rules

**User Story:** As an HR administrator, I want the system to automatically validate leave requests against policy rules and employee balances, so that I can approve or deny requests consistently and fairly.

#### Acceptance Criteria

1. WHEN evaluating a leave request, THE Leave_Manager SHALL check if the employee has sufficient remaining balance for the leave type
2. THE Leave_Manager SHALL calculate the number of days requested (end_date - start_date + 1)
3. WHEN the requested days exceed the employee's remaining balance, THE Leave_Manager SHALL set request status to "denied" with reason "insufficient_balance"
4. THE Leave_Manager SHALL validate that requested consecutive days do not exceed the policy's max_consecutive_days limit
5. WHEN consecutive days exceed the limit, THE Leave_Manager SHALL set request status to "denied" with reason "exceeds_max_consecutive_days"
6. THE Leave_Manager SHALL calculate notice period as (start_date - current_date) in days
7. WHEN notice period is less than policy's min_notice_days, THE Leave_Manager SHALL set request status to "denied" with reason "insufficient_notice"
8. THE Leave_Manager SHALL check for overlapping leave requests from the same employee
9. WHEN overlapping requests exist, THE Leave_Manager SHALL set request status to "denied" with reason "overlapping_request"
10. WHEN all policy checks pass, THE Leave_Manager SHALL set request status to "approved"
11. THE Leave_Manager SHALL return a decision object containing status, reason, and policy_checks_passed list
12. THE Leave_Manager SHALL support leave types: annual, sick, personal, unpaid

### Requirement 4: Enforce Valid Pipeline State Transitions

**User Story:** As a system administrator, I want the system to enforce valid state transitions in the candidate pipeline, so that candidates cannot skip required stages or move to invalid states.

#### Acceptance Criteria

1. WHEN updating a candidate's status, THE Pipeline_State_Validator SHALL verify the transition is valid according to PipelineStatus.valid_transitions()
2. THE Pipeline_State_Validator SHALL reject transitions from "hired" to any other state
3. THE Pipeline_State_Validator SHALL reject transitions from "rejected" to any other state
4. WHEN an invalid transition is attempted, THE Pipeline_State_Validator SHALL raise a ValueError with message "Invalid transition from {current} to {target}"
5. THE Pipeline_State_Validator SHALL allow transition from "applied" to "screened" or "rejected" only
6. THE Pipeline_State_Validator SHALL allow transition from "screened" to "interview_scheduled" or "rejected" only
7. THE Pipeline_State_Validator SHALL allow transition from "interview_scheduled" to "interviewed" or "rejected" only
8. THE Pipeline_State_Validator SHALL allow transition from "interviewed" to "offer_extended" or "rejected" only
9. THE Pipeline_State_Validator SHALL allow transition from "offer_extended" to "offer_accepted" or "rejected" only
10. THE Pipeline_State_Validator SHALL allow transition from "offer_accepted" to "hired" or "rejected" only
11. THE Pipeline_State_Validator SHALL log all state transitions with timestamp, candidate_id, from_state, and to_state
12. THE HR_Agent SHALL use Pipeline_State_Validator for all status updates in screen_resumes() and shortlist_top_n() methods

### Requirement 5: Escalate Complex Queries to Human Review

**User Story:** As an HR manager, I want the system to identify queries that require human judgment and escalate them appropriately, so that complex or sensitive issues receive proper attention.

#### Acceptance Criteria

1. WHEN analyzing a query, THE Query_Escalator SHALL classify it as "auto_handle" or "escalate"
2. THE Query_Escalator SHALL escalate queries containing keywords: "discrimination", "harassment", "legal", "lawsuit", "complaint", "grievance", "termination", "layoff"
3. THE Query_Escalator SHALL escalate queries about salary negotiations above a configurable threshold (default: $150,000)
4. THE Query_Escalator SHALL escalate queries about executive-level positions (VP, C-suite, Director)
5. WHEN a candidate has match_score below 0.3 but is being considered for interview, THE Query_Escalator SHALL escalate with reason "low_score_override"
6. WHEN leave requests exceed 15 consecutive days, THE Query_Escalator SHALL escalate with reason "extended_leave"
7. WHEN a candidate has been in "interview_scheduled" status for more than 30 days, THE Query_Escalator SHALL escalate with reason "stale_pipeline"
8. THE Query_Escalator SHALL return an escalation decision containing: should_escalate (bool), reason (str), severity (low/medium/high), and recommended_action (str)
9. THE Query_Escalator SHALL assign severity "high" to legal/compliance keywords, "medium" to executive positions and extended leave, "low" to stale pipeline
10. THE Query_Escalator SHALL provide recommended_action text describing why escalation is needed

### Requirement 6: Calculate Mean Reciprocal Rank for Ranking Quality

**User Story:** As a system evaluator, I want to measure the quality of candidate rankings using MRR metric, so that I can quantify how well the system ranks relevant candidates.

#### Acceptance Criteria

1. WHEN calculating MRR, THE HR_Agent SHALL accept a list of ranked candidates and a list of relevant candidate IDs
2. THE HR_Agent SHALL find the rank position (1-indexed) of the first relevant candidate in the ranked list
3. THE HR_Agent SHALL calculate MRR as 1 divided by the rank of the first relevant candidate
4. WHEN no relevant candidates exist in the ranked list, THE HR_Agent SHALL return MRR of 0.0
5. WHEN the first candidate in the ranked list is relevant, THE HR_Agent SHALL return MRR of 1.0
6. THE HR_Agent SHALL support calculating average MRR across multiple queries
7. THE HR_Agent SHALL include MRR score in the export_results() output under a "metrics" section

### Requirement 7: Export Complete Results Including All Components

**User Story:** As a hackathon evaluator, I want the system to export a comprehensive JSON result containing all functionality outputs, so that I can evaluate all aspects of the system in a standardized format.

#### Acceptance Criteria

1. THE HR_Agent SHALL include interview questions for each shortlisted candidate in export_results()
2. THE HR_Agent SHALL include interview schedule assignments with slot_id, interviewer_id, start_time, and end_time in export_results()
3. THE HR_Agent SHALL include leave request decisions with status, reason, and policy_checks in export_results()
4. THE HR_Agent SHALL include pipeline state transition history in export_results()
5. THE HR_Agent SHALL include escalation decisions for any escalated queries in export_results()
6. THE HR_Agent SHALL include MRR and other ranking metrics in export_results()
7. THE HR_Agent SHALL maintain the existing pipeline structure in export_results() for backward compatibility
8. THE HR_Agent SHALL format all datetime objects as ISO 8601 strings in export_results()
9. THE HR_Agent SHALL include a "metadata" section with generation timestamp and system version in export_results()
10. THE HR_Agent SHALL ensure export_results() returns valid JSON that can be serialized without errors

### Requirement 8: Integrate All Components into HR Agent Workflow

**User Story:** As a developer, I want all new components to be properly integrated into the HRAgent class workflow, so that the system functions as a cohesive unit.

#### Acceptance Criteria

1. THE HR_Agent SHALL initialize Interview_Question_Generator, Interview_Scheduler, Leave_Manager, Pipeline_State_Validator, and Query_Escalator in __init__()
2. WHEN screen_resumes() is called, THE HR_Agent SHALL use Pipeline_State_Validator to transition candidates from "applied" to "screened"
3. WHEN shortlist_top_n() is called, THE HR_Agent SHALL generate interview questions for shortlisted candidates
4. WHEN shortlist_top_n() is called, THE HR_Agent SHALL schedule interviews for shortlisted candidates
5. WHEN shortlist_top_n() is called, THE HR_Agent SHALL use Pipeline_State_Validator to transition shortlisted candidates to "interview_scheduled"
6. WHEN shortlist_top_n() is called, THE HR_Agent SHALL use Pipeline_State_Validator to transition rejected candidates to "rejected"
7. THE HR_Agent SHALL provide a process_leave_request() method that uses Leave_Manager to evaluate requests
8. THE HR_Agent SHALL provide an escalate_query() method that uses Query_Escalator to classify queries
9. THE HR_Agent SHALL provide a calculate_mrr() method that computes ranking quality metrics
10. THE HR_Agent SHALL maintain all existing method signatures for backward compatibility with app.py and main.py

### Requirement 9: Parse and Pretty-Print Interview Schedules

**User Story:** As an HR coordinator, I want to view interview schedules in a human-readable format, so that I can easily communicate schedules to candidates and interviewers.

#### Acceptance Criteria

1. THE Interview_Scheduler SHALL provide a format_schedule() method that returns a human-readable string representation
2. WHEN formatting a schedule, THE Interview_Scheduler SHALL include candidate name, interviewer ID, date, and time range
3. THE Interview_Scheduler SHALL sort scheduled interviews by start_time in chronological order
4. THE Interview_Scheduler SHALL format times in 12-hour format with AM/PM indicators
5. THE Interview_Scheduler SHALL group interviews by date when formatting
6. WHEN parsing schedule data, THE Interview_Scheduler SHALL validate datetime formats and raise ValueError for invalid formats
7. FOR ALL valid schedule objects, formatting then parsing then formatting SHALL produce equivalent output (round-trip property)

### Requirement 10: Handle Edge Cases and Error Conditions

**User Story:** As a system administrator, I want the system to handle edge cases and error conditions gracefully, so that the system remains stable and provides useful error messages.

#### Acceptance Criteria

1. WHEN candidates list is empty, THE HR_Agent SHALL return empty results without raising exceptions
2. WHEN job description has empty required_skills list, THE HR_Agent SHALL assign match_score based on experience and quality only
3. WHEN interview slots list is empty, THE Interview_Scheduler SHALL return all candidates as unscheduled
4. WHEN leave request has start_date after end_date, THE Leave_Manager SHALL set status to "denied" with reason "invalid_date_range"
5. WHEN employee data is missing for a leave request, THE Leave_Manager SHALL set status to "denied" with reason "employee_not_found"
6. WHEN LLM service fails during question generation, THE Interview_Question_Generator SHALL fall back to template-based generation
7. WHEN invalid PipelineStatus value is provided, THE Pipeline_State_Validator SHALL raise ValueError with descriptive message
8. WHEN Query_Escalator receives empty query string, THE Query_Escalator SHALL return should_escalate=False
9. WHEN calculating MRR with empty candidate list, THE HR_Agent SHALL return MRR of 0.0
10. THE HR_Agent SHALL log all errors with ERROR level including component name, operation, and error details
