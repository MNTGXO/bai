# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging

logger = logging.getLogger(__name__)

START_TEXT = """
🎥 **Video Processing Bot** 

Hi {mention}! I can help you process your videos with the following features:

🔼 **Upscale Videos** - Enhance video quality
🔽 **Compress Videos** - Reduce file size

Simply send me a video file and I'll show you the available options!

**Supported formats:** MP4, AVI, MKV, MOV, WMV, FLV, WEBM
**Max file size:** 100MB

Made with ❤️ by @MrMNTG
"""

START_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/MrMNTG"),
        InlineKeyboardButton("📢 Updates", url="https://t.me/MNBots")
    ],
    [
        InlineKeyboardButton("💬 Support", url="https://t.me/MNBots_support"),
        InlineKeyboardButton("🌟 Rate Bot", url="https://t.me/botfather")
    ]
])

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    try:
        await message.reply_text(
            START_TEXT.format(mention=message.from_user.mention),
            reply_markup=START_BUTTONS,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.reply_text("Sorry, something went wrong. Please try again.")

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    help_text = """
🆘 **How to use this bot:**

1️⃣ Send me a video file (max 100MB)
2️⃣ Choose whether to upscale or compress
3️⃣ Select your preferred quality
4️⃣ Wait for processing to complete
5️⃣ Download your processed video!

**Upscale Options:**
• HD (720p) - Good quality, moderate size
• Full HD (1080p) - Better quality, larger size  
• 2K - Best quality, largest size

**Compress Options:**
• Low (480p) - Smallest size, lower quality
• Medium (540p) - Balanced size and quality
• High (720p) - Good quality, reasonable size

**Tips:**
• Use compress for sharing on social media
• Use upscale to improve old/low-quality videos
• Processing time depends on video length and quality

Need help? Contact @MNBots_support
    """
    
    try:
        await message.reply_text(help_text, reply_markup=START_BUTTONS)
    except Exception as e:
        logger.error(f"Help command error: {e}")
        await message.reply_text("Sorry, something went wrong. Please try again.")

@Client.on_message(filters.command("about") & filters.private)
async def about_command(client: Client, message: Message):
    about_text = """
ℹ️ **About Video Processing Bot**

🤖 **Bot Info:**
• Version: 2.0
• Developer: @MrMNTG  
• Updates: @MNBots
• Support: @MNBots_support

🛠️ **Technologies Used:**
• Python-Telegram-Bot (Pyrogram)
• FFmpeg for video processing
• Hosted on Koyeb Platform

⭐ **Features:**
• Video upscaling with multiple quality options
• Video compression for size reduction
• Watermark addition for branding
• Support for multiple video formats
• Fast processing with quality optimization

📝 **Credits:**
Made with ❤️ by the MN-BOTS team
Source: https://github.com/MN-BOTS

Give us a ⭐ on GitHub if you like this bot!
    """
    
    try:
        await message.reply_text(about_text, reply_markup=START_BUTTONS)
    except Exception as e:
        logger.error(f"About command error: {e}")
        await message.reply_text("Sorry, something went wrong. Please try again.")
