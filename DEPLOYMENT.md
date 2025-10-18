# 🚀 Deployment Guide - Chat App Multitool

This guide covers deployment options for the Chat App Multitool with Telegram/WhatsApp integration.

## 📋 Pre-Deployment Checklist

### Required API Keys
- ✅ **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- ✅ **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)
- ✅ **Composio API Key**: Get from [Composio Dashboard](https://app.composio.dev/)
- ⚠️ **WhatsApp Access Token** (optional): Get from [Meta Developers](https://developers.facebook.com/docs/whatsapp/cloud-api)

### Environment Setup
1. Copy `.env.example` to `.env`
2. Fill in all required API keys
3. Configure webhook URLs for production

## 🌐 Deployment Options

### 1. Railway Deployment (Recommended)

Railway provides easy deployment with automatic HTTPS and webhooks.

#### Step 1: Prepare for Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

#### Step 2: Create railway.json
```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

#### Step 3: Deploy
```bash
# Initialize Railway project
railway init

# Add environment variables
railway variables set OPENAI_API_KEY=your_key_here
railway variables set TELEGRAM_BOT_TOKEN=your_token_here
railway variables set COMPOSIO_API_KEY=your_key_here

# Deploy
railway up
```

#### Step 4: Set Webhook
```bash
# Get your Railway URL
railway domain

# Set Telegram webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-app.railway.app/webhook/telegram"}'
```

### 2. Render Deployment

Render offers free tier with automatic deployments from Git.

#### Step 1: Create render.yaml
```yaml
services:
  - type: web
    name: chat-app-multitool
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: COMPOSIO_API_KEY
        sync: false
```

#### Step 2: Deploy
1. Connect your GitHub repository to Render
2. Add environment variables in Render dashboard
3. Deploy automatically on git push

### 3. Google Cloud Run

For scalable serverless deployment.

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Step 2: Deploy to Cloud Run
```bash
# Build and deploy
gcloud run deploy chat-app-multitool \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key,TELEGRAM_BOT_TOKEN=your_token
```

### 4. Heroku Deployment

#### Step 1: Create Procfile
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Step 2: Deploy
```bash
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set COMPOSIO_API_KEY=your_key

# Deploy
git push heroku main
```

## 🔧 Production Configuration

### Environment Variables for Production
```env
# Production settings
DEBUG=False
RELOAD=False
HOST=0.0.0.0
PORT=8080

# Security
WEBHOOK_SECRET=your_secure_random_string
ALLOWED_ORIGINS=https://your-domain.com

# Performance
MAX_FILE_SIZE=20971520  # 20MB
OPENAI_MAX_TOKENS=2000
```

### Webhook Security
Add webhook verification:

```python
# In your webhook endpoint
import hmac
import hashlib

def verify_webhook(request_body: bytes, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

## 📊 Monitoring and Logging

### Add Structured Logging
```python
import structlog

logger = structlog.get_logger()

# In your handlers
logger.info("Processing request", 
           user_id=user_id, 
           input_type=input_type,
           processing_time=processing_time)
```

### Health Check Endpoint
The app includes `/health` and `/router/health` endpoints for monitoring.

### Error Tracking
Consider adding Sentry for error tracking:

```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
)
```

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit `.env` files
- Use platform-specific secret management
- Rotate API keys regularly

### 2. Rate Limiting
Add rate limiting to prevent abuse:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/process")
@limiter.limit("10/minute")
async def process_input(request: Request, ...):
    # Your endpoint logic
```

### 3. Input Validation
- Validate file sizes and types
- Sanitize text inputs
- Implement request timeouts

## 🧪 Testing in Production

### 1. Test Telegram Bot
```bash
# Send test message to your bot
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
     -H "Content-Type: application/json" \
     -d '{"chat_id": "YOUR_CHAT_ID", "text": "Test message"}'
```

### 2. Test API Endpoints
```bash
# Test health endpoint
curl https://your-app.railway.app/health

# Test processing endpoint
curl -X POST https://your-app.railway.app/api/process \
     -F "text=Hello, test message"
```

### 3. Load Testing
Use tools like `wrk` or `artillery` to test performance:

```bash
# Install artillery
npm install -g artillery

# Create test script
artillery quick --count 10 --num 5 https://your-app.railway.app/health
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use multiple instances behind a load balancer
- Implement session affinity for Telegram webhooks
- Consider using Redis for shared state

### Database Integration
For persistent storage:

```python
# Add to requirements.txt
# sqlalchemy==2.0.23
# alembic==1.12.1

# Database models
from sqlalchemy import create_database_url
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
```

### File Storage
For production file handling:

```python
# Google Cloud Storage
from google.cloud import storage

# AWS S3
import boto3
```

## 🎯 Go-Live Checklist

- [ ] All API keys configured
- [ ] Webhooks set and tested
- [ ] Health checks passing
- [ ] Error monitoring configured
- [ ] Rate limiting enabled
- [ ] SSL/HTTPS enabled
- [ ] Domain configured
- [ ] Backup strategy in place
- [ ] Monitoring dashboards set up
- [ ] Documentation updated

## 🆘 Troubleshooting

### Common Issues

1. **Webhook not receiving updates**
   - Check webhook URL is accessible
   - Verify SSL certificate
   - Check Telegram webhook status: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

2. **OpenAI API errors**
   - Verify API key is valid
   - Check rate limits and quotas
   - Monitor usage in OpenAI dashboard

3. **Memory/timeout issues**
   - Increase server memory allocation
   - Implement request timeouts
   - Optimize file processing

### Debug Commands
```bash
# Check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Test bot commands
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# Check app logs
railway logs  # For Railway
heroku logs --tail  # For Heroku
```

---

**Need help?** Join the [Composio Discord](https://discord.gg/PPUtg6uz) for technical support!
