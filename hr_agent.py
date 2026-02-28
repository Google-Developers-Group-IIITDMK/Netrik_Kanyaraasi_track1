import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIG
# =====================================================

CONFIG = {
    "team_id": "Kanyaraasi",  # TODO: Update with your team name
    "track": "track_1_hr_agent"
}

# =====================================================
# PIPELINE STATES
# =====================================================

class PipelineStatus(Enum):
    APPLIED = "applied"
    SCREENED = "screened"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_EXTENDED = "offer_extended"
    OFFER_ACCEPTED = "offer_accepted"
    HIRED = "hired"
    REJECTED = "rejected"

    @staticmethod
    def valid_transitions():
        return {
            "applied": ["screened", "rejected"],
            "screened": ["interview_scheduled", "rejected"],
            "interview_scheduled": ["interviewed", "rejected"],
            "interviewed": ["offer_extended", "rejected"],
            "offer_extended": ["offer_accepted", "rejected"],
            "offer_accepted": ["hired", "rejected"],
            "hired": [],
            "rejected": [],
        }

# =====================================================
# DATA MODELS
# =====================================================

@dataclass
class Candidate:
    candidate_id: str
    name: str
    email: str
    resume_text: str
    skills: List[str] = field(default_factory=list)
    experience_years: float = 0.0
    match_score: float = 0.0
    explanation: Dict = field(default_factory=dict)
    status: str = "applied"
    # New fields for interview and scheduling
    interview_questions: List[Dict[str, str]] = field(default_factory=list)
    slot_id: Optional[str] = None
    interviewer_id: Optional[str] = None
    status_updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class JobDescription:
    job_id: str
    title: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience: float

@dataclass
class InterviewSlot:
    slot_id: str
    interviewer_id: str
    start_time: datetime
    end_time: datetime
    is_available: bool = True

@dataclass
class LeaveRequest:
    request_id: str
    employee_id: str
    leave_type: str
    start_date: datetime
    end_date: datetime
    reason: str
    status: str = "pending"

@dataclass
class LeavePolicy:
    leave_type: str
    annual_quota: int
    max_consecutive_days: int
    min_notice_days: int

@dataclass
class EmployeeBalance:
    employee_id: str
    annual_leave: int
    sick_leave: int
    personal_leave: int
    unpaid_leave: int

# =====================================================
# ABSTRACT CLASS
# =====================================================

class ResumeScreener(ABC):

    @abstractmethod
    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        pass

# =====================================================
# SMART RANKING ENGINE WITH SKILL GAP ANALYSIS
# =====================================================

