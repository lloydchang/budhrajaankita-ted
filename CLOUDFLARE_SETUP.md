# Cloudflare Workers AI Setup Guide

## Overview

Cloudflare Workers AI is an optional **third provider** in the multi-provider LLM system. It provides an additional layer of redundancy and has a generous free tier (10,000 requests/day).

## Why Add Cloudflare?

### Benefits
- ✅ **10,000 free requests/day** - More than Gemini's 1,500
- ✅ **Additional redundancy** - Third fallback option
- ✅ **Fast inference** - Runs on Cloudflare's edge network
- ✅ **No credit card required** - Free tier doesn't require payment info
- ✅ **Multiple models** - Access to various open-source models

### Use Cases
- High-traffic applications needing more than 1,500 requests/day
- Maximum reliability with 3 providers
- Testing and development without worrying about rate limits

## Setup Instructions

### Step 1: Create Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Sign up for a free account (no credit card required)
3. Verify your email address

### Step 2: Get Your Account ID

1. Log in to https://dash.cloudflare.com/
2. Your Account ID is visible in:
   - **URL:** `https://dash.cloudflare.com/{ACCOUNT_ID}/...`
   - **Sidebar:** Under your account name
   - **Workers & Pages:** In the right sidebar

Example Account ID: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

### Step 3: Create API Token

1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click **"Create Token"**
3. Choose **"Create Custom Token"**
4. Configure the token:
   - **Token name:** `Workers AI API Token`
   - **Permissions:**
     - Account → Workers AI → Read
     - Account → Workers AI → Edit
   - **Account Resources:**
     - Include → Your Account
   - **TTL:** Leave as default (no expiration) or set your preference
