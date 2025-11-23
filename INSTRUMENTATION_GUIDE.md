# Enhanced Honeycomb Instrumentation Guide

## Overview

Your multi-provider LLM system now has **comprehensive instrumentation** that tracks every aspect of API usage, performance, and behavior. This guide explains all the telemetry data being collected and how to use it.

## 🎯 What's Being Tracked

### Request-Level Metrics

Every request to your API is automatically instrumented with:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `http.method` | string | HTTP method | `POST` |
| `http.route` | string | Endpoint route | `/business_plan_roadmap` |
| `http.status_code` | int | Response status | `200`, `429`, `500` |
| `endpoint.name` | string | Endpoint identifier | `business_plan_roadmap` |
| `request.message_count` | int | Number of messages in request | `3` |
| `total.duration_ms` | float | Total request duration | `2345.67` |

### Cache Metrics

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `cache.hit` | bool | Whether cache was hit | `true`, `false` |
| `total.duration_ms` | float | Duration including cache lookup | `12.34` (cache hit) |

### Provider Metrics

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `providers.available` | int | Number of configured providers | `3` |
| `providers.list` | string | Comma-separated provider names | `Google Gemini,OpenRouter,Cloudflare Workers AI` |
| `provider.used` | string | Which provider succeeded | `Google Gemini` |
| `provider.success` | bool | Whether any provider succeeded | `true`, `false` |
| `provider.attempt` | int | Which attempt succeeded | `1`, `2`, `3` |

### LLM-Specific Metrics (Per Provider)

Each provider call creates a child span with:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `llm.provider` | string | Provider name | `Google Gemini` |
| `llm.model` | string | Model identifier | `gemini-2.0-flash-exp` |
| `llm.latency_ms` | float | API call duration | `1823.45` |
| `response.length` | int | Response character count | `1543` |
| `llm.usage.prompt_tokens` | int | Input tokens used | `245` |
| `llm.usage.completion_tokens` | int | Output tokens used | `512` |
| `llm.usage.total_tokens` | int | Total tokens used | `757` |

### Events

Events mark important moments in the trace:

| Event | Attributes | When |
|-------|------------|------|
| `trying_provider` | `provider.name`, `provider.index`, `endpoint.name` | Before attempting each provider |
| `provider_success` | `provider.name`, `endpoint.name`, `duration_ms` | When a provider succeeds |
| `provider_failed` | `provider.name`, `error.message`, `endpoint.name` | When a provider fails |
| `api_attempt` | `attempt` | Each retry attempt |
| `rate_limited` | `wait_time`, `attempt` | When rate limited |

## 📊 Example Traces

### Successful Request (Cache Miss, Gemini Success)

```
POST /business_plan_roadmap (2.3s, 200 OK)
├─ endpoint.name: "business_plan_roadmap"
├─ request.message_count: 3
├─ cache.hit: false
├─ providers.available: 3
├─ providers.list: "Google Gemini,OpenRouter,Cloudflare Workers AI"
├─ Event: trying_provider (Google Gemini, index=0)
│
├─ Span: call_gemini_api (1.8s)
│  ├─ llm.provider: "Google Gemini"
│  ├─ llm.model: "gemini-2.0-flash-exp"
│  ├─ request.message_count: 3
│  ├─ llm.latency_ms: 1823.45
│  ├─ response.length: 1543
│  ├─ llm.usage.prompt_tokens: 245
│  ├─ llm.usage.completion_tokens: 512
│  └─ llm.usage.total_tokens: 757
│
├─ Event: provider_success (Google Gemini, duration_ms=1823.45)
├─ total.duration_ms: 2345.67
├─ provider.used: "Google Gemini"
├─ provider.success: true
└─ provider.attempt: 1
```

### Cache Hit

```
POST /business_plan_roadmap (0.012s, 200 OK)
├─ endpoint.name: "business_plan_roadmap"
├─ request.message_count: 3
├─ cache.hit: true
└─ total.duration_ms: 12.34
```

### Failover to Secondary Provider

```
POST /business_plan_roadmap (5.2s, 200 OK)
├─ endpoint.name: "business_plan_roadmap"
├─ request.message_count: 3
├─ cache.hit: false
├─ providers.available: 3
│
├─ Event: trying_provider (Google Gemini, index=0)
├─ Span: call_gemini_api (failed)
│  ├─ llm.provider: "Google Gemini"
│  ├─ llm.model: "gemini-2.0-flash-exp"
│  └─ Error: Rate limit exceeded
├─ Event: provider_failed (Google Gemini, error="Rate limit exceeded")
│
├─ Event: trying_provider (OpenRouter, index=1)
├─ Span: call_openrouter_api (3.2s)
│  ├─ llm.provider: "OpenRouter"
│  ├─ llm.model: "meta-llama/llama-3.2-3b-instruct:free"
│  ├─ Event: api_attempt (attempt=1)
│  ├─ llm.latency_ms: 3234.56
│  ├─ response.length: 1234
│  ├─ llm.usage.prompt_tokens: 245
│  ├─ llm.usage.completion_tokens: 456
│  └─ llm.usage.total_tokens: 701
│
├─ Event: provider_success (OpenRouter, duration_ms=3234.56)
├─ total.duration_ms: 5234.78
├─ provider.used: "OpenRouter"
├─ provider.success: true
└─ provider.attempt: 2
```

