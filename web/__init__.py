from aiohttp import web
from .stream_routes import routes, cors_middleware
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from admin_api import setup_admin_routes, start_cleanup_task
from simple_admin_routes import setup_simple_admin_routes
import asyncio

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    
    # Setup simple admin routes FIRST (for testing)
    setup_simple_admin_routes(web_app)
    
    # Setup full admin routes
    await setup_admin_routes(web_app)
    
    # Then add existing routes
    web_app.add_routes(routes)
    web_app.middlewares.append(cors_middleware)
    
    # Start cleanup task for expired sessions
    asyncio.create_task(start_cleanup_task())
    
    # Debug: Print all registered routes
    print("Registered routes:")
    for route in web_app.router.routes():
        print(f"  {route.method} {route.get_info()}")
    
    return web_app

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP
