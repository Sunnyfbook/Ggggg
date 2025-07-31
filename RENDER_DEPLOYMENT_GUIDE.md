# Render Deployment Guide - Keep Bot Alive

## 🚀 **Solutions to Prevent Bot Sleep**

### **Solution 1: Improved Ping Mechanism**
✅ **Already implemented** - The bot now pings both main URL and health endpoint every 20 minutes

### **Solution 2: External Ping Service**
Run this on a separate service (like Railway, UptimeRobot, or your own server):

```bash
# Install requirements
pip install aiohttp

# Run the ping service
python ping_service.py
```

**Environment Variables:**
- `BOT_URL`: Your Render bot URL (e.g., https://camgrabber.onrender.com)
- `PING_INTERVAL`: Ping interval in seconds (default: 600 = 10 minutes)

### **Solution 3: UptimeRobot (Recommended)**
1. Go to [UptimeRobot](https://uptimerobot.com/)
2. Create free account
3. Add new monitor:
   - **URL**: `https://camgrabber.onrender.com/api/health`
   - **Type**: HTTP(s)
   - **Interval**: 5 minutes
   - **Alert**: Email/SMS when down

### **Solution 4: Railway Ping Service**
1. Create new Railway project
2. Add this code to `main.py`:
```python
import asyncio
import aiohttp
import os

BOT_URL = "https://camgrabber.onrender.com"

async def ping():
    async with aiohttp.ClientSession() as session:
        await session.get(f"{BOT_URL}/api/health")

async def main():
    while True:
        await ping()
        await asyncio.sleep(300)  # 5 minutes

if __name__ == "__main__":
    asyncio.run(main())
```

3. Add to `requirements.txt`:
```
aiohttp
```

### **Solution 5: GitHub Actions (Free)**
Create `.github/workflows/ping.yml`:
```yaml
name: Ping Bot
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Bot
        run: |
          curl -s https://camgrabber.onrender.com/api/health
          echo "Bot pinged at $(date)"
```

## 🔧 **Render Configuration**

### **Environment Variables to Set:**
```
PING_INTERVAL=600
PYTHON_VERSION=3.9.16
```

### **Health Check Endpoint:**
- **URL**: `https://camgrabber.onrender.com/api/health`
- **Expected Response**: `{"success": true, "status": "healthy"}`

## 📊 **Monitoring Your Bot**

### **Check Bot Status:**
```bash
# Check if bot is responding
curl https://camgrabber.onrender.com/api/health

# Check main endpoint
curl https://camgrabber.onrender.com/
```

### **Bot Logs:**
- Go to Render Dashboard
- Click on your service
- Go to "Logs" tab
- Look for ping messages every 20 minutes

## 🚨 **Troubleshooting**

### **Bot Not Responding:**
1. Check Render logs for errors
2. Verify environment variables are set
3. Check if health endpoint is accessible
4. Restart the service manually

### **Frequent Sleep:**
1. Reduce `PING_INTERVAL` to 300 (5 minutes)
2. Set up multiple ping services
3. Use UptimeRobot for external monitoring

### **Memory Issues:**
1. Check if bot is using too much memory
2. Optimize file handling
3. Consider upgrading to paid plan

## 💡 **Best Practices**

1. **Use Multiple Ping Services**: Don't rely on just one
2. **Monitor Logs**: Check Render logs regularly
3. **Set Up Alerts**: Get notified when bot goes down
4. **Backup Strategy**: Keep your code in Git
5. **Test Regularly**: Verify bot functionality

## 🔄 **Auto-Restart on Crash**

The bot now has auto-restart functionality. If it crashes, it will:
1. Log the error
2. Wait 10 seconds
3. Restart automatically

## 📈 **Performance Tips**

1. **Optimize Ping Interval**: 5-10 minutes is ideal
2. **Use Health Endpoint**: More reliable than main page
3. **Monitor Memory**: Keep an eye on resource usage
4. **Log Rotation**: Don't let logs grow too large

## 🆘 **Emergency Restart**

If bot is completely down:
1. Go to Render Dashboard
2. Click "Manual Deploy"
3. Or restart the service
4. Check logs for errors

---

**Remember**: Render's free tier has limitations. For production use, consider upgrading to a paid plan for better reliability. 