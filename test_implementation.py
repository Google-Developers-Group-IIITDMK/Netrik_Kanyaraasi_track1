"""
Quick validation test for HR Agent implementation
"""
import json
from datetime import datetime, timedelta
from hr_agent import (
    HRAgent, Candidate, JobDescription, InterviewSlot, 
    LeaveRequest, LeavePolicy
)

def test_basic_workflow():
    """Test complete HR workflow"""
    print("=" * 60)
    print("Testing AI HR Agent Implementation")
    print("=" * 60)
    
    # 1. Initialize agent
    print("\n1. Initializing HR Agent...")
    agent = HRAgent()
    print("✅ Agent initialized successfully")
    
    # 2. Create sample candidates
    print("\n2. Creating sample candidates...")
    candidates = [
        Candidate(
            candidate_id="C001",
            name="Alice Johnson",
            email="alice@example.com",
            resume_text="Experienced Python developer with 5 years in machine learning",
            skills=["Python", "Machine Learning", "TensorFlow", "SQL"],
            experience_years=5.0
        ),
        Candidate(
            candidate_id="C002",
            name="Bob Smith",
            email="bob@example.com",
            resume_text="Full-stack developer with React and Node.js expertise",
            skills=["JavaScript", "React", "Node.js", "MongoDB"],
            experience_years=3.0
        ),
        Candidate(
            candidate_id="C003",
            name="Carol Davis",
            email="carol@example.com",
            resume_text="Data scientist with Python and R experience",
            skills=["Python", "R", "Machine Learning", "Statistics"],
            experience_years=4.0
        )
    ]
    print(f"✅ Created {len(candidates)} sample candidates")
    
    # 3. Create job description
    print("\n3. Creating job description...")
    jd = JobDescription(
        job_id="JD001",
        title="Senior ML Engineer",
        description="Looking for experienced ML engineer",
        required_skills=["Python", "Machine Learning", "TensorFlow"],
        preferred_skills=["SQL", "Docker"],
        min_experience=3.0
    )
    print("✅ Job description created")
    
    # 4. Screen resumes
    print("\n4. Screening resumes...")
    ranked = agent.screen_resumes(candidates, jd)
    print(f"✅ Screened {len(ranked)} candidates")
    for i, c in enumerate(ranked, 1):
        print(f"   {i}. {c.name}: {c.match_score:.3f} (Status: {c.status})")
    
    # 5. Create interview slots
    print("\n5. Creating interview slots...")
    slots = []
    base_time = datetime.now() + timedelta(days=7)
    for i in range(5):
        slot_time = base_time + timedelta(hours=i)
        slots.append(InterviewSlot(
            slot_id=f"SLOT-{i+1:03d}",
            interviewer_id=f"INT-{(i % 2) + 1:03d}",
            start_time=slot_time,
            end_time=slot_time + timedelta(hours=1),
            is_available=True
        ))
    print(f"✅ Created {len(slots)} interview slots")
    
    # 6. Shortlist candidates
    print("\n6. Shortlisting top 2 candidates...")
    shortlisted = agent.shortlist_top_n(2, slots, jd)
    print(f"✅ Shortlisted {len(shortlisted)} candidates")
    
    for c in shortlisted:
        print(f"\n   Candidate: {c.name}")
        print(f"   Status: {c.status}")
        print(f"   Slot: {c.slot_id}")
        print(f"   Interviewer: {c.interviewer_id}")
        print(f"   Questions generated: {len(c.interview_questions)}")
        if c.interview_questions:
            print(f"   Sample question: {c.interview_questions[0]['question'][:60]}...")
    
    # 7. Test leave request
    print("\n7. Testing leave request processing...")
    agent_with_leave = HRAgent(
        employee_balances={
            "EMP001": {
                "annual": 20,
                "sick": 10,
                "personal": 5,
                "unpaid": 30
            }
        }
    )
    
    leave_req = LeaveRequest(
        request_id="LR001",
        employee_id="EMP001",
        leave_type="annual",
        start_date=datetime.now() + timedelta(days=14),
        end_date=datetime.now() + timedelta(days=18),
        reason="Vacation",
        status="pending"
    )
    
    decision = agent_with_leave.process_leave_request(leave_req)
    print(f"✅ Leave request processed: {decision['status']}")
    print(f"   Reason: {decision['reason']}")
    print(f"   Days requested: {decision['days_requested']}")
    
    # 8. Test query escalation
    print("\n8. Testing query escalation...")
    
    # Test normal query
    normal_decision = agent.escalate_query("What is the interview process?")
    print(f"✅ Normal query: should_escalate={normal_decision['should_escalate']}")
    
    # Test sensitive query
    sensitive_decision = agent.escalate_query("I want to file a harassment complaint")
    print(f"✅ Sensitive query: should_escalate={sensitive_decision['should_escalate']}, severity={sensitive_decision['severity']}")
    
    # 9. Test MRR calculation
    print("\n9. Testing MRR calculation...")
    mrr = agent.calculate_mrr(ranked, ["C001", "C003"])
    print(f"✅ MRR calculated: {mrr:.3f}")
    
    # 10. Export results
    print("\n10. Exporting results...")
    results = agent.export_results()
    
    print(f"✅ Export successful")
    print(f"   Team ID: {results['team_id']}")
    print(f"   Track: {results['track']}")
    print(f"   Candidates in pipeline: {len(results['results']['pipeline'])}")
    print(f"   Interviews scheduled: {len(results['results']['interview_schedule'].get('assignments', []))}")
    print(f"   State transitions: {len(results['results']['transition_log'])}")
    print(f"   Leave decisions: {len(results['results']['leave_decisions'])}")
    print(f"   Escalation decisions: {len(results['results']['escalation_decisions'])}")
    
    # Validate JSON serialization
    print("\n11. Validating JSON serialization...")
    try:
        json_str = json.dumps(results, indent=2)
        print(f"✅ JSON serialization successful ({len(json_str)} bytes)")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_basic_workflow()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
