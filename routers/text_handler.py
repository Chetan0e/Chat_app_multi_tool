"""
Text processing router using OpenAI API.
"""

import logging
from typing import Dict, Any
from fastapi import HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client (works with OpenRouter)
client_kwargs = {"api_key": settings.openai_api_key}
if settings.openai_base_url:
    client_kwargs["base_url"] = settings.openai_base_url

client = AsyncOpenAI(**client_kwargs)


class TextRequest(BaseModel):
    """Request model for text processing."""
    text: str
    max_tokens: int = settings.openai_max_tokens
    temperature: float = settings.openai_temperature


class TextResponse(BaseModel):
    """Response model for text processing."""
    response: str
    status: str


async def handle_text(text: str) -> Dict[str, Any]:
    """
    Process text using OpenAI API and return the response.
    
    Args:
        text: Input text to process
        
    Returns:
        Dictionary containing the AI response and metadata
        
    Raises:
        HTTPException: If processing fails
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="No text provided or text is empty.")
    
    logger.info(f"Processing text request with {len(text)} characters")
    
    try:
        # Check if API key is configured
        if not settings.openai_api_key or settings.openai_api_key == "your_openrouter_api_key_here":
            raise HTTPException(
                status_code=500,
                detail="OpenRouter API key is not configured. Please set your OPENAI_API_KEY with your OpenRouter key in the .env file."
            )
        
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful, knowledgeable, and professional AI assistant. Provide clear, accurate, and helpful responses."
                },
                {"role": "user", "content": text}
            ],
            max_tokens=settings.openai_max_tokens,
            temperature=settings.openai_temperature
        )
        
        result = {
            "response": response.choices[0].message.content.strip(),
            "status": "success"
        }
        
        logger.info("Text processing completed successfully")
        return result
        
    except Exception as e:
        error_str = str(e).lower()
        logger.error(f"Error processing text with OpenAI: {str(e)}")
        
        # Provide specific error messages for common issues
        if "insufficient_quota" in error_str or "quota" in error_str:
            raise HTTPException(
                status_code=429,
                detail="OpenRouter API quota exceeded. Please check your credits at https://openrouter.ai/credits"
            )
        elif "authentication" in error_str or "api key" in error_str:
            raise HTTPException(
                status_code=401,
                detail="OpenRouter API authentication failed. Please check your API key in the .env file."
            )
        elif "rate limit" in error_str:
            raise HTTPException(
                status_code=429,
                detail="OpenRouter API rate limit exceeded. Please wait a moment and try again."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing text with OpenRouter: {str(e)}"
            )
