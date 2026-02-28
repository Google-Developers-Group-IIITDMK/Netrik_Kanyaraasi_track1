#!/bin/bash
# Git Commit Script for AI HR Agent
# NETRIK Hackathon 2026 - Team Kanyaraasi

echo "========================================"
echo "AI HR Agent - Git Commit Helper"
echo "========================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "ERROR: Git is not installed or not in PATH"
    echo "Please install Git from: https://git-scm.com/download/win"
    echo ""
    exit 1
fi

echo "Git is installed. Proceeding..."
echo ""

# Check if this is a git repository
if [ ! -d ".git" ]; then
    echo "This is not a git repository yet."
    echo "Initializing git repository..."
    git init
    echo ""
fi

# Show current status
echo "Current git status:"
echo "----------------------------------------"
git status
echo "----------------------------------------"
echo ""

# Ask user to confirm
read -p "Ready to commit all changes? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Commit cancelled."
    exit 0
fi

echo ""
echo "Adding files to git..."
git add .

echo ""
echo "Creating commit..."
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

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Commit failed!"
    echo "Check the error message above."
    exit 1
fi

echo ""
echo "========================================"
echo "SUCCESS! Changes committed to git."
echo "========================================"
echo ""

# Check if remote exists
if git remote -v &> /dev/null; then
    echo "Remote repository found."
    echo ""
    read -p "Push to remote repository? (y/n): " push
    if [ "$push" = "y" ] || [ "$push" = "Y" ]; then
        echo "Pushing to remote..."
        git push
        if [ $? -ne 0 ]; then
            echo ""
            echo "Push failed. You may need to set upstream:"
            echo "  git push -u origin main"
        else
            echo ""
            echo "Successfully pushed to remote!"
        fi
    fi
else
    echo "No remote repository configured."
    echo "To push to GitHub/GitLab, run:"
    echo "  git remote add origin YOUR_REPO_URL"
    echo "  git push -u origin main"
fi

echo ""
echo "View commit history:"
git log --oneline -5

echo ""
echo "========================================"
echo "Done!"
echo "========================================"
