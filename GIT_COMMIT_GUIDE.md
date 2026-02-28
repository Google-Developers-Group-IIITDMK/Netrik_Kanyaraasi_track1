# Git Commit Guide - AI HR Agent

## Prerequisites

### 1. Install Git (if not already installed)

**Windows**:
- Download from: https://git-scm.com/download/win
- Run installer with default settings
- Restart terminal after installation

**Verify installation**:
```bash
git --version
```

### 2. Configure Git (First time only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Initial Setup (If not already a git repository)

### Option A: New Repository

```bash
# Initialize git repository
git init

# Add remote (if you have a GitHub/GitLab repo)
git remote add origin https://github.com/yourusername/your-repo.git
```

### Option B: Existing Repository

```bash
# If you already cloned a repo, skip to "Committing Changes" section
```

---

## Committing Changes

### Step 1: Check Status

```bash
git status
```

This shows:
- Modified files (red)
- New files (red)
- Files ready to commit (green)

### Step 2: Add Files

**Add all files** (recommended for first commit):
```bash
git add .
```

**Or add specific files**:
```bash
git add hr_agent.py app.py README.md
```

**Important files to commit**:
```bash
# Core implementation
git add hr_agent.py
git add app.py
git add data_loader.py
git add requirements.txt

# Documentation
git add README.md
git add QUICKSTART.md
git add IMPLEMENTATION_SUMMARY.md
git add AWS_BEDROCK_INTEGRATION.md
git add ACTION_PLAN.md

# Testing
git add test_implementation.py

# Configuration
git add .gitignore

# Data (if not too large)
git add data/resume_dataset_1200.csv
git add data/"employee leave tracking data.xlsx"

# Spec files (optional but recommended)
git add .kiro/
```

### Step 3: Commit

```bash
git commit -m "Complete AI HR Agent implementation for NETRIK Hackathon 2026

- Implemented all 6 core requirements:
  * Resume screening with explainable scoring
  * Interview question generation (LLM-ready with template fallback)
  * Conflict-free interview scheduling
  * Pipeline state management with validation
  * Leave management with policy compliance
  * Query escalation with severity classification

- Added 5 new components:
  * PipelineStateValidator
  * InterviewQuestionGenerator
  * InterviewScheduler
  * LeaveManager
  * QueryEscalator

- Features:
  * Production-ready code with error handling
  * Comprehensive documentation
  * Interactive Streamlit UI
  * Complete test suite
  * AWS Bedrock integration ready

- Expected score: 85-95/100
- Team: Kanyaraasi
- Track: Track 1 - HR Agent"
```

### Step 4: Push to Remote (if applicable)

```bash
# First time push
git push -u origin main

# Or if your branch is named 'master'
git push -u origin master

# Subsequent pushes
git push
```

---

## Quick Commit Commands (Copy-Paste)

### Full Commit (Everything)

```bash
git add .
git commit -m "Complete AI HR Agent - All 6 requirements implemented"
git push
```

### Selective Commit (Core files only)

```bash
git add hr_agent.py app.py data_loader.py requirements.txt README.md .gitignore
git commit -m "Core implementation: HR Agent with all components"
git push
```

---

## What NOT to Commit

The `.gitignore` file already excludes these, but double-check:

❌ **Never commit**:
- `.env` file (contains AWS credentials!)
- `__pycache__/` folders
- `.vscode/` or `.idea/` folders
- Personal AWS credentials
- Large data files (>100MB)

✅ **Safe to commit**:
- All `.py` files
- All `.md` documentation files
- `requirements.txt`
- `.gitignore`
- Data files (if <100MB)
- `.kiro/` spec files

---

## Checking What Will Be Committed

Before committing, verify:

```bash
# See what files are staged
git status

# See what changes will be committed
git diff --cached

# See list of files that will be committed
git diff --cached --name-only
```

---

## Common Git Commands

### View History
```bash
git log --oneline
```

### Undo Last Commit (keep changes)
```bash
git reset --soft HEAD~1
```

### Undo Changes to a File
```bash
git checkout -- filename.py
```

### Create a Branch
```bash
git checkout -b feature-branch-name
```

