import asyncio
import logging
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from typing import Optional, Dict, Any
from config.settings import settings
from app.services.message_service import MessageService
from app.schemas.message import MessageCreate
from datetime import datetime
import os
import aiofiles


class TelegramService:
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.application = None
        self.message_service = MessageService()
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
    
    async def initialize_bot(self):
        """Initialize the Telegram bot application"""
        if not self.bot_token:
            self.logger.error("Telegram bot token not provided")
            return False
        
        try:
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
            # Catch-all for any other message types
            self.application.add_handler(
                MessageHandler(filters.ALL & ~filters.COMMAND, self.handle_generic_message)
            )
            
            self.logger.info("Telegram bot initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {e}")
            return False
    
    async def start_bot(self):
        """Start the Telegram bot (initialize only, no polling)"""
        if not self.application:
            await self.initialize_bot()
        
        if self.application:
            try:
                # Just initialize the application, don't start polling
                # Polling conflicts with FastAPI's event loop
                await self.application.initialize()
                self.logger.info("Telegram bot initialized (polling disabled to avoid event loop conflicts)")
            except Exception as e:
                self.logger.error(f"Error initializing Telegram bot: {e}")
    
    async def process_update(self, update_data: dict):
        """Process a Telegram update manually"""
        if not self.application:
            return
        
        try:
            from telegram import Update
            update = Update.de_json(update_data, self.application.bot)
            await self.application.process_update(update)
        except Exception as e:
            self.logger.error(f"Error processing update: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Welcome to DataVault Bot!

Forward any messages, images, videos, or documents to me and I'll intelligently store and organize them for you.

Commands:
/help - Show this help message
/stats - Show your message statistics

Just forward or send any content and I'll take care of the rest!
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
        """
        await update.message.reply_text(help_message)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        try:
            user_id = str(update.effective_user.id)
            stats = await self.message_service.get_user_stats(user_id)
            
            stats_message = f"""
📊 Your DataVault Statistics

📨 Total messages: {stats.get('total_messages', 0)}
📂 Categories: {', '.join(stats.get('top_categories', [])[:5]) or 'None yet'}
📅 Last activity: {stats.get('last_activity', 'Never')}
💾 Storage used: {stats.get('storage_used', '0 MB')}

Keep sending messages to build your knowledge base!
            """
            await update.message.reply_text(stats_message)
            
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            await update.message.reply_text("Sorry, couldn't retrieve statistics right now.")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            message_data = MessageCreate(
                content=update.message.text,
                source_type="telegram",
                source_chat_id=str(update.effective_chat.id),
                source_message_id=str(update.message.message_id),
                sender_name=update.effective_user.full_name,
                sender_id=str(update.effective_user.id),
                timestamp=update.message.date,
                message_type="text"
            )
            
            # Store message
            stored_message = await self.message_service.create_message(message_data)
            
            if stored_message:
                await update.message.reply_text(
                    "✅ Message stored and will be processed shortly!",
                    reply_to_message_id=update.message.message_id
                )
            else:
                await update.message.reply_text("❌ Failed to store message.")
                
        except Exception as e:
            self.logger.error(f"Error handling text message: {e}")
            await update.message.reply_text("❌ Error processing message.")
    
    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages"""
        try:
            photo = update.message.photo[-1]  # Get highest resolution
            file_info = await context.bot.get_file(photo.file_id)
            
            # Download and save file
            file_path = await self.download_file(file_info, "photos", "jpg")
            
            # Get content from caption or forwarded message text
            content = ""
            if update.message.caption:
                content = update.message.caption
            elif update.message.forward_from_message_id and update.message.text:
                content = update.message.text
            elif hasattr(update.message, 'forward_origin') and update.message.forward_origin:
                # Try to get original message content if available
                content = getattr(update.message, 'text', '') or update.message.caption or ""
            
            # Log for debugging
            self.logger.info(f"Photo message content: '{content}', has_caption: {bool(update.message.caption)}, is_forwarded: {bool(update.message.forward_from_message_id)}")
            
            message_data = MessageCreate(
                content=content,
                source_type="telegram",
                source_chat_id=str(update.effective_chat.id),
                source_message_id=str(update.message.message_id),
                sender_name=update.effective_user.full_name,
                sender_id=str(update.effective_user.id),
                timestamp=update.message.date,
                message_type="image",
                file_path=file_path,
                file_type="image/jpeg",
                file_size=getattr(photo, 'file_size', 0)
            )
            
            stored_message = await self.message_service.create_message(message_data)
            
            if stored_message:
                await update.message.reply_text(
                    "📸 Photo with text stored successfully!",
                    reply_to_message_id=update.message.message_id
                )
            
        except Exception as e:
            self.logger.error(f"Error handling photo: {e}")
            await update.message.reply_text("❌ Error processing photo.")
    
    async def handle_video_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle video messages"""
        try:
            video = update.message.video
            file_info = await context.bot.get_file(video.file_id)
            
            file_path = await self.download_file(file_info, "videos", "mp4")
            
            message_data = MessageCreate(
                content=update.message.caption or "",
                source_type="telegram",
                source_chat_id=str(update.effective_chat.id),
                source_message_id=str(update.message.message_id),
                sender_name=update.effective_user.full_name,
                sender_id=str(update.effective_user.id),
                timestamp=update.message.date,
                message_type="video",
                file_path=file_path,
                file_type="video/mp4",
                file_size=getattr(video, 'file_size', 0)
            )
            
            await self.message_service.create_message(message_data)
            await update.message.reply_text("🎥 Video stored successfully!")
            
        except Exception as e:
            self.logger.error(f"Error handling video: {e}")
            await update.message.reply_text("❌ Error processing video.")
    
    async def handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio messages"""
        try:
            audio = update.message.audio or update.message.voice
            file_info = await context.bot.get_file(audio.file_id)
            
            file_extension = "ogg" if update.message.voice else "mp3"
            file_path = await self.download_file(file_info, "audio", file_extension)
            
            message_data = MessageCreate(
                content=update.message.caption or "",
                source_type="telegram",
                source_chat_id=str(update.effective_chat.id),
                source_message_id=str(update.message.message_id),
                sender_name=update.effective_user.full_name,
                sender_id=str(update.effective_user.id),
                timestamp=update.message.date,
                message_type="audio",
                file_path=file_path,
                file_type=f"audio/{file_extension}",
                file_size=getattr(audio, 'file_size', 0)
            )
            
            await self.message_service.create_message(message_data)
            await update.message.reply_text("🎵 Audio stored successfully!")
            
        except Exception as e:
            self.logger.error(f"Error handling audio: {e}")
            await update.message.reply_text("❌ Error processing audio.")
    
    async def handle_document_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document messages"""
        try:
            document = update.message.document
            file_info = await context.bot.get_file(document.file_id)
            
            file_extension = document.file_name.split('.')[-1] if '.' in document.file_name else 'bin'
            file_path = await self.download_file(file_info, "documents", file_extension)
            
            message_data = MessageCreate(
                content=update.message.caption or document.file_name,
                source_type="telegram",
                source_chat_id=str(update.effective_chat.id),
                source_message_id=str(update.message.message_id),
                sender_name=update.effective_user.full_name,
                sender_id=str(update.effective_user.id),
                timestamp=update.message.date,
                message_type="document",
                file_path=file_path,
                file_type=document.mime_type or "application/octet-stream",
                file_size=document.file_size
            )
            
            await self.message_service.create_message(message_data)
            await update.message.reply_text("📄 Document stored successfully!")
            
        except Exception as e:
            self.logger.error(f"Error handling document: {e}")
            await update.message.reply_text("❌ Error processing document.")
    
    async def handle_generic_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any message type that wasn't caught by specific handlers"""
        try:
            # Log the message type for debugging
            message_type = "unknown"
            content = ""
            
            if update.message.text:
                message_type = "text"
                content = update.message.text
            elif update.message.caption:
                content = update.message.caption
                if update.message.photo:
                    message_type = "photo_with_caption"
                elif update.message.video:
                    message_type = "video_with_caption"
                else:
                    message_type = "media_with_caption"
            
            # Log for debugging
            self.logger.info(f"Generic message handler: type={message_type}, content_length={len(content)}, is_forwarded={bool(update.message.forward_from_message_id)}")
            
            if content:  # Only process if we have content
                message_data = MessageCreate(
                    content=content,
                    source_type="telegram",
                    source_chat_id=str(update.effective_chat.id),
                    source_message_id=str(update.message.message_id),
                    sender_name=update.effective_user.full_name,
                    sender_id=str(update.effective_user.id),
                    timestamp=update.message.date,
                    message_type=message_type
                )
                
                stored_message = await self.message_service.create_message(message_data)
                
                if stored_message:
                    await update.message.reply_text(
                        f"✅ {message_type.title()} message stored!",
                        reply_to_message_id=update.message.message_id
                    )
            else:
                self.logger.info("No content found in generic message")
                
        except Exception as e:
            self.logger.error(f"Error handling generic message: {e}")
            await update.message.reply_text("❌ Error processing message.")
    
    async def download_file(self, file_info, folder: str, extension: str) -> str:
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
            self.logger.error(f"Error downloading file: {e}")
            return None 