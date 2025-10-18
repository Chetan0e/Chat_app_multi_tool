"""
Telegram Bot integration for the Chat App Multitool.
Handles incoming messages and routes them through the appropriate processors.
"""

import logging
import os
from typing import Optional, Dict, Any
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import asyncio

from config.settings import settings
from . import text_handler, image_handler, pdf_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram Bot handler for the Chat App Multitool."""
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.bot = None
        self.application = None
        
    async def initialize(self):
        """Initialize the Telegram bot application."""
        if not self.bot_token:
            logger.error("Telegram bot token not found in environment variables")
            return False
            
        try:
            # Create application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
            self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
            self.application.add_handler(MessageHandler(filters.Document.PDF, self.handle_pdf))
            
            logger.info("Telegram bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """
🤖 **Welcome to Chat App Multitool!**

I'm your AI-powered assistant that can help you with:

🔤 **Text Processing**: Ask me questions, get summaries, or have conversations
🖼️ **Image Analysis**: Send me images and I'll analyze them for you
📄 **PDF Processing**: Upload PDFs and I'll extract and summarize the content

**How to use:**
- Just send me a text message for AI responses
- Send an image for detailed analysis
- Upload a PDF file for content extraction

Type /help for more information!
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
🆘 **Chat App Multitool Help**

**Available Features:**

🔤 **Text Processing**
- Send any text message
- Ask questions, request summaries, or have conversations
- Powered by OpenAI GPT-4

🖼️ **Image Analysis**
- Send any image (PNG, JPG, GIF, WebP)
- Get detailed descriptions and analysis
- Powered by OpenAI Vision API

📄 **PDF Processing**
- Upload PDF files (max 10MB)
- Extract text and get AI-powered summaries
- Supports multi-page documents

**Commands:**
- /start - Welcome message
- /help - This help message

**Tips:**
- You can send multiple types of content in one conversation
- All processing is done securely and privately
- Files are processed temporarily and not stored permanently

Need more help? Contact support!
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        try:
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            user_text = update.message.text
            logger.info(f"Processing text message from user {update.effective_user.id}")
            
            # Process text through handler
            result = await text_handler.handle_text(user_text)
            
            if "error" in result:
                await update.message.reply_text(
                    f"❌ Error processing your message: {result['error']}"
                )
            else:
                # Split long messages if needed
                response_text = result.get("response", "No response generated")
                await self.send_long_message(update, response_text)
                
                # Send metadata if available
                if result.get("status"):
                    metadata_text = f"📊 Status: {result['status']}"
                    await update.message.reply_text(metadata_text, parse_mode=ParseMode.MARKDOWN)
                    
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error processing your message. Please try again."
            )
    
    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image messages."""
        try:
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            logger.info(f"Processing image from user {update.effective_user.id}")
            
            # Get the largest photo
            photo = update.message.photo[-1]
            
            # Download the image
            photo_file = await photo.get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Create a mock UploadFile object for compatibility
            class MockUploadFile:
                def __init__(self, content: bytes, filename: str, content_type: str):
                    self.content = content
                    self.filename = filename
                    self.content_type = content_type
                    self._position = 0
                
                async def read(self):
                    return self.content
                
                async def seek(self, position: int):
                    self._position = position
            
            mock_file = MockUploadFile(
                content=bytes(photo_bytes),
                filename=f"telegram_image_{photo.file_id}.jpg",
                content_type="image/jpeg"
            )
            
            # Process image through handler
            result = await image_handler.handle_image(mock_file)
            
            if "error" in result:
                await update.message.reply_text(
                    f"❌ Error processing your image: {result['error']}"
                )
            else:
                response_text = result.get("response", "No analysis generated")
                await self.send_long_message(update, f"🖼️ **Image Analysis:**\n\n{response_text}")
                
                # Send metadata
                if result.get("status"):
                    metadata_text = f"📊 Status: {result['status']}"
                    await update.message.reply_text(metadata_text, parse_mode=ParseMode.MARKDOWN)
                    
        except Exception as e:
            logger.error(f"Error handling image: {e}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error processing your image. Please try again."
            )
    
    async def handle_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle PDF document messages."""
        try:
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            logger.info(f"Processing PDF from user {update.effective_user.id}")
            
            document = update.message.document
            
            # Check file size (Telegram limit is 20MB, but we'll use our own limit)
            if document.file_size > settings.max_file_size:
                await update.message.reply_text(
                    f"❌ File too large. Maximum size allowed: {settings.max_file_size / 1024 / 1024:.1f}MB"
                )
                return
            
            # Download the PDF
            pdf_file = await document.get_file()
            pdf_bytes = await pdf_file.download_as_bytearray()
            
            # Create a mock UploadFile object
            class MockUploadFile:
                def __init__(self, content: bytes, filename: str, content_type: str):
                    self.content = content
                    self.filename = filename
                    self.content_type = content_type
                    self._position = 0
                
                async def read(self):
                    return self.content
                
                async def seek(self, position: int):
                    self._position = position
            
            mock_file = MockUploadFile(
                content=bytes(pdf_bytes),
                filename=document.file_name or f"telegram_pdf_{document.file_id}.pdf",
                content_type="application/pdf"
            )
            
            # Process PDF through handler
            result = await pdf_handler.handle_pdf(mock_file, analyze=True)
            
            if "error" in result:
                await update.message.reply_text(
                    f"❌ Error processing your PDF: {result['error']}"
                )
            else:
                response_text = result.get("response", "No content extracted")
                await self.send_long_message(update, f"📄 **PDF Analysis:**\n\n{response_text}")
                
                # Send metadata
                metadata_items = []
                if result.get("page_count"):
                    metadata_items.append(f"Pages: {result['page_count']}")
                if result.get("text_length"):
                    metadata_items.append(f"Text length: {result['text_length']} chars")
                if result.get("status"):
                    metadata_items.append(f"Status: {result['status']}")
                
                if metadata_items:
                    metadata_text = f"📊 {' | '.join(metadata_items)}"
                    await update.message.reply_text(metadata_text)
                    
        except Exception as e:
            logger.error(f"Error handling PDF: {e}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error processing your PDF. Please try again."
            )
    
    async def send_long_message(self, update: Update, text: str, max_length: int = 4096):
        """Send long messages by splitting them if necessary."""
        if len(text) <= max_length:
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        else:
            # Split the message into chunks
            chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await update.message.reply_text(f"{chunk}...", parse_mode=ParseMode.MARKDOWN)
                elif i == len(chunks) - 1:
                    await update.message.reply_text(f"...{chunk}", parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(f"...{chunk}...", parse_mode=ParseMode.MARKDOWN)
    
    async def start_polling(self):
        """Start the bot with polling."""
        if not self.application:
            await self.initialize()
        
        if self.application:
            logger.info("Starting Telegram bot with polling...")
            # Initialize and start polling
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Keep the bot running
            try:
                # Run until interrupted
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping bot...")
            finally:
                # Cleanup
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
    
    async def set_webhook(self, webhook_url: str):
        """Set webhook for the bot."""
        if not self.application:
            await self.initialize()
        
        if self.application:
            logger.info(f"Setting webhook to: {webhook_url}")
            await self.application.bot.set_webhook(url=webhook_url)
    
    async def process_webhook(self, update_data: Dict[str, Any]):
        """Process webhook update."""
        if not self.application:
            await self.initialize()
        
        if self.application:
            update = Update.de_json(update_data, self.application.bot)
            await self.application.process_update(update)

# Global bot instance
telegram_bot = TelegramBot()
