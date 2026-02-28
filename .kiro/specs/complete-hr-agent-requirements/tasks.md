# Implementation Plan: Complete HR Agent Requirements

## Overview

This implementation plan completes the AI HR Agent hackathon project by adding five new components to the existing system: Interview Question Generator, Interview Scheduler, Leave Manager, Pipeline State Validator, and Query Escalator. The implementation follows an incremental approach, building each component independently before integrating them into the HRAgent orchestrator. All components use Python with type hints and dataclasses for consistency with the existing codebase.

## Tasks

- [x] 1. Extend data models and add new data structures
  - [x] 1.1 Extend Candidate dataclass with new fields
    - Add interview_questions, slot_id, interviewer_id, and status_updated_at fields to Candidate
    - Ensure backward compatibility with existing Candidate usage
    - _Requirements: 1.9, 2.8, 4.11_
  
  - [x] 1.2 Create InterviewSlot dataclass
    - Define InterviewSlot with slot_id, interviewer_id, start_time, end_time, and is_available fields
    - Add validation for start_time < end_time
    - _Requirements: 2.1, 2.6_
  
  - [x] 1.3 Create LeaveRequest and LeavePolicy dataclasses
    - Define LeaveRequest with employee_id, leave_type, start_date, end_date fields
    - Define LeavePolicy with max_consecutive_days, min_notice_days, quota fields
    - _Requirements: 3.1, 3.2, 3.4, 3.7_
  
  - [x] 1.4 Create EmployeeBalance dataclass
    - Define EmployeeBalance with employee_id and leave type balance fields
    - Support leave types: annual, sick, personal, unpaid
    - _Requirements: 3.1, 3.12_
  
  - [x] 1.5 Create PipelineStatus enum with valid_transitions
    - Define all pipeline states: applied, screened, interview_scheduled, interviewed, offer_extended, offer_accepted, hired, rejected
    - Implement valid_transitions() method returning dict of allowed transitions
    - _Requirements: 4.1, 4.2, 4.3, 4.5-4.10_

- [x] 2. Implement PipelineStateValidator component
  - [x] 2.1 Create PipelineStateValidator class with validation logic
    - Implement validate_transition() method checking valid_transitions dict
    - Implement transition() method that validates, updates status, and logs
    - Add transition_log list to store all transitions
    - Implement get_transition_log() method
    - _Requirements: 4.1, 4.4, 4.11_
  
  - [ ]* 2.2 Write property test for valid transition enforcement
    - **Property 24: Valid Transition Enforcement**
    - **Validates: Requirements 4.1, 4.4**
  
  - [ ]* 2.3 Write property tests for terminal state immutability
    - **Property 25: Terminal State Immutability - Hired**
    - **Property 26: Terminal State Immutability - Rejected**
    - **Validates: Requirements 4.2, 4.3**
  
  - [ ]* 2.4 Write property test for transition logging
    - **Property 27: Transition Logging**
    - **Validates: Requirements 4.11**
  
  - [ ]* 2.5 Write unit tests for specific transition rules
    - Test each valid transition path (applied→screened, screened→interview_scheduled, etc.)
    - Test invalid transitions raise ValueError
    - Test terminal state rejection
    - _Requirements: 4.1-4.10_

- [x] 3. Implement InterviewQuestionGenerator component
  - [x] 3.1 Create InterviewQuestionGenerator class with template-based generation
    - Implement __init__ with use_llm and bedrock_client parameters
    - Implement generate_template_questions() for fallback
    - Create question templates for technical, behavioral, and experience types
    - Ensure 5-10 questions covering missing skills and matched preferred skills
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 1.8_
  
  - [x] 3.2 Add LLM-based question generation with AWS Bedrock
    - Implement construct_prompt() method using job description and candidate skills
    - Implement call_bedrock() with 5-second timeout using anthropic.claude-3-sonnet
    - Implement parse_llm_response() to extract structured questions
    - Add fallback to template generation on timeout or service error
    - _Requirements: 1.7, 1.10_
  
  - [x] 3.3 Implement generate_questions() main method
    - Coordinate LLM attempt with template fallback
    - Validate question count (5-10) and add general questions if needed
    - Ensure each question has 'question', 'type', and 'skill_focus' fields
    - Store questions in candidate.interview_questions
    - _Requirements: 1.1, 1.3, 1.6, 1.9_
  
  - [ ]* 3.4 Write property test for question count range
    - **Property 1: Question Count Range**
    - **Validates: Requirements 1.1**
  
  - [ ]* 3.5 Write property test for question type coverage
    - **Property 2: Question Type Coverage**
    - **Validates: Requirements 1.2**
  
  - [ ]* 3.6 Write property test for skill reference in questions
    - **Property 3: Skill Reference in Questions**
    - **Property 4: Missing Skill Coverage**
    - **Property 5: Preferred Skill Coverage**
    - **Validates: Requirements 1.3, 1.4, 1.5**
  
  - [ ]* 3.7 Write property test for question structure validity
    - **Property 6: Question Structure Validity**
    - **Property 7: Question Storage**
    - **Validates: Requirements 1.6, 1.9**
  
  - [ ]* 3.8 Write unit tests for question generation scenarios
    - Test template generation with various skill combinations
    - Test LLM fallback on timeout
    - Test edge cases: empty skills, no missing skills
    - _Requirements: 1.1-1.10_

