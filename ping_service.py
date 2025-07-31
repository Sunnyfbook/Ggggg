#!/usr/bin/env python3
"""
External Ping Service for Render Bot
This script pings your bot to keep it alive on Render's free tier
"""

import asyncio
import aiohttp
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Your bot's URL - replace with your actual Render URL
BOT_URL = os.getenv('BOT_URL', 'https://camgrabber.onrender.com')
PING_INTERVAL = int(os.getenv('PING_INTERVAL', '600'))  # 10 minutes

async def ping_bot():
    """Ping the bot to keep it alive"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # Ping main endpoint
            async with session.get(f"{BOT_URL}/") as resp:
                logging.info(f"Main endpoint ping: {resp.status}")
            
            # Ping health endpoint
            async with session.get(f"{BOT_URL}/api/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logging.info(f"Health check: {data.get('status', 'unknown')} - Uptime: {data.get('uptime', 'unknown')}")
                else:
                    logging.warning(f"Health check failed: {resp.status}")
                    
    except Exception as e:
        logging.error(f"Ping failed: {e}")

async def main():
    """Main ping loop"""
    logging.info(f"Starting ping service for {BOT_URL}")
    logging.info(f"Ping interval: {PING_INTERVAL} seconds")
    
    while True:
        await ping_bot()
        await asyncio.sleep(PING_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Ping service stopped") 