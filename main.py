from hr_agent import HRAgent
from data_loader import load_candidates, create_job_from_dataset

def main():
    agent = HRAgent()

    # Path to resume dataset
    resume_path = "data/resume_dataset_1200.csv"

    # Load candidates
    candidates = load_candidates(resume_path)

    # Create job description from dataset
    jd = create_job_from_dataset(resume_path)

    # Screen and rank candidates
    ranked = agent.screen_resumes(candidates, jd)

    # Print top 5 ranked candidates
    print("\nTop 5 Ranked Candidates:\n")
    for c in ranked[:5]:
        print(f"Name: {c.name}, Score: {c.match_score}, Status: {c.status}")

    shortlisted = agent.shortlist_top_n(5)

    print("\nShortlisted Candidates:\n")
    for c in shortlisted:
        print(f"{c.name} - {c.match_score}")
    
    # Print full JSON export
    print("\nFinal Export JSON:\n")
    print(agent.export_results())


if __name__ == "__main__":
    main()