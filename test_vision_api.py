#!/usr/bin/env python3
"""
Test script to validate OpenRouter Vision API functionality.
"""

import asyncio
import os
import base64
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

async def test_vision_api():
    """Test the OpenRouter Vision API with a simple base64 image."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    vision_model = os.getenv("OPENAI_VISION_MODEL", "openai/gpt-4o")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        return False
    
    print(f"🔑 API Key found: {api_key[:20]}...{api_key[-4:] if len(api_key) > 24 else api_key}")
    print(f"🌐 Base URL: {base_url}")
    print(f"👁️ Vision Model: {vision_model}")
    
    # Create a simple test image (1x1 red pixel PNG in base64)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    try:
        # Configure client for OpenRouter
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print("🧪 Testing OpenRouter Vision API connection...")
        
        response = await client.chat.completions.create(
            model=vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What do you see in this image? Describe it briefly."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{test_image_base64}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100
        )
        
        if response and response.choices:
            print("✅ SUCCESS: OpenRouter Vision API is working correctly!")
            print(f"📝 Response: {response.choices[0].message.content}")
            print(f"🔧 Model used: {response.model}")
            print(f"🎯 Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
            return True
        else:
            print("❌ ERROR: Empty response from OpenRouter Vision API")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to OpenRouter Vision API: {str(e)}")
        
        # Check for common error types
        error_str = str(e).lower()
        if "no endpoints found" in error_str or "404" in error_str:
            print("💡 SOLUTION: The vision model is not available on OpenRouter.")
            print(f"   - Try using 'openai/gpt-4-vision-preview' instead of '{vision_model}'")
            print("   - Check available models at https://openrouter.ai/models")
        elif "authentication" in error_str or "api key" in error_str:
            print("💡 SOLUTION: Your API key appears to be invalid or expired.")
            print("   - Check if your OpenRouter API key is correct")
            print("   - Verify your OpenRouter account has credits")
        elif "quota" in error_str or "billing" in error_str:
            print("💡 SOLUTION: You may have exceeded your API quota or have billing issues.")
            print("   - Check your OpenRouter account billing and usage at https://openrouter.ai/credits")
        elif "rate limit" in error_str:
            print("💡 SOLUTION: You're being rate limited. Wait a moment and try again.")
        
        return False

if __name__ == "__main__":
    print("🚀 OpenRouter Vision API Test")
    print("=" * 40)
    
    result = asyncio.run(test_vision_api())
    
    if result:
        print("\n🎉 Your OpenRouter Vision API configuration is working correctly!")
    else:
        print("\n🔧 Please fix the Vision API issues and try again.")
