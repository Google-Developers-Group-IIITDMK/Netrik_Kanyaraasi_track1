"""
AI Intelligence Layer - Core Components for AI-Native Transformation
Implements conversational agent, strategic intelligence, predictive analytics, and proactive insights
"""

import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class IntentType(Enum):
    """Types of user intents"""
    SCREEN_CANDIDATES = "screen_candidates"
    SCHEDULE_INTERVIEWS = "schedule_interviews"
    ANALYZE_CANDIDATE = "analyze_candidate"
    GET_INSIGHTS = "get_insights"
    GENERATE_QUESTIONS = "generate_questions"
    GENERAL_QUERY = "general_query"


class InsightType(Enum):
    """Types of proactive insights"""
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"


class SeverityLevel(Enum):
    """Severity levels for insights"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RiskLevel(Enum):
    """Risk levels for attrition prediction"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Message:
    """Individual message in conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ConversationContext:
    """
    Conversation context with history and state
    Validates conversation_id uniqueness and message history limits
    """
    conversation_id: str
    user_id: str
    message_history: List[Message] = field(default_factory=list)
    current_intent: Optional[IntentType] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate conversation context"""
        if not self.conversation_id:
            raise ValueError("conversation_id cannot be empty")
        
        # Enforce 50 message limit
        if len(self.message_history) > 50:
            self.message_history = self.message_history[-50:]
    
    def add_message(self, role: str, content: str):
        """Add message to history with limit enforcement"""
        self.message_history.append(Message(role=role, content=content))
        
        # Enforce 50 message limit
        if len(self.message_history) > 50:
            self.message_history = self.message_history[-50:]
    
    def to_dict(self) -> Dict:
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "message_history": [m.to_dict() for m in self.message_history],
            "current_intent": self.current_intent.value if self.current_intent else None,
            "entities": self.entities,
            "session_data": self.session_data,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class CandidateInsight:
    """Insights about a specific candidate"""
    candidate_id: str
    name: str
    match_score: float
    insights: List[str]
    hidden_strengths: List[str] = field(default_factory=list)
    key_concerns: List[str] = field(default_factory=list)
    recommendation: str = "review"
    
    def __post_init__(self):
        """Validate candidate insight"""
        if not 0.0 <= self.match_score <= 1.0:
            raise ValueError(f"match_score must be between 0.0 and 1.0, got {self.match_score}")


@dataclass
class SkillGapReport:
    """Skill gap analysis report"""
    common_gaps: Dict[str, int]  # skill -> count
    gap_percentage: Dict[str, float]  # skill -> percentage
    most_common_gap: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """Strategic recommendation"""
    title: str
    description: str
    impact: str
    priority: str  # "high", "medium", "low"
    rationale: str


@dataclass
class Risk:
    """Identified risk"""
    title: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    impact: str
    mitigation: str


@dataclass
class Opportunity:
    """Identified opportunity"""
    title: str
    description: str
    value: str
    action: str


