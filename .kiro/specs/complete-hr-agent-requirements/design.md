# Design Document: Complete HR Agent Requirements

## Overview

This design document specifies the technical implementation for completing the AI HR Agent hackathon project. The system currently implements basic resume parsing and ranking (40% complete). This design covers the remaining 60% of functionality across five new components:

1. **Interview Question Generator**: Generates role-specific interview questions using LLM or template fallback
2. **Interview Scheduler**: Assigns candidates to interview slots without conflicts
3. **Leave Manager**: Validates leave requests against policy rules and employee balances
4. **Pipeline State Validator**: Enforces valid state transitions in the candidate pipeline
5. **Query Escalator**: Identifies queries requiring human review

The design integrates these components into the existing HRAgent class while maintaining backward compatibility with the current app.py interface. The system will export comprehensive JSON results including all component outputs for hackathon evaluation.

### Design Goals

- Maintain existing architecture and data models where possible
- Ensure all components are loosely coupled and independently testable
- Provide graceful degradation (e.g., LLM fallback to templates)
- Handle edge cases and error conditions robustly
- Support comprehensive metrics and reporting for evaluation

## Architecture

### System Architecture

The system follows a component-based architecture where the HRAgent class acts as the orchestrator for five specialized components:

```
┌─────────────────────────────────────────────────────────────┐
│                         HRAgent                              │
│  (Orchestrator - coordinates all HR automation workflows)   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐   ┌──────────────┐
│SmartResume   │    │Interview     │   │Interview     │
│Screener      │    │Question      │   │Scheduler     │
│(existing)    │    │Generator     │   │              │
└──────────────┘    └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐   ┌──────────────┐
│Pipeline      │    │Leave         │   │Query         │
│State         │    │Manager       │   │Escalator     │
│Validator     │    │              │   │              │
└──────────────┘    └──────────────┘   └──────────────┘
```

### Component Responsibilities

**HRAgent (Orchestrator)**
- Initializes all components
- Coordinates workflow: screen → rank → generate questions → schedule interviews
- Manages candidate pipeline state
- Provides public API methods: screen_resumes(), shortlist_top_n(), process_leave_request(), escalate_query(), calculate_mrr()
- Exports comprehensive results in JSON format

**SmartResumeScreener (Existing)**
- Parses resumes and extracts skills
- Calculates match scores based on required/preferred skills, experience, and resume quality
- Provides skill gap analysis (matched vs missing skills)

**InterviewQuestionGenerator (New)**
- Generates 5-10 role-specific interview questions per candidate
- Uses AWS Bedrock LLM when available, falls back to templates
- Covers technical, behavioral, and experience question types
- References candidate's matched and missing skills
- Completes within 5 seconds per candidate

**InterviewScheduler (New)**
- Assigns candidates to available interview slots
- Prevents double-booking (one candidate per slot)
- Distributes candidates across interviewers when possible
- Validates slot timing (start < end, future dates)
- Returns scheduling report with assignments and unscheduled candidates

**LeaveManager (New)**
- Validates leave requests against policy rules
- Checks: balance sufficiency, consecutive day limits, notice period, overlapping requests
- Supports leave types: annual, sick, personal, unpaid
- Returns decision with status, reason, and policy checks passed

**PipelineStateValidator (New)**
- Enforces valid state transitions per PipelineStatus.valid_transitions()
- Prevents transitions from terminal states (hired, rejected)
- Logs all transitions with timestamp
- Raises ValueError for invalid transitions

**QueryEscalator (New)**
- Classifies queries as "auto_handle" or "escalate"
- Escalates based on: sensitive keywords, salary thresholds, executive positions, low scores, extended leave, stale pipeline
- Assigns severity (low/medium/high) and recommended action
- Returns escalation decision object

### Data Flow

1. **Resume Screening Flow**
   ```
   Candidates → SmartResumeScreener → Ranked Candidates → PipelineStateValidator (applied→screened)
   ```

2. **Shortlisting Flow**
   ```
   Top N Candidates → InterviewQuestionGenerator → Questions Generated
                   → InterviewScheduler → Slots Assigned
                   → PipelineStateValidator (screened→interview_scheduled or rejected)
   ```

3. **Leave Request Flow**
   ```
   LeaveRequest → LeaveManager → Policy Validation → Decision (approved/denied)
   ```

4. **Query Escalation Flow**
   ```
   Query → QueryEscalator → Classification → Escalation Decision
   ```

## Components and Interfaces

### InterviewQuestionGenerator

**Purpose**: Generate role-specific interview questions for shortlisted candidates

**Interface**:
```python
class InterviewQuestionGenerator:
    def __init__(self, use_llm: bool = True, bedrock_client = None):
        """
        Args:
            use_llm: Whether to attempt LLM-based generation
            bedrock_client: AWS Bedrock client (optional)
        """
        
    def generate_questions(
        self, 
        candidate: Candidate, 
        job_description: JobDescription
    ) -> List[Dict[str, str]]:
        """
        Generate 5-10 interview questions for a candidate.
        
        Args:
            candidate: Candidate with skills and explanation
            job_description: Job requirements and description
            
        Returns:
            List of question dicts with keys: 'question', 'type', 'skill_focus'
            
        Raises:
            TimeoutError: If generation exceeds 5 seconds
        """
```

