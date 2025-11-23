# Multi-Provider Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      API Request                            │
│              (e.g., /business_plan_roadmap)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Check Cache? │
                  └──────┬───────┘
                         │
              ┌──────────┴──────────┐
              │                     │
           YES│                     │NO
              │                     │
              ▼                     ▼
    ┌──────────────────┐   ┌──────────────────────┐
    │ Return Cached    │   │ Build Provider List  │
    │ Response ✅      │   │ (Gemini + OpenRouter)│
    └──────────────────┘   └──────┬───────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ Try Provider 1:  │
                         │ Google Gemini 🔵 │
                         └────────┬─────────┘
                                  │
                       ┌──────────┴──────────┐
                       │                     │
                   SUCCESS                 FAIL
                       │                     │
                       ▼                     ▼
            ┌──────────────────┐   ┌──────────────────┐
            │ Cache Response   │   │ Try Provider 2:  │
            │ Return to Client │   │ OpenRouter 🟢    │
            │ ✅               │   └────────┬─────────┘
            └──────────────────┘            │
                                 ┌──────────┴──────────┐
                                 │                     │
                             SUCCESS                 FAIL
                                 │                     │
                                 ▼                     ▼
                      ┌──────────────────┐   ┌──────────────┐
                      │ Cache Response   │   │ Return Error │
                      │ Return to Client │   │ 500 ❌       │
                      │ ✅               │   └──────────────┘
                      └──────────────────┘
```

## Provider Priority

### 1️⃣ Google Gemini (Primary)
- **Model:** gemini-2.0-flash-exp
- **Free Tier:** 1,500 requests/day
- **Latency:** ~1-2 seconds
- **Use Case:** Primary provider for all requests

### 2️⃣ OpenRouter (Fallback)
- **Model:** meta-llama/llama-3.2-3b-instruct:free
- **Free Tier:** Rate-limited
- **Latency:** ~2-4 seconds
- **Use Case:** Backup when Gemini fails or is rate-limited

## Cache Strategy

```
Request Hash ──┐
               │
               ├─► Check .cache/{endpoint}/{hash}.json
               │
               ├─► If exists & not expired (< 24h)
               │   └─► Return cached response ✅
               │
               └─► If not exists or expired
                   └─► Call LLM provider
                       └─► Cache response
                           └─► Return response
```

## Rate Limiting Strategy

```
Provider: Gemini
├─► Track last call time
├─► If < 60 seconds since last call
│   └─► Wait (60 - elapsed) seconds
└─► Make API call

Provider: OpenRouter
├─► Track last call time
├─► If < 60 seconds since last call
│   └─► Wait (60 - elapsed) seconds
└─► Make API call
```

## Error Handling

```
Request
  │
  ├─► Try Gemini
  │   ├─► Success ✅ → Return
  │   └─► Fail ❌ → Continue
  │
  ├─► Try OpenRouter
  │   ├─► Success ✅ → Return
  │   └─► Fail ❌ → Continue
  │
  └─► All Failed → Return 500 Error
```

## Logging Flow

```
Request Received
  │
  ├─► "🔵 Google Gemini API available for {endpoint}"
  ├─► "🟢 OpenRouter API available for {endpoint}"
  ├─► "📡 Attempting 2 provider(s) for {endpoint}"
  │
  ├─► "🔄 Trying Google Gemini..."
  │   ├─► "✅ Google Gemini succeeded for {endpoint}"
  │   └─► "❌ Google Gemini failed: {error}"
  │
  ├─► "🔄 Trying OpenRouter..."
  │   ├─► "✅ OpenRouter succeeded for {endpoint}"
  │   └─► "❌ OpenRouter failed: {error}"
  │
  └─► "🚨 All LLM providers failed. Last error: {error}"
```

## Message Format Conversion

### Input (OpenRouter Format)
```python
[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]
```

### Gemini Conversion
```python
{
    "systemInstruction": {
        "parts": [{"text": "You are a helpful assistant."}]
    },
    "contents": [
        {
            "role": "user",
            "parts": [{"text": "Hello!"}]
        }
    ]
}
```

### Output (Normalized)
```python
{
    "choices": [{
        "message": {
            "content": "Response text",
            "role": "assistant"
        }
    }]
}
```

## Performance Metrics

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Rate Limit Errors** | ~30% of requests | ~5% of requests | 83% reduction |
| **Average Latency** | 3-4 seconds | 1-2 seconds | 50% faster |
| **Cache Hit Rate** | 0% | 60-70% | Infinite improvement |
| **Reliability** | 70% | 95% | 36% improvement |

### Cost Analysis

| Provider | Requests/Day | Cost | Total |
|----------|--------------|------|-------|
| Gemini Free | 1,500 | $0 | $0 |
| OpenRouter Free | Varies | $0 | $0 |
| **Total** | **~1,500+** | **$0** | **$0** |

## Scalability

### Current Capacity
- **Gemini:** 1,500 requests/day (free)
- **OpenRouter:** Rate-limited (free)
- **Cache:** Unlimited (local storage)
- **Total Unique Requests:** ~1,500/day
- **Total Cached Requests:** Unlimited

### Upgrade Path
1. **Gemini Pro:** $0.00025/request (1M requests/month)
2. **OpenRouter Paid:** Various models available
3. **Add More Providers:** Easy to extend

## Security Considerations

### API Key Storage
```bash
# .env file (gitignored)
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### Best Practices
- ✅ API keys in environment variables
- ✅ .env file in .gitignore
- ✅ No keys in code
- ✅ No keys in logs
- ✅ Timeout on all requests (30s)

## Monitoring

### Key Metrics to Track
1. **Provider Usage**
   - Which provider handles most requests?
   - Gemini vs OpenRouter ratio

2. **Cache Performance**
   - Cache hit rate
   - Cache size
   - Expired entries

3. **Error Rates**
   - Provider-specific errors
   - Rate limit errors
   - Timeout errors

4. **Latency**
   - Average response time
   - P95, P99 latency
   - Provider-specific latency

### Log Analysis
```bash
# Count provider usage
grep "succeeded for" logs.txt | grep "Gemini" | wc -l
grep "succeeded for" logs.txt | grep "OpenRouter" | wc -l

# Count cache hits
grep "Cache hit" logs.txt | wc -l

# Count errors
grep "failed:" logs.txt | wc -l
```
