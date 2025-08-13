"""
Simple Admin Routes for CamGrabber
This is a simplified version to test if the admin routes work
"""

import json
import logging
from aiohttp import web
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_simple_admin_routes(app):
    """Setup simple admin routes for testing"""
    
    async def simple_admin_login(request):
        """Simple admin login endpoint"""
        try:
            logger.info("Simple admin login endpoint hit")
            
            # Check if it's a POST request
            if request.method != 'POST':
                return web.json_response({
                    "error": "Method not allowed",
                    "message": "Only POST method is allowed"
                }, status=405)
            
            data = await request.json()
            username = data.get('username')
            password = data.get('password')
            
            logger.info(f"Login attempt for username: {username}")
            
            # Simple validation
            if username == "admin" and password == "admin123":
                return web.json_response({
                    "success": True,
                    "message": "Login successful",
                    "token": "test_token_123",
                    "user": {
                        "username": "admin",
                        "email": "admin@example.com"
                    }
                })
            else:
                return web.json_response({
                    "success": False,
                    "message": "Invalid credentials"
                }, status=401)
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return web.json_response({
                "error": "Server error",
                "message": str(e)
            }, status=500)
    
    async def simple_admin_test(request):
        """Simple admin test endpoint"""
        return web.json_response({
            "message": "Simple admin API is working!",
            "timestamp": datetime.now().isoformat(),
            "endpoint": "/api/admin/simple-login"
        })
    
    async def simple_admin_stats(request):
        """Simple admin stats endpoint"""
        return web.json_response({
            "totalViews": 0,
            "totalDownloads": 0,
            "totalReactions": 0,
            "activeAds": 0,
            "message": "Simple stats endpoint working"
        })
    
    # Add routes
    app.router.add_post('/api/admin/simple-login', simple_admin_login)
    app.router.add_get('/api/admin/simple-test', simple_admin_test)
    app.router.add_get('/api/admin/simple-stats', simple_admin_stats)
    
    logger.info("Simple admin routes added successfully!")
    return app 