# CRAWL Phase: Detailed Implementation Plan

> **Timeline:** 8 weeks
> **Goal:** Ship a useful MVP that helps users discover 1-2 real business opportunities daily
> **Budget:** $100-200 total (infrastructure only)

---

## Why CRAWL Matters

**Critical Insight:** The first version must be USEFUL, not impressive.

Users don't care about:
- ❌ Perfect ML models
- ❌ Real-time updates
- ❌ Beautiful React UI
- ❌ Multi-platform coverage

Users DO care about:
- ✅ Finding ONE good business opportunity
- ✅ Signal vs noise (quality over quantity)
- ✅ Simple, clear presentation
- ✅ Daily habit formation (email digest)

**Success = 10 beta users who check the app daily and tell their friends**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CRAWL ARCHITECTURE                    │
└─────────────────────────────────────────────────────────┘

[Twitter API]
     │
     ▼
[Collection Script] ──→ [Pain Detection] ──→ [Scoring]
  (Daily Cron)          (Keyword-based)     (Simple algo)
     │
     ▼
[SQLite Database]
     │
     ├──→ [Flask Web App] ──→ [Users view opportunities]
     │
     └──→ [Email Digest] ──→ [Daily email at 7am]
          (SendGrid)
```

**Key Decisions:**
- **SQLite** (not PostgreSQL): Single file, zero setup, good enough for <10K records/day
- **Flask** (not React): Server-rendered HTML, faster to build, SEO-friendly
- **Cron jobs** (not real-time): Daily batch is fine for MVP, simpler architecture
- **Keywords** (not ML): 80% accuracy with 10% of the work
- **Single platform** (Twitter only): Better to do one thing well

---

## Week-by-Week Plan

### Week 1: Foundation (Issues #1-4)

**Goal:** Infrastructure working, Twitter data flowing

**Monday-Tuesday: Repository & Database**
- [ ] Create directory structure (backend, scripts, docs, tests)
- [ ] Write comprehensive README.md
- [ ] Design SQLite schema (see below)
- [ ] Create migration script
- [ ] Add sample data for development

**Wednesday-Thursday: Twitter Integration**
- [ ] Register Twitter Developer account (apply for elevated access)
- [ ] Create app, get API credentials (API Key, Secret, Bearer Token)
- [ ] Write `scripts/test_twitter_auth.py` to verify credentials
- [ ] Implement rate limit tracker
- [ ] Document API limits and costs

**Friday: Testing & Documentation**
- [ ] Test end-to-end: auth → search → parse → store
- [ ] Document setup instructions
- [ ] Create `.env.example` for configuration
- [ ] Write troubleshooting guide

**Deliverable:** Can successfully collect 10 test tweets and store them

---

### Week 2: Data Collection Pipeline (Issues #5-8)

**Goal:** Automated daily collection of 500-1000 pain-related tweets

**Monday: Pain Pattern Research**
- [ ] Research pain expression language on Twitter
- [ ] Create list of 50+ pain keywords/phrases (see below)
- [ ] Define regex patterns for frustration markers
- [ ] Identify budget signal keywords
- [ ] Test patterns on sample tweets

**Tuesday-Wednesday: Collection Script**
- [ ] Build `scripts/collect_tweets.py`
  - Search API calls with pain keywords
  - Parse tweet JSON (text, user, engagement, timestamp)
  - Extract mentions (@product_name)
  - Calculate engagement score (likes + retweets × 2)
  - Deduplicate by tweet ID
  - Store in `tweets` table
- [ ] Add error handling and retry logic
- [ ] Implement logging to file
- [ ] Test on 100+ tweets

**Thursday: Automation**
- [ ] Create `scripts/daily_collection.sh` wrapper
- [ ] Setup cron job for 2am daily
- [ ] Add email notification on errors
- [ ] Monitor first successful run
- [ ] Verify data quality

**Friday: Validation**
- [ ] Review collected tweets (are they actual pain points?)
- [ ] Tune search queries to reduce noise
- [ ] Calculate collection metrics (tweets/day, duplicates, errors)
- [ ] Document collection process

**Deliverable:** Automated daily collection of 500-1000 quality tweets

---

### Week 3: Pain Detection & Scoring (Issues #9-12)

**Goal:** Generate daily top 10 opportunities with scores

**Monday-Tuesday: Pain Classifier**
- [ ] Build `backend/pain_detector.py`
  - Frustration level: 0-10 (keyword matching)
  - Budget signals: 0-50 (paid tool mentions, $ amounts)
  - Product extraction: simple regex for @mentions and caps words
- [ ] Test on sample data
- [ ] Tune thresholds (what score = good pain point?)
- [ ] Calculate precision/recall on 100 hand-labeled tweets

**Wednesday: Scoring Algorithm**
- [ ] Implement simple scoring formula:
  ```
  Score = (Engagement × 2) + (Frustration × 3) + (Budget Signal × 5)
  ```
- [ ] Test on historical data
- [ ] Identify score thresholds:
  - 80+: Excellent opportunity
  - 60-79: Good opportunity
  - 40-59: Worth investigating
  - <40: Low signal
- [ ] Validate scores make intuitive sense

**Thursday: Opportunity Aggregation**
- [ ] Group similar tweets (simple: same extracted product/keywords)
- [ ] Calculate aggregate scores (average? max? weighted?)
- [ ] Rank opportunities by score
- [ ] Generate daily top 10 list
- [ ] Store in `opportunities` table

**Friday: Testing & Tuning**
- [ ] Run pipeline on 3 days of historical data
- [ ] Manually review top 10 for each day
- [ ] Measure quality: Are these real opportunities?
- [ ] Tune scoring weights based on feedback
- [ ] Document scoring methodology

**Deliverable:** Daily top 10 list of scored opportunities

---

### Week 4-5: Web Application (Issues #13-18)

**Goal:** Simple, functional web app

**Week 4 Monday-Tuesday: Flask Setup**
- [ ] Initialize Flask project structure
- [ ] Setup Jinja2 templates
- [ ] Add Bootstrap 5 CSS
- [ ] Create base template with nav
- [ ] Setup routes (/, /opportunity/<id>, /login, /register, /dashboard)
- [ ] Configure development server

**Week 4 Wednesday-Friday: Homepage**
- [ ] Create homepage route `/`
- [ ] Query database for top 10 opportunities (today)
- [ ] Display in card format:
  - Opportunity title
  - Score badge (color-coded)
  - Key metrics (mentions, engagement)
  - Preview text
  - "View Details" button
- [ ] Add filters:
  - Minimum score slider
  - Date selector
- [ ] Make responsive (mobile-friendly)

**Week 5 Monday-Tuesday: Detail Page**
- [ ] Create opportunity detail route `/opportunity/<id>`
- [ ] Show full information:
  - Score breakdown (engagement, frustration, budget)
  - Related tweets (top 10 by engagement)
  - Extracted products/competitors
  - Temporal trend (if multiple days)
- [ ] Add "Save to Watchlist" button (requires auth)
- [ ] Add "Share" button (copy link)

**Week 5 Wednesday-Thursday: Authentication**
- [ ] User registration form
  - Email, password, confirm password
  - Email validation (format only, no verification yet)
  - Password hashing (bcrypt)
- [ ] Login form
  - Email, password
  - Session management (Flask-Login)
- [ ] Logout functionality
- [ ] Protected routes (redirect to login)

**Week 5 Friday: User Dashboard**
- [ ] Create dashboard route `/dashboard`
- [ ] Show personalized feed
- [ ] Watchlist section (saved opportunities)
- [ ] Email preferences link
- [ ] Basic settings (update email, password)

**Deliverable:** Functional web app where users can browse and save opportunities

---

### Week 6: Email Digest System (Issues #19-22)

**Goal:** Daily email digest at 7am with top 5 opportunities

**Monday: SendGrid Setup**
- [ ] Register SendGrid account (free tier: 100 emails/day)
- [ ] Verify sender email address
- [ ] Get API key
- [ ] Test sending email via Python SDK
- [ ] Create HTML email template

**Tuesday-Wednesday: Digest Generator**
- [ ] Build `scripts/send_daily_digest.py`
- [ ] Query top 5 opportunities (yesterday)
- [ ] Generate HTML email:
  - Subject: "5 Business Opportunities Discovered Yesterday"
  - Body: Opportunity cards with scores, preview, link
  - Footer: Unsubscribe link, settings link
- [ ] Generate plain text version (fallback)
- [ ] Personalize based on user preferences (if set)

**Thursday: Preferences System**
- [ ] Create email preferences page
- [ ] Settings:
  - Enable/disable daily digest
  - Minimum score threshold
  - Frequency (daily, weekly, off)
  - Categories (if we add them later)
- [ ] Unsubscribe flow (one-click)
- [ ] Re-subscribe option

**Friday: Automation & Testing**
- [ ] Setup cron job for 7am daily
- [ ] Test sending to 5 test users
- [ ] Monitor email delivery (opens, clicks, bounces)
- [ ] Handle errors (failed sends, invalid emails)
- [ ] Document email system

**Deliverable:** Daily email digest sent to all active users

---

### Week 7: Deployment (Issues #23-26)

**Goal:** Live in production, accessible to beta users

**Monday: Server Setup**
- [ ] Provision DigitalOcean droplet ($6/mo: 1GB RAM, 25GB SSD)
- [ ] SSH key setup
- [ ] Install dependencies (Python 3.11, SQLite, nginx, certbot)
- [ ] Configure firewall (ports 22, 80, 443)
- [ ] Create deploy user and directory

**Tuesday: Application Deployment**
- [ ] Clone repository to server
- [ ] Setup Python virtual environment
- [ ] Install requirements
- [ ] Copy `.env` with production credentials
- [ ] Run database migrations
- [ ] Test app locally on server

**Wednesday: Web Server Configuration**
- [ ] Setup Gunicorn (WSGI server)
- [ ] Create systemd service for app
- [ ] Configure nginx reverse proxy
- [ ] Setup SSL certificate (Let's Encrypt)
- [ ] Configure domain name (ppde.app or similar)
- [ ] Test HTTPS access

**Thursday: Cron Jobs**
- [ ] Setup collection cron (2am daily)
- [ ] Setup digest cron (7am daily)
- [ ] Setup cleanup cron (delete old data, weekly)
- [ ] Configure logging paths
- [ ] Test cron execution

**Friday: Monitoring**
- [ ] Setup basic monitoring (uptime check)
- [ ] Configure error logging (to file)
- [ ] Setup email alerts for critical errors
- [ ] Create simple health check endpoint (`/health`)
- [ ] Document deployment process

**Deliverable:** App running in production at https://yourapp.com

---

### Week 8: Testing & Beta Launch (Issue #27)

**Goal:** 10 beta users actively using the app

**Monday-Tuesday: End-to-End Testing**
- [ ] Test data collection (verify cron ran)
- [ ] Test web application (all pages, all flows)
- [ ] Test email delivery (verify digest sent)
- [ ] Test edge cases:
  - No opportunities found (empty day)
  - Database errors
  - API rate limits exceeded
  - Invalid user input
- [ ] Fix all critical bugs

**Wednesday: Landing Page**
- [ ] Create simple landing page
  - Hero: "Discover Business Opportunities Before Your Competition"
  - Value prop: Daily list of problems people need solved
  - Screenshot of app
  - Beta signup form (email, name)
  - Testimonials (if we have them)
- [ ] Setup waitlist in database
- [ ] Auto-send invite email when ready

**Thursday: Beta Invites**
- [ ] Identify first 10 users:
  - Friends/colleagues who are entrepreneurs
  - Active indie hackers on Twitter
  - People in relevant communities
- [ ] Send personalized invite emails
- [ ] Onboard users (quick walkthrough)
- [ ] Ask for feedback

**Friday: Feedback & Iteration**
- [ ] Schedule 15-min calls with each user
- [ ] Ask key questions:
  - Did you find any opportunities interesting?
  - What's confusing or unclear?
  - What features are missing?
  - Would you pay for this?
- [ ] Prioritize feedback
- [ ] Make quick fixes
- [ ] Plan for WALK phase

**Deliverable:** 10 active beta users, clear feedback for improvements

---

## Database Schema

### SQLite Tables

```sql
-- Tweets table: Raw collected data
CREATE TABLE tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT UNIQUE NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    author_username TEXT,
    author_followers INTEGER,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    engagement_score INTEGER, -- likes + (retweets * 2)
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_engagement (engagement_score)
);

