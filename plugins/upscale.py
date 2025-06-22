# Please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN

import os
import ffmpeg
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
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
    FILE_TOO_LARGE = "❌ File too large. Please send a smaller video file."
    INVALID_FILE = "❌ Please send a valid video file."

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
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit for downloads
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB limit for video uploads

os.makedirs(TEMP_DIR, exist_ok=True)

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
                .output(output_file, **{'c:v': 'libx264', 'preset': 'fast'})
                .overwrite_output()
                .run(quiet=True, capture_stdout=True, capture_stderr=True)
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
        
        # First process the video with quality settings
        await loop.run_in_executor(
            None,
            lambda: (
                ffmpeg
                .input(file_path)
                .filter('scale', settings["resolution"])
                .output(processed_path, 
                       **{'c:v': 'libx264', 'b:v': settings["bitrate"], 'preset': 'fast'})
                .overwrite_output()
                .run(quiet=True, capture_stdout=True, capture_stderr=True)
            )
        )
        
        # Add watermark
        if not await add_watermark(processed_path, final_path):
            logger.warning("Watermark failed, using processed video without watermark")
            return processed_path
        
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
@Client.on_message(filters.video | (filters.document & filters.regex(r'\.(mp4|avi|mkv|mov|wmv|flv|webm)$')))
async def video_handler(client, message):
    try:
        # Check file size
        file_size = 0
        if message.video:
            file_size = message.video.file_size
        elif message.document:
            file_size = message.document.file_size
            # Check if it's actually a video file
            if not (message.document.mime_type and message.document.mime_type.startswith('video/')):
                return
        
        if file_size > MAX_FILE_SIZE:
            await message.reply_text(TEXT.FILE_TOO_LARGE)
            return
        
        await message.reply_text(
            TEXT.CHOOSE_ACTION,
            reply_markup=INLINE.ACTION_BTNS
        )
    except Exception as e:
        logger.error(f"Video handler error: {e}")
        await message.reply_text(TEXT.INVALID_FILE)

@Client.on_callback_query(filters.regex("^action_(upscale|compress)$"))
async def action_handler(client, callback):
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

@Client.on_callback_query(filters.regex("^quality_"))
async def quality_handler(client, callback):
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
        
        # Show processing message
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
        
        if not os.path.exists(file_path):
            raise Exception("Failed to download file")
        
        # Process the video
        processed_path = await process_video(file_path, action, quality)
        
        if not processed_path or not os.path.exists(processed_path):
            raise Exception("Processing failed")
        
        # Send the processed video
        file_size = os.path.getsize(processed_path)
        
        try:
            if file_size > MAX_VIDEO_SIZE:
                # Send as document if file is too large for video
                await callback.message.reply_document(
                    processed_path,
                    caption=f"{TEXT.SUCCESS}\n{TEXT.WATERMARK}",
                    reply_markup=INLINE.CREDITS_BTN
                )
            else:
                await callback.message.reply_video(
                    processed_path,
                    caption=f"{TEXT.SUCCESS}\n{TEXT.WATERMARK}",
                    reply_markup=INLINE.CREDITS_BTN
                )
        except Exception as send_error:
            # Fallback to document if video sending fails
            logger.warning(f"Failed to send as video, trying as document: {send_error}")
            await callback.message.reply_document(
                processed_path,
                caption=f"{TEXT.SUCCESS}\n{TEXT.WATERMARK}",
                reply_markup=INLINE.CREDITS_BTN
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Quality handler error: {str(e)}")
        await callback.answer(TEXT.FAILED, show_alert=True)
        if processing_msg:
            try:
                await processing_msg.edit_text(f"{TEXT.FAILED}: {str(e)}")
            except:
                pass
    finally:
        # Clean up processing message
        if processing_msg:
            try:
                await processing_msg.delete()
            except:
                pass
        
        # Clean up files
        for path in [file_path, processed_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup {path}: {cleanup_error}")
