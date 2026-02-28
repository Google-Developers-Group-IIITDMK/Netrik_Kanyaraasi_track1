import pandas as pd
from hr_agent import Candidate, JobDescription


# -----------------------------------------------------
# LOAD CANDIDATES FROM RESUME DATASET
# -----------------------------------------------------
def load_candidates(path: str):
    df = pd.read_csv(path)
    candidates = []

    for idx, row in df.iterrows():
        skills_raw = str(row.get("Skills", ""))
        skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]

        candidate = Candidate(
            candidate_id=str(idx),
            name=row.get("Name", f"Candidate_{idx}"),
            email=f"user{idx}@example.com",
            resume_text=f"{row.get('Current_Job_Title','')} {skills_raw}",
            skills=skills_list,
            experience_years=float(row.get("Experience_Years", 0)),
            status="applied"
        )

        candidates.append(candidate)

    return candidates


# -----------------------------------------------------
# CREATE JOB DESCRIPTION FROM DATASET
# -----------------------------------------------------
def create_job_from_dataset(path: str):
    df = pd.read_csv(path)

    # Use first Target_Job_Description as base
    description = df["Target_Job_Description"].iloc[0]

    # Collect most common skills across dataset
    all_skills = []
    for skills in df["Skills"].dropna():
        all_skills.extend([s.strip() for s in str(skills).split(",") if s.strip()])

    # Take top 10 unique skills
    required_skills = list(set(all_skills))[:10]

    jd = JobDescription(
        job_id="JD_001",
        title="Target Role",
        description=description,
        required_skills=required_skills,
        preferred_skills=[],
        min_experience=3
    )

    return jd


# -----------------------------------------------------
# LOAD LEAVE DATA
# -----------------------------------------------------
def load_leave_data(path: str):
    df = pd.read_excel(path)
    return df