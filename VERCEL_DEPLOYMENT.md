# 🚀 Deploy to Vercel - Complete Guide

## Why Vercel?

✅ **Better CSP handling** - No more Adstera blocking issues  
✅ **Faster deployment** - Instant updates  
✅ **Better performance** - Global CDN  
✅ **Easier debugging** - Better error messages  
✅ **Free tier** - Generous limits  

## 📋 Prerequisites

1. **Node.js installed** (version 18 or higher)
2. **GitHub account** (for repository)
3. **Vercel account** (free at vercel.com)

## 🔧 Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

## 🚀 Step 2: Deploy to Vercel

### Option A: Deploy from Local Files

1. **Navigate to the web directory:**
   ```bash
   cd netlify-web
   ```

2. **Deploy to Vercel:**
   ```bash
   vercel
   ```

3. **Follow the prompts:**
   ```
   ? Set up and deploy "~/netlify-web"? [Y/n] y
   ? Which scope do you want to deploy to? [your-username]
   ? Link to existing project? [y/N] n
   ? What's your project's name? video-streamer-web
   ? In which directory is your code located? ./
   ? Want to override the settings? [y/N] n
   ```

4. **Wait for deployment** - Vercel will build and deploy your site

### Option B: Deploy from GitHub

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Add Vercel deployment"
   git push origin main
   ```

2. **Go to [vercel.com](https://vercel.com)**

3. **Click "New Project"**

4. **Import your GitHub repository**

5. **Configure settings:**
   - Framework Preset: `Other`
   - Root Directory: `netlify-web`
   - Build Command: (leave empty)
   - Output Directory: `.`

6. **Click "Deploy"**

## 🔗 Step 3: Update Your Bot

After deployment, you'll get a URL like: `https://video-streamer-web.vercel.app`

### Update Bot Environment Variables:

1. **Go to your Render dashboard**
2. **Find your bot service**
3. **Go to Environment tab**
4. **Update `NETLIFY_URL`:**
   ```
   NETLIFY_URL=https://your-project.vercel.app
   ```

### Update JavaScript Files (if needed):

If your bot URL changed, update these files:
- `js/app.js` - Line with `BOT_API_URL`
- `js/stream.js` - Line with `BOT_API_URL`  
- `js/admin.js` - Line with `BOT_API_URL`

## 🧪 Step 4: Test Everything

### Test Your Site:
1. **Visit your Vercel URL**
2. **Test video streaming**
3. **Test admin panel** (`/admin`)
4. **Test ads display**

### Test Bot Integration:
1. **Send a video to your bot**
2. **Check the generated links**
3. **Verify they point to Vercel**

## 🔧 Step 5: Custom Domain (Optional)

1. **Go to Vercel dashboard**
2. **Click on your project**
3. **Go to Settings → Domains**
4. **Add your custom domain**
5. **Update `NETLIFY_URL` in bot**

## 🛠️ Troubleshooting

### Deployment Issues:

**Error: "Build failed"**
- Check if all files are in the correct directory
- Ensure `package.json` exists
- Check Vercel build logs

**Error: "Function not found"**
- Make sure you're deploying from `netlify-web` directory
- Check `vercel.json` configuration

### CSP Issues:

**Ads still not showing:**
- Check browser console for CSP errors
- Verify `vercel.json` has correct CSP settings
- Wait for deployment to complete

### Bot Integration Issues:

**Links not working:**
- Verify `NETLIFY_URL` is updated in bot
- Check bot environment variables
- Restart bot service on Render

## 📊 Monitoring

### Vercel Analytics:
- Go to your project dashboard
- Check "Analytics" tab
- Monitor performance and errors

### Bot Logs:
- Check Render logs for API errors
- Monitor bot response times
- Verify CORS headers

## 🔄 Updates

### To update your site:
```bash
cd netlify-web
vercel --prod
```

### To update from GitHub:
- Push changes to GitHub
- Vercel auto-deploys

## 🎉 Success!

Your web interface is now on Vercel with:
- ✅ **Better performance**
- ✅ **No CSP issues**
- ✅ **Faster deployment**
- ✅ **Global CDN**
- ✅ **Working Adstera ads**

## 📞 Support

If you encounter issues:
1. **Check Vercel deployment logs**
2. **Check browser console for errors**
3. **Verify bot API is accessible**
4. **Test with a simple ad code first**

Your Adstera ads should now work perfectly! 🚀 