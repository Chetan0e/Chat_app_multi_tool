"""
Routers module for the Chat App Multitool.
Contains all API route handlers, Telegram bot integration, and Composio ToolRouter.
"""

from . import text_handler, image_handler, pdf_handler
from . import telegram_bot, composio_router

__all__ = [
    "text_handler", 
    "image_handler", 
    "pdf_handler",
    "telegram_bot",
    "composio_router"
]
