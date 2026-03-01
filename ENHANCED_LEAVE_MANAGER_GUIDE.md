# Enhanced Leave Manager - Hackathon Requirements

## Overview

The Enhanced Leave Manager meets all NETRIK hackathon requirements for leave policy evaluation with **deterministic decisions** and **formal evidence**.

## ✅ Hackathon Requirements Met

### 1. ✅ Check Available Leave Balance
- Loads employee leave data from `data/employee leave tracking data.xlsx`
- Validates requested days against remaining balance
- Provides detailed balance information in decision evidence

### 2. ✅ Validate Leave Type Eligibility
- Checks leave type against employee position/role
- Maintains eligibility matrix for all positions
- Denies requests for ineligible leave types

### 3. ✅ Detect Date-Overlap Conflicts
- Checks against existing approved leaves
- Checks against historical leave data
- Identifies conflicts with team members
- Prevents double-booking

### 4. ✅ Formal Decision Output
- **Decision Type**: APPROVED or DENIED
- **Applied Policy Rules**: List of all rules checked (RULE_001, RULE_002, etc.)
- **Decision Evidence**: Complete audit trail with:
  - All checks performed
  - Balance information
  - Eligibility details
  - Conflict details (if any)
  - Team capacity status

## Policy Rules

The system enforces these deterministic rules:

| Rule ID | Description |
|---------|-------------|
| RULE_001 | Employee must have sufficient leave balance |
| RULE_002 | Leave type must be eligible for employee position |
| RULE_003 | No date overlap with existing approved leaves |
| RULE_004 | Start date must be before end date |
| RULE_005 | Leave request must be for future dates |
| RULE_006 | Maximum consecutive days limit must not be exceeded |
| RULE_007 | Minimum notice period must be met |
| RULE_008 | No more than 2 team members on leave simultaneously |

## Leave Type Eligibility Matrix

| Position | Eligible Leave Types |
|----------|---------------------|
| Software Engineer | Earned Leave, Sick Leave, Casual Leave, Paternity Leave |
| HR Manager | Earned Leave, Sick Leave, Casual Leave, Maternity Leave, Paternity Leave |
| Accountant | Earned Leave, Sick Leave, Casual Leave, Maternity Leave |
| Financial Analyst | Earned Leave, Sick Leave, Casual Leave, Maternity Leave, Paternity Leave |
| Operations Manager | Earned Leave, Sick Leave, Casual Leave, Paternity Leave |
| SEO Analyst | Earned Leave, Sick Leave, Casual Leave |
| Marketing Manager | Earned Leave, Sick Leave, Casual Leave, Maternity Leave, Paternity Leave |
| Sales Executive | Earned Leave, Sick Leave, Casual Leave |

## Usage

### Basic Usage

```python
from enhanced_leave_manager import EnhancedLeaveManager, LeaveRequest
from datetime import datetime

# Initialize manager
manager = EnhancedLeaveManager()

# Create leave request
request = LeaveRequest(
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

# Evaluate request
decision = manager.evaluate_leave_request(request)

# Print formatted report
print(manager.format_decision_report(decision))
```

### Decision Output Structure

```python
LeaveDecision(
    request_id="LR-001",
    employee_name="Michael Moore",
    decision_type="APPROVED",  # or "DENIED"
    applied_policy_rules=["RULE_004", "RULE_001", "RULE_002", "RULE_003", "RULE_008"],
    decision_evidence={
        "request_id": "LR-001",
        "employee_name": "Michael Moore",
        "position": "Software Engineer",
        "department": "IT",
        "leave_type": "Earned Leave",
        "requested_days": 5,
        "checks_performed": [
            "Date Range Validation: PASSED",
            "Leave Balance Check: PASSED (Available: 12 days)",
            "Leave Type Eligibility: PASSED (Earned Leave allowed for Software Engineer)",
            "Date Overlap Check: PASSED (No conflicts detected)",
            "Team Capacity Check: PASSED"
        ],
        "available_balance": 12,
        "balance_check": {...},
        "eligibility_check": {...},
        "overlap_check": {...},
        "team_capacity_check": {...},
        "approval_summary": {
            "all_checks_passed": True,
            "total_checks": 5,
            "new_remaining_balance": 7
        }
    },
    remaining_balance=7
)
```

## Example Decision Reports

### Approved Request

```
======================================================================
LEAVE REQUEST DECISION REPORT
======================================================================
Request ID: LR-001
Employee: Michael Moore
Decision: APPROVED

APPLIED POLICY RULES:
  • RULE_004: Start date must be before end date
  • RULE_001: Employee must have sufficient leave balance
  • RULE_002: Leave type must be eligible for employee position
  • RULE_003: No date overlap with existing approved leaves
  • RULE_008: No more than 2 team members on leave simultaneously

DECISION EVIDENCE:
  Checks Performed:
    ✓ Date Range Validation: PASSED
    ✓ Leave Balance Check: PASSED (Available: 12 days)
    ✓ Leave Type Eligibility: PASSED (Earned Leave allowed for Software Engineer)
    ✓ Date Overlap Check: PASSED (No conflicts detected)
    ✓ Team Capacity Check: PASSED

  ✅ REQUEST APPROVED
  Remaining Leave Balance: 7 days
======================================================================
```

### Denied Request (Insufficient Balance)

```
======================================================================
LEAVE REQUEST DECISION REPORT
======================================================================
Request ID: LR-002
Employee: Michael Moore
Decision: DENIED

APPLIED POLICY RULES:
  • RULE_004: Start date must be before end date
  • RULE_001: Employee must have sufficient leave balance

DECISION EVIDENCE:
  Checks Performed:
    ✓ Date Range Validation: PASSED
    ✓ Leave Balance Check: FAILED (Requested: 20, Available: 12)

  ❌ REQUEST DENIED
  Reason: Insufficient balance: Requested 20 days, Available 12 days
======================================================================
```