**Implementation Approach**:

1. **LLM-Based Generation** (Primary):
   - Construct prompt with: job title, required skills, candidate's matched skills, missing skills, preferred skills
   - Call AWS Bedrock with model: anthropic.claude-3-sonnet
   - Parse LLM response into structured question list
   - Validate: 5-10 questions, each has type (technical/behavioral/experience)
   - Timeout after 5 seconds

2. **Template-Based Generation** (Fallback):
   - Use predefined templates per question type:
     - Technical: "Explain your experience with {skill}" for missing skills
     - Behavioral: "Describe a situation where you used {skill} to solve a problem"
     - Experience: "How many years have you worked with {skill}?"
   - Generate at least one question per missing required skill
   - Generate questions for matched preferred skills
   - Ensure 5-10 total questions by filling with general questions

3. **Question Storage**:
   - Add 'interview_questions' field to Candidate dataclass
   - Store as List[Dict] with structure: {'question': str, 'type': str, 'skill_focus': str}

**Algorithm**:
```
function generate_questions(candidate, job_description):
    questions = []
    
    # Extract skills from candidate explanation
    missing_skills = candidate.explanation['missing_required_skills']
    matched_skills = candidate.explanation['matched_required_skills']
    preferred_skills = candidate.explanation['matched_preferred_skills']
    
    if use_llm and bedrock_available:
        try:
            prompt = construct_prompt(candidate, job_description, missing_skills, matched_skills, preferred_skills)
            response = call_bedrock(prompt, timeout=5)
            questions = parse_llm_response(response)
        except (TimeoutError, ServiceError):
            questions = generate_template_questions(missing_skills, matched_skills, preferred_skills)
    else:
        questions = generate_template_questions(missing_skills, matched_skills, preferred_skills)
    
    # Ensure 5-10 questions
    if len(questions) < 5:
        questions.extend(generate_general_questions(5 - len(questions)))
    if len(questions) > 10:
        questions = questions[:10]
    
    return questions
```

### InterviewScheduler

**Purpose**: Assign candidates to interview slots without conflicts

**Interface**:
```python
class InterviewScheduler:
    def schedule_interviews(
        self,
        candidates: List[Candidate],
        slots: List[InterviewSlot]
    ) -> Dict:
        """
        Assign candidates to available slots without conflicts.
        
        Args:
            candidates: List of candidates to schedule
            slots: List of available interview slots
            
        Returns:
            Dict with keys:
                - 'assignments': List[Dict] with candidate_id, slot_id, interviewer_id, start_time, end_time
                - 'unscheduled': List[str] of candidate_ids without slots
                - 'conflicts': int (should be 0)
        """
        
    def format_schedule(self, assignments: List[Dict]) -> str:
        """
        Format schedule in human-readable format.
        
        Returns:
            Multi-line string with interviews sorted by time, grouped by date
        """
```

**Implementation Approach**:

1. **Slot Validation**:
   - Filter slots where is_available == True
   - Validate start_time < end_time
   - Validate start_time > current_time
   - Remove invalid slots and log warnings

2. **Assignment Algorithm** (Greedy with Interviewer Distribution):
   - Sort candidates by match_score (descending)
   - Group available slots by interviewer_id
   - For each candidate:
     - Select interviewer with most available slots
     - Assign candidate to first available slot for that interviewer
     - Mark slot as unavailable (is_available = False)
     - Store assignment: {candidate_id, slot_id, interviewer_id, start_time, end_time}
     - Update candidate object with slot_id and interviewer_id
   - Track unscheduled candidates if slots exhausted

3. **Conflict Detection**:
   - After assignment, verify no slot has multiple candidates
   - Count conflicts (should be 0 with correct implementation)

4. **Schedule Formatting**:
   - Sort assignments by start_time
   - Group by date
   - Format times as 12-hour with AM/PM
   - Output format:
     ```
     Date: 2024-01-15
       09:00 AM - 10:00 AM: John Doe with Interviewer INT-001
       02:00 PM - 03:00 PM: Jane Smith with Interviewer INT-002
     ```

