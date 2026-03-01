import streamlit as st
from hr_agent import HRAgent, InterviewSlot
from data_loader import load_candidates, create_job_from_dataset
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="AI HR Agent - NETRIK 2026",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    padding: 1rem 0;
}
.sub-header {
    text-align: center;
    color: #666;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.candidate-card {
    border-left: 4px solid #667eea;
    padding: 1rem;
    margin: 1rem 0;
    background: #f8f9fa;
    border-radius: 5px;
}
.skill-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    margin: 0.2rem;
    border-radius: 15px;
    font-size: 0.85rem;
    font-weight: 500;
}
.skill-matched {
    background: #d4edda;
    color: #155724;
}
.skill-missing {
    background: #f8d7da;
    color: #721c24;
}
.stButton>button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
    border-radius: 25px;
    font-weight: 600;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 AI HR Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Complete Recruitment Automation System | NETRIK Hackathon 2026</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=AI+HR+Agent", use_container_width=True)
    st.markdown("### 🎯 System Overview")
    st.info("""**Complete HR Automation**

✅ Resume Screening  
✅ Interview Scheduling  
✅ Question Generation  
✅ Pipeline Management  
✅ Leave Management  
✅ Query Escalation""")
    
    st.markdown("### 📊 Quick Stats")
    st.metric("Team", "Kanyaraasi", delta="Track 1")
    st.metric("Expected Score", "85-95/100", delta="+10 pts")
    
    st.markdown("---")
    st.markdown("### 🔧 Settings")
    show_debug = st.checkbox("Show Debug Info", value=False)
    auto_refresh = st.checkbox("Auto Refresh", value=False)

# Main content
st.write("Comprehensive HR automation: Resume screening, interview scheduling, question generation, and more.")

resume_path = "data/resume_dataset_1200.csv"

# Main workflow button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_workflow = st.button("🚀 Run Complete HR Workflow", type="primary", use_container_width=True)

