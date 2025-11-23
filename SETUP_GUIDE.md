# Quick Setup Guide

## Required API Keys

This application requires **TWO** API keys to function properly:

### 1. OpenRouter API Key (REQUIRED)
- **Used for:** All AI text generation endpoints (investors, grants, proposals, pitches, roadmaps)
- **Get it from:** https://openrouter.ai/keys
- **Free tier:** Available with rate limits
- **Environment variable:** `OPENROUTER_API_KEY`

### 2. ElevenLabs API Key (REQUIRED for audio)
- **Used for:** Audio generation from pitch text
- **Get it from:** https://elevenlabs.io/app/settings/api-keys
- **Free tier:** Available with monthly character limits
- **Environment variable:** `ELEVENLABS_API_KEY`

## Setup Steps

### 1. Create Environment File

```bash
# Copy the example file
cp .env.example .env
```

### 2. Add Your API Keys

Edit the `.env` file and replace the placeholder values:

```bash
# OpenRouter API Key (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx

# ElevenLabs API Key (REQUIRED for audio)
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxx
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Server

```bash
uvicorn main:app --reload --port 8000
```

### 5. Verify Setup

Run the test suite to verify everything is working:

```bash
# Quick test
python test_apis.py

# Or slower test with better rate limit handling
python test_apis_slow.py
```

## Expected Results

With both API keys configured:
- ✅ All 6 endpoints should work
- ✅ `/investors` - Get investor recommendations
- ✅ `/grantInfo` - Discover grants
- ✅ `/getGrantProposal` - Generate grant proposals
- ✅ `/generatePitchText` - Create pitch transcripts
- ✅ `/generatePitchAudio` - Generate audio files
- ✅ `/business_plan_roadmap` - Create business plans

## Troubleshooting

### "OpenRouter API error: 429"
- **Cause:** Rate limit exceeded on free tier
- **Solution:** Wait a few seconds between requests, or upgrade to paid tier

### "ElevenLabs 401 Unauthorized"
- **Cause:** API key not set or invalid
- **Solution:** Check that `ELEVENLABS_API_KEY` is set correctly in `.env`

### "DuckDuckGo search error: Ratelimit"
- **Cause:** DuckDuckGo search API rate limit
- **Solution:** This is handled gracefully - citations will be skipped but main content will still work

### Server shows "API Key loaded: None"
- **Cause:** `.env` file not found or not loaded
- **Solution:** 
  1. Verify `.env` file exists in project root
  2. Restart the server
  3. Check that `python-dotenv` is installed

## API Key Security

⚠️ **Important Security Notes:**

1. **Never commit `.env` to git** - It's already in `.gitignore`
2. **Keep your API keys secret** - Don't share them publicly
3. **Rotate keys regularly** - Especially if they may have been exposed
4. **Use environment-specific keys** - Different keys for dev/staging/production

## Rate Limits

### OpenRouter (Free Tier)
- Aggressive rate limiting on free models
- Retry logic implemented with exponential backoff
- Consider paid tier for production use

### ElevenLabs (Free Tier)
- Monthly character limit
- Check your usage at: https://elevenlabs.io/app/usage

## Next Steps

Once setup is complete:
1. Review `API_TESTING_REPORT.md` for detailed endpoint documentation
2. Check `README.md` for full project documentation
3. Start building your non-profit tools!

## Support

For issues or questions:
- Check `API_TESTING_REPORT.md` for common issues
- Review server logs for detailed error messages
- Ensure all dependencies are installed correctly
