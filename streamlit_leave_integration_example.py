"""
Example: How to integrate Enhanced Leave Manager into Streamlit app
Add this to your app.py to demonstrate leave policy evaluation
"""

import streamlit as st
from enhanced_leave_manager import EnhancedLeaveManager, LeaveRequest
from datetime import datetime, timedelta


def add_leave_management_demo():
    """
    Add this function to your Streamlit app to demo leave management.
    Call it from your main app.py
    """
    
    st.markdown("## 📋 Enhanced Leave Management System")
    st.write("Demonstrates all 4 hackathon requirements with deterministic decisions")
    
    # Initialize manager
    if 'leave_manager' not in st.session_state:
        st.session_state.leave_manager = EnhancedLeaveManager()
    
    manager = st.session_state.leave_manager
    
    # Create tabs for different demos
    tab1, tab2, tab3 = st.tabs([
        "📝 Submit Leave Request",
        "📊 Employee Leave Summary",
        "🧪 Demo Scenarios"
    ])
    
    with tab1:
        st.markdown("### Submit New Leave Request")
        
        col1, col2 = st.columns(2)
        
        with col1:
            employee_name = st.text_input("Employee Name", "Michael Moore")
            department = st.selectbox("Department", ["IT", "HR", "Finance", "Operations", "Marketing"])
            position = st.selectbox("Position", [
                "Software Engineer", "HR Manager", "Accountant",
                "Financial Analyst", "Operations Manager", "SEO Analyst"
            ])
        
        with col2:
            leave_type = st.selectbox("Leave Type", [
                "Earned Leave", "Sick Leave", "Casual Leave",
                "Maternity Leave", "Paternity Leave"
            ])
            start_date = st.date_input("Start Date", datetime.now() + timedelta(days=7))
            end_date = st.date_input("End Date", datetime.now() + timedelta(days=11))
        
        reason = st.text_area("Reason", "Vacation")
        
        if st.button("🎯 Evaluate Leave Request", type="primary"):
            # Create request
            request = LeaveRequest(
                request_id=f"LR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                employee_name=employee_name,
                employee_id=f"EMP-{hash(employee_name) % 1000:03d}",
                department=department,
                position=position,
                leave_type=leave_type,
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.min.time()),
                reason=reason
            )
            
            # Evaluate
            decision = manager.evaluate_leave_request(request)
            
            # Display result
            if decision.decision_type == "APPROVED":
                st.success("✅ LEAVE REQUEST APPROVED")
                st.balloons()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Decision", "APPROVED", delta="✓")
                with col2:
                    requested_days = (request.end_date - request.start_date).days + 1
                    st.metric("Days Requested", requested_days)
                with col3:
                    if decision.remaining_balance:
                        st.metric("Remaining Balance", f"{decision.remaining_balance:.0f} days")
            else:
                st.error("❌ LEAVE REQUEST DENIED")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Decision", "DENIED", delta="✗")
                with col2:
                    requested_days = (request.end_date - request.start_date).days + 1
                    st.metric("Days Requested", requested_days)
            
            # Show formatted report
            st.markdown("### 📄 Decision Report")
            report = manager.format_decision_report(decision)
            st.code(report, language=None)
            
            # Show policy rules
            st.markdown("### 📋 Applied Policy Rules")
            for rule_id in decision.applied_policy_rules:
                st.write(f"✓ **{rule_id}**: {manager.POLICY_RULES[rule_id]}")
            
            # Show evidence
            with st.expander("🔍 View Complete Decision Evidence"):
                st.json(decision.decision_evidence)
    
    with tab2:
        st.markdown("### Employee Leave Summary")
        
        employee_search = st.text_input("Search Employee", "Michael Moore")
        
        if st.button("🔍 Get Summary"):
            summary = manager.get_employee_leave_summary(employee_search)
            
            if summary.get("status") == "NOT_FOUND":
                st.warning(f"No records found for {employee_search}")
            else:
                st.success(f"Found records for {employee_search}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Department", summary["department"])
                with col2:
                    st.metric("Position", summary["position"])
                with col3:
                    st.metric("Total Entitlement", f"{summary['total_entitlement']:.0f} days")
                with col4:
                    st.metric("Remaining", f"{summary['remaining_balance']:.0f} days")
                
                # Progress bar
                taken_percentage = (summary['taken_so_far'] / summary['total_entitlement']) * 100
                st.progress(taken_percentage / 100)
                st.caption(f"Used: {summary['taken_so_far']:.0f} days ({taken_percentage:.1f}%)")
                
                # Recent leaves
                st.markdown("#### Recent Leave History")
                for leave in summary.get("recent_leaves", []):
                    st.write(f"- **{leave['leave_type']}**: {leave['start_date']} to {leave['end_date']} ({leave['days_taken']} days)")
    
    with tab3:
        st.markdown("### 🧪 Demo Scenarios")
        st.write("Click buttons to test different scenarios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Test: Approved Request"):
                request = LeaveRequest(
                    request_id="DEMO-001",
                    employee_name="Nicole Day",
                    employee_id="EMP-007",
                    department="Operations",
                    position="Operations Manager",
                    leave_type="Earned Leave",
                    start_date=datetime(2024, 12, 25),
                    end_date=datetime(2024, 12, 28),
                    reason="Holiday"
                )
                decision = manager.evaluate_leave_request(request)
                st.code(manager.format_decision_report(decision), language=None)
            
            if st.button("❌ Test: Insufficient Balance"):
                request = LeaveRequest(
                    request_id="DEMO-002",
                    employee_name="Michael Moore",
                    employee_id="EMP-001",
                    department="IT",
                    position="Software Engineer",
                    leave_type="Earned Leave",
                    start_date=datetime(2025, 1, 1),
                    end_date=datetime(2025, 1, 25),  # 25 days
                    reason="Extended vacation"
                )
                decision = manager.evaluate_leave_request(request)
                st.code(manager.format_decision_report(decision), language=None)
        
        with col2:
            if st.button("❌ Test: Ineligible Leave Type"):
                request = LeaveRequest(
                    request_id="DEMO-003",
                    employee_name="Kevin Wall",
                    employee_id="EMP-009",
                    department="Marketing",
                    position="SEO Analyst",
                    leave_type="Maternity Leave",  # Not eligible
                    start_date=datetime(2024, 12, 15),
                    end_date=datetime(2024, 12, 20),
                    reason="Invalid"
                )
                decision = manager.evaluate_leave_request(request)
                st.code(manager.format_decision_report(decision), language=None)
            
            if st.button("❌ Test: Date Overlap"):
                # Create existing leave
                existing = LeaveRequest(
                    request_id="EXISTING-001",
                    employee_name="Daniel Schmidt",
                    employee_id="EMP-006",
                    department="Finance",
                    position="Financial Analyst",
                    leave_type="Earned Leave",
                    start_date=datetime(2024, 12, 10),
                    end_date=datetime(2024, 12, 15),
                    reason="Vacation",
                    status="approved"
                )
                
                # New overlapping request
                request = LeaveRequest(
                    request_id="DEMO-004",
                    employee_name="Daniel Schmidt",
                    employee_id="EMP-006",
                    department="Finance",
                    position="Financial Analyst",
                    leave_type="Sick Leave",
                    start_date=datetime(2024, 12, 12),  # Overlaps
                    end_date=datetime(2024, 12, 17),
                    reason="Medical"
                )
                
                decision = manager.evaluate_leave_request(request, [existing])
                st.code(manager.format_decision_report(decision), language=None)


# Example: How to add to your main app.py
"""
Add this to your app.py:

# At the top with other imports
from streamlit_leave_integration_example import add_leave_management_demo

# In your main app, add a new section
st.divider()
add_leave_management_demo()
"""
