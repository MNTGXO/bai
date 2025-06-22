# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN

import os
import ffmpeg
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import FileTooLarge, VideoTooLong
import logging
import asyncio

logger = logging.getLogger(__name__)

class TEXT:
    PROCESSING = "⏳ Processing your video..."
    SUCCESS = "✅ Here's your processed video!"
    FAILED = "❌ Failed to process video"
    CHOOSE_ACTION = "What would you like to do with this video?"
    CHOOSE_QUALITY = "Select quality:"
    WATERMARK = "Join @MNBots and @MrMNTG in Telegram"

class INLINE:
    ACTION_BTNS = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔼 Upscale Video", callback_data="action_upscale")],
        [InlineKeyboardButton("🔽 Compress Video", callback_data="action_compress")]
    ])
    
    CREDITS_BTN = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/MrMNTG")],
        [
            InlineKeyboardButton("📢 Updates", url="https://t.me/MNBots"),
            InlineKeyboardButton("💬 Support", url="https://t.me/MNBots_support")
        ]
    ])

# Video processing settings
QUALITY_OPTIONS = {
    "upscale": {
        "HD (720p)": {"resolution": "1280x720", "bitrate": "3000k"},
        "Full HD (1080p)": {"resolution": "1920x1080", "bitrate": "6000k"},
        "2K": {"resolution": "2560x1440", "bitrate": "12000k"}
    },
    "compress": {
        "Low (480p)": {"resolution": "854x480", "bitrate": "1000k"},
        "Medium (540p)": {"resolution": "960x540", "bitrate": "1500k"},
        "High (720p)": {"resolution": "1280x720", "bitrate": "2500k"}
    }
}

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Initialize the bot client (you need to define this)
# MN_Bot = Client("video_bot", api_id=YOUR_API_ID, api_hash="YOUR_API_HASH", bot_token="YOUR_BOT_TOKEN")

# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN
async def add_watermark(input_file, output_file):
    try:
        # Run ffmpeg in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: (
                ffmpeg
                .input(input_file)
                .filter('drawtext', text=TEXT.WATERMARK, fontsize=24,
                        fontcolor='white@0.8', x='(w-text_w)/2', y='h-text_h-10')
                .output(output_file)
                .overwrite_output()
                .run(quiet=True)
            )
        )
        return True
    except Exception as e:
        logger.error(f"Watermark error: {str(e)}")
        return False

# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN
async def process_video(file_path, action, quality):
    processed_path = None
    try:
        settings = QUALITY_OPTIONS[action][quality]
        processed_path = os.path.join(TEMP_DIR, f"processed_{os.path.basename(file_path)}")
        final_path = os.path.join(TEMP_DIR, f"final_{os.path.basename(file_path)}")
        
        # Run ffmpeg in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: (
                ffmpeg
                .input(file_path)
                .filter('scale', settings["resolution"])
                .output(processed_path, video_bitrate=settings["bitrate"])
                .overwrite_output()
                .run(quiet=True)
            )
        )
        
        if not await add_watermark(processed_path, final_path):
            return None
        
        return final_path
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return None
    finally:
        if processed_path and os.path.exists(processed_path):
            try:
                os.remove(processed_path)
            except:
                pass

# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN
def video_handler(client, message):
    @client.on_message(filters.video | filters.document)
    async def handle_video(client, message):
        if message.document and not message.document.mime_type.startswith('video/'):
            return
        
        await message.reply_text(
            TEXT.CHOOSE_ACTION,
            reply_markup=INLINE.ACTION_BTNS
        )
    return handle_video

# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN
def action_handler(client):
    @client.on_callback_query(filters.regex("^action_(upscale|compress)$"))
    async def handle_action(client, callback):
        try:
            action = callback.data.split('_')[1]
            quality_btns = [
                [InlineKeyboardButton(quality, callback_data=f"quality_{action}_{quality.replace(' ', '_').replace('(', '').replace(')', '')}")]
                for quality in QUALITY_OPTIONS[action]
            ]
            
            await callback.message.edit_text(
                TEXT.CHOOSE_QUALITY,
                reply_markup=InlineKeyboardMarkup(quality_btns)
            )
            await callback.answer()
        except Exception as e:
            logger.error(f"Action error: {str(e)}")
            await callback.answer(TEXT.FAILED, show_alert=True)
    return handle_action

# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN
def quality_handler(client):
    @client.on_callback_query(filters.regex("^quality_"))
    async def handle_quality(client, callback):
        processing_msg = None
        file_path = None
        processed_path = None
        
        try:
            data = callback.data.split('_')
            action = data[1]
            # Reconstruct quality name properly
            quality_parts = data[2:]
            
            # Find matching quality from options
            quality = None
            for q in QUALITY_OPTIONS[action]:
                clean_q = q.replace(' ', '_').replace('(', '').replace(')', '')
                if clean_q == '_'.join(quality_parts):
                    quality = q
                    break
            
            if not quality:
                raise Exception("Invalid quality selection")
            
            # Get the original message with video
            if not callback.message.reply_to_message:
                await callback.answer("Original video message not found", show_alert=True)
                return
                
            original_msg = callback.message.reply_to_message
            
            processing_msg = await callback.message.reply_text(TEXT.PROCESSING)
            
            # Get file info
            if original_msg.video:
                file_id = original_msg.video.file_id
                file_ext = "mp4"
            elif original_msg.document and original_msg.document.mime_type.startswith('video/'):
                file_id = original_msg.document.file_id
                file_ext = original_msg.document.file_name.split('.')[-1] if original_msg.document.file_name else "mp4"
            else:
                raise Exception("No video found")
            
            file_path = os.path.join(TEMP_DIR, f"original_{file_id}.{file_ext}")
            
            # Download the file
            await client.download_media(original_msg, file_name=file_path)
            
            # Process the video
            processed_path = await process_video(file_path, action, quality)
            
            if not processed_path or not os.path.exists(processed_path):
                raise Exception("Processing failed")
            
            # Send the processed video
            try:
                await callback.message.reply_video(
                    processed_path,
                    caption=f"{TEXT.SUCCESS}\n{TEXT.WATERMARK}",
                    reply_markup=INLINE.CREDITS_BTN
                )
            except (VideoTooLong, FileTooLarge):
                await callback.message.reply_document(
                    processed_path,
                    caption=f"{TEXT.SUCCESS}\n{TEXT.WATERMARK}",
                    reply_markup=INLINE.CREDITS_BTN
                )
            
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Quality error: {str(e)}")
            await callback.answer(TEXT.FAILED, show_alert=True)
        finally:
            # Clean up processing message
            if processing_msg:
                try:
                    await processing_msg.delete()
                except:
                    pass
            
            # Clean up files
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            if processed_path and os.path.exists(processed_path):
                try:
                    os.remove(processed_path)
                except:
                    pass
    
    return handle_quality
"""
# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN
def register(bot):
    video_handler(bot)
    action_handler(bot)
    quality_handler(bot)

"""

@MN_Bot.on_message(filters.video | filters.document)
async def video_handler_direct(client, message):
    if message.document and not message.document.mime_type.startswith('video/'):
        return
    
    await message.reply_text(
        TEXT.CHOOSE_ACTION,
        reply_markup=INLINE.ACTION_BTNS
    )

@MN_Bot.on_callback_query(filters.regex("^action_(upscale|compress)$"))
async def action_handler_direct(client, callback):
    try:
        action = callback.data.split('_')[1]
        quality_btns = [
            [InlineKeyboardButton(quality, callback_data=f"quality_{action}_{quality.replace(' ', '_').replace('(', '').replace(')', '')}")]
            for quality in QUALITY_OPTIONS[action]
        ]
        
        await callback.message.edit_text(
            TEXT.CHOOSE_QUALITY,
            reply_markup=InlineKeyboardMarkup(quality_btns)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Action error: {str(e)}")
        await callback.answer(TEXT.FAILED, show_alert=True)

@MN_Bot.on_callback_query(filters.regex("^quality_"))
async def quality_handler_direct(client, callback):
    # ... (same implementation as in quality_handler function above)
    pass