- [x] 4. Implement InterviewScheduler component
  - [x] 4.1 Create InterviewScheduler class with slot validation
    - Implement validate_slot() checking start_time < end_time and future dates
    - Filter valid and available slots in schedule_interviews()
    - _Requirements: 2.6, 2.7_
  
  - [x] 4.2 Implement greedy scheduling algorithm with interviewer distribution
    - Sort candidates by match_score descending
    - Group available slots by interviewer_id
    - Assign candidates to interviewers with most available slots
    - Mark assigned slots as unavailable
    - Track unscheduled candidates when slots exhausted
    - _Requirements: 2.1, 2.2, 2.4, 2.5_
  
  - [x] 4.3 Implement schedule_interviews() method
    - Return dict with 'assignments', 'unscheduled', and 'conflicts' keys
    - Update candidate objects with slot_id and interviewer_id
    - Detect conflicts (should be 0 with correct implementation)
    - _Requirements: 2.1, 2.3, 2.8, 2.10_
  
  - [x] 4.4 Implement format_schedule() method
    - Sort assignments by start_time chronologically
    - Group by date
    - Format times in 12-hour format with AM/PM
    - Include candidate name, interviewer ID, date, and time range
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 4.5 Write property test for unique slot assignment
    - **Property 8: Unique Slot Assignment**
    - **Property 10: No Slot Conflicts**
    - **Validates: Requirements 2.1, 2.3**
  
  - [ ]* 4.6 Write property test for slot availability update
    - **Property 9: Slot Availability Update**
    - **Validates: Requirements 2.2**
  
  - [ ]* 4.7 Write property test for complete candidate accounting
    - **Property 11: Complete Candidate Accounting**
    - **Validates: Requirements 2.5**
  
  - [ ]* 4.8 Write property tests for slot time validation
    - **Property 12: Valid Slot Time Range**
    - **Property 13: Future Slot Times**
    - **Validates: Requirements 2.6, 2.7**
  
  - [ ]* 4.9 Write property test for assignment data consistency
    - **Property 14: Assignment Data Consistency**
    - **Property 15: Scheduling Report Structure**
    - **Validates: Requirements 2.8, 2.10**
  
  - [ ]* 4.10 Write property test for schedule format round-trip
    - **Property 16: Schedule Format Round-Trip**
    - **Validates: Requirements 2.11, 9.7**
  
  - [ ]* 4.11 Write unit tests for scheduling scenarios
    - Test interviewer distribution logic
    - Test insufficient slots scenario
    - Test edge cases: empty slots, empty candidates, all slots in past
    - _Requirements: 2.1-2.10, 9.1-9.7_

