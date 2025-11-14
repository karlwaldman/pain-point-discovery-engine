#!/usr/bin/env python3
"""
HackerNews Pain Point Collection

Uses HackerNews Algolia API (free, public, no auth needed) to find:
- "Ask HN" posts about pain points
- Comments discussing frustrations
- Feature requests and problems

Much cleaner than scraping with Firecrawl!
"""

import os
import sys
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Tweet, PainAnalysis, Opportunity
from backend.pain_detector import analyze_pain
from backend.scoring import calculate_opportunity_score


def search_hackernews(query, num_results=50):
    """
    Search HackerNews using Algolia API.

    API Docs: https://hn.algolia.com/api
    Free, no auth required!
    """
    url = 'https://hn.algolia.com/api/v1/search'

    params = {
        'query': query,
        'tags': 'ask_hn',  # Only "Ask HN" posts
        'hitsPerPage': num_results
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get('hits', [])
        else:
            print(f"  ✗ API error: {response.status_code}")
            return []

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []


def process_hn_post(post):
    """Process a HackerNews post for pain signals."""

    # Combine title and text (if available)
    title = post.get('title', '')
    text = post.get('story_text', '')
    full_text = f"{title}\n\n{text}" if text else title

    if not full_text or len(full_text) < 20:
        return False, 0

    # Check if already exists (use HN post ID)
    hn_id = str(post.get('objectID', ''))
    if Tweet.exists(hn_id):
        return False, 0

    # Analyze pain
    pain_analysis = analyze_pain(full_text)

    # Create engagement data from HN metrics
    points = post.get('points', 0)
    num_comments = post.get('num_comments', 0)

    tweet_data = {
        'likes': points,
        'retweets': num_comments // 2,  # Approximate
        'replies': num_comments
    }

    # Score
    score = calculate_opportunity_score(tweet_data, pain_analysis)

    # Only store if meets threshold
    min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 40))
    if score < min_score:
        return False, score

    # Store
    try:
        tweet_id = Tweet.create(
            tweet_id=hn_id,
            text=full_text[:1000],
            created_at=post.get('created_at', datetime.now().isoformat()),
            author_username=post.get('author', 'unknown'),
            author_followers=points,  # Use points as proxy
            likes=points,
            retweets=num_comments // 2,
            replies=num_comments
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
        opportunity_id = Opportunity.create(
            title=f"[HN] {title[:150]}",
            description=full_text[:500],
            score=score,
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat()
        )

        Opportunity.add_tweet(opportunity_id, tweet_id)

        return True, score

    except Exception as e:
        print(f"    ✗ Error storing: {e}")
        return False, 0


def collect_from_hackernews():
    """Main HackerNews collection function."""

    print("=" * 60)
    print("HACKERNEWS PAIN POINT COLLECTION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    load_dotenv()

    # Search queries for pain points
    pain_queries = [
        "why is there no",
        "frustrated with",
        "looking for tool",
        "does anyone know",
        "pain point",
        "biggest problem",
        "wish someone would build",
        "struggling with",
        "better way to",
    ]

    total_found = 0
    total_stored = 0
    total_high_value = 0

    print(f"Running {len(pain_queries)} search queries...")
    print()

    for i, query in enumerate(pain_queries, 1):
        print(f"[{i}/{len(pain_queries)}] Searching: \"{query}\"")

        posts = search_hackernews(query, num_results=20)
        total_found += len(posts)

        print(f"  Found: {len(posts)} Ask HN posts")

        stored_this_query = 0
        high_value_this_query = 0

        for post in posts:
            stored, score = process_hn_post(post)

            if stored:
                stored_this_query += 1
                total_stored += 1

                if score >= 70:
                    high_value_this_query += 1
                    total_high_value += 1

                    title = post.get('title', '')[:60]
                    print(f"    ⭐ High-value: \"{title}...\" (Score: {score})")

        print(f"  Stored: {stored_this_query} posts")
        if high_value_this_query > 0:
            print(f"  🔥 High-value: {high_value_this_query}")
        print()

        time.sleep(1)  # Rate limiting (being nice to HN API)

    # Summary
    print("=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Queries executed: {len(pain_queries)}")
    print(f"Posts found: {total_found}")
    print(f"Posts stored: {total_stored}")
    print(f"High-value: {total_high_value} (score >= 70)")
    print()

    # Show top opportunities
    opps = Opportunity.get_top_opportunities(limit=5, min_score=40, days=1)

    hn_opps = [o for o in opps if o['title'].startswith('[HN]')]

    if hn_opps:
        print("🔥 TOP 5 HACKERNEWS OPPORTUNITIES:")
        print("-" * 60)
        for i, opp in enumerate(hn_opps[:5], 1):
            title = opp['title'][5:].strip()  # Remove [HN] prefix
            print(f"{i}. [{opp['score']}/100] {title[:60]}...")

    print("=" * 60)


if __name__ == "__main__":
    try:
        collect_from_hackernews()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Collection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
