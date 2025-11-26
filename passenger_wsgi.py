import os
import sys
import asyncio
import threading
from asgiref.wsgi import AsgiToWsgi

# Add the project directory to the Python path to ensure all modules are importable.
sys.path.insert(0, os.path.dirname(__file__))

# Import the bot's web server and startup function
from web import web_server
from bot import start as start_bot

def run_bot_loop():
    """Creates a new event loop for the bot and runs its startup logic."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

# Run the bot in a background thread.
# This is necessary because the bot is a long-running process.
bot_thread = threading.Thread(target=run_bot_loop)
bot_thread.daemon = True
bot_thread.start()

# The web server will be managed by the cPanel application server.
# We create the ASGI application in the main thread's event loop and wrap it for WSGI compatibility.
main_loop = asyncio.get_event_loop()
asgi_app = main_loop.run_until_complete(web_server())
application = AsgiToWsgi(asgi_app)