-- Pain analysis: Extracted features
CREATE TABLE pain_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id INTEGER REFERENCES tweets(id),
    frustration_score INTEGER, -- 0-10
    budget_signal_score INTEGER, -- 0-50
    products_mentioned TEXT, -- JSON array
    pain_keywords TEXT, -- JSON array of matched keywords
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tweet (tweet_id)
);

-- Opportunities: Aggregated pain points
CREATE TABLE opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL, -- "Invoice management for freelancers"
    description TEXT,
    score INTEGER NOT NULL, -- 0-100
    tweet_count INTEGER DEFAULT 0,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_score (score),
    INDEX idx_created_at (created_at)
);

-- Opportunity tweets: Many-to-many relationship
CREATE TABLE opportunity_tweets (
    opportunity_id INTEGER REFERENCES opportunities(id),
    tweet_id INTEGER REFERENCES tweets(id),
    PRIMARY KEY (opportunity_id, tweet_id)
);

-- Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT 0,
    INDEX idx_email (email)
);

-- Email preferences
CREATE TABLE email_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    enabled BOOLEAN DEFAULT 1,
    frequency TEXT DEFAULT 'daily', -- 'daily', 'weekly', 'off'
    min_score INTEGER DEFAULT 60,
    last_sent TIMESTAMP
);

