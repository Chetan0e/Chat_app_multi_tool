#!/usr/bin/env python3
"""
Test script to validate OpenRouter API key functionality.
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

async def test_openrouter_api():
    """Test the OpenRouter API key by making a simple request."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "openai/gpt-3.5-turbo")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        return False
    
    if api_key == "your_openrouter_api_key_here":
        print("❌ ERROR: Please replace the placeholder API key with your actual OpenRouter API key")
        print("💡 Get your API key from: https://openrouter.ai/keys")
        return False
    
    if not base_url:
        print("❌ ERROR: OPENAI_BASE_URL not found. Should be: https://openrouter.ai/api/v1")
        return False
    
    print(f"🔑 API Key found: {api_key[:20]}...{api_key[-4:] if len(api_key) > 24 else api_key}")
    print(f"🌐 Base URL: {base_url}")
    print(f"🤖 Model: {model}")
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print("🧪 Testing OpenRouter API connection...")
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say 'Hello, OpenRouter test successful!'"}
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
        if "authentication" in error_str or "api key" in error_str or "unauthorized" in error_str:
            print("💡 SOLUTION: Your OpenRouter API key appears to be invalid.")
            print("   - Get your API key from: https://openrouter.ai/keys")
            print("   - Make sure you've copied the key correctly")
            print("   - Check if your account is active")
        elif "quota" in error_str or "billing" in error_str or "credits" in error_str:
            print("💡 SOLUTION: You may have insufficient credits.")
            print("   - Check your credits at: https://openrouter.ai/credits")
            print("   - Add credits to your account if needed")
        elif "rate limit" in error_str:
            print("💡 SOLUTION: You're being rate limited. Wait a moment and try again.")
        elif "model" in error_str:
            print(f"💡 SOLUTION: The model '{model}' may not be available.")
            print("   - Try a different model like 'openai/gpt-3.5-turbo'")
            print("   - Check available models at: https://openrouter.ai/docs")
        
        return False

if __name__ == "__main__":
    print("🚀 OpenRouter API Key Test")
    print("=" * 40)
    
    result = asyncio.run(test_openrouter_api())
    
    if result:
        print("\n🎉 Your OpenRouter API configuration is working correctly!")
        print("\n📚 Available models you can use:")
        print("   - openai/gpt-3.5-turbo (Fast & cheap)")
        print("   - openai/gpt-4 (More capable)")
        print("   - anthropic/claude-3-haiku (Fast)")
        print("   - anthropic/claude-3-sonnet (Balanced)")
        print("   - meta-llama/llama-2-70b-chat (Open source)")
        print("   - And many more at: https://openrouter.ai/docs")
    else:
        print("\n🔧 Please fix the OpenRouter API issues and try again.")
        print("📖 Setup guide: https://openrouter.ai/docs/quick-start")
