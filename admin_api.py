import json
import logging
import bcrypt
import jwt
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Secret (change this in production)
JWT_SECRET = "your-secret-key-change-in-production"

# MongoDB connection
client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]

# Collections
admin_collection = db.admins
session_collection = db.sessions
settings_collection = db.settings
stats_collection = db.stats
activity_collection = db.activities

# MongoDB Schemas (Python dict structures)
ADMIN_SCHEMA = {
    "username": str,
    "password": str,
    "email": str,
    "createdAt": datetime
}

SESSION_SCHEMA = {
    "token": str,
    "adminId": str,
    "username": str,
    "createdAt": datetime,
    "expiresAt": datetime,
    "isActive": bool
}

SETTINGS_SCHEMA = {
    "key": str,
    "value": dict,
    "createdAt": datetime,
    "updatedAt": datetime
}

STATS_SCHEMA = {
    "totalViews": int,
    "totalDownloads": int,
    "totalReactions": int,
    "activeAds": int,
    "createdAt": datetime,
    "updatedAt": datetime
}

ACTIVITY_SCHEMA = {
    "message": str,
    "type": str,
    "timestamp": datetime
}

# Session Management Functions
async def create_session(admin_id: str, username: str) -> str:
    """Create a new admin session"""
    token = jwt.encode(
        {"id": admin_id, "username": username, "exp": datetime.utcnow() + timedelta(hours=24)},
        JWT_SECRET,
        algorithm="HS256"
    )
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    session_data = {
        "token": token,
        "adminId": admin_id,
        "username": username,
        "createdAt": datetime.utcnow(),
        "expiresAt": expires_at,
        "isActive": True
    }
    
    await session_collection.insert_one(session_data)
    return token

