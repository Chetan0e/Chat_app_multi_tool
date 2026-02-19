# 🤖 Chat App Multitool - AI Assistant for Telegram & Web

A powerful AI-powered assistant that processes text, analyzes images, and extracts insights from PDFs. Available as both a **Telegram bot** and **web application**.

![Telegram](https://img.shields.io/badge/Telegram-Bot_API-26A5E4?style=flat-square&logo=telegram)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=flat-square&logo=openai)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)

## ✨ What This App Does

🔤 **Text Processing**: Ask questions, get AI responses using GPT-4  
🖼️ **Image Analysis**: Upload images for detailed AI analysis using Vision API  
📄 **PDF Processing**: Extract and summarize content from PDF documents  
🤖 **Telegram Bot**: Chat with the AI directly in Telegram  
🌐 **Web Interface**: Beautiful web app for browser-based interaction  

## 🚀 Quick Start Guide

### Step 1: Get Your API Keys

#### OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### Telegram Bot Token (Optional - for bot features)
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name: `Your Chat Assistant`
4. Choose username: `your_chat_assistant_bot`
5. Copy the token (looks like `1234567890:ABC...`)

### Step 2: Setup Project

#### Download and Install
```bash
# Clone or download this project
cd "Chat_app multi tool"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment
```bash
# Copy example environment file
copy .env.example .env

# Edit .env file and add your keys:
OPENAI_API_KEY=sk-your-openai-key-here
TELEGRAM_BOT_TOKEN=your-telegram-token-here
```

### Step 3: Run the Application

#### Option A: Web Application
```bash
# Start web server
python run.py

# Open browser and go to:
http://localhost:8000
```

#### Option B: Telegram Bot
```bash
# Start Telegram bot
python run_telegram_bot.py

# Your bot is now live! Message it on Telegram
```

#### Option C: Both (Web + Telegram)
```bash
# Start full application with web and webhook support
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🏗️ Project Structure

```
Chat_app multi tool/
├── app/
│   ├── __init__.py
│   └── main.py              # Main FastAPI application
├── routers/
│   ├── __init__.py
│   ├── text_handler.py      # Text processing with GPT-4
│   ├── image_handler.py     # Image analysis with Vision API
│   └── pdf_handler.py       # PDF text extraction and analysis
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── static/
│   ├── index.html           # Frontend HTML
│   ├── style.css            # Modern CSS styling
│   └── script.js            # Enhanced JavaScript
├── tests/                   # Test directory (for future tests)
├── .env                     # Environment variables
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 💬 How to Use

### Web Interface
1. **Open browser** to `http://localhost:8000`
2. **Type a message** or **upload a file** (image/PDF)
3. **Click Process** to get AI response
4. **Copy results** using the copy button

### Telegram Bot
1. **Find your bot** on Telegram (search for the username you created)
2. **Send `/start`** to begin
3. **Send text messages** for AI responses
4. **Send images** for analysis
5. **Upload PDFs** for content extraction

### Example Interactions

#### Text Processing
```
You: "Explain quantum computing in simple terms"
Bot: "Quantum computing is like having a super-powerful calculator that can solve certain problems much faster than regular computers..."
```

#### Image Analysis
```
You: [Upload an image of a cat]
Bot: "🖼️ Image Analysis: This image shows a domestic cat with orange and white fur, sitting on what appears to be a wooden surface..."
```

#### PDF Processing
```
You: [Upload a PDF document]
Bot: "📄 PDF Analysis: This document contains 5 pages discussing market trends in technology. Key points include..."
```

## 🛠️ Tech Stack & Features

### Core Technologies
- **FastAPI**: High-performance web framework
- **OpenAI GPT-4**: Advanced text processing
- **OpenAI Vision**: Image analysis capabilities
- **Telegram Bot API**: Chat interface
- **PyMuPDF**: PDF text extraction
- **Composio ToolRouter**: Smart request routing

### Key Features
- ✅ **Multi-modal AI**: Text, image, and PDF processing
- ✅ **Dual Interface**: Web app + Telegram bot
- ✅ **Smart Routing**: Automatic tool selection
- ✅ **File Upload**: Support for images and PDFs up to 10MB
- ✅ **Real-time Processing**: Fast AI responses
- ✅ **Error Handling**: Robust error management
- ✅ **Responsive Design**: Works on all devices

## 🔧 Configuration Options

### Environment Variables
Edit your `.env` file to customize:

```env
# Required
OPENAI_API_KEY=sk-your-key-here
TELEGRAM_BOT_TOKEN=your-token-here

# Optional Customization
OPENAI_MODEL=gpt-4                    # AI model to use
OPENAI_MAX_TOKENS=1000               # Response length limit
OPENAI_TEMPERATURE=0.7               # Creativity level (0-1)
MAX_FILE_SIZE=10485760               # Max file size (10MB)
HOST=0.0.0.0                         # Server host
PORT=8000                            # Server port
```

## 🚨 Troubleshooting

### Common Issues

#### "OpenAI API Key not found"
- ✅ Check your `.env` file exists
- ✅ Verify the key starts with `sk-`
- ✅ Make sure no extra spaces in the key

#### "Telegram bot not responding"
- ✅ Verify bot token is correct
- ✅ Check bot is running: `python run_telegram_bot.py`
- ✅ Make sure you started the bot with `/start`

#### "Module not found" errors
- ✅ Activate virtual environment: `venv\Scripts\activate`
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Check Python version: `python --version` (need 3.8+)

#### "File too large" error
- ✅ Images/PDFs must be under 10MB
- ✅ Try compressing large files
- ✅ Use supported formats: PNG, JPG, PDF

### Debug Commands
```bash
# Check if OpenAI key works
python -c "from openai import OpenAI; print('OpenAI key valid!')"

# Test Telegram bot token
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Check dependencies
pip list | grep -E "(fastapi|openai|telegram)"
```

## 📱 Usage Examples

### For Students
- **Homework Help**: Ask questions about any subject
- **Image Analysis**: Analyze charts, diagrams, scientific images
- **PDF Summarization**: Quickly summarize research papers

### For Professionals
- **Document Analysis**: Extract key points from reports
- **Image Processing**: Analyze business charts and graphs
- **Quick Research**: Get instant answers to technical questions

### For Developers
- **Code Explanation**: Ask about programming concepts
- **Architecture Analysis**: Upload system diagrams for analysis
- **Documentation**: Summarize technical PDFs

## 🔗 API Endpoints

When running the server, you can access:

- **Web Interface**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Available Tools**: `http://localhost:8000/tools`
- **Process API**: `POST http://localhost:8000/api/process`

## 🎯 What Makes This Special

- **🚀 Easy Setup**: Get running in 5 minutes with simple commands
- **🤖 Dual Interface**: Use via web browser OR Telegram bot
- **🧠 Smart AI**: Powered by OpenAI's latest GPT-4 and Vision models
- **📁 Multi-format**: Handles text, images (PNG/JPG), and PDF documents
- **🔧 Customizable**: Easy to modify and extend for your needs
- **📱 Mobile Ready**: Works perfectly on phones and tablets
- **🔒 Secure**: Your data is processed securely and not stored

## 🎉 You're Ready!

Your Chat App Multitool is now ready to use! Whether you're a student needing homework help, a professional analyzing documents, or a developer exploring AI capabilities, this tool has you covered.

**Start with the web interface** at `http://localhost:8000` or **chat with your Telegram bot** - the choice is yours!

---

**Built with ❤️ using FastAPI, OpenAI GPT-4, and modern Python technologies**
