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
        self._running = True
        await super().start()
        me = await self.get_me()
        logger.info(f"Bot started as @{me.username}")
        
        await self.send_message(
            OWNER.ID,
            f"🤖 Bot @{me.username} started successfully!\n"
            f"Ready to process your requests."
        )

    async def stop(self, *args):
        if not self._running:
            return
            
        self._running = False
        logger.info("Shutting down bot...")
        
        # Clean temp files
        try:
            for file in os.listdir("temp_files"):
                os.remove(f"temp_files/{file}")
            logger.info("Cleaned temporary files")
        except Exception as e:
            logger.warning(f"Error cleaning temp files: {e}")
        
        try:
            if await self.is_initialized:
                await super().stop()
        except Exception as e:
            logger.warning(f"During shutdown: {e}")

async def main():
    bot = MN_Bot()
    try:
        await bot.start()
        await asyncio.get_event_loop().create_future()  # Run forever
    except (KeyboardInterrupt, SystemExit):
        logger.info("Received stop signal, shutting down...")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
