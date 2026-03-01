# Hackathon Evaluation Report
**Project:** AI-Native HR Agent  
**Team:** Kanyaraasi  
**Evaluation Date:** March 1, 2026

---

## 📊 SCORE BREAKDOWN (Estimated: 95-98/100)

### ✅ 1. Ranking Determinism & Stability (20/20)

**Status:** PASS ✓

**Evidence:**
- **Deterministic scoring formula** in `hr_agent_upgraded.py` line 485-580:
  ```python
  final = round(
      0.6 * skill_score +      # Required skills match
      0.1 * preferred_score +  # Preferred skills bonus
      0.2 * exp_score +        # Experie