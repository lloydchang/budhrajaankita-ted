# Honeycomb Observability Setup Guide

## Overview

Honeycomb provides powerful observability for your multi-provider LLM system. With Honeycomb, you can:

- 🔍 **Trace every request** through your system
- 📊 **Visualize provider performance** (Gemini vs OpenRouter vs Cloudflare)
- 🐛 **Debug failures** with detailed error traces
- 📈 **Monitor cache hit rates** and performance
- ⚡ **Identify slow requests** and bottlenecks
- 🎯 **Track API usage** across all providers

## Why Honeycomb?

### Benefits
- ✅ **Free tier** - 20M events/month, 60-day retention
- ✅ **OpenTelemetry native** - Standard, vendor-agnostic instrumentation
- ✅ **Automatic instrumentation** - FastAPI and requests library auto-traced
- ✅ **Powerful queries** - BubbleUp, heatmaps, and more
- ✅ **No sampling required** - See every trace
- ✅ **Fast setup** - 5 minutes to full observability

### What You'll See
- Which provider handled each request
- Cache hit/miss rates
- Provider failover patterns
- Request latency breakdown
- Error rates and patterns
- API call distribution

## Setup Instructions

### Step 1: Create Honeycomb Account

1. Go to https://www.honeycomb.io/
2. Click **"Sign Up"** (free account, no credit card required)
3. Verify your email address
4. Complete the onboarding wizard

### Step 2: Get Your API Key

1. Log in to https://ui.honeycomb.io/
2. Click on your profile (bottom left)
3. Select **"Team Settings"**
4. Go to **"API Keys"** tab
5. Click **"Create API Key"**
6. Configure the key:
   - **Name:** `budhrajaankita-ted-dev`
   - **Permissions:** Check "Can create datasets"
   - **Environment:** Default