class PipelineStateValidator:
    """Validates and enforces pipeline state transitions"""
    
    def __init__(self):
        self.transition_log: List[Dict] = []
    
    def validate_transition(self, current_status: str, target_status: str) -> bool:
        """
        Check if transition is valid according to PipelineStatus rules.
        
        Args:
            current_status: Current pipeline status
            target_status: Target pipeline status
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = PipelineStatus.valid_transitions()
        return target_status in valid_transitions.get(current_status, [])
    
    def transition(self, candidate: Candidate, target_status: str) -> None:
        """
        Transition candidate to target status if valid, otherwise raise ValueError.
        
        Args:
            candidate: Candidate to transition
            target_status: Target pipeline status
            
        Raises:
            ValueError: If transition is invalid
        """
        current_status = candidate.status
        
        if not self.validate_transition(current_status, target_status):
            raise ValueError(
                f"Invalid transition from {current_status} to {target_status}"
            )
        
        # Update status
        candidate.status = target_status
        candidate.status_updated_at = datetime.now()
        
        # Log transition
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'candidate_id': candidate.candidate_id,
            'from_state': current_status,
            'to_state': target_status
        }
        self.transition_log.append(log_entry)
        
        logger.info(
            f"Transitioned candidate {candidate.candidate_id} from "
            f"{current_status} to {target_status}"
        )
    
    def get_transition_log(self) -> List[Dict]:
        """Get log of all transitions"""
        return self.transition_log


class InterviewQuestionGenerator:
    """Generates role-specific interview questions for candidates"""
    
    def __init__(self, use_llm: bool = True, bedrock_client=None):
        """
        Initialize question generator.
        
        Args:
            use_llm: Whether to attempt LLM-based generation
            bedrock_client: AWS Bedrock client (optional)
        """
        self.use_llm = use_llm
        self.bedrock_client = bedrock_client
        
        # Question templates for fallback
        self.technical_templates = [
            "Explain your experience with {skill} and provide a specific example.",
            "How would you approach a problem involving {skill}?",
            "Describe a challenging project where you used {skill}.",
            "What are the key considerations when working with {skill}?",
        ]
        
        self.behavioral_templates = [
            "Describe a situation where you had to learn {skill} quickly. What was the outcome?",
            "Tell me about a time when you used {skill} to solve a difficult problem.",
            "Give an example of how you've applied {skill} in a team setting.",
        ]
        
        self.experience_templates = [
            "How many years of experience do you have with {skill}?",
            "What projects have you completed using {skill}?",
        ]
    
    def generate_template_questions(
        self, 
        missing_skills: List[str],
        matched_skills: List[str],
        preferred_skills: List[str]
    ) -> List[Dict[str, str]]:
        """Generate questions using templates"""
        questions = []
        
        # Generate questions for missing required skills (priority)
        for skill in missing_skills[:3]:  # Focus on top 3 missing skills
            questions.append({
                'question': f"We noticed {skill} is required for this role. Describe your experience with {skill} or similar technologies.",
                'type': 'technical',
                'skill_focus': skill
            })
        
        # Generate questions for matched preferred skills
        for skill in preferred_skills[:2]:
            questions.append({
                'question': f"Tell me about a time when you used {skill} to solve a problem.",
                'type': 'behavioral',
                'skill_focus': skill
            })
        
        # Add general behavioral questions
        questions.append({
            'question': "Describe a situation where you had to learn a new technology quickly. What approach did you take?",
            'type': 'behavioral',
            'skill_focus': 'adaptability'
        })
        
        questions.append({
            'question': "Tell me about a challenging technical problem you solved. What was your approach?",
            'type': 'experience',
            'skill_focus': 'problem-solving'
        })
        
        # Add situational question
        questions.append({
            'question': "How do you prioritize tasks when working on multiple projects with tight deadlines?",
            'type': 'behavioral',
            'skill_focus': 'time-management'
        })
        
        return questions
    
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
        """
        # Extract skills from candidate explanation
        missing_skills = candidate.explanation.get('missing_required_skills', [])
        matched_skills = candidate.explanation.get('matched_required_skills', [])
        preferred_skills = candidate.explanation.get('matched_preferred_skills', [])
        
        questions = []
        
        # Try LLM generation if enabled
        if self.use_llm and self.bedrock_client:
            try:
                questions = self._generate_with_llm(
                    candidate, job_description, missing_skills, matched_skills, preferred_skills
                )
            except Exception as e:
                logger.warning(f"LLM generation failed: {e}. Falling back to templates.")
                questions = self.generate_template_questions(
                    missing_skills, matched_skills, preferred_skills
                )
        else:
            questions = self.generate_template_questions(
                missing_skills, matched_skills, preferred_skills
            )
        
        # Ensure 5-10 questions
        if len(questions) < 5:
            # Add general questions to reach minimum
            general_questions = [
                {
                    'question': "What interests you most about this role?",
                    'type': 'behavioral',
                    'skill_focus': 'motivation'
                },
                {
                    'question': "Describe your ideal work environment and team structure.",
                    'type': 'behavioral',
                    'skill_focus': 'culture-fit'
                }
            ]
            questions.extend(general_questions[:5 - len(questions)])
        
        if len(questions) > 10:
            questions = questions[:10]
        
        # Store in candidate
        candidate.interview_questions = questions
        
        return questions
    
    def _generate_with_llm(
        self,
        candidate: Candidate,
        job_description: JobDescription,
        missing_skills: List[str],
        matched_skills: List[str],
        preferred_skills: List[str]
    ) -> List[Dict[str, str]]:
        """Generate questions using AWS Bedrock LLM"""
        import json
        
        prompt = f"""Generate 7 interview questions for a candidate applying for: {job_description.title}

Candidate Profile:
- Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
- Missing Required Skills: {', '.join(missing_skills) if missing_skills else 'None'}
- Matched Preferred Skills: {', '.join(preferred_skills) if preferred_skills else 'None'}
- Experience: {candidate.experience_years} years

Generate a mix of:
- Technical questions (focus on missing skills and matched skills)
- Behavioral questions (STAR format)
- Situational questions

Return ONLY a JSON array with this exact format:
[
  {{"question": "...", "type": "technical", "skill_focus": "skill_name"}},
  {{"question": "...", "type": "behavioral", "skill_focus": "skill_name"}}
]

Types must be: technical, behavioral, or experience"""

        response = self.bedrock_client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            })
        )
        
        result = json.loads(response['body'].read())
        content = result['content'][0]['text']
        
        # Parse JSON from response
        questions = json.loads(content)
        
        return questions