### All Providers Failed

```
POST /business_plan_roadmap (15.5s, 500 Internal Server Error)
├─ endpoint.name: "business_plan_roadmap"
├─ request.message_count: 3
├─ cache.hit: false
├─ providers.available: 3
│
├─ Event: trying_provider (Google Gemini, index=0)
├─ Span: call_gemini_api (failed)
├─ Event: provider_failed (Google Gemini, error="Rate limit exceeded")
│
├─ Event: trying_provider (OpenRouter, index=1)
├─ Span: call_openrouter_api (failed)
├─ Event: provider_failed (OpenRouter, error="Rate limit exceeded")
│
├─ Event: trying_provider (Cloudflare Workers AI, index=2)
├─ Span: call_cloudflare_api (failed)
├─ Event: provider_failed (Cloudflare, error="Rate limit exceeded")
│
├─ total.duration_ms: 15543.21
├─ provider.success: false
└─ error: "All LLM providers failed. Last error: Rate limit exceeded"
```

## 🔍 Powerful Queries

### Provider Performance Comparison

```
AVG(llm.latency_ms), P95(llm.latency_ms), P99(llm.latency_ms) 
| GROUP BY llm.provider
```

**What it shows:** Average, 95th percentile, and 99th percentile latency for each provider.

### Token Usage by Provider

```
SUM(llm.usage.total_tokens) 
| GROUP BY llm.provider
```

**What it shows:** Total tokens consumed by each provider (useful for cost tracking).

### Cache Effectiveness

```
COUNT 
| GROUP BY cache.hit 
| VISUALIZE AS PIE
```

**What it shows:** Percentage of requests served from cache vs. API calls.

### Provider Reliability

```
COUNT 
| WHERE provider.success = true 
| GROUP BY provider.used
```

**What it shows:** How many successful requests each provider handled.

### Failover Frequency

```
COUNT 
| WHERE provider.attempt > 1 
| GROUP BY provider.used, provider.attempt
```

**What it shows:** How often you're falling back to secondary/tertiary providers.

### Response Size Distribution

```
HEATMAP(response.length) 
| GROUP BY endpoint.name
```

**What it shows:** Distribution of response sizes for each endpoint.

### Token Cost Analysis

```
SUM(llm.usage.prompt_tokens), SUM(llm.usage.completion_tokens) 
| GROUP BY llm.model
```

**What it shows:** Input vs. output token usage by model (for cost estimation).

### Slow Requests by Provider

```
WHERE llm.latency_ms > 3000 
| COUNT 
| GROUP BY llm.provider
```

**What it shows:** Which provider has the most slow requests (>3 seconds).

### Error Patterns

```
WHERE provider.success = false 
| COUNT 
| GROUP BY error
```

**What it shows:** Common error messages and their frequency.

### Request Volume by Endpoint

```
COUNT 
| GROUP BY endpoint.name 
| ORDER BY COUNT DESC
```

**What it shows:** Most popular endpoints.

### Cache Hit Rate by Endpoint

```
WHERE cache.hit = true 
| COUNT 
| GROUP BY endpoint.name
```

**What it shows:** Which endpoints benefit most from caching.

## 📈 Dashboard Recommendations

### Executive Dashboard

1. **Request Rate**
   ```
   COUNT | VISUALIZE AS LINE
   ```

2. **Error Rate**
   ```
   WHERE http.status_code >= 400 | COUNT | VISUALIZE AS LINE
   ```

3. **P95 Latency**
   ```
   P95(total.duration_ms) | VISUALIZE AS LINE
   ```

4. **Cache Hit Rate**
   ```
   WHERE cache.hit = true | COUNT | VISUALIZE AS LINE
   ```

5. **Provider Distribution**
   ```
   COUNT | GROUP BY provider.used | VISUALIZE AS PIE
   ```

### Technical Dashboard

1. **Provider Latency Comparison**
   ```
   AVG(llm.latency_ms) | GROUP BY llm.provider | VISUALIZE AS BAR
   ```

2. **Token Usage**
   ```
   SUM(llm.usage.total_tokens) | GROUP BY llm.model | VISUALIZE AS LINE
   ```

3. **Failover Rate**
   ```
   WHERE provider.attempt > 1 | COUNT | VISUALIZE AS LINE
   ```

