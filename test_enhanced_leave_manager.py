"""
Test script for Enhanced Leave Manager
Demonstrates all hackathon requirements
"""

from enhanced_leave_manager import EnhancedLeaveManager, LeaveRequest, LeaveDecision
from datetime import datetime, timedelta
import json


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_leave_balance_check():
    """Test Requirement 1: Check available leave balance"""
    print_section("TEST 1: Leave Balance Check")
    
    manager = EnhancedLeaveManager()
    
    # Test case 1: Sufficient balance
    request1 = LeaveRequest(
        request_id="LR-001",
        employee_name="Michael Moore",
        employee_id="EMP-001",
        department="IT",
        position="Software Engineer",
        leave_type="Earned Leave",
        start_date=datetime(2024, 12, 26),
        end_date=datetime(2024, 12, 30),
        reason="Vacation"
    )
    
    decision1 = manager.evaluate_leave_request(request1)
    print(manager.format_decision_report(decision1))
    
    # Test case 2: Insufficient balance
    request2 = LeaveRequest(
        request_id="LR-002",
        employee_name="Michael Moore",
        employee_id="EMP-001",
        department="IT",
        position="Software Engineer",
        leave_type="Earned Leave",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 20),  # 20 days - exceeds balance
        reason="Extended vacation"
    )
    
    decision2 = manager.evaluate_leave_request(request2)
    print(manager.format_decision_report(decision2))


def test_leave_type_eligibility():
    """Test Requirement 2: Validate leave type eligibility"""
    print_section("TEST 2: Leave Type Eligibility Check")
    
    manager = EnhancedLeaveManager()
    
    # Test case 1: Eligible leave type
    request1 = LeaveRequest(
        request_id="LR-003",
        employee_name="Ashley Rogers",
        employee_id="EMP-003",
        department="Finance",
        position="Accountant",
        leave_type="Maternity Leave",
        start_date=datetime(2024, 12, 15),
        end_date=datetime(2024, 12, 20),
        reason="Maternity"
    )
    
    decision1 = manager.evaluate_leave_request(request1)
    print(manager.format_decision_report(decision1))
    
    # Test case 2: Ineligible leave type
    request2 = LeaveRequest(
        request_id="LR-004",
        employee_name="Kevin Wall",
        employee_id="EMP-009",
        department="Marketing",
        position="SEO Analyst",
        leave_type="Maternity Leave",  # Not eligible for male SEO Analyst
        start_date=datetime(2024, 12, 15),
        end_date=datetime(2024, 12, 20),
        reason="Invalid request"
    )
    
    decision2 = manager.evaluate_leave_request(request2)
    print(manager.format_decision_report(decision2))


def test_date_overlap_detection():
    """Test Requirement 3: Detect date-overlap conflicts"""
    print_section("TEST 3: Date Overlap Detection")
    
    manager = EnhancedLeaveManager()
    
    # Create an existing approved leave
    existing_leave = LeaveRequest(
        request_id="LR-005",
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
    
    # Test case 1: No overlap
    request1 = LeaveRequest(
        request_id="LR-006",
        employee_name="Daniel Schmidt",
        employee_id="EMP-006",
        department="Finance",
        position="Financial Analyst",
        leave_type="Sick Leave",
        start_date=datetime(2024, 12, 20),
        end_date=datetime(2024, 12, 22),
        reason="Medical"
    )
    
    decision1 = manager.evaluate_leave_request(request1, [existing_leave])
    print(manager.format_decision_report(decision1))
    
    # Test case 2: With overlap
    request2 = LeaveRequest(
        request_id="LR-007",
        employee_name="Daniel Schmidt",
        employee_id="EMP-006",
        department="Finance",
        position="Financial Analyst",
        leave_type="Sick Leave",
        start_date=datetime(2024, 12, 12),  # Overlaps with existing leave
        end_date=datetime(2024, 12, 17),
        reason="Medical"
    )
    
    decision2 = manager.evaluate_leave_request(request2, [existing_leave])
    print(manager.format_decision_report(decision2))


def test_team_capacity():
    """Test team capacity constraint"""
    print_section("TEST 4: Team Capacity Check (Max 2 members on leave)")
    
    manager = EnhancedLeaveManager()
    
    # Create 2 existing approved leaves in same department
    existing_leaves = [
        LeaveRequest(
            request_id="LR-008",
            employee_name="Ashley Rogers",
            employee_id="EMP-003",
            department="Finance",
            position="Accountant",
            leave_type="Earned Leave",
            start_date=datetime(2024, 12, 10),
            end_date=datetime(2024, 12, 15),
            reason="Vacation",
            status="approved"
        ),
        LeaveRequest(
            request_id="LR-009",
            employee_name="Kelly Alexander",
            employee_id="EMP-004",
            department="Finance",
            position="Accountant",
            leave_type="Earned Leave",
            start_date=datetime(2024, 12, 10),
            end_date=datetime(2024, 12, 15),
            reason="Vacation",
            status="approved"
        )
    ]
    
    # Test case: 3rd person trying to take leave (should be denied)
    request = LeaveRequest(
        request_id="LR-010",
        employee_name="Corey Chung",
        employee_id="EMP-005",
        department="Finance",
        position="Financial Analyst",
        leave_type="Earned Leave",
        start_date=datetime(2024, 12, 10),
        end_date=datetime(2024, 12, 15),
        reason="Vacation"
    )
    
    decision = manager.evaluate_leave_request(request, existing_leaves)
    print(manager.format_decision_report(decision))


def test_formal_output():
    """Test Requirement 4: Formal output with decision evidence"""
    print_section("TEST 5: Formal Decision Output with Evidence")
    
    manager = EnhancedLeaveManager()
    
    request = LeaveRequest(
        request_id="LR-011",
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
    
    # Show formatted report
    print(manager.format_decision_report(decision))
    
    # Show JSON evidence
    print("\nJSON EVIDENCE:")
    print(json.dumps(decision.decision_evidence, indent=2, default=str))
    
    print("\nAPPLIED POLICY RULES:")
    for rule_id in decision.applied_policy_rules:
        print(f"  {rule_id}: {manager.POLICY_RULES[rule_id]}")


def test_employee_summary():
    """Test employee leave summary"""
    print_section("TEST 6: Employee Leave Summary")
    
    manager = EnhancedLeaveManager()
    
    # Get summary for an employee
    summary = manager.get_employee_leave_summary("Michael Moore")
    
    print("EMPLOYEE LEAVE SUMMARY:")
    print(json.dumps(summary, indent=2))


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  ENHANCED LEAVE MANAGER - HACKATHON REQUIREMENTS TEST")
    print("  Demonstrating all 4 requirements with deterministic decisions")
    print("=" * 80)
    
    try:
        # Test all requirements
        test_leave_balance_check()
        test_leave_type_eligibility()
        test_date_overlap_detection()
        test_team_capacity()
        test_formal_output()
        test_employee_summary()
        
        print("\n" + "=" * 80)
        print("  ✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
