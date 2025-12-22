import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Try importing from the two common locations for v0.8.6
try:
    from pytgcalls import GroupCallFactory
except ImportError:
    from pytgcalls.group_call_factory import GroupCallFactory

# Correct Legacy Imports for audio streams
from pytgcalls.types.input_stream import InputStream, InputAudioStream

# --- Configuration ---
from config import API_ID, API_HASH, BOT_TOKEN, PROXY_HOST_IP, PROXY_HOST_PORT, USER_SESSION_STRING

PROXY_URL_BASE = f"http://{PROXY_HOST_IP}:{PROXY_HOST_PORT}/stream_audio"

# --- Clients ---
bot_app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_app = Client(USER_SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

# Initialize Factory and Get the Call Client
group_call_factory = GroupCallFactory(user_app)
calls_app = group_call_factory.get_file_group_call()

# --- Play Command ---
@bot_app.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/play <URL>`")

    youtube_url = message.command[1]
    status_msg = await message.reply_text("🎧 Preparing stream...")
    
    try:
        # Construct proxy URL
        final_stream_url = f"{PROXY_URL_BASE}?url={youtube_url}"
        
        # Legacy v0.8.6 Syntax: join_group_call with InputStream
        await calls_app.join_group_call(
            message.chat.id,
            InputStream(
                InputAudioStream(final_stream_url)
            )
        )
        await status_msg.edit_text(f"▶️ **Playing**: {youtube_url}")
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error**: `{e}`")

# --- Startup ---
async def main():
    await bot_app.start()
    await user_app.start()
    print("Bot is LIVE (Legacy Mode) on Python 3.9!")
    # Use gather to keep both clients running
    await asyncio.gather(bot_app.idle(), user_app.idle())

if __name__ == "__main__":
    asyncio.run(main())
