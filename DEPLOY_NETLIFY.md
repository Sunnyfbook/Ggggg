# Web Interface Deployment Guide - Netlify

This guide will help you deploy the web interface to Netlify step by step.

## Prerequisites

- ✅ GitHub account
- ✅ Netlify account (sign up at [netlify.com](https://netlify.com))
- ✅ Bot already deployed on Render (from previous guide)
- ✅ Bot URL ready (e.g., `https://your-bot-name.onrender.com`)

## Step 1: Prepare Your Repository

### 1.1 Create GitHub Repository for Web Interface
1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Name it: `filetolinkbot-web`
4. Make it **Public** (required for free Netlify)
5. Click "Create repository"

### 1.2 Upload Web Interface Files
1. **Option A: Using Git (Recommended)**
   ```bash
   # Create a new folder for web interface
   mkdir filetolinkbot-web
   cd filetolinkbot-web
   
   # Copy netlify-web contents
   cp -r ../filetolinkbot-main/netlify-web/* .
   
   # Initialize git and push
   git init
   git add .
   git commit -m "Initial web interface commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/filetolinkbot-web.git
   git push -u origin main
   ```

2. **Option B: Direct Upload**
   - Go to your `filetolinkbot-web` repository on GitHub
   - Click "uploading an existing file"
   - Drag and drop all files from `netlify-web/` folder
   - Click "Commit changes"

## Step 2: Update API URLs

### 2.1 Update JavaScript Files
Before deploying, update these files with your actual bot URL:

1. **Edit `js/app.js`**
   ```javascript
   // Line 2: Replace with your actual bot URL
   const BOT_API_URL = 'https://your-bot-name.onrender.com';
   ```

2. **Edit `js/stream.js`**
   ```javascript
   // Line 2: Replace with your actual bot URL
   const BOT_API_URL = 'https://your-bot-name.onrender.com';
   ```

3. **Edit `js/download.js`**
   ```javascript
   // Line 2: Replace with your actual bot URL
   const BOT_API_URL = 'https://your-bot-name.onrender.com';
   ```

4. **Edit `netlify.toml`**
   ```toml
   # Line 12: Replace with your actual bot URL
   connect-src 'self' https://your-bot-name.onrender.com;
   ```

### 2.2 Commit Changes
```bash
git add .
git commit -m "Update API URLs"
git push
```

## Step 3: Deploy to Netlify

### 3.1 Create Netlify Account
1. Go to [netlify.com](https://netlify.com)
2. Click "Sign up"
3. Sign up with GitHub (recommended)

### 3.2 Deploy from Git
1. In Netlify dashboard, click "New site from Git"
2. Choose "GitHub" as Git provider
3. Authorize Netlify to access your GitHub account

### 3.3 Configure Deployment
1. **Repository**: Select your `filetolinkbot-web` repository
2. **Branch**: `main`
3. **Base directory**: Leave empty (deploy from root)
4. **Build command**: Leave empty (static site)
5. **Publish directory**: Leave empty (deploy from root)

### 3.4 Deploy
1. Click "Deploy site"
2. Wait for deployment (2-5 minutes)
3. Your site URL will be: `https://random-name.netlify.app`

## Step 4: Configure Custom Domain (Optional)

### 4.1 Add Custom Domain
1. In Netlify dashboard, go to your site
2. Click "Domain settings"
3. Click "Add custom domain"
4. Enter your domain (e.g., `mydownloader.com`)
5. Follow DNS configuration instructions

### 4.2 Configure DNS
1. Go to your domain registrar
2. Add CNAME record:
   - **Name**: `@` or `www`
   - **Value**: `your-site-name.netlify.app`
3. Wait for DNS propagation (up to 24 hours)

## Step 5: Test Your Web Interface

### 5.1 Test Home Page
1. Visit your Netlify URL
2. Check if page loads correctly
3. Verify design and functionality

### 5.2 Test API Connection
1. Open browser developer tools (F12)
2. Go to "Console" tab
3. Try uploading a file or entering a URL
4. Check for any CORS errors

### 5.3 Test File Access
1. Get a file link from your bot
2. Try accessing it through the web interface
3. Test both streaming and download functionality

## Step 6: Configure Site Settings

### 6.1 Enable HTTPS
- ✅ Already enabled by default on Netlify

### 6.2 Configure Redirects
1. Go to "Site settings" → "Build & deploy"
2. Click "Edit settings" under "Post processing"
3. Add redirect rule:
   ```
   /*    /index.html   200
   ```

### 6.3 Enable Analytics (Optional)
1. Go to "Site settings" → "Analytics"
2. Enable "Netlify Analytics"
3. Monitor your site traffic

## Step 7: Test Complete Flow

### 7.1 End-to-End Test
1. **Upload file to bot**:
   - Open Telegram
   - Send file to your bot
   - Get download/stream links

2. **Test web interface**:
   - Visit your Netlify site
   - Try the file links from bot
   - Verify streaming and download work

3. **Test direct access**:
   - Use file IDs directly in web interface
   - Test streaming page: `your-site.netlify.app/stream.html?id=FILE_ID`
   - Test download page: `your-site.netlify.app/download.html?id=FILE_ID`

## Troubleshooting

### Common Issues

1. **Page Not Loading**
   - Check if deployment was successful
   - Verify all files were uploaded
   - Check Netlify logs

2. **API Connection Errors**
   - Verify bot URL is correct in JavaScript files
   - Check if bot is running on Render
   - Test bot API endpoints manually

3. **CORS Errors**
   - Ensure bot has CORS headers
   - Check browser console for errors
   - Verify bot URL in `netlify.toml`

4. **File Not Found**
   - Check if file ID is correct
   - Verify file exists in bot's database
   - Test with a known working file

### Debug Steps

1. **Check Netlify Logs**
   ```
   Go to Netlify Dashboard → Your Site → Deploys → Latest Deploy → View Logs
   ```

2. **Test API Manually**
   ```bash
   curl https://your-bot-name.onrender.com/api/health
   ```

3. **Check Browser Console**
   ```
   Open Developer Tools → Console
   Look for JavaScript errors
   ```

4. **Test File Access**
   ```
   Visit: https://your-site.netlify.app/stream.html?id=TEST_FILE_ID
   ```

## Performance Optimization

### 1. Enable Compression
- ✅ Already enabled by default on Netlify

### 2. Optimize Images
- Use WebP format when possible
- Compress images before uploading
- Use appropriate sizes

### 3. Minimize JavaScript
- Consider bundling JS files
- Remove unused code
- Use modern JavaScript features

## Security Considerations

### 1. HTTPS
- ✅ Automatically enabled on Netlify

### 2. Security Headers
- ✅ Already configured in `netlify.toml`

### 3. Content Security Policy
- ✅ Configured to allow necessary resources

## Monitoring

### 1. Netlify Analytics
- Monitor page views
- Track user behavior
- Analyze performance

### 2. Error Tracking
- Check Netlify logs regularly
- Monitor browser console errors
- Test functionality periodically

### 3. Performance Monitoring
- Use Netlify's built-in analytics
- Monitor page load times
- Track API response times

## Important Notes

- ✅ **Free Tier**: Netlify free tier is generous
- ✅ **Global CDN**: Automatic global distribution
- ✅ **HTTPS**: Automatic SSL certificates
- ✅ **Auto-Deploy**: Automatic deployment from Git
- ✅ **Custom Domains**: Easy domain configuration

## Next Steps

After successful web interface deployment:
1. ✅ Test all functionality
2. ✅ Configure custom domain (optional)
3. ✅ Monitor performance
4. ✅ Share your web interface URL

Your web interface is now deployed and ready to work with your bot! 🚀

## Quick Reference

- **Bot URL**: `https://your-bot-name.onrender.com`
- **Web Interface URL**: `https://your-site-name.netlify.app`
- **API Health Check**: `https://your-bot-name.onrender.com/api/health`
- **Test Script**: `python test_api.py` 