class InterviewScheduler:
    """Assigns candidates to interview slots without conflicts"""
    
    def __init__(self):
        pass
    
    def validate_slot(self, slot: InterviewSlot) -> bool:
        """
        Validate that a slot has valid timing.
        
        Args:
            slot: InterviewSlot to validate
            
        Returns:
            True if slot is valid, False otherwise
        """
        # Check start_time < end_time
        if slot.start_time >= slot.end_time:
            logger.warning(
                f"Invalid slot {slot.slot_id}: start_time >= end_time"
            )
            return False
        
        # Check slot is in the future
        if slot.start_time <= datetime.now():
            logger.warning(
                f"Invalid slot {slot.slot_id}: start_time is in the past"
            )
            return False
        
        return True
    
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
        # Validate and filter slots
        valid_slots = [s for s in slots if self.validate_slot(s)]
        available_slots = [s for s in valid_slots if s.is_available]
        
        # Group slots by interviewer
        from collections import defaultdict
        interviewer_slots = defaultdict(list)
        for slot in available_slots:
            interviewer_slots[slot.interviewer_id].append(slot)
        
        # Sort candidates by match_score (descending)
        sorted_candidates = sorted(
            candidates,
            key=lambda c: c.match_score,
            reverse=True
        )
        
        assignments = []
        unscheduled = []
        
        for candidate in sorted_candidates:
            # Find interviewer with most available slots
            if interviewer_slots:
                interviewer = max(
                    interviewer_slots.keys(),
                    key=lambda i: len(interviewer_slots[i])
                )
                
                if interviewer_slots[interviewer]:
                    slot = interviewer_slots[interviewer].pop(0)
                    slot.is_available = False
                    
                    assignment = {
                        'candidate_id': candidate.candidate_id,
                        'candidate_name': candidate.name,
                        'slot_id': slot.slot_id,
                        'interviewer_id': slot.interviewer_id,
                        'start_time': slot.start_time.isoformat(),
                        'end_time': slot.end_time.isoformat()
                    }
                    assignments.append(assignment)
                    
                    # Update candidate object
                    candidate.slot_id = slot.slot_id
                    candidate.interviewer_id = slot.interviewer_id
                    
                    # Remove interviewer from dict if no more slots
                    if not interviewer_slots[interviewer]:
                        del interviewer_slots[interviewer]
                else:
                    unscheduled.append(candidate.candidate_id)
            else:
                unscheduled.append(candidate.candidate_id)
        
        # Detect conflicts (should be 0)
        conflicts = self._detect_conflicts(assignments)
        
        return {
            'assignments': assignments,
            'unscheduled': unscheduled,
            'conflicts': conflicts
        }
    
    def _detect_conflicts(self, assignments: List[Dict]) -> int:
        """Detect scheduling conflicts"""
        slot_ids = [a['slot_id'] for a in assignments]
        return len(slot_ids) - len(set(slot_ids))
    
    def format_schedule(self, assignments: List[Dict]) -> str:
        """
        Format schedule in human-readable format.
        
        Args:
            assignments: List of assignment dicts
            
        Returns:
            Multi-line string with interviews sorted by time, grouped by date
        """
        if not assignments:
            return "No interviews scheduled."
        
        # Sort by start_time
        sorted_assignments = sorted(
            assignments,
            key=lambda a: a['start_time']
        )
        
        # Group by date
        from collections import defaultdict
        by_date = defaultdict(list)
        
        for assignment in sorted_assignments:
            start_dt = datetime.fromisoformat(assignment['start_time'])
            date_key = start_dt.strftime('%Y-%m-%d')
            by_date[date_key].append(assignment)
        
        # Format output
        lines = []
        for date_key in sorted(by_date.keys()):
            lines.append(f"\nDate: {date_key}")
            for assignment in by_date[date_key]:
                start_dt = datetime.fromisoformat(assignment['start_time'])
                end_dt = datetime.fromisoformat(assignment['end_time'])
                
                start_time = start_dt.strftime('%I:%M %p')
                end_time = end_dt.strftime('%I:%M %p')
                
                lines.append(
                    f"  {start_time} - {end_time}: {assignment['candidate_name']} "
                    f"with Interviewer {assignment['interviewer_id']}"
                )
        
        return '\n'.join(lines)


