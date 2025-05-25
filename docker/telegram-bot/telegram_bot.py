#!/usr/bin/env python3
"""
DataVault Telegram Bot - Standalone Service
Receives messages from Telegram and forwards them to DataVault API
"""

import asyncio
import logging
import os
import aiohttp
import aiofiles
from datetime import datetime
from typing import Optional, Dict, Any

from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATAVAULT_API_URL = os.getenv('DATAVAULT_API_URL', 'http://backend:8000')

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class DataVaultTelegramBot:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.api_url = DATAVAULT_API_URL
        self.application = None
        self.session = None
    
    async def initialize(self):
        """Initialize the bot and HTTP session"""
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not provided")
            return False
        
        try:
            # Create HTTP session for API calls
            self.session = aiohttp.ClientSession()
            
            # Create Telegram application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("stats", self.stats_command))
            
            # Message handlers (order matters - more specific first)
            self.application.add_handler(
                MessageHandler(filters.PHOTO, self.handle_photo_message)
            )
            self.application.add_handler(
                MessageHandler(filters.VIDEO, self.handle_video_message)
            )
            self.application.add_handler(
                MessageHandler(filters.AUDIO, self.handle_audio_message)
            )
            self.application.add_handler(
                MessageHandler(filters.Document.ALL, self.handle_document_message)
            )
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
            )
            
            logger.info("DataVault Telegram bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    async def start(self):
        """Start the bot"""
        if not await self.initialize():
            return
        
        try:
            logger.info("🤖 Starting DataVault Telegram Bot...")
            logger.info("Bot is ready to receive messages!")
            
            # Start the application and run polling
            async with self.application:
                await self.application.start()
                await self.application.updater.start_polling(drop_pending_updates=True)
                
                # Keep running until interrupted
                try:
                    await asyncio.Event().wait()  # Wait indefinitely
                except asyncio.CancelledError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            # Cleanup
            if self.session and not self.session.closed:
                await self.session.close()
    
    async def send_to_api(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Send data to DataVault API"""
        try:
            url = f"{self.api_url}/api/{endpoint}"
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error {response.status}: {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Error sending to API: {e}")
            return None
    
    async def download_file(self, file_info, folder: str, extension: str) -> Optional[str]:
        """Download file from Telegram and save locally"""
        try:
            # Create folder if it doesn't exist
            os.makedirs(f"storage/{folder}", exist_ok=True)
            
            # Generate unique filename
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_info.file_id}.{extension}"
            file_path = f"storage/{folder}/{filename}"
            
            # Download file
            await file_info.download_to_drive(file_path)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    # Command handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Welcome to DataVault Bot!

Forward any messages, images, videos, or documents to me and I'll intelligently store and organize them for you.

Commands:
/help - Show this help message
/stats - Show your message statistics

Just forward or send any content and I'll take care of the rest!

✨ Features:
• AI-powered categorization
• Semantic search
• Automatic tagging
• Sentiment analysis
• Smart querying
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 DataVault Bot Help

🔹 Forward messages from any chat
🔹 Send text, images, videos, audio, or documents
🔹 I'll automatically categorize and store everything
🔹 Use the web interface to search and query your data

Features:
✅ AI-powered categorization
✅ Semantic search
✅ Automatic tagging
✅ Sentiment analysis
✅ Smart querying

Your data is processed and stored securely.
Access your dashboard at: http://localhost:3000
        """
        await update.message.reply_text(help_message)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        try:
            user_id = str(update.effective_user.id)
            # TODO: Implement stats API call
            stats_message = f"""
📊 Your DataVault Statistics

📨 Total messages: Loading...
📂 Categories: Loading...
📅 Last activity: Loading...
💾 Storage used: Loading...

Keep sending messages to build your knowledge base!
            """
            await update.message.reply_text(stats_message)
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await update.message.reply_text("Sorry, couldn't retrieve statistics right now.")
    
    # Message handlers
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            message_data = {
                "content": update.message.text,
                "source_type": "telegram",
                "source_chat_id": str(update.effective_chat.id),
                "source_message_id": str(update.message.message_id),
                "sender_name": update.effective_user.full_name,
                "sender_id": str(update.effective_user.id),
                "timestamp": update.message.date.isoformat(),
                "message_type": "text"
            }
            
            # Send to API
            result = await self.send_to_api("messages", message_data)
            
            if result:
                await update.message.reply_text(
                    "✅ Message stored and will be processed shortly!",
                    reply_to_message_id=update.message.message_id
                )
                logger.info(f"Text message stored: {result.get('id')}")
            else:
                await update.message.reply_text("❌ Failed to store message.")
                
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text("❌ Error processing message.")
    
    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages with improved content extraction"""
        try:
            photo = update.message.photo[-1]  # Get highest resolution
            file_info = await context.bot.get_file(photo.file_id)
            
            # Download and save file
            file_path = await self.download_file(file_info, "photos", "jpg")
            
            # Extract content from various sources
            content = ""
            
            # Try different ways to get the text content
            if update.message.caption:
                content = update.message.caption
                logger.info(f"Found caption: {content[:100]}...")
            elif hasattr(update.message, 'text') and update.message.text:
                content = update.message.text
                logger.info(f"Found text: {content[:100]}...")
            elif update.message.forward_origin:
                # Handle forwarded messages
                if hasattr(update.message.forward_origin, 'sender_user'):
                    content = f"Forwarded from {update.message.forward_origin.sender_user.full_name}"
                logger.info("Found forwarded message")
            
            # Log for debugging
            logger.info(f"Photo message - Content length: {len(content)}, Has caption: {bool(update.message.caption)}, Is forwarded: {bool(update.message.forward_origin)}")
            
            message_data = {
                "content": content,
                "source_type": "telegram",
                "source_chat_id": str(update.effective_chat.id),
                "source_message_id": str(update.message.message_id),
                "sender_name": update.effective_user.full_name,
                "sender_id": str(update.effective_user.id),
                "timestamp": update.message.date.isoformat(),
                "message_type": "image",
                "file_path": file_path,
                "file_type": "image/jpeg",
                "file_size": getattr(photo, 'file_size', 0)
            }
            
            # Send to API
            result = await self.send_to_api("messages", message_data)
            
            if result:
                await update.message.reply_text(
                    "📸 Photo with text stored successfully!",
                    reply_to_message_id=update.message.message_id
                )
                logger.info(f"Photo message stored: {result.get('id')}")
            else:
                await update.message.reply_text("❌ Failed to store photo.")
            
        except Exception as e:
            logger.error(f"Error handling photo: {e}")
            await update.message.reply_text("❌ Error processing photo.")
    
    async def handle_video_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle video messages"""
        try:
            video = update.message.video
            file_info = await context.bot.get_file(video.file_id)
            
            file_path = await self.download_file(file_info, "videos", "mp4")
            
            message_data = {
                "content": update.message.caption or "",
                "source_type": "telegram",
                "source_chat_id": str(update.effective_chat.id),
                "source_message_id": str(update.message.message_id),
                "sender_name": update.effective_user.full_name,
                "sender_id": str(update.effective_user.id),
                "timestamp": update.message.date.isoformat(),
                "message_type": "video",
                "file_path": file_path,
                "file_type": "video/mp4",
                "file_size": getattr(video, 'file_size', 0)
            }
            
            result = await self.send_to_api("messages", message_data)
            
            if result:
                await update.message.reply_text("🎥 Video stored successfully!")
                logger.info(f"Video message stored: {result.get('id')}")
            
        except Exception as e:
            logger.error(f"Error handling video: {e}")
            await update.message.reply_text("❌ Error processing video.")
    
    async def handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio messages"""
        try:
            audio = update.message.audio or update.message.voice
            file_info = await context.bot.get_file(audio.file_id)
            
            file_extension = "ogg" if update.message.voice else "mp3"
            file_path = await self.download_file(file_info, "audio", file_extension)
            
            message_data = {
                "content": update.message.caption or "",
                "source_type": "telegram",
                "source_chat_id": str(update.effective_chat.id),
                "source_message_id": str(update.message.message_id),
                "sender_name": update.effective_user.full_name,
                "sender_id": str(update.effective_user.id),
                "timestamp": update.message.date.isoformat(),
                "message_type": "audio",
                "file_path": file_path,
                "file_type": f"audio/{file_extension}",
                "file_size": getattr(audio, 'file_size', 0)
            }
            
            result = await self.send_to_api("messages", message_data)
            
            if result:
                await update.message.reply_text("🎵 Audio stored successfully!")
                logger.info(f"Audio message stored: {result.get('id')}")
            
        except Exception as e:
            logger.error(f"Error handling audio: {e}")
            await update.message.reply_text("❌ Error processing audio.")
    
    async def handle_document_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document messages"""
        try:
            document = update.message.document
            file_info = await context.bot.get_file(document.file_id)
            
            file_extension = document.file_name.split('.')[-1] if '.' in document.file_name else 'bin'
            file_path = await self.download_file(file_info, "documents", file_extension)
            
            message_data = {
                "content": update.message.caption or document.file_name,
                "source_type": "telegram",
                "source_chat_id": str(update.effective_chat.id),
                "source_message_id": str(update.message.message_id),
                "sender_name": update.effective_user.full_name,
                "sender_id": str(update.effective_user.id),
                "timestamp": update.message.date.isoformat(),
                "message_type": "document",
                "file_path": file_path,
                "file_type": document.mime_type or "application/octet-stream",
                "file_size": document.file_size
            }
            
            result = await self.send_to_api("messages", message_data)
            
            if result:
                await update.message.reply_text("📄 Document stored successfully!")
                logger.info(f"Document message stored: {result.get('id')}")
            
        except Exception as e:
            logger.error(f"Error handling document: {e}")
            await update.message.reply_text("❌ Error processing document.")


def main():
    """Main function"""
    bot = DataVaultTelegramBot()
    
    # Use asyncio.new_event_loop to avoid conflicts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        loop.close()


if __name__ == "__main__":
    main() 