# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN

import logging
import threading
import os
from flask import Flask
from pyrogram import Client
from config import BOT, API, OWNER

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "MNBot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8000)

class MN_Bot(Client):
    def __init__(self):
        super().__init__(
            "MN-Bot",
            api_id=API.ID,
            api_hash=API.HASH,
            bot_token=BOT.TOKEN,
            plugins=dict(root="plugins"),
            workers=16,
            max_concurrent_transmissions=4
        )
        self.temp_dir = "temp_files"
        self._setup()

    def _setup(self):
        """Initialize bot directories"""
        os.makedirs(self.temp_dir, exist_ok=True)
        logging.info("Initialized bot directories")

    async def start(self):
        await super().start()
        me = await self.get_me()
        BOT.USERNAME = f"@{me.username}"
        
        # Modified startup notification to include video processing info
        startup_msg = (
            f"✨ **{me.first_name} is now running!**\n\n"
            f"• **Video Tools:** Upscale/Compress Active\n"
            f"• **Plugins Loaded:** {len(self.plugins)}\n"
            f"• **Ready to process your requests!**\n\n"
            f"`Send /start to see my capabilities`"
        )
        
        await self.send_message(
            chat_id=OWNER.ID,
            text=startup_msg
        )
        logging.info(f"{me.first_name} started with video processing support")

    async def stop(self, *args):
        """Clean shutdown with temp file cleanup"""
        await self._clean_temp_files()
        await super().stop()
        logging.info("Bot stopped gracefully")

    async def _clean_temp_files(self):
        """Remove temporary video files"""
        try:
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            logging.info("Cleaned temporary files")
        except Exception as e:
            logging.warning(f"Couldn't clean temp files: {e}")

    def load_plugins(self):
        """Dynamically load all plugins"""
        from plugins import upscale, downloader  # Add other plugins here
        logging.info("Video processing plugins loaded")

if __name__ == "__main__":
    # Start Flask server in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Create and run bot
    bot = MN_Bot()
    
    try:
        # Load plugins before starting
        bot.load_plugins()
        
        # Run the bot
        bot.run()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.critical(f"Bot crashed: {e}")
    finally:
        import asyncio
        asyncio.run(bot.stop())
