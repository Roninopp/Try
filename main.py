import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
# v0.8.6 specific imports
from pytgcalls import GroupCallFactory
from pytgcalls.types.input_stream import InputStream, InputAudioStream

# --- Configuration Imports ---
from config import API_ID, API_HASH, BOT_TOKEN, PROXY_HOST_IP, PROXY_HOST_PORT, USER_SESSION_STRING

# --- Define the Proxy Endpoint ---
PROXY_URL_BASE = f"http://{PROXY_HOST_IP}:{PROXY_HOST_PORT}/stream_audio"

# --- Initialize the Clients ---

# 1. The Bot Client
bot_app = Client(
    "music_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 2. The UserBot Client
user_app = Client(
    USER_SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

# 3. The PyTgCalls Client (The v0.8.6 Legacy Way)
# We create a factory linked to the user_app
group_call_factory = GroupCallFactory(user_app)
# This client will handle joining and streaming
calls_app = group_call_factory.get_file_group_call()

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
        
        # v0.8.6 SYNTAX: Use join_group_call with InputStream and InputAudioStream
        await calls_app.join_group_call(
            chat_id,
            InputStream(
                InputAudioStream(
                    final_proxy_stream_url,
                ),
            ),
        )

        await status_msg.edit_text(f"▶️ **Started Playing**! \nStream: `{youtube_url}`")
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed!** \nDetails: `{e}`")

# --- /leavevc Command Handler ---
@bot_app.on_message(filters.command("leavevc") & filters.group)
async def leave_command(client: Client, message: Message):
    try:
        # v0.8.6 SYNTAX: leave_group_call
        await calls_app.leave_group_call()
        await message.reply_text("👋 Left.")
    except Exception:
        await message.reply_text("Not in a Voice Chat.")

# --- Start the Clients ---
async def start_clients():
    await bot_app.start()
    await user_app.start()
    # Note: In v0.8.6, the calls_app usually starts automatically upon joining,
    # but we keep the structure consistent.
    
    print("Bot is LIVE on Legacy v0.8.6!")
    # Use standard idle to keep both running
    await asyncio.gather(bot_app.idle(), user_app.idle())

if __name__ == "__main__":
    asyncio.run(start_clients())
