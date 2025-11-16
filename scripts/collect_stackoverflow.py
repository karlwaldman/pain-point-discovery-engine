#!/usr/bin/env python3
"""
Stack Overflow Pain Point Collection

Uses Stack Exchange API (free, no auth needed) to find:
- Technical DevOps/infrastructure pain points
- API and integration challenges
- Performance and scalability issues
- Missing features in existing tools

High B2B value - developers have budgets and decision-making power!
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


def search_stackoverflow(tag, keyword=None, min_votes=5):
    """
    Search Stack Overflow using Stack Exchange API.

    API Docs: https://api.stackexchange.com/docs/search
    Free, no auth required! 300 requests/day
    """
    url = 'https://api.stackexchange.com/2.3/search/advanced'

    params = {
        'site': 'stackoverflow',
        'tagged': tag,
        'sort': 'votes',
        'order': 'desc',
        'pagesize': 20,
        'filter': 'withbody',  # Include question body
    }

    # Add keyword to title search if provided
    if keyword:
        params['q'] = keyword

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Check quota
            quota_remaining = data.get('quota_remaining', 0)
            if quota_remaining < 10:
                print(f"  ⚠ Low quota remaining: {quota_remaining}")

            items = data.get('items', [])
            # Filter by minimum votes
            filtered = [q for q in items if q.get('score', 0) >= min_votes]
            return filtered
        else:
            print(f"  ✗ API error: {response.status_code}")
            return []

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []


def process_stackoverflow_question(question):
    """Process a Stack Overflow question for pain signals."""

    # Combine title and body (if available)
    title = question.get('title', '')
    body = question.get('body', '')

    # Remove HTML tags from body
    import re
    body_clean = re.sub(r'<[^>]+>', '', body)

    full_text = f"{title}\n\n{body_clean[:500]}"  # Limit body to 500 chars

    if not full_text or len(full_text) < 20:
        return False, 0

    # Check if already exists (use SO question ID)
    so_id = str(question.get('question_id', ''))
    if Tweet.exists(f"SO_{so_id}"):
        return False, 0

    # Analyze pain
    pain_analysis = analyze_pain(full_text)

    # Create engagement data from SO metrics
    score = question.get('score', 0)
    view_count = question.get('view_count', 0)
    answer_count = question.get('answer_count', 0)

    # High votes + high views + few answers = painful unsolved problem
    tweet_data = {
        'likes': score * 2,  # Upvotes indicate shared pain
        'retweets': view_count // 100,  # Many views = widespread issue
        'replies': answer_count
    }

    # Calculate opportunity score
    opp_score = calculate_opportunity_score(tweet_data, pain_analysis)

    # Boost score if question is unanswered or poorly answered
    if answer_count == 0:
        opp_score += 10  # Unanswered = gap in solutions
    elif not question.get('is_answered', False):
        opp_score += 5  # No accepted answer = no good solution

    opp_score = min(100, opp_score)

    # Only store if meets threshold
    min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 40))
    if opp_score < min_score:
        return False, opp_score

    # Store
    try:
        tweet_id = Tweet.create(
            tweet_id=f"SO_{so_id}",
            text=full_text[:1000],
            created_at=datetime.fromtimestamp(question.get('creation_date', time.time())).isoformat(),
            author_username=question.get('owner', {}).get('display_name', 'unknown'),
            author_followers=question.get('owner', {}).get('reputation', 0) // 100,
            likes=score * 2,
            retweets=view_count // 100,
            replies=answer_count
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
        tags = ', '.join(question.get('tags', [])[:3])
        opportunity_id = Opportunity.create(
            title=f"[SO/{tags}] {title[:120]}",
            description=f"{full_text[:400]}\n\nLink: {question.get('link', '')}",
            score=opp_score,
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat()
        )

        Opportunity.add_tweet(opportunity_id, tweet_id)

        return True, opp_score

    except Exception as e:
        print(f"    ✗ Error storing: {e}")
        return False, 0


def collect_from_stackoverflow():
    """Main Stack Overflow collection function."""

    print("=" * 60)
    print("STACK OVERFLOW PAIN POINT COLLECTION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    load_dotenv()

    # Import search parameters from pain_keywords
    from backend.pain_keywords import STACKOVERFLOW_TAGS, STACKOVERFLOW_KEYWORDS

    total_found = 0
    total_stored = 0
    total_high_value = 0

    # Strategy: Search top tags with pain keywords
    # Limit to avoid hitting 300 req/day quota
    selected_tags = STACKOVERFLOW_TAGS[:5]  # Top 5 most valuable tags
    selected_keywords = STACKOVERFLOW_KEYWORDS[:3]  # Top 3 pain keywords

    print(f"Searching {len(selected_tags)} tags × {len(selected_keywords)} keywords...")
    print()

    search_count = 0

    for tag in selected_tags:
        for keyword in selected_keywords:
            search_count += 1
            print(f"[{search_count}/{len(selected_tags) * len(selected_keywords)}] Tag: {tag}, Keyword: \"{keyword}\"")

            questions = search_stackoverflow(tag, keyword, min_votes=3)
            total_found += len(questions)

            print(f"  Found: {len(questions)} questions")

            stored_this_search = 0
            high_value_this_search = 0

            for question in questions:
                stored, score = process_stackoverflow_question(question)

                if stored:
                    stored_this_search += 1
                    total_stored += 1

                    if score >= 70:
                        high_value_this_search += 1
                        total_high_value += 1

                        title = question.get('title', '')[:50]
                        print(f"    ⭐ High-value: \"{title}...\" (Score: {score})")

            print(f"  Stored: {stored_this_search} questions")
            if high_value_this_search > 0:
                print(f"  🔥 High-value: {high_value_this_search}")
            print()

            time.sleep(0.5)  # Rate limiting (being nice to SO API)

    # Summary
    print("=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Searches executed: {search_count}")
    print(f"Questions found: {total_found}")
    print(f"Questions stored: {total_stored}")
    print(f"High-value: {total_high_value} (score >= 70)")
    print()

    # Show top opportunities
    opps = Opportunity.get_top_opportunities(limit=5, min_score=40, days=1)

    so_opps = [o for o in opps if o['title'].startswith('[SO/')]

    if so_opps:
        print("🔥 TOP 5 STACK OVERFLOW OPPORTUNITIES:")
        print("-" * 60)
        for i, opp in enumerate(so_opps[:5], 1):
            # Extract title after [SO/tags]
            title_parts = opp['title'].split('] ', 1)
            title = title_parts[1] if len(title_parts) > 1 else opp['title']
            print(f"{i}. [{opp['score']}/100] {title[:60]}...")

    print("=" * 60)


if __name__ == "__main__":
    try:
        collect_from_stackoverflow()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Collection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