- [ ] 5. Checkpoint - Ensure all tests pass for components 1-4
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement LeaveManager component
  - [x] 6.1 Create LeaveManager class with policy initialization
    - Implement __init__ accepting policies dict and employee_balances dict
    - Support leave types: annual, sick, personal, unpaid
    - _Requirements: 3.1, 3.12_
  
  - [x] 6.2 Implement policy check methods
    - Implement check_employee_exists()
    - Implement check_date_range_valid()
    - Implement calculate_days_requested()
    - Implement check_sufficient_balance()
    - Implement check_consecutive_days_limit()
    - Implement check_notice_period()
    - Implement check_no_overlaps()
    - _Requirements: 3.1-3.9_
  
  - [x] 6.3 Implement evaluate_request() method with short-circuit logic
    - Execute checks in order, stopping at first failure
    - Track policy_checks_passed list
    - Return decision dict with status, reason, policy_checks_passed, days_requested
    - Set status to "approved" if all checks pass
    - _Requirements: 3.10, 3.11_
  
  - [ ]* 6.4 Write property test for leave balance validation
    - **Property 17: Leave Balance Validation**
    - **Validates: Requirements 3.1, 3.3**
  
  - [ ]* 6.5 Write property test for days calculation
    - **Property 18: Days Calculation**
    - **Validates: Requirements 3.2**
  
  - [ ]* 6.6 Write property test for consecutive days limit
    - **Property 19: Consecutive Days Limit**
    - **Validates: Requirements 3.4, 3.5**
  
  - [ ]* 6.7 Write property test for notice period validation
    - **Property 20: Notice Period Validation**
    - **Validates: Requirements 3.7**
  
  - [ ]* 6.8 Write property test for overlap detection
    - **Property 21: Overlap Detection**
    - **Validates: Requirements 3.8, 3.9**
  
  - [ ]* 6.9 Write property test for leave approval
    - **Property 22: Leave Approval**
    - **Property 23: Leave Decision Structure**
    - **Validates: Requirements 3.10, 3.11**
  
  - [ ]* 6.10 Write unit tests for leave management scenarios
    - Test each leave type with specific policy rules
    - Test each denial reason
    - Test edge cases: invalid date range, missing employee, boundary dates
    - _Requirements: 3.1-3.12_

- [x] 7. Implement QueryEscalator component
  - [x] 7.1 Create QueryEscalator class with keyword-based escalation
    - Implement __init__ with configurable salary_threshold (default: $150,000)
    - Implement check for sensitive keywords: discrimination, harassment, legal, lawsuit, complaint, grievance, termination, layoff
    - Return escalation decision with severity='high' for sensitive keywords
    - _Requirements: 5.1, 5.2, 5.9_
  
  - [x] 7.2 Implement context-based escalation checks
    - Implement salary threshold check (medium severity)
    - Implement executive position check (medium severity)
    - Implement low score override check (medium severity)
    - Implement extended leave check (medium severity)
    - Implement stale pipeline check (low severity)
    - _Requirements: 5.3, 5.4, 5.5, 5.6, 5.7, 5.9_
  
  - [x] 7.3 Implement evaluate_query() method
    - Check sensitive keywords first
    - Then check context-based escalations
    - Return decision dict with should_escalate, reason, severity, recommended_action
    - Generate human-readable recommended_action text
    - _Requirements: 5.1, 5.8, 5.10_
  
  - [ ]* 7.4 Write property test for escalation classification
    - **Property 28: Escalation Classification**
    - **Validates: Requirements 5.1**
  
  - [ ]* 7.5 Write property test for sensitive keyword escalation
    - **Property 29: Sensitive Keyword Escalation**
    - **Validates: Requirements 5.2**
  
  - [ ]* 7.6 Write property tests for context-based escalations
    - **Property 30: Salary Threshold Escalation**
    - **Property 31: Executive Position Escalation**
    - **Property 32: Low Score Override Escalation**
    - **Property 33: Extended Leave Escalation**
    - **Property 34: Stale Pipeline Escalation**
    - **Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7**
  
  - [ ]* 7.7 Write property test for escalation decision structure
    - **Property 35: Escalation Decision Structure**
    - **Property 36: Severity Assignment**
    - **Property 37: Recommended Action Presence**
    - **Validates: Requirements 5.8, 5.9, 5.10**
  
  - [ ]* 7.8 Write unit tests for query escalation scenarios
    - Test each escalation reason with specific examples
    - Test edge cases: empty query, missing context, boundary values
    - _Requirements: 5.1-5.10_

