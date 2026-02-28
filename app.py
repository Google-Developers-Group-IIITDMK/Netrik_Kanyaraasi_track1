import streamlit as st
from hr_agent import HRAgent, InterviewSlot
from data_loader import load_candidates, create_job_from_dataset
from datetime import datetime, timedelta

st.set_page_config(page_title="AI HR Agent", layout="wide")

st.title("🤖 AI HR Agent — Complete Recruitment System")

st.write("Comprehensive HR automation: Resume screening, interview scheduling, question generation, and more.")

resume_path = "data/resume_dataset_1200.csv"

if st.button("🚀 Run Complete HR Workflow", type="primary"):
    
    with st.spinner("Initializing HR Agent..."):
        agent = HRAgent()
    
    # Load data
    with st.spinner("Loading candidates..."):
        candidates = load_candidates(resume_path)
        jd = create_job_from_dataset(resume_path)
        st.success(f"✅ Loaded {len(candidates)} candidates")
    
    # Screen resumes
    with st.spinner("Screening resumes..."):
        ranked = agent.screen_resumes(candidates, jd)
        st.success(f"✅ Screened and ranked {len(ranked)} candidates")
    
    # Create sample interview slots
    with st.spinner("Creating interview slots..."):
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
    
    # Shortlist top candidates
    with st.spinner("Shortlisting top 5 candidates and generating interview questions..."):
        shortlisted = agent.shortlist_top_n(5, interview_slots, jd)
        st.success(f"✅ Shortlisted {len(shortlisted)} candidates")
    
    # Display results
    st.header("📊 Top 5 Ranked Candidates")
    
    for i, c in enumerate(shortlisted, 1):
        with st.expander(f"#{i} - {c.name} (Score: {c.match_score:.3f})", expanded=(i==1)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Candidate Profile")
                st.metric("Match Score", f"{c.match_score:.3f}")
                st.metric("Readiness", f"{c.explanation['readiness_percentage']}%")
                st.metric("Experience", f"{c.experience_years} years")
                st.metric("Status", c.status)
                
                st.write("**Matched Skills:**")
                if c.explanation['matched_required_skills']:
                    for skill in c.explanation['matched_required_skills']:
                        st.write(f"✅ {skill}")
                else:
                    st.write("None")
                
                st.write("**Missing Skills:**")
                if c.explanation['missing_required_skills']:
                    for skill in c.explanation['missing_required_skills']:
                        st.write(f"❌ {skill}")
                else:
                    st.write("None")
            
            with col2:
                st.subheader("📅 Interview Details")
                if c.slot_id:
                    st.write(f"**Slot ID:** {c.slot_id}")
                    st.write(f"**Interviewer:** {c.interviewer_id}")
                else:
                    st.warning("No interview slot assigned")
                
                st.subheader("❓ Interview Questions")
                if c.interview_questions:
                    for idx, q in enumerate(c.interview_questions, 1):
                        st.write(f"**Q{idx}** ({q['type']}):")
                        st.write(f"_{q['question']}_")
                        st.caption(f"Focus: {q['skill_focus']}")
                        st.divider()
                else:
                    st.info("No questions generated")
    
    # Display interview schedule
    if agent.interview_schedule.get('assignments'):
        st.header("📅 Interview Schedule")
        schedule_text = agent.scheduler.format_schedule(agent.interview_schedule['assignments'])
        st.code(schedule_text, language=None)
        
        if agent.interview_schedule.get('unscheduled'):
            st.warning(f"⚠️ {len(agent.interview_schedule['unscheduled'])} candidates could not be scheduled")
    
    # Export results
    st.header("📤 Export Results")
    results = agent.export_results()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Candidates", len(results['results']['pipeline']))
    with col2:
        st.metric("Interviews Scheduled", len(results['results']['interview_schedule'].get('assignments', [])))
    with col3:
        st.metric("State Transitions", len(results['results']['transition_log']))
    
    with st.expander("View Full Export JSON"):
        st.json(results)

st.divider()

# Additional features section
st.header("🔧 Additional Features")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Leave Request Processing")
    st.write("Process employee leave requests with policy compliance checking.")
    if st.button("Demo Leave Request"):
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
        
        st.json(decision)

with col2:
    st.subheader("🚨 Query Escalation")
    st.write("Identify queries requiring human HR intervention.")
    
    query_text = st.text_input("Enter a query:", "I want to discuss salary for this position")
    
    if st.button("Evaluate Query"):
        agent_esc = HRAgent()
        escalation = agent_esc.escalate_query(query_text, {'salary': 175000})
        
        if escalation['should_escalate']:
            st.warning(f"⚠️ Escalation Required ({escalation['severity']} severity)")
            st.write(f"**Reason:** {escalation['reason']}")
            st.write(f"**Action:** {escalation['recommended_action']}")
        else:
            st.success("✅ Can be handled automatically")
        
        st.json(escalation)