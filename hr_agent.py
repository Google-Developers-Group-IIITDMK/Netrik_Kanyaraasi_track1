import os
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
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
# PIPELINE STATES (AS PER OFFICIAL GUIDE)
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
# LLM SERVICE (MOCK FOR NOW)
# =====================================================

class MockLLMService:
    def invoke(self, prompt: str) -> dict:
        # Simulated structured response
        return {
            "skills": ["Python", "Docker", "REST APIs", "SQL"],
            "confidence": 0.9
        }

# =====================================================
# ABSTRACT CLASSES
# =====================================================

class ResumeScreener(ABC):
    @abstractmethod
    def extract_skills(self, resume_text: str) -> List[str]:
        pass

    @abstractmethod
    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        pass

class InterviewScheduler(ABC):
    @abstractmethod
    def schedule_interview(self, candidate: Candidate, slots: List[InterviewSlot]) -> Optional[InterviewSlot]:
        pass

class LeaveManager(ABC):
    @abstractmethod
    def process_leave(self, request: LeaveRequest, policy: LeavePolicy, balance: int) -> Dict:
        pass

class EscalationHandler(ABC):
    @abstractmethod
    def should_escalate(self, query: str) -> Dict:
        pass

# =====================================================
# IMPLEMENTATIONS
# =====================================================

class LLMResumeScreener(ResumeScreener):
    def __init__(self, llm_service=None):
        self.llm = llm_service or MockLLMService()

    def extract_skills(self, resume_text: str) -> List[str]:
        prompt = f"""
        Extract technical skills from resume.
        Return JSON format: {{"skills": []}}

        Resume:
        {resume_text}
        """
        response = self.llm.invoke(prompt)
        return response.get("skills", [])

    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        for c in candidates:
            required = set(jd.required_skills)
            candidate_skills = set(c.skills)

            skill_overlap = len(required & candidate_skills)
            skill_score = skill_overlap / len(required) if required else 0

            exp_score = min(c.experience_years / jd.min_experience, 1.0) if jd.min_experience else 1

            c.match_score = round(
                0.6 * skill_score + 0.4 * exp_score,
                4
            )

        return sorted(candidates, key=lambda x: x.match_score, reverse=True)

class BasicInterviewScheduler(InterviewScheduler):
    def schedule_interview(self, candidate: Candidate, slots: List[InterviewSlot]) -> Optional[InterviewSlot]:
        for slot in slots:
            if slot.is_available:
                slot.is_available = False
                candidate.status = "interview_scheduled"
                return slot
        return None

class PolicyLeaveManager(LeaveManager):
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

class RuleBasedEscalation(EscalationHandler):
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
# MAIN HR AGENT
# =====================================================

class HRAgent:

    def __init__(self):
        self.screener = LLMResumeScreener()
        self.scheduler = BasicInterviewScheduler()
        self.leave_manager = PolicyLeaveManager()
        self.escalation = RuleBasedEscalation()
        self.pipeline: Dict[str, Candidate] = {}

    def screen_resumes(self, candidates: List[Candidate], jd: JobDescription):
        for c in candidates:
            c.skills = self.screener.extract_skills(c.resume_text)
            c.status = "screened"

        ranked = self.screener.rank_candidates(candidates, jd)

        for c in ranked:
            self.pipeline[c.candidate_id] = c

        return ranked

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
                        "score": c.match_score
                    }
                    for cid, c in self.pipeline.items()
                }
            }
        }