class LeaveManager:
    """Validates leave requests against policy rules and employee balances"""
    
    def __init__(
        self,
        policies: Dict[str, LeavePolicy],
        employee_balances: Dict[str, Dict[str, int]]
    ):
        """
        Initialize leave manager.
        
        Args:
            policies: Dict mapping leave_type to LeavePolicy
            employee_balances: Dict mapping employee_id to dict of leave_type: remaining_days
        """
        self.policies = policies
        self.employee_balances = employee_balances
    
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
        policy_checks_passed = []
        
        # Check 1: Employee exists
        if request.employee_id not in self.employee_balances:
            return {
                'status': 'denied',
                'reason': 'employee_not_found',
                'policy_checks_passed': [],
                'days_requested': 0
            }
        policy_checks_passed.append('employee_exists')
        
        # Check 2: Valid date range
        if request.start_date > request.end_date:
            return {
                'status': 'denied',
                'reason': 'invalid_date_range',
                'policy_checks_passed': policy_checks_passed,
                'days_requested': 0
            }
        policy_checks_passed.append('valid_date_range')
        
        # Check 3: Calculate days
        days_requested = (request.end_date - request.start_date).days + 1
        
        # Check 4: Policy exists for leave type
        if request.leave_type not in self.policies:
            return {
                'status': 'denied',
                'reason': 'invalid_leave_type',
                'policy_checks_passed': policy_checks_passed,
                'days_requested': days_requested
            }
        
        policy = self.policies[request.leave_type]
        
        # Check 5: Sufficient balance
        balance = self.employee_balances[request.employee_id].get(request.leave_type, 0)
        if days_requested > balance:
            return {
                'status': 'denied',
                'reason': 'insufficient_balance',
                'policy_checks_passed': policy_checks_passed,
                'days_requested': days_requested,
                'remaining_balance': balance
            }
        policy_checks_passed.append('sufficient_balance')
        
        # Check 6: Consecutive days limit
        if days_requested > policy.max_consecutive_days:
            return {
                'status': 'denied',
                'reason': 'exceeds_max_consecutive_days',
                'policy_checks_passed': policy_checks_passed,
                'days_requested': days_requested
            }
        policy_checks_passed.append('within_consecutive_limit')
        
        # Check 7: Notice period
        notice_days = (request.start_date - datetime.now()).days
        if notice_days < policy.min_notice_days:
            return {
                'status': 'denied',
                'reason': 'insufficient_notice',
                'policy_checks_passed': policy_checks_passed,
                'days_requested': days_requested
            }
        policy_checks_passed.append('sufficient_notice')
        
        # Check 8: No overlaps
        if existing_requests:
            if self._has_overlap(request, existing_requests):
                return {
                    'status': 'denied',
                    'reason': 'overlapping_request',
                    'policy_checks_passed': policy_checks_passed,
                    'days_requested': days_requested
                }
        policy_checks_passed.append('no_overlaps')
        
        # All checks passed
        return {
            'status': 'approved',
            'reason': 'approved',
            'policy_checks_passed': policy_checks_passed,
            'days_requested': days_requested,
            'remaining_balance': balance - days_requested
        }
    
    def _has_overlap(
        self,
        request: LeaveRequest,
        existing_requests: List[LeaveRequest]
    ) -> bool:
        """Check if request overlaps with existing requests from same employee"""
        for existing in existing_requests:
            if existing.employee_id == request.employee_id:
                # Check for date overlap
                if (request.start_date <= existing.end_date and
                    request.end_date >= existing.start_date):
                    return True
        return False


