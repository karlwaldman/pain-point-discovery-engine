#!/usr/bin/env python3
"""
Test Twitter API Authentication

Verifies that Twitter API credentials are valid and working.
Provides instructions for getting new credentials if needed.
"""

import os
import sys
import tweepy
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_twitter_auth():
    """Test Twitter API credentials."""

    print("=" * 60)
    print("Twitter API Authentication Test")
    print("=" * 60)
    print()

    # Load environment variables
    load_dotenv()

    # Check if credentials exist
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')

    print("Checking credentials...")
    print()

    if not bearer_token:
        print("✗ TWITTER_BEARER_TOKEN not found in .env")
        print_instructions()
        return False

    if not api_key:
        print("⚠ TWITTER_API_KEY not found (optional for v2 API)")

    if not api_secret:
        print("⚠ TWITTER_API_SECRET not found (optional for v2 API)")

    print("✓ Credentials found in .env")
    print()

    # Test authentication
    print("Testing Bearer Token authentication...")
    try:
        client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

        # Test with a simple request (get our own user)
        # This should work if the bearer token is valid
        me = client.get_me()

        if me and me.data:
            print(f"✓ Authentication successful!")
            print(f"✓ Authenticated as: @{me.data.username}")
            print()
            return True
        else:
            # Bearer token is valid but we can't get user (read-only app)
            # Try a simple search instead
            print("Testing with search...")
            response = client.search_recent_tweets(
                query="test -is:retweet",
                max_results=10
            )

            if response:
                print("✓ Authentication successful!")
                print("✓ Bearer token is valid (read-only access)")
                print()
                return True

    except tweepy.Unauthorized:
        print("✗ Authentication failed: 401 Unauthorized")
        print()
        print("This means your Bearer Token is invalid or expired.")
        print()
        print_instructions()
        return False

    except tweepy.Forbidden:
        print("✗ Authentication failed: 403 Forbidden")
        print()
        print("Your app doesn't have the required permissions.")
        print_instructions()
        return False

    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print()
        print_instructions()
        return False


def print_instructions():
    """Print instructions for getting Twitter API access."""

    print("=" * 60)
    print("HOW TO GET TWITTER API ACCESS")
    print("=" * 60)
    print()
    print("1. Go to: https://developer.twitter.com/")
    print()
    print("2. Sign in with your Twitter account")
    print()
    print("3. Apply for Elevated Access:")
    print("   - Click 'Developer Portal'")
    print("   - Click 'Elevated' under your project")
    print("   - Fill out the application form")
    print("   - Describe your use case:")
    print("     'Building a pain point discovery tool to identify")
    print("      business opportunities from social media conversations'")
    print()
    print("4. Create a Project and App:")
    print("   - Name: Pain Point Discovery Engine")
    print("   - Type: Read-only")
    print()
    print("5. Get your Bearer Token:")
    print("   - Go to your app settings")
    print("   - Under 'Keys and tokens'")
    print("   - Generate Bearer Token")
    print()
    print("6. Update .env file:")
    print("   TWITTER_BEARER_TOKEN=your-bearer-token-here")
    print()
    print("=" * 60)
    print()
    print("NOTE: Approval can take 1-3 days for Elevated Access")
    print()


if __name__ == "__main__":
    success = test_twitter_auth()

    if success:
        print("✅ Ready to collect data from Twitter!")
        print()
        print("Run: python scripts/collect_tweets.py")
        sys.exit(0)
    else:
        print("❌ Twitter API not configured")
        print()
        print("Follow the instructions above to get access.")
        sys.exit(1)
