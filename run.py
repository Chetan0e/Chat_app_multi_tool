#!/usr/bin/env python3
"""
Quick start script for the Multi-Tool Chat App.
This script handles the startup process and provides helpful information.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path(".env")
    if not env_path.exists():
        print("[ERROR] .env file not found!")
        print("   Please create a .env file with your OpenAI API key.")
        print("   Example:")
        print("   OPENAI_API_KEY=your_api_key_here")
        return False
    
    # Check if OPENAI_API_KEY is set
    with open(env_path, 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY=' not in content or 'your_openai_api_key' in content:
            print("[WARNING] Please set your actual OpenAI API key in the .env file.")
            return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import openai
        from pypdf import PdfReader  # pypdf
        from PIL import Image
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("   Please install dependencies with: pip install -r requirements.txt")
        return False

def main():
    """Main startup function."""
    print("Multi-Tool Chat App - Startup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check .env file
    if not check_env_file():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n[INFO] To install dependencies, run:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    print("[SUCCESS] All checks passed!")
    print("\nStarting the Multi-Tool Chat App...")
    print("   Server will be available at: http://localhost:8000")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "localhost", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n[ERROR] Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