async def validate_session(token: str) -> Optional[Dict[str, Any]]:
    """Validate an admin session"""
    try:
        # Check if session exists and is active
        session = await session_collection.find_one({
            "token": token,
            "isActive": True,
            "expiresAt": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            return None
        
        # Verify JWT token
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {"session": session, "decoded": decoded}
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return None

async def invalidate_session(token: str):
    """Invalidate an admin session"""
    await session_collection.update_one(
        {"token": token},
        {"$set": {"isActive": False}}
    )

async def cleanup_expired_sessions():
    """Clean up expired sessions"""
    await session_collection.delete_many({
        "expiresAt": {"$lt": datetime.utcnow()}
    })

# Authentication Middleware
async def authenticate_token(request: web.Request) -> Optional[Dict[str, Any]]:
    """Authentication middleware for admin routes"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else None
    if not token:
        return None
    
    return await validate_session(token)

# Helper function to update active ads count
async def update_active_ads_count():
    """Update the count of active ads based on settings"""
    try:
        active_ads_count = 0
        
        # Check banner ads
        banner_ads = await settings_collection.find_one({"key": "banner_ads"})
        if banner_ads and banner_ads.get("value"):
            value = banner_ads["value"]
            for slot in ["top", "middle", "bottom", "header", "sidebar", "footer"]:
                if value.get(slot) and value[slot].strip():
                    active_ads_count += 1
        
        # Check VAST ads
        vast_ads = await settings_collection.find_one({"key": "vast_ads"})
        if vast_ads and vast_ads.get("value"):
            value = vast_ads["value"]
            for slot in ["preRoll", "midRoll", "postRoll"]:
                if value.get(slot) and value[slot].strip():
                    active_ads_count += 1
        
        # Update stats
        await stats_collection.update_one(
            {},
            {
                "$set": {
                    "activeAds": active_ads_count,
                    "updatedAt": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.info(f'Active ads count updated: {active_ads_count}')
    except Exception as e:
        logger.error(f'Error updating active ads count: {e}')

# Admin API Routes
async def setup_admin_routes(app: web.Application):
    """Setup all admin API routes"""
    
    # Admin Authentication
    async def admin_login(request: web.Request):
        """Admin login endpoint"""
        try:
            logger.info('Login route hit')
            logger.info(f'Request headers: {dict(request.headers)}')
            
            data = await request.json()
            username = data.get('username')
            password = data.get('password')
            
            logger.info(f'Login attempt: {username}')
            
            # Check if admin exists, if not create default admin
            admin = await admin_collection.find_one({"username": username})
            if not admin:
                # Check if default admin exists
                admin = await admin_collection.find_one({"username": "admin"})
                if not admin:
                    logger.info('Creating default admin user...')
                    hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
                    admin_data = {
                        "username": "admin",
                        "password": hashed_password.decode('utf-8'),
                        "email": "admin@example.com",
                        "createdAt": datetime.utcnow()
                    }
                    result = await admin_collection.insert_one(admin_data)
                    admin = await admin_collection.find_one({"_id": result.inserted_id})
                    logger.info('Default admin created successfully')
                else:
                    logger.info('Default admin exists, but user provided different username')
                    return web.json_response({"message": "Invalid credentials"}, status=401)
            
            # Verify password
            valid_password = bcrypt.checkpw(password.encode('utf-8'), admin["password"].encode('utf-8'))
            logger.info(f'Password validation: {"success" if valid_password else "failed"}')
            
            if not valid_password:
                return web.json_response({"message": "Invalid credentials"}, status=401)
            
            # Create session
            token = await create_session(str(admin["_id"]), admin["username"])
            logger.info(f'Session created for user: {admin["username"]}')
            
            # Log activity
            await activity_collection.insert_one({
                "message": f"Admin login: {admin['username']}",
                "type": "admin_login",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({
                "token": token,
                "user": {
                    "username": admin["username"],
                    "email": admin["email"]
                }
            })
        except Exception as e:
            logger.error(f'Login error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Admin Logout
    async def admin_logout(request: web.Request):
        """Admin logout endpoint"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            token = request.headers['Authorization'].split(' ')[1]
            await invalidate_session(token)
            
            # Log activity
            await activity_collection.insert_one({
                "message": f"Admin logout: {auth_data['decoded']['username']}",
                "type": "admin_logout",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "Logged out successfully"})
        except Exception as e:
            logger.error(f'Logout error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Admin Stats
    async def get_admin_stats(request: web.Request):
        """Get admin statistics"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            stats = await stats_collection.find_one()
            if not stats:
                stats = {
                    "totalViews": 0,
                    "totalDownloads": 0,
                    "totalReactions": 0,
                    "activeAds": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                await stats_collection.insert_one(stats)
            
            # Calculate active ads based on actual settings
            await update_active_ads_count()
            
            # Get updated stats
            stats = await stats_collection.find_one()
            stats["_id"] = str(stats["_id"])  # Convert ObjectId to string
            stats["createdAt"] = stats["createdAt"].isoformat()
            stats["updatedAt"] = stats["updatedAt"].isoformat()
            
            return web.json_response(stats)
        except Exception as e:
            logger.error(f'Stats error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    async def update_stats(request: web.Request):
        """Update statistics"""
        try:
            data = await request.json()
            action = data.get('action')
            file_id = data.get('fileId')
            title = data.get('title')
            
            update_data = {"updatedAt": datetime.utcnow()}
            
            if action == 'view':
                update_data["$inc"] = {"totalViews": 1}
            elif action == 'download':
                update_data["$inc"] = {"totalDownloads": 1}
            elif action == 'reaction':
                update_data["$inc"] = {"totalReactions": 1}
            
            await stats_collection.update_one({}, update_data, upsert=True)
            return web.json_response({"message": "Stats updated"})
        except Exception as e:
            logger.error(f'Update stats error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Banner Ads Management
    async def save_banner_ads(request: web.Request):
        """Save banner ads configuration"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            
            await settings_collection.update_one(
                {"key": "banner_ads"},
                {
                    "$set": {
                        "value": data,
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Update active ads count
            await update_active_ads_count()
            
            # Log activity
            await activity_collection.insert_one({
                "message": "Banner ads updated",
                "type": "settings_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "Banner ads saved successfully"})
        except Exception as e:
            logger.error(f'Save banner ads error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # VAST Ads Management
    async def save_vast_ads(request: web.Request):
        """Save VAST ads configuration"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            
            await settings_collection.update_one(
                {"key": "vast_ads"},
                {
                    "$set": {
                        "value": data,
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Update active ads count
            await update_active_ads_count()
            
            # Log activity
            await activity_collection.insert_one({
                "message": "VAST ads updated",
                "type": "settings_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "VAST ads saved successfully"})
        except Exception as e:
            logger.error(f'Save VAST ads error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Credentials Management
    async def get_credentials(request: web.Request):
        """Get admin credentials"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            credentials = await settings_collection.find_one({"key": "admin_credentials"})
            return web.json_response(credentials.get("value", {}) if credentials else {})
        except Exception as e:
            logger.error(f'Credentials error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    async def update_credentials(request: web.Request):
        """Update admin credentials"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            
            # Hash the new password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Update admin credentials
            await admin_collection.update_one(
                {"username": "admin"},
                {
                    "$set": {
                        "username": username or "admin",
                        "password": hashed_password.decode('utf-8'),
                        "email": email or "admin@example.com"
                    }
                },
                upsert=True
            )
            
            # Save to settings as well
            await settings_collection.update_one(
                {"key": "admin_credentials"},
                {
                    "$set": {
                        "value": {
                            "username": username or "admin",
                            "email": email or "admin@example.com"
                        },
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Log activity
            await activity_collection.insert_one({
                "message": "Admin credentials updated",
                "type": "settings_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "Credentials updated successfully"})
        except Exception as e:
            logger.error(f'Update credentials error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Password Change Endpoint
    async def change_password(request: web.Request):
        """Change admin password"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            current_password = data.get('currentPassword')
            new_password = data.get('newPassword')
            
            if not current_password or not new_password:
                return web.json_response({
                    "message": "Current password and new password are required"
                }, status=400)
            
            # Get current admin credentials
            admin = await admin_collection.find_one({"username": "admin"})
            if not admin:
                return web.json_response({"message": "Admin account not found"}, status=404)
            
            # Verify current password
            is_current_password_valid = bcrypt.checkpw(
                current_password.encode('utf-8'),
                admin["password"].encode('utf-8')
            )
            if not is_current_password_valid:
                return web.json_response({"message": "Current password is incorrect"}, status=400)
            
            # Hash the new password
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Update password
            await admin_collection.update_one(
                {"username": "admin"},
                {"$set": {"password": hashed_new_password.decode('utf-8')}}
            )
            
            # Log activity
            await activity_collection.insert_one({
                "message": "Admin password changed",
                "type": "security_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "Password changed successfully"})
        except Exception as e:
            logger.error(f'Password change error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Ads Management
    async def get_ads_settings(request: web.Request):
        """Get ads settings"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            # Check for ads_settings first (new format)
            ads_settings = await settings_collection.find_one({"key": "ads_settings"})
            
            if not ads_settings:
                # Try to combine old format keys
                banner_ads = await settings_collection.find_one({"key": "banner_ads"})
                vast_ads = await settings_collection.find_one({"key": "vast_ads"})
                
                if banner_ads or vast_ads:
                    combined_settings = {
                        "banner": banner_ads.get("value", {}) if banner_ads else {},
                        "vast": vast_ads.get("value", {}) if vast_ads else {}
                    }
                    return web.json_response(combined_settings)
            
            return web.json_response(ads_settings.get("value", {}) if ads_settings else {})
        except Exception as e:
            logger.error(f'Ads settings error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Reactions Management
    async def get_reactions_settings(request: web.Request):
        """Get reactions settings"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            reactions_settings = await settings_collection.find_one({"key": "reactions_settings"})
            return web.json_response(reactions_settings.get("value", {}) if reactions_settings else {})
        except Exception as e:
            logger.error(f'Reactions settings error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    async def save_reactions_settings(request: web.Request):
        """Save reactions settings"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            
            await settings_collection.update_one(
                {"key": "reactions_settings"},
                {
                    "$set": {
                        "value": data,
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Log activity
            await activity_collection.insert_one({
                "message": "Reactions updated",
                "type": "settings_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "Reactions saved successfully"})
        except Exception as e:
            logger.error(f'Save reactions error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # API Settings Management
    async def get_api_settings(request: web.Request):
        """Get API settings"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            api_settings = await settings_collection.find_one({"key": "api_settings"})
            return web.json_response(api_settings.get("value", {}) if api_settings else {})
        except Exception as e:
            logger.error(f'API settings error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    async def save_api_settings(request: web.Request):
        """Save API settings"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            api_base_url = data.get('apiBaseUrl')
            api_key = data.get('apiKey')
            server_port = data.get('serverPort')
            environment = data.get('environment')
            
            # Validate API Base URL
            if not api_base_url or not api_base_url.startswith('http'):
                return web.json_response({
                    "message": "Invalid API Base URL. Must start with http:// or https://"
                }, status=400)
            
            await settings_collection.update_one(
                {"key": "api_settings"},
                {
                    "$set": {
                        "value": {
                            "apiBaseUrl": api_base_url,
                            "apiKey": api_key,
                            "serverPort": server_port,
                            "environment": environment
                        },
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Log activity
            await activity_collection.insert_one({
                "message": f"API settings updated - Base URL: {api_base_url}",
                "type": "settings_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "API settings saved successfully"})
        except Exception as e:
            logger.error(f'Save API settings error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Server Settings Management
    async def get_server_settings(request: web.Request):
        """Get server settings"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            server_settings = await settings_collection.find_one({"key": "server_settings"})
            return web.json_response(server_settings.get("value", {}) if server_settings else {})
        except Exception as e:
            logger.error(f'Server settings error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    async def save_server_settings(request: web.Request):
        """Save server settings"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            
            await settings_collection.update_one(
                {"key": "server_settings"},
                {
                    "$set": {
                        "value": data,
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Log activity
            await activity_collection.insert_one({
                "message": "Server settings updated",
                "type": "settings_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "Server settings saved successfully"})
        except Exception as e:
            logger.error(f'Save server settings error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Metadata Management
    async def get_metadata(request: web.Request):
        """Get website metadata"""
        try:
            metadata = await settings_collection.find_one({"key": "website_metadata"})
            return web.json_response(metadata.get("value", {}) if metadata else {})
        except Exception as e:
            logger.error(f'Metadata settings error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    async def save_metadata(request: web.Request):
        """Save website metadata"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            
            await settings_collection.update_one(
                {"key": "website_metadata"},
                {
                    "$set": {
                        "value": data,
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Log activity
            await activity_collection.insert_one({
                "message": "Website metadata updated",
                "type": "settings_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "Metadata saved successfully"})
        except Exception as e:
            logger.error(f'Save metadata error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Page Titles Management
    async def get_page_titles(request: web.Request):
        """Get page titles"""
        try:
            page_titles = await settings_collection.find_one({"key": "page_titles"})
            return web.json_response(page_titles.get("value", {}) if page_titles else {})
        except Exception as e:
            logger.error(f'Page titles error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    async def save_page_titles(request: web.Request):
        """Save page titles"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            data = await request.json()
            
            await settings_collection.update_one(
                {"key": "page_titles"},
                {
                    "$set": {
                        "value": data,
                        "updatedAt": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Log activity
            await activity_collection.insert_one({
                "message": "Page titles updated",
                "type": "settings_update",
                "timestamp": datetime.utcnow()
            })
            
            return web.json_response({"message": "Page titles saved successfully"})
        except Exception as e:
            logger.error(f'Save page titles error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Activity Logs
    async def get_activity_logs(request: web.Request):
        """Get activity logs"""
        try:
            auth_data = await authenticate_token(request)
            if not auth_data:
                return web.json_response({"message": "Unauthorized"}, status=401)
            
            activities = await activity_collection.find().sort("timestamp", -1).limit(50).to_list(50)
            
            # Convert ObjectId to string and datetime to ISO format
            for activity in activities:
                activity["_id"] = str(activity["_id"])
                activity["timestamp"] = activity["timestamp"].isoformat()
            
            return web.json_response(activities)
        except Exception as e:
            logger.error(f'Activity logs error: {e}')
            return web.json_response({"message": "Server error"}, status=500)

    # Test endpoint
    async def test_endpoint(request: web.Request):
        """Test endpoint to check admin existence"""
        try:
            admin = await admin_collection.find_one({"username": "admin"})
            return web.json_response({
                "adminExists": bool(admin),
                "message": "Admin exists" if admin else "No admin found"
            })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    # Add routes to the app
    app.router.add_post('/api/admin/login', admin_login)
    app.router.add_post('/api/admin/logout', admin_logout)
    app.router.add_get('/api/admin/stats', get_admin_stats)
    app.router.add_post('/api/admin/stats', update_stats)
    app.router.add_post('/api/admin/ads/banner', save_banner_ads)
    app.router.add_post('/api/admin/ads/vast', save_vast_ads)
    app.router.add_get('/api/admin/credentials', get_credentials)
    app.router.add_post('/api/admin/credentials', update_credentials)
    app.router.add_post('/api/admin/credentials/password', change_password)
    app.router.add_get('/api/admin/ads', get_ads_settings)
    app.router.add_get('/api/admin/reactions', get_reactions_settings)
    app.router.add_post('/api/admin/reactions', save_reactions_settings)
    app.router.add_get('/api/admin/api', get_api_settings)
    app.router.add_post('/api/admin/api', save_api_settings)
    app.router.add_get('/api/admin/server', get_server_settings)
    app.router.add_post('/api/admin/server', save_server_settings)
    app.router.add_get('/api/admin/metadata', get_metadata)
    app.router.add_post('/api/admin/metadata', save_metadata)
    app.router.add_get('/api/admin/page_titles', get_page_titles)
    app.router.add_post('/api/admin/page_titles', save_page_titles)
    app.router.add_get('/api/admin/activity', get_activity_logs)
    app.router.add_get('/api/admin/test', test_endpoint)

# Cleanup expired sessions every hour
async def start_cleanup_task():
    """Start the cleanup task for expired sessions"""
    while True:
        await asyncio.sleep(3600)  # 1 hour
        await cleanup_expired_sessions()

# Export functions
__all__ = [
    'setup_admin_routes',
    'create_session',
    'validate_session',
    'invalidate_session',
    'cleanup_expired_sessions',
    'authenticate_token',
    'update_active_ads_count',
    'start_cleanup_task'
] 