**Algorithm**:
```
function schedule_interviews(candidates, slots):
    # Validate and filter slots
    valid_slots = [s for s in slots if validate_slot(s)]
    available_slots = [s for s in valid_slots if s.is_available]
    
    # Group slots by interviewer
    interviewer_slots = group_by(available_slots, 'interviewer_id')
    
    # Sort candidates by score
    sorted_candidates = sort(candidates, key='match_score', reverse=True)
    
    assignments = []
    unscheduled = []
    
    for candidate in sorted_candidates:
        # Find interviewer with most available slots
        interviewer = max(interviewer_slots, key=lambda i: len(interviewer_slots[i]))
        
        if interviewer_slots[interviewer]:
            slot = interviewer_slots[interviewer].pop(0)
            slot.is_available = False
            
            assignment = {
                'candidate_id': candidate.candidate_id,
                'candidate_name': candidate.name,
                'slot_id': slot.slot_id,
                'interviewer_id': slot.interviewer_id,
                'start_time': slot.start_time,
                'end_time': slot.end_time
            }
            assignments.append(assignment)
            
            # Update candidate object
            candidate.slot_id = slot.slot_id
            candidate.interviewer_id = slot.interviewer_id
        else:
            unscheduled.append(candidate.candidate_id)
    
    conflicts = detect_conflicts(assignments)
    
    return {
        'assignments': assignments,
        'unscheduled': unscheduled,
        'conflicts': conflicts
    }
```

### LeaveManager

**Purpose**: Validate leave requests against policy rules and employee balances

**Interface**:
```python
class LeaveManager:
    def __init__(self, policies: Dict[str, LeavePolicy], employee_balances: Dict[str, Dict[str, int]]):
        """
        Args:
            policies: Dict mapping leave_type to LeavePolicy
            employee_balances: Dict mapping employee_id to dict of leave_type: remaining_days
        """
        
    def evaluate_request(
        self,
        request: LeaveRequest,
        existing_requests: List[LeaveRequest] = None
    ) -> Dict:
        """
        Evaluate leave request against policy rules.
        
        Args:
            request: LeaveRequest to evaluate
            existing_requests: List of existing requests for overlap checking
            
        Returns:
            Dict with keys:
                - 'status': 'approved' or 'denied'
                - 'reason': str (denial reason or 'approved')
                - 'policy_checks_passed': List[str] of passed checks
                - 'days_requested': int
        """
```

**Implementation Approach**:

1. **Policy Checks** (in order):
   - **Employee Existence**: Check if employee_id exists in employee_balances
   - **Date Range Validity**: Verify start_date <= end_date
   - **Days Calculation**: days_requested = (end_date - start_date).days + 1
   - **Balance Check**: Verify employee_balances[employee_id][leave_type] >= days_requested
   - **Consecutive Days Limit**: Verify days_requested <= policy.max_consecutive_days
   - **Notice Period**: Verify (start_date - current_date).days >= policy.min_notice_days
   - **Overlap Check**: Verify no existing requests overlap with [start_date, end_date]

2. **Short-Circuit Logic**:
   - Stop at first failed check
   - Set status = "denied" with specific reason
   - Track which checks passed in policy_checks_passed list

3. **Approval**:
   - If all checks pass, set status = "approved"
   - Include all checks in policy_checks_passed

4. **Supported Leave Types**:
   - annual, sick, personal, unpaid
   - Each has different policy rules (quota, max_consecutive, min_notice)

**Algorithm**:
```
function evaluate_request(request, existing_requests):
    policy = policies[request.leave_type]
    policy_checks_passed = []
    
    # Check 1: Employee exists
    if request.employee_id not in employee_balances:
        return {'status': 'denied', 'reason': 'employee_not_found', 'policy_checks_passed': [], 'days_requested': 0}
    policy_checks_passed.append('employee_exists')
    
    # Check 2: Valid date range
    if request.start_date > request.end_date:
        return {'status': 'denied', 'reason': 'invalid_date_range', 'policy_checks_passed': policy_checks_passed, 'days_requested': 0}
    policy_checks_passed.append('valid_date_range')
    
    # Check 3: Calculate days
    days_requested = (request.end_date - request.start_date).days + 1
    
    # Check 4: Sufficient balance
    balance = employee_balances[request.employee_id][request.leave_type]
    if days_requested > balance:
        return {'status': 'denied', 'reason': 'insufficient_balance', 'policy_checks_passed': policy_checks_passed, 'days_requested': days_requested}
    policy_checks_passed.append('sufficient_balance')
    
    # Check 5: Consecutive days limit
    if days_requested > policy.max_consecutive_days:
        return {'status': 'denied', 'reason': 'exceeds_max_consecutive_days', 'policy_checks_passed': policy_checks_passed, 'days_requested': days_requested}
    policy_checks_passed.append('within_consecutive_limit')
    
    # Check 6: Notice period
    notice_days = (request.start_date - current_date).days
    if notice_days < policy.min_notice_days:
        return {'status': 'denied', 'reason': 'insufficient_notice', 'policy_checks_passed': policy_checks_passed, 'days_requested': days_requested}
    policy_checks_passed.append('sufficient_notice')
    
    # Check 7: No overlaps
    if has_overlap(request, existing_requests):
        return {'status': 'denied', 'reason': 'overlapping_request', 'policy_checks_passed': policy_checks_passed, 'days_requested': days_requested}
    policy_checks_passed.append('no_overlaps')
    
    # All checks passed
    return {'status': 'approved', 'reason': 'approved', 'policy_checks_passed': policy_checks_passed, 'days_requested': days_requested}
```

### PipelineStateValidator

**Purpose**: Enforce valid state transitions in candidate pipeline

