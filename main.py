# main.py
# The core Telegram bot logic with the /play command and Voice Chat integration.

import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import AudioPiped
import requests
from config import API_ID, API_HASH, BOT_TOKEN, PROXY_HOST_IP, PROXY_HOST_PORT, USER_SESSION_STRING

# --- Initialize the Clients ---

# 1. The Bot Client (for commands and messages)
bot_app = Client(
    "music_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 2. The UserBot Client (for joining voice chats)
user_app = Client(
    USER_SESSION_STRING, # Pyrogram uses the session string directly
    api_id=API_ID,
    api_hash=API_HASH
)

# 3. The PyTgCalls Client (manages the streaming logic)
pytgcalls_app = PyTgCalls(user_app)


# --- Define the Proxy Endpoint ---
PROXY_URL_BASE = f"http://{PROXY_HOST_IP}:{PROXY_HOST_PORT}/stream_audio"

def get_youtube_url(query: str):
    # This remains a placeholder; for testing, use a direct URL
    if "youtube.com" in query or "youtu.be" in query:
        return query
    return None

# --- /play Command Handler ---
@bot_app.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    """Handles the /play command in a group chat."""
    
    if not USER_SESSION_STRING:
        await message.reply_text("❌ **ERROR:** The `USER_SESSION_STRING` in `config.py` is empty. Run `userbot_session.py` and update it.")
        return

    if len(message.command) < 2:
        await message.reply_text("Usage: `/play <YouTube URL>`")
        return

    query = " ".join(message.command[1:])
    youtube_url = get_youtube_url(query)
    
    if not youtube_url:
        await message.reply_text("Please provide a direct YouTube URL for now. (e.g., `/play https://youtu.be/dQw4w9WgXcQ`)")
        return
        
    status_msg = await message.reply_text(f"🎧 Searching and preparing stream for: `{youtube_url}`...")
    
    chat_id = message.chat.id
    
    try:
        # 1. JOIN THE VOICE CHAT (using the UserBot)
        await pytgcalls_app.join_group_call(
            chat_id,
            AudioPiped(
                # 2. Pass the stream to your custom proxy server!
                f"{PROXY_URL_BASE}?url={youtube_url}",
                # 3. Use raw FFmpeg input for maximum compatibility (AudioPiped)
                StreamType.pulse
            ),
            # You can set this to True if you want the UserBot to be muted when joining
            mute=False
        )

        await status_msg.edit_text(f"▶️ **Started Playing** in Voice Chat! \nTitle: `{youtube_url}`")
        
    except Exception as e:
        print(f"Error during voice chat operation: {e}")
        await status_msg.edit_text(f"❌ **Failed to Play Music!** \nDetails: `{e}` \n\n*Ensure the UserBot is an Admin with 'Manage Voice Chat' permissions.*")

# --- /leavevc Command Handler ---
@bot_app.on_message(filters.command("leavevc") & filters.group)
async def leave_command(client: Client, message: Message):
    """Handles the /leavevc command."""
    try:
        await pytgcalls_app.leave_group_call(message.chat.id)
        await message.reply_text("👋 Left the Voice Chat.")
    except Exception:
        await message.reply_text("The bot is not currently in a Voice Chat.")


# --- Start the Clients ---
async def start_clients():
    await user_app.start()
    await bot_app.start()
    await pytgcalls_app.start()
    print("Clients started successfully! Bot is ready.")
    await bot_app.idle() # Keep the bot running

if __name__ == "__main__":
    print("Starting Telegram Bot and Voice Chat Clients...")
    import asyncio
    asyncio.run(start_clients())