class QueryEscalator:
    """Identifies queries requiring human review"""
    
    def __init__(self, salary_threshold: float = 150000.0):
        """
        Initialize query escalator.
        
        Args:
            salary_threshold: Salary above which to escalate (default: $150,000)
        """
        self.salary_threshold = salary_threshold
        
        self.sensitive_keywords = [
            'discrimination', 'harassment', 'legal', 'lawsuit',
            'complaint', 'grievance', 'termination', 'layoff'
        ]
        
        self.executive_levels = [
            'VP', 'C-suite', 'Director', 'SVP', 'CTO', 'CEO', 'CFO', 'COO', 'CIO'
        ]
    
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
        # Handle empty query
        if not query or not query.strip():
            return {
                'should_escalate': False,
                'reason': 'auto_handle',
                'severity': 'low',
                'recommended_action': 'Query can be handled automatically'
            }
        
        query_lower = query.lower()
        
        # Check for sensitive keywords (high severity)
        for keyword in self.sensitive_keywords:
            if keyword in query_lower:
                return {
                    'should_escalate': True,
                    'reason': 'sensitive_keyword',
                    'severity': 'high',
                    'recommended_action': f"Query contains sensitive keyword '{keyword}' - requires immediate HR manager review"
                }
        
        # Check context-based escalations
        if context:
            # Salary threshold (medium severity)
            if 'salary' in context and context['salary'] > self.salary_threshold:
                return {
                    'should_escalate': True,
                    'reason': 'salary_threshold',
                    'severity': 'medium',
                    'recommended_action': f"Salary ${context['salary']:,.0f} exceeds threshold - requires approval"
                }
            
            # Executive position (medium severity)
            if 'position_level' in context and context['position_level'] in self.executive_levels:
                return {
                    'should_escalate': True,
                    'reason': 'executive_position',
                    'severity': 'medium',
                    'recommended_action': f"Executive-level position ({context['position_level']}) - requires senior HR review"
                }
            
            # Low score override (medium severity)
            if 'candidate' in context and context['candidate'].match_score < 0.3:
                return {
                    'should_escalate': True,
                    'reason': 'low_score_override',
                    'severity': 'medium',
                    'recommended_action': f"Candidate score {context['candidate'].match_score:.2f} below threshold - requires justification"
                }
            
            # Extended leave (medium severity)
            if 'leave_request' in context:
                leave_req = context['leave_request']
                days = (leave_req.end_date - leave_req.start_date).days + 1
                if days > 15:
                    return {
                        'should_escalate': True,
                        'reason': 'extended_leave',
                        'severity': 'medium',
                        'recommended_action': f"Leave request for {days} days exceeds 15-day limit - requires manager approval"
                    }
            
            # Stale pipeline (low severity)
            if 'candidate' in context:
                candidate = context['candidate']
                if candidate.status == 'interview_scheduled':
                    days_in_status = (datetime.now() - candidate.status_updated_at).days
                    if days_in_status > 30:
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


