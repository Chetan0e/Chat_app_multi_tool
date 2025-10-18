# OpenRouter Setup Guide

## 🚀 What is OpenRouter?

OpenRouter is a unified API that provides access to multiple AI models from different providers (OpenAI, Anthropic, Meta, Google, etc.) through a single interface. It's often more cost-effective than using OpenAI directly and offers more model choices.

## 📋 Setup Steps

### 1. Create an OpenRouter Account
- Go to [https://openrouter.ai](https://openrouter.ai)
- Sign up for a free account
- Verify your email address

### 2. Get Your API Key
- Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
- Click "Create Key"
- Copy your API key (starts with `sk-or-`)

### 3. Add Credits (Optional but Recommended)
- Go to [https://openrouter.ai/credits](https://openrouter.ai/credits)
- Add credits to your account ($5-10 is usually enough to start)
- OpenRouter has pay-per-use pricing, often cheaper than OpenAI

### 4. Update Your .env File
Replace your current API configuration with:

```env
# OpenRouter Configuration (replaces OpenAI)
OPENAI_API_KEY=sk-or-your-actual-openrouter-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# OpenRouter Model Configuration
OPENAI_MODEL=openai/gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
```

### 5. Test Your Configuration
Run the test script:
```bash
python test_openrouter.py
```

## 🤖 Available Models

OpenRouter provides access to many models. Here are some popular options:

### **OpenAI Models**
- `openai/gpt-3.5-turbo` - Fast and cost-effective
- `openai/gpt-4` - More capable but pricier
- `openai/gpt-4-turbo` - Latest GPT-4 variant

### **Anthropic Models**
- `anthropic/claude-3-haiku` - Fast and efficient
- `anthropic/claude-3-sonnet` - Balanced performance
- `anthropic/claude-3-opus` - Most capable

### **Open Source Models**
- `meta-llama/llama-2-70b-chat` - Free to use
- `mistralai/mistral-7b-instruct` - Fast and free
- `google/palm-2-chat-bison` - Google's model

### **Specialized Models**
- `openai/gpt-4-vision-preview` - For image analysis
- `anthropic/claude-3-opus` - Excellent for coding

## 💰 Pricing Benefits

OpenRouter often offers better pricing than direct API access:
- **Competitive rates**: Often 10-50% cheaper than direct access
- **No monthly minimums**: Pay only for what you use
- **Free models available**: Some open-source models are free
- **Transparent pricing**: See costs upfront at [https://openrouter.ai/docs](https://openrouter.ai/docs)

## 🔧 Configuration Options

You can easily switch models by changing the `OPENAI_MODEL` in your `.env` file:

```env
# For cost-effectiveness
OPENAI_MODEL=openai/gpt-3.5-turbo

# For better performance
OPENAI_MODEL=anthropic/claude-3-sonnet

# For free usage (open source)
OPENAI_MODEL=meta-llama/llama-2-70b-chat
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Authentication Error**
   - Make sure your API key starts with `sk-or-`
   - Verify the key is copied correctly
   - Check your account is active

2. **Insufficient Credits**
   - Add credits at [https://openrouter.ai/credits](https://openrouter.ai/credits)
   - Some models are free (check the pricing page)

3. **Model Not Found**
   - Check available models at [https://openrouter.ai/docs](https://openrouter.ai/docs)
   - Make sure the model name is correct (case-sensitive)

4. **Rate Limits**
   - OpenRouter has generous rate limits
   - If hit, wait a moment and retry

## 📚 Additional Resources

- **Documentation**: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- **Model List**: [https://openrouter.ai/docs#models](https://openrouter.ai/docs#models)
- **Pricing**: [https://openrouter.ai/docs#pricing](https://openrouter.ai/docs#pricing)
- **Support**: [https://openrouter.ai/discord](https://openrouter.ai/discord)

## ✅ Verification

After setup, your chat app will:
- Use OpenRouter instead of OpenAI directly
- Have access to multiple AI models
- Potentially save money on API costs
- Provide better error handling and model flexibility

Run `python test_openrouter.py` to verify everything is working!
