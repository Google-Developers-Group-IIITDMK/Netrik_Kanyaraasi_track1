# 🤖 AI HR Agent - NETRIK Hackathon 2026

## Overview

A comprehensive AI-powered HR automation system that handles end-to-end recruitment workflows including resume screening, interview scheduling, question generation, pipeline management, leave administration, and query escalation.

## ✨ Features

### Core Functionality

- **Resume Screening & Ranking**
  - Intelligent skill matching with weighted scoring
  - Required skill overlap (60%)
  - Preferred skill bonus (10%)
  - Experience normalization (20%)
  - Resume quality assessment (10%)
  - Explainable scoring with skill gap analysis

- **Interview Question Generation**
  - Role-specific technical questions
  - Behavioral questions (STAR format)
  - Situational assessments
  - LLM-powered generation (AWS Bedrock) with template fallback
  - 5-10 questions per candidate focusing on skill gaps

- **Conflict-Free Interview Scheduling**
  - Automated slot assignment
  - Interviewer availability tracking
  - Conflict detection and prevention
  - Prioritizes top-ranked candidates
  - Human-readable schedule formatting

- **Pipeline State Management**
  - Enforces valid state transitions
  - Prevents invalid workflow jumps
  - Complete transition history logging
  - States: applied → screened → interview_scheduled → interviewed → offer_extended → offer_accepted → hired/rejected

- **Leave Management**
  - Policy-compliant request evaluation
  - Balance checking across leave types (annual, sick, personal, unpaid)
  - Consecutive days limit enforcement
  - Notice period validation
  - Overlap detection

- **Query Escalation**
  - Keyword-based sensitive topic detection
  - Salary threshold escalation
  - Executive position flagging
  - Low-score override alerts
  - Extended leave approval routing
  - Severity classification (high/medium/low)

## 🏗️ Architecture

```
HRAgent (Orchestrator)
├── SmartResumeScreener (Resume ranking)
├── PipelineStateValidator (State transitions)
├── InterviewQuestionGenerator (Question generation)
├── InterviewScheduler (Slot assignment)
├── LeaveManager (Policy compliance)
└── QueryEscalator (Escalation logic)
```

### Design Principles

- **Separation of Concerns**: Each component handles a specific domain
- **Modular Architecture**: Components are independently testable
- **Graceful Degradation**: LLM fallback to templates
- **Explainability**: All decisions include reasoning
- **Production-Ready**: Error handling, logging, validation

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

### Basic Usage

```python
from hr_agent import HRAgent, InterviewSlot
from data_loader import load_candidates, create_job_from_dataset
from datetime import datetime, timedelta

# Initialize agent
agent = HRAgent()

# Load candidates and job description
candidates = load_candidates("data/resume_dataset_1200.csv")
jd = create_job_from_dataset("data/resume_dataset_1200.csv")

# Screen and rank candidates
ranked = agent.screen_resumes(candidates, jd)

# Create interview slots
slots = [
    InterviewSlot(
        slot_id="SLOT-001",
        interviewer_id="INT-001",
        start_time=datetime.now() + timedelta(days=7),
        end_time=datetime.now() + timedelta(days=7, hours=1),
        is_available=True
    )
]

# Shortlist top 5 with questions and scheduling
shortlisted = agent.shortlist_top_n(5, slots, jd)

# Export comprehensive results
results = agent.export_results()
```

## 📊 Evaluation Metrics

### Hackathon Scoring (100 points)

| Criteria | Points | Implementation |
|----------|--------|----------------|
| Resume-Job Matching Accuracy | 25 | MRR calculation, explainable scoring |
| Scheduling Validity | 20 | Zero conflicts, availability tracking |
| Pipeline State Correctness | 15 | Valid transitions, complete logging |
| Leave Policy Compliance | 15 | Balance checks, policy enforcement |
| Architecture & Modularity | 10 | Clean separation, OOP principles |
| Output Format Robustness | 10 | Complete JSON export, ISO 8601 dates |
| Documentation Quality | 5 | Comprehensive README, inline docs |

## 📁 Project Structure

```
.
├── hr_agent.py           # Core agent logic and components
├── data_loader.py        # Dataset integration
├── app.py                # Streamlit UI
├── main.py               # CLI interface
├── requirements.txt      # Dependencies
├── README.md             # This file
└── data/
    ├── resume_dataset_1200.csv
    └── employee leave tracking data.xlsx
```

## 🔧 Configuration

### Team Configuration

Update `hr_agent.py`:

```python
CONFIG = {
    "team_id": "YOUR_TEAM_NAME",
    "track": "track_1_hr_agent"
}
```

### LLM Integration (Optional)

```python
import boto3

bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
agent = HRAgent(use_llm=True, bedrock_client=bedrock_client)
```

### Leave Policies

```python
from hr_agent import LeavePolicy

policies = {
    'annual': LeavePolicy('annual', annual_quota=20, max_consecutive_days=15, min_notice_days=7),
    'sick': LeavePolicy('sick', annual_quota=10, max_consecutive_days=5, min_notice_days=0),
}

agent = HRAgent(leave_policies=policies)
```

## 📤 Export Format

```json
{
  "team_id": "YOUR_TEAM_NAME",
  "track": "track_1_hr_agent",
  "metadata": {
    "timestamp": "2024-01-15T10:30:00",
    "version": "1.0.0"
  },
  "results": {
    "pipeline": {
      "candidate_id": {
        "name": "John Doe",
        "status": "interview_scheduled",
        "score": 0.85,
        "explanation": {...},
        "interview_questions": [...],
        "slot_id": "SLOT-001",
        "interviewer_id": "INT-001"
      }
    },
    "interview_schedule": {
      "assignments": [...],
      "unscheduled": [],
      "conflicts": 0
    },
    "leave_decisions": [...],
    "escalation_decisions": [...],
    "transition_log": [...]
  }
}
```

## 🎯 Key Differentiators

1. **Complete Implementation**: All 6 core requirements fully implemented
2. **Explainable AI**: Every decision includes reasoning and evidence
3. **Production-Ready**: Error handling, logging, validation throughout
4. **Modular Design**: Clean architecture with independent components
5. **Comprehensive Export**: All functionality results in single JSON output
6. **Interactive UI**: Full-featured Streamlit dashboard

## 🧪 Testing

Run diagnostics:

```bash
python -m pytest tests/
```

## 📝 License

MIT License - NETRIK Hackathon 2026

## 👥 Team

Team ID: YOUR_TEAM_NAME
Track: Track 1 - HR Agent

## 🙏 Acknowledgments

- Kaggle for resume and leave tracking datasets
- NETRIK Hackathon organizers
- AWS Bedrock for LLM capabilities
