#!/usr/bin/env python3
"""
Twitter/X Pain Point Collection Script

Searches Twitter for pain expressions using the Twitter API v2.
Analyzes tweets for pain signals and stores high-scoring opportunities.
"""

import os
import sys
import tweepy
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Tweet, PainAnalysis, Opportunity
from backend.pain_detector import analyze_pain
from backend.scoring import calculate_opportunity_score
from backend.pain_keywords import (
    TWITTER_SEARCH_QUERIES,
    build_twitter_query,
    FRUSTRATION_PHRASES,
    SOLUTION_SEEKING_PHRASES
)


def get_twitter_client():
    """Initialize Twitter API v2 client."""
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN not found in environment")

    client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    return client


def search_tweets(client, query, max_results=100):
    """
    Search for tweets using Twitter API v2.

    Args:
        client: Tweepy client
        query: Search query string
        max_results: Maximum tweets to retrieve (10-100)

    Returns:
        List of tweet objects
    """
    try:
        # Twitter API v2 search
        response = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),  # API limit
            tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
            user_fields=['username', 'public_metrics'],
            expansions=['author_id']
        )

        if not response.data:
            return []

        # Build user lookup dict
        users = {}
        if response.includes and 'users' in response.includes:
            for user in response.includes['users']:
                users[user.id] = user

        tweets = []
        for tweet in response.data:
            # Get author info
            author = users.get(tweet.author_id)
            author_username = author.username if author else None
            author_followers = author.public_metrics['followers_count'] if author else 0

            tweets.append({
                'tweet_id': str(tweet.id),
                'text': tweet.text,
                'created_at': tweet.created_at.isoformat(),
                'author_username': author_username,
                'author_followers': author_followers,
                'likes': tweet.public_metrics['like_count'],
                'retweets': tweet.public_metrics['retweet_count'],
                'replies': tweet.public_metrics['reply_count'],
            })

        return tweets

    except tweepy.TweepyException as e:
        print(f"Error searching tweets: {e}")
        return []


def process_tweet(tweet_data):
    """
    Process a single tweet: analyze, score, and store if valuable.

    Returns:
        Tuple of (stored: bool, score: int)
    """

    # Check if we already have this tweet
    if Tweet.exists(tweet_data['tweet_id']):
        return False, 0

    # Analyze pain signals
    pain_analysis = analyze_pain(tweet_data['text'])

    # Calculate opportunity score
    score = calculate_opportunity_score(tweet_data, pain_analysis)

    # Only store if score meets minimum threshold
    min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 40))

    if score < min_score:
        return False, score

    # Store tweet
    try:
        tweet_id = Tweet.create(
            tweet_id=tweet_data['tweet_id'],
            text=tweet_data['text'],
            created_at=tweet_data['created_at'],
            author_username=tweet_data['author_username'],
            author_followers=tweet_data['author_followers'],
            likes=tweet_data['likes'],
            retweets=tweet_data['retweets'],
            replies=tweet_data['replies']
        )

        # Store pain analysis
        PainAnalysis.create(
            tweet_id=tweet_id,
            frustration_score=pain_analysis['frustration_score'],
            budget_signal_score=pain_analysis['budget_signal_score'],
            products_mentioned=pain_analysis['products_mentioned'],
            pain_keywords=pain_analysis['pain_keywords']
        )

        return True, score

    except Exception as e:
        print(f"Error storing tweet: {e}")
        return False, score


def create_or_update_opportunity(tweet_id, tweet_text, score):
    """
    Create a new opportunity or update existing one.

    For MVP, we create one opportunity per tweet.
    In WALK phase, we'll cluster similar tweets.
    """
    # Extract title from first 100 chars
    title = tweet_text[:100].strip()
    if len(tweet_text) > 100:
        title += "..."

    # Create opportunity
    opportunity_id = Opportunity.create(
        title=title,
        description=tweet_text,
        score=score,
        first_seen=datetime.now().isoformat(),
        last_seen=datetime.now().isoformat()
    )

    # Link tweet to opportunity
    Opportunity.add_tweet(opportunity_id, tweet_id)

    return opportunity_id


def collect_from_twitter():
    """Main collection function."""

    print("=" * 60)
    print("Twitter Pain Point Collection")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Load environment variables
    load_dotenv()

    # Initialize Twitter client
    try:
        client = get_twitter_client()
        print("✓ Twitter API client initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Twitter client: {e}")
        return

    # Collection settings
    max_results = int(os.getenv('MAX_RESULTS_PER_REQUEST', 100))
    min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 40))

    print(f"✓ Settings loaded:")
    print(f"  - Max results per query: {max_results}")
    print(f"  - Minimum score threshold: {min_score}")
    print()

    # Stats tracking
    total_searched = 0
    total_found = 0
    total_stored = 0
    total_high_value = 0  # Score >= 70

    # Use first 10 queries for MVP (to avoid rate limits)
    queries_to_use = TWITTER_SEARCH_QUERIES[:10]

    print(f"Running {len(queries_to_use)} search queries...")
    print()

    for i, keyword_query in enumerate(queries_to_use, 1):
        print(f"[{i}/{len(queries_to_use)}] Searching: \"{keyword_query}\"")

        # Build proper Twitter API query
        query = build_twitter_query([keyword_query])

        # Search
        tweets = search_tweets(client, query, max_results=max_results)
        total_searched += 1
        total_found += len(tweets)

        print(f"  Found: {len(tweets)} tweets")

        # Process each tweet
        stored_this_query = 0
        high_value_this_query = 0

        for tweet_data in tweets:
            stored, score = process_tweet(tweet_data)

            if stored:
                stored_this_query += 1
                total_stored += 1

                # Create opportunity
                create_or_update_opportunity(
                    tweet_id=Tweet.get_by_tweet_id(tweet_data['tweet_id'])['id'],
                    tweet_text=tweet_data['text'],
                    score=score
                )

                if score >= 70:
                    high_value_this_query += 1
                    total_high_value += 1
                    print(f"    ⭐ High-value opportunity found! Score: {score}")

        print(f"  Stored: {stored_this_query} tweets (score >= {min_score})")
        if high_value_this_query > 0:
            print(f"  🔥 High-value: {high_value_this_query} (score >= 70)")
        print()

    # Final summary
    print("=" * 60)
    print("Collection Complete")
    print("=" * 60)
    print(f"Queries executed: {total_searched}")
    print(f"Tweets found: {total_found}")
    print(f"Tweets stored: {total_stored} (score >= {min_score})")
    print(f"High-value opportunities: {total_high_value} (score >= 70)")
    print(f"Success rate: {(total_stored / total_found * 100) if total_found > 0 else 0:.1f}%")
    print()
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        collect_from_twitter()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Collection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
