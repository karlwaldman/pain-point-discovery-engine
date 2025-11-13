#!/usr/bin/env python3
"""
Reddit Pain Point Collection Script

Monitors Reddit for pain expressions in entrepreneurship/startup subreddits.
Analyzes posts and comments for pain signals.
"""

import os
import sys
import praw
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Tweet, PainAnalysis, Opportunity
from backend.pain_detector import analyze_pain
from backend.scoring import calculate_opportunity_score
from backend.pain_keywords import REDDIT_SUBREDDITS, REDDIT_SEARCH_QUERIES


def get_reddit_client():
    """Initialize Reddit API client (PRAW)."""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'PainPointDiscovery/1.0')

    if not client_id or not client_secret:
        raise ValueError(
            "Reddit API credentials not found. "
            "Get them from https://www.reddit.com/prefs/apps\n"
            "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env"
        )

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    return reddit


def search_subreddit(reddit, subreddit_name, query, limit=100):
    """
    Search a subreddit for posts matching query.

    Args:
        reddit: PRAW Reddit instance
        subreddit_name: Name of subreddit (without r/)
        query: Search query string
        limit: Maximum posts to retrieve

    Returns:
        List of post objects
    """
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []

        # Search for posts matching query
        for submission in subreddit.search(query, limit=limit, time_filter='week'):
            # Skip if it's a link post with no text
            if not submission.selftext and not submission.title:
                continue

            # Combine title and text for analysis
            full_text = submission.title
            if submission.selftext:
                full_text += "\n\n" + submission.selftext

            posts.append({
                'reddit_id': submission.id,
                'title': submission.title,
                'text': full_text,
                'created_at': datetime.fromtimestamp(submission.created_utc).isoformat(),
                'author': str(submission.author) if submission.author else '[deleted]',
                'upvotes': submission.score,
                'comments': submission.num_comments,
                'url': f"https://reddit.com{submission.permalink}",
                'subreddit': subreddit_name
            })

        return posts

    except Exception as e:
        print(f"Error searching r/{subreddit_name}: {e}")
        return []


def get_hot_posts(reddit, subreddit_name, limit=25):
    """
    Get hot posts from a subreddit (last 24 hours).

    These are often pain points that are currently resonating.
    """
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []

        for submission in subreddit.hot(limit=limit):
            # Skip stickied posts
            if submission.stickied:
                continue

            full_text = submission.title
            if submission.selftext:
                full_text += "\n\n" + submission.selftext

            posts.append({
                'reddit_id': submission.id,
                'title': submission.title,
                'text': full_text,
                'created_at': datetime.fromtimestamp(submission.created_utc).isoformat(),
                'author': str(submission.author) if submission.author else '[deleted]',
                'upvotes': submission.score,
                'comments': submission.num_comments,
                'url': f"https://reddit.com{submission.permalink}",
                'subreddit': subreddit_name
            })

        return posts

    except Exception as e:
        print(f"Error getting hot posts from r/{subreddit_name}: {e}")
        return []


def process_reddit_post(post_data):
    """
    Process a Reddit post: analyze, score, and store if valuable.

    We use the Tweet model to store Reddit posts (with reddit_id as tweet_id).
    This is fine for MVP - we'll separate in WALK phase if needed.

    Returns:
        Tuple of (stored: bool, score: int)
    """

    # Check if we already have this post
    if Tweet.exists(post_data['reddit_id']):
        return False, 0

    # Analyze pain signals
    pain_analysis = analyze_pain(post_data['text'])

    # Create tweet-like data structure for scoring
    # Reddit upvotes = likes, comments = engagement
    tweet_data = {
        'likes': post_data['upvotes'],
        'retweets': post_data['comments'] // 2,  # Approximate retweets from comments
        'replies': post_data['comments']
    }

    # Calculate opportunity score
    score = calculate_opportunity_score(tweet_data, pain_analysis)

    # Only store if score meets minimum threshold
    min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 40))

    if score < min_score:
        return False, score

    # Store post (using Tweet model)
    try:
        post_id = Tweet.create(
            tweet_id=post_data['reddit_id'],
            text=post_data['text'],
            created_at=post_data['created_at'],
            author_username=f"r/{post_data['subreddit']}",  # Store subreddit
            author_followers=post_data['upvotes'],  # Use upvotes as proxy
            likes=post_data['upvotes'],
            retweets=post_data['comments'] // 2,
            replies=post_data['comments']
        )

        # Store pain analysis
        PainAnalysis.create(
            tweet_id=post_id,
            frustration_score=pain_analysis['frustration_score'],
            budget_signal_score=pain_analysis['budget_signal_score'],
            products_mentioned=pain_analysis['products_mentioned'],
            pain_keywords=pain_analysis['pain_keywords']
        )

        return True, score

    except Exception as e:
        print(f"Error storing Reddit post: {e}")
        return False, score