4. **Response Size**
   ```
   AVG(response.length) | GROUP BY endpoint.name | VISUALIZE AS BAR
   ```

5. **Rate Limit Events**
   ```
   WHERE EXISTS(rate_limited) | COUNT | VISUALIZE AS LINE
   ```

### Cost Dashboard

1. **Total Tokens by Provider**
   ```
   SUM(llm.usage.total_tokens) | GROUP BY llm.provider
   ```

2. **Prompt vs. Completion Tokens**
   ```
   SUM(llm.usage.prompt_tokens), SUM(llm.usage.completion_tokens) 
   | GROUP BY llm.model
   ```

3. **Cache Savings**
   ```
   WHERE cache.hit = true | COUNT
   ```
   *(Each cache hit = 1 saved API call)*

4. **Provider Cost Estimate**
   ```
   SUM(llm.usage.total_tokens) * 0.000001 
   | GROUP BY llm.provider
   ```
   *(Adjust multiplier based on actual pricing)*

## 🚨 Recommended Alerts

### Critical Alerts

1. **High Error Rate**
   ```
   Query: WHERE http.status_code >= 500 | COUNT
   Threshold: > 10 in 5 minutes
   Severity: Critical
   ```

2. **All Providers Failing**
   ```
   Query: WHERE provider.success = false | COUNT
   Threshold: > 5 in 5 minutes
   Severity: Critical
   ```

3. **Extreme Latency**
   ```
   Query: P95(total.duration_ms)
   Threshold: > 10000 (10 seconds)
   Severity: Critical
   ```

### Warning Alerts

1. **Increased Failover**
   ```
   Query: WHERE provider.attempt > 1 | COUNT
   Threshold: > 20 in 10 minutes
   Severity: Warning
   ```

2. **Cache Hit Rate Drop**
   ```
   Query: WHERE cache.hit = true | COUNT
   Threshold: < 30% of total requests
   Severity: Warning
   ```

3. **High Token Usage**
   ```
   Query: SUM(llm.usage.total_tokens)
   Threshold: > 1000000 in 1 hour
   Severity: Warning
   ```

## 💡 Advanced Analysis

### BubbleUp for Error Investigation

When you see errors, use BubbleUp to find patterns:

1. Click **"New Query"**
2. Select **"BubbleUp"**
3. Choose dimension: `http.status_code = 500`
4. Honeycomb shows what's different about failed requests

Example insights:
- "All 500 errors have `provider.attempt = 3`" → All providers are failing
- "All 500 errors have `endpoint.name = business_plan_roadmap`" → Specific endpoint issue
- "All 500 errors have `llm.provider = Google Gemini`" → Gemini-specific problem

### Latency Investigation

Find what makes requests slow:

```
WHERE total.duration_ms > 5000 
| GROUP BY provider.used, cache.hit, endpoint.name
```

This shows:
- Which provider is slow
- If cache would help
- Which endpoints are affected

### Cost Optimization

Find expensive requests:

```
WHERE llm.usage.total_tokens > 1000 
| GROUP BY endpoint.name, llm.model
```

This shows:
- Which endpoints use the most tokens
- Which models are most expensive
- Opportunities for optimization

## 🎯 Best Practices

### 1. Monitor Key Metrics Daily

- **Cache hit rate** - Should be >60%
- **Provider distribution** - Should match expected priority
- **Error rate** - Should be <1%
- **P95 latency** - Should be <5 seconds

### 2. Set Up Alerts

- Critical alerts for outages
- Warning alerts for degradation
- Info alerts for trends

### 3. Use BubbleUp for Investigation

When something goes wrong:
1. Filter to the problem (e.g., errors)
2. Use BubbleUp to find patterns
3. Drill into specific traces
4. Fix the root cause

### 4. Track Trends Over Time

- Compare week-over-week
- Identify seasonal patterns
- Spot gradual degradation

### 5. Optimize Based on Data

- Cache frequently requested content
- Adjust provider priority based on performance
- Optimize slow endpoints
- Reduce token usage where possible

## 📚 Resources

- **Honeycomb Docs:** https://docs.honeycomb.io/
- **Query Language:** https://docs.honeycomb.io/working-with-your-data/queries/
- **BubbleUp Guide:** https://docs.honeycomb.io/working-with-your-data/bubbleup/
- **OpenTelemetry Semantic Conventions:** https://opentelemetry.io/docs/specs/semconv/

## ✅ Summary

Your instrumentation now tracks:

✅ **Request metrics** - Method, route, status, duration  
✅ **Cache performance** - Hit rate, lookup time  
✅ **Provider behavior** - Which provider, attempts, success/failure  
✅ **LLM specifics** - Model, latency, token usage  
✅ **Error details** - Full context for debugging  
✅ **Performance data** - Latency at every level  
✅ **Cost metrics** - Token usage for billing  

**You have complete visibility into your multi-provider LLM system!** 🎉
