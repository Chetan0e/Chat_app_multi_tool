#!/usr/bin/env python3
"""
Telegram Bot startup script for the Chat App Multitool.
This script starts the Telegram bot in polling mode for development and testing.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings, validate_settings
from routers.telegram_bot import telegram_bot
from routers.composio_router import composio_router

async def main():
    """Main function to start the Telegram bot."""
    print("[BOT] Chat App Multitool - Telegram Bot")
    print("=" * 50)
    
    # Validate settings
    if not validate_settings():
        print("[ERROR] Settings validation failed. Please check your configuration.")
        return
    
    # Check if Telegram bot token is available
    if not settings.telegram_bot_token:
        print("[ERROR] Telegram bot token not found!")
        print("   Please set TELEGRAM_BOT_TOKEN in your .env file.")
        print("   Get a token from @BotFather on Telegram.")
        return
    
    print("[SUCCESS] Configuration validated successfully!")
    
    # Initialize Composio router
    print("[INFO] Initializing Composio ToolRouter...")
    await composio_router.initialize()
    
    # Initialize and start Telegram bot
    print("[INFO] Initializing Telegram bot...")
    if await telegram_bot.initialize():
        print("[SUCCESS] Telegram bot initialized successfully!")
        print("\n[INFO] Starting Telegram bot in polling mode...")
        print("   Your bot is now ready to receive messages!")
        print("   Press Ctrl+C to stop the bot")
        print("-" * 50)
        
        try:
            await telegram_bot.start_polling()
        except KeyboardInterrupt:
            print("\n[INFO] Bot stopped. Goodbye!")
        except Exception as e:
            print(f"\n[ERROR] Error running bot: {e}")
    else:
        print("[ERROR] Failed to initialize Telegram bot")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the bot
    asyncio.run(main())