def create_opportunity_from_reddit(post_id, post_data, score):
    """Create opportunity from Reddit post."""

    # Use title as opportunity title
    title = post_data['title'][:200].strip()

    # Create opportunity
    opportunity_id = Opportunity.create(
        title=f"[Reddit] {title}",
        description=post_data['text'][:500],  # First 500 chars
        score=score,
        first_seen=datetime.now().isoformat(),
        last_seen=datetime.now().isoformat()
    )

    # Link post to opportunity
    Opportunity.add_tweet(opportunity_id, post_id)

    return opportunity_id


def collect_from_reddit():
    """Main collection function for Reddit."""

    print("=" * 60)
    print("Reddit Pain Point Collection")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Load environment variables
    load_dotenv()

    # Initialize Reddit client
    try:
        reddit = get_reddit_client()
        print("✓ Reddit API client initialized")
        print(f"✓ User agent: {reddit.config.user_agent}")
    except Exception as e:
        print(f"✗ Failed to initialize Reddit client: {e}")
        print("\nTo use Reddit API:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'Create App' or 'Create Another App'")
        print("3. Select 'script' as type")
        print("4. Add credentials to .env file")
        return

    # Collection settings
    min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 40))
    posts_per_sub = 25

    print(f"✓ Settings loaded:")
    print(f"  - Posts per subreddit: {posts_per_sub}")
    print(f"  - Minimum score threshold: {min_score}")
    print(f"  - Monitoring {len(REDDIT_SUBREDDITS)} subreddits")
    print()

    # Stats tracking
    total_subs_searched = 0
    total_posts_found = 0
    total_stored = 0
    total_high_value = 0

    # Use top entrepreneurship subreddits for MVP
    subs_to_monitor = REDDIT_SUBREDDITS[:10]  # First 10 subs

    print(f"Monitoring {len(subs_to_monitor)} subreddits...")
    print()

    for i, subreddit_name in enumerate(subs_to_monitor, 1):
        print(f"[{i}/{len(subs_to_monitor)}] r/{subreddit_name}")

        # Get hot posts (trending pain points)
        posts = get_hot_posts(reddit, subreddit_name, limit=posts_per_sub)
        total_subs_searched += 1
        total_posts_found += len(posts)

        print(f"  Found: {len(posts)} hot posts")

        # Process each post
        stored_this_sub = 0
        high_value_this_sub = 0

        for post_data in posts:
            stored, score = process_reddit_post(post_data)

            if stored:
                stored_this_sub += 1
                total_stored += 1

                # Create opportunity
                post_id = Tweet.get_by_tweet_id(post_data['reddit_id'])['id']
                create_opportunity_from_reddit(post_id, post_data, score)

                if score >= 70:
                    high_value_this_sub += 1
                    total_high_value += 1
                    print(f"    ⭐ High-value: \"{post_data['title'][:60]}...\" (Score: {score})")

        print(f"  Stored: {stored_this_sub} posts (score >= {min_score})")
        if high_value_this_sub > 0:
            print(f"  🔥 High-value: {high_value_this_sub} (score >= 70)")
        print()

    # Final summary
    print("=" * 60)
    print("Collection Complete")
    print("=" * 60)
    print(f"Subreddits searched: {total_subs_searched}")
    print(f"Posts found: {total_posts_found}")
    print(f"Posts stored: {total_stored} (score >= {min_score})")
    print(f"High-value opportunities: {total_high_value} (score >= 70)")
    print(f"Success rate: {(total_stored / total_posts_found * 100) if total_posts_found > 0 else 0:.1f}%")
    print()
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        collect_from_reddit()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Collection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
