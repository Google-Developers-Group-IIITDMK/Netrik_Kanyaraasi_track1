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
    "team_id": "YOUR_TEAM_NAME",
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

# =====================================================
# ABSTRACT CLASSES
# =====================================================

class ResumeScreener(ABC):

    @abstractmethod
    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        pass

# =====================================================
# SMART RANKING ENGINE
# =====================================================

class SmartResumeScreener(ResumeScreener):

    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:

        required = {s.lower().strip() for s in jd.required_skills}
        preferred = {s.lower().strip() for s in jd.preferred_skills}

        for c in candidates:

            candidate_skills = {s.lower().strip() for s in c.skills}

            # Required skill score (60%)
            matched_required = required & candidate_skills
            skill_score = len(matched_required) / len(required) if required else 0

            # Preferred skill bonus (10%)
            matched_preferred = preferred & candidate_skills
            preferred_score = len(matched_preferred) / len(preferred) if preferred else 0

            # Experience score (20%)
            exp_score = min(c.experience_years / jd.min_experience, 1.0) if jd.min_experience else 1

            # Resume quality score (10%)
            word_count = len(c.resume_text.split())
            quality_score = min(word_count / 200, 1.0)

            final_score = (
                0.6 * skill_score +
                0.1 * preferred_score +
                0.2 * exp_score +
                0.1 * quality_score
            )

            c.match_score = round(final_score, 4)

            # Explainability
            c.explanation = {
                "matched_required_skills": list(matched_required),
                "matched_preferred_skills": list(matched_preferred),
                "experience_years": c.experience_years,
                "skill_score_component": round(0.6 * skill_score, 4),
                "preferred_score_component": round(0.1 * preferred_score, 4),
                "experience_score_component": round(0.2 * exp_score, 4),
                "quality_score_component": round(0.1 * quality_score, 4),
                "final_score": c.match_score
            }

        return sorted(candidates, key=lambda x: x.match_score, reverse=True)

# =====================================================
# INTERVIEW SCHEDULER
# =====================================================

class BasicInterviewScheduler:

    def schedule_interview(self, candidate: Candidate, slots: List[InterviewSlot]) -> Optional[InterviewSlot]:

        for slot in slots:
            if slot.is_available:
                slot.is_available = False
                candidate.status = "interview_scheduled"
                return slot

        return None

# =====================================================
# LEAVE MANAGER
# =====================================================

class PolicyLeaveManager:

    def process_leave(self, request: LeaveRequest, policy: LeavePolicy, balance: int) -> Dict:

        days_requested = (request.end_date - request.start_date).days + 1
        violations = []

        if days_requested > balance:
            violations.append("Insufficient leave balance")

        if days_requested > policy.max_consecutive_days:
            violations.append("Exceeds max consecutive days")

        notice_days = (request.start_date - datetime.now()).days
        if notice_days < policy.min_notice_days:
            violations.append("Insufficient notice period")

        approved = len(violations) == 0

        return {
            "approved": approved,
            "violations": violations,
            "days_requested": days_requested
        }

# =====================================================
# ESCALATION
# =====================================================

class RuleBasedEscalation:

    KEYWORDS = ["harassment", "legal", "discrimination", "termination"]

    def should_escalate(self, query: str) -> Dict:

        for word in self.KEYWORDS:
            if word in query.lower():
                return {
                    "escalated": True,
                    "reason": f"Sensitive keyword detected: {word}"
                }

        return {"escalated": False}

# =====================================================
# HR AGENT
# =====================================================

class HRAgent:

    def __init__(self):
        self.screener = SmartResumeScreener()
        self.scheduler = BasicInterviewScheduler()
        self.leave_manager = PolicyLeaveManager()
        self.escalation = RuleBasedEscalation()
        self.pipeline: Dict[str, Candidate] = {}

    def screen_resumes(self, candidates: List[Candidate], jd: JobDescription):

        for c in candidates:
            c.status = "screened"

        ranked = self.screener.rank_candidates(candidates, jd)

        for c in ranked:
            self.pipeline[c.candidate_id] = c

        return ranked
        
    def shortlist_top_n(self, n: int):
    sorted_candidates = sorted(
        self.pipeline.values(),
        key=lambda x: x.match_score,
        reverse=True
    )

    for i, c in enumerate(sorted_candidates):
        if i < n:
            c.status = "interview_scheduled"
        else:
            c.status = "rejected"

    return sorted_candidates[:n]

    def update_status(self, candidate_id: str, new_status: str):

        candidate = self.pipeline.get(candidate_id)

        if not candidate:
            return {"error": "Candidate not found"}

        valid = PipelineStatus.valid_transitions()

        if new_status not in valid.get(candidate.status, []):
            return {"error": "Invalid state transition"}

        candidate.status = new_status
        return {"success": True}

    def export_results(self):

        return {
            "team_id": CONFIG["team_id"],
            "track": CONFIG["track"],
            "results": {
                "pipeline": {
                    cid: {
                        "name": c.name,
                        "status": c.status,
                        "score": c.match_score,
                        "explanation": c.explanation
                    }
                    for cid, c in self.pipeline.items()
                }
            }
        }