5. Click **"Continue to summary"**
6. Click **"Create Token"**
7. **Copy the token** (you won't be able to see it again!)

Example API Token: `abcdef1234567890abcdef1234567890abcdef12`

### Step 4: Add to .env File

Add both credentials to your `.env` file:

```bash
# Cloudflare Workers AI (Optional Third Provider)
CLOUDFLARE_API_KEY=your_actual_api_token_here
CLOUDFLARE_ACCOUNT_ID=your_actual_account_id_here
```

### Step 5: Test the Setup

Run the test script:

```bash
python test_multi_provider.py
```

You should see:

```
📋 Configuration Check:
   GEMINI_API_KEY: ✅ Configured
   OPENROUTER_API_KEY: ✅ Configured
   CLOUDFLARE_API_KEY: ✅ Configured
   CLOUDFLARE_ACCOUNT_ID: ✅ Configured

============================================================
Testing Cloudflare Workers AI
============================================================
📤 Sending test request to Cloudflare...
✅ Cloudflare response: Hello from Cloudflare!
```

## Available Models

Cloudflare Workers AI supports multiple models. The default is Llama 2 7B, but you can change it in `main.py`:

### Current Model
```python
url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/meta/llama-2-7b-chat-fp16"
```

### Other Available Models

| Model | Identifier | Use Case |
|-------|------------|----------|
| **Llama 2 7B** (default) | `@cf/meta/llama-2-7b-chat-fp16` | General chat, fast |
| **Llama 3 8B** | `@cf/meta/llama-3-8b-instruct` | Better quality |
| **Mistral 7B** | `@cf/mistral/mistral-7b-instruct-v0.1` | Good for instructions |
| **Gemma 7B** | `@cf/google/gemma-7b-it` | Google's open model |

To change models, update line 253 in `main.py`:

```python
# Change from:
url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/meta/llama-2-7b-chat-fp16"

# To (for example, Llama 3):
url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/meta/llama-3-8b-instruct"
```

## Rate Limits

### Free Tier
- **10,000 requests per day**
- **No concurrent request limit**
- **No credit card required**

### Paid Tier (Workers Paid Plan - $5/month)
- **Unlimited requests**
- **Higher priority**
- **Faster inference**

## Troubleshooting

### Error: "CLOUDFLARE_API_KEY not configured"
**Solution:** Add `CLOUDFLARE_API_KEY` to your `.env` file

### Error: "CLOUDFLARE_ACCOUNT_ID not configured"
**Solution:** Add `CLOUDFLARE_ACCOUNT_ID` to your `.env` file

### Error: "Authentication error"
**Solution:** 
- Check that your API token is correct
- Verify the token has Workers AI permissions
- Make sure the token hasn't expired

### Error: "Account not found"
**Solution:**
- Double-check your Account ID
- Make sure you're using the Account ID, not the Zone ID

### Error: "Model not found"
**Solution:**
- Verify the model identifier is correct
- Some models may not be available in all regions
- Try using the default Llama 2 model

### Cloudflare is slower than expected
**Solution:**
- Cloudflare runs on edge network, but first request may be slower
- Subsequent requests should be faster
- Consider upgrading to paid tier for priority

## Comparison with Other Providers

| Feature | Gemini | OpenRouter | Cloudflare |
|---------|--------|------------|------------|
| **Free Requests/Day** | 1,500 | Limited | 10,000 |
| **Speed** | Very Fast | Moderate | Fast |
| **Quality** | Excellent | Good | Good |
| **Setup Complexity** | Easy | Easy | Medium |
| **Credit Card Required** | No | No | No |
| **Paid Upgrade** | Yes | Yes | Yes |

## When to Use Cloudflare

### ✅ Use Cloudflare When:
- You need more than 1,500 requests/day
- You want maximum reliability (3 providers)
- You're building a high-traffic application
- You want to avoid rate limiting completely

### ❌ Skip Cloudflare When:
- You're just getting started (Gemini + OpenRouter is enough)
- You have low traffic (< 1,000 requests/day)
- You want the simplest setup possible

## Monitoring Cloudflare Usage

### Check Usage in Dashboard
1. Go to https://dash.cloudflare.com/
2. Navigate to **Workers & Pages** → **AI**
3. View your usage statistics

### Check Usage in Logs
The application logs which provider is used:

```bash
# Cloudflare being used
🟠 Cloudflare Workers AI available for business_plan_roadmap
🔄 Trying Cloudflare Workers AI...
✅ Cloudflare Workers AI succeeded for business_plan_roadmap
```

### Count Cloudflare Requests
```bash
# In your application logs
grep "Cloudflare Workers AI succeeded" logs.txt | wc -l
```

## Security Best Practices

### API Token Security
- ✅ Store in `.env` file (gitignored)
- ✅ Never commit to version control
- ✅ Use tokens with minimal required permissions
- ✅ Rotate tokens periodically
- ✅ Delete unused tokens

### Account ID
- ℹ️ Account ID is not sensitive (it's in URLs)
- ℹ️ Still good practice to keep in `.env`
- ℹ️ No security risk if exposed

## Advanced Configuration

### Adjust Timeout
In `main.py`, line 268:

```python
response = requests.post(
    url=url,
    headers={...},
    json={...},
    timeout=30  # Increase if needed
)
```

### Custom System Prompts
Cloudflare supports the same message format as OpenRouter:

```python
messages = [
    {"role": "system", "content": "Custom system prompt here"},
    {"role": "user", "content": "User message"}
]
```

### Temperature Control
Add temperature to the request (requires modifying `call_cloudflare_api`):

```python
json={
    "messages": messages,
    "temperature": 0.7  # 0.0 to 1.0
}
```

## Migration from 2-Provider to 3-Provider

No code changes needed! The system automatically detects Cloudflare credentials:

**Before (2 providers):**
```
📡 Attempting 2 provider(s) for endpoint
🔵 Google Gemini API available
🟢 OpenRouter API available
```

**After (3 providers):**
```
📡 Attempting 3 provider(s) for endpoint
🔵 Google Gemini API available
🟢 OpenRouter API available
🟠 Cloudflare Workers AI available
```

## Cost Analysis

### Free Tier Capacity
- **Gemini:** 1,500 requests/day = $0
- **OpenRouter:** Rate-limited = $0
- **Cloudflare:** 10,000 requests/day = $0
- **Total:** 11,500+ requests/day = **$0**

### With Caching (70% hit rate)
- **Unique requests:** 11,500
- **Total requests served:** ~38,000/day
- **Cost:** **$0**

### Paid Tier Upgrade Path
If you exceed free tiers:

1. **Cloudflare Workers Paid** ($5/month)
   - Unlimited Workers AI requests
   - Best value for high volume

2. **Gemini Pro** ($0.00025/request)
   - Pay per use
   - Good for moderate volume

3. **OpenRouter Paid** (varies by model)
   - Access to premium models
   - Good for quality requirements

## Conclusion

Cloudflare Workers AI is an excellent addition to your multi-provider setup:

- 🚀 **10,000 free requests/day** - 6x more than Gemini
- 🛡️ **Triple redundancy** - Maximum reliability
- ⚡ **Fast edge inference** - Low latency worldwide
- 💰 **$0 cost** - No credit card required

**Recommended for:** Production applications, high-traffic sites, or anyone wanting maximum reliability.

**Optional for:** Small projects, development, or low-traffic applications.
