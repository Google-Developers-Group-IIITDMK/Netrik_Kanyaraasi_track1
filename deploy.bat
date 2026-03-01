@echo off
REM HR Agent Deployment Script for Windows
REM This script helps you deploy your HR Agent to various platforms

echo.
echo 🚀 HR Agent Deployment Helper
echo ==============================
echo.

REM Check if git is initialized
if not exist .git (
    echo 📦 Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit - HR Agent for NETRIK 2026"
    echo ✅ Git initialized
) else (
    echo ✅ Git already initialized
)

echo.
echo Choose deployment option:
echo 1) Streamlit Community Cloud (Recommended - Free)
echo 2) Heroku
echo 3) Docker (Local)
echo 4) AWS EC2 (Manual)
echo 5) Just commit and push to GitHub
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto streamlit
if "%choice%"=="2" goto heroku
if "%choice%"=="3" goto docker
if "%choice%"=="4" goto aws
if "%choice%"=="5" goto github
goto invalid

:streamlit
echo.
echo 📱 Streamlit Community Cloud Deployment
echo =======================================
echo.
echo Steps to deploy:
echo 1. Push your code to GitHub (option 5)
echo 2. Go to https://share.streamlit.io/
echo 3. Sign in with GitHub
echo 4. Click 'New app'
echo 5. Select your repository
echo 6. Main file: app.py
echo 7. Click 'Deploy'
echo.
echo 📖 Full guide: See DEPLOYMENT_GUIDE.md
goto end

:heroku
echo.
echo 🔷 Heroku Deployment
echo ====================
echo.

REM Check if heroku CLI is installed
where heroku >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli
    goto end
)

set /p app_name="Enter your Heroku app name: "

echo Creating Heroku app...
heroku create %app_name%

echo Setting buildpacks...
heroku buildpacks:set heroku/python

echo Deploying to Heroku...
git push heroku main

echo.
echo ✅ Deployed! Your app is at: https://%app_name%.herokuapp.com
echo.
echo To set environment variables:
echo heroku config:set AWS_ACCESS_KEY_ID=your_key
echo heroku config:set AWS_SECRET_ACCESS_KEY=your_secret
goto end

:docker
echo.
echo 🐳 Docker Deployment
echo ====================
echo.

REM Check if docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker not found. Install from: https://www.docker.com/get-started
    goto end
)

echo Building Docker image...
docker build -t hr-agent .

echo.
echo ✅ Image built successfully!
echo.
echo To run locally:
echo docker run -p 8501:8501 hr-agent
echo.
echo To run with AWS credentials:
echo docker run -p 8501:8501 -e AWS_ACCESS_KEY_ID=your_key -e AWS_SECRET_ACCESS_KEY=your_secret hr-agent
goto end

:aws
echo.
echo ☁️  AWS EC2 Deployment
echo ======================
echo.
echo Manual steps required:
echo 1. Launch EC2 instance (t2.micro or t2.small)
echo 2. Configure security group (ports 22, 80, 8501)
echo 3. SSH into instance
echo 4. Clone your repository
echo 5. Install dependencies
echo 6. Run: streamlit run app.py
echo.
echo 📖 Full guide: See DEPLOYMENT_GUIDE.md
goto end

:github
echo.
echo 📤 Pushing to GitHub
echo ====================
echo.

set /p repo_url="Enter your GitHub repository URL: "

REM Check if remote exists
git remote | findstr origin >nul
if %ERRORLEVEL% EQU 0 (
    echo Remote 'origin' already exists. Updating...
    git remote set-url origin %repo_url%
) else (
    echo Adding remote 'origin'...
    git remote add origin %repo_url%
)

echo Committing changes...
git add .
git commit -m "Update: Ready for deployment"

echo Pushing to GitHub...
git push -u origin main

echo.
echo ✅ Pushed to GitHub!
echo Repository: %repo_url%
goto end

:invalid
echo Invalid choice. Exiting.
goto end

:end
echo.
echo 🎉 Deployment process complete!
echo.
echo 📖 For detailed instructions, see: DEPLOYMENT_GUIDE.md
echo 🐛 For troubleshooting, check the guide or logs
echo.
pause
