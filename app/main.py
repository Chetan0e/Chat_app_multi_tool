"""
Main FastAPI application for the Multi-Tool Chat App.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import settings, validate_settings
from routers import text_handler, image_handler, pdf_handler
from routers.telegram_bot import telegram_bot
from routers.composio_router import composio_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    message: str


class ProcessResponse(BaseModel):
    """Generic processing response model."""
    response: str
    status: str
    metadata: Optional[dict] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Multi-Tool Chat App...")
    
    # Validate settings
    if not validate_settings():
        logger.error("Settings validation failed. Please check your configuration.")
        raise RuntimeError("Invalid configuration")
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_directory, exist_ok=True)
    logger.info(f"Upload directory ready: {settings.upload_directory}")
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Tool Chat App...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def serve_frontend():
    """Serve the main frontend application."""
    return FileResponse("static/index.html")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify the application is running."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        message="Multi-Tool Chat App is running successfully"
    )


@app.get("/api/status", tags=["Status"])
async def api_status():
    """Check API configuration status."""
    from config.settings import settings
    from openai import AsyncOpenAI
    
    status = {
        "openrouter_configured": bool(settings.openai_api_key and settings.openai_api_key != "your_openrouter_api_key_here"),
        "telegram_configured": bool(settings.telegram_bot_token),
        "composio_configured": bool(settings.composio_api_key)
    }
    
    # Test OpenRouter API if configured
    openrouter_status = "not_configured"
    openrouter_message = "OpenRouter API key not configured"
    
    if status["openrouter_configured"]:
        try:
            client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
            test_response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            openrouter_status = "working"
            openrouter_message = "OpenRouter API is working correctly"
        except Exception as e:
            error_str = str(e).lower()
            if "insufficient_quota" in error_str or "quota" in error_str:
                openrouter_status = "quota_exceeded"
                openrouter_message = "OpenRouter API quota exceeded. Please check your credits."
            elif "authentication" in error_str:
                openrouter_status = "auth_failed"
                openrouter_message = "OpenRouter API authentication failed. Check your API key."
            else:
                openrouter_status = "error"
                openrouter_message = f"OpenRouter API error: {str(e)}"
    
    status["openrouter_status"] = openrouter_status
    
    return {
        "status": "ok",
        "services": status,
        "message": openrouter_message
    }


@app.post("/api/process", response_model=ProcessResponse, tags=["Processing"])
async def process_input(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    analyze: bool = Form(True),
    use_router: bool = Form(True)
):
    """
    Process text input or uploaded file using Composio ToolRouter for smart routing.
    
    Args:
        text: Text input to process
        file: File to upload and process
        analyze: Whether to perform AI analysis (for PDFs)
        use_router: Whether to use Composio ToolRouter for smart routing
        
    Returns:
        Processing results with metadata
        
    Raises:
        HTTPException: If no input provided or processing fails
    """
    if not text and not file:
        raise HTTPException(
            status_code=400, 
            detail="Please provide either text input or upload a file."
        )
    
    try:
        if use_router:
            # Use Composio ToolRouter for smart routing
            logger.info("Using Composio ToolRouter for processing")
            context = {"analyze": analyze} if file else None
            result = await composio_router.route_request(text=text, file=file, context=context)
        else:
            # Use direct routing (legacy mode)
            logger.info("Using direct routing for processing")
            if file:
                content_type = file.content_type or ""
                logger.info(f"Processing file: {file.filename} ({content_type})")
                
                if "image" in content_type:
                    result = await image_handler.handle_image(file)
                elif "pdf" in content_type:
                    result = await pdf_handler.handle_pdf(file, analyze=analyze)
                else:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Unsupported file type: {content_type}. Supported types: images (PNG, JPG, JPEG, GIF, WebP) and PDFs."
                    )
            
            elif text:
                logger.info("Processing text input")
                result = await text_handler.handle_text(text)
        
        # Format response
        return ProcessResponse(
            response=result.get("response", ""),
            status=result.get("status", "success"),
            metadata={
                k: v for k, v in result.items() 
                if k not in ["response", "status"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_input: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.post("/webhook/telegram", tags=["Telegram"])
async def telegram_webhook(update: dict):
    """
    Telegram webhook endpoint for receiving bot updates.
    
    Args:
        update: Telegram update object
        
    Returns:
        Success response
    """
    try:
        logger.info("Received Telegram webhook update")
        await telegram_bot.process_webhook(update)
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@app.get("/tools", tags=["Tools"])
async def get_available_tools():
    """Get information about available processing tools."""
    try:
        tools_info = await composio_router.get_available_tools()
        return tools_info
        
    except Exception as e:
        logger.error(f"Error getting tools info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tools information")


@app.get("/router/health", tags=["Health"])
async def router_health_check():
    """Check the health of the Composio router and all tools."""
    try:
        health_info = await composio_router.health_check()
        return health_info
        
    except Exception as e:
        logger.error(f"Error checking router health: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "status": "error"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An internal server error occurred",
            "status_code": 500,
            "status": "error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Server will run on {settings.host}:{settings.port}")
    logger.info("For development, use: uvicorn app.main:app --reload")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )
