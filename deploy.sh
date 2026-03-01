#!/bin/bash

# HR Agent Deployment Script
# This script helps you deploy your HR Agent to various platforms

echo "🚀 HR Agent Deployment Helper"
echo "=============================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - HR Agent for NETRIK 2026"
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

echo ""
echo "Choose deployment option:"
echo "1) Streamlit Community Cloud (Recommended - Free)"
echo "2) Heroku"
echo "3) Docker (Local)"
echo "4) AWS EC2 (Manual)"
echo "5) Just commit and push to GitHub"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📱 Streamlit Community Cloud Deployment"
        echo "======================================="
        echo ""
        echo "Steps to deploy:"
        echo "1. Push your code to GitHub (option 5)"
        echo "2. Go to https://share.streamlit.io/"
        echo "3. Sign in with GitHub"
        echo "4. Click 'New app'"
        echo "5. Select your repository"
        echo "6. Main file: app.py"
        echo "7. Click 'Deploy'"
        echo ""
        echo "📖 Full guide: See DEPLOYMENT_GUIDE.md"
        ;;
    
    2)
        echo ""
        echo "🔷 Heroku Deployment"
        echo "===================="
        echo ""
        
        # Check if heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        read -p "Enter your Heroku app name: " app_name
        
        echo "Creating Heroku app..."
        heroku create $app_name
        
        echo "Setting buildpacks..."
        heroku buildpacks:set heroku/python
        
        echo "Deploying to Heroku..."
        git push heroku main
        
        echo ""
        echo "✅ Deployed! Your app is at: https://$app_name.herokuapp.com"
        echo ""
        echo "To set environment variables:"
        echo "heroku config:set AWS_ACCESS_KEY_ID=your_key"
        echo "heroku config:set AWS_SECRET_ACCESS_KEY=your_secret"
        ;;
    
    3)
        echo ""
        echo "🐳 Docker Deployment"
        echo "===================="
        echo ""
        
        # Check if docker is installed
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not found. Install from: https://www.docker.com/get-started"
            exit 1
        fi
        
        echo "Building Docker image..."
        docker build -t hr-agent .
        
        echo ""
        echo "✅ Image built successfully!"
        echo ""
        echo "To run locally:"
        echo "docker run -p 8501:8501 hr-agent"
        echo ""
        echo "To run with AWS credentials:"
        echo "docker run -p 8501:8501 -e AWS_ACCESS_KEY_ID=your_key -e AWS_SECRET_ACCESS_KEY=your_secret hr-agent"
        ;;
    
    4)
        echo ""
        echo "☁️  AWS EC2 Deployment"
        echo "======================"
        echo ""
        echo "Manual steps required:"
        echo "1. Launch EC2 instance (t2.micro or t2.small)"
        echo "2. Configure security group (ports 22, 80, 8501)"
        echo "3. SSH into instance"
        echo "4. Clone your repository"
        echo "5. Install dependencies"
        echo "6. Run: streamlit run app.py"
        echo ""
        echo "📖 Full guide: See DEPLOYMENT_GUIDE.md"
        ;;
    
    5)
        echo ""
        echo "📤 Pushing to GitHub"
        echo "===================="
        echo ""
        
        read -p "Enter your GitHub repository URL: " repo_url
        
        # Check if remote exists
        if git remote | grep -q origin; then
            echo "Remote 'origin' already exists. Updating..."
            git remote set-url origin $repo_url
        else
            echo "Adding remote 'origin'..."
            git remote add origin $repo_url
        fi
        
        echo "Committing changes..."
        git add .
        git commit -m "Update: Ready for deployment"
        
        echo "Pushing to GitHub..."
        git push -u origin main
        
        echo ""
        echo "✅ Pushed to GitHub!"
        echo "Repository: $repo_url"
        ;;
    
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process complete!"
echo ""
echo "📖 For detailed instructions, see: DEPLOYMENT_GUIDE.md"
echo "🐛 For troubleshooting, check the guide or logs"
echo ""
