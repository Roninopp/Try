# userbot_session.py
# Run this file ONCE to generate the session string.

from pyrogram import Client
from config import API_ID, API_HASH

# We use the same API_ID and API_HASH from your config.py
# The session will be saved as 'user_session.session'

async def generate_session():
    print("--- UserBot Session Generator ---")
    
    # Client will prompt for phone number, login code, and 2FA password
    async with Client(":user_session:", api_id=API_ID, api_hash=API_HASH) as app:
        session_string = await app.export_session_string()
        print("\n✅ Session String Generated Successfully!")
        print("------------------------------------------")
        print(session_string)
        print("------------------------------------------")
        print("\n☝️ COPY this string and PASTE it into USER_SESSION_STRING in your config.py file.")
        print("A file named 'user_session.session' has also been created.")

if __name__ == "__main__":
    try:
        # We need to run the async function
        import asyncio
        asyncio.run(generate_session())
    except Exception as e:
        print(f"An error occurred: {e}")
