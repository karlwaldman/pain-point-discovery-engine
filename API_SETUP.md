# API Setup Guide

This guide will help you get API credentials for Twitter and Reddit.

## Twitter/X API Setup ⚡

### Current Status
- ❌ Found old credentials from OilPriceAPI (expired/unauthorized)
- ⏳ Need to apply for new Elevated Access

### Steps to Get Twitter API Access

1. **Go to Twitter Developer Portal**
   - Visit: https://developer.twitter.com/
   - Sign in with your Twitter account

2. **Apply for Elevated Access**
   - Click "Developer Portal"
   - Click "Elevated" under your project
   - Fill out application form
   - **Use Case Description:**
     ```
     Building a pain point discovery tool to identify business opportunities
     from social media conversations. The tool analyzes tweets for frustration
     expressions, solution-seeking behavior, and budget signals to help
     entrepreneurs find problems worth solving. We'll search for specific pain
     keywords (e.g., "why is there no tool for", "frustrated with", "looking
     for alternative to") and analyze engagement patterns. No private data
     collection, only public tweets. Estimated volume: 1,000-5,000 tweets/day.
     ```

3. **Create Project and App**
   - Project Name: "Pain Point Discovery Engine"
   - App Name: "PPDE Collector"
   - App Type: **Read-only** (we only search and read tweets)

4. **Get Your Bearer Token**
   - Go to your app's "Keys and tokens" tab
   - Click "Generate" under Bearer Token
   - **Copy it immediately** (you won't see it again)

5. **Update .env File**
   ```bash
   TWITTER_BEARER_TOKEN=your-bearer-token-here
   ```

6. **Test Authentication**
   ```bash
   python scripts/test_twitter_auth.py
   ```

### Timeline
- **Application:** Instant submission
- **Approval:** 1-3 business days (usually 24 hours)
- **Rate Limits (Elevated):**
  - 2 million tweets/month
  - 450 requests per 15 minutes
  - Perfect for our use case (1K tweets/day)

---

## Reddit API Setup 🤖

### Steps to Get Reddit API Access

1. **Go to Reddit Apps**
   - Visit: https://www.reddit.com/prefs/apps
   - Sign in with your Reddit account

2. **Create App**
   - Click "Create App" or "Create Another App"
   - Fill out form:
     - **Name:** Pain Point Discovery Engine
     - **Type:** Select **"script"**
     - **Description:** Analyzing entrepreneurship discussions for pain points
     - **About URL:** (leave blank)
     - **Redirect URI:** http://localhost:8000 (required but not used)
   - Click "Create app"

3. **Get Your Credentials**
   - After creation, you'll see:
     - **Client ID:** 14-character string (under app name)
     - **Client Secret:** Click "Edit" to reveal

4. **Update .env File**
   ```bash
   REDDIT_CLIENT_ID=your-14-char-client-id
   REDDIT_CLIENT_SECRET=your-27-char-secret
   REDDIT_USER_AGENT=PainPointDiscovery/1.0
   ```

5. **Test Authentication**
   ```bash
   python scripts/collect_reddit.py
   ```

### Timeline
- **Instant** - No approval needed!
- **Rate Limits:**
  - 60 requests per minute
  - Plenty for our use case (25 posts per subreddit)

---

## Facebook/Meta API ❌ (Not Recommended)

**Why we're NOT using Facebook:**

1. **Groups are private** - Can't access without joining
2. **Restricted API** - Meta heavily restricts data access after Cambridge Analytica
3. **Business pages only** - Public API only works for pages, not personal posts
4. **Complex approval** - Requires business verification and app review
5. **Rate limits** - Very restrictive for free tier
6. **Better alternatives** - Twitter and Reddit have more public entrepreneurship discussions

**Alternative:** If you need Facebook data, manually join relevant groups like:
- SaaS Growth Hacks
- Indie Hackers (unofficial)
- Startup Founders
- Small Business Owners

---

## Testing Your Setup

### 1. Test Twitter (if credentials ready)
```bash
python scripts/test_twitter_auth.py
```

Expected output:
```
✓ Authentication successful!
✓ Authenticated as: @your_username
```

### 2. Test Reddit
```bash
# Check if Reddit is configured
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ Reddit configured' if os.getenv('REDDIT_CLIENT_ID') else '✗ Reddit not configured')"
```

### 3. Run Collections
```bash
# Twitter only
python scripts/collect_tweets.py

# Reddit only
python scripts/collect_reddit.py

# Both platforms
python scripts/collect_all.py
```

---

## Current Configuration Status

Run this to check your setup:

```bash
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

print('API Configuration Status')
print('=' * 40)
print(f'Twitter Bearer Token: {'✓ Set' if os.getenv('TWITTER_BEARER_TOKEN') else '✗ Missing'}')
print(f'Reddit Client ID: {'✓ Set' if os.getenv('REDDIT_CLIENT_ID') else '✗ Missing'}')
print(f'Reddit Client Secret: {'✓ Set' if os.getenv('REDDIT_CLIENT_SECRET') else '✗ Missing'}')
print('=' * 40)
"
```

---

## Rate Limits Summary

| Platform | Free Tier | Elevated/Paid |
|----------|-----------|---------------|
| **Twitter** | 500K tweets/month | 2M tweets/month |
| **Reddit** | 60 req/min | Same (free) |

**Our Usage (CRAWL Phase):**
- Twitter: ~1,000 tweets/day = 30K/month ✅ Well under limits
- Reddit: ~250 posts/day = minimal requests ✅ No issues

---

## Troubleshooting

### Twitter: 401 Unauthorized
- Bearer Token expired or invalid
- Solution: Regenerate token in Developer Portal

### Twitter: 403 Forbidden
- App doesn't have required permissions
- Solution: Apply for Elevated Access

### Reddit: 401 Unauthorized
- Client ID or Secret incorrect
- Solution: Double-check credentials from apps page

### Reddit: 429 Too Many Requests
- Hit rate limit (60 req/min)
- Solution: Script already handles this with wait_on_rate_limit

---

## Next Steps

1. ✅ Twitter: Apply for Elevated Access (wait 1-3 days)
2. ✅ Reddit: Create app (instant, 5 minutes)
3. ⏳ Test both APIs
4. 🚀 Run first collection: `python scripts/collect_all.py`

---

**Note:** The old OilPriceAPI Twitter credentials in your .env are expired. You'll need to get fresh credentials following the instructions above.
