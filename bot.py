# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN

import logging
import os
import asyncio
from pyrogram import Client
from config import BOT, API, OWNER

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MN_Bot(Client):
    def __init__(self):
        super().__init__(
            "mn_bot",
            api_id=API.ID,
            api_hash=API.HASH,
            bot_token=BOT.TOKEN,
            plugins={"root": "plugins"},
            workers=4
        )
        os.makedirs("temp_files", exist_ok=True)
        self._running = False

    async def start(self):
        try:
            self._running = True
            await super().start()
            me = await self.get_me()
            logger.info(f"Bot started as @{me.username}")
            
            # Only send startup message if owner ID is properly configured
            if hasattr(OWNER, 'ID') and OWNER.ID:
                try:
                    await self.send_message(
                        OWNER.ID,
                        f"🤖 Bot @{me.username} started successfully!\n"
                        f"Ready to process your requests."
                    )
                except Exception as e:
                    logger.warning(f"Could not send startup message to owner: {e}")
        except Exception as e:
            logger.error(f"Error during bot startup: {e}")
            raise

    async def stop(self, *args):
        if not self._running:
            return
            
        self._running = False
        logger.info("Shutting down bot...")
        
        # Clean temp files
        try:
            if os.path.exists("temp_files"):
                for file in os.listdir("temp_files"):
                    file_path = os.path.join("temp_files", file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                logger.info("Cleaned temporary files")
        except Exception as e:
            logger.warning(f"Error cleaning temp files: {e}")
        
        try:
            # Check if client is initialized before stopping
            if hasattr(self, '_initialized') and self._initialized:
                await super().stop()
        except Exception as e:
            logger.warning(f"During shutdown: {e}")

# Create global bot instance
bot = MN_Bot()

async def main():
    try:
        await bot.start()
        logger.info("Bot is running. Press Ctrl+C to stop.")
        await asyncio.get_event_loop().create_future()  # Run forever
    except (KeyboardInterrupt, SystemExit):
        logger.info("Received stop signal, shutting down...")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
        # Add exponential backoff for flood wait errors
        if "FLOOD_WAIT" in str(e):
            import re
            wait_time = re.search(r'(\d+)', str(e))
            if wait_time:
                wait_seconds = int(wait_time.group(1))
                logger.info(f"Flood wait detected. Waiting {wait_seconds} seconds...")
                await asyncio.sleep(wait_seconds)
        raise
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
