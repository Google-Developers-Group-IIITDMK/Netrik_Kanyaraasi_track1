"""
Unit Tests for Automated Scheduler

Comprehensive test suite covering:
- Constraint validation
- Conflict detection
- Edge cases
- Performance scenarios
"""

import unittest
from datetime import datetime, timedelta
from automated_scheduler import (
    AutomatedScheduler, Candidate, Interviewer, TimeSlot,
    SchedulingConstraints, SchedulingStatus
)


class TestTimeSlot(unittest.TestCase):
    """Test TimeSlot functionality"""
    
    def test_time_slot_creation(self):
        """Test basic time slot creation"""
        start = datetime(2024, 12, 1, 9, 0)
        end = datetime(2024, 12, 1, 10, 0)
        slot = TimeSlot(start, end)
        
        self.assertEqual(slot.start_time, start)
        self.assertEqual(slot.end_time, end)
        self.assertEqual(slot.duration_minutes(), 60)
    
    def test_invalid_time_slot(self):
        """Test that invalid time slots raise error"""
        start = datetime(2024, 12, 1, 10, 0)
        end = datetime(2024, 12, 1, 9, 0)  # End before start
        
        with self.assertRaises(ValueError):
            TimeSlot(start, end)
    
    def test_overlap_detection(self):
        """Test overlap detection between slots"""
        slot1 = TimeSlot(
            datetime(2024, 12, 1, 9, 0),
            datetime(2024, 12, 1, 10, 0)
        )
        
        # Overlapping slot
        slot2 = TimeSlot(
            datetime(2024, 12, 1, 9, 30),
            datetime(2024, 12, 1, 10, 30)
        )
        self.assertTrue(slot1.overlaps_with(slot2))
        self.assertTrue(slot2.overlaps_with(slot1))
        
        # Non-overlapping slot
        slot3 = TimeSlot(
            datetime(2024, 12, 1, 10, 0),
            datetime(2024, 12, 1, 11, 0)
        )
        self.assertFalse(slot1.overlaps_with(slot3))
        self.assertFalse(slot3.overlaps_with(slot1))
        
        # Adjacent slots (no overlap)
        slot4 = TimeSlot(
            datetime(2024, 12, 1, 10, 0),
            datetime(2024, 12, 1, 11, 0)
        )
        self.assertFalse(slot1.overlaps_with(slot4))


