#!/usr/bin/env python3
"""
Test Firecrawl API for Twitter Scraping

Tests if we can use Firecrawl to scrape Twitter search results
instead of using the Twitter API.
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_firecrawl_twitter():
    """Test Firecrawl with Twitter search."""

    print("=" * 60)
    print("Firecrawl + Twitter Test")
    print("=" * 60)
    print()

    # Load environment
    load_dotenv()

    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        print("✗ FIRECRAWL_API_KEY not found in .env")
        print()
        print("Add to .env:")
        print("FIRECRAWL_API_KEY=your-api-key")
        return False

    print(f"✓ API Key found: {api_key[:10]}...")
    print()

    # Test URLs to try
    test_searches = [
        {
            'description': 'Twitter search (logged out)',
            'url': 'https://twitter.com/search?q=why%20is%20there%20no%20tool&src=typed_query&f=live'
        },
        {
            'description': 'Twitter search (x.com)',
            'url': 'https://x.com/search?q=frustrated%20with&src=typed_query&f=live'
        },
        {
            'description': 'Single tweet (public)',
            'url': 'https://twitter.com/elonmusk/status/1'
        }
    ]

    # Firecrawl API endpoint
    api_url = 'https://api.firecrawl.dev/v1/scrape'

    for test in test_searches:
        print(f"Testing: {test['description']}")
        print(f"URL: {test['url']}")
        print()

        # Prepare request
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'url': test['url'],
            'formats': ['markdown', 'html'],
            'onlyMainContent': True
        }

        try:
            # Make request
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    print("✓ Scrape successful!")
                    print()

                    # Check what we got
                    if 'data' in data:
                        content = data['data'].get('markdown', data['data'].get('html', ''))
                        print(f"Content length: {len(content)} characters")
                        print()
                        print("First 500 characters:")
                        print("-" * 60)
                        print(content[:500])
                        print("-" * 60)
                        print()

                        # Check if we actually got tweet content
                        if 'sign in' in content.lower() or 'log in' in content.lower():
                            print("⚠ Warning: Appears to show login page")
                        elif 'tweet' in content.lower() or 'post' in content.lower():
                            print("✓ Looks like we got actual tweet content!")
                        else:
                            print("? Unclear if content is useful")

                    return True
                else:
                    print(f"✗ Scrape failed: {data.get('error', 'Unknown error')}")

            elif response.status_code == 429:
                print("✗ Rate limit exceeded")
                print("Firecrawl has rate limits. Try again later.")

            elif response.status_code == 401:
                print("✗ Authentication failed")
                print("API key may be invalid or expired")

            else:
                print(f"✗ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Message: {error_data}")
                except:
                    print(f"Response: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print("✗ Request timeout (30 seconds)")

        except Exception as e:
            print(f"✗ Error: {e}")

        print()
        print("=" * 60)
        print()

    return False


def test_firecrawl_general():
    """Test Firecrawl with a simple website to verify it works."""

    print("Testing Firecrawl with a simple website first...")
    print()

    load_dotenv()
    api_key = os.getenv('FIRECRAWL_API_KEY')

    if not api_key:
        print("✗ No API key")
        return False

    # Test with a simple public website
    test_url = 'https://example.com'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'url': test_url,
        'formats': ['markdown']
    }

    try:
        response = requests.post(
            'https://api.firecrawl.dev/v1/scrape',
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ Firecrawl API is working!")
                content = data.get('data', {}).get('markdown', '')
                print(f"✓ Got {len(content)} characters from {test_url}")
                print()
                return True

        print("✗ Firecrawl test failed")
        print(response.text[:200])
        return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("Firecrawl API Test for Twitter Scraping")
    print("=" * 60)
    print()

    # First test if Firecrawl works at all
    if test_firecrawl_general():
        print()
        print("=" * 60)
        print("Now testing Twitter scraping...")
        print("=" * 60)
        print()

        # Then test Twitter
        success = test_firecrawl_twitter()

        if success:
            print()
            print("✅ Twitter scraping might be viable with Firecrawl!")
            print()
            print("Next steps:")
            print("1. Review the content quality")
            print("2. Check if we can get search results")
            print("3. Test rate limits")
            print("4. Build production scraper if viable")
        else:
            print()
            print("❌ Twitter scraping with Firecrawl doesn't look viable")
            print()
            print("Reasons could be:")
            print("- Twitter requires authentication")
            print("- Firecrawl can't bypass login wall")
            print("- Content is too dynamic/JavaScript-heavy")
            print()
            print("Recommendation: Stick with official Twitter API")

        sys.exit(0 if success else 1)
    else:
        print()
        print("❌ Firecrawl API not working")
        print("Check your API key and try again")
        sys.exit(1)
