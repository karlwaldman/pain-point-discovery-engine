#!/usr/bin/env python3
"""
Firecrawl-based Pain Point Collection

Scrapes pain points from public sites using Firecrawl:
- HackerNews (Ask HN, Show HN)
- Indie Hackers (community posts)
- Product Hunt (product comments)

These sites are public and NOT blocked by Firecrawl (unlike Twitter).
"""

import os
import sys
import requests
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Tweet, PainAnalysis, Opportunity
from backend.pain_detector import analyze_pain
from backend.scoring import calculate_opportunity_score


class FirecrawlCollector:
    """Collector using Firecrawl API for public sites."""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('FIRECRAWL_API_KEY')
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment")

        self.base_url = 'https://api.firecrawl.dev/v1'
        self.min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 40))

    def scrape_url(self, url, description=""):
        """Scrape a URL using Firecrawl."""
        print(f"  Scraping: {description or url}")

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'url': url,
            'formats': ['markdown'],
            'onlyMainContent': True
        }

        try:
            response = requests.post(
                f'{self.base_url}/scrape',
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    content = data.get('data', {}).get('markdown', '')
                    print(f"    ✓ Got {len(content)} characters")
                    return content
                else:
                    print(f"    ✗ Failed: {data.get('error', 'Unknown error')}")
                    return None

            elif response.status_code == 429:
                print("    ⚠ Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                return None

            elif response.status_code == 403:
                print(f"    ✗ Site is blocked by Firecrawl")
                return None

            else:
                print(f"    ✗ Error {response.status_code}")
                return None

        except Exception as e:
            print(f"    ✗ Error: {e}")
            return None

    def extract_posts_from_markdown(self, content, source_type):
        """Extract individual posts from markdown content."""
        posts = []

        if source_type == 'hackernews':
            # HN structure: Title, then comments
            # Look for "Ask HN:" or "Show HN:" patterns
            lines = content.split('\n')
            current_post = None

            for line in lines:
                # Detect post titles (usually ## or ### headers)
                if line.strip().startswith('#') and ('Ask HN' in line or 'Show HN' in line or 'Tell HN' in line):
                    if current_post:
                        posts.append(current_post)

                    title = line.strip('#').strip()
                    current_post = {
                        'title': title,
                        'text': title,
                        'source': 'hackernews'
                    }
                elif current_post:
                    # Add to current post text
                    current_post['text'] += '\n' + line

            if current_post:
                posts.append(current_post)

        elif source_type == 'indiehackers':
            # Similar structure - look for discussion topics
            lines = content.split('\n')
            current_post = None

            for line in lines:
                if line.strip().startswith('#'):
                    if current_post:
                        posts.append(current_post)

                    title = line.strip('#').strip()
                    current_post = {
                        'title': title,
                        'text': title,
                        'source': 'indiehackers'
                    }
                elif current_post and line.strip():
                    current_post['text'] += '\n' + line

            if current_post:
                posts.append(current_post)

        # If no structured posts found, treat whole content as one post
        if not posts and content:
            posts.append({
                'title': 'Discussion',
                'text': content[:500],  # First 500 chars
                'source': source_type
            })

        return posts

    def process_content(self, content, source, url):
        """Process scraped content for pain points."""
        if not content or len(content) < 50:
            return 0

        # For now, treat the whole page as one opportunity
        # In production, we'd parse out individual posts/comments

        # Analyze pain signals
        pain_analysis = analyze_pain(content)

        # Create pseudo-tweet data (no likes/retweets from Firecrawl)
        # Use content length and pain signals as proxy
        pseudo_engagement = {
            'likes': len(content) // 100,  # Rough proxy
            'retweets': 0,
            'replies': 0
        }

        # Calculate score
        score = calculate_opportunity_score(pseudo_engagement, pain_analysis)

        if score < self.min_score:
            return 0

        # Generate unique ID from URL
        url_hash = str(hash(url))[:10]

        # Store in database (reusing Tweet model)
        try:
            # Check if already exists
            if Tweet.exists(url_hash):
                return 0

            tweet_id = Tweet.create(
                tweet_id=url_hash,
                text=content[:1000],  # First 1000 chars
                created_at=datetime.now().isoformat(),
                author_username=source,
                author_followers=0,
                likes=pseudo_engagement['likes'],
                retweets=0,
                replies=0
            )

            # Store pain analysis
            PainAnalysis.create(
                tweet_id=tweet_id,
                frustration_score=pain_analysis['frustration_score'],
                budget_signal_score=pain_analysis['budget_signal_score'],
                products_mentioned=pain_analysis['products_mentioned'],
                pain_keywords=pain_analysis['pain_keywords']
            )

            # Create opportunity
            title = f"[{source.upper()}] {content[:100].strip()}"
            opportunity_id = Opportunity.create(
                title=title,
                description=content[:500],
                score=score,
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat()
            )

            Opportunity.add_tweet(opportunity_id, tweet_id)

            return score

        except Exception as e:
            print(f"    ✗ Error storing: {e}")
            return 0


def collect_hackernews():
    """Collect from HackerNews."""
    print("\n📰 HACKERNEWS COLLECTION")
    print("=" * 60)

    collector = FirecrawlCollector()

    # URLs to scrape
    urls = [
        ('https://news.ycombinator.com/ask', 'Ask HN - Latest'),
        ('https://news.ycombinator.com/newest', 'Newest Posts'),
    ]

    total_stored = 0
    high_value = 0

    for url, description in urls:
        content = collector.scrape_url(url, description)

        if content:
            score = collector.process_content(content, 'hackernews', url)
            if score > 0:
                total_stored += 1
                if score >= 70:
                    high_value += 1
                    print(f"    ⭐ High-value opportunity! Score: {score}")

        time.sleep(2)  # Rate limiting

    print(f"\nStored: {total_stored} opportunities")
    print(f"High-value: {high_value} (score >= 70)")
    print()


def collect_indiehackers():
    """Collect from Indie Hackers."""
    print("\n💼 INDIE HACKERS COLLECTION")
    print("=" * 60)

    collector = FirecrawlCollector()

    # Indie Hackers community URLs
    urls = [
        ('https://www.indiehackers.com/group/bootstrapped-businesses/recent', 'Bootstrapped Businesses'),
        ('https://www.indiehackers.com/group/landing-page-feedback/recent', 'Landing Page Feedback'),
    ]

    total_stored = 0
    high_value = 0

    for url, description in urls:
        content = collector.scrape_url(url, description)

        if content:
            score = collector.process_content(content, 'indiehackers', url)
            if score > 0:
                total_stored += 1
                if score >= 70:
                    high_value += 1
                    print(f"    ⭐ High-value opportunity! Score: {score}")

        time.sleep(2)

    print(f"\nStored: {total_stored} opportunities")
    print(f"High-value: {high_value} (score >= 70)")
    print()


def collect_producthunt():
    """Collect from Product Hunt."""
    print("\n🚀 PRODUCT HUNT COLLECTION")
    print("=" * 60)

    collector = FirecrawlCollector()

    # Product Hunt URLs
    urls = [
        ('https://www.producthunt.com/', 'Today\'s Products'),
    ]

    total_stored = 0
    high_value = 0

    for url, description in urls:
        content = collector.scrape_url(url, description)

        if content:
            score = collector.process_content(content, 'producthunt', url)
            if score > 0:
                total_stored += 1
                if score >= 70:
                    high_value += 1
                    print(f"    ⭐ High-value opportunity! Score: {score}")

        time.sleep(2)

    print(f"\nStored: {total_stored} opportunities")
    print(f"High-value: {high_value} (score >= 70)")
    print()


def main():
    """Main collection function."""
    print("=" * 60)
    print("FIRECRAWL PAIN POINT COLLECTION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    start_time = datetime.now()

    # Collect from all sources
    try:
        collect_hackernews()
    except Exception as e:
        print(f"⚠ HackerNews failed: {e}")

    try:
        collect_indiehackers()
    except Exception as e:
        print(f"⚠ Indie Hackers failed: {e}")

    try:
        collect_producthunt()
    except Exception as e:
        print(f"⚠ Product Hunt failed: {e}")

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Total time: {duration:.1f} seconds")
    print()

    # Show top opportunities
    from backend.models import Opportunity
    top_opps = Opportunity.get_top_opportunities(limit=5, min_score=40, days=1)

    if top_opps:
        print("🔥 TOP 5 OPPORTUNITIES:")
        print("-" * 60)
        for i, opp in enumerate(top_opps, 1):
            source = opp['title'].split(']')[0].strip('[')
            title = opp['title'][opp['title'].find(']')+1:].strip()
            print(f"{i}. [{opp['score']}/100] {source}: {title[:50]}...")
    else:
        print("No high-value opportunities found.")

    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Collection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
