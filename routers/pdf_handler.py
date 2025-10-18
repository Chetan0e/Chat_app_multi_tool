"""
PDF processing router with text extraction and AI analysis.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from pypdf import PdfReader
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


class PDFResponse(BaseModel):
    """Response model for PDF processing."""
    response: str
    filename: str
    file_size: int
    page_count: int
    text_length: int
    status: str


def validate_pdf_file(file: UploadFile) -> None:
    """
    Validate uploaded PDF file.
    
    Args:
        file: Uploaded file to validate
        
    Raises:
        HTTPException: If file is invalid
    """
    if not file.content_type or "pdf" not in file.content_type.lower():
        raise HTTPException(status_code=400, detail="File must be a PDF.")
    
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must have a .pdf extension.")


async def extract_text_from_pdf(file: UploadFile) -> Dict[str, Any]:
    """
    Extract text from PDF file.
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        Dictionary containing extracted text and metadata
        
    Raises:
        HTTPException: If extraction fails
    """
    try:
        # Read the file content into memory
        file_bytes = await file.read()
        file_size = len(file_bytes)
        
        # Check file size limit
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Open the PDF from bytes using pypdf
        pdf_stream = io.BytesIO(file_bytes)
        pdf_reader = PdfReader(pdf_stream)
        
        # Extract text from all pages
        extracted_text = ""
        page_count = len(pdf_reader.pages)
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            
            if page_text.strip():
                extracted_text += f"\n--- Page {page_num + 1} ---\n"
                extracted_text += page_text
        
        return {
            "text": extracted_text.strip(),
            "page_count": page_count,
            "file_size": file_size,
            "text_length": len(extracted_text)
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


async def analyze_pdf_content(text: str) -> Dict[str, Any]:
    """
    Analyze extracted PDF content using OpenAI.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        Dictionary containing AI analysis and metadata
    """
    try:
        # Truncate text if too long (to stay within token limits)
        max_chars = 8000  # Approximate limit to stay within token constraints
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Content truncated due to length...]"
        
        prompt = f"""
        Analyze the following PDF content and provide a comprehensive summary including:
        1. Main topics and themes
        2. Key points and important information
        3. Document structure and organization
        4. Any notable findings or insights
        
        PDF Content:
        {text}
        """
        
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional document analyzer. Provide clear, structured summaries of document content."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=settings.openai_max_tokens,
            temperature=settings.openai_temperature
        )
        
        return {
            "analysis": response.choices[0].message.content.strip()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing PDF content: {str(e)}")
        # Return the raw text if AI analysis fails
        return {
            "analysis": f"Text extracted successfully but AI analysis failed: {str(e)}\n\nRaw content:\n{text}"
        }


async def handle_pdf(file: UploadFile, analyze: bool = True) -> Dict[str, Any]:
    """
    Process a PDF file by extracting text and optionally analyzing it with AI.
    
    Args:
        file: Uploaded PDF file
        analyze: Whether to perform AI analysis of the content
        
    Returns:
        Dictionary containing the processing results and metadata
        
    Raises:
        HTTPException: If processing fails
    """
    validate_pdf_file(file)
    
    logger.info(f"Processing PDF: {file.filename}")
    
    try:
        # Extract text from PDF
        extraction_result = await extract_text_from_pdf(file)
        
        if not extraction_result["text"]:
            return {
                "response": "The PDF contains no extractable text or the text could not be read.",
                "filename": file.filename,
                "file_size": extraction_result["file_size"],
                "page_count": extraction_result["page_count"],
                "text_length": 0,
                "status": "no_text"
            }
        
        # Analyze content with AI if requested
        if analyze and extraction_result["text"]:
            analysis_result = await analyze_pdf_content(extraction_result["text"])
            response_text = analysis_result["analysis"]
        else:
            response_text = extraction_result["text"]
        
        result = {
            "response": response_text,
            "filename": file.filename,
            "file_size": extraction_result["file_size"],
            "page_count": extraction_result["page_count"],
            "text_length": extraction_result["text_length"],
            "status": "success"
        }
        
        logger.info(f"PDF processing completed successfully. Pages: {result['page_count']}, Text length: {result['text_length']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing PDF: {str(e)}"
        )
