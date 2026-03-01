# HR Agent Deployment Guide

## Quick Deployment Options

### Option 1: Streamlit Community Cloud (Recommended - FREE)

**Best for:** Hackathon demos, quick sharing, free hosting

**Steps:**

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - HR Agent"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/hr-agent.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/hr-agent`
   - Main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets (if using AWS Bedrock):**
   - In Streamlit Cloud dashboard, go to your app settings
   - Click "Secrets"
   - Add your environment variables:
   ```toml
   AWS_ACCESS_KEY_ID = "your_access_key"
   AWS_SECRET_ACCESS_KEY = "your_secret_key"
   AWS_REGION = "us-east-1"
   ```

**Pros:**
- ✅ Completely free
- ✅ Easy setup (5 minutes)
- ✅ Auto-deploys on git push
- ✅ Perfect for hackathons
- ✅ Custom domain available

**Cons:**
- ⚠️ Limited resources (1GB RAM)
- ⚠️ App sleeps after inactivity

---

### Option 2: Heroku (Free Tier Available)

**Best for:** More control, better performance

**Steps:**

1. **Create Procfile:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create runtime.txt:**
   ```
   python-3.11.0
   ```

3. **Deploy:**
   ```bash
   heroku login
   heroku create hr-agent-netrik
   git push heroku main
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set AWS_ACCESS_KEY_ID=your_key
   heroku config:set AWS_SECRET_ACCESS_KEY=your_secret
   heroku config:set AWS_REGION=us-east-1
   ```

**Pros:**
- ✅ Better performance than Streamlit Cloud
- ✅ More RAM (512MB free tier)
- ✅ Custom domains

**Cons:**
- ⚠️ Requires credit card for verification
- ⚠️ App sleeps after 30 min inactivity (free tier)

---

### Option 3: AWS EC2 (Production-Ready)

**Best for:** Production deployment, full control

**Steps:**

1. **Launch EC2 Instance:**
   - Instance type: t2.micro (free tier) or t2.small
   - OS: Ubuntu 22.04 LTS
   - Security group: Allow ports 22 (SSH), 80 (HTTP), 8501 (Streamlit)

2. **Connect and setup:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3-pip python3-venv -y
   
   # Clone your repository
   git clone https://github.com/YOUR_USERNAME/hr-agent.git
   cd hr-agent
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set environment variables
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_REGION=us-east-1
   
   # Run with nohup (keeps running after logout)
   nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
   ```

3. **Access your app:**
   - http://your-ec2-ip:8501

4. **Optional - Setup Nginx reverse proxy:**
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/hr-agent
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```
   
   Enable:
   ```bash
   sudo ln -s /etc/nginx/sites-available/hr-agent /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

**Pros:**
- ✅ Full control
- ✅ Production-ready
- ✅ Scalable
- ✅ No sleep/downtime

**Cons:**
- ⚠️ Costs money (after free tier)
- ⚠️ Requires server management
- ⚠️ More complex setup

---

### Option 4: Docker + Any Cloud Platform

**Best for:** Containerized deployment, portability

**Steps:**

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Create .dockerignore:**
   ```
   __pycache__
   *.pyc
   .env
   .git
   .kiro
   venv
   ```

3. **Build and run locally:**
   ```bash
   docker build -t hr-agent .
   docker run -p 8501:8501 -e AWS_ACCESS_KEY_ID=your_key hr-agent
   ```

4. **Deploy to cloud:**
   - **Google Cloud Run:** `gcloud run deploy`
   - **AWS ECS:** Push to ECR and deploy
   - **Azure Container Instances:** `az container create`

**Pros:**
- ✅ Portable
- ✅ Consistent environment
- ✅ Easy scaling

**Cons:**
- ⚠️ Requires Docker knowledge
- ⚠️ More complex setup

---

## Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All dependencies in `requirements.txt`
- [ ] `.env` file NOT committed (use `.gitignore`)
- [ ] Secrets configured in deployment platform
- [ ] Data files included or accessible
- [ ] Test locally: `streamlit run app.py`
- [ ] Check for hardcoded paths (use relative paths)
- [ ] Verify all imports work
- [ ] Test with sample data

---

## Environment Variables Setup

Your app needs these environment variables (optional for basic functionality):

```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

**Note:** The app works without AWS credentials by falling back to keyword matching!

---

## Quick Start Commands

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Access at: http://localhost:8501
```

### Git Setup (for Streamlit Cloud/Heroku)
```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - HR Agent for NETRIK 2026"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/hr-agent.git

# Push
git push -u origin main
```

---

## Troubleshooting

### Issue: Module not found
**Solution:** Add missing package to `requirements.txt`

### Issue: Port already in use
**Solution:** 
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

### Issue: AWS credentials error
**Solution:** App works without AWS! It falls back to keyword matching. For full LLM features, configure AWS Bedrock credentials.

### Issue: Large file size
**Solution:** Use Git LFS for large data files:
```bash
git lfs install
git lfs track "*.csv"
git add .gitattributes
```

---

## Recommended: Streamlit Cloud Deployment (Step-by-Step)

This is the fastest way to get your app online for the hackathon:

1. **Prepare your repository:**
   ```bash
   # Make sure .gitignore excludes sensitive files
   echo ".env" >> .gitignore
   echo "__pycache__/" >> .gitignore
   echo "*.pyc" >> .gitignore
   
   # Commit everything
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy:**
   - Visit: https://share.streamlit.io/
   - Click "New app"
   - Connect GitHub account
   - Select repository
   - Main file: `app.py`
   - Click "Deploy"

3. **Share your app:**
   - You'll get a URL like: `https://your-app.streamlit.app`
   - Share this URL with judges/team

4. **Monitor:**
   - View logs in Streamlit Cloud dashboard
   - Check resource usage
   - Update by pushing to GitHub (auto-deploys)

---

## Performance Tips

1. **Cache data loading:**
   ```python
   @st.cache_data
   def load_candidates(path):
       return load_candidates(path)
   ```

2. **Optimize imports:**
   - Import only what you need
   - Use lazy imports for heavy libraries

3. **Reduce data size:**
   - Use smaller dataset for demo
   - Paginate results

4. **Enable compression:**
   ```python
   st.set_page_config(
       page_title="HR Agent",
       layout="wide",
       initial_sidebar_state="expanded"
   )
   ```

---

## Support & Resources

- **Streamlit Docs:** https://docs.streamlit.io/
- **Streamlit Community:** https://discuss.streamlit.io/
- **Deployment Guide:** https://docs.streamlit.io/streamlit-community-cloud
- **Heroku Docs:** https://devcenter.heroku.com/
- **AWS EC2 Guide:** https://docs.aws.amazon.com/ec2/

---

## For Hackathon Judges

**Live Demo URL:** [Your deployed URL here]

**GitHub Repository:** [Your repo URL here]

**Key Features:**
- ✅ Complete HR automation (6 modules)
- ✅ Resume screening with semantic matching
- ✅ Interview scheduling
- ✅ Question generation
- ✅ Leave management
- ✅ Query escalation
- ✅ Beautiful UI with Plotly visualizations

**Tech Stack:**
- Python 3.11
- Streamlit
- AWS Bedrock (optional)
- Plotly
- Pandas
- Sentence Transformers

---

## Next Steps After Deployment

1. Test all features on deployed app
2. Share URL with team/judges
3. Monitor logs for errors
4. Prepare demo script
5. Document any known issues
6. Create backup deployment (if time permits)

Good luck with your hackathon! 🚀
