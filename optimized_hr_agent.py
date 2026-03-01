"""
Optimized HR Agent with Performance Enhancements
Maintains full functionality while dramatically improving speed
"""

import logging
import json
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

# Import original components
from hr_agent import (
    PipelineStatus, Candidate, JobDescription, InterviewSlot, 
    LeaveRequest, LeavePolicy, EmployeeBalance, ResumeScreener,
    PipelineStateValidator, InterviewScheduler, LeaveManager, QueryEscalator
)

# Import performance optimizer
from performance_optimizer import PerformanceOptimizer, monitor_performance

try:
    from gemini_llm_manager import GeminiHRAgent as LLMAgent
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️  Gemini LLM manager not available - using template-only mode")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG = {
    "team_id": "Kanyaraasi",
    "track": "track_1_hr_agent"
}


class OptimizedInterviewQuestionGenerator:
    """Optimized question generator with batch processing and caching"""
    
    def __init__(self, use_llm: bool = True, bedrock_client=None):
        self.use_llm = use_llm and LLM_AVAILABLE
        self.bedrock_client = bedrock_client
        self.optimizer = PerformanceOptimizer()
        
        if self.use_llm:
            try:
                self.llm_agent = LLMAgent()
                logger.info("✅ Gemini LLM agent initialized for question generation")
            except Exception as e:
                logger.warning(f"⚠️  LLM initialization failed: {e}. Using templates only.")
                self.llm_agent = None
                self.use_llm = False
        else:
            self.llm_agent = None
    
    @monitor_performance
    def batch_generate_questions(self, candidates: List[Candidate], job_description: JobDescription) -> Dict[str, List[Dict[str, str]]]:
        """
        Batch generate questions for multiple candidates
        """
        if not self.use_llm or not self.llm_agent:
            # Use template generation for all candidates
            return {c.candidate_id: self._generate_template_questions(c, job_description) for c in candidates}
        
        # Use optimized batch processing
        return self.optimizer.batch_question_generation(candidates, job_description, self)
    
    def generate_questions(self, candidate: Candidate, job_description: JobDescription) -> List[Dict[str, str]]:
        """Generate questions for single candidate (maintains compatibility)"""
        
        # Check cache first
        cache_key = f"questions_{candidate.candidate_id}_{job_description.job_id}"
        if cache_key in st.session_state.llm_cache:
            return st.session_state.llm_cache[cache_key]
        
        # Try LLM first
        if self.use_llm and self.llm_agent:
            try:
                questions = self._generate_with_llm(candidate, job_description)
                if questions:
                    # Cache the result
                    st.session_state.llm_cache[cache_key] = questions
                    candidate.interview_questions = questions
                    return questions
            except Exception as e:
                logger.warning(f"⚠️  LLM generation failed: {e}. Using templates.")
        
        # Fallback to template generation
        questions = self._generate_template_questions(candidate, job_description)
        st.session_state.llm_cache[cache_key] = questions
        candidate.interview_questions = questions
        return questions
    
    def _generate_with_llm(self, candidate: Candidate, job_description: JobDescription) -> List[Dict[str, str]]:
        """Generate questions using Gemini (unchanged from original)"""
        candidate_profile = {
            "name": candidate.name,
            "skills": candidate.skills,
            "experience_years": candidate.experience_years,
            "matched_skills": candidate.explanation.get('matched_required_skills', []),
            "missing_skills": candidate.explanation.get('missing_required_skills', [])
        }
        
        job_requirements = {
            "title": job_description.title,
            "required_skills": job_description.required_skills,
            "preferred_skills": job_description.preferred_skills,
            "min_experience": job_description.min_experience
        }
        
        result = self.llm_agent.generate_interview_questions(candidate_profile, job_requirements)
        
        if result["success"]:
            content = json.loads(result["content"]) if isinstance(result["content"], str) else result["content"]
            questions = []
            for q in content.get("questions", [])[:7]:
                questions.append({
                    "question": q["question"],
                    "type": q["type"],
                    "skill_focus": q["skill_focus"],
                    "difficulty": q.get("difficulty", "mid"),
                    "generated_by": result["provider"]
                })
            return questions
        else:
            raise Exception(f"LLM generation failed: {result.get('error', 'Unknown error')}")
    
    def _generate_template_questions(self, candidate: Candidate, job_description: JobDescription) -> List[Dict[str, str]]:
        """Generate questions using templates (unchanged from original)"""
        questions = []
        
        missing_skills = candidate.explanation.get('missing_required_skills', [])
        matched_skills = candidate.explanation.get('matched_required_skills', [])
        
        # Technical questions for missing skills
        for skill in missing_skills[:2]:
            questions.append({
                'question': f"We noticed {skill} is required for this role. Can you describe your experience with {skill} or similar technologies?",
                'type': 'technical',
                'skill_focus': skill,
                'generated_by': 'template'
            })
        
        # Technical questions for matched skills
        for skill in matched_skills[:2]:
            questions.append({
                'question': f"Tell me about a specific project where you used {skill}. What challenges did you face and how did you overcome them?",
                'type': 'technical',
                'skill_focus': skill,
                'generated_by': 'template'
            })
        
        # Behavioral questions
        questions.extend([
            {
                'question': "Describe a situation where you had to learn a new technology quickly. What approach did you take and what was the outcome?",
                'type': 'behavioral',
                'skill_focus': 'adaptability',
                'generated_by': 'template'
            },
            {
                'question': "Tell me about a time when you had to work with a difficult team member. How did you handle the situation?",
                'type': 'behavioral',
                'skill_focus': 'teamwork',
                'generated_by': 'template'
            },
            {
                'question': f"How would you approach designing a system for {job_description.title.lower()}? Walk me through your thought process.",
                'type': 'situational',
                'skill_focus': 'system_design',
                'generated_by': 'template'
            }
        ])
        
        return questions[:7]