class SmartResumeScreener(ResumeScreener):

    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:

        required = {s.lower().strip() for s in jd.required_skills}
        preferred = {s.lower().strip() for s in jd.preferred_skills}

        for c in candidates:

            candidate_skills = {s.lower().strip() for s in c.skills}

            matched_required = required & candidate_skills
            missing_required = required - candidate_skills
            skill_score = len(matched_required) / len(required) if required else 0

            matched_preferred = preferred & candidate_skills
            preferred_score = len(matched_preferred) / len(preferred) if preferred else 0

            exp_score = min(c.experience_years / jd.min_experience, 1.0) if jd.min_experience else 1

            word_count = len(c.resume_text.split())
            quality_score = min(word_count / 200, 1.0)

            final_score = (
                0.6 * skill_score +
                0.1 * preferred_score +
                0.2 * exp_score +
                0.1 * quality_score
            )

            c.match_score = round(final_score, 4)

            readiness = round(skill_score * 100, 2)

            c.explanation = {
                "matched_required_skills": list(matched_required),
                "missing_required_skills": list(missing_required),
                "matched_preferred_skills": list(matched_preferred),
                "experience_years": c.experience_years,
                "readiness_percentage": readiness,
                "final_score": c.match_score
            }

        sorted_candidates = sorted(
            candidates,
            key=lambda x: x.match_score,
            reverse=True
        )

        return sorted_candidates

# =====================================================
# HR AGENT
# =====================================================

