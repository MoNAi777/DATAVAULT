#!/usr/bin/env python3
"""
DataVault Telegram Bot - Simple Synchronous Version
Receives messages from Telegram and forwards them to DataVault API
"""

import logging
import os
import requests
import time
from datetime import datetime
from typing import Optional, Dict, Any

from telegram import Update
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
    
    def initialize(self):
        """Initialize the bot"""
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not provided")
            return False
        
        try:
            # Create Telegram application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            
            # Message handlers
            self.application.add_handler(
                MessageHandler(filters.PHOTO, self.handle_photo_message)
            )
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
            )
            
            logger.info("DataVault Telegram bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    def send_to_api(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Send data to DataVault API using requests"""
        try:
            url = f"{self.api_url}/api/{endpoint}"
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error sending to API: {e}")
            return None
    
    # Command handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Welcome to DataVault Bot!

Forward any messages, images, videos, or documents to me and I'll intelligently store and organize them for you.

Commands:
/help - Show this help message

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
            result = self.send_to_api("messages", message_data)
            
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
                content = "Forwarded message with image"
                logger.info("Found forwarded message with image")
            
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
                "file_path": f"telegram_photo_{update.message.message_id}.jpg",
                "file_type": "image/jpeg",
                "file_size": getattr(photo, 'file_size', 0)
            }
            
            # Send to API
            result = self.send_to_api("messages", message_data)
            
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
    
    def start(self):
        """Start the bot"""
        if not self.initialize():
            return
        
        logger.info("🤖 Starting DataVault Telegram Bot...")
        logger.info("Bot is ready to receive messages!")
        
        try:
            # Start polling
            self.application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Error running bot: {e}")


def main():
    """Main function"""
    bot = DataVaultTelegramBot()
    bot.start()


if __name__ == "__main__":
    main() 