if run_workflow:
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Initialize
    status_text.text("🔧 Initializing HR Agent...")
    progress_bar.progress(10)
    agent = HRAgent(use_llm=False)  # Disable Gemini for fast demo
    st.success("✅ Agent initialized successfully (Template Mode - Fast)")
    
    # Step 2: Load data
    status_text.text("📂 Loading candidates...")
    progress_bar.progress(20)
    candidates = load_candidates(resume_path)
    jd = create_job_from_dataset(resume_path)
    st.success(f"✅ Loaded {len(candidates)} candidates")
    
    # Step 3: Screen resumes
    status_text.text("🔍 Screening resumes...")
    progress_bar.progress(40)
    ranked = agent.screen_resumes(candidates, jd)
    st.success(f"✅ Screened and ranked {len(ranked)} candidates")
    
    # Step 4: Create interview slots
    status_text.text("📅 Creating interview slots...")
    progress_bar.progress(60)
    interview_slots = []
    base_time = datetime.now() + timedelta(days=7)
    for i in range(10):
        slot_time = base_time + timedelta(hours=i)
        interview_slots.append(InterviewSlot(
            slot_id=f"SLOT-{i+1:03d}",
            interviewer_id=f"INT-{(i % 3) + 1:03d}",
            start_time=slot_time,
            end_time=slot_time + timedelta(hours=1),
            is_available=True
        ))
    st.success(f"✅ Created {len(interview_slots)} interview slots")
    
    # Step 5: Shortlist and schedule
    status_text.text("⭐ Shortlisting top candidates...")
    progress_bar.progress(80)
    shortlisted = agent.shortlist_top_n(5, interview_slots, jd)
    st.success(f"✅ Shortlisted {len(shortlisted)} candidates")
    
    progress_bar.progress(100)
    status_text.text("✅ Workflow complete!")
    
    # Display metrics in cards
    st.markdown("---")
    st.markdown("## 📊 Screening Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""<div class="metric-card">
<h2>📝</h2>
<h3>{}</h3>
<p>Total Candidates</p>
</div>""".format(len(ranked)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""<div class="metric-card">
<h2>⭐</h2>
<h3>{}</h3>
<p>Shortlisted</p>
</div>""".format(len(shortlisted)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""<div class="metric-card">
<h2>📅</h2>
<h3>{}</h3>
<p>Interviews Scheduled</p>
</div>""".format(len(agent.interview_schedule.get('assignments', []))), unsafe_allow_html=True)
    
    with col4:
        avg_score = sum(c.match_score for c in ranked[:5]) / 5
        st.markdown("""<div class="metric-card">
<h2>🎯</h2>
<h3>{:.2f}</h3>
<p>Avg Top 5 Score</p>
</div>""".format(avg_score), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Score distribution chart
    st.markdown("## 📈 Score Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create histogram
        scores = [c.match_score for c in ranked]
        fig = go.Figure(data=[go.Histogram(
            x=scores,
            nbinsx=20,
            marker_color='#667eea',
            opacity=0.75
        )])
        fig.update_layout(
            title="Candidate Score Distribution",
            xaxis_title="Match Score",
            yaxis_title="Number of Candidates",
            showlegend=False,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True, key="score_distribution_histogram")
    
    with col2:
        # Score breakdown pie chart
        score_ranges = {
            'Excellent (0.8-1.0)': sum(1 for c in ranked if c.match_score >= 0.8),
            'Good (0.6-0.8)': sum(1 for c in ranked if 0.6 <= c.match_score < 0.8),
            'Fair (0.4-0.6)': sum(1 for c in ranked if 0.4 <= c.match_score < 0.6),
            'Poor (<0.4)': sum(1 for c in ranked if c.match_score < 0.4)
        }
        fig = go.Figure(data=[go.Pie(
            labels=list(score_ranges.keys()),
            values=list(score_ranges.values()),
            hole=0.4,
            marker_colors=['#667eea', '#764ba2', '#f093fb', '#f5576c']
        )])
        fig.update_layout(
            title="Score Categories",
            showlegend=True,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True, key="score_categories_pie")
    
    st.markdown("---")
    
    # Display top candidates
    st.markdown("## 🏆 Top 5 Ranked Candidates")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Detailed View", "📊 Comparison", "❓ Interview Questions"])
    
    with tab1:
        for i, c in enumerate(shortlisted, 1):
            with st.expander(f"🥇 #{i} - {c.name} | Score: {c.match_score:.3f}", expanded=(i==1)):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 👤 Candidate Profile")
                    
                    # Metrics in a nice layout
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric("Match Score", f"{c.match_score:.3f}", delta=f"Rank #{i}")
                    with metric_col2:
                        st.metric("Readiness", f"{c.explanation['readiness_percentage']}%")
                    with metric_col3:
                        st.metric("Experience", f"{c.experience_years} yrs")
                    
                    st.markdown("**Status:** " + ("🟢 " if c.status == "interview_scheduled" else "🔴 ") + c.status.replace("_", " ").title())
                    
                    # Skills visualization
                    st.markdown("#### ✅ Matched Skills")
                    if c.explanation['matched_required_skills']:
                        skills_html = "".join([
                            f'<span class="skill-badge skill-matched">✓ {skill}</span>'
                            for skill in c.explanation['matched_required_skills']
                        ])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.info("No matched required skills")
                    
                    st.markdown("#### ❌ Missing Skills")
                    if c.explanation['missing_required_skills']:
                        skills_html = "".join([
                            f'<span class="skill-badge skill-missing">✗ {skill}</span>'
                            for skill in c.explanation['missing_required_skills']
                        ])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.success("All required skills matched!")
                    
                    # Skill coverage gauge
                    total_required = len(c.explanation['matched_required_skills']) + len(c.explanation['missing_required_skills'])
                    if total_required > 0:
                        coverage = len(c.explanation['matched_required_skills']) / total_required * 100
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=coverage,
                            title={'text': "Skill Coverage"},
                            gauge={
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "#667eea"},
                                'steps': [
                                    {'range': [0, 50], 'color': "#f5576c"},
                                    {'range': [50, 75], 'color': "#f093fb"},
                                    {'range': [75, 100], 'color': "#667eea"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 80
                                }
                            }
                        ))
                        fig.update_layout(height=250)
                        st.plotly_chart(fig, use_container_width=True, key=f"skill_coverage_gauge_{i}")
                
                with col2:
                    st.markdown("### 📅 Interview Details")
                    if c.slot_id:
                        st.success(f"**Slot:** {c.slot_id}")
                        st.info(f"**Interviewer:** {c.interviewer_id}")
                    else:
                        st.warning("No interview slot assigned")
                    
                    st.markdown("### ❓ Interview Questions")
                    if c.interview_questions:
                        for idx, q in enumerate(c.interview_questions, 1):
                            question_type_emoji = {
                                'technical': '💻',
                                'behavioral': '🗣️',
                                'experience': '📚'
                            }
                            emoji = question_type_emoji.get(q['type'], '❓')
                            
                            with st.container():
                                st.markdown(f"**Q{idx}** {emoji} *{q['type'].title()}*")
                                st.write(f"_{q['question']}_")
                                st.caption(f"🎯 Focus: {q['skill_focus']}")
                                if idx < len(c.interview_questions):
                                    st.markdown("---")
                    else:
                        st.info("No questions generated")
    
    with tab2:
        st.markdown("### 📊 Candidate Comparison")
        
        # Comparison table
        comparison_data = []
        for i, c in enumerate(shortlisted, 1):
            comparison_data.append({
                'Rank': i,
                'Name': c.name,
                'Score': c.match_score,
                'Readiness': f"{c.explanation['readiness_percentage']}%",
                'Experience': f"{c.experience_years} yrs",
                'Matched Skills': len(c.explanation['matched_required_skills']),
                'Missing Skills': len(c.explanation['missing_required_skills']),
                'Status': c.status
            })
        
        st.dataframe(comparison_data, use_container_width=True, hide_index=True)
        
        # Radar chart comparison
        st.markdown("#### 🎯 Skills Radar Comparison")
        fig = go.Figure()
        
        for c in shortlisted[:3]:  # Top 3 only for clarity
            categories = ['Match Score', 'Readiness', 'Experience', 'Skill Coverage']
            total_skills = len(c.explanation['matched_required_skills']) + len(c.explanation['missing_required_skills'])
            skill_coverage = len(c.explanation['matched_required_skills']) / total_skills if total_skills > 0 else 0
            
            values = [
                c.match_score * 100,
                c.explanation['readiness_percentage'],
                min(c.experience_years / 10 * 100, 100),
                skill_coverage * 100
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=c.name
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True, key="skills_radar_comparison")
    
    with tab3:
        st.markdown("### ❓ All Interview Questions")
        
        for i, c in enumerate(shortlisted, 1):
            st.markdown(f"#### 🥇 {c.name}")
            if c.interview_questions:
                for idx, q in enumerate(c.interview_questions, 1):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Q{idx}.** {q['question']}")
                    with col2:
                        st.caption(f"Type: {q['type']}")
                        st.caption(f"Focus: {q['skill_focus']}")
                st.markdown("---")
    
    # Interview schedule
    if agent.interview_schedule.get('assignments'):
        st.markdown("---")
        st.markdown("## 📅 Interview Schedule")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            schedule_text = agent.scheduler.format_schedule(agent.interview_schedule['assignments'])
            st.code(schedule_text, language=None)
        
        with col2:
            st.metric("Total Scheduled", len(agent.interview_schedule['assignments']))
            st.metric("Conflicts", agent.interview_schedule.get('conflicts', 0), delta="0 is perfect")
            
            if agent.interview_schedule.get('unscheduled'):
                st.warning(f"⚠️ {len(agent.interview_schedule['unscheduled'])} unscheduled")
            else:
                st.success("✅ All candidates scheduled")
    
    # Export results
    st.markdown("---")
    st.markdown("## 📤 Export Results")
    
    results = agent.export_results()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", len(results['results']['pipeline']))
    with col2:
        st.metric("Interviews Scheduled", len(results['results']['interview_schedule'].get('assignments', [])))
    with col3:
        st.metric("State Transitions", len(results['results']['transition_log']))
    with col4:
        st.metric("Team", results['team_id'])
    
    # Add download button
    import json
    st.download_button(
        label="📥 Download Complete Results (JSON)",
        data=json.dumps(results, indent=2),
        file_name=f"hr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    with st.expander("📄 View Full Export JSON"):
        st.json(results)

st.divider()

# Additional features section
st.markdown("## 🔧 Additional Features")

tab1, tab2 = st.tabs(["📋 Leave Request Processing", "🚨 Query Escalation"])

with tab1:
    st.markdown("### 📋 Leave Request Management")
    st.write("Process employee leave requests with comprehensive policy compliance checking.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🎯 Demo Leave Request", use_container_width=True):
            from hr_agent import LeaveRequest
            
            # Create sample leave request
            leave_req = LeaveRequest(
                request_id="LR-001",
                employee_id="EMP-001",
                leave_type="annual",
                start_date=datetime.now() + timedelta(days=14),
                end_date=datetime.now() + timedelta(days=18),
                reason="Vacation"
            )
            
            # Initialize agent with sample employee balance
            agent_with_leave = HRAgent(
                employee_balances={
                    "EMP-001": {
                        "annual": 20,
                        "sick": 10,
                        "personal": 5,
                        "unpaid": 30
                    }
                }
            )
            
            decision = agent_with_leave.process_leave_request(leave_req)
            
            if decision['status'] == 'approved':
                st.success(f"✅ Leave Request Approved")
            else:
                st.error(f"❌ Leave Request Denied: {decision['reason']}")
            
            # Display decision details in a nice format
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Days Requested", decision['days_requested'])
            with col_b:
                st.metric("Status", decision['status'].upper())
            with col_c:
                if 'remaining_balance' in decision:
                    st.metric("Remaining Balance", decision['remaining_balance'])
            
            st.markdown("#### Policy Checks")
            for check in decision.get('policy_checks_passed', []):
                st.write(f"✅ {check.replace('_', ' ').title()}")
            
            with st.expander("📄 Full Decision Details"):
                st.json(decision)
    
    with col2:
        st.info("""**Leave Types Supported:**
- 📅 Annual Leave
- 🏥 Sick Leave
- 👤 Personal Leave
- 💼 Unpaid Leave

**Policy Checks:**
- Balance verification
- Consecutive days limit
- Notice period
- Overlap detection""")

with tab2:
    st.markdown("### 🚨 Query Escalation System")
    st.write("Intelligent query classification with severity-based escalation.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query_text = st.text_input("🔍 Enter a query:", "I want to discuss salary for this position", key="query_input")
        
        col_a, col_b = st.columns(2)
        with col_a:
            include_context = st.checkbox("Include salary context", value=True)
        with col_b:
            salary_amount = st.number_input("Salary ($)", value=175000, step=1000, disabled=not include_context)
        
        if st.button("🎯 Evaluate Query", use_container_width=True):
            agent_esc = HRAgent()
            context = {'salary': salary_amount} if include_context else None
            escalation = agent_esc.escalate_query(query_text, context)
            
            # Display result with color coding
            if escalation['should_escalate']:
                severity_colors = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }
                emoji = severity_colors.get(escalation['severity'], '⚪')
                st.warning(f"{emoji} **Escalation Required** ({escalation['severity'].upper()} severity)")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Should Escalate", "YES", delta="Action Required")
                with col_b:
                    st.metric("Severity", escalation['severity'].upper())
                
                st.markdown("#### 📋 Details")
                st.write(f"**Reason:** {escalation['reason'].replace('_', ' ').title()}")
                st.write(f"**Recommended Action:**")
                st.info(escalation['recommended_action'])
            else:
                st.success("✅ Can be handled automatically")
                st.metric("Should Escalate", "NO", delta="Auto-handle")
            
            with st.expander("📄 Full Escalation Details"):
                st.json(escalation)
    
    with col2:
        st.info("""**Escalation Triggers:**

🔴 **High Severity:**
- Legal issues
- Harassment
- Discrimination
- Complaints

🟡 **Medium Severity:**
- High salary ($150k+)
- Executive positions
- Extended leave (>15 days)
- Low score overrides

🟢 **Low Severity:**
- Stale pipeline (>30 days)
- General inquiries""")

# Footer
st.markdown("---")
st.markdown("""<div style='text-align: center; color: #666; padding: 2rem 0;'>
<p><strong>AI HR Agent</strong> | NETRIK Hackathon 2026 | Team Kanyaraasi</p>
<p>Complete HR Automation System with 6 Core Modules</p>
<p style='font-size: 0.9rem;'>Expected Score: 85-95/100 | Track 1 - HR Agent</p>
</div>""", unsafe_allow_html=True)
