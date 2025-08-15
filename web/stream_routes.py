import re, math, logging, secrets, mimetypes, time, json
from info import *
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from web.server import multi_clients, work_loads, Webavbot
from web.server.exceptions import FIleNotFound, InvalidHash
from web.utils.custom_dl import ByteStreamer
from utils import get_readable_time
from web.utils import StartTime, __version__
from web.utils.render_template import render_page
from database.users_db import ads_config
from web.utils.file_properties import get_file_ids, get_hash
from pyrogram.types import Message

routes = web.RouteTableDef()

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

@routes.get("/", allow_head=True)
async def root_route_handler(_):
    """API-only endpoint - web interface moved to Netlify"""
    return web.json_response({
        "message": "API Server Running",
        "status": "healthy",
        "web_interface": "https://your-site-name.netlify.app"
    })

@routes.get("/topics")
async def topics_page_handler(_):
    """Serve the topics viewer page"""
    try:
        with open('web/template/topics.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return web.Response(text=content, content_type='text/html')
    except FileNotFoundError:
        return web.Response(status=404, text="Topics page not found")

# Web interface routes removed - moved to Netlify
# Only API endpoints remain for Netlify to use

@routes.get('/sw.js')
async def monetag_sw(request):
    with open('sw.js', 'r') as f:
        content = f.read()
    return web.Response(text=content, content_type='application/javascript')

ADS_CONFIG_PATH = 'ads_config.json'
SETTINGS_CONFIG_PATH = 'site_settings.json'
ADMIN_PASSWORD = 'admin123'  # Change this to a secure password
AD_SLOTS = [
    'head', 'top', 'pre_video', 'post_video', 'sidebar1', 'sidebar2', 'mobile', 'footer'
]

# New comprehensive ad slots for the admin panel
ADMIN_AD_SLOTS = [
    'ads_preroll', 'ads_top', 'ads_video_preroll', 'ads_video_overlay', 
    'ads_video_postroll', 'ads_middle', 'ads_post_reactions', 'ads_sidebar', 
    'ads_bottom', 'ads_footer'
]

# Helper to load site settings
async def load_site_settings():
    try:
        with open(SETTINGS_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {
            'site_name': 'Video Streamer',
            'footer_text': '© 2024 Video Downloader. All rights reserved.',
            'primary_color': '#667eea',
            'accent_color': '#f093fb',
            'ads_preroll': '',
            'ads_top': '',
            'ads_video_preroll': '',
            'ads_video_overlay': '',
            'ads_video_postroll': '',
            'ads_middle': '',
            'ads_post_reactions': '',
            'ads_sidebar': '',
            'ads_bottom': '',
            'ads_footer': ''
        }

# Helper to save site settings
async def save_site_settings(data):
    with open(SETTINGS_CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)

# Helper to load ad codes
async def load_ads_config():
    try:
        with open(ADS_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {slot: '' for slot in AD_SLOTS}

# Helper to save ad codes
async def save_ads_config(data):
    with open(ADS_CONFIG_PATH, 'w') as f:
        json.dump(data, f)

# New API endpoint to get all site settings
@routes.get('/api/settings')
async def get_site_settings(request):
    settings = await load_site_settings()
    return web.json_response(settings)

# New API endpoint to update site settings
@routes.post('/api/settings')
async def update_site_settings(request):
    try:
        data = await request.json()
        password = data.get('password')
        
        if password != ADMIN_PASSWORD:
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        # Load current settings
        current_settings = await load_site_settings()
        
        # Update with new data
        for key in ['site_name', 'footer_text', 'primary_color', 'accent_color'] + ADMIN_AD_SLOTS:
            if key in data:
                current_settings[key] = data[key]
        
        # Save updated settings
        await save_site_settings(current_settings)
        
        return web.json_response({
            'success': True,
            'message': 'Settings saved successfully'
        })
        
    except Exception as e:
        return web.json_response({
            'error': f'Failed to save settings: {str(e)}'
        }, status=500)

@routes.get('/api/ads')
async def get_ads(request):
    ads = await ads_config.get_ads()
    # Remove _id if present
    ads.pop('_id', None)
    return web.json_response(ads)

@routes.post('/api/ads')
async def update_ads(request):
    data = await request.json()
    password = data.get('password')
    if password != ADMIN_PASSWORD:
        return web.json_response({'error': 'Unauthorized'}, status=401)
    update_data = {slot: data.get(slot, '') for slot in AD_SLOTS}
    await ads_config.update_ads(update_data)
    return web.json_response({'success': True})

@routes.get('/admin')
async def admin_panel(request):
    ad_slots = ['head', 'top', 'pre_video', 'post_video', 'sidebar1', 'sidebar2', 'mobile', 'footer']
    ad_slots_js = str(ad_slots)  # outputs a valid JS array
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <title>Admin Panel - Ad Code Manager</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #181818; color: #fff; padding: 2em; }}
            .container {{ max-width: 1200px; margin: auto; background: #222; padding: 2em; border-radius: 8px; }}
            .tabs {{ display: flex; margin-bottom: 2em; }}
            .tab {{ padding: 1em 2em; background: #333; cursor: pointer; margin-right: 0.5em; border-radius: 4px; }}
            .tab.active {{ background: #667eea; }}
            .tab-content {{ display: none; }}
            .tab-content.active {{ display: block; }}
            textarea {{ width: 100%; height: 100px; margin-bottom: 1em; }}
            input[type=password], input[type=text], button {{ padding: 0.5em; margin-top: 1em; }}
            .error {{ color: #ff4d4d; }}
            .success {{ color: #4dff4d; }}
            label {{ font-weight: bold; }}
            .topic-item {{ background: #333; padding: 1em; margin: 1em 0; border-radius: 4px; }}
            .topic-title {{ font-weight: bold; color: #667eea; }}
            .topic-info {{ color: #ccc; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class='container'>
            <h2>Admin Panel</h2>
            
            <div class='tabs'>
                <div class='tab active' onclick='showTab("ads")'>Ad Manager</div>
                <div class='tab' onclick='showTab("topics")'>Group Topics</div>
            </div>
            
            <div id='ads' class='tab-content active'>
                <h3>Ad Code Manager</h3>
                <form id='adForm'>
                    <label for='head'>Head (for scripts in &lt;head&gt;):</label><br>
                    <textarea id='head' name='head'></textarea><br>
                    <label for='top'>Top Banner Ad:</label><br>
                    <textarea id='top' name='top'></textarea><br>
                    <label for='pre_video'>Pre-Video Ad:</label><br>
                    <textarea id='pre_video' name='pre_video'></textarea><br>
                    <label for='post_video'>Post-Video Ad:</label><br>
                    <textarea id='post_video' name='post_video'></textarea><br>
                    <label for='sidebar1'>Sidebar Ad 1:</label><br>
                    <textarea id='sidebar1' name='sidebar1'></textarea><br>
                    <label for='sidebar2'>Sidebar Ad 2:</label><br>
                    <textarea id='sidebar2' name='sidebar2'></textarea><br>
                    <label for='mobile'>Mobile Bottom Ad:</label><br>
                    <textarea id='mobile' name='mobile'></textarea><br>
                    <label for='footer'>Footer Ad:</label><br>
                    <textarea id='footer' name='footer'></textarea><br>
                    <label for='password'>Password:</label><br>
                    <input type='password' id='password' name='password'><br>
                    <button type='submit'>Save Ads</button>
                </form>
                <div id='adMsg'></div>
            </div>
            
            <div id='topics' class='tab-content'>
                <h3>Group Topics Manager</h3>
                <div>
                    <label for='groupId'>Group ID:</label><br>
                    <input type='text' id='groupId' placeholder='-1001234567890'><br>
                    <button onclick='fetchTopics()'>Fetch Topics</button>
                    <button onclick='clearTopics()'>Clear All Topics</button>
                </div>
                <div id='topicsList'></div>
                <div id='topicMsg'></div>
            </div>
        </div>
        
        <script>
        const AD_SLOTS = {ad_slots_js};
        
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // Ad Manager Functions
        async function fetchAdCodes() {{
            const res = await fetch('/api/ads');
            const data = await res.json();
            for (const slot of AD_SLOTS) {{
                document.getElementById(slot).value = data[slot] || '';
            }}
        }}
        
        document.getElementById('adForm').onsubmit = async function(e) {{
            e.preventDefault();
            const password = document.getElementById('password').value;
            let body = {{ password }};
            for (const slot of AD_SLOTS) {{
                body[slot] = document.getElementById(slot).value;
            }}
            const res = await fetch('/api/ads', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(body)
            }});
            const data = await res.json();
            const msg = document.getElementById('adMsg');
            if (data.success) {{
                msg.innerHTML = '<span class=\"success\">Ad codes updated!</span>';
            }} else {{
                msg.innerHTML = '<span class=\"error\">' + (data.error || 'Error') + '</span>';
            }}
        }}
        
        // Topics Manager Functions
        async function fetchTopics() {{
            const groupId = document.getElementById('groupId').value;
            if (!groupId) {{
                document.getElementById('topicMsg').innerHTML = '<span class=\"error\">Please enter a group ID</span>';
                return;
            }}
            
            try {{
                const res = await fetch(`/api/topics/group/${{groupId}}`);
                const data = await res.json();
                
                if (data.success) {{
                    displayTopics(data.topics);
                    document.getElementById('topicMsg').innerHTML = '<span class=\"success\">Topics loaded successfully!</span>';
                }} else {{
                    document.getElementById('topicMsg').innerHTML = '<span class=\"error\">' + data.error + '</span>';
                }}
            }} catch (error) {{
                document.getElementById('topicMsg').innerHTML = '<span class=\"error\">Error fetching topics</span>';
            }}
        }}
        
        function displayTopics(topics) {{
            const container = document.getElementById('topicsList');
            if (topics.length === 0) {{
                container.innerHTML = '<p>No topics found</p>';
                return;
            }}
            
            let html = '<h4>Found Topics:</h4>';
            topics.forEach(topic => {{
                html += `
                    <div class='topic-item'>
                        <div class='topic-title'>${{topic.topic_name}}</div>
                        <div class='topic-info'>
                            ID: ${{topic.topic_id}} | Videos: ${{topic.video_count}} | Date: ${{topic.processed_at}}
                        </div>
                        <div class='topic-info'>Title: ${{topic.title}}</div>
                    </div>
                `;
            }});
            container.innerHTML = html;
        }}
        
        async function clearTopics() {{
            if (confirm('Are you sure you want to clear all topics?')) {{
                try {{
                    const res = await fetch('/api/topics/clear', {{ method: 'POST' }});
                    const data = await res.json();
                    
                    if (data.success) {{
                        document.getElementById('topicMsg').innerHTML = '<span class=\"success\">All topics cleared!</span>';
                        document.getElementById('topicsList').innerHTML = '';
                    }} else {{
                        document.getElementById('topicMsg').innerHTML = '<span class=\"error\">' + data.error + '</span>';
                    }}
                }} catch (error) {{
                    document.getElementById('topicMsg').innerHTML = '<span class=\"error\">Error clearing topics</span>';
                }}
            }}
        }}
        
        // Initialize
        fetchAdCodes();
        </script>
    </body>
    </html>
    """, content_type='text/html')

class_cache = {}

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("after calling get_file_properties")
    
    # Verify hash if provided
    if secure_hash and file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
  )
#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

# Streaming and Download Routes for Netlify Integration

@routes.get("/watch/{file_id}")
async def watch_file(request):
    """Stream video files"""
    try:
        file_id = request.match_info["file_id"]
        
        # Parse file ID and hash
        if "_" in file_id:
            # Format: hash_id (e.g., abc123_123456)
            parts = file_id.split("_")
            if len(parts) == 2:
                secure_hash, msg_id = parts
                msg_id = int(msg_id)
            else:
                return web.Response(status=404, text="Invalid file ID format")
        else:
            # Format: just ID
            msg_id = int(file_id)
            secure_hash = None
        
        # Get file info from BIN_CHANNEL
        try:
            index = min(work_loads, key=work_loads.get)
            faster_client = multi_clients[index]
            
            message = await faster_client.get_messages(BIN_CHANNEL, msg_id)
            if not message:
                return web.Response(status=404, text="File not found")
            
            # Get file properties
            file_props = await get_file_ids(faster_client, BIN_CHANNEL, msg_id)
            if not file_props:
                return web.Response(status=404, text="File properties not found")
            
            # Verify hash if provided
            if secure_hash and file_props.unique_id[:6] != secure_hash:
                return web.Response(status=404, text="Invalid file hash")
            
            # Stream the file
            return await media_streamer(request, msg_id, secure_hash or file_props.unique_id[:6])
            
        except Exception as e:
            logging.error(f"Error streaming file: {e}")
            return web.Response(status=500, text="Internal server error")
            
    except Exception as e:
        logging.error(f"Watch route error: {e}")
        return web.Response(status=400, text="Invalid request")

@routes.get("/dl/{file_id}")
async def download_file(request):
    """Download files"""
    try:
        file_id = request.match_info["file_id"]
        
        # Parse file ID and hash
        if "_" in file_id:
            # Format: hash_id (e.g., abc123_123456)
            parts = file_id.split("_")
            if len(parts) == 2:
                secure_hash, msg_id = parts
                msg_id = int(msg_id)
            else:
                return web.Response(status=404, text="Invalid file ID format")
        else:
            # Format: just ID
            msg_id = int(file_id)
            secure_hash = None
        
        # Get file info from BIN_CHANNEL
        try:
            index = min(work_loads, key=work_loads.get)
            faster_client = multi_clients[index]
            
            message = await faster_client.get_messages(BIN_CHANNEL, msg_id)
            if not message:
                return web.Response(status=404, text="File not found")
            
            # Get file properties
            file_props = await get_file_ids(faster_client, BIN_CHANNEL, msg_id)
            if not file_props:
                return web.Response(status=404, text="File properties not found")
            
            # Verify hash if provided
            if secure_hash and file_props.unique_id[:6] != secure_hash:
                return web.Response(status=404, text="Invalid file hash")
            
            # Download the file
            return await media_streamer(request, msg_id, secure_hash or file_props.unique_id[:6])
            
        except Exception as e:
            logging.error(f"Error downloading file: {e}")
            return web.Response(status=500, text="Internal server error")
            
    except Exception as e:
        logging.error(f"Download route error: {e}")
        return web.Response(status=400, text="Invalid request")

# API Endpoints for Netlify Integration

@routes.get("/api/file/{file_id}")
async def get_file_info_api(request):
    """Get file information for API requests"""
    try:
        file_id = request.match_info["file_id"]
        
        # Parse file ID and hash
        if "_" in file_id:
            # Format: hash_id (e.g., abc123_123456)
            parts = file_id.split("_")
            if len(parts) == 2:
                secure_hash = parts[0]
                msg_id = int(parts[1])
            else:
                raise web.HTTPBadRequest(text="Invalid file ID format")
        else:
            # Try to extract from numeric ID
            try:
                msg_id = int(file_id)
                secure_hash = None
            except ValueError:
                raise web.HTTPBadRequest(text="Invalid file ID")
        
        # Get file information
        index = min(work_loads, key=work_loads.get)
        faster_client = multi_clients[index]
        
        try:
            message = await faster_client.get_messages(BIN_CHANNEL, msg_id)
            if message.empty:
                raise FIleNotFound("File not found")
            
            # Get file properties
            file_props = await get_file_ids(faster_client, BIN_CHANNEL, msg_id)
            
            # Verify hash if provided
            if secure_hash and file_props.unique_id[:6] != secure_hash:
                raise InvalidHash("Invalid file hash")
            
            # Get file size
            file_size = getattr(file_props, 'file_size', 0)
            file_name = getattr(file_props, 'file_name', 'Unknown File')
            mime_type = getattr(file_props, 'mime_type', 'application/octet-stream')
            
            # Determine file type
            if mime_type.startswith('video/'):
                file_type = 'video'
            elif mime_type.startswith('audio/'):
                file_type = 'audio'
            elif mime_type.startswith('image/'):
                file_type = 'image'
            else:
                file_type = 'document'
            
            # Generate URLs - use bot's Render URL for actual video content
            bot_url = "https://camgrabber.onrender.com"
            stream_url = f"{bot_url}/watch/{secure_hash}_{msg_id}" if secure_hash else f"{bot_url}/watch/{msg_id}"
            download_url = f"{bot_url}/dl/{secure_hash}_{msg_id}" if secure_hash else f"{bot_url}/dl/{msg_id}"
            
            return web.json_response({
                "success": True,
                "file_id": f"{secure_hash}_{msg_id}" if secure_hash else str(msg_id),
                "file_name": file_name,
                "file_size": file_size,
                "file_type": mime_type,
                "file_category": file_type,
                "duration": getattr(file_props, 'duration', 0),
                "quality": "HD" if file_size > 10 * 1024 * 1024 else "SD",  # 10MB threshold
                "date": message.date.isoformat() if message.date else None,
                "stream_url": stream_url,
                "download_url": download_url
            })
            
        except (FIleNotFound, InvalidHash) as e:
            return web.json_response({
                "success": False,
                "error": str(e),
                "code": 404
            }, status=404)
        except Exception as e:
            logging.error(f"Error getting file info: {e}")
            return web.json_response({
                "success": False,
                "error": "Internal server error",
                "code": 500
            }, status=500)
            
    except Exception as e:
        logging.error(f"API error: {e}")
        return web.json_response({
            "success": False,
            "error": "Invalid request",
            "code": 400
        }, status=400)

@routes.post("/api/process")
async def process_url_api(request):
    """Process URL and return file information"""
    try:
        data = await request.json()
        url = data.get("url")
        
        if not url:
            return web.json_response({
                "success": False,
                "error": "URL is required",
                "code": 400
            }, status=400)
        
        # For now, this endpoint returns a placeholder response
        # You can extend this to actually process URLs and download files
        return web.json_response({
            "success": True,
            "message": "URL processing is not implemented yet. Please upload files directly to the bot.",
            "file_id": None,
            "download_links": [],
            "stream_url": None
        })
        
    except Exception as e:
        logging.error(f"Process URL error: {e}")
        return web.json_response({
            "success": False,
            "error": "Failed to process URL",
            "code": 500
        }, status=500)

@routes.get("/api/health")
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "success": True,
        "status": "healthy",
        "version": __version__,
        "uptime": get_readable_time(time.time() - StartTime)
    })

# Group Topics API Endpoints

@routes.get("/api/topics")
async def get_all_topics_api(request):
    """Get all stored topics"""
    try:
        limit = int(request.query.get('limit', 50))
        topics = await db.get_all_topics(limit)
        
        # Format topics for API response
        formatted_topics = []
        for topic in topics:
            formatted_topic = {
                "topic_id": topic["topic_id"],
                "topic_name": topic["topic_name"],
                "group_id": topic["group_id"],
                "title": topic.get("title", ""),
                "thumbnail": topic.get("thumbnail", ""),
                "video_count": len(topic.get("videos", [])),
                "processed_at": topic.get("processed_at", ""),
                "videos": []
            }
            
            # Add video information
            for video in topic.get("videos", []):
                video_info = {
                    "message_id": video["message_id"],
                    "file_name": video["file_name"],
                    "file_size": video["file_size"],
                    "duration": video["duration"],
                    "caption": video["caption"],
                    "stream_url": f"/watch/{video['message_id']}",
                    "download_url": f"/dl/{video['message_id']}"
                }
                formatted_topic["videos"].append(video_info)
            
            formatted_topics.append(formatted_topic)
        
        return web.json_response({
            "success": True,
            "topics": formatted_topics,
            "total": len(formatted_topics)
        })
        
    except Exception as e:
        logging.error(f"Error getting topics: {e}")
        return web.json_response({
            "success": False,
            "error": "Failed to fetch topics",
            "code": 500
        }, status=500)

@routes.get("/api/topics/{topic_id}")
async def get_topic_by_id_api(request):
    """Get a specific topic by ID"""
    try:
        topic_id = int(request.match_info["topic_id"])
        group_id = int(request.query.get('group_id', 0))
        
        if not group_id:
            return web.json_response({
                "success": False,
                "error": "group_id parameter is required",
                "code": 400
            }, status=400)
        
        topic = await db.get_topic(topic_id, group_id)
        
        if not topic:
            return web.json_response({
                "success": False,
                "error": "Topic not found",
                "code": 404
            }, status=404)
        
        # Format topic for API response
        formatted_topic = {
            "topic_id": topic["topic_id"],
            "topic_name": topic["topic_name"],
            "group_id": topic["group_id"],
            "title": topic.get("title", ""),
            "thumbnail": topic.get("thumbnail", ""),
            "processed_at": topic.get("processed_at", ""),
            "videos": []
        }
        
        # Add video information with URLs
        for video in topic.get("videos", []):
            video_info = {
                "message_id": video["message_id"],
                "file_name": video["file_name"],
                "file_size": video["file_size"],
                "duration": video["duration"],
                "caption": video["caption"],
                "stream_url": f"/watch/{video['message_id']}",
                "download_url": f"/dl/{video['message_id']}"
            }
            formatted_topic["videos"].append(video_info)
        
        return web.json_response({
            "success": True,
            "topic": formatted_topic
        })
        
    except ValueError:
        return web.json_response({
            "success": False,
            "error": "Invalid topic_id or group_id",
            "code": 400
        }, status=400)
    except Exception as e:
        logging.error(f"Error getting topic: {e}")
        return web.json_response({
            "success": False,
            "error": "Failed to fetch topic",
            "code": 500
        }, status=500)

@routes.get("/api/topics/group/{group_id}")
async def get_topics_by_group_api(request):
    """Get all topics from a specific group"""
    try:
        group_id = int(request.match_info["group_id"])
        limit = int(request.query.get('limit', 20))
        
        topics = await db.get_topics_by_group(group_id, limit)
        
        # Format topics for API response
        formatted_topics = []
        for topic in topics:
            formatted_topic = {
                "topic_id": topic["topic_id"],
                "topic_name": topic["topic_name"],
                "group_id": topic["group_id"],
                "title": topic.get("title", ""),
                "thumbnail": topic.get("thumbnail", ""),
                "video_count": len(topic.get("videos", [])),
                "processed_at": topic.get("processed_at", "")
            }
            formatted_topics.append(formatted_topic)
        
        return web.json_response({
            "success": True,
            "topics": formatted_topics,
            "total": len(formatted_topics),
            "group_id": group_id
        })
        
    except ValueError:
        return web.json_response({
            "success": False,
            "error": "Invalid group_id",
            "code": 400
        }, status=400)
    except Exception as e:
        logging.error(f"Error getting group topics: {e}")
        return web.json_response({
            "success": False,
            "error": "Failed to fetch group topics",
            "code": 500
        }, status=500)

@routes.get("/api/topics/{topic_id}/thumbnail")
async def get_topic_thumbnail_api(request):
    """Get thumbnail for a specific topic"""
    try:
        topic_id = int(request.match_info["topic_id"])
        group_id = int(request.query.get('group_id', 0))
        
        if not group_id:
            return web.json_response({
                "success": False,
                "error": "group_id parameter is required",
                "code": 400
            }, status=400)
        
        topic = await db.get_topic(topic_id, group_id)
        
        if not topic or not topic.get("thumbnail"):
            return web.json_response({
                "success": False,
                "error": "Thumbnail not found",
                "code": 404
            }, status=404)
        
        # Get the thumbnail file from Telegram
        try:
            index = min(work_loads, key=work_loads.get)
            faster_client = multi_clients[index]
            
            # Download and serve the thumbnail
            file = await faster_client.download_media(topic["thumbnail"])
            
            with open(file, 'rb') as f:
                content = f.read()
            
            return web.Response(
                body=content,
                content_type='image/jpeg',
                headers={
                    'Content-Disposition': f'inline; filename="thumbnail_{topic_id}.jpg"'
                }
            )
            
        except Exception as e:
            logging.error(f"Error serving thumbnail: {e}")
            return web.json_response({
                "success": False,
                "error": "Failed to serve thumbnail",
                "code": 500
            }, status=500)
        
    except ValueError:
        return web.json_response({
            "success": False,
            "error": "Invalid topic_id or group_id",
            "code": 400
        }, status=400)
    except Exception as e:
        logging.error(f"Error getting thumbnail: {e}")
        return web.json_response({
            "success": False,
            "error": "Failed to fetch thumbnail",
            "code": 500
        }, status=500)

@routes.post("/api/topics/clear")
async def clear_all_topics_api(request):
    """Clear all topics from database"""
    try:
        deleted_count = await db.clear_all_topics()
        return web.json_response({
            "success": True,
            "message": f"Cleared {deleted_count} topics",
            "deleted_count": deleted_count
        })
    except Exception as e:
        logging.error(f"Error clearing topics: {e}")
        return web.json_response({
            "success": False,
            "error": "Failed to clear topics",
            "code": 500
        }, status=500)

# CORS Headers for all responses
@web.middleware
async def cors_middleware(request, handler):
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = web.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
    
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