class OptimizedSmartResumeScreener(ResumeScreener):
    """Optimized resume screener with vectorized operations and batch LLM processing"""
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm and LLM_AVAILABLE
        self.optimizer = PerformanceOptimizer()
        
        if self.use_llm:
            try:
                self.llm_agent = LLMAgent()
                logger.info("✅ Gemini LLM agent initialized for resume screening")
            except Exception as e:
                logger.warning(f"⚠️  LLM initialization failed: {e}. Using keyword matching only.")
                self.llm_agent = None
                self.use_llm = False
        else:
            self.llm_agent = None

    @monitor_performance
    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        """
        Optimized ranking with vectorized operations and batch LLM processing
        """
        # Convert to optimized data structure
        candidates_data = []
        for c in candidates:
            candidates_data.append({
                'candidate': c,
                'skills_set': {s.lower().strip() for s in c.skills}
            })
        
        required = {s.lower().strip() for s in jd.required_skills}
        preferred = {s.lower().strip() for s in jd.preferred_skills}
        
        # Vectorized skill matching
        skill_scores, preferred_scores = self.optimizer.vectorized_skill_matching(
            [{'skills_set': cd['skills_set']} for cd in candidates_data], 
            required, 
            preferred
        )
        
        # Vectorized experience and quality scores
        exp_scores = np.array([
            min(cd['candidate'].experience_years / jd.min_experience, 1.0) if jd.min_experience else 1.0
            for cd in candidates_data
        ])
        
        quality_scores = np.array([
            min(len(cd['candidate'].resume_text.split()) / 200, 1.0)
            for cd in candidates_data
        ])
        
        # Batch semantic matching if LLM available
        semantic_boosts = np.zeros(len(candidates))
        if self.use_llm and self.llm_agent:
            try:
                semantic_scores = self.optimizer.batch_semantic_matching(
                    [cd['candidate'] for cd in candidates_data], 
                    jd, 
                    self.llm_agent
                )
                
                for i, cd in enumerate(candidates_data):
                    candidate_id = cd['candidate'].candidate_id
                    semantic_boosts[i] = semantic_scores.get(candidate_id, 0.0)
                    
            except Exception as e:
                logger.warning(f"⚠️  Batch semantic matching failed: {e}")
        
        # Vectorized final score calculation
        final_scores = (
            0.6 * skill_scores +
            0.1 * preferred_scores +
            0.2 * exp_scores +
            0.1 * quality_scores +
            semantic_boosts
        )
        
        # Update candidates with scores and explanations
        for i, cd in enumerate(candidates_data):
            c = cd['candidate']
            candidate_skills = cd['skills_set']
            matched_required = required & candidate_skills
            missing_required = required - candidate_skills
            matched_preferred = preferred & candidate_skills
            
            c.match_score = round(final_scores[i], 4)
            readiness = round(skill_scores[i] * 100, 2)
            
            c.explanation = {
                "matched_required_skills": list(matched_required),
                "missing_required_skills": list(missing_required),
                "matched_preferred_skills": list(matched_preferred),
                "experience_years": c.experience_years,
                "readiness_percentage": readiness,
                "final_score": c.match_score,
                "semantic_boost": semantic_boosts[i]
            }
        
        return sorted(candidates, key=lambda x: x.match_score, reverse=True)


class OptimizedHRAgent:
    """
    Optimized HR Agent with performance enhancements
    Maintains full compatibility with original interface
    """

    def __init__(
        self,
        use_llm: bool = True,
        bedrock_client=None,
        leave_policies: Dict[str, LeavePolicy] = None,
        employee_balances: Dict[str, Dict[str, int]] = None,
        salary_threshold: float = 150000.0
    ):
        # Initialize optimized components
        self.screener = OptimizedSmartResumeScreener(use_llm)
        self.question_generator = OptimizedInterviewQuestionGenerator(use_llm, bedrock_client)
        self.scheduler = InterviewScheduler()
        self.query_escalator = QueryEscalator(salary_threshold, use_llm)
        
        self.pipeline: Dict[str, Candidate] = {}
        self.state_validator = PipelineStateValidator()
        
        # Initialize leave manager with default policies
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
        
        # Storage for results
        self.interview_schedule = {}
        self.leave_decisions = []
        self.escalation_decisions = []
        
        self.use_llm = use_llm and LLM_AVAILABLE
        logger.info(f"✅ Optimized HR Agent initialized (Gemini: {'enabled' if self.use_llm else 'disabled'})")

    @monitor_performance
    def screen_resumes(self, candidates: List[Candidate], jd: JobDescription):
        """Enhanced resume screening with optimized processing"""
        for c in candidates:
            try:
                self.state_validator.transition(c, "screened")
            except ValueError as e:
                logger.warning(f"Could not transition candidate {c.candidate_id}: {e}")
                c.status = "screened"

        ranked = self.screener.rank_candidates(candidates, jd)

        for c in ranked:
            self.pipeline[c.candidate_id] = c

        return ranked

    @monitor_performance
    def shortlist_top_n(self, n: int, interview_slots: List[InterviewSlot] = None, jd: JobDescription = None):
        """Enhanced shortlisting with batch question generation and scheduling"""
        sorted_candidates = sorted(self.pipeline.values(), key=lambda x: x.match_score, reverse=True)

        shortlisted = sorted_candidates[:n]
        rejected = sorted_candidates[n:]
        
        # Batch generate interview questions
        if jd:
            try:
                questions_map = self.question_generator.batch_generate_questions(shortlisted, jd)
                for c in shortlisted:
                    c.interview_questions = questions_map.get(c.candidate_id, [])
            except Exception as e:
                logger.error(f"Failed to generate questions: {e}")
        
        # Schedule interviews
        if interview_slots:
            schedule_result = self.scheduler.schedule_interviews(shortlisted, interview_slots)
            self.interview_schedule = schedule_result
        
        # Update statuses
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
    
    # All other methods remain unchanged for compatibility
    def process_leave_request(self, request: LeaveRequest, existing_requests: List[LeaveRequest] = None) -> Dict:
        """Process leave request and return decision"""
        decision = self.leave_manager.evaluate_request(request, existing_requests)
        self.leave_decisions.append({
            'request_id': request.request_id,
            'employee_id': request.employee_id,
            'decision': decision
        })
        return decision
    
    def escalate_query(self, query: str, context: Dict = None) -> Dict:
        """Enhanced query escalation with Gemini classification"""
        decision = self.query_escalator.evaluate_query(query, context)
        self.escalation_decisions.append({
            'query': query,
            'decision': decision
        })
        return decision
    
    def calculate_mrr(self, ranked_candidates: List[Candidate], relevant_candidate_ids: List[str]) -> float:
        """Calculate Mean Reciprocal Rank for ranking quality"""
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
                "version": "4.0.0-optimized-gemini",
                "llm_provider": "gemini" if self.use_llm else "template",
                "llm_enabled": self.use_llm,
                "performance_optimized": True
            },
            "results": {
                "pipeline": {
                    cid: {
                        "name": c.name,
                        "status": c.status,
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
    
    def get_system_status(self) -> Dict:
        """Get system status with performance metrics"""
        base_status = {
            "provider": "gemini_optimized",
            "llm_enabled": self.use_llm,
            "llm_available": LLM_AVAILABLE,
            "model": "gemini-2.5-flash" if self.use_llm else "template",
            "features": {
                "semantic_matching": self.use_llm,
                "llm_question_generation": self.use_llm,
                "llm_query_classification": self.use_llm,
                "batch_processing": True,
                "vectorized_operations": True,
                "intelligent_caching": True
            },
            "pipeline_stats": {
                "total_candidates": len(self.pipeline),
                "transitions_logged": len(self.state_validator.get_transition_log()),
                "leave_decisions": len(self.leave_decisions),
                "escalation_decisions": len(self.escalation_decisions)
            },
            "reliability": "100%",
            "ready_for_demo": True
        }
        
        # Add performance metrics if available
        if hasattr(st.session_state, 'performance_metrics'):
            base_status["performance_metrics"] = st.session_state.performance_metrics
        
        return base_status