**Interface**:
```python
class PipelineStateValidator:
    def __init__(self):
        self.transition_log: List[Dict] = []
        
    def validate_transition(self, current_status: str, target_status: str) -> bool:
        """
        Check if transition is valid.
        
        Args:
            current_status: Current PipelineStatus value
            target_status: Target PipelineStatus value
            
        Returns:
            True if valid, False otherwise
        """
        
    def transition(self, candidate: Candidate, target_status: str) -> None:
        """
        Transition candidate to target status if valid.
        
        Args:
            candidate: Candidate to transition
            target_status: Target PipelineStatus value
            
        Raises:
            ValueError: If transition is invalid
        """
        
    def get_transition_log(self) -> List[Dict]:
        """
        Get log of all transitions.
        
        Returns:
            List of dicts with: timestamp, candidate_id, from_state, to_state
        """
```

**Implementation Approach**:

1. **Validation Logic**:
   - Use PipelineStatus.valid_transitions() dict
   - Check if target_status in valid_transitions[current_status]
   - Terminal states (hired, rejected) have empty transition lists

2. **Transition Execution**:
   - Validate transition first
   - If invalid, raise ValueError with message: "Invalid transition from {current} to {target}"
   - If valid, update candidate.status
   - Log transition with timestamp, candidate_id, from_state, to_state

3. **Integration with HRAgent**:
   - HRAgent calls validator.transition() instead of directly setting candidate.status
   - Used in screen_resumes() for applied→screened
   - Used in shortlist_top_n() for screened→interview_scheduled or screened→rejected

**Algorithm**:
```
function transition(candidate, target_status):
    current_status = candidate.status
    
    if not validate_transition(current_status, target_status):
        raise ValueError(f"Invalid transition from {current_status} to {target_status}")
    
    # Update status
    candidate.status = target_status
    
    # Log transition
    log_entry = {
        'timestamp': current_datetime(),
        'candidate_id': candidate.candidate_id,
        'from_state': current_status,
        'to_state': target_status
    }
    transition_log.append(log_entry)
    
function validate_transition(current_status, target_status):
    valid_targets = PipelineStatus.valid_transitions()[current_status]
    return target_status in valid_targets
```

### QueryEscalator

**Purpose**: Identify queries requiring human review

**Interface**:
```python
class QueryEscalator:
    def __init__(self, salary_threshold: float = 150000.0):
        """
        Args:
            salary_threshold: Salary above which to escalate (default: $150,000)
        """
        
    def evaluate_query(self, query: str, context: Dict = None) -> Dict:
        """
        Classify query and determine if escalation needed.
        
        Args:
            query: Query text to analyze
            context: Optional context dict with keys:
                - candidate: Candidate object
                - leave_request: LeaveRequest object
                - salary: float
                - position_level: str
                
        Returns:
            Dict with keys:
                - 'should_escalate': bool
                - 'reason': str
                - 'severity': 'low' | 'medium' | 'high'
                - 'recommended_action': str
        """
```

**Implementation Approach**:

1. **Keyword-Based Escalation** (High Severity):
   - Check query for sensitive keywords: "discrimination", "harassment", "legal", "lawsuit", "complaint", "grievance", "termination", "layoff"
   - If found, escalate with severity='high', reason='sensitive_keyword'

2. **Context-Based Escalation**:
   - **Salary Threshold** (Medium): If context['salary'] > salary_threshold
   - **Executive Position** (Medium): If context['position_level'] in ['VP', 'C-suite', 'Director', 'SVP', 'CTO', 'CEO', 'CFO', 'COO']
   - **Low Score Override** (Medium): If context['candidate'].match_score < 0.3 and being considered for interview
   - **Extended Leave** (Medium): If context['leave_request'].days > 15
   - **Stale Pipeline** (Low): If candidate in 'interview_scheduled' for > 30 days

3. **Recommended Actions**:
   - Generate human-readable explanation of why escalation is needed
   - Examples:
     - "Query contains sensitive legal keyword 'harassment' - requires HR manager review"
     - "Salary negotiation of $175,000 exceeds threshold - requires approval"
     - "Candidate has low match score (0.25) but being considered - requires justification"