- [ ] 8. Checkpoint - Ensure all tests pass for components 5-7
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Integrate components into HRAgent class
  - [x] 9.1 Update HRAgent.__init__ to initialize all new components
    - Initialize InterviewQuestionGenerator with LLM configuration
    - Initialize InterviewScheduler
    - Initialize LeaveManager with policies and employee balances
    - Initialize PipelineStateValidator
    - Initialize QueryEscalator with salary threshold
    - _Requirements: 8.1_
  
  - [x] 9.2 Update screen_resumes() to use PipelineStateValidator
    - Replace direct status assignment with validator.transition()
    - Transition candidates from "applied" to "screened"
    - _Requirements: 8.2, 4.12_
  
  - [x] 9.3 Update shortlist_top_n() to generate interview questions
    - Call question_generator.generate_questions() for each shortlisted candidate
    - Store questions in candidate.interview_questions
    - _Requirements: 8.3, 1.9_
  
  - [x] 9.4 Update shortlist_top_n() to schedule interviews
    - Call scheduler.schedule_interviews() with shortlisted candidates and available slots
    - Store scheduling results (assignments, unscheduled)
    - _Requirements: 8.4_
  
  - [x] 9.5 Update shortlist_top_n() to use PipelineStateValidator for status transitions
    - Transition shortlisted candidates to "interview_scheduled" after successful slot assignment
    - Transition rejected candidates to "rejected"
    - _Requirements: 8.5, 8.6, 4.12_
  
  - [x] 9.6 Add process_leave_request() method to HRAgent
    - Accept LeaveRequest and optional existing_requests list
    - Call leave_manager.evaluate_request()
    - Return decision dict
    - _Requirements: 8.7_
  
  - [x] 9.7 Add escalate_query() method to HRAgent
    - Accept query string and optional context dict
    - Call query_escalator.evaluate_query()
    - Return escalation decision dict
    - _Requirements: 8.8_
  
  - [x] 9.8 Add calculate_mrr() method to HRAgent
    - Accept ranked candidates list and relevant candidate IDs list
    - Find rank of first relevant candidate (1-indexed)
    - Calculate MRR as 1/rank, or 0.0 if no relevant candidates
    - Support average MRR calculation across multiple queries
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ]* 9.9 Write property test for screen resumes state transition
    - **Property 49: Screen Resumes State Transition**
    - **Validates: Requirements 8.2**
  
  - [ ]* 9.10 Write property tests for shortlist workflow
    - **Property 50: Shortlist Question Generation**
    - **Property 51: Shortlist Interview Scheduling**
    - **Property 52: Shortlist Status Transition**
    - **Property 53: Rejection Status Transition**
    - **Validates: Requirements 8.3, 8.4, 8.5, 8.6**
  
  - [ ]* 9.11 Write property test for MRR formula
    - **Property 38: MRR Formula**
    - **Property 39: Average MRR Calculation**
    - **Validates: Requirements 6.2, 6.3, 6.6**
  
  - [ ]* 9.12 Write unit tests for integration scenarios
    - Test complete workflow: screen → shortlist → schedule
    - Test backward compatibility with existing app.py interface
    - Test edge cases: empty candidates, component initialization failures
    - _Requirements: 8.1-8.10, 10.1-10.10_

- [x] 10. Implement export_results() enhancements
  - [x] 10.1 Add interview questions to export output
    - Include candidate.interview_questions for each shortlisted candidate
    - _Requirements: 7.1_
  
  - [x] 10.2 Add interview schedule to export output
    - Include assignments list with slot_id, interviewer_id, start_time, end_time
    - Include unscheduled candidates list
    - _Requirements: 7.2_
  
  - [x] 10.3 Add leave decisions to export output
    - Include leave request decisions with status, reason, policy_checks_passed
    - _Requirements: 7.3_
  
  - [x] 10.4 Add pipeline transition history to export output
    - Include transition log from PipelineStateValidator
    - _Requirements: 7.4_
  
  - [x] 10.5 Add escalation decisions to export output
    - Include escalation decisions for any escalated queries
    - _Requirements: 7.5_
  
  - [x] 10.6 Add metrics section to export output
    - Include MRR and other ranking metrics
    - _Requirements: 7.6, 6.7_
  
  - [x] 10.7 Add metadata section to export output
    - Include generation timestamp and system version
    - _Requirements: 7.9_
  
  - [x] 10.8 Ensure datetime formatting as ISO 8601
    - Format all datetime objects as ISO 8601 strings
    - _Requirements: 7.8_
  
  - [x] 10.9 Validate JSON serialization
    - Ensure export_results() returns valid JSON-serializable dict
    - _Requirements: 7.10_
  
  - [ ]* 10.10 Write property tests for export structure
    - **Property 40: Interview Questions in Export**
    - **Property 41: Schedule Assignments in Export**
    - **Property 42: Leave Decisions in Export**
    - **Property 43: Transition History in Export**
    - **Property 44: Escalation Decisions in Export**
    - **Property 45: Backward Compatible Pipeline Structure**
    - **Property 46: ISO 8601 Datetime Format**
    - **Property 47: Metadata Section Presence**
    - **Property 48: JSON Serialization**
    - **Validates: Requirements 7.1-7.10**
  
  - [ ]* 10.11 Write unit tests for export scenarios
    - Test export with all components populated
    - Test backward compatibility with existing export format
    - Test edge cases: empty pipeline, no interviews scheduled
    - _Requirements: 7.1-7.10_

