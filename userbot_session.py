#!/usr/bin/env python3
"""
Session String Generator for Pyrogram
This will generate a new USER_SESSION_STRING for your config.py
"""

from pyrogram import Client

# Replace these with your actual values from config.py
API_ID = 12345678  # Your API_ID
API_HASH = "your_api_hash_here"  # Your API_HASH

async def generate_session():
    print("=" * 50)
    print("Session String Generator")
    print("=" * 50)
    
    async with Client(
        "my_account",
        api_id=API_ID,
        api_hash=API_HASH
    ) as app:
        session_string = await app.export_session_string()
        
        print("\n✅ SESSION STRING GENERATED SUCCESSFULLY!\n")
        print("Copy this string and paste it in your config.py as USER_SESSION_STRING:\n")
        print("-" * 50)
        print(session_string)
        print("-" * 50)
        print("\n⚠️ Keep this string SECRET! Don't share it with anyone.")

if __name__ == "__main__":
    import asyncio
    
    print("\n📱 You will need to enter:")
    print("   1. Your phone number (with country code, e.g., +1234567890)")
    print("   2. The verification code sent to your Telegram\n")
    
    asyncio.run(generate_session())
