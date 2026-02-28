from hr_agent import HRAgent
from data_loader import load_candidates, create_job_from_dataset
import pandas as pd

agent = HRAgent()

resume_path = "data/resume_dataset_1200.csv"
df = pd.read_csv(resume_path)

candidates = load_candidates(resume_path)
jd = create_job_from_dataset(df)

ranked = agent.screen_resumes(candidates, jd)

print(agent.export_results())