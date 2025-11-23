# Quick Start Guide - Multi-Provider LLM Setup

## ⚡ Quick Setup (2 minutes)

### Step 1: Get Your Gemini API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

### Step 2: Add to .env File
```bash
# Open your .env file and add:
GEMINI_API_KEY=AIza...your_actual_key_here
```

### Step 3: Test It
```bash
# Run the test script
python test_multi_provider.py
```

### Step 4: Start Your Server
```bash
uvicorn main:app --reload --port 8001
```

## ✅ What You'll See

### Before (Rate Limited)
```
INFO: 127.0.0.1:61330 - "POST /business_plan_roadmap HTTP/1.1" 429 Too Many Requests
Rate limited. Waiting 2 seconds before retry 1/3
Rate limited. Waiting 4 seconds before retry 2/3
Rate limited. Waiting 8 seconds before retry 3/3
```

### After (Working!)
```
🔵 Google Gemini API available for business_plan_roadmap
🟢 OpenRouter API available for business_plan_roadmap
📡 Attempting 2 provider(s) for business_plan_roadmap
🔄 Trying Google Gemini...
✅ Google Gemini succeeded for business_plan_roadmap
INFO: 127.0.0.1:61330 - "POST /business_plan_roadmap HTTP/1.1" 200 OK
```

## 🎯 Key Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Rate Limiting** | Frequent 429 errors | Distributed across 2 providers |
| **Reliability** | Single point of failure | Automatic failover |
| **Speed** | Llama 3.2 (slower) | Gemini 2.0 Flash (faster) |
| **Cost** | Free tier only | 2x free tier capacity |

## 📊 Provider Details

### Provider 1: Google Gemini (Primary)
- **Model:** `gemini-2.0-flash-exp`
- **Free Tier:** 1,500 requests/day
- **Speed:** Very fast (~1-2 seconds)
- **Quality:** Excellent

### Provider 2: OpenRouter (Fallback)
- **Model:** `meta-llama/llama-3.2-3b-instruct:free`
- **Free Tier:** Limited by rate limits
- **Speed:** Moderate (~2-4 seconds)
- **Quality:** Good

## 🔍 Troubleshooting

### "No LLM API keys configured"
**Fix:** Add `GEMINI_API_KEY` to your `.env` file

### "GEMINI_API_KEY not configured"
**Fix:** Make sure you saved the `.env` file and restart the server

### Still getting rate limited
**Fix:** 
1. Check cache is working (should see `✅ Cache hit` messages)
2. Wait 60 seconds between unique requests
3. Both providers might be rate-limited (rare)

## 📚 More Information

- **Full Documentation:** See `MULTI_PROVIDER_SETUP.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Test Script:** Run `python test_multi_provider.py`

## 🚀 That's It!

You're now using a multi-provider LLM system that:
- ✅ Reduces rate limiting
- ✅ Improves reliability
- ✅ Increases speed
- ✅ Optimizes costs

No code changes needed - it just works! 🎉