**Algorithm**:
```
function evaluate_query(query, context):
    # Check for sensitive keywords
    sensitive_keywords = ['discrimination', 'harassment', 'legal', 'lawsuit', 'complaint', 'grievance', 'termination', 'layoff']
    for keyword in sensitive_keywords:
        if keyword in query.lower():
            return {
                'should_escalate': True,
                'reason': 'sensitive_keyword',
                'severity': 'high',
                'recommended_action': f"Query contains sensitive keyword '{keyword}' - requires immediate HR manager review"
            }
    
    # Check context-based escalations
    if context:
        # Salary threshold
        if 'salary' in context and context['salary'] > salary_threshold:
            return {
                'should_escalate': True,
                'reason': 'salary_threshold',
                'severity': 'medium',
                'recommended_action': f"Salary ${context['salary']} exceeds threshold - requires approval"
            }
        
        # Executive position
        if 'position_level' in context and context['position_level'] in executive_levels:
            return {
                'should_escalate': True,
                'reason': 'executive_position',
                'severity': 'medium',
                'recommended_action': f"Executive-level position ({context['position_level']}) - requires senior HR review"
            }
        
        # Low score override
        if 'candidate' in context and context['candidate'].match_score < 0.3:
            return {
                'should_escalate': True,
                'reason': 'low_score_override',
                'severity': 'medium',
                'recommended_action': f"Candidate score {context['candidate'].match_score} below threshold - requires justification"
            }
        
        # Extended leave
        if 'leave_request' in context:
            days = (context['leave_request'].end_date - context['leave_request'].start_date).days + 1
            if days > 15:
                return {
                    'should_escalate': True,
                    'reason': 'extended_leave',
                    'severity': 'medium',
                    'recommended_action': f"Leave request for {days} days exceeds 15-day limit - requires manager approval"
                }
        
        # Stale pipeline
        if 'candidate' in context and context['candidate'].status == 'interview_scheduled':
            # Check if status unchanged for > 30 days (requires status_updated_at field)
            if days_in_status(context['candidate']) > 30:
                return {
                    'should_escalate': True,
                    'reason': 'stale_pipeline',
                    'severity': 'low',
                    'recommended_action': "Candidate in interview_scheduled for >30 days - requires follow-up"
                }
    
    # No escalation needed
    return {
        'should_escalate': False,
        'reason': 'auto_handle',
        'severity': 'low',
        'recommended_action': 'Query can be handled automatically'
    }
```

## Data Models

### Extended Candidate Model

Add fields to existing Candidate dataclass:

```python
@dataclass
class Candidate:
    # Existing fields
    candidate_id: str
    name: str
    email: str
    resume_text: str
    skills: List[str] = field(default_factory=list)
    experience_years: float = 0.0
    match_score: float = 0.0
    explanation: Dict = field(default_factory=dict)
    status: str = "applied"
    
    # New fields
    interview_questions: List[Dict[str, str]] = field(default_factory=list)
    slot_id: Optional[str] = None
    interviewer_id: Optional[str] = None
    status_updated_at: datetime = field(default_factory=datetime.now)
```

### Employee Balance Model

New dataclass for leave management:

```python
@dataclass
class EmployeeBalance:
    employee_id: str
    annual_leave: int
    sick_leave: int
    personal_leave: int
    unpaid_leave: int
```

### Escalation Decision Model

New dataclass for query escalation:

```python
@dataclass
class EscalationDecision:
    should_escalate: bool
    reason: str
    severity: str  # 'low', 'medium', 'high'
    recommended_action: str
```

### Transition Log Entry Model

New dataclass for pipeline state tracking:

```python
@dataclass
class TransitionLogEntry:
    timestamp: datetime
    candidate_id: str
    from_state: str
    to_state: str
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:

**Redundant Properties to Consolidate:**
- 3.1 and 3.3 both test balance checking - combine into single property
- 3.4 and 3.5 both test consecutive days limit - combine into single property
- 3.8 and 3.9 both test overlap detection - combine into single property
- 6.7 and 7.6 both test MRR in export - keep only 7.6 as it's more comprehensive
- 4.5-4.10 are all specific examples of the general rule in 4.1 - keep as examples, not properties

**Properties Subsumed by Others:**
- 6.3 (MRR formula) subsumes 6.2 (rank finding) - the formula inherently requires finding the rank
- 2.3 (no duplicate slots) is ensured by 2.2 (marking slots unavailable) if implementation is correct

**Final Property Set:**
After reflection, we have 45 unique testable properties covering all functional requirements.

### Interview Question Generation Properties

### Property 1: Question Count Range

*For any* candidate being shortlisted for interview, the generated question set SHALL contain between 5 and 10 questions inclusive.

**Validates: Requirements 1.1**

### Property 2: Question Type Coverage

*For any* generated question set, it SHALL include at least one question of each type: technical, behavioral, and experience.

**Validates: Requirements 1.2**

### Property 3: Skill Reference in Questions

*For any* candidate with matched or missing skills in their explanation, at least one generated question SHALL reference skills from the candidate's explanation.

**Validates: Requirements 1.3**

### Property 4: Missing Skill Coverage

*For any* candidate with missing required skills, the generated question set SHALL include at least one question addressing each missing skill.

**Validates: Requirements 1.4**

### Property 5: Preferred Skill Coverage

*For any* candidate with matched preferred skills, the generated question set SHALL include at least one question about those preferred skills.

**Validates: Requirements 1.5**

### Property 6: Question Structure Validity

*For any* generated question, it SHALL have a 'type' field with value in {'technical', 'behavioral', 'experience'}.

**Validates: Requirements 1.6**

### Property 7: Question Storage

*For any* candidate after question generation, the candidate.interview_questions field SHALL contain the generated questions.

**Validates: Requirements 1.9**

### Interview Scheduling Properties

### Property 8: Unique Slot Assignment

*For any* candidate in a scheduling result, that candidate SHALL be assigned to at most one interview slot.

**Validates: Requirements 2.1**

### Property 9: Slot Availability Update

*For any* interview slot that is assigned to a candidate, the slot's is_available field SHALL be False.

**Validates: Requirements 2.2**

### Property 10: No Slot Conflicts

*For any* scheduling result, no slot_id SHALL appear more than once in the assignments list.

**Validates: Requirements 2.3**

### Property 11: Complete Candidate Accounting

*For any* scheduling operation with N candidates, the sum of assigned candidates and unscheduled candidates SHALL equal N.

**Validates: Requirements 2.5**

### Property 12: Valid Slot Time Range

*For any* interview slot used in scheduling, the start_time SHALL be strictly before end_time.

**Validates: Requirements 2.6**

### Property 13: Future Slot Times

*For any* interview slot used in scheduling, the start_time SHALL be after the current time.

**Validates: Requirements 2.7**

### Property 14: Assignment Data Consistency

*For any* candidate assigned to a slot, the candidate's slot_id and interviewer_id fields SHALL match the assigned slot's slot_id and interviewer_id.

**Validates: Requirements 2.8**

### Property 15: Scheduling Report Structure

*For any* scheduling result, it SHALL contain keys 'assignments', 'unscheduled', and 'conflicts', with conflicts equal to 0.

**Validates: Requirements 2.10**

### Property 16: Schedule Format Round-Trip

*For any* valid schedule object, formatting then parsing then formatting SHALL produce output equivalent to the first formatting.

**Validates: Requirements 2.11, 9.7**

### Leave Management Properties

### Property 17: Leave Balance Validation

*For any* leave request where requested days exceed the employee's remaining balance for that leave type, the decision status SHALL be "denied" with reason "insufficient_balance".

**Validates: Requirements 3.1, 3.3**

### Property 18: Days Calculation

*For any* leave request, the days_requested in the decision SHALL equal (end_date - start_date).days + 1.

**Validates: Requirements 3.2**

### Property 19: Consecutive Days Limit

*For any* leave request where requested days exceed the policy's max_consecutive_days, the decision status SHALL be "denied" with reason "exceeds_max_consecutive_days".

**Validates: Requirements 3.4, 3.5**

### Property 20: Notice Period Validation

*For any* leave request where (start_date - current_date).days is less than the policy's min_notice_days, the decision status SHALL be "denied" with reason "insufficient_notice".

**Validates: Requirements 3.7**

### Property 21: Overlap Detection

*For any* leave request that overlaps with an existing approved request from the same employee, the decision status SHALL be "denied" with reason "overlapping_request".

**Validates: Requirements 3.8, 3.9**

### Property 22: Leave Approval

*For any* leave request that passes all policy checks (balance, consecutive days, notice period, no overlaps), the decision status SHALL be "approved".

**Validates: Requirements 3.10**

### Property 23: Leave Decision Structure

*For any* leave request evaluation, the returned decision SHALL contain keys: 'status', 'reason', 'policy_checks_passed', and 'days_requested'.

**Validates: Requirements 3.11**

### Pipeline State Validation Properties

### Property 24: Valid Transition Enforcement

*For any* state transition attempt, if the target status is not in PipelineStatus.valid_transitions()[current_status], a ValueError SHALL be raised.

**Validates: Requirements 4.1, 4.4**

### Property 25: Terminal State Immutability - Hired

*For any* candidate with status "hired", attempting to transition to any other status SHALL raise a ValueError.

**Validates: Requirements 4.2**

### Property 26: Terminal State Immutability - Rejected

*For any* candidate with status "rejected", attempting to transition to any other status SHALL raise a ValueError.

**Validates: Requirements 4.3**

### Property 27: Transition Logging

*For any* successful state transition, a log entry SHALL be created containing timestamp, candidate_id, from_state, and to_state.

**Validates: Requirements 4.11**

### Query Escalation Properties

### Property 28: Escalation Classification

*For any* query, the escalation decision SHALL have a should_escalate field with boolean value.

**Validates: Requirements 5.1**

### Property 29: Sensitive Keyword Escalation

*For any* query containing keywords {"discrimination", "harassment", "legal", "lawsuit", "complaint", "grievance", "termination", "layoff"}, the decision SHALL have should_escalate=True.

**Validates: Requirements 5.2**

### Property 30: Salary Threshold Escalation

*For any* query with context containing salary > threshold, the decision SHALL have should_escalate=True with reason "salary_threshold".

**Validates: Requirements 5.3**

### Property 31: Executive Position Escalation

*For any* query with context containing position_level in {"VP", "C-suite", "Director", "SVP", "CTO", "CEO", "CFO", "COO"}, the decision SHALL have should_escalate=True.

**Validates: Requirements 5.4**

### Property 32: Low Score Override Escalation

*For any* query with context containing a candidate with match_score < 0.3, the decision SHALL have should_escalate=True with reason "low_score_override".

**Validates: Requirements 5.5**

### Property 33: Extended Leave Escalation

*For any* query with context containing a leave request exceeding 15 consecutive days, the decision SHALL have should_escalate=True with reason "extended_leave".

**Validates: Requirements 5.6**

### Property 34: Stale Pipeline Escalation

*For any* query with context containing a candidate in "interview_scheduled" status for more than 30 days, the decision SHALL have should_escalate=True with reason "stale_pipeline".

**Validates: Requirements 5.7**

### Property 35: Escalation Decision Structure

*For any* query evaluation, the returned decision SHALL contain keys: 'should_escalate', 'reason', 'severity', and 'recommended_action'.

**Validates: Requirements 5.8**

### Property 36: Severity Assignment

*For any* escalation with reason in {"sensitive_keyword"}, severity SHALL be "high"; for reason in {"salary_threshold", "executive_position", "extended_leave", "low_score_override"}, severity SHALL be "medium"; for reason "stale_pipeline", severity SHALL be "low".

**Validates: Requirements 5.9**

### Property 37: Recommended Action Presence

*For any* escalation where should_escalate=True, the recommended_action field SHALL be a non-empty string.

**Validates: Requirements 5.10**

### MRR Calculation Properties

### Property 38: MRR Formula

*For any* ranked candidate list and relevant candidate IDs, if a relevant candidate exists at rank R (1-indexed), the MRR SHALL equal 1/R.

**Validates: Requirements 6.2, 6.3**

### Property 39: Average MRR Calculation

*For any* list of MRR values, the average MRR SHALL equal the sum of all MRR values divided by the count of values.

**Validates: Requirements 6.6**

### Export Results Properties

### Property 40: Interview Questions in Export

*For any* shortlisted candidate, the export_results() output SHALL include that candidate's interview_questions.

**Validates: Requirements 7.1**

### Property 41: Schedule Assignments in Export

*For any* interview assignment, the export_results() output SHALL include the assignment with fields: slot_id, interviewer_id, start_time, and end_time.

**Validates: Requirements 7.2**

### Property 42: Leave Decisions in Export

*For any* processed leave request, the export_results() output SHALL include the decision with fields: status, reason, and policy_checks_passed.

**Validates: Requirements 7.3**

### Property 43: Transition History in Export

*For any* state transition that occurred, the export_results() output SHALL include the transition in the history.

**Validates: Requirements 7.4**

### Property 44: Escalation Decisions in Export

*For any* escalated query, the export_results() output SHALL include the escalation decision.

**Validates: Requirements 7.5, 7.6**

### Property 45: Backward Compatible Pipeline Structure

*For any* export_results() output, it SHALL contain the 'pipeline' structure with candidate data matching the original format.

**Validates: Requirements 7.7**

### Property 46: ISO 8601 Datetime Format

*For any* datetime object in export_results() output, it SHALL be formatted as an ISO 8601 string.

**Validates: Requirements 7.8**

### Property 47: Metadata Section Presence

*For any* export_results() output, it SHALL contain a 'metadata' section with 'timestamp' and 'version' fields.

**Validates: Requirements 7.9**

### Property 48: JSON Serialization

*For any* export_results() output, calling json.dumps() on it SHALL succeed without raising exceptions.

**Validates: Requirements 7.10**

### Integration Properties

### Property 49: Screen Resumes State Transition

*For any* candidate processed by screen_resumes(), the candidate's status SHALL transition from "applied" to "screened".

**Validates: Requirements 8.2**

### Property 50: Shortlist Question Generation

*For any* candidate shortlisted by shortlist_top_n(), that candidate SHALL have interview_questions populated.

**Validates: Requirements 8.3**

### Property 51: Shortlist Interview Scheduling

*For any* candidate shortlisted by shortlist_top_n(), if slots are available, that candidate SHALL be assigned to a slot.

**Validates: Requirements 8.4**

### Property 52: Shortlist Status Transition

*For any* candidate shortlisted by shortlist_top_n(), that candidate's status SHALL be "interview_scheduled".

**Validates: Requirements 8.5**

### Property 53: Rejection Status Transition

*For any* candidate not shortlisted by shortlist_top_n(), that candidate's status SHALL be "rejected".

**Validates: Requirements 8.6**

### Schedule Formatting Properties

### Property 54: Schedule Content Completeness

*For any* formatted schedule, it SHALL include candidate name, interviewer ID, date, and time range for each interview.

**Validates: Requirements 9.2**

### Property 55: Chronological Ordering

*For any* formatted schedule with multiple interviews, the interviews SHALL be ordered by start_time in ascending order.

**Validates: Requirements 9.3**

### Property 56: 12-Hour Time Format

*For any* formatted schedule, all times SHALL be in 12-hour format with AM/PM indicators.

**Validates: Requirements 9.4**

### Property 57: Date Grouping

*For any* formatted schedule with interviews on multiple dates, interviews SHALL be grouped by date.

**Validates: Requirements 9.5**

### Property 58: Schedule Parse Validation

*For any* invalid datetime format in schedule parsing, a ValueError SHALL be raised.

**Validates: Requirements 9.6**

## Error Handling

### Error Handling Strategy

The system implements defensive programming with graceful degradation:

1. **Input Validation**
   - Validate all inputs at component boundaries
   - Raise ValueError with descriptive messages for invalid inputs
   - Log validation failures at WARNING level

2. **Service Failures**
   - LLM service failures trigger fallback to template-based generation
   - Log service failures at ERROR level with component name and operation
   - Continue operation with degraded functionality

3. **Edge Cases**
   - Empty inputs return empty results without exceptions
   - Missing data returns appropriate error responses (e.g., "employee_not_found")
   - Invalid state transitions raise ValueError with clear messages

4. **Logging Standards**
   - ERROR level: Service failures, unexpected exceptions, data integrity issues
   - WARNING level: Input validation failures, edge cases handled
   - INFO level: Normal operations, state transitions, scheduling results
   - All logs include: component name, operation, relevant IDs, error details

### Component-Specific Error Handling

**InterviewQuestionGenerator**
- LLM timeout (>5s): Fall back to template generation
- LLM service unavailable: Fall back to template generation
- Invalid candidate data: Log warning, generate generic questions

**InterviewScheduler**
- Invalid slot times: Filter out invalid slots, log warning
- Insufficient slots: Schedule as many as possible, return unscheduled list
- Past slot times: Filter out past slots, log warning

**LeaveManager**
- Missing employee: Return denial with reason "employee_not_found"
- Invalid date range: Return denial with reason "invalid_date_range"
- Missing policy: Raise ValueError (configuration error)

**PipelineStateValidator**
- Invalid transition: Raise ValueError with descriptive message
- Invalid status value: Raise ValueError with valid status list
- Missing candidate: Raise ValueError

**QueryEscalator**
- Empty query: Return should_escalate=False
- Missing context: Evaluate based on query text only
- Invalid context data: Log warning, skip context-based checks

**HRAgent**
- Empty candidate list: Return empty results
- Empty job description: Use default scoring weights
- Component initialization failure: Raise RuntimeError with component name

## Testing Strategy

### Dual Testing Approach

The system requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples demonstrating correct behavior
- Edge cases (empty inputs, invalid data, boundary conditions)
- Error conditions and exception handling
- Integration points between components
- Backward compatibility with existing API

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants and round-trip properties
- State transition rules
- Data consistency across components

### Property-Based Testing Configuration

**Library Selection**: Use `hypothesis` for Python property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test references its design document property
- Tag format: `# Feature: complete-hr-agent-requirements, Property {number}: {property_text}`

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st