class TestBasicScheduling(unittest.TestCase):
    """Test basic scheduling functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scheduler = AutomatedScheduler()
        
        # Create test candidate
        self.candidate = Candidate(
            candidate_id="C001",
            name="Alice Johnson",
            email="alice@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 9, 0),
                    datetime(2024, 12, 1, 17, 0)
                )
            ]
        )
        
        # Create test interviewer
        self.interviewer = Interviewer(
            interviewer_id="I001",
            name="Bob Smith",
            email="bob@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                ),
                TimeSlot(
                    datetime(2024, 12, 1, 14, 0),
                    datetime(2024, 12, 1, 15, 0)
                )
            ]
        )
    
    def test_add_candidate(self):
        """Test adding candidate to scheduler"""
        self.scheduler.add_candidate(self.candidate)
        self.assertIn("C001", self.scheduler.candidates)
        self.assertEqual(self.scheduler.stats["total_candidates"], 1)
    
    def test_add_interviewer(self):
        """Test adding interviewer to scheduler"""
        self.scheduler.add_interviewer(self.interviewer)
        self.assertIn("I001", self.scheduler.interviewers)
    
    def test_successful_scheduling(self):
        """Test successful candidate scheduling"""
        self.scheduler.add_candidate(self.candidate)
        self.scheduler.add_interviewer(self.interviewer)
        
        result = self.scheduler.schedule_candidate("C001")
        
        self.assertEqual(result.status, SchedulingStatus.CONFIRMED)
        self.assertEqual(result.interviewer_id, "I001")
        self.assertIsNotNone(result.assigned_slot)
        self.assertEqual(self.scheduler.stats["scheduled"], 1)
    
    def test_no_availability_match(self):
        """Test scheduling when no slots match availability"""
        # Candidate available only in morning
        candidate = Candidate(
            candidate_id="C002",
            name="Charlie Brown",
            email="charlie@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 8, 0),
                    datetime(2024, 12, 1, 9, 0)
                )
            ]
        )
        
        # Interviewer available only in afternoon
        interviewer = Interviewer(
            interviewer_id="I002",
            name="Diana Prince",
            email="diana@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 14, 0),
                    datetime(2024, 12, 1, 15, 0)
                )
            ]
        )
        
        self.scheduler.add_candidate(candidate)
        self.scheduler.add_interviewer(interviewer)
        
        result = self.scheduler.schedule_candidate("C002")
        
        self.assertEqual(result.status, SchedulingStatus.WAITLISTED)
        self.assertIsNone(result.assigned_slot)


class TestConstraintValidation(unittest.TestCase):
    """Test constraint enforcement"""
    
    def test_no_overlapping_assignments(self):
        """Test that overlapping assignments are prevented"""
        scheduler = AutomatedScheduler()
        
        # Two candidates with same availability
        candidate1 = Candidate(
            candidate_id="C001",
            name="Alice",
            email="alice@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                )
            ]
        )
        
        candidate2 = Candidate(
            candidate_id="C002",
            name="Bob",
            email="bob@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                )
            ]
        )
        
        # One interviewer with one slot
        interviewer = Interviewer(
            interviewer_id="I001",
            name="Charlie",
            email="charlie@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                )
            ]
        )
        
        scheduler.add_candidate(candidate1)
        scheduler.add_candidate(candidate2)
        scheduler.add_interviewer(interviewer)
        
        # Schedule first candidate
        result1 = scheduler.schedule_candidate("C001")
        self.assertEqual(result1.status, SchedulingStatus.CONFIRMED)
        
        # Try to schedule second candidate (should fail - slot taken)
        result2 = scheduler.schedule_candidate("C002")
        self.assertEqual(result2.status, SchedulingStatus.WAITLISTED)
    
    def test_max_interviews_per_day(self):
        """Test maximum interviews per day constraint"""
        constraints = SchedulingConstraints(
            max_interviews_per_interviewer_per_day=2
        )
        scheduler = AutomatedScheduler(constraints)
        
        # Create 3 candidates
        candidates = [
            Candidate(
                candidate_id=f"C{i:03d}",
                name=f"Candidate {i}",
                email=f"candidate{i}@example.com",
                availability_windows=[
                    TimeSlot(
                        datetime(2024, 12, 1, 9 + i, 0),
                        datetime(2024, 12, 1, 10 + i, 0)
                    )
                ]
            )
            for i in range(3)
        ]
        
        # One interviewer with 3 slots on same day
        interviewer = Interviewer(
            interviewer_id="I001",
            name="Interviewer",
            email="interviewer@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 9 + i, 0),
                    datetime(2024, 12, 1, 10 + i, 0)
                )
                for i in range(3)
            ],
            max_interviews_per_day=2
        )
        
        for candidate in candidates:
            scheduler.add_candidate(candidate)
        scheduler.add_interviewer(interviewer)
        
        # Schedule all candidates
        results = scheduler.schedule_all_candidates()
        
        # Only 2 should be scheduled (daily limit)
        scheduled = [r for r in results if r.status == SchedulingStatus.CONFIRMED]
        self.assertEqual(len(scheduled), 2)
    
    def test_slot_duration_consistency(self):
        """Test slot duration constraint"""
        constraints = SchedulingConstraints(
            slot_duration_minutes=60,
            allow_duration_variance_minutes=0  # Strict
        )
        scheduler = AutomatedScheduler(constraints)
        
        candidate = Candidate(
            candidate_id="C001",
            name="Alice",
            email="alice@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 9, 0),
                    datetime(2024, 12, 1, 17, 0)
                )
            ]
        )
        
        # Interviewer with wrong duration slot
        interviewer = Interviewer(
            interviewer_id="I001",
            name="Bob",
            email="bob@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 10, 45)  # 45 minutes (wrong)
                )
            ]
        )
        
        scheduler.add_candidate(candidate)
        scheduler.add_interviewer(interviewer)
        
        result = scheduler.schedule_candidate("C001")
        
        # Should be waitlisted due to duration mismatch
        self.assertEqual(result.status, SchedulingStatus.WAITLISTED)
    
    def test_minimum_gap_between_interviews(self):
        """Test minimum gap constraint"""
        constraints = SchedulingConstraints(
            min_gap_between_interviews_minutes=15
        )
        scheduler = AutomatedScheduler(constraints)
        
        # Two candidates
        candidate1 = Candidate(
            candidate_id="C001",
            name="Alice",
            email="alice@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                )
            ]
        )
        
        candidate2 = Candidate(
            candidate_id="C002",
            name="Bob",
            email="bob@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 11, 0),  # Immediately after first
                    datetime(2024, 12, 1, 12, 0)
                )
            ]
        )
        
        # Interviewer with back-to-back slots
        interviewer = Interviewer(
            interviewer_id="I001",
            name="Charlie",
            email="charlie@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                ),
                TimeSlot(
                    datetime(2024, 12, 1, 11, 0),  # No gap
                    datetime(2024, 12, 1, 12, 0)
                )
            ]
        )
        
        scheduler.add_candidate(candidate1)
        scheduler.add_candidate(candidate2)
        scheduler.add_interviewer(interviewer)
        
        # Schedule first candidate
        result1 = scheduler.schedule_candidate("C001")
        self.assertEqual(result1.status, SchedulingStatus.CONFIRMED)
        
        # Second should fail due to insufficient gap
        result2 = scheduler.schedule_candidate("C002")
        self.assertEqual(result2.status, SchedulingStatus.WAITLISTED)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_fully_booked_schedule(self):
        """Test handling of fully booked schedules"""
        scheduler = AutomatedScheduler()
        
        # 5 candidates
        candidates = [
            Candidate(
                candidate_id=f"C{i:03d}",
                name=f"Candidate {i}",
                email=f"c{i}@example.com",
                availability_windows=[
                    TimeSlot(
                        datetime(2024, 12, 1, 9, 0),
                        datetime(2024, 12, 1, 17, 0)
                    )
                ]
            )
            for i in range(5)
        ]
        
        # Interviewer with only 2 slots
        interviewer = Interviewer(
            interviewer_id="I001",
            name="Interviewer",
            email="interviewer@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                ),
                TimeSlot(
                    datetime(2024, 12, 1, 14, 0),
                    datetime(2024, 12, 1, 15, 0)
                )
            ]
        )
        
        for candidate in candidates:
            scheduler.add_candidate(candidate)
        scheduler.add_interviewer(interviewer)
        
        results = scheduler.schedule_all_candidates()
        
        # Only 2 should be scheduled
        scheduled = [r for r in results if r.status == SchedulingStatus.CONFIRMED]
        waitlisted = [r for r in results if r.status == SchedulingStatus.WAITLISTED]
        
        self.assertEqual(len(scheduled), 2)
        self.assertEqual(len(waitlisted), 3)
    
    def test_partial_overlap_handling(self):
        """Test handling of partial overlaps"""
        scheduler = AutomatedScheduler()
        
        # Candidate available 9-12
        candidate = Candidate(
            candidate_id="C001",
            name="Alice",
            email="alice@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 9, 0),
                    datetime(2024, 12, 1, 12, 0)
                )
            ]
        )
        
        # Interviewer available 11-14 (partial overlap)
        interviewer = Interviewer(
            interviewer_id="I001",
            name="Bob",
            email="bob@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 11, 0),
                    datetime(2024, 12, 1, 12, 0)
                )
            ]
        )
        
        scheduler.add_candidate(candidate)
        scheduler.add_interviewer(interviewer)
        
        result = scheduler.schedule_candidate("C001")
        
        # Should successfully schedule in overlap period
        self.assertEqual(result.status, SchedulingStatus.CONFIRMED)
        self.assertEqual(result.assigned_slot.start_time, datetime(2024, 12, 1, 11, 0))
    
    def test_rescheduling(self):
        """Test candidate rescheduling"""
        scheduler = AutomatedScheduler()
        
        candidate = Candidate(
            candidate_id="C001",
            name="Alice",
            email="alice@example.com",
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                )
            ]
        )
        
        interviewer = Interviewer(
            interviewer_id="I001",
            name="Bob",
            email="bob@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                ),
                TimeSlot(
                    datetime(2024, 12, 1, 14, 0),
                    datetime(2024, 12, 1, 15, 0)
                )
            ]
        )
        
        scheduler.add_candidate(candidate)
        scheduler.add_interviewer(interviewer)
        
        # Initial scheduling
        result1 = scheduler.schedule_candidate("C001")
        self.assertEqual(result1.status, SchedulingStatus.CONFIRMED)
        original_slot = result1.assigned_slot
        
        # Reschedule with new availability
        new_availability = [
            TimeSlot(
                datetime(2024, 12, 1, 14, 0),
                datetime(2024, 12, 1, 15, 0)
            )
        ]
        
        result2 = scheduler.reschedule_candidate("C001", new_availability)
        
        self.assertEqual(result2.status, SchedulingStatus.RESCHEDULED)
        self.assertNotEqual(result2.assigned_slot.start_time, original_slot.start_time)
        self.assertEqual(result2.previous_slot, original_slot)
    
    def test_priority_scheduling(self):
        """Test priority-based scheduling"""
        scheduler = AutomatedScheduler()
        
        # High priority candidate
        candidate1 = Candidate(
            candidate_id="C001",
            name="VIP Candidate",
            email="vip@example.com",
            priority=10,
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                )
            ]
        )
        
        # Low priority candidate
        candidate2 = Candidate(
            candidate_id="C002",
            name="Regular Candidate",
            email="regular@example.com",
            priority=1,
            availability_windows=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                )
            ]
        )
        
        # One slot available
        interviewer = Interviewer(
            interviewer_id="I001",
            name="Interviewer",
            email="interviewer@example.com",
            availability_slots=[
                TimeSlot(
                    datetime(2024, 12, 1, 10, 0),
                    datetime(2024, 12, 1, 11, 0)
                )
            ]
        )
        
        # Add in reverse priority order
        scheduler.add_candidate(candidate2)
        scheduler.add_candidate(candidate1)
        scheduler.add_interviewer(interviewer)
        
        results = scheduler.schedule_all_candidates()
        
        # High priority should get the slot
        self.assertEqual(results[0].candidate_id, "C001")
        self.assertEqual(results[0].status, SchedulingStatus.CONFIRMED)
        self.assertEqual(results[1].status, SchedulingStatus.WAITLISTED)


class TestPerformance(unittest.TestCase):
    """Test performance and scalability"""
    
    def test_large_scale_scheduling(self):
        """Test scheduling with many candidates and interviewers"""
        import time
        
        scheduler = AutomatedScheduler()
        
        # Create 100 candidates
        for i in range(100):
            candidate = Candidate(
                candidate_id=f"C{i:03d}",
                name=f"Candidate {i}",
                email=f"c{i}@example.com",
                availability_windows=[
                    TimeSlot(
                        datetime(2024, 12, 1, 9, 0),
                        datetime(2024, 12, 1, 17, 0)
                    )
                ]
            )
            scheduler.add_candidate(candidate)
        
        # Create 10 interviewers with 10 slots each
        for i in range(10):
            slots = [
                TimeSlot(
                    datetime(2024, 12, 1, 9 + j, 0),
                    datetime(2024, 12, 1, 10 + j, 0)
                )
                for j in range(8)  # 8 hours
            ]
            
            interviewer = Interviewer(
                interviewer_id=f"I{i:03d}",
                name=f"Interviewer {i}",
                email=f"i{i}@example.com",
                availability_slots=slots
            )
            scheduler.add_interviewer(interviewer)
        
        # Measure scheduling time
        start_time = time.time()
        results = scheduler.schedule_all_candidates()
        end_time = time.time()
        
        elapsed = end_time - start_time
        
        # Should complete in reasonable time (< 5 seconds)
        self.assertLess(elapsed, 5.0)
        
        # Should schedule most candidates (80 slots available)
        scheduled = [r for r in results if r.status == SchedulingStatus.CONFIRMED]
        self.assertEqual(len(scheduled), 80)
        
        print(f"\nScheduled {len(scheduled)}/100 candidates in {elapsed:.3f} seconds")


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
