"""
AI-Native Streamlit App - Hackathon Edition
Features: Executive Summary, Strategic Insights, Predictive Recommendations, AI Narrative
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime, timedelta

# Import AI-native components
try:
    from hr_agent_ai_native import AINativeHRAgent as HRAgent, Candidate, JobDescription, InterviewSlot
    from hr_agent_upgraded import LeaveRequest
    from data_loader import load_candidates, create_job_from_dataset
    AI_NATIVE_AVAILABLE = True
except ImportError:
    st.error("⚠️  AI-Native components not available")
    AI_NATIVE_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="AI-Native HR Agent",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .executive-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .insight-card {
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        background: #f8f9fa;
        border-radius: 5px;
    }
    .insight-high { border-left-color: #ef4444; }
    .insight-medium { border-left-color: #f59e0b; }
    .insight-low { border-left-color: #10b981; }
    .recommendation-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
    .rec-strong-hire { background: #10b981; color: white; }
    .rec-hire { background: #3b82f6; color: white; }
    .rec-interview { background: #f59e0b; color: white; }
    .rec-maybe { background: #6b7280; color: white; }
    .confidence-bar {
        height: 8px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
    }
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
        transition: width 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 AI-Native HR Agent")
st.markdown("**Intelligent Hiring with Executive Insights & Predictive Analytics**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    use_llm = st.checkbox("Enable AI (Gemini)", value=True)
    fast_mode = st.checkbox("Fast Mode (Rule-based)", value=True, help="Use rule-based logic for speed. Uncheck for full LLM analysis (slower)")
    num_candidates = st.slider("Candidates to analyze", 50, 1200, 100, 50)
    
    st.markdown("---")
    st.markdown("### 🎯 AI Features")
    st.markdown("""
    - 📊 Executive Summary
    - 🔍 Cross-Candidate Insights
    - 🎯 Predictive Recommendations
    - 💡 Strategic Insights
    - 📈 Confidence Scoring
    """)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'ranked' not in st.session_state:
    st.session_state.ranked = None
if 'jd' not in st.session_state:
    st.session_state.jd = None

# Main workflow
st.header("🚀 AI-Powered Hiring Workflow")

if st.button("▶️ Run AI Analysis", type="primary"):
    
    # Initialize
    with st.spinner("Initializing AI-Native HR Agent..."):
        agent = HRAgent(use_llm=use_llm, fast_mode=fast_mode)
        st.session_state.agent = agent
        time.sleep(0.5)
    
    st.success("✅ Agent initialized")
    
    # Load data
    with st.spinner(f"Loading {num_candidates} candidates..."):
        candidates = load_candidates("data/resume_dataset_1200.csv")[:num_candidates]
        jd = create_job_from_dataset("data/resume_dataset_1200.csv")
        st.session_state.jd = jd
        time.sleep(0.3)
    
    st.success(f"✅ Loaded {len(candidates)} candidates")
    
    # Screen with AI insights
    with st.spinner("🤖 AI is analyzing candidates..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📊 Screening resumes...")
        progress_bar.progress(20)
        time.sleep(0.3)
        
        status_text.text("🧠 Performing semantic analysis...")
        progress_bar.progress(40)
        
        ranked = agent.screen_resumes(candidates, jd)
        st.session_state.ranked = ranked
        
        status_text.text("💡 Generating strategic insights...")
        progress_bar.progress(70)
        time.sleep(0.3)
        
        status_text.text("🎯 Creating predictive recommendations...")
        progress_bar.progress(90)
        time.sleep(0.3)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        time.sleep(0.5)
    
    st.success("🎉 AI Analysis Complete!")

# ========================================
# TABS FOR ALL 6 MODULES (Always visible)
# ========================================
st.markdown("---")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Resume Screening", 
    "📅 Interview Scheduling", 
    "❓ Questionnaire Generation",
    "🔄 Pipeline Management",
    "🏖️ Leave Management",
    "🚨 Escalation Handling"
])

# Check if analysis has been run
if 'agent' not in st.session_state or 'ranked' not in st.session_state or 'jd' not in st.session_state or st.session_state.agent is None or st.session_state.ranked is None or st.session_state.jd is None:
    with tab1:
        st.info("👆 Click 'Run AI Analysis' above to start")
    with tab2:
        st.info("👆 Click 'Run AI Analysis' above to start")
    with tab3:
        st.info("👆 Click 'Run AI Analysis' above to start")
    with tab4:
        st.info("👆 Click 'Run AI Analysis' above to start")
    with tab5:
        st.info("👆 Click 'Run AI Analysis' above to start")
    with tab6:
        st.info("👆 Click 'Run AI Analysis' above to start")
else:
    agent = st.session_state.agent
    ranked = st.session_state.ranked
    jd = st.session_state.jd
    
    # ========================================
    # TAB 1: RESUME SCREENING + AI INSIGHTS
    # ========================================
    with tab1:
        st.markdown("## 📊 Executive Summary")
        
        if hasattr(agent, 'executive_summary') and agent.executive_summary:
            summary = agent.executive_summary
            
            st.markdown(f"""
            <div class="executive-summary">
                <h3>🎯 Hiring Intelligence Report</h3>
                <p style="font-size: 16px; line-height: 1.6;">{summary['summary']}</p>
            <p style="font-size: 14px; opacity: 0.9;">
                <strong>Confidence:</strong> {summary['confidence']:.0%} | 
                <strong>Generated by:</strong> {summary['generated_by'].upper()}
            </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔍 Key Findings")
                for finding in summary['key_findings']:
                    st.markdown(f"- {finding}")
            
            with col2:
                st.markdown("### 💡 Strategic Recommendations")
                for rec in summary['recommendations']:
                    st.markdown(f"- {rec}")
        
        # ========================================
        # CROSS-CANDIDATE INSIGHTS
        # ========================================
        st.markdown("---")
        st.markdown("## 🔍 Strategic Insights")
        
        if hasattr(agent, 'cross_candidate_insights') and agent.cross_candidate_insights and agent.cross_candidate_insights.get('insights'):
            insights = agent.cross_candidate_insights['insights']
            
            for insight in insights:
                severity_class = f"insight-{insight['severity']}"
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[insight['severity']]
                
                st.markdown(f"""
                <div class="insight-card {severity_class}">
                    <h4>{severity_emoji} {insight['title']}</h4>
                    <p>{insight['description']}</p>
                    <p><strong>Recommended Action:</strong> {insight['action']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No strategic insights generated for this candidate pool")
        
        # ========================================
        # TOP CANDIDATES WITH PREDICTIONS
        # ========================================
        st.markdown("---")
        st.markdown("## 🏆 Top Candidates with AI Predictions")
        
        if ranked and len(ranked) > 0:
            for i, c in enumerate(ranked[:5], 1):
                with st.expander(f"#{i} - {c.name} | Match: {c.match_score:.1%}", expanded=(i==1)):
                    
                    # Get prediction
                    pred = {}
                    if hasattr(agent, 'predictive_recommendations') and agent.predictive_recommendations:
                        pred = agent.predictive_recommendations.get(c.candidate_id, {})
                    
                    rec = pred.get('recommendation', 'interview')
                    confidence = pred.get('confidence', 0.75)
                    
                    # Header with recommendation badge
                    rec_class = f"rec-{rec.replace('_', '-')}"
                    rec_display = rec.replace('_', ' ').title()
                    
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                    <span class="recommendation-badge {rec_class}">{rec_display}</span>
                    <span style="color: #666;">Confidence: {confidence:.0%}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Confidence bar
                st.markdown(f"""
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence*100}%"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Details in columns
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown("**📋 Profile**")
                    st.write(f"Experience: {c.experience_years} years")
                    st.write(f"Match Score: {c.match_score:.1%}")
                    
                    if hasattr(agent, 'cross_candidate_insights') and agent.cross_candidate_insights and agent.cross_candidate_insights.get('percentiles', {}).get(c.candidate_id):
                        perc = agent.cross_candidate_insights['percentiles'][c.candidate_id]
                        st.write(f"Percentile: Top {100-perc['percentile']:.0f}%")
                
                with col2:
                    st.markdown("**🎯 Skills**")
                    matched = c.explanation.get('matched_required_skills', [])
                    missing = c.explanation.get('missing_required_skills', [])
                    
                    if matched:
                        st.success(f"✅ {len(matched)} matched: {', '.join(matched[:3])}")
                    if missing:
                        st.warning(f"⚠️ {len(missing)} missing: {', '.join(missing[:3])}")
                
                with col3:
                    st.markdown("**📊 Metrics**")
                    st.metric("Readiness", f"{c.explanation.get('readiness_percentage', 0):.0f}%")
                    if pred.get('predicted_success_rate'):
                        st.metric("Success Rate", f"{pred['predicted_success_rate']:.0%}")
                
                # AI Reasoning
                st.markdown("---")
                st.markdown("**🤖 AI Reasoning**")
                st.info(pred.get('reasoning', 'No reasoning available'))
                
                # Risk factors
                if pred.get('risk_factors'):
                    st.markdown("**⚠️ Risk Factors**")
                    for risk in pred['risk_factors']:
                        st.markdown(f"- {risk}")
                
                # Strengths
                if pred.get('strengths'):
                    st.markdown("**💪 Key Strengths**")
                    for strength in pred['strengths']:
                        st.markdown(f"- {strength}")
                
                # Interview questions preview
                if c.interview_questions:
                    st.markdown("**💬 Sample Interview Questions**")
                    for q in c.interview_questions[:2]:
                        st.markdown(f"- {q['question']}")
                        st.caption(f"  Type: {q['type']} | Focus: {q['skill_focus']}")
        else:
            st.info("No candidates to display. Run analysis first.")
        
        # ========================================
        # CANDIDATE COMPARISON TABLE
        # ========================================
        st.markdown("---")
        st.markdown("## 📊 Candidate Comparison")
        
        if ranked and len(ranked) > 0:
            comparison_data = []
            for c in ranked[:10]:
                pred = {}
                if hasattr(agent, 'predictive_recommendations') and agent.predictive_recommendations:
                    pred = agent.predictive_recommendations.get(c.candidate_id, {})
                
                perc = {}
                if hasattr(agent, 'cross_candidate_insights') and agent.cross_candidate_insights:
                    perc = agent.cross_candidate_insights.get('percentiles', {}).get(c.candidate_id, {})
                
                comparison_data.append({
                    "Rank": ranked.index(c) + 1,
                    "Name": c.name,
                    "Match": f"{c.match_score:.1%}",
                    "Experience": f"{c.experience_years}y",
                    "Recommendation": pred.get('recommendation', 'N/A').replace('_', ' ').title(),
                    "Confidence": f"{pred.get('confidence', 0):.0%}",
                    "Percentile": f"Top {100-perc.get('percentile', 0):.0f}%" if perc else "N/A",
                    "Risks": len(pred.get('risk_factors', []))
                })
            
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No candidates to display. Run analysis first.")
        
        # ========================================
        # EXPORT
        # ========================================
        st.markdown("---")
        st.markdown("## 📥 Export Results")
        
        if ranked and len(ranked) > 0:
            results = agent.export_results()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Analyzed", len(ranked))
            with col2:
                st.metric("Qualified", len([c for c in ranked if c.match_score >= 0.7]))
            with col3:
                strong_hires = 0
                if hasattr(agent, 'predictive_recommendations') and agent.predictive_recommendations:
                    strong_hires = len([c for c in ranked[:10] if agent.predictive_recommendations.get(c.candidate_id, {}).get('recommendation') == 'strong_hire'])
                st.metric("Strong Hires", strong_hires)
            with col4:
                insights_count = 0
                if hasattr(agent, 'cross_candidate_insights') and agent.cross_candidate_insights:
                    insights_count = len(agent.cross_candidate_insights.get('insights', []))
                st.metric("AI Insights", insights_count)
            
            json_str = json.dumps(results, indent=2)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            st.download_button(
                label="📥 Download Complete Results (JSON)",
                data=json_str,
                file_name=f"ai_native_results_{timestamp}.json",
                mime="application/json",
                type="primary"
            )
            
            with st.expander("👁️ Preview AI Insights JSON"):
                st.json(results.get('ai_insights', {}))
        else:
            st.info("No results to export. Run analysis first.")
    
    # ========================================
    # TAB 2: INTERVIEW SCHEDULING
        # ========================================
    with tab2:
        st.markdown("## 📅 Interview Scheduling")
        
        # Generate sample slots
        from datetime import timedelta
        slots = []
        start_date = datetime.now() + timedelta(days=1)
        for i in range(20):
            slot_time = start_date + timedelta(hours=i)
            slots.append(InterviewSlot(
                slot_id=f"SLOT_{i+1:03d}",
                interviewer_id=f"INT_{(i%5)+1}",
                start_time=slot_time,
                end_time=slot_time + timedelta(hours=1),
                is_available=True
            ))
        
        if st.button("📅 Schedule Top 10 Candidates"):
            with st.spinner("Scheduling interviews..."):
                schedule_result = agent.schedule_interviews(ranked[:10], slots)
                
                st.success(f"✅ Scheduled {len(schedule_result['assignments'])} interviews")
                
                if schedule_result['assignments']:
                    st.markdown("### 📋 Interview Schedule")
                    schedule_df = pd.DataFrame(schedule_result['assignments'])
                    st.dataframe(schedule_df, use_container_width=True, hide_index=True)
                
                if schedule_result['unscheduled']:
                    st.warning(f"⚠️ {len(schedule_result['unscheduled'])} candidates could not be scheduled (no slots available)")
                
                st.info(f"✅ Zero conflicts: {schedule_result['conflicts']} overlapping interviews")
    
    # ========================================
    # TAB 3: QUESTIONNAIRE GENERATION
    # ========================================
    with tab3:
        st.markdown("## ❓ Interview Question Generation")
        
        st.info("Select a candidate to generate personalized interview questions")
        
        candidate_names = [f"{c.name} (Match: {c.match_score:.1%})" for c in ranked[:10]]
        selected_idx = st.selectbox("Select Candidate", range(len(candidate_names)), format_func=lambda x: candidate_names[x])
        
        if st.button("🎯 Generate Questions"):
            selected_candidate = ranked[selected_idx]
            
            with st.spinner(f"Generating questions for {selected_candidate.name}..."):
                questions = agent.generate_questions(selected_candidate, jd)
                
                st.success(f"✅ Generated {len(questions)} personalized questions")
                
                # Group by type
                tech_q = [q for q in questions if q['type'] == 'technical']
                behav_q = [q for q in questions if q['type'] == 'behavioral']
                sit_q = [q for q in questions if q['type'] == 'situational']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Technical", len(tech_q))
                with col2:
                    st.metric("Behavioral", len(behav_q))
                with col3:
                    st.metric("Situational", len(sit_q))
                
                st.markdown("---")
                
                for i, q in enumerate(questions, 1):
                    with st.expander(f"Q{i}: {q['type'].title()} - {q['skill_focus']}", expanded=(i<=2)):
                        st.markdown(f"**Question:** {q['question']}")
                        st.caption(f"**Rationale:** {q['rationale']}")
                        st.caption(f"**Difficulty:** {q['difficulty']} | **Generated by:** {q.get('generated_by', 'N/A')}")
    
    # ========================================
    # TAB 4: PIPELINE MANAGEMENT
    # ========================================
    with tab4:
        st.markdown("## 🔄 Pipeline State Management")
        
        st.info("Track candidate status transitions with validation")
        
        # Show current pipeline
        pipeline_data = []
        if hasattr(agent, 'pipeline') and agent.pipeline:
            for cid, c in list(agent.pipeline.items())[:15]:
                pipeline_data.append({
                    "ID": cid,
                    "Name": c.name,
                    "Status": c.status,
                    "Match": f"{c.match_score:.1%}",
                    "Last Updated": c.status_updated_at.strftime("%Y-%m-%d %H:%M")
                })
        
        st.markdown("### 📊 Current Pipeline Status")
        if pipeline_data:
            st.dataframe(pd.DataFrame(pipeline_data), use_container_width=True, hide_index=True)
        else:
            st.info("No candidates in pipeline yet")
        
        # Transition log
        st.markdown("### 📜 Transition Log")
        transitions = []
        if hasattr(agent, 'state'):
            transitions = agent.state.get_transition_log()
        
        if transitions:
            st.success(f"✅ {len(transitions)} valid transitions recorded")
            trans_df = pd.DataFrame(transitions[-10:])  # Last 10
            st.dataframe(trans_df, use_container_width=True, hide_index=True)
        else:
            st.info("No transitions yet. Transitions are logged when candidates move through the pipeline.")
        
        # Valid transitions reference
        with st.expander("📖 Valid State Transitions"):
            st.json({
                "applied": ["screened", "rejected"],
                "screened": ["interview_scheduled", "rejected"],
                "interview_scheduled": ["interviewed", "rejected"],
                "interviewed": ["offer_extended", "rejected"],
                "offer_extended": ["offer_accepted", "rejected"],
                "offer_accepted": ["hired", "rejected"],
                "hired": [],
                "rejected": []
            })
    
    # ========================================
    # TAB 5: LEAVE MANAGEMENT
    # ========================================
    with tab5:
        st.markdown("## 🏖️ Leave Request Management")
        
        st.info("Test leave policy enforcement with sample requests")
        
        # Sample leave request form
        col1, col2 = st.columns(2)
        with col1:
            emp_id = st.text_input("Employee ID", "EMP_001")
            leave_type = st.selectbox("Leave Type", ["annual", "sick", "personal", "unpaid"])
            start_date = st.date_input("Start Date", datetime.now() + timedelta(days=7))
        
        with col2:
            reason = st.text_area("Reason", "Personal matters")
            end_date = st.date_input("End Date", datetime.now() + timedelta(days=10))
        
        if st.button("📝 Submit Leave Request"):
            leave_request = LeaveRequest(
                request_id=f"LR_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                employee_id=emp_id,
                leave_type=leave_type,
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.min.time()),
                reason=reason
            )
            
            with st.spinner("Processing leave request..."):
                decision = agent.process_leave(leave_request)
                
                if decision.get('status') == 'approved':
                    st.success(f"✅ Leave Approved: {decision.get('reason', 'Request approved')}")
                    st.info(f"Days Requested: {decision.get('days_requested', 0)}")
                    st.info(f"Remaining Balance: {decision.get('remaining_balance', 0)}")
                else:
                    st.error(f"❌ Leave Denied: {decision.get('reason', 'Request denied')}")
                    st.info(f"Days Requested: {decision.get('days_requested', 0)}")
                    st.info(f"Current Balance: {decision.get('remaining_balance', 0)}")
                
                st.json(decision)
        
        # Show leave policies
        with st.expander("📋 Leave Policies"):
            if hasattr(agent, 'leave_policies') and agent.leave_policies:
                policies_data = []
                for policy_type, policy in agent.leave_policies.items():
                    policies_data.append({
                        "Type": policy_type.title(),
                        "Annual Quota": policy.annual_quota,
                        "Max Consecutive": policy.max_consecutive_days,
                        "Min Notice (days)": policy.min_notice_days
                    })
                st.dataframe(pd.DataFrame(policies_data), use_container_width=True, hide_index=True)
            else:
                st.info("Leave policies not available")
    
    # ========================================
    # TAB 6: ESCALATION HANDLING
    # ========================================
    with tab6:
        st.markdown("## 🚨 Query Escalation System")
        
        st.info("Test intelligent query categorization and escalation")
        
        # Sample queries
        sample_queries = [
            "Candidate is asking about salary range for senior position",
            "Need to schedule interview for tomorrow",
            "Question about company culture and work-life balance",
            "Urgent: Candidate has competing offer, needs decision today",
            "Can you tell me about the tech stack?",
            "CEO wants to interview this candidate personally"
        ]
        
        query_input = st.text_area("Enter Query", sample_queries[0], height=100)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔍 Evaluate Query", type="primary"):
                with st.spinner("Analyzing query..."):
                    decision = agent.escalate_query(query_input)
                    
                    priority_colors = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }
                    
                    st.markdown(f"### {priority_colors[decision['priority']]} Priority: {decision['priority'].upper()}")
                    st.markdown(f"**Reasoning:** {decision['reasoning']}")
                    st.markdown(f"**Recommended Action:** {decision['action']}")
                    
                    if decision['priority'] == 'high':
                        st.error("⚠️ HIGH PRIORITY - Immediate attention required")
                    elif decision['priority'] == 'medium':
                        st.warning("⚡ MEDIUM PRIORITY - Handle within 24 hours")
                    else:
                        st.success("✅ LOW PRIORITY - Standard processing")
        
        with col2:
            st.markdown("### Quick Tests")
            for i, sample in enumerate(sample_queries[:3], 1):
                if st.button(f"Test #{i}", key=f"sample_{i}"):
                    st.session_state.test_query = sample
        
        # Show escalation history
        st.markdown("### 📜 Escalation History")
        if hasattr(agent, 'escalation_decisions') and agent.escalation_decisions:
            esc_data = []
            for esc in agent.escalation_decisions[-5:]:
                esc_data.append({
                    "Query": esc['query'][:50] + "...",
                    "Priority": esc['decision']['priority'].upper(),
                    "Action": esc['decision']['action'][:40] + "..."
                })
            st.dataframe(pd.DataFrame(esc_data), use_container_width=True, hide_index=True)
        else:
            st.info("No escalations yet")

# Footer (outside tabs)
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 AI-Native HR Agent | Powered by Gemini 2.5 Flash</p>
    <p>Executive Summary • Strategic Insights • Predictive Recommendations</p>
</div>
""", unsafe_allow_html=True)

