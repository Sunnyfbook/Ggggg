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
    # Fetch all ad codes from MongoDB
    from database.users_db import ads_config
    ads = await ads_config.get_ads()
    def ad_div(slot):
        return f"<div class='ad-container'>{ads.get(slot, '')}</div>"
    ad_html = (
        ad_div('top') +
        ad_div('pre_video') +
        ad_div('post_video') +
        ad_div('sidebar1') +
        ad_div('sidebar2') +
        ad_div('mobile') +
        ad_div('footer')
    )
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <title>Free Online Video Downloader</title>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
            body {{ background: #181818; color: #fff; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 500px; margin: 5em auto; background: #232323; padding: 2em; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }}
            h1 {{ text-align: center; margin-bottom: 1em; }}
            input[type=url] {{ width: 100%; padding: 0.7em; border-radius: 6px; border: none; margin-bottom: 1em; font-size: 1em; }}
            button {{ width: 100%; padding: 0.7em; border-radius: 6px; border: none; background: #4f8cff; color: #fff; font-size: 1.1em; font-weight: bold; cursor: pointer; transition: background 0.2s; }}
            button:hover {{ background: #357ae8; }}
            .info {{ margin-top: 2em; font-size: 0.95em; color: #b3b3b3; text-align: center; }}
            .ad-container {{ background: rgba(255,255,255,0.03); border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); padding: 10px; margin-bottom: 1.5em; text-align: center; }}
        </style>
    </head>
    <body>
        <div class='container'>
            {ad_html}
            <h1>Free Online Video Downloader</h1>
            <form onsubmit='return false;'>
                <input type='url' placeholder='Paste video URL here...' required disabled>
                <button disabled>Download</button>
            </form>
            <div class='info'>
                Download videos from YouTube, Facebook, Instagram, Twitter, and more!<br>
                No registration required. Fast & free.
            </div>
        </div>
        <script>
        // Loader to execute scripts injected via admin panel
        document.querySelectorAll('.ad-container').forEach(function(container) {{
            container.querySelectorAll('script').forEach(function(oldScript) {{
                const newScript = document.createElement('script');
                if (oldScript.src) {{
                    newScript.src = oldScript.src;
                }} else {{
                    newScript.textContent = oldScript.textContent;
                }}
                oldScript.parentNode.replaceChild(newScript, oldScript);
            }});
        }});
        </script>
    </body>
    </html>
    """, content_type='text/html')

@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return web.Response(text=await render_page(id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

@routes.get('/sw.js')
async def monetag_sw(request):
    with open('sw.js', 'r') as f:
        content = f.read()
    return web.Response(text=content, content_type='application/javascript')

ADS_CONFIG_PATH = 'ads_config.json'
ADMIN_PASSWORD = 'admin123'  # Change this to a secure password
AD_SLOTS = [
    'head', 'top', 'pre_video', 'post_video', 'sidebar1', 'sidebar2', 'mobile', 'footer'
]

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
            .container {{ max-width: 700px; margin: auto; background: #222; padding: 2em; border-radius: 8px; }}
            textarea {{ width: 100%; height: 100px; margin-bottom: 1em; }}
            input[type=password], button {{ padding: 0.5em; margin-top: 1em; }}
            .error {{ color: #ff4d4d; }}
            .success {{ color: #4dff4d; }}
            label {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class='container'>
            <h2>Ad Code Manager</h2>
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
                <button type='submit'>Save</button>
            </form>
            <div id='msg'></div>
        </div>
        <script>
        const AD_SLOTS = {ad_slots_js};
        async function fetchAdCodes() {{
            const res = await fetch('/api/ads');
            const data = await res.json();
            for (const slot of AD_SLOTS) {{
                document.getElementById(slot).value = data[slot] || '';
            }}
        }}
        fetchAdCodes();
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
            const msg = document.getElementById('msg');
            if (data.success) {{
                msg.innerHTML = '<span class=\"success\">Ad codes updated!</span>';
            }} else {{
                msg.innerHTML = '<span class=\"error\">' + (data.error || 'Error') + '</span>';
            }}
        }}
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
    
    if file_id.unique_id[:6] != secure_hash:
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
            
            # Generate URLs
            stream_url = f"{URL}watch/{secure_hash}_{msg_id}" if secure_hash else f"{URL}watch/{msg_id}"
            download_url = f"{URL}dl/{secure_hash}_{msg_id}" if secure_hash else f"{URL}dl/{msg_id}"
            
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

# CORS Headers for all responses
@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
