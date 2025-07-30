# Netlify URL Setup Guide

This guide will help you configure your bot to generate Netlify URLs instead of Render URLs.

## 🔧 **Step 1: Get Your Netlify URL**

1. **Go to your Netlify dashboard**
2. **Click on your site**
3. **Copy the URL**: `https://your-site-name.netlify.app`

## 🔧 **Step 2: Update Render Environment Variables**

1. **Go to Render dashboard**
2. **Click on your bot service**
3. **Click "Environment" tab**
4. **Add this environment variable**:

```
NETLIFY_URL=https://your-site-name.netlify.app
```

**Replace `your-site-name.netlify.app` with your actual Netlify URL**

## 🔧 **Step 3: Redeploy Your Bot**

1. **Save the environment variable** in Render
2. **Wait for auto-redeploy** (2-5 minutes)
3. **Or manually redeploy** if needed

## 🔧 **Step 4: Test the New URLs**

1. **Upload a new file to your bot**
2. **Check the generated links** - they should now be:

```
🖥 Stream  :  https://your-site-name.netlify.app/stream.html?id=AgADLx_1150
📥 Download :  https://your-site-name.netlify.app/download.html?id=AgADLx_1150
```

## ✅ **Expected Result**

After the fix, your bot will generate:
- **Stream links** that point to your Netlify streaming page
- **Download links** that point to your Netlify download page
- **Beautiful web interface** instead of basic bot pages

## 🧪 **Test Complete Flow**

1. **Upload file to bot** → Get Netlify links
2. **Click stream link** → Opens Netlify streaming page
3. **Click download link** → Opens Netlify download page
4. **Both pages** will communicate with your bot API

## 🔍 **Troubleshooting**

### **If links still show Render URL:**
- Check if `NETLIFY_URL` environment variable is set correctly
- Verify the bot has been redeployed
- Try uploading a new file

### **If Netlify pages don't load:**
- Check if your Netlify site is deployed
- Verify the Netlify URL is correct
- Test the Netlify site directly

### **If API calls fail:**
- Ensure your bot API endpoints are working
- Check if CORS is configured correctly
- Verify the bot URL in Netlify JavaScript files

## 📋 **Quick Reference**

### **Environment Variable to Add:**
```
NETLIFY_URL=https://your-actual-netlify-url.netlify.app
```

### **Expected Link Format:**
```
Stream: https://your-site.netlify.app/stream.html?id=HASH_ID
Download: https://your-site.netlify.app/download.html?id=HASH_ID
```

### **Test Commands:**
```bash
# Test bot health
curl https://your-bot-name.onrender.com/api/health

# Test Netlify site
curl https://your-site-name.netlify.app
```

Your bot will now generate beautiful Netlify URLs instead of basic Render URLs! 🎉 