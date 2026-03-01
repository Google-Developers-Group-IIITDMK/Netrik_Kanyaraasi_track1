# 🚀 Quick Deployment Guide

## Fastest Way to Deploy (5 Minutes)

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "HR Agent - Ready for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/hr-agent.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to **https://share.streamlit.io/**
2. Click **"New app"**
3. Sign in with GitHub
4. Select your repository: `YOUR_USERNAME/hr-agent`
5. Main file path: `app.py`
6. Click **"Deploy"**

**That's it!** Your app will be live in 2-3 minutes at:
`https://your-app-name.streamlit.app`

---

## Alternative: Use Deployment Script

### Windows:
```bash
deploy.bat
```

### Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

Follow the prompts to choose your deployment platform.

---

## Environment Variables (Optional)

If you want to use AWS Bedrock LLM features:

1. In Streamlit Cloud dashboard → App Settings → Secrets
2. Add:
```toml
AWS_ACCESS_KEY_ID = "your_key"
AWS_SECRET_ACCESS_KEY = "your_secret"
AWS_REGION = "us-east-1"
```

**Note:** App works perfectly without AWS credentials using keyword matching!

---

## Test Locally First

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Open browser to: http://localhost:8501
```

---

## Troubleshooting

**Issue:** Module not found
- **Fix:** `pip install -r requirements.txt`

**Issue:** Port already in use
- **Fix (Windows):** `netstat -ano | findstr :8501` then `taskkill /PID <PID> /F`
- **Fix (Linux/Mac):** `lsof -ti:8501 | xargs kill -9`

**Issue:** Git push rejected
- **Fix:** `git pull origin main --rebase` then `git push origin main`

---

## Need More Help?

See **DEPLOYMENT_GUIDE.md** for:
- Detailed deployment instructions
- Multiple platform options
- Advanced configuration
- Performance optimization
- Troubleshooting guide

---

## Quick Links

- **Streamlit Cloud:** https://share.streamlit.io/
- **Streamlit Docs:** https://docs.streamlit.io/
- **GitHub:** https://github.com/
- **Full Guide:** DEPLOYMENT_GUIDE.md

---

Good luck with your hackathon! 🎉
