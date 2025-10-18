"""
Composio ToolRouter integration for smart routing between different AI tools.
Routes between text, image, and PDF processing based on input type and content.
"""

import logging
from typing import Dict, Any, Optional, Union
from fastapi import UploadFile
import asyncio

try:
    from composio import ComposioToolSet, Action
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False
    logging.warning("Composio SDK not available. Install with: pip install composio-core")

from config.settings import settings
from . import text_handler, image_handler, pdf_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComposioRouter:
    """
    Smart router using Composio ToolRouter SDK to route between different processing tools.
    """
    
    def __init__(self):
        self.composio_api_key = getattr(settings, 'composio_api_key', None)
        self.toolset = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize Composio ToolRouter."""
        if not COMPOSIO_AVAILABLE:
            logger.warning("Composio SDK not available, using fallback routing")
            self.initialized = True
            return True
            
        if not self.composio_api_key:
            logger.warning("Composio API key not found, using fallback routing")
            self.initialized = True
            return True
            
        try:
            # Initialize Composio ToolSet
            self.toolset = ComposioToolSet(api_key=self.composio_api_key)
            self.initialized = True
            logger.info("Composio ToolRouter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Composio ToolRouter: {e}")
            self.initialized = True  # Use fallback routing
            return False
    
    async def route_request(
        self, 
        text: Optional[str] = None, 
        file: Optional[UploadFile] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route the request to the appropriate handler based on input type and content.
        
        Args:
            text: Text input to process
            file: File to process
            context: Additional context for routing decisions
            
        Returns:
            Processing results with routing metadata
        """
        if not self.initialized:
            await self.initialize()
        
        routing_info = {
            "router": "composio" if self.toolset else "fallback",
            "input_type": None,
            "tool_used": None,
            "confidence": 1.0
        }
        
        try:
            # Determine input type and route accordingly
            if file:
                routing_info["input_type"] = "file"
                result = await self._route_file(file, context)
                
            elif text:
                routing_info["input_type"] = "text"
                result = await self._route_text(text, context)
                
            else:
                return {
                    "error": "No input provided",
                    "routing_info": routing_info
                }
            
            # Add routing information to result
            result["routing_info"] = routing_info
            return result
            
        except Exception as e:
            logger.error(f"Error in routing request: {e}")
            return {
                "error": f"Routing error: {str(e)}",
                "routing_info": routing_info
            }
    
    async def _route_file(self, file: UploadFile, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route file-based requests."""
        content_type = file.content_type or ""
        filename = file.filename or ""
        
        if "image" in content_type.lower():
            logger.info(f"Routing image file: {filename}")
            return await self._process_with_tool("image", image_handler.handle_image, file)
            
        elif "pdf" in content_type.lower() or filename.lower().endswith('.pdf'):
            logger.info(f"Routing PDF file: {filename}")
            analyze = context.get("analyze", True) if context else True
            return await self._process_with_tool("pdf", pdf_handler.handle_pdf, file, analyze=analyze)
            
        else:
            return {
                "error": f"Unsupported file type: {content_type}",
                "supported_types": ["image/*", "application/pdf"]
            }
    
    async def _route_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route text-based requests."""
        logger.info("Routing text input")
        
        # Use Composio for intelligent routing if available
        if self.toolset:
            try:
                # Analyze text to determine best routing
                routing_decision = await self._analyze_text_for_routing(text)
                logger.info(f"Composio routing decision: {routing_decision}")
            except Exception as e:
                logger.warning(f"Composio routing failed, using fallback: {e}")
                routing_decision = {"tool": "text", "confidence": 0.8}
        else:
            # Fallback routing logic
            routing_decision = await self._fallback_text_routing(text)
        
        # Process with the selected tool
        tool_name = routing_decision.get("tool", "text")
        
        if tool_name == "text":
            return await self._process_with_tool("text", text_handler.handle_text, text)
        else:
            # Default to text processing
            return await self._process_with_tool("text", text_handler.handle_text, text)
    
    async def _analyze_text_for_routing(self, text: str) -> Dict[str, Any]:
        """Use Composio to analyze text and determine optimal routing."""
        if not self.toolset:
            return {"tool": "text", "confidence": 0.8}
        
        try:
            # This is a placeholder for Composio ToolRouter logic
            # In a real implementation, you would use Composio's routing capabilities
            
            # Simple heuristic-based routing for now
            text_lower = text.lower()
            
            if any(keyword in text_lower for keyword in ["image", "picture", "photo", "analyze image"]):
                return {"tool": "image", "confidence": 0.9}
            elif any(keyword in text_lower for keyword in ["pdf", "document", "extract text", "summarize document"]):
                return {"tool": "pdf", "confidence": 0.9}
            else:
                return {"tool": "text", "confidence": 1.0}
                
        except Exception as e:
            logger.error(f"Error in Composio text analysis: {e}")
            return {"tool": "text", "confidence": 0.5}
    
    async def _fallback_text_routing(self, text: str) -> Dict[str, Any]:
        """Fallback routing logic when Composio is not available."""
        text_lower = text.lower()
        
        # Simple keyword-based routing
        if any(keyword in text_lower for keyword in ["image", "picture", "photo"]):
            return {"tool": "image", "confidence": 0.7}
        elif any(keyword in text_lower for keyword in ["pdf", "document"]):
            return {"tool": "pdf", "confidence": 0.7}
        else:
            return {"tool": "text", "confidence": 1.0}
    
    async def _process_with_tool(self, tool_name: str, handler_func, *args, **kwargs) -> Dict[str, Any]:
        """Process request with the specified tool and add metadata."""
        try:
            result = await handler_func(*args, **kwargs)
            
            # Add tool information to result
            if isinstance(result, dict):
                result["tool_used"] = tool_name
                result["processing_time"] = None  # Could add timing here
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing with {tool_name} tool: {e}")
            return {
                "error": f"Processing error with {tool_name} tool: {str(e)}",
                "tool_used": tool_name
            }
    
    async def get_available_tools(self) -> Dict[str, Any]:
        """Get information about available tools."""
        tools_info = {
            "text_processor": {
                "name": "Text Processor",
                "description": "AI-powered text processing using OpenAI GPT-4",
                "input_types": ["text"],
                "capabilities": ["question_answering", "text_generation", "summarization"]
            },
            "image_analyzer": {
                "name": "Image Analyzer",
                "description": "Image analysis using OpenAI Vision API",
                "input_types": ["image/png", "image/jpeg", "image/gif", "image/webp"],
                "capabilities": ["image_description", "object_detection", "text_extraction"]
            },
            "pdf_processor": {
                "name": "PDF Processor",
                "description": "PDF text extraction and analysis",
                "input_types": ["application/pdf"],
                "capabilities": ["text_extraction", "content_summarization", "document_analysis"]
            }
        }
        
        return {
            "available_tools": tools_info,
            "router_type": "composio" if self.toolset else "fallback",
            "composio_available": COMPOSIO_AVAILABLE,
            "initialized": self.initialized
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the router and all tools."""
        health_status = {
            "router_status": "healthy" if self.initialized else "not_initialized",
            "composio_available": COMPOSIO_AVAILABLE,
            "composio_connected": bool(self.toolset),
            "tools_status": {}
        }
        
        # Check individual tool health (simplified)
        try:
            # Test text handler
            test_result = await text_handler.handle_text("Health check")
            health_status["tools_status"]["text_processor"] = "healthy" if "response" in test_result else "error"
        except Exception:
            health_status["tools_status"]["text_processor"] = "error"
        
        # Image and PDF handlers would need actual files to test properly
        health_status["tools_status"]["image_analyzer"] = "available"
        health_status["tools_status"]["pdf_processor"] = "available"
        
        return health_status

# Global router instance
composio_router = ComposioRouter()
