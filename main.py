# main.py - Telethon
# The core Telegram bot logic with the /play command and Voice Chat integration.

from telethon import TelegramClient, events
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import AudioPiped
import requests
from config import API_ID, API_HASH, BOT_TOKEN, PROXY_HOST_IP, PROXY_HOST_PORT, USER_SESSION_STRING

# --- Initialize the Clients ---

# 1. The Bot Client (for commands and messages)
bot_app = TelegramClient('telethon_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 2. The UserBot Client (for joining voice chats)
user_app = TelegramClient(
    USER_SESSION_STRING, # Use the string session directly
    API_ID, 
    API_HASH
)

# 3. The PyTgCalls Client (manages the streaming logic - uses UserBot)
pytgcalls_app = PyTgCalls(user_app)

# --- Define the Proxy Endpoint ---
PROXY_URL_BASE = f"http://{PROXY_HOST_IP}:{PROXY_HOST_PORT}/stream_audio"

def get_youtube_url(query: str):
    # This remains a placeholder; for testing, use a direct URL
    if "youtube.com" in query or "youtu.be" in query:
        return query
    return None

# --- /play Command Handler ---
@bot_app.on(events.NewMessage(pattern='/play (.*)', chats=-1))
async def play_command(event):
    """Handles the /play command in a group chat."""
    
    if not USER_SESSION_STRING:
        await event.reply("❌ **ERROR:** The `USER_SESSION_STRING` in `config.py` is empty. Run `userbot_session.py` and update it.")
        return

    query = event.pattern_match.group(1).strip()
    youtube_url = get_youtube_url(query)
    
    if not youtube_url:
        await event.reply("Please provide a direct YouTube URL for now. (e.g., `/play https://youtu.be/dQw4w9WgXcQ`)")
        return
        
    status_msg = await event.reply(f"🎧 Searching and preparing stream for: `{youtube_url}`...")
    
    chat_id = event.chat_id
    
    try:
        # 1. Start the UserBot and PyTgCalls if not started (Telethon way)
        if not user_app.is_connected():
            await user_app.start()
        if not pytgcalls_app.is_connected:
             await pytgcalls_app.start()
             
        # 2. JOIN THE VOICE CHAT
        await pytgcalls_app.join_group_call(
            chat_id,
            AudioPiped(
                f"{PROXY_URL_BASE}?url={youtube_url}",
                StreamType.pulse
            )
        )

        await status_msg.edit(f"▶️ **Started Playing** in Voice Chat! \nTitle: `{youtube_url}`")
        
    except Exception as e:
        print(f"Error during voice chat operation: {e}")
        await status_msg.edit(f"❌ **Failed to Play Music!** \nDetails: `{e}` \n\n*Ensure the UserBot is an Admin with 'Manage Voice Chat' permissions.*")

# --- /leavevc Command Handler ---
@bot_app.on(events.NewMessage(pattern='/leavevc', chats=-1))
async def leave_command(event):
    """Handles the /leavevc command."""
    try:
        await pytgcalls_app.leave_group_call(event.chat_id)
        await event.reply("👋 Left the Voice Chat.")
    except Exception:
        await event.reply("The bot is not currently in a Voice Chat.")


# --- Start the Bot ---
if __name__ == "__main__":
    print("Starting Telegram Bot and Voice Chat Clients...")
    try:
        # Run all clients concurrently
        user_app.loop.run_until_complete(pytgcalls_app.start())
        print("Voice Chat Client started successfully!")
        
        print("Bot Client started successfully!")
        bot_app.run_until_disconnected()

    except Exception as e:
        print(f"An error occurred during startup: {e}")