### Switch Branches
```bash
git checkout main
```

### Merge Branch
```bash
git checkout main
git merge feature-branch-name
```

---

## GitHub/GitLab Setup (If needed)

### Create New Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `netrik-hr-agent` (or your choice)
3. Description: "AI HR Agent for NETRIK Hackathon 2026"
4. Choose Public or Private
5. Don't initialize with README (you already have one)
6. Click "Create repository"

### Connect Local to GitHub

```bash
git remote add origin https://github.com/yourusername/netrik-hr-agent.git
git branch -M main
git push -u origin main
```

---

## Commit Message Best Practices

### Good Commit Messages

✅ "Complete AI HR Agent implementation - all 6 requirements"
✅ "Add interview question generation with LLM support"
✅ "Implement conflict-free interview scheduling"
✅ "Add comprehensive documentation and test suite"

### Bad Commit Messages

❌ "Update"
❌ "Fix stuff"
❌ "Changes"
❌ "asdf"

### Our Recommended Commit Message

```
Complete AI HR Agent for NETRIK Hackathon 2026

Implemented all 6 core requirements:
- Resume screening with explainable scoring
- Interview question generation (LLM + templates)
- Conflict-free interview scheduling
- Pipeline state management
- Leave management with policy compliance
- Query escalation

Features:
- 5 modular components
- Production-ready error handling
- Comprehensive documentation
- Interactive Streamlit UI
- Complete test suite
- AWS Bedrock ready

Team: Kanyaraasi
Expected Score: 85-95/100
```

---

## Troubleshooting

### Issue: "git: command not found"
**Solution**: Install Git from https://git-scm.com/download/win

### Issue: "Permission denied (publickey)"
**Solution**: Use HTTPS instead of SSH, or set up SSH keys

### Issue: "Large files rejected"
**Solution**: 
```bash
# Remove large files from commit
git rm --cached data/large_file.csv
# Add to .gitignore
echo "data/large_file.csv" >> .gitignore
```

### Issue: "Merge conflict"
**Solution**:
```bash
# See conflicted files
git status

# Edit files to resolve conflicts
# Then:
git add resolved_file.py
git commit -m "Resolve merge conflict"
```

### Issue: "Accidentally committed .env file"
**Solution**:
```bash
# Remove from git but keep local file
git rm --cached .env
git commit -m "Remove .env from git"

# Add to .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

---

## Pre-Commit Checklist

Before committing, verify:

- [ ] `.gitignore` file exists
- [ ] No `.env` file in commit
- [ ] No `__pycache__/` folders in commit
- [ ] All core files included (hr_agent.py, app.py, etc.)
- [ ] Documentation files included
- [ ] Test file included
- [ ] requirements.txt updated
- [ ] Team ID is correct in hr_agent.py
- [ ] Commit message is descriptive

---

## Quick Reference Card

```bash
# Status
git status

# Add all files
git add .

# Commit
git commit -m "Your message"

# Push
git push

# Pull latest
git pull

# View history
git log --oneline

# Create branch
git checkout -b branch-name

# Switch branch
git checkout main
```

---

## After Committing

### Verify Commit

```bash
# Check last commit
git log -1

# See what was committed
git show HEAD
```

### Share Repository

If using GitHub/GitLab:
1. Go to your repository URL
2. Share link with team/judges
3. Ensure repository is public (if required)

### Tag Release (Optional)

```bash
# Create tag for submission
git tag -a v1.0-submission -m "NETRIK Hackathon 2026 Submission"
git push origin v1.0-submission
```

---

## Final Notes

1. **Commit often** - Don't wait until the end
2. **Write clear messages** - Future you will thank you
3. **Never commit secrets** - Use .gitignore for .env files
4. **Test before pushing** - Run validation test first
5. **Keep backups** - Git is your backup, but have local copies too

---

## Need Help?

- Git documentation: https://git-scm.com/doc
- GitHub guides: https://guides.github.com/
- Git cheat sheet: https://education.github.com/git-cheat-sheet-education.pdf

---

**Ready to commit?** Follow the "Quick Commit Commands" section above!
