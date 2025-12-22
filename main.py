import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import requests

# --- Configuration Imports ---
from config import API_ID, API_HASH, BOT_TOKEN, PROXY_HOST_IP, PROXY_HOST_PORT, USER_SESSION_STRING

# --- Define the Proxy Endpoint ---
PROXY_URL_BASE = f"http://{PROXY_HOST_IP}:{PROXY_HOST_PORT}/stream_audio"

# --- Initialize the Clients ---

# 1. The Bot Client (for commands)
bot_app = Client(
    "music_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 2. The UserBot Client (for voice chat)
user_app = Client(
    "user_bot_session", # In v2, session name is preferred over raw string here
    session_string=USER_SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

# 3. The PyTgCalls Client
# Link it to the UserBot (user_app)
calls_app = PyTgCalls(user_app)

def get_youtube_url(query: str):
    if "youtube.com" in query or "youtu.be" in query:
        return query
    return None

# --- /play Command Handler ---
@bot_app.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    if not USER_SESSION_STRING:
        await message.reply_text("❌ **ERROR:** `USER_SESSION_STRING` missing.")
        return

    if len(message.command) < 2:
        await message.reply_text("Usage: `/play <YouTube URL>`")
        return

    query = " ".join(message.command[1:])
    youtube_url = get_youtube_url(query)
    
    if not youtube_url:
        await message.reply_text("Please provide a direct YouTube URL.")
        return
        
    status_msg = await message.reply_text(f"🎧 Preparing stream...")
    chat_id = message.chat.id
    
    try:
        # Construct proxy URL
        final_proxy_stream_url = f"{PROXY_URL_BASE}?url={youtube_url}"
        
        # NEW SYNTAX for v2.2.8: Use .play() and MediaStream()
        await calls_app.play(
            chat_id,
            MediaStream(final_proxy_stream_url)
        )

        await status_msg.edit_text(f"▶️ **Started Playing**! \nStream: `{youtube_url}`")
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed!** \nDetails: `{e}`")

# --- /leavevc Command Handler ---
@bot_app.on_message(filters.command("leavevc") & filters.group)
async def leave_command(client: Client, message: Message):
    try:
        # NEW SYNTAX: Use .stop_playout() or just leave
        await calls_app.leave_call(message.chat.id)
        await message.reply_text("👋 Left.")
    except Exception:
        await message.reply_text("Not in a Voice Chat.")

# --- Start the Clients ---
async def start_clients():
    await bot_app.start()
    await user_app.start()
    await calls_app.start() # Start pytgcalls AFTER pyrogram
    
    print("Bot is LIVE!")
    await idle() # Pyrogram's idle blocks execution correctly

if __name__ == "__main__":
    asyncio.run(start_clients())