# Feature: complete-hr-agent-requirements, Property 1: Question Count Range
@given(candidate=st.builds(Candidate, ...))
def test_question_count_range(candidate):
    generator = InterviewQuestionGenerator()
    questions = generator.generate_questions(candidate, job_description)
    assert 5 <= len(questions) <= 10
```

### Test Coverage Requirements

**Interview Question Generation**:
- Property tests: Question count, type coverage, skill coverage, structure validity
- Unit tests: LLM fallback, template generation, specific skill scenarios
- Edge cases: Empty skills, no missing skills, LLM timeout

**Interview Scheduling**:
- Property tests: Unique assignment, no conflicts, complete accounting, time validation
- Unit tests: Interviewer distribution, specific scheduling scenarios
- Edge cases: Empty slots, empty candidates, all slots in past

**Leave Management**:
- Property tests: Balance validation, consecutive days, notice period, overlap detection
- Unit tests: Each leave type, specific policy scenarios
- Edge cases: Invalid date range, missing employee, boundary dates

**Pipeline State Validation**:
- Property tests: Valid transitions, terminal state immutability, logging
- Unit tests: Each specific transition rule (applied→screened, etc.)
- Edge cases: Invalid status values, missing candidate

**Query Escalation**:
- Property tests: Keyword detection, threshold checks, severity assignment
- Unit tests: Each escalation reason, specific keyword scenarios
- Edge cases: Empty query, missing context, boundary values

**MRR Calculation**:
- Property tests: MRR formula, average calculation
- Unit tests: Specific ranking scenarios
- Edge cases: No relevant candidates, first candidate relevant, empty list

**Export Results**:
- Property tests: Structure completeness, JSON serialization, datetime formatting
- Unit tests: Backward compatibility, specific export scenarios
- Edge cases: Empty pipeline, no interviews scheduled

**Integration**:
- Property tests: State transitions, workflow completeness
- Unit tests: Component interaction, method signatures
- Edge cases: Component initialization failures, missing dependencies

### Test Data Generation

Use `hypothesis` strategies to generate:
- Candidates with random skills, experience, scores
- Job descriptions with random required/preferred skills
- Interview slots with random times (ensuring validity)
- Leave requests with random dates and types
- Queries with random keywords and context

### Continuous Testing

- Run property tests with 100 iterations in CI/CD
- Run unit tests on every commit
- Track test coverage (target: >90% line coverage)
- Monitor property test failure rates
- Investigate and fix any property test failures immediately

