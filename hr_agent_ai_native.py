"""
AI-Native HR Agent - Hackathon Edition
Adds: Executive Summary, Cross-Candidate Insights, Predictive Recommendations, Strategic Insights
Implementation time: 6-8 hours
"""

import logging
import json
from typing import List, Dict
from datetime import datetime
from hr_agent_upgraded import (
    UpgradedHRAgent, Candidate, JobDescription, InterviewSlot, LLM_AVAILABLE
)

try:
    from gemini_llm_manager_upgraded import UpgradedGeminiHRAgent as LLMAgent
except ImportError:
    LLM_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI_NATIVE_HR")

# Re-export for convenience
__all__ = ['AINativeHRAgent', 'Candidate', 'JobDescription', 'InterviewSlot', 'AIStrategicInsights']


class AIStrategicInsights:
    """Generate strategic insights from candidate pool"""
    
    def __init__(self, use_llm=True, fast_mode=True):
        self.use_llm = use_llm and LLM_AVAILABLE
        self.fast_mode = fast_mode  # Use rule-based for speed
        self.llm = LLMAgent() if self.use_llm else None
    
    def generate_executive_summary(self, candidates: List[Candidate], jd: JobDescription) -> Dict:
        """Generate executive summary after screening - FAST MODE"""
        
        total = len(candidates)
        qualified = len([c for c in candidates if c.match_score >= 0.7])
        top_5_avg = sum(c.match_score for c in candidates[:5]) / 5 if len(candidates) >= 5 else 0
        
        # Skill gap analysis
        all_missing = []
        for c in candidates[:20]:  # Top 20
            all_missing.extend(c.explanation.get('missing_required_skills', []))
        
        from collections import Counter
        gap_counts = Counter(all_missing)
        common_gaps = gap_counts.most_common(3)
        
        # Market observations
        overqualified = len([c for c in candidates[:10] if c.experience_years > jd.min_experience * 1.5])
        underqualified = len([c for c in candidates[:10] if c.experience_years < jd.min_experience * 0.8])
        
        # FAST MODE: Use template-based summary (instant)
        if self.fast_mode:
            return self._template_summary(total, qualified, top_5_avg, common_gaps)
        
        # SLOW MODE: Try LLM (only if fast_mode=False)
        if self.llm:
            try:
                # LLM-generated summary
                prompt = f"""Generate an executive summary for this hiring analysis:

Total Candidates: {total}
Qualified (>70% match): {qualified}
Top 5 Average Score: {top_5_avg:.1%}
Common Skill Gaps: {', '.join([f"{skill} ({count} candidates)" for skill, count in common_gaps])}
Overqualified Candidates: {overqualified}/10
Underqualified Candidates: {underqualified}/10

Job: {jd.title}
Required Skills: {', '.join(jd.required_skills[:5])}

Generate a 3-paragraph executive summary covering:
1. Overall talent pool quality
2. Key findings and patterns
3. Strategic recommendations

Return JSON: {{"summary": "text", "key_findings": ["finding1", "finding2"], "recommendations": ["rec1", "rec2"], "confidence": 0.85}}"""
                
                result = self.llm.llm_manager.generate_with_retry(
                    prompt,
                    self.llm.llm_manager.TaskType.SEMANTIC_MATCHING
                )
                
                if result['success']:
                    content = json.loads(result['content'])
                    return {
                        "summary": content.get("summary", self._template_summary(total, qualified, top_5_avg, common_gaps)),
                        "key_findings": content.get("key_findings", []),
                        "recommendations": content.get("recommendations", []),
                        "confidence": content.get("confidence", 0.85),
                        "generated_by": "llm"
                    }
            except Exception as e:
                logger.warning(f"LLM summary failed: {e}")
        
        # Template fallback
        return self._template_summary(total, qualified, top_5_avg, common_gaps)
    
    def _template_summary(self, total, qualified, top_5_avg, common_gaps):
        """Template-based summary"""
        
        quality = "strong" if top_5_avg >= 0.8 else "moderate" if top_5_avg >= 0.6 else "limited"
        
        summary = f"""Analyzed {total} candidates for this position. The talent pool shows {quality} overall quality with {qualified} candidates meeting minimum qualifications (70%+ match).

Top candidates demonstrate an average match score of {top_5_avg:.1%}, indicating {"excellent" if top_5_avg >= 0.8 else "good"} alignment with role requirements. """
        
        if common_gaps:
            gap_text = ", ".join([f"{skill} ({count} candidates)" for skill, count in common_gaps])
            summary += f"Notable skill gaps across the candidate pool include: {gap_text}. This may indicate market-wide shortages or overly specific requirements. "
        
        summary += f"""

Strategic Recommendation: {"Proceed with top candidates immediately - strong pool quality." if top_5_avg >= 0.8 else "Consider adjusting requirements or expanding search - moderate pool quality."}"""
        
        return {
            "summary": summary,
            "key_findings": [
                f"{qualified}/{total} candidates meet minimum qualifications",
                f"Top 5 average score: {top_5_avg:.1%}",
                f"Common skill gaps: {', '.join([skill for skill, _ in common_gaps])}" if common_gaps else "No significant skill gaps"
            ],
            "recommendations": [
                "Expedite interviews for top 3 candidates" if top_5_avg >= 0.8 else "Expand candidate search",
                "Consider skill gap training programs" if common_gaps else "Maintain current requirements"
            ],
            "confidence": 0.82,
            "generated_by": "template"
        }
    
    def generate_cross_candidate_insights(self, candidates: List[Candidate]) -> Dict:
        """Generate cross-candidate comparison insights"""
        
        if len(candidates) < 2:
            return {"insights": [], "percentiles": {}}
        
        # Calculate percentiles
        scores = [c.match_score for c in candidates]
        scores.sort()
        
        def get_percentile(score):
            rank = sum(1 for s in scores if s < score)
            return (rank / len(scores)) * 100
        
        percentiles = {}
        for c in candidates[:10]:  # Top 10
            percentiles[c.candidate_id] = {
                "percentile": round(get_percentile(c.match_score), 1),
                "rank": candidates.index(c) + 1,
                "total": len(candidates)
            }
        
        # Generate insights
        insights = []
        
        # Top tier detection
        top_3 = candidates[:3]
        if len(top_3) >= 3 and all(c.match_score >= 0.85 for c in top_3):
            insights.append({
                "type": "opportunity",
                "severity": "high",
                "title": "Exceptional Top Tier Detected",
                "description": f"Top 3 candidates all score above 85% - rare high-quality pool",
                "candidates": [c.candidate_id for c in top_3],
                "action": "Fast-track interviews to secure top talent before competitors"
            })
        
        # Score clustering
        if len(candidates) >= 5:
            top_5_range = max(c.match_score for c in candidates[:5]) - min(c.match_score for c in candidates[:5])
            if top_5_range < 0.05:  # Very close scores
                insights.append({
                    "type": "insight",
                    "severity": "medium",
                    "title": "Highly Competitive Top 5",
                    "description": f"Top 5 candidates within {top_5_range:.1%} of each other - difficult to differentiate",
                    "candidates": [c.candidate_id for c in candidates[:5]],
                    "action": "Use behavioral interviews and culture fit assessments to differentiate"
                })
        
        # Hidden gem detection
        for i, c in enumerate(candidates[5:15], 5):  # Ranks 6-15
            if c.match_score >= 0.75 and c.experience_years < candidates[0].experience_years * 0.7:
                insights.append({
                    "type": "opportunity",
                    "severity": "medium",
                    "title": "Hidden Gem Identified",
                    "description": f"{c.name} (rank #{i+1}) shows strong skills with less experience - high growth potential",
                    "candidates": [c.candidate_id],
                    "action": "Consider for junior/mid-level role or mentorship program"
                })
                break  # Only report one
        
        return {
            "insights": insights,
            "percentiles": percentiles
        }
    
    def generate_predictive_recommendations(self, candidates: List[Candidate], jd: JobDescription) -> Dict:
        """Generate predictive hiring recommendations"""
        
        recommendations = {}
        
        for c in candidates[:10]:  # Top 10
            score = c.match_score
            exp_ratio = c.experience_years / jd.min_experience if jd.min_experience > 0 else 1
            missing_count = len(c.explanation.get('missing_required_skills', []))
            
            # Predictive scoring
            if score >= 0.85 and missing_count <= 1:
                recommendation = "strong_hire"
                confidence = 0.90
                reasoning = "Exceptional match with minimal skill gaps"
            elif score >= 0.75 and missing_count <= 2:
                recommendation = "hire"
                confidence = 0.80
                reasoning = "Strong match with manageable skill gaps"
            elif score >= 0.65:
                recommendation = "interview"
                confidence = 0.70
                reasoning = "Promising candidate, needs interview validation"
            else:
                recommendation = "maybe"
                confidence = 0.60
                reasoning = "Moderate match, consider if pool is limited"
            
            # Adjust for experience
            if exp_ratio > 1.5:
                reasoning += " | Overqualified - may seek more challenging role"
                confidence *= 0.95
            elif exp_ratio < 0.8:
                reasoning += " | Underqualified - may need extended ramp-up"
                confidence *= 0.90
            
            recommendations[c.candidate_id] = {
                "recommendation": recommendation,
                "confidence": round(confidence, 2),
                "reasoning": reasoning,
                "predicted_success_rate": round(score * confidence, 2),
                "risk_factors": self._identify_risk_factors(c, jd),
                "strengths": c.explanation.get('key_strengths', [])[:3]
            }
        
        return recommendations
    
    def _identify_risk_factors(self, candidate: Candidate, jd: JobDescription) -> List[str]:
        """Identify hiring risk factors"""
        
        risks = []
        
        missing = len(candidate.explanation.get('missing_required_skills', []))
        if missing > 3:
            risks.append(f"Significant skill gaps ({missing} missing skills)")
        
        exp_ratio = candidate.experience_years / jd.min_experience if jd.min_experience > 0 else 1
        if exp_ratio > 1.8:
            risks.append("Overqualified - retention risk")
        elif exp_ratio < 0.6:
            risks.append("Underqualified - extended ramp-up needed")
        
        if candidate.match_score < 0.7:
            risks.append("Below qualification threshold")
        
        return risks if risks else ["No significant risks identified"]


