"""
Conversational Agent - Natural Language Interface for HR Operations
Wraps existing HR Agent with conversational capabilities
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ai_intelligence_layer import (
    ConversationContext, AgentResponse, IntentType, 
    ProactiveInsight, generate_uuid
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationalAgent:
    """
    Natural language interface for HR operations
    Wraps existing HR Agent without modifying it
    """
    
    def __init__(self, hr_agent, use_llm=True):
        """
        Initialize conversational agent
        
        Args:
            hr_agent: Existing UpgradedHRAgent instance
            use_llm: Whether to use LLM for intent extraction
        """
        self.hr_agent = hr_agent
        self.use_llm = use_llm
        self.conversations = {}  # conversation_id -> ConversationContext
        
        logger.info(f"✅ Conversational Agent initialized (LLM: {use_llm})")
    
    def process_message(
        self, 
        message: str, 
        context: Optional[ConversationContext] = None,
        **kwargs
    ) -> AgentResponse:
        """
        Process natural language message and generate intelligent response
        
        Args:
            message: User's natural language input
            context: Conversation context (created if None)
            **kwargs: Additional context (candidates, jd, slots, etc.)
        
        Returns:
            AgentResponse with text, insights, and recommendations
        """
        
        # Create or retrieve context
        if context is None:
            context = ConversationContext(
                conversation_id=generate_uuid(),
                user_id=kwargs.get("user_id", "default_user")
            )
            self.conversations[context.conversation_id] = context
        
        # Add user message to history
        context.add_message("user", message)
        
        # Extract intent and entities
        intent = self._extract_intent(message, context)
        entities = self._extract_entities(message, intent)
        
        # Update context
        context.current_intent = intent
        context.entities = entities
        
        # Route to appropriate handler
        try:
            if intent == IntentType.SCREEN_CANDIDATES:
                response = self._handle_screening(message, context, **kwargs)
            elif intent == IntentType.SCHEDULE_INTERVIEWS:
                response = self._handle_scheduling(message, context, **kwargs)
            elif intent == IntentType.ANALYZE_CANDIDATE:
                response = self._handle_analysis(message, context, **kwargs)
            elif intent == IntentType.GET_INSIGHTS:
                response = self._handle_insights(message, context, **kwargs)
            elif intent == IntentType.GENERATE_QUESTIONS:
                response = self._handle_questions(message, context, **kwargs)
            else:
                response = self._handle_general(message, context, **kwargs)
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            response = AgentResponse(
                text=f"I encountered an error: {str(e)}. Let me try a different approach.",
                confidence=0.5
            )
        
        # Add assistant response to history
        context.add_message("assistant", response.text)
        
        return response
    
    def _extract_intent(
        self, 
        message: str, 
        context: ConversationContext
    ) -> IntentType:
        """
        Extract user intent from natural language
        Uses keyword matching (can be enhanced with LLM)
        """
        
        msg_lower = message.lower()
        
        # Screen candidates intent
        if any(kw in msg_lower for kw in ["screen", "rank", "evaluate", "candidates", "resumes"]):
            return IntentType.SCREEN_CANDIDATES
        
        # Schedule interviews intent
        if any(kw in msg_lower for kw in ["schedule", "interview", "book", "slot"]):
            return IntentType.SCHEDULE_INTERVIEWS
        
        # Analyze candidate intent
        if any(kw in msg_lower for kw in ["analyze", "tell me about", "candidate", "profile"]):
            return IntentType.ANALYZE_CANDIDATE
        
        # Get insights intent
        if any(kw in msg_lower for kw in ["insight", "recommendation", "suggest", "what should"]):
            return IntentType.GET_INSIGHTS
        
        # Generate questions intent
        if any(kw in msg_lower for kw in ["question", "interview", "ask"]):
            return IntentType.GENERATE_QUESTIONS
        
        return IntentType.GENERAL_QUERY
    
    def _extract_entities(
        self, 
        message: str, 
        intent: IntentType
    ) -> Dict[str, Any]:
        """
        Extract entities from message (job titles, skills, numbers)
        """
        
        entities = {}
        
        # Extract numbers (for top N candidates)
        numbers = re.findall(r'\b(\d+)\b', message)
        if numbers:
            entities["count"] = int(numbers[0])
        
        # Extract common job titles
        job_titles = [
            "software engineer", "developer", "data scientist", 
            "product manager", "designer", "analyst"
        ]
        msg_lower = message.lower()
        for title in job_titles:
            if title in msg_lower:
                entities["job_title"] = title
                break
        
        # Extract skills (common tech skills)
        common_skills = [
            "python", "java", "javascript", "react", "aws", 
            "docker", "kubernetes", "sql", "machine learning"
        ]
        found_skills = [skill for skill in common_skills if skill in msg_lower]
        if found_skills:
            entities["skills"] = found_skills
        
        return entities
    
    def _handle_screening(
        self, 
        message: str, 
        context: ConversationContext,
        **kwargs
    ) -> AgentResponse:
        """Handle candidate screening request"""
        
        candidates = kwargs.get("candidates", [])
        jd = kwargs.get("jd")
        
        if not candidates:
            return AgentResponse(
                text="I don't see any candidates to screen. Please provide candidate data.",
                confidence=1.0
            )
        
        if not jd:
            return AgentResponse(
                text="I need a job description to screen candidates. Please provide the job requirements.",
                confidence=1.0
            )
        
        # Use existing HR agent to screen
        ranked = self.hr_agent.screen_resumes(candidates, jd)
        
        # Generate natural language response
        qualified = [c for c in ranked if c.match_score >= 0.7]
        top_candidate = ranked[0] if ranked else None
        
        response_text = self._generate_screening_response(
            total=len(candidates),
            qualified=len(qualified),
            top_candidate=top_candidate,
            jd=jd
        )
        
        return AgentResponse(
            text=response_text,
            confidence=0.85,
            data={
                "ranked_candidates": [
                    {
                        "candidate_id": c.candidate_id,
                        "name": c.name,
                        "match_score": c.match_score,
                        "explanation": c.explanation
                    }
                    for c in ranked[:10]
                ]
            }
        )
    
    def _handle_scheduling(
        self, 
        message: str, 
        context: ConversationContext,
        **kwargs
    ) -> AgentResponse:
        """Handle interview scheduling request"""
        
        candidates = kwargs.get("candidates", [])
        slots = kwargs.get("slots", [])
        
        if not candidates or not slots:
            return AgentResponse(
                text="I need both candidates and available time slots to schedule interviews.",
                confidence=1.0
            )
        
        # Use existing HR agent to schedule
        result = self.hr_agent.schedule_interviews(candidates, slots)
        
        scheduled_count = len(result.get("assignments", []))
        unscheduled_count = len(result.get("unscheduled", []))
        
        response_text = f"I've scheduled {scheduled_count} interviews. "
        
        if unscheduled_count > 0:
            response_text += f"However, {unscheduled_count} candidates couldn't be scheduled due to lack of available slots. "
            response_text += "Consider adding more interview slots or prioritizing top candidates."
        else:
            response_text += "All candidates have been scheduled successfully!"
        
        return AgentResponse(
            text=response_text,
            confidence=0.90,
            data=result
        )
    
    def _handle_analysis(
        self, 
        message: str, 
        context: ConversationContext,
        **kwargs
    ) -> AgentResponse:
        """Handle candidate analysis request"""
        
        candidate_id = context.entities.get("candidate_id")
        candidates = kwargs.get("candidates", [])
        
        if not candidate_id and candidates:
            # Analyze top candidate
            candidate = candidates[0] if candidates else None
        else:
            candidate = next(
                (c for c in candidates if c.candidate_id == candidate_id), 
                None
            )
        
        if not candidate:
            return AgentResponse(
                text="I couldn't find that candidate. Please specify which candidate you'd like to analyze.",
                confidence=0.7
            )
        
        # Generate analysis
        response_text = self._generate_candidate_analysis(candidate)
        
        return AgentResponse(
            text=response_text,
            confidence=0.85,
            data={
                "candidate": {
                    "name": candidate.name,
                    "match_score": candidate.match_score,
                    "explanation": candidate.explanation,
                    "reasoning_chain": candidate.reasoning_chain
                }
            }
        )
    
    def _handle_insights(
        self, 
        message: str, 
        context: ConversationContext,
        **kwargs
    ) -> AgentResponse:
        """Handle insights request"""
        
        # This will be enhanced with proactive insights generator
        return AgentResponse(
            text="Insights generation is being enhanced. For now, I can provide candidate rankings and analysis.",
            confidence=0.7,
            recommendations=[
                "Screen candidates to see top matches",
                "Analyze individual candidates for detailed insights",
                "Schedule interviews for qualified candidates"
            ]
        )
    
    def _handle_questions(
        self, 
        message: str, 
        context: ConversationContext,
        **kwargs
    ) -> AgentResponse:
        """Handle question generation request"""
        
        candidate = kwargs.get("candidate")
        jd = kwargs.get("jd")
        
        if not candidate or not jd:
            return AgentResponse(
                text="I need both a candidate profile and job description to generate interview questions.",
                confidence=1.0
            )
        
        # Use existing HR agent to generate questions
        questions = self.hr_agent.generate_questions(candidate, jd)
        
        response_text = f"I've generated {len(questions)} interview questions for {candidate.name}:\n\n"
        
        for i, q in enumerate(questions[:5], 1):
            response_text += f"{i}. {q['question']}\n"
            response_text += f"   Type: {q['type']}, Focus: {q.get('skill_focus', 'general')}\n\n"
        
        return AgentResponse(
            text=response_text,
            confidence=0.85,
            data={"questions": questions}
        )
    
    def _handle_general(
        self, 
        message: str, 
        context: ConversationContext,
        **kwargs
    ) -> AgentResponse:
        """Handle general queries"""
        
        response_text = (
            "I'm your AI HR assistant. I can help you with:\n"
            "• Screening and ranking candidates\n"
            "• Scheduling interviews\n"
            "• Analyzing candidate profiles\n"
            "• Generating interview questions\n"
            "• Providing strategic insights\n\n"
            "What would you like to do?"
        )
        
        return AgentResponse(
            text=response_text,
            confidence=0.90
        )
    
    def _generate_screening_response(
        self, 
        total: int, 
        qualified: int, 
        top_candidate, 
        jd
    ) -> str:
        """Generate natural language screening response"""
        
        response = f"I've analyzed {total} candidates for the {jd.title} role. "
        
        if qualified > 0:
            percentage = (qualified / total) * 100
            response += f"{qualified} candidates meet the minimum requirements ({percentage:.0f}% match or higher).\n\n"
            
            if top_candidate:
                response += f"🌟 Top Recommendation: {top_candidate.name} ({top_candidate.match_score:.0%} match)\n"
                
                # Add key strengths
                strengths = top_candidate.explanation.get("key_strengths", [])
                if strengths:
                    response += f"   Strengths: {', '.join(strengths[:3])}\n"
                
                # Add concerns if any
                concerns = top_candidate.explanation.get("key_concerns", [])
                if concerns:
                    response += f"   ⚠️  Concerns: {', '.join(concerns[:2])}\n"
        else:
            response += "Unfortunately, no candidates meet the minimum requirements. "
            response += "Consider adjusting the job requirements or expanding the candidate pool."
        
        return response
    
    def _generate_candidate_analysis(self, candidate) -> str:
        """Generate natural language candidate analysis"""
        
        response = f"Analysis of {candidate.name}:\n\n"
        response += f"Match Score: {candidate.match_score:.0%}\n"
        response += f"Experience: {candidate.experience_years} years\n\n"
        
        # Matched skills
        matched = candidate.explanation.get("matched_required_skills", [])
        if matched:
            response += f"✅ Matched Skills: {', '.join(matched)}\n"
        
        # Missing skills
        missing = candidate.explanation.get("missing_required_skills", [])
        if missing:
            response += f"❌ Missing Skills: {', '.join(missing)}\n"
        
        # Hidden strengths
        hidden = candidate.explanation.get("hidden_strengths", [])
        if hidden:
            response += f"\n💡 Hidden Strengths: {', '.join(hidden)}\n"
        
        # Recommendation
        recommendation = candidate.explanation.get("recommendation", "review")
        response += f"\nRecommendation: {recommendation.upper()}\n"
        
        # Reasoning chain
        if candidate.reasoning_chain:
            response += "\nReasoning:\n"
            for step in candidate.reasoning_chain[:3]:
                response += f"  • {step}\n"
        
        return response
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context"""
        return self.conversations.get(conversation_id)
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Conversational Agent")
    print("=" * 60)
    
    # Mock HR agent
    class MockHRAgent:
        def screen_resumes(self, candidates, jd):
            return candidates
        
        def schedule_interviews(self, candidates, slots):
            return {"assignments": [], "unscheduled": []}
        
        def generate_questions(self, candidate, jd):
            return [{"question": "Test question", "type": "technical"}]
    
    agent = ConversationalAgent(MockHRAgent(), use_llm=False)
    
    # Test intent extraction
    message = "Can you screen the candidates for me?"
    context = ConversationContext(
        conversation_id=generate_uuid(),
        user_id="test_user"
    )
    
    intent = agent._extract_intent(message, context)
    print(f"✅ Intent extracted: {intent}")
    
    # Test message processing
    response = agent.process_message(
        "Show me the best candidates",
        context,
        candidates=[],
        jd=None
    )
    print(f"✅ Response generated: {response.text[:50]}...")
    
    print("\n🎉 Conversational Agent ready!")
