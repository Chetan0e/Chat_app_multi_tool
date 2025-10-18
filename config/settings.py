"""
Application settings and configuration management.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(None, env="OPENAI_BASE_URL")
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    composio_api_key: Optional[str] = Field(None, env="COMPOSIO_API_KEY")
    
    # Telegram Configuration
    telegram_webhook_url: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    
    # WhatsApp Configuration
    whatsapp_access_token: Optional[str] = Field(None, env="WHATSAPP_ACCESS_TOKEN")
    whatsapp_phone_number_id: Optional[str] = Field(None, env="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_webhook_verify_token: Optional[str] = Field(None, env="WHATSAPP_WEBHOOK_VERIFY_TOKEN")
    
    # Server Configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(False, env="DEBUG")
    reload: bool = Field(True, env="RELOAD")
    
    # Application Configuration
    app_name: str = "Multi-Tool Chat App"
    app_version: str = "1.0.0"
    app_description: str = "A professional application to handle text, images, and PDFs using AI"
    
    # File Upload Configuration
    max_file_size: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    upload_directory: str = Field("./uploads", env="UPLOAD_DIRECTORY")
    allowed_file_types: list = ["pdf", "png", "jpg", "jpeg", "gif", "webp"]
    
    # OpenAI Configuration
    openai_model: str = Field("gpt-4", env="OPENAI_MODEL")
    openai_vision_model: str = Field("openai/gpt-4o", env="OPENAI_VISION_MODEL")
    openai_max_tokens: int = Field(1000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(0.7, env="OPENAI_TEMPERATURE")
    
    # Security Configuration
    webhook_secret: Optional[str] = Field(None, env="WEBHOOK_SECRET")
    allowed_origins: Optional[str] = Field(None, env="ALLOWED_ORIGINS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def validate_settings() -> bool:
    """Validate that all required settings are properly configured."""
    try:
        if not settings.openai_api_key:
            print("[WARNING] OpenAI API Key not found. AI features will not work until you set OPENAI_API_KEY in your .env file.")
            print("[INFO] Copy .env.example to .env and add your OpenAI API key to enable AI features.")
            # Don't return False - let the app start but warn about missing API key
        
        print("[SUCCESS] Settings validation completed.")
        return True
    except Exception as e:
        print(f"[ERROR] Settings validation failed: {e}")
        return False
