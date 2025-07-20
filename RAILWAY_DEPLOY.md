# 🚀 Railway Deployment Guide

## Quick Setup (5 minutes)

### 1. Create GitHub Repository
1. Go to https://github.com/new
2. Name: `genyourbot`
3. Make it **Public** (Railway needs access)
4. Click "Create repository"

### 2. Push code to GitHub
```bash
# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/genyourbot.git

# Push to GitHub
git push -u origin main
```

### 3. Deploy on Railway
1. Go to https://railway.app
2. Click **"Login with GitHub"**
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `genyourbot` repository
6. Click **"Deploy Now"**

### 4. Add Environment Variables
In Railway dashboard:
1. Go to your project
2. Click **"Variables"** tab
3. Add these variables:

```
BOT_TOKEN=your_telegram_bot_token_here
CRYPTOBOT_API_TOKEN=your_cryptobot_api_token_here
```

### 5. Upload Firebase Key
1. In Railway dashboard, go to **"Settings"**
2. In **"Environment"** section
3. Upload your `serviceAccountKey.json` file

### 6. That's it! 🎉
Your bot should start automatically. Check logs in Railway dashboard.

## Free Tier Limits
- ✅ **500 hours/month** (always enough for 1 bot)
- ✅ **512MB RAM**
- ✅ **1GB storage**
- ✅ **Auto-sleep after 30min inactivity**

## Monitoring
- View logs in Railway dashboard
- Bot auto-restarts on crashes
- Easy redeploys from GitHub

---
**Need help?** Check Railway docs: https://docs.railway.app