- [ ] 11. Implement error handling and edge cases
  - [ ] 11.1 Add error handling to InterviewQuestionGenerator
    - Handle LLM timeout with fallback to templates
    - Handle LLM service unavailable with fallback
    - Handle invalid candidate data with generic questions
    - Log all errors at ERROR level
    - _Requirements: 10.6_
  
  - [ ] 11.2 Add error handling to InterviewScheduler
    - Filter invalid slot times with warning logs
    - Handle insufficient slots gracefully
    - Filter past slot times with warning logs
    - _Requirements: 10.3_
  
  - [ ] 11.3 Add error handling to LeaveManager
    - Handle missing employee with "employee_not_found" denial
    - Handle invalid date range with "invalid_date_range" denial
    - Raise ValueError for missing policy (configuration error)
    - _Requirements: 10.4, 10.5_
  
  - [ ] 11.4 Add error handling to PipelineStateValidator
    - Raise ValueError for invalid transitions with descriptive message
    - Raise ValueError for invalid status values
    - Raise ValueError for missing candidate
    - _Requirements: 10.7_
  
  - [ ] 11.5 Add error handling to QueryEscalator
    - Handle empty query with should_escalate=False
    - Handle missing context by evaluating query text only
    - Log warnings for invalid context data
    - _Requirements: 10.8_
  
  - [ ] 11.6 Add error handling to HRAgent
    - Handle empty candidate list with empty results
    - Handle empty job description with default scoring weights
    - Raise RuntimeError for component initialization failures
    - Log all errors with component name, operation, and error details
    - _Requirements: 10.1, 10.2, 10.9, 10.10_
  
  - [ ]* 11.7 Write unit tests for error conditions
    - Test each error scenario for all components
    - Verify error messages are descriptive
    - Verify logging includes required details
    - _Requirements: 10.1-10.10_

- [ ] 12. Final checkpoint and integration testing
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Update app.py and main.py for new functionality
  - [x] 13.1 Add example usage for interview question generation
    - Demonstrate calling shortlist_top_n() and accessing interview_questions
    - _Requirements: 8.3_
  
  - [x] 13.2 Add example usage for interview scheduling
    - Create sample InterviewSlot objects
    - Demonstrate calling shortlist_top_n() with slots
    - Display formatted schedule
    - _Requirements: 8.4, 9.1_
  
  - [x] 13.3 Add example usage for leave request processing
    - Create sample LeaveRequest and LeavePolicy objects
    - Demonstrate calling process_leave_request()
    - Display decision results
    - _Requirements: 8.7_
  
  - [x] 13.4 Add example usage for query escalation
    - Demonstrate calling escalate_query() with various query types
    - Display escalation decisions
    - _Requirements: 8.8_
  
  - [x] 13.5 Add example usage for MRR calculation
    - Demonstrate calling calculate_mrr() with ranked candidates
    - Display MRR metrics
    - _Requirements: 8.9_
  
  - [x] 13.6 Update export_results() call to show new sections
    - Display interview questions, schedule, leave decisions, transitions, escalations, and metrics
    - _Requirements: 7.1-7.10_

- [x] 14. Final validation and testing
  - [x] 14.1 Run all unit tests and verify 100% pass rate
    - Execute all unit tests across all components
    - Fix any failing tests
    - _Requirements: All_
  
  - [x] 14.2 Run all property tests with 100 iterations
    - Execute all property tests with hypothesis
    - Verify no property violations
    - _Requirements: All_
  
  - [x] 14.3 Test complete workflow end-to-end
    - Run app.py with sample data
    - Verify all components work together
    - Verify export_results() produces valid JSON
    - _Requirements: 8.1-8.10, 7.1-7.10_
  
  - [x] 14.4 Verify backward compatibility
    - Test existing app.py functionality still works
    - Verify no breaking changes to existing API
    - _Requirements: 8.10, 7.7_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties with 100 iterations
- Unit tests validate specific examples and edge cases
- All components are designed to be independently testable before integration
- The implementation maintains backward compatibility with existing app.py interface
- Error handling follows defensive programming with graceful degradation
- All datetime objects use ISO 8601 format for consistency
- Logging follows standard levels: ERROR for failures, WARNING for edge cases, INFO for normal operations
