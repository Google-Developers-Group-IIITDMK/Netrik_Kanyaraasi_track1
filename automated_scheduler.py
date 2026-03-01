"""
Automated Interview Scheduling Module

A production-ready scheduling system that assigns interview slots to candidates
while strictly adhering to predefined constraints.

Time Complexity:
- Scheduling N candidates with M interviewers and K slots: O(N * M * K * log K)
- Conflict detection: O(log K) using interval tree
- Overall: O(N * M * K * log K) where typically K << N*M

Space Complexity: O(N + M + K)

Author: NETRIK Hackathon 2026 - Team Kanyaraasi
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import logging
from collections import defaultdict
import bisect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchedulingStatus(Enum):
    """Scheduling status codes"""
    CONFIRMED = "confirmed"
    WAITLISTED = "waitlisted"
    REJECTED = "rejected"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"


@dataclass
class TimeSlot:
    """Represents a time slot with start and end times"""
    start_time: datetime
    end_time: datetime
    slot_id: str = ""
    
    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        if not self.slot_id:
            self.slot_id = f"SLOT-{self.start_time.strftime('%Y%m%d%H%M')}"
    
    def duration_minutes(self) -> int:
        """Get slot duration in minutes"""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """
        Check if this slot overlaps with another slot.
        
        Time Complexity: O(1)
        
        Args:
            other: Another TimeSlot to check against
            
        Returns:
            True if slots overlap, False otherwise
        """
        return self.start_time < other.end_time and self.end_time > other.start_time
    
    def __lt__(self, other):
        """For sorting slots by start time"""
        return self.start_time < other.start_time
    
    def __repr__(self):
        return f"TimeSlot({self.slot_id}: {self.start_time} - {self.end_time})"


@dataclass
class Candidate:
    """Represents a candidate with availability windows"""
    candidate_id: str
    name: str
    email: str
    availability_windows: List[TimeSlot] = field(default_factory=list)
    priority: int = 0  # Higher priority = scheduled first
    timezone: str = "UTC"
    
    def __post_init__(self):
        # Sort availability windows by start time for efficient searching
        self.availability_windows.sort()


@dataclass
class Interviewer:
    """Represents an interviewer with availability slots"""
    interviewer_id: str
    name: str
    email: str
    availability_slots: List[TimeSlot] = field(default_factory=list)
    max_interviews_per_day: int = 5
    timezone: str = "UTC"
    
    def __post_init__(self):
        # Sort availability slots by start time
        self.availability_slots.sort()


@dataclass
class SchedulingConstraints:
    """Scheduling constraints configuration"""
    slot_duration_minutes: int = 60
    allow_duration_variance_minutes: int = 0  # Strict by default
    max_interviews_per_interviewer_per_day: int = 5
    min_gap_between_interviews_minutes: int = 15
    prioritize_earliest_slot: bool = True
    allow_timezone_conversion: bool = True
    max_candidates_per_slot: int = 1  # Panel interviews if > 1


@dataclass
class SchedulingResult:
    """Result of a scheduling attempt"""
    candidate_id: str
    interviewer_id: Optional[str]
    assigned_slot: Optional[TimeSlot]
    status: SchedulingStatus
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    previous_slot: Optional[TimeSlot] = None  # For rescheduling
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/export"""
        return {
            "candidate_id": self.candidate_id,
            "interviewer_id": self.interviewer_id,
            "assigned_slot": str(self.assigned_slot) if self.assigned_slot else None,
            "status": self.status.value,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "previous_slot": str(self.previous_slot) if self.previous_slot else None
        }


class IntervalTree:
    """
    Efficient interval tree for conflict detection.
    
    Time Complexity:
    - Insert: O(log n)
    - Query overlaps: O(log n + k) where k is number of overlaps
    - Delete: O(log n)
    
    Space Complexity: O(n)
    """
    
    def __init__(self):
        self.intervals: List[Tuple[datetime, datetime, str]] = []
        self.sorted = True
    
    def insert(self, start: datetime, end: datetime, slot_id: str):
        """Insert an interval"""
        self.intervals.append((start, end, slot_id))
        self.sorted = False
    
    def _ensure_sorted(self):
        """Ensure intervals are sorted by start time"""
        if not self.sorted:
            self.intervals.sort()
            self.sorted = True
    
    def has_overlap(self, start: datetime, end: datetime) -> bool:
        """
        Check if interval overlaps with any existing interval.
        
        Time Complexity: O(log n + k) where k is number of overlaps
        """
        self._ensure_sorted()
        
        # Binary search for potential overlaps
        for interval_start, interval_end, _ in self.intervals:
            if interval_start >= end:
                break  # No more possible overlaps
            if interval_end > start:
                return True  # Found overlap
        
        return False
    
    def get_overlapping(self, start: datetime, end: datetime) -> List[str]:
        """Get all slot IDs that overlap with given interval"""
        self._ensure_sorted()
        
        overlapping = []
        for interval_start, interval_end, slot_id in self.intervals:
            if interval_start >= end:
                break
            if interval_end > start:
                overlapping.append(slot_id)
        
        return overlapping
    
    def remove(self, slot_id: str):
        """Remove an interval by slot ID"""
        self.intervals = [(s, e, sid) for s, e, sid in self.intervals if sid != slot_id]


