# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN

import logging
import os
from pyrogram import Client
from config import BOT, API, OWNER

# Basic logging setup
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
            workers=8
        )
        # Create temp directory if not exists
        os.makedirs("temp_files", exist_ok=True)

    async def start(self):
        await super().start()
        me = await self.get_me()
        logger.info(f"Bot started as @{me.username}")
        
        # Notify owner
        await self.send_message(
            OWNER.ID,
            f"🤖 **Bot Started Successfully**\n\n"
            f"• **Username**: @{me.username}\n"
            f"• **Ready to serve!**"
        )

    async def stop(self, *args):
        # Clean temp files
        try:
            for file in os.listdir("temp_files"):
                os.remove(f"temp_files/{file}")
            logger.info("Cleaned temporary files")
        except Exception as e:
            logger.warning(f"Error cleaning temp files: {e}")
        
        await super().stop()
        logger.info("Bot stopped gracefully")

if __name__ == "__main__":
    bot = MN_Bot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
    finally:
        # Ensure proper cleanup
        import asyncio
        asyncio.get_event_loop().run_until_complete(bot.stop())
