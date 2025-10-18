#!/usr/bin/env python3
"""
Test script to validate OpenAI API key functionality.
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

async def test_openai_api():
    """Test the OpenRouter API key by making a simple request."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "openai/gpt-3.5-turbo")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        return False
    
    if api_key == "your_openai_api_key_here" or api_key == "your_openrouter_api_key_here":
        print("❌ ERROR: Please replace the placeholder API key with your actual OpenRouter API key")
        return False
    
    print(f"🔑 API Key found: {api_key[:20]}...{api_key[-4:] if len(api_key) > 24 else api_key}")
    print(f"🌐 Base URL: {base_url}")
    print(f"🤖 Model: {model}")
    
    try:
        # Configure client for OpenRouter
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print("🧪 Testing OpenRouter API connection...")
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say 'Hello, OpenRouter API test successful!'"}
            ],
            max_tokens=50
        )
        
        if response and response.choices:
            print("✅ SUCCESS: OpenRouter API is working correctly!")
            print(f"📝 Response: {response.choices[0].message.content}")
            print(f"🔧 Model used: {response.model}")
            print(f"🎯 Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
            return True
        else:
            print("❌ ERROR: Empty response from OpenRouter API")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to OpenRouter API: {str(e)}")
        
        # Check for common error types
        error_str = str(e).lower()
        if "authentication" in error_str or "api key" in error_str:
            print("💡 SOLUTION: Your API key appears to be invalid or expired.")
            print("   - Check if your OpenRouter API key is correct")
            print("   - Verify your OpenRouter account has credits at https://openrouter.ai/credits")
            print("   - Make sure the API key has the necessary permissions")
        elif "quota" in error_str or "billing" in error_str:
            print("💡 SOLUTION: You may have exceeded your API quota or have billing issues.")
            print("   - Check your OpenRouter account billing and usage at https://openrouter.ai/credits")
        elif "rate limit" in error_str:
            print("💡 SOLUTION: You're being rate limited. Wait a moment and try again.")
        
        return False

if __name__ == "__main__":
    print("🚀 OpenRouter API Key Test")
    print("=" * 40)
    
    result = asyncio.run(test_openai_api())
    
    if result:
        print("\n🎉 Your OpenRouter API configuration is working correctly!")
    else:
        print("\n🔧 Please fix the OpenRouter API key issues and try again.")
