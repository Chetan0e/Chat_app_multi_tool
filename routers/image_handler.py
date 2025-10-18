"""
Image processing router using OpenAI Vision API.
"""

import logging
import base64
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from PIL import Image
import io

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client (works with OpenRouter)
client_kwargs = {"api_key": settings.openai_api_key}
if settings.openai_base_url:
    client_kwargs["base_url"] = settings.openai_base_url

client = AsyncOpenAI(**client_kwargs)


class ImageResponse(BaseModel):
    """Response model for image processing."""
    response: str
    filename: str
    file_size: int
    content_type: str
    status: str


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image file.
    
    Args:
        file: Uploaded file to validate
        
    Raises:
        HTTPException: If file is invalid
    """
    if not file.content_type or "image" not in file.content_type:
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    # Check file extension
    allowed_extensions = ["png", "jpg", "jpeg", "gif", "webp"]
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported image format. Allowed: {', '.join(allowed_extensions)}"
        )


async def encode_image_to_base64(file: UploadFile) -> str:
    """
    Convert uploaded image to base64 string.
    
    Args:
        file: Uploaded image file
        
    Returns:
        Base64 encoded image string
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Optimize image if it's too large
        if len(file_content) > 5 * 1024 * 1024:  # 5MB
            image = Image.open(io.BytesIO(file_content))
            
            # Resize if too large
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            file_content = img_byte_arr.getvalue()
        
        # Encode to base64
        return base64.b64encode(file_content).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error encoding image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


async def handle_image(file: UploadFile, prompt: str = None) -> Dict[str, Any]:
    """
    Process an image file using OpenAI Vision API.
    
    Args:
        file: Uploaded image file
        prompt: Optional custom prompt for image analysis
        
    Returns:
        Dictionary containing the AI response and metadata
        
    Raises:
        HTTPException: If processing fails
    """
    validate_image_file(file)
    
    logger.info(f"Processing image: {file.filename} ({file.content_type})")
    
    try:
        # Check if API key is configured
        if not settings.openai_api_key or settings.openai_api_key == "your_openrouter_api_key_here":
            raise HTTPException(
                status_code=500,
                detail="OpenRouter API key is not configured. Please set your OPENAI_API_KEY with your OpenRouter key in the .env file."
            )
        
        # Get file size
        file_content = await file.read()
        file_size = len(file_content)
        
        # Reset file pointer
        await file.seek(0)
        
        # Check file size limit
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Log the configuration being used
        logger.info(f"Using vision model: {settings.openai_vision_model}")
        logger.info(f"Using base URL: {settings.openai_base_url}")
        logger.info(f"Image size: {file_size} bytes")
        
        # Encode image to base64
        base64_image = await encode_image_to_base64(file)
        
        # Prepare the prompt
        default_prompt = "Analyze this image and provide a detailed description of what you see. Include any text, objects, people, scenes, colors, and other relevant details."
        analysis_prompt = prompt or default_prompt
        
        # Call OpenRouter Vision API
        # Use the configured vision model
        vision_model = settings.openai_vision_model
        response = await client.chat.completions.create(
            model=vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": analysis_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=settings.openai_max_tokens,
            temperature=settings.openai_temperature
        )
        
        result = {
            "response": response.choices[0].message.content.strip(),
            "filename": file.filename,
            "file_size": file_size,
            "content_type": file.content_type,
            "status": "success"
        }
        
        logger.info("Image processing completed successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e).lower()
        logger.error(f"Error processing image: {str(e)}")
        
        # Provide specific error messages for common issues
        if "no endpoints found" in error_str or "404" in error_str:
            raise HTTPException(
                status_code=404,
                detail=f"Vision model '{vision_model}' not available on OpenRouter. The model 'openai/gpt-4o' is confirmed to work. Please check available models at https://openrouter.ai/models"
            )
        elif "authentication" in error_str or "api key" in error_str:
            raise HTTPException(
                status_code=401,
                detail="OpenRouter API authentication failed. Please check your API key."
            )
        elif "quota" in error_str or "insufficient" in error_str:
            raise HTTPException(
                status_code=429,
                detail="OpenRouter API quota exceeded. Please check your credits at https://openrouter.ai/credits"
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing image: {str(e)}"
            )
