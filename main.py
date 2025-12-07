# main.py (Pyrogram Calls)

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram_calls import PyrogramCalls
from pyrogram_calls.types import AudioPiped
import asyncio
import requests
from config import API_ID, API_HASH, BOT_TOKEN, PROXY_HOST_IP, PROXY_HOST_PORT, USER_SESSION_STRING

# --- Initialize the Clients ---
bot_app = Client(
    "music_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN
)
user_app = Client(
    USER_SESSION_STRING, api_id=API_ID, api_hash=API_HASH # Session must be generated first
)
calls_app = PyrogramCalls(user_app) # Pyrogram-Calls wrapper

# --- Define the Proxy Endpoint ---
PROXY_URL_BASE = f"http://{PROXY_HOST_IP}:{PROXY_HOST_PORT}/stream_audio"

def get_youtube_url(query: str):
    if "youtube.com" in query or "youtu.be" in query:
        return query
    return None

# --- /play Command Handler ---
@bot_app.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    if not USER_SESSION_STRING:
        await message.reply_text("❌ ERROR: USER_SESSION_STRING is empty. Generate and update config.py.")
        return

    if len(message.command) < 2:
        await message.reply_text("Usage: `/play <YouTube URL>`")
        return

    query = " ".join(message.command[1:])
    youtube_url = get_youtube_url(query)
    
    if not youtube_url:
        await message.reply_text("Please provide a direct YouTube URL for now.")
        return
        
    status_msg = await message.reply_text(f"🎧 Preparing stream for: `{youtube_url}`...")
    
    chat_id = message.chat.id
    
    try:
        # The key step: Use AudioPiped to stream from YOUR PROXY ENDPOINT
        await calls_app.join_group_call(
            chat_id,
            AudioPiped(f"{PROXY_URL_BASE}?url={youtube_url}")
        )

        await status_msg.edit_text(f"▶️ **Started Playing** in Voice Chat! \nTitle: `{youtube_url}`")
        
    except Exception as e:
        print(f"Error during voice chat operation: {e}")
        await status_msg.edit_text(f"❌ **Failed to Play Music!** \nDetails: `{e}` \n\n*Ensure the UserBot is an Admin.*")

# --- /leavevc Command Handler ---
@bot_app.on_message(filters.command("leavevc") & filters.group)
async def leave_command(client: Client, message: Message):
    try:
        await calls_app.leave_group_call(message.chat.id)
        await message.reply_text("👋 Left the Voice Chat.")
    except Exception:
        await message.reply_text("The bot is not currently in a Voice Chat.")


# --- Start the Clients ---
async def start_clients():
    await user_app.start()
    await bot_app.start()
    await calls_app.start()
    print("All Clients started successfully! Bot is ready.")
    await asyncio.gather(bot_app.idle(), calls_app.idle()) # Keep both running

if __name__ == "__main__":
    print("Starting Telegram Bot and Voice Chat Clients...")
    asyncio.run(start_clients())