class HRAgent:

    def __init__(
        self,
        use_llm: bool = False,
        bedrock_client=None,
        leave_policies: Dict[str, LeavePolicy] = None,
        employee_balances: Dict[str, Dict[str, int]] = None,
        salary_threshold: float = 150000.0
    ):
        """
        Initialize HR Agent with all components.
        
        Args:
            use_llm: Whether to use LLM for question generation
            bedrock_client: AWS Bedrock client (optional)
            leave_policies: Dict mapping leave_type to LeavePolicy
            employee_balances: Dict mapping employee_id to leave balances
            salary_threshold: Salary threshold for escalation
        """
        self.screener = SmartResumeScreener()
        self.pipeline: Dict[str, Candidate] = {}
        
        # Initialize new components
        self.state_validator = PipelineStateValidator()
        self.question_generator = InterviewQuestionGenerator(use_llm, bedrock_client)
        self.scheduler = InterviewScheduler()
        
        # Initialize leave manager with default policies if not provided
        if leave_policies is None:
            leave_policies = {
                'annual': LeavePolicy('annual', 20, 15, 7),
                'sick': LeavePolicy('sick', 10, 5, 0),
                'personal': LeavePolicy('personal', 5, 3, 3),
                'unpaid': LeavePolicy('unpaid', 30, 30, 14)
            }
        
        if employee_balances is None:
            employee_balances = {}
        
        self.leave_manager = LeaveManager(leave_policies, employee_balances)
        self.query_escalator = QueryEscalator(salary_threshold)
        
        # Storage for additional results
        self.interview_schedule = {}
        self.leave_decisions = []
        self.escalation_decisions = []

    def screen_resumes(self, candidates: List[Candidate], jd: JobDescription):
        """Screen and rank candidates, updating pipeline state"""
        # Transition candidates from applied to screened using validator
        for c in candidates:
            try:
                self.state_validator.transition(c, "screened")
            except ValueError as e:
                logger.warning(f"Could not transition candidate {c.candidate_id}: {e}")
                c.status = "screened"  # Fallback for backward compatibility

        ranked = self.screener.rank_candidates(candidates, jd)

        for c in ranked:
            self.pipeline[c.candidate_id] = c

        return ranked

    def shortlist_top_n(
        self, 
        n: int, 
        interview_slots: List[InterviewSlot] = None,
        jd: JobDescription = None
    ):
        """
        Shortlist top N candidates, generate questions, and schedule interviews.
        
        Args:
            n: Number of candidates to shortlist
            interview_slots: Available interview slots (optional)
            jd: Job description for question generation (optional)
            
        Returns:
            List of shortlisted candidates
        """
        sorted_candidates = sorted(
            self.pipeline.values(),
            key=lambda x: x.match_score,
            reverse=True
        )

        shortlisted = sorted_candidates[:n]
        rejected = sorted_candidates[n:]
        
        # Generate interview questions for shortlisted candidates
        if jd:
            for c in shortlisted:
                try:
                    self.question_generator.generate_questions(c, jd)
                except Exception as e:
                    logger.error(f"Failed to generate questions for {c.candidate_id}: {e}")
        
        # Schedule interviews if slots provided
        if interview_slots:
            schedule_result = self.scheduler.schedule_interviews(shortlisted, interview_slots)
            self.interview_schedule = schedule_result
        
        # Update statuses using state validator
        for c in shortlisted:
            try:
                self.state_validator.transition(c, "interview_scheduled")
            except ValueError as e:
                logger.warning(f"Could not transition candidate {c.candidate_id}: {e}")
                c.status = "interview_scheduled"
        
        for c in rejected:
            try:
                self.state_validator.transition(c, "rejected")
            except ValueError as e:
                logger.warning(f"Could not transition candidate {c.candidate_id}: {e}")
                c.status = "rejected"

        return shortlisted
    
    def process_leave_request(
        self,
        request: LeaveRequest,
        existing_requests: List[LeaveRequest] = None
    ) -> Dict:
        """
        Process a leave request and return decision.
        
        Args:
            request: LeaveRequest to evaluate
            existing_requests: List of existing requests for overlap checking
            
        Returns:
            Decision dict with status, reason, policy_checks_passed, days_requested
        """
        decision = self.leave_manager.evaluate_request(request, existing_requests)
        self.leave_decisions.append({
            'request_id': request.request_id,
            'employee_id': request.employee_id,
            'decision': decision
        })
        return decision
    
    def escalate_query(self, query: str, context: Dict = None) -> Dict:
        """
        Evaluate if a query should be escalated to human review.
        
        Args:
            query: Query text to analyze
            context: Optional context dict
            
        Returns:
            Escalation decision dict
        """
        decision = self.query_escalator.evaluate_query(query, context)
        self.escalation_decisions.append({
            'query': query,
            'decision': decision
        })
        return decision
    
    def calculate_mrr(
        self,
        ranked_candidates: List[Candidate],
        relevant_candidate_ids: List[str]
    ) -> float:
        """
        Calculate Mean Reciprocal Rank for ranking quality.
        
        Args:
            ranked_candidates: List of candidates in ranked order
            relevant_candidate_ids: List of candidate IDs considered relevant
            
        Returns:
            MRR score (0.0 to 1.0)
        """
        for rank, candidate in enumerate(ranked_candidates, start=1):
            if candidate.candidate_id in relevant_candidate_ids:
                return 1.0 / rank
        return 0.0

    def export_results(self):
        """Export comprehensive results in evaluation format"""
        return {
            "team_id": CONFIG["team_id"],
            "track": CONFIG["track"],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "results": {
                "pipeline": {
                    cid: {
                        "name": c.name,
                        "status": c.status,
                        "score": c.match_score,
                        "explanation": c.explanation,
                        "interview_questions": c.interview_questions,
                        "slot_id": c.slot_id,
                        "interviewer_id": c.interviewer_id
                    }
                    for cid, c in self.pipeline.items()
                },
                "interview_schedule": self.interview_schedule,
                "leave_decisions": self.leave_decisions,
                "escalation_decisions": self.escalation_decisions,
                "transition_log": self.state_validator.get_transition_log()
            }
        }