-- Watchlist
CREATE TABLE watchlist (
    user_id INTEGER REFERENCES users(id),
    opportunity_id INTEGER REFERENCES opportunities(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    PRIMARY KEY (user_id, opportunity_id)
);
```

---

## Pain Expression Patterns

### 50+ Keyword Patterns to Search

**Frustration expressions:**
1. "why is there no"
2. "I can't believe there's no"
3. "still no solution for"
4. "how is there not a"
5. "someone needs to build"
6. "I wish someone would make"
7. "there should be a tool for"
8. "frustrated with"
9. "hate dealing with"
10. "sick of"

**Solution seeking:**
11. "does anyone know a tool for"
12. "looking for a way to"
13. "is there a service that"
14. "anyone have a solution for"
15. "recommendations for"
16. "what do you use for"
17. "how do you handle"
18. "what's the best way to"
19. "struggling with"
20. "need help with"

**Workaround mentions:**
21. "my janky solution is"
22. "I'm duct-taping together"
23. "currently using 3 tools for"
24. "built a spreadsheet to"
25. "manual process for"

**Time investment signals:**
26. "spent hours trying to"
27. "wasted all day"
28. "takes me forever to"
29. "so much time on"
30. "always spending time"

**Budget signals:**
31. "paying $"
32. "our team uses [paid tool]"
33. "tried [competitor] but"
34. "switching from [tool]"
35. "looking for alternative to"
36. "cheaper than"
37. "too expensive"

**Urgency markers:**
38. "need this ASAP"
39. "urgent:"
40. "immediately need"
41. "this week I need"
42. "deadline coming up"

**Frequency indicators:**
43. "every single time"
44. "daily struggle"
45. "always having to"
46. "constantly dealing with"
47. "this keeps happening"

**Impact statements:**
48. "losing customers because"
49. "costing us $"
50. "blocking our team"
51. "can't scale until"
52. "biggest pain point"

### Regex Patterns for Frustration

```python
FRUSTRATION_PATTERNS = [
    r'\b(hate|hating|frustrated|annoying|annoyed|sick of|fed up)\b',
    r'\b(wtf|wth|omg|ugh|argh)\b',
    r'\b(terrible|horrible|awful|worst)\s+\w+\s+(tool|app|service|software)',
    r'\b(why|how)\s+(is there no|isn\'t there a|don\'t we have)\b',
    r'[!]{2,}',  # Multiple exclamation marks
    r'CAPS{5,}',  # 5+ consecutive caps (yelling)
]

BUDGET_PATTERNS = [
    r'\$\d+',  # Dollar amounts
    r'\b(paying|pay|paid|spend|spent|cost|costs|expensive|cheap)\b',
    r'\b(subscription|monthly|annually|per month|per year)\b',
    r'\b(stripe|paypal|chargebee|paddle|braintree)\b',  # Payment processors
]
```

---

## Simple Scoring Algorithm (MVP)

```python
def calculate_opportunity_score(tweet_data):
    """
    Simple scoring algorithm for MVP
    Score range: 0-100
    """

    # Engagement Score (0-20 points)
    # Normalize by typical engagement levels
    engagement = tweet_data['likes'] + (tweet_data['retweets'] * 2)
    engagement_score = min(20, engagement / 10)  # Cap at 20

    # Frustration Score (0-30 points)
    frustration_keywords = count_frustration_keywords(tweet_data['text'])
    caps_ratio = count_caps_letters(tweet_data['text']) / len(tweet_data['text'])
    exclamation_marks = tweet_data['text'].count('!')

    frustration_score = (
        (frustration_keywords * 8) +  # Each keyword worth 8 points
        (caps_ratio * 100 * 0.15) +   # Caps percentage
        (min(exclamation_marks, 3) * 2)  # Exclamation marks (max 6 points)
    )
    frustration_score = min(30, frustration_score)

    # Budget Signal Score (0-50 points)
    has_dollar_amount = bool(re.search(r'\$\d+', tweet_data['text']))
    mentions_paid_tool = bool(re.search(KNOWN_PAID_TOOLS_REGEX, tweet_data['text']))
    mentions_payment_terms = count_payment_keywords(tweet_data['text'])

    budget_score = 0
    if has_dollar_amount:
        budget_score += 20
    if mentions_paid_tool:
        budget_score += 20
    budget_score += mentions_payment_terms * 5  # Each term worth 5
    budget_score = min(50, budget_score)

    # Total Score
    total = engagement_score + frustration_score + budget_score
    return round(total)


# Example:
# Tweet: "I'm paying $99/mo for Airtable and it STILL doesn't do what I need!
#         Why is there no simple database for small teams???"
#
# Engagement: 45 likes, 12 retweets = 45 + (12*2) = 69 → 6 points
# Frustration: "STILL" (caps), 3 exclamation marks, "why is there no" → 22 points
# Budget: "$99/mo" + "paying" + "Airtable" (paid tool) → 45 points
#
# Total Score: 73/100 ✅ High-quality opportunity
```

---

## Tech Stack Details

### Backend
```
Python 3.11
├── Flask 3.0 (web framework)
├── SQLite 3 (database)
├── Tweepy 4.14 (Twitter API)
├── SendGrid 6.11 (email)
├── Flask-Login (authentication)
├── bcrypt (password hashing)
└── python-dotenv (config management)
```

### Frontend
```
HTML5 + Jinja2 templates
Bootstrap 5.3 (CSS framework)
Vanilla JavaScript (minimal, no React yet)
```

### Infrastructure
```
DigitalOcean Droplet ($6/mo)
├── Ubuntu 22.04 LTS
├── Nginx (reverse proxy)
├── Gunicorn (WSGI server)
├── Certbot (SSL certificates)
└── Cron (scheduling)

SendGrid (Free tier: 100 emails/day)
```

### Development Tools
```
Git/GitHub (version control)
VS Code (editor)
pytest (testing)
black (code formatting)
flake8 (linting)
```

---

## File Structure

```
pain-point-discovery-engine/
├── backend/
│   ├── __init__.py
│   ├── app.py                 # Flask application
│   ├── models.py              # Database models
│   ├── auth.py                # Authentication logic
│   ├── pain_detector.py       # Pain detection algorithms
│   ├── scoring.py             # Opportunity scoring
│   └── utils.py               # Helper functions
├── scripts/
│   ├── collect_tweets.py      # Daily collection script
│   ├── send_daily_digest.py   # Email digest script
│   ├── daily_collection.sh    # Cron wrapper
│   └── test_twitter_auth.py   # Auth testing
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Homepage
│   ├── opportunity.html       # Detail page
│   ├── login.html             # Login form
│   ├── register.html          # Registration form
│   └── dashboard.html         # User dashboard
├── static/
│   ├── css/
│   │   └── custom.css         # Custom styles
│   └── js/
│       └── app.js             # Minimal JS
├── tests/
│   ├── test_pain_detector.py
│   ├── test_scoring.py
│   └── test_routes.py
├── data/
│   └── ppde.db                # SQLite database
├── logs/
│   ├── collection.log
│   └── app.log
├── requirements.txt           # Python dependencies
├── .env.example               # Config template
├── .gitignore
├── README.md
└── PRD.md                     # Full product spec
```

---

## Cost Breakdown (CRAWL Phase)

```
DigitalOcean Droplet:        $6/month
Domain name (ppde.app):       $12/year = $1/month
SendGrid (free tier):         $0/month
Twitter API (free tier):      $0/month (elevated access)
SSL certificate:              $0/month (Let's Encrypt)
─────────────────────────────
Total:                        ~$7/month = $56 for 8 weeks

One-time:
└── Domain registration:      $12

TOTAL CRAWL BUDGET:          ~$70
```

---

## Success Metrics (CRAWL)

### Quantitative
- [ ] 500-1000 tweets collected per day
- [ ] 10-20 opportunities scored per day
- [ ] 10+ beta users registered
- [ ] 60%+ users return next day (retention)
- [ ] 70%+ users find opportunities "interesting"
- [ ] <5% email bounce rate
- [ ] <2 second page load time
- [ ] Zero critical bugs in production

### Qualitative
- [ ] Users say "this is useful"
- [ ] Users share with friends
- [ ] Users request specific features
- [ ] Users ask "when can I pay?"
- [ ] Clear feedback on what to build next

---

## Risks & Mitigation

### Risk: Twitter API Access Denied
**Probability:** Low-Medium
**Impact:** Critical (no data = no product)
**Mitigation:**
- Apply for elevated access early (Week 1)
- Have Reddit integration plan ready as backup
- Consider using Twitter scraping libraries (less reliable but possible)
- Worst case: Pivot to Reddit-first approach

### Risk: Too Much Noise, Not Enough Signal
**Probability:** Medium-High
**Impact:** High (users won't find value)
**Mitigation:**
- Start with very specific pain keywords
- Manually review first 100 opportunities
- Tune scoring algorithm based on feedback
- Add manual curation layer if needed (not scalable but ok for MVP)

### Risk: No One Wants This
**Probability:** Low-Medium
**Impact:** Critical (no market)
**Mitigation:**
- Validate with interviews BEFORE building (Week 0)
- Beta test with 10 users who fit ICP
- Offer refund if we add payments
- Be ready to pivot based on feedback

### Risk: Can't Get 10 Beta Users
**Probability:** Low
**Impact:** Medium (can't validate)
**Mitigation:**
- Leverage personal network first
- Post in indie hacker communities
- Offer free lifetime access for early users
- Direct outreach to entrepreneurs on Twitter

### Risk: Infrastructure Issues
**Probability:** Low
**Impact:** Medium (downtime frustrates users)
**Mitigation:**
- Keep architecture simple (fewer failure points)
- Monitor uptime with external service
- Have deployment runbook documented
- Quick rollback process

---

## Week 0: Pre-Work Checklist

**Before starting Week 1, complete these:**

- [ ] **Customer Validation**
  - Interview 5 potential users
  - Ask: "How do you currently find business ideas?"
  - Ask: "Would you pay for a service that emails you opportunities daily?"
  - Validate problem exists

- [ ] **Technical Setup**
  - Install Python 3.11
  - Setup virtual environment
  - Create GitHub repo
  - Apply for Twitter Developer account
  - Register domain name

- [ ] **Team Alignment**
  - Review CRAWL plan with team/co-founder
  - Agree on success criteria
  - Set weekly check-in meetings
  - Assign responsibilities

- [ ] **Budget Approval**
  - Confirm $70 budget is available
  - Get DigitalOcean account
  - Get SendGrid account
  - Setup payment method for domain

---

## Daily Development Routine

**To stay on track, follow this daily routine:**

**Morning (2 hours):**
- [ ] Review yesterday's progress
- [ ] Check GitHub issues for today
- [ ] Set 1-3 concrete goals for the day
- [ ] Block time for focused work

**Afternoon (3-4 hours):**
- [ ] Execute on goals
- [ ] Commit code frequently (small commits)
- [ ] Write tests as you go
- [ ] Document as you build

**Evening (30 mins):**
- [ ] Review what got done
- [ ] Update GitHub issues
- [ ] Note any blockers
- [ ] Plan tomorrow's goals

**Weekly Review (Friday, 1 hour):**
- [ ] Review week's accomplishments
- [ ] Test everything end-to-end
- [ ] Identify what's behind schedule
- [ ] Adjust next week's plan
- [ ] Share progress update with stakeholders

---

## What NOT to Build in CRAWL

**Resist the temptation to build these (save for WALK/RUN):**

❌ **Machine Learning Models**
- Keyword matching is good enough for MVP
- ML adds complexity and training time
- 80% accuracy from keywords vs 85% from ML not worth it yet

❌ **Real-time Updates**
- Daily batch is fine for MVP
- Real-time adds architectural complexity
- Users don't need instant notifications yet

❌ **Multiple Platforms**
- Twitter has enough signal
- Each platform adds integration time
- Better to do one platform really well

❌ **Advanced Filters**
- Basic score + date filters are enough
- Can add categories/topics later
- Don't over-engineer before users ask

❌ **Mobile App**
- Responsive web app is sufficient
- Native apps are expensive to maintain
- Wait until users demand it

❌ **Social Features**
- No comments, likes, shares yet
- Focus on core value first
- Can add community later

❌ **Payment Integration**
- Keep it free during CRAWL
- Validate value before asking for money
- Easier to iterate without payment constraints

---

## Transition to WALK Phase

**After CRAWL is complete, evaluate these before moving to WALK:**

### Go/No-Go Criteria

**GO to WALK if:**
✅ 8+ of 10 beta users are actively using the app
✅ 70%+ users say they find opportunities "useful" or "very useful"
✅ Users are requesting more features (not complaining about bugs)
✅ 3+ users say they would pay for this
✅ Zero critical bugs in production
✅ Clear understanding of what to build next

**NO-GO (iterate on CRAWL) if:**
❌ <5 users are active
❌ Users say it's "interesting but not useful"
❌ Major bugs or reliability issues
❌ Unclear what users actually want
❌ No indication of willingness to pay

### What Changes in WALK

- ✅ Add Reddit + HackerNews (multi-platform)
- ✅ Replace keywords with ML models (higher accuracy)
- ✅ Add competitive intelligence (competitor analysis)
- ✅ Add market sizing (how big is this opportunity?)
- ✅ Rebuild frontend in React (better UX)
- ✅ Add payments (monetization)
- ✅ Scale infrastructure (handle 100+ users)

---

## Appendix: Code Snippets

### A. Twitter Collection Script (Pseudocode)

```python
# scripts/collect_tweets.py

import tweepy
import sqlite3
from datetime import datetime
from pain_detector import analyze_pain
from scoring import calculate_score

def collect_tweets():
    # Initialize Twitter API
    api = get_twitter_api()

    # Pain keywords to search
    pain_keywords = load_pain_keywords()

    tweets_collected = 0

    for keyword in pain_keywords:
        try:
            # Search tweets (max 100 per search)
            tweets = api.search_recent_tweets(
                query=keyword,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )

            for tweet in tweets.data:
                # Extract data
                tweet_data = {
                    'tweet_id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                }

                # Analyze pain
                pain_analysis = analyze_pain(tweet_data['text'])

                # Calculate score
                score = calculate_score(tweet_data, pain_analysis)

                # Store in database (if high enough score)
                if score >= 40:
                    store_tweet(tweet_data, pain_analysis, score)
                    tweets_collected += 1

        except Exception as e:
            log_error(f"Error with keyword '{keyword}': {e}")
            continue

    log_info(f"Collected {tweets_collected} tweets")

if __name__ == "__main__":
    collect_tweets()
```

### B. Pain Detection (Pseudocode)

```python
# backend/pain_detector.py

import re

FRUSTRATION_KEYWORDS = [
    'hate', 'frustrated', 'annoying', 'sick of', 'fed up',
    'terrible', 'horrible', 'awful', 'worst'
]

BUDGET_KEYWORDS = [
    'paying', 'expensive', 'subscription', 'monthly',
    'stripe', 'chargebee'
]

def analyze_pain(text):
    """Extract pain signals from text"""

    # Frustration level (0-10)
    frustration = 0
    for keyword in FRUSTRATION_KEYWORDS:
        if keyword in text.lower():
            frustration += 2
    frustration += count_exclamation_marks(text)
    frustration += calculate_caps_ratio(text) * 5
    frustration = min(10, frustration)

    # Budget signal (0-50)
    budget = 0
    if re.search(r'\$\d+', text):
        budget += 20
    for keyword in BUDGET_KEYWORDS:
        if keyword in text.lower():
            budget += 10
    budget = min(50, budget)

    # Extract products mentioned
    products = extract_products(text)

    return {
        'frustration_score': frustration,
        'budget_signal': budget,
        'products': products
    }
```

### C. Email Digest Template

```html
<!-- Daily digest email template -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }
        .opportunity { border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 8px; }
        .score { display: inline-block; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
        .score-high { background: #10b981; color: white; }
        .score-med { background: #f59e0b; color: white; }
    </style>
</head>
<body>
    <h1>🔥 5 Business Opportunities Discovered Yesterday</h1>

    {% for opp in opportunities %}
    <div class="opportunity">
        <h2>{{ opp.title }}</h2>
        <span class="score score-{{ 'high' if opp.score >= 70 else 'med' }}">
            Score: {{ opp.score }}/100
        </span>
        <p>{{ opp.description }}</p>
        <p><strong>{{ opp.tweet_count }}</strong> people mentioned this pain point</p>
        <a href="{{ base_url }}/opportunity/{{ opp.id }}">View Details →</a>
    </div>
    {% endfor %}

    <hr>
    <p style="color: #666; font-size: 12px;">
        <a href="{{ base_url }}/settings/email">Email Preferences</a> |
        <a href="{{ base_url }}/unsubscribe?token={{ unsubscribe_token }}">Unsubscribe</a>
    </p>
</body>
</html>
```

---

## Final Checklist: Ready for Beta Launch?

**Before inviting first users, verify:**

- [ ] Data collection running automatically (check logs)
- [ ] Opportunities being scored daily (check database)
- [ ] Web app accessible via HTTPS
- [ ] User registration working
- [ ] Login/logout working
- [ ] Homepage showing opportunities
- [ ] Detail pages working
- [ ] Watchlist functionality working
- [ ] Email digest sending successfully
- [ ] Email preferences page working
- [ ] No critical bugs
- [ ] Page load times <2 seconds
- [ ] Mobile-responsive design
- [ ] Privacy policy page (basic)
- [ ] Terms of service page (basic)
- [ ] Contact/support email setup
- [ ] Monitoring in place (uptime, errors)
- [ ] Backup strategy for database
- [ ] Deployment runbook documented
- [ ] README with setup instructions

**If all checked: LAUNCH! 🚀**

---

*Good luck building! Remember: Perfect is the enemy of shipped. Get CRAWL out the door, gather real feedback, then iterate to WALK.*