class AINativeHRAgent(UpgradedHRAgent):
    """
    AI-Native HR Agent with strategic intelligence
    Extends UpgradedHRAgent with executive summaries and insights
    """
    
    def __init__(self, use_llm=True, fast_mode=True, **kwargs):
        super().__init__(use_llm=use_llm, fast_mode=fast_mode, **kwargs)
        self.strategic = AIStrategicInsights(use_llm, fast_mode=fast_mode)
        self.executive_summary = None
        self.cross_candidate_insights = None
        self.predictive_recommendations = None
        logger.info(f"✅ AI-Native HR Agent initialized (fast_mode={fast_mode})")
    
    def screen_resumes(self, candidates: List[Candidate], jd: JobDescription):
        """Screen with AI insights generation"""
        
        # Call parent screening
        ranked = super().screen_resumes(candidates, jd)
        
        # Generate AI insights
        logger.info("🤖 Generating AI strategic insights...")
        
        self.executive_summary = self.strategic.generate_executive_summary(ranked, jd)
        self.cross_candidate_insights = self.strategic.generate_cross_candidate_insights(ranked)
        self.predictive_recommendations = self.strategic.generate_predictive_recommendations(ranked, jd)
        
        logger.info("✅ AI insights generated")
        
        return ranked
    
    def export_results(self):
        """Export with AI insights"""
        
        base_results = super().export_results()
        
        # Add AI-native features
        base_results["ai_insights"] = {
            "executive_summary": self.executive_summary,
            "cross_candidate_insights": self.cross_candidate_insights,
            "predictive_recommendations": self.predictive_recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
        base_results["metadata"]["version"] = "6.0-ai-native"
        base_results["metadata"]["features"]["executive_summary"] = True
        base_results["metadata"]["features"]["cross_candidate_insights"] = True
        base_results["metadata"]["features"]["predictive_recommendations"] = True
        
        return base_results


# Quick test
if __name__ == "__main__":
    print("🧪 Testing AI-Native HR Agent")
    print("=" * 50)
    
    from data_loader import load_candidates, create_job_from_dataset
    
    # Load data
    candidates = load_candidates("data/resume_dataset_1200.csv")[:50]  # Test with 50
    jd = create_job_from_dataset("data/resume_dataset_1200.csv")
    
    # Initialize agent
    agent = AINativeHRAgent(use_llm=True)
    
    # Screen
    ranked = agent.screen_resumes(candidates, jd)
    
    # Show results
    print(f"\n📊 Executive Summary:")
    print(agent.executive_summary['summary'])
    
    print(f"\n🎯 Key Findings:")
    for finding in agent.executive_summary['key_findings']:
        print(f"  • {finding}")
    
    print(f"\n💡 Recommendations:")
    for rec in agent.executive_summary['recommendations']:
        print(f"  • {rec}")
    
    print(f"\n🔍 Cross-Candidate Insights:")
    for insight in agent.cross_candidate_insights['insights']:
        print(f"  • [{insight['severity'].upper()}] {insight['title']}")
        print(f"    {insight['description']}")
    
    print(f"\n🎯 Top 3 Predictive Recommendations:")
    for i, c in enumerate(ranked[:3], 1):
        pred = agent.predictive_recommendations[c.candidate_id]
        print(f"  {i}. {c.name}: {pred['recommendation'].upper()} ({pred['confidence']:.0%} confidence)")
        print(f"     {pred['reasoning']}")
    
    print("\n🎉 AI-Native system ready!")
