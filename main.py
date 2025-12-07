# main.py
# Uses Pyrogram 1.4.16 and PyTgCalls 0.8.6 (The stable architecture)
# Integrates the custom streaming_proxy.py to handle unstable stream URLs.

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from py_tgcalls import PyTgCalls # CORRECT import for the installed library
from py_tgcalls.types import AudioPiped
import requests

# --- Configuration Imports ---
# Make sure your config.py is correctly updated with API_ID, BOT_TOKEN, etc.
from config import API_ID, API_HASH, BOT_TOKEN, PROXY_HOST_IP, PROXY_HOST_PORT, USER_SESSION_STRING

# --- Define the Proxy Endpoint ---
# This is the URL that points to your streaming_proxy.py server running on port 8080
PROXY_URL_BASE = f"http://{PROXY_HOST_IP}:{PROXY_HOST_PORT}/stream_audio"

# --- Initialize the Clients ---

# 1. The Bot Client (for commands and messages)
# We use an explicit session name for better control
bot_app = Client(
    "music_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 2. The UserBot Client (for joining voice chats)
# Pyrogram 1.x uses the session string directly for UserBots
user_app = Client(
    USER_SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

# 3. The PyTgCalls Client (manages the streaming logic)
# Correctly uses PyTgCalls from the py_tgcalls library
calls_app = PyTgCalls(user_app)

# --- Helper Function to Search YouTube (Simplified) ---
# NOTE: For production, you should use a library like 'youtube-search-python'
# to get the URL from a search query. We rely on direct URL input for this test.
def get_youtube_url(query: str):
    """Returns the URL if the query looks like a YouTube link."""
    if "youtube.com" in query or "youtu.be" in query:
        return query
    return None

# --- /play Command Handler ---
@bot_app.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    """Handles the /play command in a group chat."""
    
    if not USER_SESSION_STRING:
        await message.reply_text("❌ **ERROR:** The `USER_SESSION_STRING` in `config.py` is empty. Please check configuration.")
        return

    if len(message.command) < 2:
        await message.reply_text("Usage: `/play <YouTube URL or search query>`")
        return

    query = " ".join(message.command[1:])
    youtube_url = get_youtube_url(query)
    
    if not youtube_url:
        # Fallback to simple search if not a direct URL (optional, can be improved)
        await message.reply_text("Please provide a direct YouTube URL for stable playback.")
        return
        
    status_msg = await message.reply_text(f"🎧 Preparing stream for: `{youtube_url}`...")
    
    chat_id = message.chat.id
    
    try:
        # 1. Construct the final proxy streaming URL
        final_proxy_stream_url = f"{PROXY_URL_BASE}?url={youtube_url}"
        
        # 2. JOIN THE VOICE CHAT and start streaming from YOUR PROXY ENDPOINT
        # AudioPiped is essential for streaming without downloading the whole file first.
        await calls_app.join_group_call(
            chat_id,
            AudioPiped(final_proxy_stream_url)
        )

        await status_msg.edit_text(f"▶️ **Started Playing** in Voice Chat! \nStreaming via Proxy: `{youtube_url}`")
        
    except Exception as e:
        print(f"Error during voice chat operation: {e}")
        await status_msg.edit_text(f"❌ **Failed to Play Music!** \nDetails: `{e}` \n\n*Ensure UserBot is an Admin with 'Manage Voice Chat' permissions.*")

# --- /leavevc Command Handler ---
@bot_app.on_message(filters.command("leavevc") & filters.group)
async def leave_command(client: Client, message: Message):
    """Handles the /leavevc command."""
    try:
        # Stop the stream and leave the call
        await calls_app.leave_group_call(message.chat.id)
        await message.reply_text("👋 Left the Voice Chat.")
    except Exception:
        await message.reply_text("The bot is not currently in a Voice Chat.")


# --- Start the Clients ---
async def start_clients():
    # Start the Pyrogram client sessions first
    await user_app.start()
    await bot_app.start()
    
    # Start the PyTgCalls wrapper
    await calls_app.start()
    
    print("All Clients started successfully! Bot is ready.")
    # Keep the bot and calls running indefinitely
    await asyncio.gather(bot_app.idle(), calls_app.idle()) 

if __name__ == "__main__":
    print("Starting Telegram Bot and Voice Chat Clients...")
    # asyncio.run() is required to run the main async function
    asyncio.run(start_clients())
