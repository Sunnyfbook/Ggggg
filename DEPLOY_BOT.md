# Bot Deployment Guide - Render

This guide will help you deploy your File to Link Bot to Render step by step.

## Prerequisites

- ✅ GitHub account
- ✅ Render account (sign up at [render.com](https://render.com))
- ✅ Telegram Bot Token (already updated in `info.py`)
- ✅ MongoDB database (already configured)

## Step 1: Prepare Your Repository

### 1.1 Create GitHub Repository
1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Name it: `filetolinkbot`
4. Make it **Public** (required for free Render)
5. Click "Create repository"

### 1.2 Upload Your Code
1. **Option A: Using Git (Recommended)**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/filetolinkbot.git
   git push -u origin main
   ```

2. **Option B: Direct Upload**
   - Go to your repository on GitHub
   - Click "uploading an existing file"
   - Drag and drop all files from your project folder
   - Click "Commit changes"

## Step 2: Deploy to Render

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Click "Get Started"
3. Sign up with GitHub (recommended)

### 2.2 Create New Web Service
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub account if not already connected

### 2.3 Configure Service
1. **Repository**: Select your `filetolinkbot` repository
2. **Name**: `filetolinkbot` (or any name you prefer)
3. **Region**: Choose closest to your users
4. **Branch**: `main`
5. **Root Directory**: Leave empty (deploy from root)
6. **Runtime**: `Python 3`
7. **Build Command**: `pip install -r requirements.txt`
8. **Start Command**: `python bot.py`

### 2.4 Environment Variables
Click "Environment" tab and add these variables:

```
BOT_TOKEN=8125185327:AAHqKXZxSg9GthfRX6VSg52aJ5Ik0bJzgAY
API_ID=1357592
API_HASH=7a0b3567c813916acafaa69bf8989f12
BOT_USERNAME=CamGrabberInsta_bot
BIN_CHANNEL=-1002679595778
LOG_CHANNEL=-1002679595778
ADMINS=7555349906
OWNER_USERNAME=BOT_OWNER26
PICS=https://envs.sh/_pM.jpg
CHANNEL=https://t.me/AV_BOTz_UPDATE
SUPPORT=https://t.me/AV_SUPPORT_GROUP
ENABLE_LIMIT=False
RATE_LIMIT_TIMEOUT=600
MAX_FILES=10
SHORTLINK=False
SHORTLINK_URL=linkmonetizer.in
SHORTLINK_API=63558804ef8ee5aa3522375d7e5762c0d40ded46
BANNED_CHANNELS=
BAN_CHNL=
BAN_ALERT=<b>ʏᴏᴜʀ ᴀʀᴇ ʙᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.ᴄᴏɴᴛᴀᴄᴛ [ᴀᴠ ᴄʜᴀᴛ ᴏᴡɴᴇʀ](https://telegram.me/AV_OWNER_BOT) ᴛᴏ ʀᴇsᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇ!!</b>
DATABASE_URI=mongodb+srv://sunnyfbook21:pY62CnoJaudg1wXt@cluster0.brruqsz.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=cluster0
AUTH_PICS=https://envs.sh/AwV.jpg
AUTH_CHANNEL=-1002679595778
FSUB=True
PORT=2626
NO_PORT=True
PING_INTERVAL=1200
SLEEP_THRESHOLD=60
WEB_SERVER_BIND_ADDRESS=0.0.0.0
WORKERS=4
MULTI_CLIENT=False
name=avbotz
ON_HEROKU=False
FQDN=
HAS_SSL=False
```

### 2.5 Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete (5-10 minutes)
3. Your bot URL will be: `https://your-app-name.onrender.com`

## Step 3: Test Your Bot

### 3.1 Check Deployment
1. Go to your Render dashboard
2. Click on your service
3. Check "Logs" tab for any errors
4. Status should show "Live"

### 3.2 Test Bot Functionality
1. Open Telegram
2. Find your bot: `@CamGrabberInsta_bot`
3. Send `/start`
4. Upload a file (video, document, etc.)
5. Check if bot responds with download links

### 3.3 Test API Endpoints
1. Open terminal/command prompt
2. Update `test_api.py` with your bot URL:
   ```python
   BOT_URL = "https://your-app-name.onrender.com"
   ```
3. Run the test:
   ```bash
   python test_api.py
   ```

## Step 4: Configure Auto-Deploy

### 4.1 Enable Auto-Deploy
1. In Render dashboard, go to your service
2. Click "Settings" tab
3. Enable "Auto-Deploy"
4. Now every push to GitHub will auto-deploy

### 4.2 Set Up Webhook (Optional)
1. In Telegram, message @BotFather
2. Send `/setwebhook`
3. Set webhook URL: `https://your-app-name.onrender.com`

## Step 5: Monitor Your Bot

### 5.1 Check Logs
- Go to Render dashboard
- Click "Logs" tab
- Monitor for errors or issues

### 5.2 Health Check
- Visit: `https://your-app-name.onrender.com/api/health`
- Should return JSON with status "healthy"

### 5.3 Bot Status
- Check if bot responds in Telegram
- Test file upload functionality
- Verify download links work

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` exists
   - Verify Python version compatibility
   - Check logs for missing dependencies

2. **Bot Not Responding**
   - Verify BOT_TOKEN is correct
   - Check if bot is started in Telegram
   - Look for errors in Render logs

3. **API Endpoints Not Working**
   - Check if service is "Live"
   - Verify CORS headers are present
   - Test with `test_api.py`

4. **Database Connection Issues**
   - Verify DATABASE_URI is correct
   - Check MongoDB connection
   - Ensure database exists

### Debug Steps

1. **Check Render Logs**
   ```
   Go to Render Dashboard → Your Service → Logs
   ```

2. **Test API Manually**
   ```bash
   curl https://your-app-name.onrender.com/api/health
   ```

3. **Check Bot Status**
   ```
   Message your bot in Telegram
   Send /start
   Upload a test file
   ```

## Important Notes

- ✅ **Free Tier**: Render free tier has limitations
- ✅ **Sleep Mode**: Free services sleep after 15 minutes of inactivity
- ✅ **Cold Start**: First request after sleep may be slow
- ✅ **Logs**: Check logs regularly for issues
- ✅ **Backup**: Keep your code in GitHub

## Next Steps

After successful bot deployment:
1. ✅ Test all functionality
2. ✅ Note your bot URL for Netlify integration
3. ✅ Proceed to deploy web interface
4. ✅ Connect both services

Your bot is now deployed and ready to work with the Netlify web interface! 🚀 