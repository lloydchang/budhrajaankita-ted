# Honeycomb Observability - Quick Reference

## 🚀 Quick Setup (5 minutes)

### 1. Get Honeycomb API Key
1. Sign up: https://www.honeycomb.io/
2. Go to: https://ui.honeycomb.io/account
3. Create API Key (check "Can create datasets")
4. Copy the key

### 2. Add to .env
```bash
HONEYCOMB_API_KEY=your_honeycomb_api_key_here
```

### 3. Install & Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### 4. View Traces
1. Make some requests to your API
2. Go to: https://ui.honeycomb.io/
3. Select dataset: `budhrajaankita-ted`
4. See your traces!

## 📊 Key Metrics to Track

### Provider Performance
```
COUNT | GROUP BY provider.used
```
Shows which provider handles most requests.

### Cache Hit Rate
```
COUNT | GROUP BY cache.hit
```
Shows cache effectiveness (aim for >60%).

### Error Rate
```
WHERE http.status_code >= 400 | COUNT
```
Shows failed requests.

### Latency
```
P95(duration_ms) | GROUP BY endpoint.name
```
Shows 95th percentile latency by endpoint.

### Provider Failover
```
WHERE provider.attempt > 1 | COUNT
```
Shows how often fallback providers are used.

## 🔍 Common Queries

### Find Slow Requests
```
WHERE duration_ms > 5000 | ORDER BY duration_ms DESC
```

### Find Errors
```
WHERE error EXISTS | GROUP BY error
```

### Cache Misses
```
WHERE cache.hit = false | COUNT | GROUP BY endpoint.name
```

### Provider Failures
```
WHERE provider.success = false | GROUP BY provider.used
```

## 🎯 Trace Attributes

### Automatically Captured
- `http.method` - GET, POST, etc.
- `http.route` - Endpoint path
- `http.status_code` - Response code
- `duration_ms` - Request duration

### Custom Attributes
- `endpoint.name` - Endpoint identifier
- `cache.hit` - Cache hit/miss
- `providers.available` - Number of providers
- `providers.list` - Available providers
- `provider.used` - Which provider succeeded
- `provider.success` - Success/failure
- `provider.attempt` - Which attempt (1, 2, or 3)

## 🛠️ Troubleshooting

### No traces appearing?
1. Check API key is correct
2. Verify service is running
3. Make test requests
4. Wait 30 seconds

### Missing attributes?
1. Check console for errors
2. Verify OpenTelemetry is installed
3. Restart the service

## 📈 Dashboard Queries

### Request Rate
```
COUNT | VISUALIZE AS LINE
```

### Error Rate
```
WHERE http.status_code >= 400 | COUNT | VISUALIZE AS LINE
```

### Provider Distribution
```
COUNT | GROUP BY provider.used | VISUALIZE AS PIE
```

### P95 Latency
```
P95(duration_ms) | VISUALIZE AS LINE
```

## 🚨 Recommended Alerts

### High Error Rate
```
WHERE http.status_code >= 500 | COUNT
Threshold: > 10 in 5 minutes
```

### Slow Requests
```
P95(duration_ms)
Threshold: > 5000
```

### All Providers Failing
```
WHERE provider.success = false | COUNT
Threshold: > 5 in 5 minutes
```

## 💡 Pro Tips

1. **Use BubbleUp** - Automatically find patterns in errors
2. **Create Dashboards** - Monitor key metrics at a glance
3. **Set Up Alerts** - Get notified of issues immediately
4. **Add Custom Attributes** - Track user IDs, request sizes, etc.
5. **Use Heatmaps** - Visualize latency distribution

## 📚 Resources

- **Full Setup Guide:** `HONEYCOMB_SETUP.md`
- **Honeycomb Docs:** https://docs.honeycomb.io/
- **Query Language:** https://docs.honeycomb.io/working-with-your-data/queries/

## ✅ What You Get

- 🔍 **Full request tracing** - See every operation
- 📊 **Provider analytics** - Track which providers are used
- 🐛 **Error debugging** - Full context for failures
- ⚡ **Performance monitoring** - Identify bottlenecks
- 📈 **Cache analytics** - Optimize cache effectiveness
- 🎯 **Custom metrics** - Track what matters to you
- 🆓 **Free tier** - 20M events/month

**Start monitoring your multi-provider LLM system today!** 🍯
