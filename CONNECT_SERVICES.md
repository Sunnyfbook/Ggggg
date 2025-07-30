# Connect Bot and Web Interface

This guide will help you connect your deployed bot (Render) with your web interface (Netlify).

## Prerequisites

- ✅ Bot deployed on Render (from `DEPLOY_BOT.md`)
- ✅ Web interface deployed on Netlify (from `DEPLOY_NETLIFY.md`)
- ✅ Both services are working independently

## Step 1: Get Your URLs

### 1.1 Bot URL (Render)
1. Go to your Render dashboard
2. Click on your bot service
3. Copy the URL: `https://your-bot-name.onrender.com`

### 1.2 Web Interface URL (Netlify)
1. Go to your Netlify dashboard
2. Click on your site
3. Copy the URL: `https://your-site-name.netlify.app`

## Step 2: Update Web Interface API URLs

### 2.1 Update JavaScript Files
You need to update 4 files in your web interface repository:

1. **Edit `js/app.js`**
   ```javascript
   // Find this line (around line 2):
   const BOT_API_URL = 'https://your-bot-render-url.onrender.com';
   
   // Replace with your actual bot URL:
   const BOT_API_URL = 'https://your-bot-name.onrender.com';
   ```

2. **Edit `js/stream.js`**
   ```javascript
   // Find this line (around line 2):
   const BOT_API_URL = 'https://your-bot-render-url.onrender.com';
   
   // Replace with your actual bot URL:
   const BOT_API_URL = 'https://your-bot-name.onrender.com';
   ```

3. **Edit `js/download.js`**
   ```javascript
   // Find this line (around line 2):
   const BOT_API_URL = 'https://your-bot-render-url.onrender.com';
   
   // Replace with your actual bot URL:
   const BOT_API_URL = 'https://your-bot-name.onrender.com';
   ```

4. **Edit `netlify.toml`**
   ```toml
   # Find this line (around line 12):
   connect-src 'self' https://your-bot-render-url.onrender.com;
   
   # Replace with your actual bot URL:
   connect-src 'self' https://your-bot-name.onrender.com;
   ```

### 2.2 Commit and Deploy Changes
```bash
# In your web interface repository
git add .
git commit -m "Update API URLs to connect with bot"
git push
```

**Note**: Netlify will automatically redeploy when you push to GitHub.

## Step 3: Test the Connection

### 3.1 Test Bot API Endpoints
1. **Health Check**:
   ```bash
   curl https://your-bot-name.onrender.com/api/health
   ```
   Should return: `{"success": true, "status": "healthy"}`

2. **Test with Browser**:
   - Open browser
   - Visit: `https://your-bot-name.onrender.com/api/health`
   - Should see JSON response

### 3.2 Test Web Interface
1. **Visit your Netlify site**:
   - Go to: `https://your-site-name.netlify.app`
   - Check if page loads correctly

2. **Test API Connection**:
   - Open browser developer tools (F12)
   - Go to "Console" tab
   - Try uploading a file or entering a URL
   - Check for any errors

### 3.3 Test Complete Flow
1. **Upload file to bot**:
   - Open Telegram
   - Send a file to your bot
   - Get the download/stream links

2. **Test in web interface**:
   - Visit your Netlify site
   - Try the file links from your bot
   - Verify streaming and download work

## Step 4: Verify CORS Configuration

### 4.1 Check CORS Headers
1. **Test CORS manually**:
   ```bash
   curl -H "Origin: https://your-site-name.netlify.app" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS https://your-bot-name.onrender.com/api/health
   ```

2. **Check response headers**:
   - Should include: `Access-Control-Allow-Origin: *`
   - Should include: `Access-Control-Allow-Methods: GET, POST, OPTIONS`

### 4.2 Fix CORS Issues (if any)
If you get CORS errors:

1. **Check bot logs**:
   - Go to Render dashboard
   - Click "Logs" tab
   - Look for CORS-related errors

2. **Verify middleware**:
   - Check if `cors_middleware` is added in `web/__init__.py`
   - Ensure it's applied to all routes

## Step 5: Test File Access

### 5.1 Test Direct File Access
1. **Get a file ID from your bot**:
   - Upload a file to your bot
   - Note the file ID from the response

2. **Test streaming**:
   - Visit: `https://your-site-name.netlify.app/stream.html?id=FILE_ID`
   - Should load the video player

3. **Test download**:
   - Visit: `https://your-site-name.netlify.app/download.html?id=FILE_ID`
   - Should show download options

### 5.2 Test URL Processing
1. **Test URL input**:
   - Go to your Netlify site
   - Enter a video URL
   - Check if it processes correctly

2. **Check console for errors**:
   - Open developer tools
   - Look for any API errors
   - Verify responses

## Step 6: Monitor and Debug

### 6.1 Monitor Bot Logs
1. **Check Render logs**:
   - Go to Render dashboard
   - Click "Logs" tab
   - Monitor for API requests

2. **Check for errors**:
   - Look for 404, 500, or CORS errors
   - Monitor API response times

### 6.2 Monitor Web Interface
1. **Check Netlify logs**:
   - Go to Netlify dashboard
   - Click "Deploys"
   - Check latest deploy logs

2. **Monitor browser console**:
   - Open developer tools
   - Check for JavaScript errors
   - Monitor API calls

### 6.3 Test Performance
1. **Test loading times**:
   - Check how fast pages load
   - Monitor API response times
   - Test on different devices

2. **Test functionality**:
   - Upload different file types
   - Test streaming quality
   - Verify download speeds

## Step 7: Troubleshooting Common Issues

### 7.1 API Connection Issues

**Problem**: Web interface can't connect to bot API
**Solution**:
1. Verify bot URL is correct in all JavaScript files
2. Check if bot is running on Render
3. Test API endpoints manually
4. Check CORS configuration

### 7.2 CORS Errors

**Problem**: Browser blocks API requests
**Solution**:
1. Ensure CORS middleware is active
2. Check bot URL in `netlify.toml`
3. Verify security headers
4. Test with different browsers

### 7.3 File Not Found

**Problem**: Files don't load in web interface
**Solution**:
1. Check if file ID is correct
2. Verify file exists in bot's database
3. Test with a known working file
4. Check bot logs for errors

### 7.4 Slow Loading

**Problem**: Web interface loads slowly
**Solution**:
1. Check Netlify CDN performance
2. Optimize images and assets
3. Monitor API response times
4. Consider caching strategies

## Step 8: Final Verification

### 8.1 Complete End-to-End Test
1. **Upload file to bot**:
   ```
   Telegram → Bot → Get file links
   ```

2. **Test web interface**:
   ```
   Netlify site → Use file links → Stream/Download
   ```

3. **Test direct access**:
   ```
   Browser → Direct file URLs → Verify functionality
   ```

### 8.2 Performance Check
1. **Page load times**: Should be under 3 seconds
2. **API response times**: Should be under 5 seconds
3. **Streaming quality**: Should be smooth
4. **Download speeds**: Should be reasonable

### 8.3 Security Check
1. **HTTPS**: Both sites should use HTTPS
2. **CORS**: Should allow necessary requests
3. **Headers**: Security headers should be present
4. **Validation**: Input validation should work

## Success Indicators

✅ **Bot responds in Telegram**
✅ **Web interface loads correctly**
✅ **API endpoints return data**
✅ **Files stream and download**
✅ **No CORS errors in console**
✅ **Both sites use HTTPS**
✅ **Performance is acceptable**

## Quick Reference

### URLs
- **Bot**: `https://your-bot-name.onrender.com`
- **Web Interface**: `https://your-site-name.netlify.app`
- **Health Check**: `https://your-bot-name.onrender.com/api/health`

### Test Commands
```bash
# Test bot health
curl https://your-bot-name.onrender.com/api/health

# Test CORS
curl -H "Origin: https://your-site-name.netlify.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS https://your-bot-name.onrender.com/api/health

# Test file info
curl https://your-bot-name.onrender.com/api/file/FILE_ID
```

### Debug Steps
1. Check bot logs on Render
2. Check web interface logs on Netlify
3. Check browser console for errors
4. Test API endpoints manually
5. Verify file IDs and URLs

## Next Steps

After successful connection:
1. ✅ Monitor both services
2. ✅ Set up alerts for errors
3. ✅ Optimize performance
4. ✅ Add custom domain (optional)
5. ✅ Share your web interface URL

Your bot and web interface are now connected and working together! 🚀

## Support

If you encounter issues:
1. Check this guide for troubleshooting steps
2. Verify all URLs are correct
3. Test each component independently
4. Check logs for specific errors
5. Use the test script: `python test_api.py` 