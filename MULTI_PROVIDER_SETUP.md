# Multi-Provider LLM Setup

## Overview

The application now uses a **multi-provider fallback system** for LLM API calls to improve reliability and reduce rate limiting issues.

## Provider Priority

1. **Google Gemini API** (Primary) - `gemini-2.0-flash-exp` model
2. **OpenRouter API** (Fallback) - `meta-llama/llama-3.2-3b-instruct:free` model

## How It Works

When an endpoint needs to generate content:

1. **Cache Check**: First checks if a cached response exists (24-hour TTL)
2. **Provider 1 (Gemini)**: Attempts to use Google Gemini API if `GEMINI_API_KEY` is configured
3. **Provider 2 (OpenRouter)**: Falls back to OpenRouter if Gemini fails or is not configured
4. **Error Handling**: Returns an error only if all providers fail

## Configuration

### Required Environment Variables

Add to your `.env` file:

```bash
# Primary Provider (Recommended)
GEMINI_API_KEY=your_gemini_api_key_here

# Fallback Provider
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Audio Generation
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### Getting API Keys

- **Gemini API**: https://aistudio.google.com/app/apikey (Free tier available)
- **OpenRouter API**: https://openrouter.ai/keys (Free models available)
- **ElevenLabs API**: https://elevenlabs.io/app/settings/api-keys

## Benefits

### 1. **Reduced Rate Limiting**
- Distributes requests across multiple providers
- Gemini has generous free tier limits
- OpenRouter provides backup when Gemini is rate-limited

### 2. **Improved Reliability**
- Automatic failover if one provider is down
- No single point of failure
- Continues working even if one API key expires

### 3. **Cost Optimization**
- Uses free Gemini tier first
- Falls back to free OpenRouter models only when needed
- Caching reduces total API calls

### 4. **Better Performance**
- Gemini 2.0 Flash is faster than Llama 3.2
- Lower latency for most requests
- Cached responses return instantly

## Logging

The system provides detailed logging for debugging:

```
✅ Cache hit for business_plan_roadmap
🔵 Google Gemini API available for investors
🟢 OpenRouter API available for investors
📡 Attempting 2 provider(s) for investors
🔄 Trying Google Gemini...
✅ Google Gemini succeeded for investors
```

Or if Gemini fails:

```
🔄 Trying Google Gemini...
❌ Google Gemini failed: GEMINI_API_KEY not configured
🔄 Trying OpenRouter...
✅ OpenRouter succeeded for investors
```

## Testing

To test the multi-provider setup:

```bash
# Start the server
uvicorn main:app --reload --port 8001

# Make a test request to any endpoint
curl -X POST http://127.0.0.1:8001/business_plan_roadmap \
  -H "Content-Type: application/json" \
  -d '{"idea": {"name": "Test", "mission": "Test mission", "goals": [], "targetMarket": {}, "primaryProduct": "Test", "sdgs": []}}'
```

Watch the console logs to see which provider is being used.

## Troubleshooting

### Issue: "No LLM API keys configured"
**Solution**: Add at least one API key (GEMINI_API_KEY or OPENROUTER_API_KEY) to your `.env` file

### Issue: "All LLM providers failed"
**Solution**: 
- Check that your API keys are valid
- Verify you haven't exceeded rate limits on both providers
- Check your internet connection
- Review the error logs for specific provider failures

### Issue: Still getting rate limited
**Solution**:
- The cache should prevent most duplicate requests
- Rate limiter enforces 60-second intervals between calls
- Consider upgrading to paid tiers for higher limits
- Add more providers to the fallback chain

## Advanced Configuration

### Adjusting Rate Limits

In `main.py`, modify the rate limiter initialization:

```python
# Default: 60 seconds between calls
rate_limiter = RateLimiter(min_interval_seconds=60)

# More aggressive: 30 seconds
rate_limiter = RateLimiter(min_interval_seconds=30)

# More conservative: 120 seconds
rate_limiter = RateLimiter(min_interval_seconds=120)
```

### Adjusting Cache TTL

In `main.py`, modify the cache initialization:

```python
# Default: 24 hours
cache = ResponseCache(cache_dir=".cache", ttl_hours=24)

# Shorter: 1 hour
cache = ResponseCache(cache_dir=".cache", ttl_hours=1)

# Longer: 7 days
cache = ResponseCache(cache_dir=".cache", ttl_hours=168)
```

### Changing Provider Order

To prioritize OpenRouter over Gemini, modify the provider list in `make_openrouter_request()`:

```python
# Build list of available providers
providers = []
if OPENROUTER_API_KEY:  # OpenRouter first
    providers.append(("OpenRouter", lambda msgs: call_openrouter_api(msgs, max_retries)))
if GEMINI_API_KEY:  # Gemini second
    providers.append(("Google Gemini", call_gemini_api))
```

## Migration Notes

### From Previous Version

The function signature for `make_openrouter_request()` remains the same, so no changes are needed in endpoint code. The function now:

1. Tries Gemini first (if configured)
2. Falls back to OpenRouter (if configured)
3. Returns responses in the same format

All existing endpoints will automatically benefit from the multi-provider system.