7. Click **"Create Key"**
8. **Copy the key** (you won't be able to see it again!)

Example API Key: `hcaik_01234567890abcdef01234567890abcdef01234567890abcdef01234567890`

### Step 3: Add to .env File

Add your Honeycomb API key to your `.env` file:

```bash
# Honeycomb Observability
HONEYCOMB_API_KEY=your_actual_honeycomb_api_key_here

# Optional: If using EU instance
# OTEL_EXPORTER_OTLP_ENDPOINT=https://api.eu1.honeycomb.io:443
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `opentelemetry-instrumentation` - Auto-instrumentation
- `opentelemetry-distro` - OpenTelemetry distribution
- `opentelemetry-exporter-otlp` - OTLP exporter for Honeycomb
- `opentelemetry-instrumentation-fastapi` - FastAPI auto-instrumentation
- `opentelemetry-instrumentation-requests` - Requests library auto-instrumentation

### Step 5: Start Your Application

```bash
uvicorn main:app --reload --port 8001
```

You should see:
```
✅ Honeycomb observability enabled for service: budhrajaankita-ted
   Endpoint: https://api.honeycomb.io:443
```

### Step 6: Generate Some Traffic

Make a few requests to your API:

```bash
# Test business plan endpoint
curl -X POST http://127.0.0.1:8001/business_plan_roadmap \
  -H "Content-Type: application/json" \
  -d '{"idea": {"name": "Test", "mission": "Test mission", "goals": [], "targetMarket": {}, "primaryProduct": "Test", "sdgs": []}}'
```

### Step 7: View Traces in Honeycomb

1. Go to https://ui.honeycomb.io/
2. Select your environment
3. You should see a dataset named **`budhrajaankita-ted`**
4. Click on it to view traces!

## What You'll See in Honeycomb

### Automatic Traces

Every request creates a trace with:

#### Request Information
- `http.method` - GET, POST, etc.
- `http.route` - `/business_plan_roadmap`, `/investors`, etc.
- `http.status_code` - 200, 429, 500, etc.
- `http.target` - Full request path

#### Provider Information
- `endpoint.name` - Which endpoint was called
- `cache.hit` - true/false
- `providers.available` - Number of providers configured
- `providers.list` - "Google Gemini,OpenRouter,Cloudflare Workers AI"
- `provider.used` - Which provider succeeded
- `provider.success` - true/false
- `provider.attempt` - Which attempt succeeded (1, 2, or 3)

#### Events Within Traces
- `trying_provider` - Each provider attempt
- `provider_success` - Successful provider call
- `provider_failed` - Failed provider call with error message

#### Timing Information
- `duration_ms` - Total request duration
- Individual span durations for each operation

### Example Trace

```
POST /business_plan_roadmap (200 OK, 2.3s)
├─ cache.hit: false
├─ providers.available: 3
├─ providers.list: "Google Gemini,OpenRouter,Cloudflare Workers AI"
├─ Event: trying_provider (Google Gemini)
├─ HTTP POST to api.google.com (1.8s)
├─ Event: provider_success (Google Gemini)
├─ provider.used: "Google Gemini"
├─ provider.success: true
└─ provider.attempt: 1
```

## Powerful Queries

### Cache Hit Rate
```
COUNT | GROUP BY cache.hit
```

### Provider Usage Distribution
```
COUNT | GROUP BY provider.used
```

### Requests by Endpoint
```
COUNT | GROUP BY endpoint.name
```

### Average Latency by Provider
```
AVG(duration_ms) | GROUP BY provider.used
```

### Failed Requests
```
WHERE provider.success = false | COUNT
```

### Slowest Endpoints
```
P95(duration_ms) | GROUP BY endpoint.name | ORDER BY P95(duration_ms) DESC
```

### Provider Failover Patterns
```
WHERE provider.attempt > 1 | COUNT | GROUP BY provider.used
```

## Advanced Features

### BubbleUp

Honeycomb's BubbleUp feature automatically finds patterns in your data:

1. Click **"New Query"**
2. Select **"BubbleUp"**
3. Choose a dimension (e.g., `http.status_code = 500`)
4. Honeycomb shows what's different about those requests

### Heatmaps

Visualize latency distribution:

1. Click **"New Query"**
2. Add `HEATMAP(duration_ms)`
3. See latency distribution over time

### Tracing

Follow a request through your entire system:

1. Click on any trace
2. See the waterfall view of all operations
3. Drill into individual spans
4. View all attributes and events

## Monitoring Dashboards

### Create a Dashboard

1. Go to **"Boards"** in Honeycomb
2. Click **"Create Board"**
3. Add queries:

#### Request Rate
```
COUNT | VISUALIZE AS LINE
```

#### Error Rate
```
WHERE http.status_code >= 400 | COUNT | VISUALIZE AS LINE
```

#### Cache Hit Rate
```
WHERE cache.hit = true | COUNT | VISUALIZE AS LINE
```

#### Provider Distribution
```
COUNT | GROUP BY provider.used | VISUALIZE AS PIE
```

#### P95 Latency
```
P95(duration_ms) | VISUALIZE AS LINE
```

## Alerts

### Create an Alert

1. Go to **"Triggers"** in Honeycomb
2. Click **"Create Trigger"**
3. Configure alert:

#### High Error Rate Alert
```
Query: WHERE http.status_code >= 500 | COUNT
Threshold: > 10 in 5 minutes
Notification: Email/Slack
```

#### Slow Requests Alert
```
Query: P95(duration_ms)
Threshold: > 5000 (5 seconds)
Notification: Email/Slack
```

#### All Providers Failing Alert
```
Query: WHERE provider.success = false | COUNT
Threshold: > 5 in 5 minutes
Notification: Email/Slack
```

## Troubleshooting

### "HONEYCOMB_API_KEY not configured"
**Solution:** Add `HONEYCOMB_API_KEY` to your `.env` file

### No traces appearing in Honeycomb
**Solution:**
1. Check that the API key is correct
2. Verify the service is running
3. Make some requests to generate traces
4. Check for errors in console output
5. Wait 30 seconds for data to appear

### "Failed to configure Honeycomb observability"
**Solution:**
1. Install OpenTelemetry packages: `pip install -r requirements.txt`
2. Check for import errors in console
3. Verify `otel_config.py` exists

### Traces missing attributes
**Solution:**
1. Check that `add_span_attribute` is being called
2. Verify OpenTelemetry is properly configured
3. Look for errors in console logs

## Best Practices

### Sampling

For high-traffic applications, you may want to sample:

```bash
# In .env file
export OTEL_TRACES_SAMPLER="traceidratio"
export OTEL_TRACES_SAMPLER_ARG=0.1  # Keep 10% of traces
export OTEL_RESOURCE_ATTRIBUTES="SampleRate=10"
```

Honeycomb will automatically adjust counts based on sample rate.

### Custom Attributes

Add custom attributes to spans:

```python
from otel_config import add_span_attribute

# In your endpoint
add_span_attribute("user.id", user_id)
add_span_attribute("request.size", len(request_data))
add_span_attribute("custom.field", "value")
```

### Custom Events

Add events to track important moments:

```python
from otel_config import add_span_event

# Track important events
add_span_event("cache_miss", {"reason": "expired"})
add_span_event("rate_limited", {"provider": "gemini"})
add_span_event("fallback_triggered", {"from": "gemini", "to": "openrouter"})
```

### Baggage for Multi-Span Attributes

Propagate attributes to all child spans:

```python
from otel_config import set_baggage, detach_baggage

# Set baggage
token = set_baggage("user.id", user_id)

# ... do work (all child spans will have user.id)

# Clean up
detach_baggage(token)
```

## Cost Management

### Free Tier
- **20M events/month** - More than enough for most applications
- **60-day retention** - 2 months of historical data
- **Unlimited users** - Whole team can access
- **All features** - No feature restrictions

### Monitoring Usage
1. Go to **"Team Settings"** → **"Usage"**
2. View current usage
3. Set up usage alerts

### Reducing Costs
If you exceed free tier:
1. **Enable sampling** - Keep 10% of traces
2. **Filter noisy endpoints** - Don't trace health checks
3. **Adjust retention** - Reduce to 30 days
4. **Upgrade plan** - $100/month for 100M events

## Integration with Existing Tools

### Slack Notifications
1. Go to **"Integrations"** → **"Slack"**
2. Connect your Slack workspace
3. Configure alert channels

### PagerDuty
1. Go to **"Integrations"** → **"PagerDuty"**
2. Add PagerDuty integration key
3. Route critical alerts to PagerDuty

### Webhooks
1. Go to **"Integrations"** → **"Webhooks"**
2. Add webhook URL
3. Send alerts to custom endpoints

## Example Queries for This Application

### Most Used Provider
```
COUNT | GROUP BY provider.used | ORDER BY COUNT DESC
```

### Cache Effectiveness
```
COUNT | GROUP BY cache.hit | VISUALIZE AS PIE
```

### Endpoint Performance
```
AVG(duration_ms), P95(duration_ms), P99(duration_ms) | GROUP BY endpoint.name
```

### Provider Reliability
```
WHERE provider.success = true | COUNT | GROUP BY provider.used
```

### Failover Analysis
```
WHERE provider.attempt > 1 | COUNT | GROUP BY provider.used, provider.attempt
```

### Error Patterns
```
WHERE error EXISTS | COUNT | GROUP BY error
```

## Next Steps

### 1. Explore Your Data
- Run queries to understand your traffic
- Create dashboards for key metrics
- Set up alerts for critical issues

### 2. Add Custom Instrumentation
- Add user IDs to traces
- Track business metrics
- Add custom events for important operations

### 3. Share with Team
- Invite team members to Honeycomb
- Create shared dashboards
- Set up team alerts

## Resources

- **Honeycomb Documentation:** https://docs.honeycomb.io/
- **OpenTelemetry Python:** https://opentelemetry.io/docs/instrumentation/python/
- **Example Queries:** https://docs.honeycomb.io/working-with-your-data/queries/
- **BubbleUp Guide:** https://docs.honeycomb.io/working-with-your-data/bubbleup/

## Conclusion

Honeycomb observability is now fully integrated! You can:

✅ **See every request** in detail  
✅ **Track provider performance** and failover  
✅ **Monitor cache effectiveness**  
✅ **Debug errors** with full context  
✅ **Create dashboards** for key metrics  
✅ **Set up alerts** for critical issues  
✅ **Analyze patterns** with BubbleUp  
✅ **Free tier** covers most use cases  

**Start exploring your data in Honeycomb!** 🍯
