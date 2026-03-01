"""
Test to verify that top candidates are now consistent across runs
"""

from data_loader import create_job_from_dataset, load_candidates
from hr_agent import HRAgent

def test_deterministic_ranking():
    """Run ranking 3 times and verify top candidates are identical"""
    
    # Load data
    candidates = load_candidates("data/resume_dataset_1200.csv")
    jd = create_job_from_dataset("data/resume_dataset_1200.csv")
    
    print(f"Job Description Required Skills: {jd.required_skills}")
    print(f"Total candidates: {len(candidates)}")
    
    # Run ranking 3 times
    top_candidates_runs = []
    
    for run in range(3):
        # Create fresh agent and candidates for each run
        agent = HRAgent(use_llm=False)
        candidates_copy = load_candidates("data/resume_dataset_1200.csv")
        
        # Screen resumes
        ranked = agent.screen_resumes(candidates_copy, jd)
        
        # Get top 5 candidates
        top_5 = [(c.candidate_id, c.name, c.match_score) for c in ranked[:5]]
        top_candidates_runs.append(top_5)
        
        print(f"\nRun {run + 1} - Top 5 Candidates:")
        for rank, (cid, name, score) in enumerate(top_5, 1):
            print(f"  {rank}. {name} (ID: {cid}, Score: {score:.4f})")
    
    # Verify all runs produced identical results
    print("\n" + "="*60)
    print("VERIFICATION:")
    print("="*60)
    
    all_identical = all(
        top_candidates_runs[0] == top_candidates_runs[i] 
        for i in range(1, len(top_candidates_runs))
    )
    
    if all_identical:
        print("✅ SUCCESS: Top candidates are IDENTICAL across all runs!")
        print("   The ranking is now deterministic.")
    else:
        print("❌ FAILURE: Top candidates are DIFFERENT across runs!")
        print("   The ranking is still non-deterministic.")
        
        # Show differences
        for i in range(1, len(top_candidates_runs)):
            if top_candidates_runs[0] != top_candidates_runs[i]:
                print(f"\n   Difference between Run 1 and Run {i+1}:")
                for rank in range(5):
                    if top_candidates_runs[0][rank] != top_candidates_runs[i][rank]:
                        print(f"     Position {rank+1}:")
                        print(f"       Run 1: {top_candidates_runs[0][rank][1]} (Score: {top_candidates_runs[0][rank][2]:.4f})")
                        print(f"       Run {i+1}: {top_candidates_runs[i][rank][1]} (Score: {top_candidates_runs[i][rank][2]:.4f})")
    
    return all_identical

if __name__ == "__main__":
    test_deterministic_ranking()
