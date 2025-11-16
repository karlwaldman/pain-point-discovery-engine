#!/usr/bin/env python3
"""
Unified Pain Point Collection Script

Runs all available collectors in sequence:
1. HackerNews (Algolia API - always works)
2. Stack Overflow (Stack Exchange API - no auth)
3. GitHub Issues (GitHub API - no auth, limited)
4. Reddit (PRAW - requires credentials)
5. Twitter (Twitter API v2 - requires Elevated Access)

This script is designed to be run daily via cron.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    print("=" * 70)
    print(" " * 15 + "DAILY PAIN POINT COLLECTION")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    load_dotenv()
    start_time = datetime.now()

    collectors_run = []
    collectors_failed = []

    # 1. HackerNews (always available)
    print("\n" + "=" * 70)
    print("COLLECTOR 1/5: HackerNews")
    print("=" * 70)
    try:
        from collect_hackernews import collect_from_hackernews
        collect_from_hackernews()
        collectors_run.append("HackerNews")
    except Exception as e:
        print(f"\n⚠ HackerNews collection failed: {e}")
        collectors_failed.append(("HackerNews", str(e)))

    # 2. Stack Overflow (no auth needed)
    print("\n" + "=" * 70)
    print("COLLECTOR 2/5: Stack Overflow")
    print("=" * 70)
    try:
        from collect_stackoverflow import collect_from_stackoverflow
        collect_from_stackoverflow()
        collectors_run.append("Stack Overflow")
    except Exception as e:
        print(f"\n⚠ Stack Overflow collection failed: {e}")
        collectors_failed.append(("Stack Overflow", str(e)))

    # 3. GitHub Issues (no auth needed, but limited)
    print("\n" + "=" * 70)
    print("COLLECTOR 3/5: GitHub Issues")
    print("=" * 70)
    try:
        from collect_github import collect_from_github
        collect_from_github()
        collectors_run.append("GitHub Issues")
    except Exception as e:
        print(f"\n⚠ GitHub collection failed: {e}")
        collectors_failed.append(("GitHub Issues", str(e)))

    # 4. Reddit (requires credentials)
    print("\n" + "=" * 70)
    print("COLLECTOR 4/5: Reddit")
    print("=" * 70)
    if os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
        try:
            from collect_reddit import collect_from_reddit
            collect_from_reddit()
            collectors_run.append("Reddit")
        except Exception as e:
            print(f"\n⚠ Reddit collection failed: {e}")
            collectors_failed.append(("Reddit", str(e)))
    else:
        print("⏩ Skipped (credentials not configured)")
        print("   Run: python scripts/collect_reddit.py to set up Reddit")

    # 5. Twitter (requires Elevated Access)
    print("\n" + "=" * 70)
    print("COLLECTOR 5/5: Twitter")
    print("=" * 70)
    if os.getenv('TWITTER_BEARER_TOKEN'):
        try:
            from collect_tweets import collect_from_twitter
            collect_from_twitter()
            collectors_run.append("Twitter")
        except Exception as e:
            print(f"\n⚠ Twitter collection failed: {e}")
            collectors_failed.append(("Twitter", str(e)))
    else:
        print("⏩ Skipped (credentials not configured)")
        print("   See: API_SETUP.md for Twitter Elevated Access")

    # Final Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 70)
    print(" " * 20 + "DAILY COLLECTION COMPLETE")
    print("=" * 70)
    print(f"Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"✅ Collectors run: {len(collectors_run)}")
    for collector in collectors_run:
        print(f"   - {collector}")
    print()

    if collectors_failed:
        print(f"❌ Collectors failed: {len(collectors_failed)}")
        for collector, error in collectors_failed:
            print(f"   - {collector}: {error[:60]}")
        print()

    # Show top opportunities from today
    from backend.models import Opportunity
    top_opps = Opportunity.get_top_opportunities(limit=10, min_score=40, days=1)

    if top_opps:
        print("🔥 TOP 10 OPPORTUNITIES FROM TODAY:")
        print("-" * 70)
        for i, opp in enumerate(top_opps, 1):
            source = opp['title'].split(']')[0].strip('[')
            title = opp['title'][opp['title'].find(']')+1:].strip()
            print(f"{i:2}. [{opp['score']:3}/100] {source:12} {title[:40]}...")
    else:
        print("No high-value opportunities found today.")
        print("Tip: Lower MIN_OPPORTUNITY_SCORE in .env to see more results.")

    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
