# Git Quick Start - 3 Easy Steps

## Option 1: Automated Script (Easiest)

### Windows Command Prompt or PowerShell:
```bash
commit_to_git.bat
```

### Git Bash or Linux/Mac:
```bash
chmod +x commit_to_git.sh
./commit_to_git.sh
```

The script will:
1. Check if git is installed
2. Initialize repository if needed
3. Show current status
4. Add all files
5. Create commit with detailed message
6. Optionally push to remote

---

## Option 2: Manual Commands (3 Steps)

### Step 1: Add all files
```bash
git add .
```

### Step 2: Commit with message
```bash
git commit -m "Complete AI HR Agent - All 6 requirements implemented"
```

### Step 3: Push to remote (if configured)
```bash
git push
```

---

## Option 3: First Time Setup

If you haven't set up git yet:

### 1. Install Git
Download from: https://git-scm.com/download/win

### 2. Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Initialize Repository
```bash
git init
```

### 4. Add Remote (if using GitHub/GitLab)
```bash
git remote add origin https://github.com/yourusername/your-repo.git
```

### 5. Commit and Push
```bash
git add .
git commit -m "Initial commit - Complete AI HR Agent"
git push -u origin main
```

---

## What Gets Committed?

✅ **Included** (safe to commit):
- `hr_agent.py` - Core implementation
- `app.py` - Streamlit UI
- `data_loader.py` - Data loading
- `requirements.txt` - Dependencies
- `README.md` - Documentation
- `test_implementation.py` - Tests
- All other `.md` files
- `.gitignore` - Git configuration
- Data files (if <100MB)

❌ **Excluded** (via .gitignore):
- `.env` - AWS credentials (NEVER commit!)
- `__pycache__/` - Python cache
- `.vscode/` - IDE settings
- `*.pyc` - Compiled Python
- `.streamlit/` - Streamlit cache

---

## Verify Before Committing

```bash
# Check what will be committed
git status

# See changes
git diff

# See staged files
git diff --cached --name-only
```

---

## After Committing

### View Commit History
```bash
git log --oneline
```

### View Last Commit
```bash
git show HEAD
```

### Check Remote Status
```bash
git remote -v
```

---

## Troubleshooting

### "git: command not found"
**Solution**: Install Git from https://git-scm.com/download/win

### "Permission denied"
**Solution**: Use HTTPS URL instead of SSH

### "Large files rejected"
**Solution**: Remove large files or use Git LFS

### "Nothing to commit"
**Solution**: You've already committed everything!

---

## Quick Reference

```bash
git status          # Check status
git add .           # Add all files
git commit -m "msg" # Commit with message
git push            # Push to remote
git pull            # Pull from remote
git log             # View history
```

---

## Need More Help?

See `GIT_COMMIT_GUIDE.md` for detailed instructions.

---

**Ready?** Run `commit_to_git.bat` (Windows) or `./commit_to_git.sh` (Git Bash)!