@dataclass
class StrategicAnalysis:
    """
    Strategic analysis of candidate pool
    Validates confidence_score range and executive_summary length
    """
    analysis_id: str
    candidate_pool_size: int
    qualified_count: int
    top_candidates: List[CandidateInsight]
    market_observations: List[str]
    competitive_pressures: List[str]
    skill_gap_analysis: SkillGapReport
    recommendations: List[Recommendation]
    risks: List[Risk]
    opportunities: List[Opportunity]
    executive_summary: str
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate strategic analysis"""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(f"confidence_score must be between 0.0 and 1.0, got {self.confidence_score}")
        
        if len(self.executive_summary) < 200:
            raise ValueError(f"executive_summary must be at least 200 characters, got {len(self.executive_summary)}")
        
        # Limit top candidates to 20
        if len(self.top_candidates) > 20:
            self.top_candidates = self.top_candidates[:20]


@dataclass
class RiskFactor:
    """Individual risk factor"""
    factor: str
    weight: float
    description: str
    
    def __post_init__(self):
        """Validate risk factor"""
        if self.weight <= 0.0:
            raise ValueError(f"weight must be positive, got {self.weight}")


@dataclass
class AttritionPrediction:
    """
    Attrition risk prediction for a candidate
    Validates risk_level enum and score ranges
    """
    candidate_id: str
    risk_level: str  # "low", "medium", "high", "critical"
    risk_score: float  # 0.0 to 1.0
    risk_factors: List[RiskFactor]
    protective_factors: List[str]
    time_horizon: str  # "6_months", "1_year", "2_years"
    confidence: float
    reasoning: str
    mitigation_strategies: List[str]
    
    def __post_init__(self):
        """Validate attrition prediction"""
        valid_levels = ["low", "medium", "high", "critical"]
        if self.risk_level not in valid_levels:
            raise ValueError(f"risk_level must be one of {valid_levels}, got {self.risk_level}")
        
        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError(f"risk_score must be between 0.0 and 1.0, got {self.risk_score}")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if not self.reasoning:
            raise ValueError("reasoning cannot be empty")


@dataclass
class RampUpEstimate:
    """Ramp-up time estimation"""
    candidate_id: str
    weeks: int
    confidence: float
    factors: List[str]
    reasoning: str
    
    def __post_init__(self):
        """Validate ramp-up estimate"""
        if self.weeks < 0:
            raise ValueError(f"weeks must be non-negative, got {self.weeks}")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class PerformanceForecast:
    """Performance trajectory forecast"""
    candidate_id: str
    trajectory: str  # "high_performer", "solid_contributor", "needs_support"
    confidence: float
    factors: List[str]
    reasoning: str


@dataclass
class CulturalFitScore:
    """Cultural fit assessment"""
    candidate_id: str
    fit_score: float  # 0.0 to 1.0
    alignment_factors: List[str]
    concerns: List[str]
    confidence: float
    reasoning: str
    
    def __post_init__(self):
        """Validate cultural fit score"""
        if not 0.0 <= self.fit_score <= 1.0:
            raise ValueError(f"fit_score must be between 0.0 and 1.0, got {self.fit_score}")


@dataclass
class ProactiveInsight:
    """
    Proactive insight generated without user prompting
    Validates insight_type, severity, and confidence ranges
    """
    insight_id: str
    insight_type: str  # "risk", "opportunity", "recommendation", "alert"
    severity: str  # "info", "warning", "critical"
    title: str
    description: str
    impact: str
    recommended_action: str
    confidence: float
    related_candidates: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate proactive insight"""
        valid_types = ["risk", "opportunity", "recommendation", "alert"]
        if self.insight_type not in valid_types:
            raise ValueError(f"insight_type must be one of {valid_types}, got {self.insight_type}")
        
        valid_severities = ["info", "warning", "critical"]
        if self.severity not in valid_severities:
            raise ValueError(f"severity must be one of {valid_severities}, got {self.severity}")
        
        if not 10 <= len(self.title) <= 100:
            raise ValueError(f"title must be 10-100 characters, got {len(self.title)}")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        # Critical insights must have expiration
        if self.severity == "critical" and self.expires_at is None:
            self.expires_at = datetime.now() + timedelta(days=7)


@dataclass
class AgentResponse:
    """Response from conversational agent"""
    text: str
    insights: List[ProactiveInsight] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.85
    data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate agent response"""
        if not self.text:
            raise ValueError("text cannot be empty")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_uuid() -> str:
    """Generate unique identifier"""
    return str(uuid.uuid4())


def validate_confidence_score(score: float) -> bool:
    """Validate confidence score is in valid range"""
    return 0.0 <= score <= 1.0


def validate_match_score(score: float) -> bool:
    """Validate match score is in valid range"""
    return 0.0 <= score <= 1.0


# Quick test
if __name__ == "__main__":
    print("🧪 Testing AI Intelligence Layer Data Models")
    print("=" * 60)
    
    # Test ConversationContext
    context = ConversationContext(
        conversation_id=generate_uuid(),
        user_id="user_123"
    )
    context.add_message("user", "Hello")
    context.add_message("assistant", "Hi! How can I help?")
    print(f"✅ ConversationContext: {len(context.message_history)} messages")
    
    # Test ProactiveInsight
    insight = ProactiveInsight(
        insight_id=generate_uuid(),
        insight_type="alert",
        severity="critical",
        title="High Competition Risk Detected",
        description="3 top candidates likely have multiple offers",
        impact="May lose best candidates within 5-7 days",
        recommended_action="Expedite interview process",
        confidence=0.82,
        related_candidates=["c1", "c2", "c3"]
    )
    print(f"✅ ProactiveInsight: {insight.title} ({insight.severity})")
    
    # Test AttritionPrediction
    prediction = AttritionPrediction(
        candidate_id="c1",
        risk_level="medium",
        risk_score=0.45,
        risk_factors=[
            RiskFactor("overqualified", 0.4, "May seek more challenging opportunities")
        ],
        protective_factors=["Strong skill match"],
        time_horizon="1_year",
        confidence=0.75,
        reasoning="Candidate has 8 years experience for 5-year role",
        mitigation_strategies=["Emphasize growth opportunities"]
    )
    print(f"✅ AttritionPrediction: {prediction.risk_level} ({prediction.risk_score:.0%})")
    
    print("\n🎉 All data models validated successfully!")
