#!/usr/bin/env python3
"""
Combined Collection Script

Runs both Twitter and Reddit collection in sequence.
This is the main script for daily automated collection.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    print("=" * 70)
    print("PAIN POINT DISCOVERY ENGINE - Daily Collection")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    start_time = datetime.now()

    # Collect from Twitter
    print("\n🐦 TWITTER COLLECTION")
    print("-" * 70)
    try:
        from collect_tweets import collect_from_twitter
        collect_from_twitter()
    except Exception as e:
        print(f"⚠ Twitter collection failed: {e}")
        print("Continuing with Reddit...")

    print("\n")

    # Collect from Reddit
    print("🤖 REDDIT COLLECTION")
    print("-" * 70)
    try:
        from collect_reddit import collect_from_reddit
        collect_from_reddit()
    except Exception as e:
        print(f"⚠ Reddit collection failed: {e}")

    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n")
    print("=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)
    print(f"Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Show top opportunities
    from backend.models import Opportunity
    top_opps = Opportunity.get_top_opportunities(limit=5, min_score=60, days=1)

    if top_opps:
        print("🔥 TOP 5 OPPORTUNITIES TODAY:")
        print("-" * 70)
        for i, opp in enumerate(top_opps, 1):
            print(f"{i}. [{opp['score']}/100] {opp['title'][:60]}...")
    else:
        print("No high-value opportunities found today.")

    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