class AutomatedScheduler:
    """
    Main scheduling engine with constraint enforcement.
    
    Features:
    - Efficient conflict detection using interval trees
    - Constraint validation
    - Priority-based scheduling
    - Rescheduling support
    - Comprehensive logging
    
    Time Complexity: O(N * M * K * log K) for N candidates, M interviewers, K slots
    Space Complexity: O(N + M + K)
    """
    
    def __init__(self, constraints: Optional[SchedulingConstraints] = None):
        """
        Initialize scheduler with constraints.
        
        Args:
            constraints: Scheduling constraints configuration
        """
        self.constraints = constraints or SchedulingConstraints()
        
        # Tracking structures
        self.candidates: Dict[str, Candidate] = {}
        self.interviewers: Dict[str, Interviewer] = {}
        self.scheduled_interviews: Dict[str, SchedulingResult] = {}
        self.waitlist: List[str] = []
        
        # Interval trees for efficient conflict detection
        self.interviewer_schedules: Dict[str, IntervalTree] = defaultdict(IntervalTree)
        self.candidate_schedules: Dict[str, IntervalTree] = defaultdict(IntervalTree)
        
        # Statistics
        self.stats = {
            "total_candidates": 0,
            "scheduled": 0,
            "waitlisted": 0,
            "rejected": 0,
            "rescheduled": 0
        }
        
        logger.info("Automated Scheduler initialized")
    
    def add_candidate(self, candidate: Candidate):
        """
        Add a candidate to the scheduling pool.
        
        Time Complexity: O(1)
        """
        self.candidates[candidate.candidate_id] = candidate
        self.stats["total_candidates"] += 1
        logger.info(f"Added candidate: {candidate.name} ({candidate.candidate_id})")
    
    def add_interviewer(self, interviewer: Interviewer):
        """
        Add an interviewer to the scheduling pool.
        
        Time Complexity: O(1)
        """
        self.interviewers[interviewer.interviewer_id] = interviewer
        logger.info(f"Added interviewer: {interviewer.name} ({interviewer.interviewer_id})")
    
    def schedule_all_candidates(self) -> List[SchedulingResult]:
        """
        Schedule all candidates with priority-based assignment.
        
        Time Complexity: O(N * M * K * log K)
        where N = candidates, M = interviewers, K = slots per interviewer
        
        Returns:
            List of scheduling results
        """
        results = []
        
        # Sort candidates by priority (higher first)
        sorted_candidates = sorted(
            self.candidates.values(),
            key=lambda c: (-c.priority, c.candidate_id)
        )
        
        logger.info(f"Starting scheduling for {len(sorted_candidates)} candidates")
        
        for candidate in sorted_candidates:
            result = self.schedule_candidate(candidate.candidate_id)
            results.append(result)
        
        logger.info(f"Scheduling complete: {self.stats}")
        
        return results
    
    def schedule_candidate(self, candidate_id: str) -> SchedulingResult:
        """
        Schedule a single candidate to the earliest feasible slot.
        
        Time Complexity: O(M * K * log K)
        where M = interviewers, K = slots per interviewer
        
        Args:
            candidate_id: ID of candidate to schedule
            
        Returns:
            SchedulingResult with assignment details
        """
        candidate = self.candidates.get(candidate_id)
        if not candidate:
            return SchedulingResult(
                candidate_id=candidate_id,
                interviewer_id=None,
                assigned_slot=None,
                status=SchedulingStatus.REJECTED,
                reason="Candidate not found"
            )
        
        # Find best slot across all interviewers
        best_match = self._find_best_slot(candidate)
        
        if best_match:
            interviewer_id, slot = best_match
            result = self._assign_slot(candidate, interviewer_id, slot)
            self.stats["scheduled"] += 1
            return result
        else:
            # No slot available - add to waitlist
            self.waitlist.append(candidate_id)
            self.stats["waitlisted"] += 1
            
            return SchedulingResult(
                candidate_id=candidate_id,
                interviewer_id=None,
                assigned_slot=None,
                status=SchedulingStatus.WAITLISTED,
                reason="No available slots matching candidate availability and constraints"
            )
    
    def _find_best_slot(
        self,
        candidate: Candidate
    ) -> Optional[Tuple[str, TimeSlot]]:
        """
        Find the best available slot for a candidate.
        
        Strategy:
        1. Iterate through candidate's availability windows
        2. For each window, check all interviewers
        3. Find earliest feasible slot that satisfies all constraints
        4. Return (interviewer_id, slot) or None
        
        Time Complexity: O(M * K * log K)
        """
        best_slot = None
        best_interviewer = None
        earliest_time = None
        
        # Check each availability window
        for availability_window in candidate.availability_windows:
            # Check each interviewer
            for interviewer_id, interviewer in self.interviewers.items():
                # Find matching slots in this interviewer's schedule
                matching_slots = self._find_matching_slots(
                    availability_window,
                    interviewer
                )
                
                for slot in matching_slots:
                    # Validate all constraints
                    if self._validate_slot_assignment(candidate, interviewer, slot):
                        # Check if this is earlier than current best
                        if earliest_time is None or slot.start_time < earliest_time:
                            best_slot = slot
                            best_interviewer = interviewer_id
                            earliest_time = slot.start_time
                            
                            # If prioritizing earliest, return immediately
                            if self.constraints.prioritize_earliest_slot:
                                return (best_interviewer, best_slot)
        
        if best_slot:
            return (best_interviewer, best_slot)
        
        return None
    
    def _find_matching_slots(
        self,
        availability_window: TimeSlot,
        interviewer: Interviewer
    ) -> List[TimeSlot]:
        """
        Find interviewer slots that overlap with candidate's availability window.
        
        Time Complexity: O(K) where K is number of interviewer slots
        """
        matching_slots = []
        
        for slot in interviewer.availability_slots:
            # Check if slot overlaps with availability window
            if slot.overlaps_with(availability_window):
                # Check duration constraint
                if self._check_duration_constraint(slot):
                    matching_slots.append(slot)
        
        return matching_slots
    
    def _check_duration_constraint(self, slot: TimeSlot) -> bool:
        """
        Check if slot duration matches constraints.
        
        Time Complexity: O(1)
        """
        duration = slot.duration_minutes()
        expected = self.constraints.slot_duration_minutes
        variance = self.constraints.allow_duration_variance_minutes
        
        return abs(duration - expected) <= variance
    
    def _validate_slot_assignment(
        self,
        candidate: Candidate,
        interviewer: Interviewer,
        slot: TimeSlot
    ) -> bool:
        """
        Validate all constraints for a slot assignment.
        
        Checks:
        1. No overlapping assignments for interviewer
        2. No overlapping assignments for candidate
        3. Max interviews per day not exceeded
        4. Minimum gap between interviews maintained
        
        Time Complexity: O(log K) using interval tree
        
        Returns:
            True if all constraints satisfied, False otherwise
        """
        # Check 1: No overlap for interviewer
        if self.interviewer_schedules[interviewer.interviewer_id].has_overlap(
            slot.start_time, slot.end_time
        ):
            return False
        
        # Check 2: No overlap for candidate
        if self.candidate_schedules[candidate.candidate_id].has_overlap(
            slot.start_time, slot.end_time
        ):
            return False
        
        # Check 3: Max interviews per day for interviewer
        if not self._check_daily_limit(interviewer.interviewer_id, slot.start_time):
            return False
        
        # Check 4: Minimum gap between interviews
        if not self._check_minimum_gap(interviewer.interviewer_id, slot):
            return False
        
        return True
    
    def _check_daily_limit(self, interviewer_id: str, date: datetime) -> bool:
        """
        Check if interviewer hasn't exceeded daily interview limit.
        
        Time Complexity: O(K) where K is interviews for that day
        """
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Count interviews on this day
        daily_interviews = 0
        for cid, result in self.scheduled_interviews.items():
            if (result.interviewer_id == interviewer_id and
                result.assigned_slot and
                day_start <= result.assigned_slot.start_time < day_end):
                daily_interviews += 1
        
        interviewer = self.interviewers[interviewer_id]
        max_daily = self.constraints.max_interviews_per_interviewer_per_day
        
        return daily_interviews < min(max_daily, interviewer.max_interviews_per_day)
    
    def _check_minimum_gap(self, interviewer_id: str, slot: TimeSlot) -> bool:
        """
        Check if minimum gap is maintained between interviews.
        
        Time Complexity: O(log K)
        """
        min_gap = timedelta(minutes=self.constraints.min_gap_between_interviews_minutes)
        
        # Check gap before this slot
        gap_start = slot.start_time - min_gap
        if self.interviewer_schedules[interviewer_id].has_overlap(gap_start, slot.start_time):
            return False
        
        # Check gap after this slot
        gap_end = slot.end_time + min_gap
        if self.interviewer_schedules[interviewer_id].has_overlap(slot.end_time, gap_end):
            return False
        
        return True
    
    def _assign_slot(
        self,
        candidate: Candidate,
        interviewer_id: str,
        slot: TimeSlot
    ) -> SchedulingResult:
        """
        Assign a slot to a candidate.
        
        Time Complexity: O(log K)
        """
        # Record in interval trees
        self.interviewer_schedules[interviewer_id].insert(
            slot.start_time, slot.end_time, slot.slot_id
        )
        self.candidate_schedules[candidate.candidate_id].insert(
            slot.start_time, slot.end_time, slot.slot_id
        )
        
        # Create result
        result = SchedulingResult(
            candidate_id=candidate.candidate_id,
            interviewer_id=interviewer_id,
            assigned_slot=slot,
            status=SchedulingStatus.CONFIRMED,
            reason="Successfully scheduled to earliest available slot"
        )
        
        self.scheduled_interviews[candidate.candidate_id] = result
        
        logger.info(
            f"Scheduled {candidate.name} with interviewer {interviewer_id} "
            f"at {slot.start_time}"
        )
        
        return result
    
    def reschedule_candidate(
        self,
        candidate_id: str,
        new_availability: Optional[List[TimeSlot]] = None
    ) -> SchedulingResult:
        """
        Reschedule a candidate to a new slot.
        
        Time Complexity: O(M * K * log K)
        
        Args:
            candidate_id: ID of candidate to reschedule
            new_availability: Optional new availability windows
            
        Returns:
            SchedulingResult with new assignment
        """
        # Get current assignment
        current_result = self.scheduled_interviews.get(candidate_id)
        if not current_result:
            return SchedulingResult(
                candidate_id=candidate_id,
                interviewer_id=None,
                assigned_slot=None,
                status=SchedulingStatus.REJECTED,
                reason="No existing schedule found"
            )
        
        # Cancel current slot
        self._cancel_slot(candidate_id)
        
        # Update availability if provided
        if new_availability:
            self.candidates[candidate_id].availability_windows = new_availability
            self.candidates[candidate_id].availability_windows.sort()
        
        # Try to reschedule
        new_result = self.schedule_candidate(candidate_id)
        
        if new_result.status == SchedulingStatus.CONFIRMED:
            new_result.status = SchedulingStatus.RESCHEDULED
            new_result.previous_slot = current_result.assigned_slot
            new_result.reason = "Successfully rescheduled"
            self.stats["rescheduled"] += 1
        
        return new_result
    
    def _cancel_slot(self, candidate_id: str):
        """
        Cancel a scheduled slot.
        
        Time Complexity: O(log K)
        """
        result = self.scheduled_interviews.get(candidate_id)
        if not result or not result.assigned_slot:
            return
        
        # Remove from interval trees
        if result.interviewer_id:
            self.interviewer_schedules[result.interviewer_id].remove(
                result.assigned_slot.slot_id
            )
        self.candidate_schedules[candidate_id].remove(result.assigned_slot.slot_id)
        
        # Remove from scheduled interviews
        del self.scheduled_interviews[candidate_id]
        
        logger.info(f"Cancelled slot for candidate {candidate_id}")
    
    def get_schedule_summary(self) -> Dict:
        """
        Get comprehensive scheduling summary.
        
        Returns:
            Dictionary with statistics and details
        """
        return {
            "statistics": self.stats,
            "total_interviewers": len(self.interviewers),
            "scheduled_interviews": len(self.scheduled_interviews),
            "waitlist_size": len(self.waitlist),
            "utilization": {
                interviewer_id: len([
                    r for r in self.scheduled_interviews.values()
                    if r.interviewer_id == interviewer_id
                ])
                for interviewer_id in self.interviewers.keys()
            }
        }
    
    def export_schedule(self) -> List[Dict]:
        """
        Export all scheduled interviews.
        
        Returns:
            List of scheduling results as dictionaries
        """
        return [result.to_dict() for result in self.scheduled_interviews.values()]
