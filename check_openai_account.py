#!/usr/bin/env python3
"""
Script to help diagnose OpenAI account and billing issues.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main function to provide OpenAI account guidance."""
    
    print("🔍 OpenAI Account Status Checker")
    print("=" * 50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No API key found in .env file")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-4:]}")
    print()
    
    print("📋 **QUOTA EXCEEDED - Here's what to do:**")
    print()
    
    print("1. 💳 **Check Your Billing Dashboard:**")
    print("   → Go to: https://platform.openai.com/account/billing")
    print("   → Check if you have credits remaining")
    print("   → Add a payment method if needed")
    print()
    
    print("2. 📊 **Check Your Usage:**")
    print("   → Go to: https://platform.openai.com/account/usage")
    print("   → See how much you've used this month")
    print("   → Check if you've hit your monthly limit")
    print()
    
    print("3. 💰 **Add Credits or Upgrade:**")
    print("   → For Pay-as-you-go: Add credits to your account")
    print("   → For API limits: Consider upgrading your plan")
    print("   → Free tier users: You may need to add payment info")
    print()
    
    print("4. ⏰ **Wait for Reset (if on free tier):**")
    print("   → Free tier limits reset monthly")
    print("   → Check when your next reset occurs")
    print()
    
    print("5. 🔧 **Alternative Solutions:**")
    print("   → Use a different model (gpt-3.5-turbo is cheaper)")
    print("   → Reduce max_tokens in your requests")
    print("   → Implement request caching to reduce API calls")
    print()
    
    print("📝 **Current Configuration:**")
    print(f"   → Model: {os.getenv('OPENAI_MODEL', 'gpt-4')}")
    print(f"   → Max Tokens: {os.getenv('OPENAI_MAX_TOKENS', '1000')}")
    print(f"   → Temperature: {os.getenv('OPENAI_TEMPERATURE', '0.7')}")
    print()
    
    print("💡 **Quick Fix - Switch to Cheaper Model:**")
    print("   Edit your .env file and change:")
    print("   OPENAI_MODEL=gpt-3.5-turbo")
    print("   (This uses ~10x fewer tokens than gpt-4)")

if __name__ == "__main__":
    main()