### Denied Request (Ineligible Leave Type)

```
======================================================================
LEAVE REQUEST DECISION REPORT
======================================================================
Request ID: LR-004
Employee: Kevin Wall
Decision: DENIED

APPLIED POLICY RULES:
  • RULE_004: Start date must be before end date
  • RULE_001: Employee must have sufficient leave balance
  • RULE_002: Leave type must be eligible for employee position

DECISION EVIDENCE:
  Checks Performed:
    ✓ Date Range Validation: PASSED
    ✓ Leave Balance Check: PASSED (Available: 1 days)
    ✓ Leave Type Eligibility: FAILED (Maternity Leave not allowed for SEO Analyst)

  ❌ REQUEST DENIED
  Reason: Maternity Leave not eligible for SEO Analyst
======================================================================
```

### Denied Request (Date Overlap)

```
======================================================================
LEAVE REQUEST DECISION REPORT
======================================================================
Request ID: LR-007
Employee: Daniel Schmidt
Decision: DENIED

APPLIED POLICY RULES:
  • RULE_004: Start date must be before end date
  • RULE_001: Employee must have sufficient leave balance
  • RULE_002: Leave type must be eligible for employee position
  • RULE_003: No date overlap with existing approved leaves

DECISION EVIDENCE:
  Checks Performed:
    ✓ Date Range Validation: PASSED
    ✓ Leave Balance Check: PASSED (Available: 6 days)
    ✓ Leave Type Eligibility: PASSED (Sick Leave allowed for Financial Analyst)
    ✓ Date Overlap Check: FAILED (1 conflict(s) detected)

  ❌ REQUEST DENIED
  Reason: Found 1 date overlap(s)
  Conflicts Found: 1
    - {'existing_request_id': 'LR-005', 'existing_dates': '2024-12-10 to 2024-12-15', 'existing_leave_type': 'Earned Leave', 'overlap_type': 'Same employee'}
======================================================================
```

## Integration with HR Agent

To integrate with the existing HR Agent:

```python
from hr_agent import HRAgent
from enhanced_leave_manager import EnhancedLeaveManager, LeaveRequest

# Initialize HR Agent with enhanced leave manager
agent = HRAgent()
enhanced_leave_mgr = EnhancedLeaveManager()

# Process leave request
request = LeaveRequest(...)
decision = enhanced_leave_mgr.evaluate_leave_request(request)

# Use decision in HR workflow
if decision.decision_type == "APPROVED":
    # Proceed with approval workflow
    print(f"✅ Leave approved for {decision.employee_name}")
else:
    # Handle denial
    print(f"❌ Leave denied: {decision.decision_evidence}")
```

## Testing

Run the comprehensive test suite:

```bash
python test_enhanced_leave_manager.py
```

This will test all 4 hackathon requirements:
1. Leave balance checking
2. Leave type eligibility validation
3. Date overlap detection
4. Formal decision output with evidence

## Key Features

### ✅ Deterministic Decisions
- All decisions are based on clear, documented rules
- Same input always produces same output
- No randomness or ambiguity

### ✅ Complete Audit Trail
- Every decision includes full evidence
- All checks are logged
- Policy rules are explicitly stated

### ✅ Conflict Detection
- Checks against existing approved leaves
- Checks against historical data
- Identifies team capacity issues

### ✅ Position-Based Eligibility
- Different leave types for different roles
- Enforces organizational policies
- Prevents invalid requests

## Data Source

The system uses `data/employee leave tracking data.xlsx` which contains:
- Employee Name
- Department
- Position
- Leave Type
- Start Date / End Date
- Days Taken
- Total Leave Entitlement
- Leave Taken So Far
- Remaining Leaves

## API Reference

### EnhancedLeaveManager

**Methods:**
- `evaluate_leave_request(request, existing_requests)` - Main evaluation method
- `format_decision_report(decision)` - Format decision as readable report
- `get_employee_leave_summary(employee_name)` - Get employee's leave summary

### LeaveRequest

**Fields:**
- `request_id` - Unique request identifier
- `employee_name` - Employee name
- `employee_id` - Employee ID
- `department` - Department name
- `position` - Job position
- `leave_type` - Type of leave
- `start_date` - Leave start date
- `end_date` - Leave end date
- `reason` - Reason for leave
- `status` - Request status (pending/approved/denied)

### LeaveDecision

**Fields:**
- `request_id` - Request identifier
- `employee_name` - Employee name
- `decision_type` - "APPROVED" or "DENIED"
- `applied_policy_rules` - List of rule IDs checked
- `decision_evidence` - Complete evidence dictionary
- `remaining_balance` - Remaining leave balance (if approved)
- `conflict_details` - List of conflicts (if denied due to overlap)

## For Hackathon Judges

This implementation demonstrates:

1. **Requirement 1 - Balance Checking**: ✅
   - Loads from tracking dataset
   - Validates against remaining balance
   - Shows balance in evidence

2. **Requirement 2 - Eligibility Validation**: ✅
   - Position-based eligibility matrix
   - Enforces role-specific rules
   - Clear denial reasons

3. **Requirement 3 - Conflict Detection**: ✅
   - Checks existing approved leaves
   - Checks historical data
   - Identifies team member overlaps

4. **Requirement 4 - Formal Output**: ✅
   - Decision Type (APPROVED/DENIED)
   - Applied Policy Rules (RULE_001, etc.)
   - Complete decision evidence
   - Structured audit trail

**All requirements met with deterministic, explainable decisions!** 🎉
