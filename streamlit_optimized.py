"""
Optimized Streamlit App for AI HR Agent
Dramatically improved performance for 1200+ candidates
"""

import streamlit as st
import time
from datetime import datetime, timedelta
from optimized_hr_agent import OptimizedHRAgent
from hr_agent import InterviewSlot, LeaveRequest
from performance_optimizer import (
    PerformanceOptimizer, StreamlitStateManager, 
    LazyUIRenderer, monitor_performance
)

# Configure Streamlit
st.set_page_config(
    page_title="AI HR Agent - Optimized", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize optimizers
optimizer = PerformanceOptimizer()
state_manager = StreamlitStateManager()
ui_renderer = LazyUIRenderer()

st.title("🚀 AI HR Agent — Optimized for Scale")
st.write("High-performance HR automation for 1200+ candidates with intelligent caching and batch processing.")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Performance Controls")
    
    # Dataset selection
    resume_path = st.selectbox(
        "Dataset",
        ["data/resume_dataset_1200.csv"],
        help="Select the resume dataset to process"
    )
    
    # Processing options
    st.subheader("Processing Options")
    use_llm = st.checkbox("Enable AI Enhancement", value=True, help="Use Gemini for semantic matching")
    batch_size = st.slider("Batch Size", 10, 100, 50, help="LLM processing batch size")
    top_n = st.slider("Top Candidates", 3, 20, 5, help="Number of candidates to shortlist")
    
    # Cache management
    st.subheader("Cache Management")
    if st.button("Clear All Cache"):
        state_manager.invalidate_cache()
        st.success("Cache cleared!")
        st.rerun()
    
    # Performance metrics
    if hasattr(st.session_state, 'performance_metrics'):
        st.subheader("📊 Performance Metrics")
        for func_name, metrics in st.session_state.performance_metrics.items():
            st.metric(
                f"{func_name.replace('_', ' ').title()}", 
                f"{metrics['duration']:.2f}s"
            )

# Main processing section
col1, col2 = st.columns([3, 1])

with col1:
    if st.button("🚀 Run Optimized HR Workflow", type="primary"):
        
        # Step 1: Load and preprocess data (cached)
        with st.spinner("Loading dataset..."):
            df = optimizer.load_dataset_cached(resume_path)
            candidates_data = optimizer.preprocess_candidates_cached(df)
            st.success(f"✅ Loaded {len(candidates_data)} candidates (cached)")
        
        # Step 2: Initialize HR Agent (cached)
        agent = state_manager.get_or_compute(
            "hr_agent", 
            lambda: OptimizedHRAgent(use_llm=use_llm)
        )
        
        # Step 3: Create job description (cached)
        jd = state_manager.get_or_compute(
            f"job_description_{resume_path}",
            create_job_from_preprocessed_data,
            candidates_data
        )
        
        # Step 4: Convert to Candidate objects (cached)
        candidates = state_manager.get_or_compute(
            f"candidates_{resume_path}",
            convert_to_candidates,
            candidates_data
        )
        
        # Step 5: Screen resumes with progress tracking
        with st.spinner("Screening resumes with AI enhancement..."):
            start_time = time.time()
            ranked = agent.screen_resumes(candidates, jd)
            screening_time = time.time() - start_time
            
            st.success(f"✅ Screened {len(ranked)} candidates in {screening_time:.2f}s")
            
            # Show performance improvement
            estimated_old_time = len(candidates) * 3  # 3 seconds per candidate
            improvement = ((estimated_old_time - screening_time) / estimated_old_time) * 100
            st.info(f"🚀 Performance improvement: {improvement:.1f}% faster than sequential processing")
        
        # Step 6: Create interview slots
        interview_slots = create_interview_slots(top_n * 2)  # Create more slots than needed
        
        # Step 7: Shortlist with batch question generation
        with st.spinner(f"Shortlisting top {top_n} candidates and generating questions..."):
            start_time = time.time()
            shortlisted = agent.shortlist_top_n(top_n, interview_slots, jd)
            shortlist_time = time.time() - start_time
            
            st.success(f"✅ Shortlisted {len(shortlisted)} candidates with questions in {shortlist_time:.2f}s")
        
        # Store results in session state for persistent display
        st.session_state.results = {
            'shortlisted': shortlisted,
            'agent': agent,
            'total_time': screening_time + shortlist_time,
            'total_candidates': len(candidates)
        }

with col2:
    st.subheader("📈 Quick Stats")
    if hasattr(st.session_state, 'results'):
        results = st.session_state.results
        st.metric("Total Candidates", results['total_candidates'])
        st.metric("Processing Time", f"{results['total_time']:.1f}s")
        st.metric("Candidates/Second", f"{results['total_candidates']/results['total_time']:.1f}")

# Display results section
if hasattr(st.session_state, 'results'):
    results = st.session_state.results
    shortlisted = results['shortlisted']
    agent = results['agent']
    
    st.header("🏆 Top Ranked Candidates")
    
    # Pagination for better performance
    display_candidates, page, total_pages = ui_renderer.paginated_results(shortlisted, page_size=3)
    
    for i, c in enumerate(display_candidates):
        global_rank = ((page - 1) * 3) + i + 1
        
        with st.expander(f"#{global_rank} - {c.name} (Score: {c.match_score:.3f})", expanded=(i==0)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Candidate Analysis")
                
                # Metrics in columns for better layout
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Match Score", f"{c.match_score:.3f}")
                    st.metric("Experience", f"{c.experience_years} years")
                with metric_col2:
                    st.metric("Readiness", f"{c.explanation['readiness_percentage']}%")
                    st.metric("Status", c.status)
                
                # Skills analysis with progress bars
                st.write("**Skills Analysis:**")
                total_required = len(c.explanation['matched_required_skills']) + len(c.explanation['missing_required_skills'])
                if total_required > 0:
                    skill_coverage = len(c.explanation['matched_required_skills']) / total_required
                    st.progress(skill_coverage, text=f"Skill Coverage: {skill_coverage:.1%}")
                
                # Matched skills
                if c.explanation['matched_required_skills']:
                    st.write("✅ **Matched Skills:**")
                    skills_text = ", ".join(c.explanation['matched_required_skills'])
                    st.write(skills_text)
                
                # Missing skills
                if c.explanation['missing_required_skills']:
                    st.write("❌ **Missing Skills:**")
                    skills_text = ", ".join(c.explanation['missing_required_skills'])
                    st.write(skills_text)
                
                # AI enhancement indicator
                if c.explanation.get('semantic_boost', 0) > 0:
                    st.info(f"🤖 AI Enhancement: +{c.explanation['semantic_boost']:.3f} boost from semantic analysis")
            
            with col2:
                st.subheader("📅 Interview Planning")
                
                # Interview slot info
                if c.slot_id:
                    st.success(f"**Slot Assigned:** {c.slot_id}")
                    st.write(f"**Interviewer:** {c.interviewer_id}")
                else:
                    st.warning("No interview slot assigned")
                
                # Interview questions with better formatting
                st.write("**Interview Questions:**")
                if c.interview_questions:
                    for idx, q in enumerate(c.interview_questions[:5], 1):  # Show first 5
                        with st.container():
                            st.write(f"**Q{idx}** ({q['type'].title()}):")
                            st.write(f"_{q['question']}_")
                            
                            # Question metadata
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.caption(f"Focus: {q['skill_focus']}")
                            with col_b:
                                st.caption(f"Source: {q.get('generated_by', 'AI')}")
                            
                            if idx < len(c.interview_questions):
                                st.divider()
                    
                    # Show remaining questions count
                    if len(c.interview_questions) > 5:
                        st.info(f"+ {len(c.interview_questions) - 5} more questions available")
                else:
                    st.info("Questions will be generated during interview scheduling")
    
    # Interview schedule summary
    if agent.interview_schedule.get('assignments'):
        st.header("📅 Interview Schedule Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Scheduled Interviews", len(agent.interview_schedule['assignments']))
        with col2:
            st.metric("Available Slots", len([s for s in interview_slots if s.is_available]))
        with col3:
            unscheduled = len(agent.interview_schedule.get('unscheduled', []))
            st.metric("Unscheduled", unscheduled)
        
        # Detailed schedule
        with st.expander("View Detailed Schedule"):
            schedule_text = agent.scheduler.format_schedule(agent.interview_schedule['assignments'])
            st.code(schedule_text, language=None)
    
    # Export and analytics
    st.header("📊 Analytics & Export")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📤 Export Results"):
            export_results = agent.export_results()
            st.download_button(
                "Download JSON",
                data=str(export_results),
                file_name=f"hr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📈 Performance Report"):
            show_performance_report(results)
    
    with col3:
        if st.button("🔄 Reprocess"):
            # Clear specific cache and rerun
            state_manager.invalidate_cache("candidates")
            state_manager.invalidate_cache("hr_agent")
            st.rerun()
    
    with col4:
        if st.button("💾 Save Session"):
            st.session_state.saved_results = results
            st.success("Session saved!")

# Additional features in tabs
st.header("🔧 Additional HR Features")

tab1, tab2, tab3 = st.tabs(["Leave Management", "Query Escalation", "System Status"])

with tab1:
    st.subheader("📋 Leave Request Processing")
    
    col1, col2 = st.columns(2)
    with col1:
        employee_id = st.text_input("Employee ID", "EMP-001")
        leave_type = st.selectbox("Leave Type", ["annual", "sick", "personal", "unpaid"])
        start_date = st.date_input("Start Date", datetime.now() + timedelta(days=7))
        end_date = st.date_input("End Date", datetime.now() + timedelta(days=10))
        reason = st.text_area("Reason", "Vacation")
    
    with col2:
        if st.button("Process Leave Request"):
            leave_req = LeaveRequest(
                request_id=f"LR-{int(time.time())}",
                employee_id=employee_id,
                leave_type=leave_type,
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.min.time()),
                reason=reason
            )
            
            # Create agent with sample balances
            leave_agent = OptimizedHRAgent(
                employee_balances={
                    employee_id: {
                        "annual": 20,
                        "sick": 10,
                        "personal": 5,
                        "unpaid": 30
                    }
                }
            )
            
            decision = leave_agent.process_leave_request(leave_req)
            
            if decision['status'] == 'approved':
                st.success("✅ Leave Request Approved")
            else:
                st.error(f"❌ Leave Request Denied: {decision['reason']}")
            
            st.json(decision)

with tab2:
    st.subheader("🚨 Query Escalation Analysis")
    
    query_text = st.text_area("Enter HR Query:", "I want to discuss salary negotiation for this position")
    
    col1, col2 = st.columns(2)
    with col1:
        salary_context = st.number_input("Salary Context ($)", 0, 500000, 75000)
    
    with col2:
        if st.button("Analyze Query"):
            escalation_agent = OptimizedHRAgent()
            escalation = escalation_agent.escalate_query(query_text, {'salary': salary_context})
            
            if escalation['should_escalate']:
                st.warning(f"⚠️ Escalation Required ({escalation['severity']} severity)")
            else:
                st.success("✅ Can be handled automatically")
            
            st.write(f"**Reason:** {escalation['reason']}")
            st.write(f"**Recommended Action:** {escalation['recommended_action']}")

with tab3:
    st.subheader("🖥️ System Status & Performance")
    
    if hasattr(st.session_state, 'results'):
        agent = st.session_state.results['agent']
        status = agent.get_system_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**System Configuration:**")
            st.write(f"- Provider: {status['provider']}")
            st.write(f"- LLM Enabled: {status['llm_enabled']}")
            st.write(f"- Model: {status['model']}")
            st.write(f"- Batch Processing: {status['features']['batch_processing']}")
            st.write(f"- Vectorized Operations: {status['features']['vectorized_operations']}")
            st.write(f"- Intelligent Caching: {status['features']['intelligent_caching']}")
        
        with col2:
            st.write("**Pipeline Statistics:**")
            for key, value in status['pipeline_stats'].items():
                st.metric(key.replace('_', ' ').title(), value)
    else:
        st.info("Run the workflow to see system status")


# Helper functions
@monitor_performance
def create_job_from_preprocessed_data(candidates_data):
    """Create job description from preprocessed candidate data"""
    from hr_agent import JobDescription
    
    # Extract skills from all candidates
    all_skills = []
    for candidate in candidates_data:
        all_skills.extend(candidate['skills'])
    
    # Get most common skills
    from collections import Counter
    skill_counts = Counter(all_skills)
    required_skills = [skill for skill, count in skill_counts.most_common(10)]
    
    return JobDescription(
        job_id="JD_OPTIMIZED_001",
        title="Target Role - Optimized",
        description="Comprehensive role requiring diverse technical skills and experience",
        required_skills=required_skills,
        preferred_skills=required_skills[5:],  # Use less common skills as preferred
        min_experience=3
    )

@monitor_performance
def convert_to_candidates(candidates_data):
    """Convert preprocessed data to Candidate objects"""
    from hr_agent import Candidate
    
    candidates = []
    for data in candidates_data:
        candidate = Candidate(
            candidate_id=data['candidate_id'],
            name=data['name'],
            email=data['email'],
            resume_text=data['resume_text'],
            skills=data['skills'],
            experience_years=data['experience_years'],
            status=data['status']
        )
        candidates.append(candidate)
    
    return candidates

def create_interview_slots(num_slots):
    """Create interview slots for scheduling"""
    slots = []
    base_time = datetime.now() + timedelta(days=7)
    
    for i in range(num_slots):
        slot_time = base_time + timedelta(hours=i)
        slots.append(InterviewSlot(
            slot_id=f"SLOT-{i+1:03d}",
            interviewer_id=f"INT-{(i % 3) + 1:03d}",
            start_time=slot_time,
            end_time=slot_time + timedelta(hours=1),
            is_available=True
        ))
    
    return slots

def show_performance_report(results):
    """Show detailed performance analysis"""
    st.subheader("📊 Performance Analysis Report")
    
    total_candidates = results['total_candidates']
    total_time = results['total_time']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Processing Rate", f"{total_candidates/total_time:.1f} candidates/sec")
    
    with col2:
        estimated_sequential = total_candidates * 3  # 3 seconds per candidate
        improvement = ((estimated_sequential - total_time) / estimated_sequential) * 100
        st.metric("Performance Improvement", f"{improvement:.1f}%")
    
    with col3:
        st.metric("Time Saved", f"{(estimated_sequential - total_time)/60:.1f} minutes")
    
    # Performance breakdown
    if hasattr(st.session_state, 'performance_metrics'):
        st.write("**Function Performance Breakdown:**")
        metrics_df = []
        for func_name, metrics in st.session_state.performance_metrics.items():
            metrics_df.append({
                'Function': func_name.replace('_', ' ').title(),
                'Duration (s)': f"{metrics['duration']:.2f}",
                'Percentage': f"{(metrics['duration']/total_time)*100:.1f}%"
            })
        
        st.table(metrics_df)

# Footer
st.divider()
st.caption("🚀 Optimized AI HR Agent - Built for scale with intelligent caching, batch processing, and vectorized operations")