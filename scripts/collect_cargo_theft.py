#!/usr/bin/env python3
"""
Cargo Theft Domain Research Collector

Specialized collector for cargo theft, freight fraud, and trucking security pain points.

Sources:
- Web search for cargo theft news/discussions
- Reddit (r/Truckers, r/FreightBrokers, r/Logistics)
- Industry-specific pain signals

This is a DOMAIN-FOCUSED approach vs broad social media scraping.
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Tweet, PainAnalysis, Opportunity
from backend.pain_detector import analyze_pain
from backend.scoring import calculate_opportunity_score


def search_web_cargo_theft(keyword):
    """
    Search web for cargo theft related content.

    Uses WebSearch tool to find recent discussions.
    """
    from backend.pain_keywords import CARGO_THEFT_KEYWORDS

    # Import WebSearch capability
    try:
        # We'll use the WebSearch tool available in the environment
        # For now, return placeholder - will integrate with actual web search
        print(f"  🔍 Searching web for: {keyword}")

        # TODO: Integrate with actual WebSearch tool
        # For MVP, we'll focus on Reddit which we can access

        return []

    except Exception as e:
        print(f"  ✗ Web search error: {e}")
        return []


def search_reddit_cargo_theft(keyword, subreddit, limit=25):
    """
    Search specific subreddit for cargo theft keywords.

    Note: Requires Reddit credentials to be set up.
    """
    try:
        import praw

        # Check if Reddit credentials are available
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')

        if not reddit_client_id or not reddit_client_secret:
            print(f"  ⏩ Reddit not configured, skipping r/{subreddit}")
            return []

        # Initialize Reddit
        reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=os.getenv('REDDIT_USER_AGENT', 'CargoTheftResearch/1.0')
        )

        print(f"  🔍 Searching r/{subreddit} for: {keyword}")

        # Search subreddit
        results = []
        subreddit_obj = reddit.subreddit(subreddit)

        for submission in subreddit_obj.search(keyword, limit=limit, time_filter='month'):
            results.append({
                'id': submission.id,
                'title': submission.title,
                'text': submission.selftext,
                'author': str(submission.author),
                'score': submission.score,
                'num_comments': submission.num_comments,
                'created_utc': submission.created_utc,
                'url': f"https://reddit.com{submission.permalink}",
                'subreddit': subreddit
            })

        return results

    except ImportError:
        print(f"  ⏩ PRAW not installed, skipping Reddit")
        return []
    except Exception as e:
        print(f"  ✗ Reddit search error: {e}")
        return []


def process_cargo_theft_post(post, source_type='reddit'):
    """Process a cargo theft related post for pain signals."""

    # Combine title and text
    title = post.get('title', '')
    text = post.get('text', '') or post.get('selftext', '')
    full_text = f"{title}\n\n{text}"

    if not full_text or len(full_text) < 20:
        return False, 0

    # Create unique ID
    post_id = f"{source_type.upper()}_{post.get('id', '')}"

    # Check if already exists
    if Tweet.exists(post_id):
        return False, 0

    # Analyze pain - cargo theft should score high on frustration + budget signals
    pain_analysis = analyze_pain(full_text)

    # Boost score for cargo theft specific keywords
    from backend.pain_keywords import CARGO_THEFT_KEYWORDS, CARGO_THEFT_PAIN_PHRASES

    cargo_boost = 0
    text_lower = full_text.lower()

    # Check for high-value cargo theft keywords
    for keyword in CARGO_THEFT_KEYWORDS:
        if keyword in text_lower:
            cargo_boost += 5

    # Check for pain phrases
    for phrase in CARGO_THEFT_PAIN_PHRASES:
        if phrase in text_lower:
            cargo_boost += 10

    # Create engagement data
    tweet_data = {
        'likes': post.get('score', 0),
        'retweets': post.get('num_comments', 0) // 2,
        'replies': post.get('num_comments', 0)
    }

    # Calculate base score
    score = calculate_opportunity_score(tweet_data, pain_analysis)

    # Add cargo theft domain boost (max +30)
    score = min(100, score + min(30, cargo_boost))

    # Only store if meets threshold (lower for domain research)
    min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 30))  # Lower threshold for domain research
    if score < min_score:
        return False, score

    # Store
    try:
        created_at = datetime.fromtimestamp(post.get('created_utc', time.time())).isoformat()

        tweet_id = Tweet.create(
            tweet_id=post_id,
            text=full_text[:1000],
            created_at=created_at,
            author_username=post.get('author', 'unknown'),
            author_followers=0,
            likes=post.get('score', 0),
            retweets=post.get('num_comments', 0) // 2,
            replies=post.get('num_comments', 0)
        )

        # Pain analysis
        PainAnalysis.create(
            tweet_id=tweet_id,
            frustration_score=pain_analysis['frustration_score'],
            budget_signal_score=pain_analysis['budget_signal_score'],
            products_mentioned=pain_analysis['products_mentioned'],
            pain_keywords=pain_analysis['pain_keywords']
        )

        # Create opportunity
        subreddit = post.get('subreddit', 'WEB')
        opportunity_id = Opportunity.create(
            title=f"[CARGO THEFT - r/{subreddit}] {title[:100]}",
            description=f"{full_text[:400]}\n\nSource: {post.get('url', 'N/A')}",
            score=score,
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat()
        )

        Opportunity.add_tweet(opportunity_id, tweet_id)

        return True, score

    except Exception as e:
        print(f"    ✗ Error storing: {e}")
        return False, 0


def collect_cargo_theft():
    """Main cargo theft collection function."""

    print("=" * 70)
    print("CARGO THEFT DOMAIN RESEARCH")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Domain: Logistics & Freight Security")
    print("Focus: Cargo theft, freight fraud, trucking security")
    print()

    load_dotenv()

    from backend.pain_keywords import CARGO_THEFT_KEYWORDS, CARGO_THEFT_SUBREDDITS

    total_found = 0
    total_stored = 0
    total_high_value = 0

    # Select top keywords and subreddits
    selected_keywords = CARGO_THEFT_KEYWORDS[:5]  # Top 5 keywords
    selected_subreddits = CARGO_THEFT_SUBREDDITS[:4]  # Top 4 subreddits

    print(f"Searching {len(selected_subreddits)} subreddits × {len(selected_keywords)} keywords...")
    print()

    search_count = 0

    # Search Reddit
    for subreddit in selected_subreddits:
        for keyword in selected_keywords:
            search_count += 1
            print(f"[{search_count}/{len(selected_subreddits) * len(selected_keywords)}] r/{subreddit} + \"{keyword}\"")

            posts = search_reddit_cargo_theft(keyword, subreddit, limit=10)
            total_found += len(posts)

            if posts:
                print(f"  Found: {len(posts)} posts")

            stored_this_search = 0
            high_value_this_search = 0

            for post in posts:
                stored, score = process_cargo_theft_post(post, source_type='reddit')

                if stored:
                    stored_this_search += 1
                    total_stored += 1

                    if score >= 70:
                        high_value_this_search += 1
                        total_high_value += 1

                        title = post.get('title', '')[:50]
                        print(f"    🔥 High-value: \"{title}...\" (Score: {score})")

            if stored_this_search > 0:
                print(f"  Stored: {stored_this_search} posts")
                if high_value_this_search > 0:
                    print(f"  🎯 High-value: {high_value_this_search}")
            print()

            time.sleep(0.5)  # Rate limiting

    # Summary
    print("=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)
    print(f"Searches executed: {search_count}")
    print(f"Posts found: {total_found}")
    print(f"Posts stored: {total_stored}")
    print(f"High-value: {total_high_value} (score >= 70)")
    print()

    # Show top cargo theft opportunities
    opps = Opportunity.get_top_opportunities(limit=10, min_score=30, days=30)

    cargo_opps = [o for o in opps if 'CARGO THEFT' in o['title'] or 'FREIGHT' in o['title'].upper()]

    if cargo_opps:
        print("🚛 TOP CARGO THEFT OPPORTUNITIES:")
        print("-" * 70)
        for i, opp in enumerate(cargo_opps[:10], 1):
            # Extract title after tag
            title_parts = opp['title'].split('] ', 1)
            title = title_parts[1] if len(title_parts) > 1 else opp['title']
            print(f"{i:2}. [{opp['score']:3}/100] {title[:55]}...")
    else:
        print("No cargo theft opportunities found.")
        print()
        print("Next steps:")
        print("1. Set up Reddit credentials (see QUICKSTART.md)")
        print("2. Or manually research:")
        print("   - r/Truckers")
        print("   - r/FreightBrokers")
        print("   - FreightWaves.com")
        print("   - Transport Topics")

    print("=" * 70)


if __name__ == "__main__":
    try:
        collect_cargo_theft()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Collection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
